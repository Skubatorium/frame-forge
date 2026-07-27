"""State-Machine fuer Projekte und Exporte.

Haelt pro Projekt die erreichte Phase (`.state.json`), pro Export einen
eigenen Sub-State ab `BRIEFED`, sowie Content-Hashes der Eingaben fuer
Invalidierung. Alle anderen Module haengen an dieser Datei (siehe Plan
`docs/plans/0001-initial-structure.md`, Abschnitt 2 und 9).
"""

from __future__ import annotations

import fcntl
import json
from collections.abc import Iterator
from contextlib import contextmanager
from enum import IntEnum
from pathlib import Path

from pydantic import BaseModel, Field


class Phase(IntEnum):
    """Reihenfolge der Prozess-Phasen. Werte sind monoton — Vergleiche (`<`, `>=`) sind erlaubt."""

    NEW = -1
    """Nur interner Default fuer Exports, die noch nie angelegt/gebrieft wurden. Keine
    echte Prozessphase — kann nicht per `advance_export` gesetzt werden."""
    INIT = 0
    INGESTED = 1
    INDEXED = 2
    DESIGNED = 3
    BRIEFED = 4
    STORYBOARDED = 5
    TIMELINE = 6
    ASSETS_BUILT = 7
    PREVIEWED = 8
    APPROVED = 9
    RENDERED = 10


# Phasen, die auf Projekt- bzw. Export-Ebene gueltig sind.
PROJECT_PHASES = frozenset({Phase.INIT, Phase.INGESTED, Phase.INDEXED, Phase.DESIGNED})
EXPORT_PHASES = frozenset(p for p in Phase if p >= Phase.BRIEFED)

_PHASE_NAMES_DE = {
    Phase.NEW: "NEW (kein brief.yaml)",
    Phase.INIT: "INIT",
    Phase.INGESTED: "INGESTED (ff-ingest)",
    Phase.INDEXED: "INDEXED (ff-index)",
    Phase.DESIGNED: "DESIGNED (ff-design)",
    Phase.BRIEFED: "BRIEFED (ff-brief)",
    Phase.STORYBOARDED: "STORYBOARDED (story-architect)",
    Phase.TIMELINE: "TIMELINE (ff-build)",
    Phase.ASSETS_BUILT: "ASSETS_BUILT",
    Phase.PREVIEWED: "PREVIEWED (ff-preview)",
    Phase.APPROVED: "APPROVED",
    Phase.RENDERED: "RENDERED (ff-render)",
}


class StateError(RuntimeError):
    """Basisfehler fuer alles rund um `.state.json`."""


class GateError(StateError):
    """Eine Vorbedingung (Gate) wurde verletzt.

    Traegt `required` und `current`, damit Aufrufer (CLI, Hook, Orchestrator)
    dieselbe Meldung anzeigen koennen wie in Plan Abschnitt 10 gefordert:
    "Phase X — erforderlich: ...".
    """

    def __init__(self, required: Phase, current: Phase, *, context: str = "Projekt"):
        self.required = required
        self.current = current
        self.context = context
        super().__init__(
            f"{context}-Phase {_PHASE_NAMES_DE[current]} — erforderlich mindestens: "
            f"{_PHASE_NAMES_DE[required]}"
        )


class ExportState(BaseModel):
    """Sub-State eines einzelnen Exports."""

    phase: Phase = Phase.NEW
    content_hashes: dict[str, str] = Field(default_factory=dict)


class ProjectStateData(BaseModel):
    """Rohform von `.state.json`."""

    schema_version: int = 1
    project_phase: Phase = Phase.INIT
    content_hashes: dict[str, str] = Field(default_factory=dict)
    exports: dict[str, ExportState] = Field(default_factory=dict)


