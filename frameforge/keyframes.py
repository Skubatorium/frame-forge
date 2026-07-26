"""Keyframe-Extraktion fuer Claude Vision.

Token-Disziplin-Regel 2 (`CLAUDE.md`): 3 Frames je Video-Clip (10 %, 50 %, 85 %),
768 px lange Kante, JPEG q80. Fotos: 1 Frame. Bei Szenenwechseln zusaetzlich je 1 Frame
pro Szene, gedeckelt auf 6 Frames insgesamt.
"""

from __future__ import annotations

from pathlib import Path

import cv2
from PIL import Image

MAX_KEYFRAMES = 6
DEFAULT_LONG_EDGE_PX = 768
DEFAULT_JPEG_QUALITY = 80
_SAMPLE_FRACTIONS = (0.10, 0.50, 0.85)


class KeyframeError(RuntimeError):
    """Ein Asset konnte nicht gelesen/kein Keyframe extrahiert werden."""


def _resize_and_save(image: Image.Image, target: Path) -> None:
    width, height = image.size
    scale = DEFAULT_LONG_EDGE_PX / max(width, height)
    if scale < 1:
        image = image.resize(
            (max(1, round(width * scale)), max(1, round(height * scale))), Image.LANCZOS
        )
    image.convert("RGB").save(target, format="JPEG", quality=DEFAULT_JPEG_QUALITY)


def extract_keyframes(
    path: Path,
    *,
    kind: str,
    out_dir: Path,
    duration: float = 0.0,
    scenes: list[tuple[float, float]] | None = None,
) -> list[Path]:
    """Extrahiert Keyframes fuer ein Video- (`kind="video"`) oder Foto-Asset (`kind="photo"`)."""
    out_dir.mkdir(parents=True, exist_ok=True)

    if kind == "photo":
        image = Image.open(path)
        target = out_dir / f"{path.stem}_kf00.jpg"
        _resize_and_save(image, target)
        return [target]

    timestamps = [duration * f for f in _SAMPLE_FRACTIONS] if duration > 0 else [0.0]
    if scenes:
        timestamps.extend((start + end) / 2 for start, end in scenes)
    timestamps = sorted(dict.fromkeys(round(t, 2) for t in timestamps))[:MAX_KEYFRAMES]

    cap = cv2.VideoCapture(str(path))
    outputs: list[Path] = []
    try:
        for i, timestamp in enumerate(timestamps):
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            ok, frame = cap.read()
            if not ok:
                continue
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            target = out_dir / f"{path.stem}_kf{i:02d}.jpg"
            _resize_and_save(image, target)
            outputs.append(target)
    finally:
        cap.release()

    if not outputs:
        raise KeyframeError(f"{path}: keine Keyframes extrahierbar")
    return outputs
