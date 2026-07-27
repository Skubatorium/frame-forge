"""Visuelle Pipeline-Uebersicht fuer `frameforge status` und den `/ff-wizard`.

Reine Ableitung aus dem `ProjectState` — kein I/O ausser dem, was der Aufrufer schon geladen
hat. Liefert pro Schritt, ob er erledigt (`[✓]`), gerade dran (`[→]`) oder offen (`[ ]`) ist,
plus den naechsten faelligen Befehl. Beides — Status-Anzeige und Wizard — nutzt dieselbe
Quelle, damit die "du bist hier"-Markierung nie auseinanderlaeuft.
"""

from __future__ import annotations

from dataclasses import dataclass

from frameforge.state import Phase, ProjectState

DONE = "[✓]"
CURRENT = "[→]"
PENDING = "[ ]"


@dataclass(frozen=True)
class Step:
    key: str  # "ingest", "brief", ...
    target: Phase  # Phase, die dieser Schritt erreicht
    command: str  # Slash-Command bzw. CLI-Aufruf fuer diesen Schritt
    done: bool
    current: bool  # der naechste faellige Schritt (genau einer ueber die ganze Pipeline)

    @property
    def marker(self) -> str:
        if self.done:
            return DONE
        return CURRENT if self.current else PENDING


# Projekt-Ebene: (key, Ziel-Phase, Command-Vorlage mit {p})
_PROJECT_STEPS: tuple[tuple[str, Phase, str], ...] = (
    ("ingest", Phase.INGESTED, "/ff-ingest {p}"),
    ("index", Phase.INDEXED, "/ff-index {p}"),
    ("design", Phase.DESIGNED, "/ff-design {p}"),
)

# Export-Ebene: (key, Ziel-Phase, Command-Vorlage mit {p} und {e})
_EXPORT_STEPS: tuple[tuple[str, Phase, str], ...] = (
    ("brief", Phase.BRIEFED, "/ff-brief {p} {e}"),
    ("build", Phase.TIMELINE, "/ff-build {p} {e}"),
    ("preview", Phase.PREVIEWED, "/ff-preview {p} {e}"),
    ("approve", Phase.APPROVED, "frameforge approve {p} {e}"),
    ("render", Phase.RENDERED, "/ff-render {p} {e}"),
)


@dataclass(frozen=True)
class Pipeline:
    project: str
    project_steps: list[Step]
    export_steps: dict[str, list[Step]]  # export-name -> steps
    next_command: str | None  # naechster faelliger Befehl, None = alles fertig
    next_hint: str  # menschenlesbarer Hinweis


def _build_steps(specs, reached: Phase, project: str, export: str | None) -> tuple[list[Step], bool]:
    """Baut die Step-Liste; markiert den ersten nicht-erledigten als `current`.

    Rueckgabe: (steps, has_current) — `has_current` sagt dem Aufrufer, ob der naechste
    faellige Schritt der Pipeline in dieser Liste lag.
    """
    steps: list[Step] = []
    current_taken = False
    for key, target, tmpl in specs:
        done = reached >= target
        current = not done and not current_taken
        if current:
            current_taken = True
        steps.append(
            Step(
                key=key,
                target=target,
                command=tmpl.format(p=project, e=export or "<export>"),
                done=done,
                current=current,
            )
        )
    return steps, current_taken


def build_pipeline(project: str, state: ProjectState, *, exports: list[str] | None = None) -> Pipeline:
    """Leitet die Pipeline-Uebersicht aus dem State ab.

    `exports` sind die bekannten Export-Namen (z.B. `project.list_exports()`); ist die Liste
    leer und das Projekt bereits `DESIGNED`, ist der naechste Schritt "einen Export briefen".
    """
    exports = exports or []
    proj_steps, proj_has_current = _build_steps(
        _PROJECT_STEPS, state.project_phase, project, None
    )

    next_command: str | None = None
    next_hint = ""

    # Der naechste faellige Schritt liegt zuerst auf Projekt-Ebene.
    if proj_has_current:
        nxt = next(s for s in proj_steps if s.current)
        next_command = nxt.command
        next_hint = f"{nxt.key}: {nxt.command}"

    export_steps: dict[str, list[Step]] = {}
    for name in exports:
        steps, has_current = _build_steps(
            _EXPORT_STEPS, state.export_phase(name), project, name
        )
        export_steps[name] = steps
        # Erster Export mit offenem Schritt bestimmt den naechsten Befehl (falls Projekt fertig).
        if next_command is None and has_current:
            nxt = next(s for s in steps if s.current)
            next_command = nxt.command
            next_hint = f"Export '{name}' — {nxt.key}: {nxt.command}"

    # Projekt fertig (DESIGNED), aber noch kein Export gebrieft.
    if next_command is None and state.project_phase >= Phase.DESIGNED and not exports:
        next_command = f"/ff-brief {project} <export>"
        next_hint = "Ersten Export anlegen und briefen (Name frei waehlbar)"

    if next_command is None and not next_hint:
        next_hint = "Alles erledigt — nichts offen."

    return Pipeline(
        project=project,
        project_steps=proj_steps,
        export_steps=export_steps,
        next_command=next_command,
        next_hint=next_hint,
    )


def format_pipeline(pipeline: Pipeline) -> list[str]:
    """Rendert die Pipeline als Klartext-Zeilen (Marker + Schritt), fuer Terminal-Ausgabe."""
    lines = [f"Pipeline  {pipeline.project}", ""]
    lines += [f"  {s.marker} {s.key}" for s in pipeline.project_steps]

    for name, steps in pipeline.export_steps.items():
        lines.append("")
        lines.append(f"  Export: {name}")
        lines += [f"    {s.marker} {s.key}" for s in steps]

    lines.append("")
    if pipeline.next_command:
        lines.append(f"Naechster Schritt: {pipeline.next_hint}")
    else:
        lines.append(pipeline.next_hint)
    return lines
