"""GPX-Parsing, Zuordnung Asset <-> Ort, Orte/POIs aus `locations.csv`."""

from __future__ import annotations

import csv
from datetime import date, datetime
from itertools import pairwise
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from xml.etree import ElementTree

import gpxpy
import gpxpy.gpx


class LocationsError(ValueError):
    """`locations.csv` fehlt eine Pflichtspalte oder enthält ungültige Koordinaten."""


def parse_locations(path: Path) -> list[dict]:
    """Liest `route/locations.csv` — Übernachtungen/POIs/manuelle Korrekturen.

    Erwartete Spalten (Header): `name`, `lat`, `lon`, optional `type` (`overnight`/`poi`/…)
    und `day` (Etappen-/Tagesnummer). Rückgabe:
    `[{"name", "lat", "lon", "type", "day"}, ...]`. Leere Liste, wenn die Datei fehlt.
    """
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        missing = {"name", "lat", "lon"} - set(reader.fieldnames or [])
        if missing:
            raise LocationsError(f"{path}: Spalten fehlen: {sorted(missing)} (erwartet: name,lat,lon)")
        for i, row in enumerate(reader, start=2):  # Zeile 1 = Header
            try:
                lat, lon = float(row["lat"]), float(row["lon"])
            except (TypeError, ValueError) as exc:
                raise LocationsError(f"{path} Zeile {i}: ungültige Koordinate ({exc})") from exc
            out.append(
                {
                    "name": (row.get("name") or "").strip(),
                    "lat": lat,
                    "lon": lon,
                    "type": (row.get("type") or "poi").strip(),
                    "day": (row.get("day") or "").strip(),
                }
            )
    return out


