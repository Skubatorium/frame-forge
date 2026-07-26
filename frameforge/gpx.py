"""GPX-Parsing, Zuordnung Asset <-> Ort."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import gpxpy


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
