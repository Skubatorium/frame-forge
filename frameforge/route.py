"""Routengeometrie und Höhen beschaffen (Plan 0003, §B1/§B5).

Drei Wege zu `route/roadtrip.gpx`, in dieser Reihenfolge:

1. **Echter GPX-Track** — beste Qualität (Zeit + Höhe), nichts zu tun.
2. **KML-Export aus Google Maps** — `import_kml` wandelt ihn in dieselbe GPX-Datei um.
3. **Routing aus den Etappenpunkten** — `build_route_gpx` fragt einen Routing-Dienst nach dem
   Straßenverlauf zwischen `from`, `via` und `to` jeder Etappe.

Der Rest der Pipeline sieht in allen drei Fällen dieselbe Datei.

Netzwerkzugriffe sind **injizierbar** (`router=` / `lookup=`) — wie schon beim Tile-Fetcher in
`map.py` laufen Tests damit komplett offline, und der Cache sorgt dafür, dass eine Koordinate
im Realbetrieb genau einmal abgefragt wird.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections.abc import Callable, Sequence
from pathlib import Path

from frameforge import gpx as gpx_module
from frameforge.project import Project

# Öffentliche Demo-Instanzen. Beide haben Nutzungsbedingungen und Rate-Limits — fuer den
# gelegentlichen Einsatz eines Privatprojekts gedacht, nicht fuer Massenabfragen. Wer das
# haeufiger braucht, injiziert seinen eigenen Dienst.
DEFAULT_ROUTER_URL = "https://router.project-osrm.org/route/v1/driving/"
# Open-Meteo statt Open-Elevation: die oeffentliche Open-Elevation-Instanz lieferte im
# Realbetrieb (Etappe Skien->Geilo, 2026-08-03) fuer 175 von 416 Punkten **0 m** statt einer
# Fehlermeldung — und 0 m ist von echter Meereshoehe nicht unterscheidbar, landet also
# unbemerkt im Cache. Gegenprobe an bekannten Hoehen aus dem Reisetagebuch:
# Hakkesetstoelen 1043 m (Tagebuch 1041), Trollstigen 694 m (702), Stegastein 614 m (639).
DEFAULT_ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"

Router = Callable[[Sequence[tuple[float, float]]], list[dict]]
ElevationLookup = Callable[[Sequence[tuple[float, float]]], list[float | None]]

_HTTP_TIMEOUT_S = 30.0
_ELEVATION_BATCH = 100


class RoutingError(RuntimeError):
    """Der Routing-/Höhendienst war nicht erreichbar oder lieferte kein verwertbares Ergebnis."""


def _fetch_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"} if data else {}
    )
    try:
        with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_S) as response:
            return json.loads(response.read())
    except Exception as exc:
        raise RoutingError(f"{url}: {exc}") from exc


def _default_router(waypoints: Sequence[tuple[float, float]]) -> list[dict]:
    """OSRM: Straßenverlauf zwischen den Wegpunkten (`(lat, lon)`) als Punktliste."""
    coords = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
    data = _fetch_json(f"{DEFAULT_ROUTER_URL}{coords}?overview=full&geometries=geojson")
    routes = data.get("routes") or []
    if not routes:
        raise RoutingError(f"Routing lieferte keine Route ({data.get('code')})")
    return [
        {"lat": lat, "lon": lon}
        for lon, lat in routes[0]["geometry"]["coordinates"]
    ]


def _default_elevation_lookup(points: Sequence[tuple[float, float]]) -> list[float | None]:
    """Open-Meteo: Höhe je Koordinate, in Blöcken (die API mag keine Riesen-Requests).

    Der Dienst nimmt die Koordinaten als kommaseparierte Query-Parameter und antwortet mit
    `{"elevation": [...]}` in derselben Reihenfolge.
    """
    out: list[float | None] = []
    for start in range(0, len(points), _ELEVATION_BATCH):
        batch = points[start : start + _ELEVATION_BATCH]
        query = urllib.parse.urlencode(
            {
                "latitude": ",".join(f"{lat:.6f}" for lat, _ in batch),
                "longitude": ",".join(f"{lon:.6f}" for _, lon in batch),
            }
        )
        data = _fetch_json(f"{DEFAULT_ELEVATION_URL}?{query}")
        values = data.get("elevation")
        if not isinstance(values, list) or len(values) != len(batch):
            raise RoutingError(
                f"Höhendienst lieferte {len(values or [])} Werte für {len(batch)} Punkte"
            )
        out.extend(values)
    return out


def _coords_for(name: str, locations: list[dict]) -> tuple[float, float] | None:
    """Koordinaten eines Ortsnamens aus `locations.csv` (case-insensitiv), sonst `None`."""
    wanted = name.strip().casefold()
    for loc in locations:
        if loc["name"].casefold() == wanted:
            return (loc["lat"], loc["lon"])
    return None


def waypoints_from_stages(
    stages: list[dict], locations: list[dict]
) -> tuple[list[tuple[float, float]], list[str]]:
    """`(Wegpunkte, unbekannte Ortsnamen)` — Reihenfolge `from`, `via…`, `to` je Etappe.

    Ein Ort ohne Koordinate in `locations.csv` wird **gemeldet, nicht geraten** — er fehlt in
    der Route, und der Nutzer bekommt eine Liste, was nachzutragen ist.
    """
    waypoints: list[tuple[float, float]] = []
    unknown: list[str] = []
    for stage in stages:
        names = [stage["from"], *[v.strip() for v in stage["via"].split(";") if v.strip()], stage["to"]]
        for name in names:
            if not name:
                continue
            coords = _coords_for(name, locations)
            if coords is None:
                if name not in unknown:
                    unknown.append(name)
                continue
            if not waypoints or waypoints[-1] != coords:
                waypoints.append(coords)
    return waypoints, unknown


def import_kml(project: Project, kml_path: Path) -> Path:
    """Wandelt einen KML-Export (Google Maps) in `route/roadtrip.gpx` um. Gibt den Pfad zurueck."""
    points = gpx_module.parse_kml(kml_path)
    return gpx_module.write_gpx(points, project.gpx_path, name=f"{project.name} (aus KML)")


def build_route_gpx(
    project: Project, *, router: Router | None = None
) -> tuple[Path, list[str]]:
    """Baut `route/roadtrip.gpx` aus `stages.csv` + `locations.csv`. `(Pfad, unbekannte Orte)`.

    Rückfallebene, wenn weder ein echter Track noch ein KML-Export vorliegt.
    """
    stages = gpx_module.parse_stages(project.stages_csv_path)
    if not stages:
        raise RoutingError(f"Keine Etappen in {project.stages_csv_path} — erst /ff-route.")
    locations = gpx_module.parse_locations(project.locations_csv_path)
    waypoints, unknown = waypoints_from_stages(stages, locations)
    if len(waypoints) < 2:
        raise RoutingError(
            "Weniger als zwei Etappenpunkte mit Koordinaten — locations.csv ergaenzen "
            f"(fehlen: {', '.join(unknown) or 'keine Namen gefunden'})."
        )
    points = (router or _default_router)(waypoints)
    path = gpx_module.write_gpx(points, project.gpx_path, name=f"{project.name} (Routing)")
    return path, unknown


def elevations_for(
    project: Project, track: list[dict], *, lookup: ElevationLookup | None = None
) -> list[float | None]:
    """Höhe je Trackpunkt, projektweit gecacht in `route/elevation.json`.

    Genau eine Abfrage je Koordinate — dieselbe Token-/Kosten-Disziplin wie beim Analyse-Cache.
    Der Cache ist nach gerundeter Koordinate (5 Nachkommastellen ≈ 1 m) geschluesselt.
    """
    cache_path = project.route_dir / "elevation.json"
    cache: dict[str, float] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())

    def cached_lookup(points: Sequence[tuple[float, float]]) -> list[float | None]:
        keys = [f"{lat:.5f},{lon:.5f}" for lat, lon in points]
        missing = [(k, p) for k, p in zip(keys, points, strict=True) if k not in cache]
        if missing:
            values = (lookup or _default_elevation_lookup)([p for _, p in missing])
            for (key, _), value in zip(missing, values, strict=False):
                if value is not None:
                    cache[key] = float(value)
        return [cache.get(k) for k in keys]

    heights = gpx_module.elevation_profile(track, lookup=cached_lookup)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")
    return heights
