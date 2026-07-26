"""Tests fuer die CV-Metriken gegen die winzigen Fixtures in `tests/fixtures/`."""

from __future__ import annotations

from pathlib import Path

import pytest

from frameforge.analyze import AnalyzeError, analyze_clip, analyze_photo, detect_scenes
from frameforge.probe import probe_video

FIXTURES = Path(__file__).parent / "fixtures"


def test_analyze_clip_returns_quality_motion_scenes():
    probe_data = probe_video(FIXTURES / "clip.mp4")
    result = analyze_clip(FIXTURES / "clip.mp4", probe_data)

    for key in ("sharpness", "stability", "exposure", "score"):
        assert 0.0 <= result["quality"][key] <= 1.0
    assert result["motion"]["type"] in ("static", "handheld")
    assert 0.0 <= result["motion"]["speed"] <= 1.0
    assert len(result["scenes"]) >= 1
    assert result["scenes"][0]["start"] == 0.0


def test_analyze_clip_missing_file_raises():
    with pytest.raises(AnalyzeError):
        analyze_clip(FIXTURES / "does-not-exist.mp4", {"dur": 2.0})


def test_analyze_photo_returns_quality_without_motion():
    result = analyze_photo(FIXTURES / "photo.jpg")
    assert "motion" not in result
    assert "scenes" not in result
    assert 0.0 <= result["quality"]["sharpness"] <= 1.0
    assert 0.0 <= result["quality"]["exposure"] <= 1.0


def test_analyze_photo_missing_file_raises():
    with pytest.raises(AnalyzeError):
        analyze_photo(FIXTURES / "does-not-exist.jpg")


def test_detect_scenes_returns_at_least_one_scene():
    scenes = detect_scenes(FIXTURES / "clip.mp4")
    assert len(scenes) >= 1
    start, end = scenes[0]
    assert start == 0.0
    assert end > start
