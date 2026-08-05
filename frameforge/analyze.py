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

from frameforge import imageio

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
    # Ueber `imageio.read_bgr` statt `cv2.imread`: identisches Ergebnis fuer JPEG/PNG, kann
    # zusaetzlich HEIC. `cv2.imread` lieferte dort nur `None` — die Datei fiel still aus dem Index.
    try:
        image = imageio.read_bgr(path)
    except imageio.ImageReadError as exc:
        raise AnalyzeError(str(exc)) from exc
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


# -- Farbstatistik fuer die Angleichung zwischen Clips (Plan 0003 §H1) --------------


def color_stats(frames: list[Path]) -> dict:
    """Mittelwert/Streuung je Kanal + Farbtemperatur-Indikator aus **vorhandenen** Keyframes.

    Kostenlos im Sinne der Token-Disziplin: es wird kein Video neu dekodiert und kein Modell
    gefragt — gelesen werden die JPEGs, die `keyframes.extract_keyframes` ohnehin erzeugt hat.

    Rueckgabe:
    - `mean`/`std` je `r`/`g`/`b` (0..255) sowie `luma` (Helligkeit)
    - `temperature`: `(mean_r - mean_b) / 255` — positiv = waermer, negativ = kuehler
    - `frames`: wie viele Keyframes eingeflossen sind

    `{}`, wenn kein Frame lesbar ist (fehlende Datei ist kein Fehler, nur keine Aussage).
    """
    means: list[np.ndarray] = []
    stds: list[np.ndarray] = []
    for frame_path in frames:
        image = cv2.imread(str(frame_path))
        if image is None:
            continue
        pixels = image.reshape(-1, 3).astype(np.float64)  # OpenCV liefert BGR
        means.append(pixels.mean(axis=0))
        stds.append(pixels.std(axis=0))
    if not means:
        return {}

    mean_b, mean_g, mean_r = np.mean(means, axis=0)
    std_b, std_g, std_r = np.mean(stds, axis=0)
    luma = 0.299 * mean_r + 0.587 * mean_g + 0.114 * mean_b
    return {
        "mean": {"r": round(float(mean_r), 2), "g": round(float(mean_g), 2), "b": round(float(mean_b), 2)},
        "std": {"r": round(float(std_r), 2), "g": round(float(std_g), 2), "b": round(float(std_b), 2)},
        "luma": round(float(luma), 2),
        "temperature": round(float((mean_r - mean_b) / 255.0), 4),
        "frames": len(means),
    }
