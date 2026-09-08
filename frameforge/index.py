"""Index-Schreiber (`assets.json` + `.md`-Dateien) und Query-Interface."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager

try:
    import fcntl
except ImportError:  # pragma: no cover - nicht-POSIX
    fcntl = None

from frameforge.project import Project

_NOTES_MARKER = "<!-- ff:notes -->"
_DEFAULT_NOTES = "\n(hier eigene Notizen ergänzen — bleibt bei Re-Indexierung erhalten)\n"

# Prioritaetsstufen fuer die Clip-Auswahl (Plan 0004 §4): "must" wird vom timeline-builder
# garantiert eingeplant, "nice" bevorzugt vor "ok" bei Restzeit, "ok" ist reiner Luecken-
# fueller. Default beim Indizieren ist "ok" (siehe preindex.index_prepared_asset).
PRIORITY_LEVELS = ("must", "nice", "ok")


def load_assets(project: Project) -> list[dict]:
    """Alle Eintraege aus `assets.json`. Leere Liste, falls die Datei noch fehlt."""
    if not project.assets_json_path.exists():
        return []
    return json.loads(project.assets_json_path.read_text())


def query_assets(
    project: Project,
    *,
    tag: str | None = None,
    place: str | None = None,
    min_rating: int | None = None,
    kind: str | None = None,
    source: str | None = None,
    priority: str | None = None,
) -> list[dict]:
    """Filtert `assets.json` nach Tag, Ort, Mindest-Rating, Art (video/photo), Quelle/Kamera
    und Prioritaetsstufe.

    `source` filtert auf die Aufnahme-Quelle (`drone`/`phone`/`camera`/`action_cam`, siehe
    `frameforge.probe.SOURCE_TYPES`) — z.B. "nur Drohnen-Shots". `priority` filtert exakt auf
    eine der `PRIORITY_LEVELS` (`must`/`nice`/`ok`) — fuer den `timeline-builder`, der zuerst
    alle `must`-Assets platziert, dann `nice` vor `ok` (Plan 0004 §4). Assets ohne gesetzte
    Prioritaet gelten als `ok` (der Default beim Indizieren).
    """

    def matches(asset: dict) -> bool:
        if asset.get("exclude"):
            return False  # dauerhaft gesperrt (z.B. Fehlaufnahme) — nie in einem Film
        if tag is not None and tag not in asset.get("content", {}).get("tags", []):
            return False
        if place is not None and place != asset.get("gps", {}).get("place"):
            return False
        if min_rating is not None and asset.get("rating", 0) < min_rating:
            return False
        if kind is not None and asset.get("kind") != kind:
            return False
        if priority is not None and asset.get("content", {}).get("priority", "ok") != priority:
            return False
        return source is None or asset.get("source") == source

    return [asset for asset in load_assets(project) if matches(asset)]


def find_assets_by_filename(project: Project, filename_substr: str) -> list[dict]:
    """Assets, deren `path` den gegebenen Teilstring enthaelt (case-insensitive).

    Grundlage fuer dateinamen-basiertes Priorisieren (`frameforge set-priority`, Plan 0004
    §4): der Nutzer kennt beim Sichten seiner eigenen Fotos/Videos keine internen Asset-Hashes,
    aber den (Teil des) Dateinamens — z.B. die letzten Ziffern von `IMG_1234.HEIC`.
    """
    needle = filename_substr.lower()
    return [a for a in load_assets(project) if needle in a.get("path", "").lower()]


def tech_of(asset: dict) -> dict:
    """Technische Angaben eines Assets (`w`, `h`, `fps`, `dur`, `codec`, `bitrate`).

    Plan 0001 §4 nennt das Feld `tech`; `preindex._prepare_one` schreibt die ffprobe-Antwort
    aber unter `probe` (plus `duration` daneben). Beide Schreibweisen existieren im Bestand,
    deshalb liest **jeder** Auswerter über diese Funktion statt direkt — sonst meldet die
    Statistik „0 s Rohmaterial" bei 142 Minuten Material (am echten Fundus gefunden,
    2026-08-03).
    """
    tech = asset.get("tech") or asset.get("probe") or {}
    if "dur" not in tech and asset.get("duration") is not None:
        tech = {**tech, "dur": asset["duration"]}
    return tech


def _existing_notes(md_path) -> str:
    """Freitext-Abschnitt nach `_NOTES_MARKER` einer bestehenden `.md`-Datei, sonst der Default."""
    if not md_path.exists():
        return _DEFAULT_NOTES
    text = md_path.read_text()
    if _NOTES_MARKER not in text:
        return _DEFAULT_NOTES
    return text.split(_NOTES_MARKER, 1)[1]


def _render_markdown(asset: dict, notes: str) -> str:
    content = asset.get("content", {})
    quality = asset.get("quality", {})
    tech = tech_of(asset)
    gps = asset.get("gps") or {}

    lines = [
        f"# {asset['id']}",
        "",
        f"**Pfad:** {asset.get('path', '-')}",
        f"**Aufgenommen:** {asset.get('captured_at') or '-'}",
        f"**Ort:** {gps.get('place', '-')}",
        f"**Typ:** {asset.get('kind', '-')}",
        f"**Rating:** {asset.get('rating', '-')}/5",
        "",
        "## Technik",
    ]
    if asset.get("kind") == "video":
        lines.append(
            f"- Auflösung: {tech.get('w', '?')}x{tech.get('h', '?')} @ {tech.get('fps', '?')} fps"
        )
        lines.append(f"- Dauer: {tech.get('dur', '?')}s")
        lines.append(f"- Codec: {tech.get('codec', '?')}")
    lines += [
        "",
        "## Qualität",
        f"- Schärfe: {quality.get('sharpness', '-')}",
        f"- Stabilität: {quality.get('stability', '-')}",
        f"- Belichtung: {quality.get('exposure', '-')}",
        f"- Score: {quality.get('score', '-')}",
        "",
        "## Inhalt",
        content.get("summary", "-"),
        "",
        f"Tags: {', '.join(content.get('tags', []))}",
        "",
        _NOTES_MARKER,
    ]
    return "\n".join(lines) + notes


@contextmanager
def _assets_lock(project: Project):
    """Prozessuebergreifender Exklusiv-Lock um das Read-modify-write von `assets.json`.

    Mehrere `media-indexer`-Agenten schreiben parallel je einen Asset-Eintrag ueber
    `write_asset`. Ohne Lock ueberschreiben sie sich gegenseitig oder lesen halb
    geschriebenes JSON. Auf Plattformen ohne `fcntl` (Windows) ist der Lock ein No-op.
    """
    if fcntl is None:
        yield
        return
    lock_path = project.assets_json_path.with_name(project.assets_json_path.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def save_assets(project: Project, assets: list[dict]) -> None:
    """Schreibt die komplette Asset-Liste nach `assets.json` (sortiert nach ID, stabile Diffs).

    Atomar: erst in eine Temp-Datei im selben Verzeichnis, dann `os.replace` — ein
    paralleler Leser sieht nie eine halb geschriebene Datei.
    """
    target = project.assets_json_path
    target.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(assets, key=lambda a: a["id"])
    payload = json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=".assets-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def write_asset_md(project: Project, asset: dict) -> None:
    """Erzeugt die `.md`-Datei eines Assets neu — Freitext nach `_NOTES_MARKER` bleibt erhalten."""
    project.assets_dir.mkdir(parents=True, exist_ok=True)
    md_path = project.assets_dir / f"{asset['id']}.md"
    md_path.write_text(_render_markdown(asset, _existing_notes(md_path)))


def write_asset(project: Project, asset: dict) -> None:
    """Schreibt/merged einen Asset-Eintrag in `assets.json` und die zugehoerige `.md`-Datei.

    Upsert nach `asset["id"]` in `assets.json` (sortiert nach ID fuer stabile Diffs). Die
    `.md`-Datei wird neu generiert, aber der Freitext-Abschnitt nach `_NOTES_MARKER`
    (eigene Notizen) bleibt ueber Re-Indexierung hinweg erhalten — Merge statt Ueberschreiben.
    """
    asset_id = asset["id"]
    with _assets_lock(project):
        assets = [a for a in load_assets(project) if a.get("id") != asset_id]
        assets.append(asset)
        save_assets(project, assets)
    write_asset_md(project, asset)
