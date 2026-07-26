"""Index-Schreiber (`assets.json` + `.md`-Dateien) und Query-Interface.

`load_assets`/`query_assets` sind bereits echt implementiert — sie lesen nur
`assets.json`, ohne Analyse-Abhaengigkeiten, und tragen Token-Disziplin-Regel 3
(`CLAUDE.md`): Agenten fragen `frameforge query` statt ganze Verzeichnisse zu
lesen. `write_asset` (Schreiben + Merge mit Freitext-Notizen) kommt mit der
Analyse-Pipeline in M1.
"""

from __future__ import annotations

import json

from frameforge.project import Project


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
) -> list[dict]:
    """Filtert `assets.json` nach Tag, Ort, Mindest-Rating und Asset-Art (video/photo)."""

    def matches(asset: dict) -> bool:
        if tag is not None and tag not in asset.get("content", {}).get("tags", []):
            return False
        if place is not None and place != asset.get("gps", {}).get("place"):
            return False
        if min_rating is not None and asset.get("rating", 0) < min_rating:
            return False
        return kind is None or asset.get("kind") == kind

    return [asset for asset in load_assets(project) if matches(asset)]


def write_asset(project: Project, asset: dict) -> None:
    """Schreibt/merged einen Asset-Eintrag in `assets.json` und die zugehoerige `.md`-Datei.

    Eigene Freitext-Notizen in der `.md`-Datei ueberleben Re-Indexierung (Merge statt
    Ueberschreiben, siehe Plan §1). Kommt mit der Analyse-Pipeline in M1.
    """
    raise NotImplementedError("index.write_asset kommt mit der Analyse-Pipeline in M1")