EARTH_RADIUS_KM = 6371.0088


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Großkreis-Distanz zwischen zwei `(lat, lon)`-Punkten in Kilometern.

    Reicht für Kilometerzähler und POI-Nähe vollkommen aus; eine ellipsoidische Formel
    (Vincenty) wäre hier Genauigkeit, die niemand sieht.
    """
    lat1, lon1 = radians(a[0]), radians(a[1])
    lat2, lon2 = radians(b[0]), radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(h))


def nearest_poi(
    position: tuple[float, float], locations: list[dict], *, max_km: float
) -> tuple[dict, float] | None:
    """Nächstgelegener Ort aus `locations.csv` innerhalb `max_km`, sonst `None`.

    Ohne Toleranzgrenze bekäme ein Clip mitten auf einer Passstraße den Namen der 80 km
    entfernten Übernachtung — genau der Fehler, den A4 abstellen soll.
    """
    candidates = [(loc, haversine_km(position, (loc["lat"], loc["lon"]))) for loc in locations]
    if not candidates:
        return None
    best, distance = min(candidates, key=lambda pair: pair[1])
    return (best, distance) if distance <= max_km else None


class StagesError(ValueError):
    """`stages.csv` fehlt eine Pflichtspalte oder enthält eine ungültige Zeile."""


def parse_stages(path: Path) -> list[dict]:
    """Liest `route/stages.csv` — die Etappenliste der Reise (Plan 0003 §A3).

    Pflichtspalten: `day`, `date`, `from`, `to`. Optional: `via`, `km`, `overnight`, `note`.
    Rückgabe je Zeile: `{"day": int, "date": date, "from", "to", "via", "km": float|None,
    "overnight", "note"}`, sortiert nach Tag. Leere Liste, wenn die Datei fehlt.

    `km` bleibt `None`, wenn die Spalte leer ist — „unbekannt" ist eine gültige Angabe und wird
    **nicht** geschätzt (Plan 0003: eine erfundene Zahl ist schlimmer als eine fehlende).
    """
    if not path.exists():
        return []
    required = {"day", "date", "from", "to"}
    out: list[dict] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise StagesError(
                f"{path}: Spalten fehlen: {sorted(missing)} (erwartet mindestens: day,date,from,to)"
            )
        for i, row in enumerate(reader, start=2):  # Zeile 1 = Header
            if not (row.get("day") or "").strip():
                continue  # Leerzeile am Dateiende
            try:
                day = int(str(row["day"]).strip())
            except ValueError as exc:
                raise StagesError(f"{path} Zeile {i}: 'day' ist keine Zahl ({row['day']!r})") from exc
            try:
                stage_date = date.fromisoformat(str(row["date"]).strip())
            except ValueError as exc:
                raise StagesError(
                    f"{path} Zeile {i}: 'date' ist kein ISO-Datum YYYY-MM-DD ({row['date']!r})"
                ) from exc
            km_raw = (row.get("km") or "").strip()
            try:
                km = float(km_raw.replace(",", ".")) if km_raw else None
            except ValueError as exc:
                raise StagesError(f"{path} Zeile {i}: 'km' ist keine Zahl ({km_raw!r})") from exc
            out.append(
                {
                    "day": day,
                    "date": stage_date,
                    "from": (row.get("from") or "").strip(),
                    "to": (row.get("to") or "").strip(),
                    "via": (row.get("via") or "").strip(),
                    "km": km,
                    "overnight": (row.get("overnight") or "").strip(),
                    "note": (row.get("note") or "").strip(),
                }
            )
    out.sort(key=lambda s: s["day"])
    return out


def stage_for(timestamp: datetime, stages: list[dict]) -> dict | None:
    """Etappe eines Zeitpunkts über das Datum, oder `None` außerhalb der Reise.

    Bewusst datumsbasiert und ohne Toleranz: eine Aufnahme um 23:50 gehört zum Tag, an dem sie
    entstanden ist — welcher Etappe sie erzählerisch zugeschlagen wird, entscheidet der Schnitt,
    nicht diese Funktion.
    """
    day = timestamp.date()
    return next((stage for stage in stages if stage["date"] == day), None)


def stage_label(stage: dict) -> str:
    """`"Geiranger → Lom"` bzw. `"Lom"` bei einem Standtag — für Overlays und Reports."""
    if stage["from"] and stage["to"] and stage["from"] != stage["to"]:
        return f"{stage['from']} → {stage['to']}"
    return stage["to"] or stage["from"]


def parse_gpx(path: Path, *, require_time: bool = True) -> list[dict]:
    """Track-Punkte einer GPX-Datei als `[{"time", "lat", "lon", "ele"}, ...]`.

    Mit `require_time=True` (Default, unveraendertes Verhalten) werden Punkte ohne Zeitstempel
    uebersprungen und der Rest chronologisch sortiert — fuer die Asset-Zuordnung per Zeit sind
    zeitlose Punkte nutzlos. Mit `require_time=False` bleibt die Dokumentreihenfolge und alle
    Punkte erhalten: eine aus KML oder Routing erzeugte Strecke (Plan 0003 §B5) ist reine
    Geometrie und traegt naturgemaess keine Zeiten.
    """
    with path.open() as fh:
        gpx = gpxpy.parse(fh)

    points = [
        {
            "time": point.time,
            "lat": point.latitude,
            "lon": point.longitude,
            "ele": point.elevation,
        }
        for track in gpx.tracks
        for segment in track.segments
        for point in segment.points
        if point.time is not None or not require_time
    ]
    if require_time:
        points.sort(key=lambda p: p["time"])
    return points


class KmlError(ValueError):
    """`.kml` liess sich nicht parsen oder enthaelt keine Route."""


_KML_NS = "{http://www.opengis.net/kml/2.2}"


def parse_kml(path: Path) -> list[dict]:
    """Punkte einer KML-Datei (Google-Maps-Export) als `[{"lat", "lon", "ele"}, ...]`.

    `gpxpy` liest nur GPX; ein Google-Maps-Export ist aber KML. Gelesen werden alle
    `<LineString><coordinates>`-Blöcke in Dokumentreihenfolge (Format `lon,lat[,ele]`).
    KML kennt keine Zeitstempel je Punkt — die Route ist Geometrie, keine Aufzeichnung.
    """
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError as exc:
        raise KmlError(f"{path}: kein gueltiges KML ({exc})") from exc

    points: list[dict] = []
    for coords in root.iter(f"{_KML_NS}coordinates"):
        for chunk in (coords.text or "").split():
            parts = chunk.split(",")
            if len(parts) < 2:
                continue
            try:
                lon, lat = float(parts[0]), float(parts[1])
                ele = float(parts[2]) if len(parts) > 2 else None
            except ValueError:
                continue
            points.append({"lat": lat, "lon": lon, "ele": ele})
    if not points:
        raise KmlError(f"{path}: keine Koordinaten gefunden (LineString/coordinates fehlt)")
    return points


def write_gpx(points: list[dict], path: Path, *, name: str = "route") -> Path:
    """Schreibt Punkte (`lat`/`lon`, optional `ele`/`time`) als GPX-Track. Gibt den Pfad zurueck.

    Damit sehen alle drei Beschaffungswege aus Plan 0003 §B5 (echter Track, KML-Export,
    berechnetes Routing) fuer den Rest der Pipeline identisch aus.
    """
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack(name=name)
    segment = gpxpy.gpx.GPXTrackSegment()
    for point in points:
        segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                latitude=point["lat"],
                longitude=point["lon"],
                elevation=point.get("ele"),
                time=point.get("time"),
            )
        )
    track.segments.append(segment)
    gpx.tracks.append(track)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(gpx.to_xml(), encoding="utf-8")
    return path


def cumulative_km(track: list[dict]) -> list[float]:
    """Kumulierte Strecke je Trackpunkt (erster Punkt = 0.0) — Kilometerzähler fürs HUD."""
    out = [0.0]
    for prev, cur in pairwise(track):
        out.append(out[-1] + haversine_km((prev["lat"], prev["lon"]), (cur["lat"], cur["lon"])))
    return out[: len(track)]


def elevation_profile(track: list[dict], *, lookup=None) -> list[float | None]:
    """Höhe je Trackpunkt. `None`, wo weder GPX-`ele` noch `lookup` etwas liefert.

    `lookup` ist injizierbar (`Callable[[list[tuple[float, float]]], list[float | None]]`),
    damit Tests offline laufen und ein Höhendienst nur dort abgefragt wird, wo wirklich Werte
    fehlen. Der Aufrufer (`route.elevations_for`) cacht das Ergebnis projektweit.
    """
    heights: list[float | None] = [p.get("ele") for p in track]
    missing = [i for i, h in enumerate(heights) if h is None]
    if missing and lookup is not None:
        filled = lookup([(track[i]["lat"], track[i]["lon"]) for i in missing])
        for i, value in zip(missing, filled, strict=False):
            heights[i] = value
    return heights


def total_ascent_m(heights: list[float | None]) -> float:
    """Summe aller Anstiege (Höhenmeter aufwärts). Lücken (`None`) werden übersprungen."""
    known = [h for h in heights if h is not None]
    return sum(max(0.0, b - a) for a, b in pairwise(known))


def nearest_location(timestamp: datetime, track: list[dict]) -> dict | None:
    """Naechster Track-Punkt zu einem Zeitstempel — ordnet Assets Orten zu.

    `None`, wenn `track` leer ist. Keine Distanz-/Zeit-Obergrenze — ein Asset weit vor/nach
    der Tour bekommt trotzdem den zeitlich naechsten Punkt zugeordnet; das ist Aufgabe des
    Aufrufers zu bewerten (z.B. ueber einen Toleranzwert in der Ingest-Pipeline).
    """
    if not track:
        return None
    return min(track, key=lambda p: abs((p["time"] - timestamp).total_seconds()))
