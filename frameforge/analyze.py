"""Schaerfe, Stabilitaet, Belichtung, Motion, Scenes — CV-Metriken pro Asset.

Heuristiken, kein ML-Modell: Schaerfe ueber Laplacian-Varianz, Belichtung ueber die
Naehe des mittleren Helligkeitswerts zu Mittelgrau, Stabilitaet ueber die mittlere
Frame-zu-Frame-Differenz dreier Sample-Frames. Genau genug, um Material grob zu sortieren
(niedrig/hoch), nicht gedacht als praezise Bildqualitaetsmessung.
"""

from __future__ import annotations

from itertools import pairwise
from pathlib import Path

import cv2
import numpy as np

_SHARPNESS_NORM = 500.0
_STABILITY_NORM = 50.0
_SAMPLE_FRACTIONS = (0.10, 0.50, 0.85)


class AnalyzeError(RuntimeError):
    """Ein Asset konnte nicht gelesen/analysiert werden."""


def _sharpness_score(gray: np.ndarray) -> float:
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(min(variance / _SHARPNESS_NORM, 1.0))


def _exposure_score(gray: np.ndarray) -> float:
    mean = float(gray.mean())
    return float(max(0.0, 1.0 - abs(mean - 128.0) / 128.0))


def _stability_score(frames: list[np.ndarray]) -> float:
    if len(frames) < 2:
        return 1.0
    diffs = []
    for a, b in pairwise(frames):
        ga = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY).astype(np.float64)
        gb = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY).astype(np.float64)
        diffs.append(float(np.abs(ga - gb).mean()))
    avg_diff = sum(diffs) / len(diffs)
    return float(max(0.0, 1.0 - avg_diff / _STABILITY_NORM))


def _read_frame_at(cap: cv2.VideoCapture, timestamp_s: float) -> np.ndarray | None:
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_s * 1000)
    ok, frame = cap.read()
    return frame if ok else None


def detect_scenes(path: Path) -> list[tuple[float, float]]:
    """Szenenwechsel via `scenedetect` (Content-Detector). Fallback: eine Szene = ganzer Clip."""
    from scenedetect import SceneManager, open_video
    from scenedetect.detectors import ContentDetector

    video = open_video(str(path))
    manager = SceneManager()
    manager.add_detector(ContentDetector())
    manager.detect_scenes(video)
    scene_list = manager.get_scene_list()
    if not scene_list:
        return [(0.0, video.duration.seconds)]
    return [(start.seconds, end.seconds) for start, end in scene_list]


def analyze_clip(path: Path, probe_data: dict) -> dict:
    """Liefert `quality`, `motion` und `scenes` im Format von `assets.json` (Plan §4)."""
    duration = float(probe_data.get("dur", 0.0))
    timestamps = [duration * f for f in _SAMPLE_FRACTIONS] if duration > 0 else [0.0]

    cap = cv2.VideoCapture(str(path))
    try:
        frames = [f for t in timestamps if (f := _read_frame_at(cap, t)) is not None]
    finally:
        cap.release()
    if not frames:
        raise AnalyzeError(f"{path}: keine Frames lesbar")

    grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    sharpness = sum(_sharpness_score(g) for g in grays) / len(grays)
    exposure = sum(_exposure_score(g) for g in grays) / len(grays)
    stability = _stability_score(frames)
    score = (sharpness + exposure + stability) / 3

    return {
        "quality": {
            "sharpness": round(sharpness, 3),
            "stability": round(stability, 3),
            "exposure": round(exposure, 3),
            "score": round(score, 3),
        },
        "motion": {
            "type": "static" if stability > 0.85 else "handheld",
            "speed": round(1.0 - stability, 3),
        },
        "scenes": [
            {"start": round(start, 2), "end": round(end, 2)} for start, end in detect_scenes(path)
        ],
    }


def analyze_photo(path: Path) -> dict:
    """Liefert `quality` (ohne `stability`/`motion`/`scenes` — nicht anwendbar auf Standbilder)."""
    image = cv2.imread(str(path))
    if image is None:
        raise AnalyzeError(f"{path}: Bild nicht lesbar")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpness = _sharpness_score(gray)
    exposure = _exposure_score(gray)
    return {
        "quality": {
            "sharpness": round(sharpness, 3),
            "exposure": round(exposure, 3),
            "score": round((sharpness + exposure) / 2, 3),
        }
    }
