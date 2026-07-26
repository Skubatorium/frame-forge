"""Keyframe-Extraktion fuer Claude Vision.

Token-Disziplin-Regel 2 (`CLAUDE.md`): 3 Frames je Clip (10 %, 50 %, 85 %),
768 px lange Kante, JPEG q80. Fotos: 1 Frame. Bei Szenenwechseln zusaetzlich
je 1 Frame pro Szene, gedeckelt auf 6. Kommt mit der Analyse-Pipeline in M1.
"""

from __future__ import annotations

from pathlib import Path

MAX_KEYFRAMES = 6
DEFAULT_LONG_EDGE_PX = 768
DEFAULT_JPEG_QUALITY = 80


def extract_keyframes(path: Path, *, scenes: list[tuple[float, float]] | None = None) -> list[Path]:
    """Extrahiert Keyframes fuer ein Video- oder Foto-Asset. Kommt in M1."""
    raise NotImplementedError("keyframes.extract_keyframes kommt in M1")
