"""Tag, Etappe und Ort je Asset — aus Daten statt aus Ordnernamen (Plan 0003, §A4/A5).

Der Realbetrieb zeigte den Fehler: `gps.place` stammte aus dem Ordnernamen, und ein Ordner wie
`2026-07-28_Norwegen_Geiranger-Lom_1_Trollstigen` beschreibt eine **Etappe**, keinen **Ort** —
Trollstigen-Clips landeten unter „Geiranger". Dieses Modul leitet stattdessen ab:

`captured_at` → Tag + Etappe (`route/stages.csv`), und den Ort in dieser Reihenfolge:

1. echte GPS-Position des Assets → nächstgelegener POI aus `route/locations.csv` (Toleranz)
2. Position über `route/roadtrip.gpx` zum Aufnahmezeitpunkt → derselbe POI-Abgleich
3. Fahretappe ohne Positionsangabe → `unterwegs: <von> → <nach>`
4. Standtag ohne Positionsangabe → der Ort des Standtags
5. sonst `unknown` — und damit Eingabe für `frameforge places-todo` (A5)

`plan_assignment` rechnet nur, `apply_assignment` schreibt. Manuell gesetzte Orte
(`place_source: "manual"`) werden ohne `force=True` nie überschrieben.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from frameforge import gpx as gpx_module
from frameforge import index as index_module
from frameforge.project import Project

DEFAULT_POI_TOLERANCE_KM = 5.0

# Woher der Ort stammt. `manual` ist der einzige Wert, den die Automatik respektiert.
PLACE_SOURCES = ("gps", "gpx", "leg", "stage", "manual", "unknown")

UNKNOWN_PLACE = "unknown"


@dataclass(frozen=True)
class PlaceChange:
    asset_id: str
    field: str  # "day", "stage", "gps.place"
    old: object
    new: object


@dataclass(frozen=True)
class PlaceConflict:
    """Der bisherige (aus dem Ordnernamen geratene) Ort widerspricht dem berechneten."""

    asset_id: str
    old_place: str
    new_place: str
    source: str


@dataclass
class AssignResult:
    scanned: int = 0
    changes: list[PlaceChange] = field(default_factory=list)
    conflicts: list[PlaceConflict] = field(default_factory=list)
    protected: list[str] = field(default_factory=list)  # manuell gesetzt, nicht angefasst
    without_time: list[str] = field(default_factory=list)
    without_stage: list[str] = field(default_factory=list)  # Tag fehlt in stages.csv
    unresolved: list[str] = field(default_factory=list)  # Ort bleibt unklar (-> places-todo)
    by_day: dict[int, int] = field(default_factory=dict)
    by_place_source: dict[str, int] = field(default_factory=dict)

    @property
    def touched_assets(self) -> set[str]:
        return {c.asset_id for c in self.changes}


def _asset_time(asset: dict) -> datetime | None:
    raw = asset.get("captured_at")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _position(asset: dict) -> tuple[float, float] | None:
    gps = asset.get("gps") or {}
    lat, lon = gps.get("lat"), gps.get("lon")
    return (lat, lon) if lat is not None and lon is not None else None


def _place_for(
    asset: dict,
    *,
    timestamp: datetime | None,
    stage: dict | None,
    locations: list[dict],
    track: list[dict],
    tolerance_km: float,
) -> tuple[str, str]:
    """`(ort, quelle)` laut der Kaskade im Modul-Docstring."""
    position = _position(asset)
    source = "gps"
    if position is None and track and timestamp is not None:
        point = gpx_module.nearest_location(timestamp, track)
        if point is not None:
            position, source = (point["lat"], point["lon"]), "gpx"

    if position is not None:
        hit = gpx_module.nearest_poi(position, locations, max_km=tolerance_km)
        if hit is not None:
            return hit[0]["name"], source
        # Position bekannt, aber kein benannter Ort in Reichweite: das ist ein echter
        # Zwischenstopp auf der Strecke — die Etappe ist die ehrlichste Aussage.
    if stage is not None:
        if stage["from"] and stage["to"] and stage["from"] != stage["to"]:
            return f"unterwegs: {stage['from']} → {stage['to']}", "leg"
        standing = stage["to"] or stage["from"]
        if standing:
            return standing, "stage"
    return UNKNOWN_PLACE, "unknown"


def plan_assignment(
    project: Project,
    *,
    tolerance_km: float = DEFAULT_POI_TOLERANCE_KM,
    force: bool = False,
) -> AssignResult:
    """Berechnet `day`, `stage` und `gps.place` je Asset. Schreibt nichts.

    Raises:
        gpx.StagesError / gpx.LocationsError: bei fehlerhaften CSV-Dateien (mit Zeilennummer).
    """
    stages = gpx_module.parse_stages(project.stages_csv_path)
    locations = gpx_module.parse_locations(project.locations_csv_path)
    track = gpx_module.parse_gpx(project.gpx_path) if project.gpx_path.exists() else []

    result = AssignResult()
    for asset in index_module.load_assets(project):
        result.scanned += 1
        asset_id = asset.get("id", "?")
        timestamp = _asset_time(asset)
        if timestamp is None:
            result.without_time.append(asset_id)
            continue

        stage = gpx_module.stage_for(timestamp, stages)
        if stage is None:
            result.without_stage.append(asset_id)

        old_place = (asset.get("gps") or {}).get("place")
        if asset.get("place_source") == "manual" and not force:
            result.protected.append(asset_id)
            new_place, place_source = old_place, "manual"
        else:
            new_place, place_source = _place_for(
                asset,
                timestamp=timestamp,
                stage=stage,
                locations=locations,
                track=track,
                tolerance_km=tolerance_km,
            )
            if new_place != old_place and old_place:
                result.conflicts.append(
                    PlaceConflict(asset_id, old_place, new_place, place_source)
                )

        if place_source == "unknown":
            result.unresolved.append(asset_id)
        result.by_place_source[place_source] = result.by_place_source.get(place_source, 0) + 1

        wanted = {
            "day": stage["day"] if stage else None,
            "stage": gpx_module.stage_label(stage) if stage else None,
            "gps.place": new_place,
            "place_source": place_source,
        }
        if stage:
            result.by_day[stage["day"]] = result.by_day.get(stage["day"], 0) + 1
        for name, value in wanted.items():
            if value is None:
                continue
            old = (asset.get("gps") or {}).get("place") if name == "gps.place" else asset.get(name)
            if old != value:
                result.changes.append(PlaceChange(asset_id, name, old, value))
    return result


def apply_assignment(project: Project, result: AssignResult) -> int:
    """Schreibt `day`, `stage`, `gps.place` und `place_source`. Gibt die Asset-Anzahl zurueck."""
    if not result.changes:
        return 0

    by_asset: dict[str, list[PlaceChange]] = {}
    for change in result.changes:
        by_asset.setdefault(change.asset_id, []).append(change)

    assets = index_module.load_assets(project)
    touched = []
    for asset in assets:
        changes = by_asset.get(asset.get("id"))
        if not changes:
            continue
        for change in changes:
            if change.field == "gps.place":
                gps = asset.get("gps") or {}
                gps["place"] = change.new
                asset["gps"] = gps
            else:
                asset[change.field] = change.new
        touched.append(asset)

    index_module.save_assets(project, assets)
    for asset in touched:
        index_module.write_asset_md(project, asset)
    return len(touched)


def set_place(
    project: Project, asset_ref: str, place: str, *, kind: str = "stop"
) -> dict:
    """Setzt den Ort eines Assets von Hand (`frameforge set-place`, Plan 0003 §A5).

    `asset_ref` ist die Asset-ID **oder** der Hash. `kind="leg"` schreibt die
    Etappen-Schreibweise `unterwegs: <place>`, `kind="stop"` den Ort unverändert. Der Eintrag
    wird mit `place_source: "manual"` markiert und damit von `assign-places` nicht mehr
    überschrieben (außer mit `--force`).
    """
    if kind not in {"stop", "leg"}:
        raise ValueError("kind muss 'stop' oder 'leg' sein")

    assets = index_module.load_assets(project)
    target = next(
        (a for a in assets if a.get("id") == asset_ref or a.get("hash") == asset_ref), None
    )
    if target is None:
        raise KeyError(f"Kein Asset mit ID oder Hash '{asset_ref}'")

    value = place if kind == "stop" or place.startswith("unterwegs:") else f"unterwegs: {place}"
    gps = target.get("gps") or {}
    gps["place"] = value
    target["gps"] = gps
    target["place_source"] = "manual"

    index_module.save_assets(project, assets)
    index_module.write_asset_md(project, target)
    return target


def places_todo(project: Project, *, day: int | None = None) -> list[dict]:
    """Assets mit unklarem Ort — kompakte Worklist für `frameforge places-todo` (A5).

    Unklar heißt: `place_source` ist `unknown` oder `leg` (Vermerk „unterwegs", kein echter
    Ortsname), bzw. es fehlt ganz. Manuell gesetzte Orte tauchen nie auf.
    """
    out = []
    for asset in index_module.load_assets(project):
        source = asset.get("place_source")
        if source in {"manual", "gps", "gpx", "stage"}:
            continue
        if day is not None and asset.get("day") != day:
            continue
        out.append(
            {
                "id": asset.get("id"),
                "hash": asset.get("hash"),
                "captured_at": asset.get("captured_at"),
                "day": asset.get("day"),
                "stage": asset.get("stage"),
                "place": (asset.get("gps") or {}).get("place"),
                "place_source": source,
                "keyframes": asset.get("keyframes", [])[:1],
                "summary": (asset.get("content") or {}).get("summary", ""),
            }
        )
    out.sort(key=lambda a: (a["captured_at"] or "", a["id"] or ""))
    return out
