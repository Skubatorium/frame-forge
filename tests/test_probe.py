"""Tests fuer die ffprobe-/exiftool-Wrapper gegen die winzigen Fixtures in `tests/fixtures/`."""

from __future__ import annotations

from pathlib import Path

import pytest

from frameforge.probe import ProbeError, probe_photo_exif, probe_video

FIXTURES = Path(__file__).parent / "fixtures"


def test_probe_video_reads_basic_metadata():
    result = probe_video(FIXTURES / "clip.mp4")
    assert result["w"] == 320
    assert result["h"] == 240
    assert result["fps"] == pytest.approx(25.0)
    assert result["dur"] == pytest.approx(2.0, abs=0.2)
    assert result["codec"] == "h264"


def test_probe_video_missing_file_raises():
    with pytest.raises(ProbeError):
        probe_video(FIXTURES / "does-not-exist.mp4")


def test_probe_photo_exif_without_gps_returns_none_fields():
    result = probe_photo_exif(FIXTURES / "photo.jpg")
    assert result == {"captured_at": None, "gps": None}


def test_probe_photo_exif_missing_file_raises():
    with pytest.raises(ProbeError):
        probe_photo_exif(FIXTURES / "does-not-exist.jpg")
