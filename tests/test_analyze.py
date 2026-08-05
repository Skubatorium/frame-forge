"""Tests fuer die CV-Metriken gegen die winzigen Fixtures in `tests/fixtures/`."""

from __future__ import annotations

from pathlib import Path

import pytest

from frameforge.analyze import AnalyzeError, analyze_clip, analyze_photo, color_stats, detect_scenes
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


def test_analyze_photo_reads_heic():
    """HEIC lief frueher in `cv2.imread` -> `None` -> AnalyzeError und fiel aus dem Index."""
    result = analyze_photo(FIXTURES / "photo.heic")
    assert 0.0 <= result["quality"]["sharpness"] <= 1.0
    assert 0.0 <= result["quality"]["exposure"] <= 1.0


def test_analyze_photo_missing_file_raises():
    with pytest.raises(AnalyzeError):
        analyze_photo(FIXTURES / "does-not-exist.jpg")


def test_analyze_photo_unreadable_file_raises_with_reason(tmp_path):
    """Kein stilles Ueberspringen: die Meldung muss Datei und Ursache benennen."""
    broken = tmp_path / "kaputt.png"
    broken.write_bytes(b"keine bilddaten")
    with pytest.raises(AnalyzeError, match="kaputt.png"):
        analyze_photo(broken)


def test_detect_scenes_returns_at_least_one_scene():
    scenes = detect_scenes(FIXTURES / "clip.mp4")
    assert len(scenes) >= 1
    start, end = scenes[0]
    assert start == 0.0
    assert end > start


# -- H1: Farbstatistik aus vorhandenen Keyframes (Plan 0003) ------------------------


def _solid_jpeg(path, color):
    import cv2 as _cv2
    import numpy as _np

    image = _np.zeros((32, 32, 3), dtype=_np.uint8)
    image[:, :] = color  # BGR
    _cv2.imwrite(str(path), image)
    return path


def test_color_stats_reads_mean_and_temperature(tmp_path):
    warm = _solid_jpeg(tmp_path / "warm.jpg", (20, 60, 200))  # BGR -> viel Rot
    stats = color_stats([warm])
    assert stats["mean"]["r"] > stats["mean"]["b"]
    assert stats["temperature"] > 0  # warm
    assert stats["frames"] == 1
    assert 0 <= stats["luma"] <= 255


def test_color_stats_cool_image_has_negative_temperature(tmp_path):
    cool = _solid_jpeg(tmp_path / "cool.jpg", (200, 60, 20))
    assert color_stats([cool])["temperature"] < 0


def test_color_stats_averages_over_frames(tmp_path):
    frames = [
        _solid_jpeg(tmp_path / "a.jpg", (0, 0, 0)),
        _solid_jpeg(tmp_path / "b.jpg", (200, 200, 200)),
    ]
    stats = color_stats(frames)
    assert stats["frames"] == 2
    assert 80 < stats["luma"] < 120


def test_color_stats_without_readable_frames_is_empty(tmp_path):
    assert color_stats([tmp_path / "gibts-nicht.jpg"]) == {}
