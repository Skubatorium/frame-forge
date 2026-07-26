"""GPX-Parsing, Zuordnung Asset <-> Ort.

Kommt mit der Ingest-Pipeline in M1 (gpxpy ist bereits Dependency).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def parse_gpx(path: Path) -> list[dict]:
    """Track-Punkte einer GPX-Datei als `[{"time": ..., "lat": ..., "lon": ...}, ...]`."""
    raise NotImplementedError("gpx.parse_gpx kommt in M1")


def nearest_location(timestamp: datetime, track: list[dict]) -> dict | None:
    """Naechster Track-Punkt zu einem Zeitstempel — ordnet Assets Orten zu."""
    raise NotImplementedError("gpx.nearest_location kommt in M1")
