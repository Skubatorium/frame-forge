"""Index-Schreiber (`assets.json` + `.md`-Dateien) und Query-Interface."""

from __future__ import annotations

import json

from frameforge.project import Project

_NOTES_MARKER = "<!-- ff:notes -->"
_DEFAULT_NOTES = "\n(hier eigene Notizen ergänzen — bleibt bei Re-Indexierung erhalten)\n"


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
) -> list[dict]:
    """Filtert `assets.json` nach Tag, Ort, Mindest-Rating, Art (video/photo) und Quelle/Kamera.

    `source` filtert auf die Aufnahme-Quelle (`drone`/`phone`/`camera`/`action_cam`, siehe
    `frameforge.probe.SOURCE_TYPES`) — z.B. "nur Drohnen-Shots".
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
        return source is None or asset.get("source") == source

    return [asset for asset in load_assets(project) if matches(asset)]


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
    tech = asset.get("tech", {})
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


def write_asset(project: Project, asset: dict) -> None:
    """Schreibt/merged einen Asset-Eintrag in `assets.json` und die zugehoerige `.md`-Datei.

    Upsert nach `asset["id"]` in `assets.json` (sortiert nach ID fuer stabile Diffs). Die
    `.md`-Datei wird neu generiert, aber der Freitext-Abschnitt nach `_NOTES_MARKER`
    (eigene Notizen) bleibt ueber Re-Indexierung hinweg erhalten — Merge statt Ueberschreiben.
    """
    asset_id = asset["id"]
    assets = load_assets(project)
    assets = [a for a in assets if a.get("id") != asset_id]
    assets.append(asset)
    assets.sort(key=lambda a: a["id"])

    project.assets_json_path.parent.mkdir(parents=True, exist_ok=True)
    project.assets_json_path.write_text(json.dumps(assets, indent=2, ensure_ascii=False) + "\n")

    project.assets_dir.mkdir(parents=True, exist_ok=True)
    md_path = project.assets_dir / f"{asset_id}.md"
    notes = _existing_notes(md_path)
    md_path.write_text(_render_markdown(asset, notes))
