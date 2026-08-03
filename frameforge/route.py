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
import re
import urllib.parse
import urllib.request
from collections.abc import Callable, Sequence
from itertools import pairwise
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
    """Koordinaten eines Ortsnamens aus `locations.csv` (case-insensitiv), sonst `None`.

    Zweiter Versuch bei `via`-Angaben, die den Ort in einen Satz einbetten: `"E134 über
    Notodden"` oder `"Fähre Larvik–Hirtshals 08:00"` — steht ein Ortsname aus `locations.csv`
    als **eigenes Wort** darin, gilt er als gemeint. Der laengste Treffer gewinnt, damit
    `"Hamburg Hafen"` nicht von `"Hamburg"` verdraengt wird. Reine Teilstring-Treffer ohne
    Wortgrenze zaehlen nicht (sonst wuerde `"Lom"` in `"Blomsterdalen"` anschlagen).
    """
    wanted = name.strip().casefold()
    for loc in locations:
        if loc["name"].casefold() == wanted:
            return (loc["lat"], loc["lon"])

    treffer = [
        loc
        for loc in locations
        if re.search(rf"(?<!\w){re.escape(loc['name'].casefold())}(?!\w)", wanted)
    ]
    if treffer:
        best = max(treffer, key=lambda loc: len(loc["name"]))
        return (best["lat"], best["lon"])
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


# Woran eine Faehrpassage in `stages.csv` erkennbar ist. Der Nutzer schreibt sie ohnehin in
# die `via`-Spalte ("Fähre Color Line Hirtshals–Larvik") — das ist eine **Angabe**, keine
# Vermutung, und damit die verlaesslichste Quelle.
FERRY_MARKERS = ("fähre", "faehre", "ferry", "ferge")

# Nur noch Sicherheitsnetz, falls eine Faehre nicht als solche benannt ist: ab diesem
# Verhaeltnis Routing-Distanz zu Luftlinie liegt mit Sicherheit Wasser dazwischen. Bewusst
# hoch angesetzt — Fjordstrassen haben legitim Faktoren um 2,5 (Geilo->Aurland kam mit dem
# frueheren Schwellwert 2,5 faelschlich als Seeweg heraus: 126 statt 190 km).
SEA_DETOUR_FACTOR = 4.0


def _is_ferry(name: str) -> bool:
    return any(marker in name.casefold() for marker in FERRY_MARKERS)


def _ferry_ports(name: str, locations: list[dict]) -> list[tuple[float, float]]:
    """Haefen, die ein Faehr-Eintrag nennt — in der Reihenfolge, in der sie im Text stehen.

    `"Fähre Color Line Hirtshals–Larvik"` nennt beide Enden der Passage; sind sie in
    `locations.csv` bekannt, wird daraus ein echtes Seesegment statt eines groben Sprungs.
    Eine kurze Fjordfaehre steht dagegen oft selbst als POI (`"Fähre Mannheller–Fodnes"`) —
    dann ist sie ein normaler Wegpunkt und dieser Weg greift nicht.
    """
    wanted = name.casefold()
    treffer = []
    for loc in locations:
        match = re.search(rf"(?<!\w){re.escape(loc['name'].casefold())}(?!\w)", wanted)
        if match:
            treffer.append((match.start(), (loc["lat"], loc["lon"])))
    return [coords for _, coords in sorted(treffer)]


def _segment_km(
    a: tuple[float, float], b: tuple[float, float], router: Router, *, ferry: bool = False
) -> tuple[float, str]:
    """`(km, art)` zwischen zwei Punkten — `art` ist `"land"` oder `"see"`.

    Eine Faehrpassage kann der Router nicht: er faehrt ums Wasser herum. Ist das Segment als
    Faehre benannt (`ferry=True`) oder weicht die gefahrene Strecke um mehr als
    `SEA_DETOUR_FACTOR` von der Luftlinie ab, wird die Luftlinie angesetzt — ein Schiff faehrt
    naeherungsweise gerade.
    """
    luftlinie = gpx_module.haversine_km(a, b)
    if ferry:
        return luftlinie, "see"
    try:
        strecke = gpx_module.cumulative_km(router([a, b]))[-1]
    except (RoutingError, IndexError):
        return luftlinie, "see"
    if luftlinie > 0 and strecke / luftlinie > SEA_DETOUR_FACTOR:
        return luftlinie, "see"
    return strecke, "land"