@contextmanager
def _locked(lock_path: Path) -> Iterator[None]:
    """Exklusiver Dateilock waehrend Lesen+Schreiben von `.state.json`.

    Verhindert Race Conditions, wenn Orchestrator und Hook gleichzeitig zugreifen.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


class ProjectState:
    """Lade-/Speicher- und Gate-API fuer `.state.json` eines Projekts."""

    def __init__(self, path: Path, data: ProjectStateData):
        self.path = path
        self.data = data

    @classmethod
    def load(cls, path: Path) -> ProjectState:
        """Laedt `.state.json`. Existiert die Datei nicht, wird Phase INIT angenommen."""
        if not path.exists():
            return cls(path, ProjectStateData())
        with _locked(path.with_suffix(".lock")):
            raw = json.loads(path.read_text())
        return cls(path, ProjectStateData.model_validate(raw))

    def save(self) -> None:
        """Schreibt `.state.json` atomar (tmp-Datei + rename) unter Lock."""
        with _locked(self.path.with_suffix(".lock")):
            tmp = self.path.with_suffix(".json.tmp")
            tmp.write_text(self.data.model_dump_json(indent=2))
            tmp.replace(self.path)

    # -- Projekt-Phase -----------------------------------------------------

    @property
    def project_phase(self) -> Phase:
        return self.data.project_phase

    def advance_project(self, phase: Phase, *, content_hash: str | None = None) -> None:
        """Setzt die Projekt-Phase. Erlaubt Vorwaerts- wie Rueckwaerts-Uebergaenge

        (Rueckwaerts z.B. bei Invalidierung durch neues Rohmaterial), aber nur
        innerhalb der gueltigen Projekt-Phasen.
        """
        if phase not in PROJECT_PHASES:
            raise StateError(f"{phase.name} ist keine gueltige Projekt-Phase")
        self.data.project_phase = phase
        if content_hash is not None:
            self.data.content_hashes["_project"] = content_hash

    def ensure_project_at_least(self, phase: Phase) -> None:
        """Hebt die Projekt-Phase auf `phase`, aber nur vorwaerts (nie zurueck).

        Fuer idempotente Kommandos: `ingest`/`index` erneut auszufuehren darf eine bereits
        weiter fortgeschrittene Phase (z.B. DESIGNED) nicht zuruecksetzen (Audit-Finding P5).
        """
        if self.data.project_phase < phase:
            self.advance_project(phase)

    def invalidate_project(self, to: Phase = Phase.INGESTED) -> None:
        """Faellt auf `to` zurueck. Analyse-Cache (assets.json) bleibt unberuehrt —

        das ist Aufgabe von ingest.py/index.py, nicht dieser Funktion.
        """
        self.advance_project(to)

    def require_project(self, minimum: Phase) -> None:
        if self.data.project_phase < minimum:
            raise GateError(minimum, self.data.project_phase, context="Projekt")

    # -- Export-Phase --------------------------------------------------------

    def _peek_export(self, name: str) -> ExportState:
        """Nicht-mutierender Lesezugriff — legt keinen Phantom-Eintrag in `.state.json` an."""
        return self.data.exports.get(name, ExportState())

    def export_phase(self, name: str) -> Phase:
        return self._peek_export(name).phase

    def advance_export(self, name: str, phase: Phase, *, content_hash: str | None = None) -> None:
        if phase not in EXPORT_PHASES:
            raise StateError(f"{phase.name} ist keine gueltige Export-Phase")
        export = self.data.exports.setdefault(name, ExportState())
        export.phase = phase
        if content_hash is not None:
            export.content_hashes["_export"] = content_hash

    def invalidate_export(self, name: str, to: Phase = Phase.BRIEFED) -> None:
        """Faellt auf `to` zurueck, z.B. wenn `brief.yaml` sich geaendert hat."""
        self.advance_export(name, to)

    def require_export(self, name: str, minimum: Phase) -> None:
        current = self.export_phase(name)
        if current < minimum:
            raise GateError(minimum, current, context=f"Export '{name}'")


# -- Gate-Regeln aus Plan Abschnitt 2 -----------------------------------------
#
# Diese Funktionen buendeln die Vorbedingungen pro Kommando, damit CLI, Hook
# und Orchestrator dieselbe Logik verwenden (Guertel + Hosentraeger).


def gate_index(state: ProjectState) -> None:
    """`ff-index` erfordert Projekt-Phase >= INGESTED."""
    state.require_project(Phase.INGESTED)


def gate_design(state: ProjectState) -> None:
    """`ff-design` erfordert Projekt-Phase >= INDEXED.

    Ohne dieses Gate koennte `design` die Phase direkt von INIT auf DESIGNED heben und damit
    INGESTED/INDEXED ueberspringen — dann waere die von `gate_brief` vorausgesetzte Invariante
    "DESIGNED impliziert INDEXED" verletzt (Audit-Finding P1).
    """
    state.require_project(Phase.INDEXED)


def gate_brief(state: ProjectState) -> None:
    """`ff-brief` erfordert Projekt-Phase >= DESIGNED (impliziert INDEXED)."""
    state.require_project(Phase.DESIGNED)


def gate_build(state: ProjectState, export: str) -> None:
    """`ff-build` erfordert Export-Phase >= BRIEFED. `brief.yaml`-Validierung ist Sache des Aufrufers."""
    state.require_export(export, Phase.BRIEFED)


def gate_preview(state: ProjectState, export: str, *, timeline_exists: bool) -> None:
    """`ff-preview` erfordert `timeline.json` und Export-Phase >= TIMELINE.

    Die inhaltliche QC-Pruefung (`qc.validate()`) liegt in `frameforge.qc` und
    wird dort zusaetzlich aufgerufen — dieses Gate deckt nur den State ab.
    """
    if not timeline_exists:
        raise StateError("timeline.json existiert nicht — zuerst ff-build ausfuehren")
    state.require_export(export, Phase.TIMELINE)


def gate_render_final(state: ProjectState, export: str) -> None:
    """`ff-render` (final) erfordert Export-Phase == APPROVED (explizite Freigabe).

    Bewusst strikte Gleichheit, nicht `>=`: Plan Abschnitt 2 verlangt wortwoertlich
    "Export-Phase = APPROVED". Ein bereits gerenderter Export (Phase RENDERED) braucht
    fuer einen erneuten Final-Render wieder eine explizite Freigabe nach Preview — sonst
    koennte ein veralteter Render ohne neue Kontrolle wiederholt werden.
    """
    current = state.export_phase(export)
    if current != Phase.APPROVED:
        raise GateError(Phase.APPROVED, current, context=f"Export '{export}'")
