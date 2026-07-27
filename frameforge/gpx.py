"""GPX-Parsing, Zuordnung Asset <-> Ort, Orte/POIs aus `locations.csv`."""

from __future__ import annotations

import csv
from datetime import datetime
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
