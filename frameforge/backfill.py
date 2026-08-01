"""Nachtragen technischer Metadaten ohne Neu-Indizierung (Plan 0003, Arbeitspaket A0).

Der bestehende Fundus (255 Assets in `norwegen-2026`) hat Beschreibungen, Tags und Ratings, die
durch Claude Vision entstanden sind — dieser Aufwand darf nicht verloren gehen (Plan 0003 §0).
Fehlende **technische** Felder werden deshalb nachgetragen statt neu erzeugt: `assets.json`
lesen, Originaldateien erneut proben, Ergebnis mergen.

Angefasst wird ausschliesslich, was aus der Datei selbst ableitbar ist (`_TECH_FIELDS`):
`captured_at`, `duration`, `probe.*`, `gps.lat`/`gps.lon`/`gps.elevation_m`. **Nie** angefasst:
`content`, `tags`, `rating`, `source`, `exclude`, `gps.place`, `keyframes`, `quality`, `motion`,
`scenes` und der Freitext in den `.md`-Dateien. Kein Vision-Call, keine CV-Analyse.

`plan_backfill` rechnet nur (probt, schreibt nichts), `apply_backfill` schreibt — damit
`--dry-run` und der echte Lauf garantiert dieselbe Entscheidung treffen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from frameforge import index as index_module
from frameforge import ingest as ingest_module
from frameforge import probe as probe_module
from frameforge.project import Project, UnsafePathError, resolve_media_path

# Erlaubte Ziel-Felder (dotted). Alles andere ruehrt der Backfill nicht an — bewusst als
# Positivliste, damit eine spaetere Erweiterung eine bewusste Entscheidung ist.
_TECH_FIELDS = frozenset(
    {
        "captured_at",
        "captured_at_source",
        "duration",
        "probe",
        "gps.lat",
        "gps.lon",
        "gps.elevation_m",
        "gps.source",
    }
)


def index_originals(originals_root: Path | None) -> dict[str, Path]:
    """`{Stem des Originals: Pfad}` unter `originals_root` (Plan 0003 §A2).

    Leeres Dict, wenn kein `originals_root` konfiguriert oder der Ordner nicht erreichbar ist
    (externe Platte nicht angeschlossen) — dann laeuft der Backfill ohne den GPS-Zweig, statt
    abzubrechen.
    """
    if originals_root is None or not originals_root.is_dir():
        return {}
    return {p.stem: p for p in ingest_module.scan_media(originals_root)}


def _gps_from_original(path, originals: dict[str, Path]) -> dict[str, Any]:
    """GPS des ungeschnittenen Originals eines vorgeschnittenen Clips, sonst `{}`.

    Der Originalname entsteht durch Abschneiden des `-HH.MM.SS.mmm-…-segN`-Suffix; ohne Suffix
    ist der Clip selbst das Original und wird direkt gesucht. Findet sich nichts, passiert
    nichts Stilles — das Asset bleibt ohne Koordinaten und taucht in der Lueckenliste (A5) auf.
    """
    if not originals:
        return {}
    stem = probe_module.original_name_from_trimmed(path)
    original = originals.get(Path(stem).stem if stem else path.stem)
    if original is None or original == path:
        return {}
    gps = probe_module.probe_media_gps(original)
    if not gps:
        return {}
    return {f"gps.{k}": v for k, v in gps.items()} | {"gps.source": "original"}


@dataclass(frozen=True)
class FieldUpdate:
    """Eine einzelne nachgetragene/korrigierte technische Angabe."""

    asset_id: str
    field: str  # dotted, z.B. "gps.lat"
    old: Any
    new: Any

    @property
    def is_new(self) -> bool:
        """True, wenn das Feld vorher fehlte (Nachtrag statt Korrektur)."""
        return self.old is None


@dataclass(frozen=True)
class BackfillFailure:
    asset_id: str
    reason: str


@dataclass
class BackfillResult:
    scanned: int = 0
    updates: list[FieldUpdate] = field(default_factory=list)
    unchanged: int = 0
    missing_files: list[str] = field(default_factory=list)  # Asset-IDs ohne auffindbare Datei
    failures: list[BackfillFailure] = field(default_factory=list)
    originals_found: int = 0  # Dateien unter `originals_root` (0 = Zweig inaktiv, siehe A2)

    @property
    def touched_assets(self) -> set[str]:
        return {u.asset_id for u in self.updates}

    def count_by_field(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for update in self.updates:
            counts[update.field] = counts.get(update.field, 0) + 1
        return dict(sorted(counts.items()))


def _get(asset: dict, dotted: str) -> Any:
    node: Any = asset
    for part in dotted.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def _set(asset: dict, dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    node = asset
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def _probe_fields(asset: dict, path, originals: dict[str, Path] | None = None) -> dict[str, Any]:
    """Technische Soll-Werte eines Assets aus der Datei — leere Werte werden weggelassen."""
    fields: dict[str, Any] = {}
    if asset.get("kind") == "video":
        probe = probe_module.probe_video(path)
        fields["probe"] = probe
        if probe.get("dur"):
            fields["duration"] = probe["dur"]
        if probe.get("captured_at"):
            fields["captured_at"] = probe["captured_at"]
            fields["captured_at_source"] = probe.get("captured_at_source")
        gps = asset.get("gps") or {}
        if gps.get("lat") is None or gps.get("lon") is None:
            # Der Vorschnitt hat die Koordinaten verloren (0 von 236 Videos im Realbetrieb) —
            # sie stehen aber noch im Original. Nur nachschlagen, wenn wirklich nichts da ist:
            # eine vorhandene Koordinate wird nie ueberschrieben.
            fields.update(_gps_from_original(path, originals or {}))
    else:
        exif = probe_module.probe_photo_exif(path)
        if exif.get("captured_at"):
            fields["captured_at"] = exif["captured_at"]
            fields["captured_at_source"] = exif.get("captured_at_source", "exif")
        gps = exif.get("gps") or {}
        for key in ("lat", "lon", "elevation_m"):
            if gps.get(key) is not None:
                fields[f"gps.{key}"] = gps[key]
    return {k: v for k, v in fields.items() if k in _TECH_FIELDS and v is not None}


def plan_backfill(project: Project) -> BackfillResult:
    """Probt die Originale und sammelt die noetigen technischen Korrekturen. Schreibt nichts.

    Ein Asset, dessen Datei fehlt, landet in `missing_files` (Hinweis auf `frameforge relink`),
    ein Probe-Fehler in `failures` — beides bricht den Lauf nicht ab, bei ~250 Dateien darf eine
    defekte nicht alles verhindern.
    """
    result = BackfillResult()
    media_root = project.config.media_root
    originals = index_originals(project.config.originals_root)
    result.originals_found = len(originals)

    for asset in index_module.load_assets(project):
        result.scanned += 1
        asset_id = asset.get("id", "?")
        try:
            path = resolve_media_path(media_root, asset.get("path", ""))
        except UnsafePathError as exc:
            result.failures.append(BackfillFailure(asset_id, str(exc)))
            continue
        if not path.exists():
            result.missing_files.append(asset_id)
            continue

        try:
            fields = _probe_fields(asset, path, originals)
        except Exception as exc:  # noqa: BLE001 — eine defekte Datei darf den Lauf nicht killen
            result.failures.append(BackfillFailure(asset_id, str(exc)))
            continue

        updates = [
            FieldUpdate(asset_id=asset_id, field=name, old=_get(asset, name), new=value)
            for name, value in sorted(fields.items())
            if _get(asset, name) != value
        ]
        if updates:
            result.updates.extend(updates)
        else:
            result.unchanged += 1
    return result


def apply_backfill(project: Project, result: BackfillResult) -> int:
    """Schreibt die geplanten technischen Korrekturen. Gibt die Anzahl geaenderter Assets zurueck.

    `assets.json` wird genau einmal geschrieben; `.md`-Dateien nur fuer geaenderte Assets
    (Freitext-Notizen bleiben ueber `index.write_asset_md` erhalten).
    """
    if not result.updates:
        return 0

    by_asset: dict[str, list[FieldUpdate]] = {}
    for update in result.updates:
        by_asset.setdefault(update.asset_id, []).append(update)

    assets = index_module.load_assets(project)
    touched = []
    for asset in assets:
        updates = by_asset.get(asset.get("id"))
        if not updates:
            continue
        for update in updates:
            if update.field not in _TECH_FIELDS:  # Sicherheitsnetz, siehe Modul-Docstring
                raise ValueError(f"Backfill darf '{update.field}' nicht schreiben")
            _set(asset, update.field, update.new)
        touched.append(asset)

    index_module.save_assets(project, assets)
    for asset in touched:
        index_module.write_asset_md(project, asset)
    return len(touched)


def captured_at_coverage(project: Project, *, kind: str | None = None) -> tuple[int, int]:
    """`(mit captured_at, gesamt)` — Abnahmekriterium A0 (>= 90 % der Videos)."""
    assets = index_module.load_assets(project)
    if kind is not None:
        assets = [a for a in assets if a.get("kind") == kind]
    return sum(1 for a in assets if a.get("captured_at")), len(assets)
