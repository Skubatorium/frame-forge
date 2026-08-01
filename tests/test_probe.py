"""Tests fuer die ffprobe-/exiftool-Wrapper gegen die winzigen Fixtures in `tests/fixtures/`."""

from __future__ import annotations

from pathlib import Path

import pytest

from frameforge.probe import (
    ProbeError,
    captured_at_for_video,
    captured_at_from_name,
    probe_photo_exif,
    probe_video,
    trim_offset_from_name,
)

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


# -- A1: Aufnahmezeit fuer Videos (Plan 0003) --------------------------------------


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("DJI_20260720153625_0006_D.MP4", "2026-07-20T15:36:25+00:00"),
        ("IMG_20260720_153625.mp4", "2026-07-20T15:36:25+00:00"),
        ("VID_20260720_153625.mp4", "2026-07-20T15:36:25+00:00"),
        ("PXL_20260720_153625123.mp4", "2026-07-20T15:36:25+00:00"),
    ],
)
def test_captured_at_from_name(name, expected):
    assert captured_at_from_name(Path(name)).isoformat() == expected


@pytest.mark.parametrize(
    "name",
    ["clip.mp4", "DJI_0006.MP4", "DJI_20261332999999_0006.MP4"],  # kein/ungueltiges Datum
)
def test_captured_at_from_name_without_timestamp(name):
    assert captured_at_from_name(Path(name)) is None


def test_trim_offset_from_name():
    name = Path("DJI_20260720153625_0006_D-00.02.10.556-00.02.18.774-seg5.MP4")
    assert trim_offset_from_name(name) == pytest.approx((130.556, 138.774))


def test_trim_offset_from_name_without_suffix():
    assert trim_offset_from_name(Path("DJI_20260720153625_0006_D.MP4")) is None


def test_captured_at_container_and_name_yield_local_wallclock():
    """Container liefert den Zeitpunkt (UTC), der Dateiname die Zone -> lokale Wanduhrzeit."""
    path = Path("DJI_20260720153625_0006_D.MP4")
    captured_at, source = captured_at_for_video(
        path, container_tags={"creation_time": "2026-07-20T13:36:25.000000Z"}
    )
    assert captured_at == "2026-07-20T15:36:25+00:00"
    assert source == "container+name"


def test_captured_at_adds_trim_in_point():
    path = Path("DJI_20260720153625_0006_D-00.02.10.556-00.02.18.774-seg5.MP4")
    captured_at, source = captured_at_for_video(
        path, container_tags={"creation_time": "2026-07-20T13:36:25.000000Z"}
    )
    # 15:36:25 + 130.556 s = 15:38:35.556 — sekundengenaue Chronologie innerhalb eines Drehtags
    assert captured_at.startswith("2026-07-20T15:38:35")
    assert source == "container+name+trim"


def test_captured_at_falls_back_to_container_then_name_then_path(tmp_path):
    only_container = tmp_path / "clip.mp4"
    only_container.touch()
    captured_at, source = captured_at_for_video(
        only_container, container_tags={"creation_time": "2026-07-20T13:36:25Z"}
    )
    assert (captured_at, source) == ("2026-07-20T13:36:25+00:00", "container")

    assert captured_at_for_video(Path("DJI_20260720153625_0006.MP4"))[1] == "name"

    in_folder = tmp_path / "2026-07-28_Norwegen_Geiranger-Lom" / "clip.mp4"
    in_folder.parent.mkdir()
    in_folder.touch()
    captured_at, source = captured_at_for_video(in_folder)
    assert (captured_at, source) == ("2026-07-28T00:00:00+00:00", "path-date")


def test_captured_at_last_resort_is_mtime(tmp_path):
    path = tmp_path / "ohne-datum.mp4"
    path.touch()
    captured_at, source = captured_at_for_video(path)
    assert source == "mtime"
    assert captured_at.startswith("20")


def test_probe_video_reports_captured_at_and_source():
    result = probe_video(FIXTURES / "clip.mp4")
    assert result["captured_at"]
    assert result["captured_at_source"] in {"container", "name", "path-date", "mtime"}
