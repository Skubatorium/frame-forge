"""Tests fuer die Keyframe-Extraktion gegen die winzigen Fixtures in `tests/fixtures/`."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from frameforge.keyframes import (
    DEFAULT_LONG_EDGE_PX,
    MAX_KEYFRAMES,
    KeyframeError,
    extract_keyframes,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_keyframes_video_returns_three_samples(tmp_path):
    outputs = extract_keyframes(FIXTURES / "clip.mp4", kind="video", out_dir=tmp_path, duration=2.0)
    assert len(outputs) == 3
    for path in outputs:
        assert path.exists()
        img = Image.open(path)
        assert img.format == "JPEG"
        assert max(img.size) <= DEFAULT_LONG_EDGE_PX


def test_extract_keyframes_video_caps_at_max_with_many_scenes(tmp_path):
    scenes = [(float(i), float(i) + 1) for i in range(10)]
    outputs = extract_keyframes(
        FIXTURES / "clip.mp4", kind="video", out_dir=tmp_path, duration=2.0, scenes=scenes
    )
    assert len(outputs) <= MAX_KEYFRAMES


def test_extract_keyframes_photo_returns_single_frame(tmp_path):
    outputs = extract_keyframes(FIXTURES / "photo.jpg", kind="photo", out_dir=tmp_path)
    assert len(outputs) == 1
    img = Image.open(outputs[0])
    assert img.format == "JPEG"


def test_extract_keyframes_missing_video_raises(tmp_path):
    with pytest.raises(KeyframeError):
        extract_keyframes(FIXTURES / "does-not-exist.mp4", kind="video", out_dir=tmp_path, duration=2.0)
