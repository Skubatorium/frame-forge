"""Karten-Frames, Marker, Route-Reveal aus GPX-Tracks.

Kommt in M3 (staticmap ist bereits Dependency, gecachte OSM-Tiles).
"""

from __future__ import annotations

from pathlib import Path


def render_route_frames(track: list[dict], out_dir: Path, *, fps: float, dur: float) -> list[Path]:
    """PNG-Sequenz mit Alpha: Route-Reveal, Marker, Figur/Auto entlang der Spur."""
    raise NotImplementedError("map.render_route_frames kommt in M3")
