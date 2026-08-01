"""GPX-Parsing, Zuordnung Asset <-> Ort, Orte/POIs aus `locations.csv`."""

from __future__ import annotations

import csv
from datetime import date, datetime
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

import gpxpy


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


def parse_gpx(path: Path) -> list[dict]:
    """Track-Punkte einer GPX-Datei als `[{"time": ..., "lat": ..., "lon": ...}, ...]`,

    chronologisch sortiert, ueber alle Tracks/Segmente hinweg. Punkte ohne Zeitstempel
    werden uebersprungen — sie sind fuer die Asset-Zuordnung per Zeit nutzlos.
    """
    with path.open() as fh:
        gpx = gpxpy.parse(fh)

    points = [
        {"time": point.time, "lat": point.latitude, "lon": point.longitude}
        for track in gpx.tracks
        for segment in track.segments
        for point in segment.points
        if point.time is not None
    ]
    points.sort(key=lambda p: p["time"])
    return points


def nearest_location(timestamp: datetime, track: list[dict]) -> dict | None:
    """Naechster Track-Punkt zu einem Zeitstempel — ordnet Assets Orten zu.

    `None`, wenn `track` leer ist. Keine Distanz-/Zeit-Obergrenze — ein Asset weit vor/nach
    der Tour bekommt trotzdem den zeitlich naechsten Punkt zugeordnet; das ist Aufgabe des
    Aufrufers zu bewerten (z.B. ueber einen Toleranzwert in der Ingest-Pipeline).
    """
    if not track:
        return None
    return min(track, key=lambda p: abs((p["time"] - timestamp).total_seconds()))
