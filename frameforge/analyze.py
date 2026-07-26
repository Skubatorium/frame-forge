"""Schaerfe, Stabilitaet, Belichtung, Motion, Scenes — CV-Metriken pro Clip.

Kommt mit der Analyse-Pipeline in M1 (opencv-python, scenedetect).
"""

from __future__ import annotations

from pathlib import Path


def analyze_clip(path: Path, probe_data: dict) -> dict:
    """Liefert `quality` (sharpness/stability/exposure/score), `motion` und `scenes`

    im Format von `assets.json` (Plan §4).
    """
    raise NotImplementedError("analyze.analyze_clip kommt in M1")
