"""BPM/Beats/Energie, Ducking-Kurven.

Kommt in M2 (Musik-Sync auf Beat-Grid), librosa ist bereits Dependency.
"""

from __future__ import annotations

from pathlib import Path


def analyze_track(path: Path) -> dict:
    """BPM, Beat-Grid, Energiekurve eines Musiktracks — gecacht unter `music/analysis/`."""
    raise NotImplementedError("audio.analyze_track kommt in M2")


def duck_curve(music_track: dict, speech_windows: list[tuple[float, float]], *, duck_db: float) -> list[dict]:
    """Gain-Kurve fuer Musik-Ducking waehrend O-Ton-Fenstern."""
    raise NotImplementedError("audio.duck_curve kommt in M2")
