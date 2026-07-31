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
    assert result["captured_at"] is None
    assert result["gps"] is None
    assert result["source_guess"] == "unknown"  # keine Kamera-Angabe in der Fixture


def test_probe_photo_exif_missing_file_raises():
    with pytest.raises(ProbeError):
        probe_photo_exif(FIXTURES / "does-not-exist.jpg")


# -- Quelle/Kamera-Erkennung --------------------------------------------------


@pytest.mark.parametrize(
    "hint,expected",
    [
        ("DJI", "drone"),
        ("Autel Robotics", "drone"),
        ("Apple iPhone 15 Pro", "phone"),
        ("Google Pixel 8", "phone"),
        ("GoPro HERO12", "action_cam"),
        ("Insta360 X3", "action_cam"),
        ("SONY ILCE-7M4", "camera"),
        ("", "unknown"),
        (None, "unknown"),
    ],
)
def test_guess_source(hint, expected):
    from frameforge.probe import guess_source

    assert guess_source(hint) == expected


def test_guess_source_combines_hints():
    from frameforge.probe import guess_source

    assert guess_source(None, "", "DJI Mavic 3") == "drone"


def test_guess_source_name_hint_detects_marker_but_not_camera():
    from frameforge.probe import guess_source

    # Dateiname mit DJI-Marker -> drone, auch ohne EXIF.
    assert guess_source(None, name_hint="DJI_20260720140435_0009_D.MP4") == "drone"
    # Dateiname ohne Marker hebt NICHT von unknown auf camera an.
    assert guess_source(None, name_hint="clip.mp4") == "unknown"
    # Vorhandene Kamera-Angabe bleibt camera, Dateiname irrelevant.
    assert guess_source("SONY ILCE-7M4", name_hint="clip.mp4") == "camera"