def estimate_stage_km(
    stage: dict, locations: list[dict], *, router: Router | None = None
) -> dict:
    """Schaetzt die Distanz einer Etappe aus den Koordinaten ihrer Wegpunkte.

    Fuer Etappen, bei denen in `stages.csv` keine Kilometerangabe steht. Rueckgabe:
    `{"km", "segments", "unresolved", "has_sea"}` — `unresolved` nennt die Wegpunkte ohne
    Koordinate, die uebersprungen wurden, damit nichts still unter den Tisch faellt.

    Ein Standtag (`from == to`, keine `via`) ergibt 0 km, keine Schaetzung.
    """
    route = router or _default_router
    namen = [stage["from"], *[v.strip() for v in stage["via"].split(";") if v.strip()], stage["to"]]

    punkte: list[tuple[float, float]] = []
    ferry_ab: set[int] = set()  # Index des Punktes, ab dem eine Faehrpassage beginnt
    unresolved: list[str] = []
    for name in namen:
        if not name:
            continue
        if _is_ferry(name):
            exakt = any(loc["name"].casefold() == name.strip().casefold() for loc in locations)
            haefen = [] if exakt else _ferry_ports(name, locations)
            if len(haefen) >= 2:
                # Beide Enden bekannt: als echte Wegpunkte einsetzen, dazwischen Seeweg.
                for hafen in haefen:
                    if not punkte or punkte[-1] != hafen:
                        punkte.append(hafen)
                        if len(punkte) > 1:
                            ferry_ab.add(len(punkte) - 2)
                continue
            if not exakt:
                # Enden unbekannt: der Uebergang zum naechsten Punkt gilt als Seeweg.
                if punkte:
                    ferry_ab.add(len(punkte) - 1)
                continue
            # Exakter POI-Treffer (kurze Fjordfaehre): normaler Wegpunkt, unten aufgeloest.
        coords = _coords_for(name, locations)
        if coords is None:
            unresolved.append(name)
            continue
        if not punkte or punkte[-1] != coords:
            punkte.append(coords)

    if len(punkte) < 2:
        return {"km": 0.0, "segments": [], "unresolved": unresolved, "has_sea": False}

    gesamt, segments, has_sea = 0.0, [], False
    for i, (a, b) in enumerate(pairwise(punkte)):
        km, art = _segment_km(a, b, route, ferry=i in ferry_ab)
        gesamt += km
        segments.append({"km": round(km, 1), "art": art})
        has_sea = has_sea or art == "see"
    return {
        "km": round(gesamt, 1),
        "segments": segments,
        "unresolved": unresolved,
        "has_sea": has_sea,
    }


def stage_km_table(
    stages: list[dict], locations: list[dict], *, router: Router | None = None
) -> list[dict]:
    """Kilometer je Etappe: Nutzerangabe, wo vorhanden — sonst aus den Koordinaten geschaetzt.

    Rueckgabe je Etappe: `{"day", "km", "source", "km_estimated", "km_user"}`. `source` ist
    `"stages.csv"` oder `"geschaetzt"`, damit im Report und in der Anzeige unterscheidbar
    bleibt, welche Zahl belegt ist und welche gerechnet.

    Die Nutzerangabe gewinnt **immer**: sie stammt vom Tacho, die Schaetzung aus einer
    Routenberechnung, die Umwege, Tankstopps und Routenwahl nicht kennt (an den belegten
    Etappen dieser Reise ~25 % mittlere Abweichung).
    """
    out = []
    for stage in stages:
        geschaetzt = estimate_stage_km(stage, locations, router=router)["km"]
        eigen = stage.get("km")
        out.append(
            {
                "day": stage["day"],
                "km": eigen if eigen is not None else geschaetzt,
                "source": "stages.csv" if eigen is not None else "geschaetzt",
                "km_user": eigen,
                "km_estimated": geschaetzt,
            }
        )
    return out


def km_offset_for(day: int, table: list[dict]) -> float:
    """Kilometerstand zu Beginn eines Reisetags — Summe aller vorherigen Etappen."""
    return round(sum(row["km"] or 0.0 for row in table if row["day"] < day), 1)


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
