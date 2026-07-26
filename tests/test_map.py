"""Tests fuer die Route-Reveal-Frame-Erzeugung."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from frameforge.gpx import parse_gpx
from frameforge.map import render_route_frames

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def track():
    return parse_gpx(FIXTURES / "route.gpx")


def test_render_route_frames_returns_expected_frame_count(track, tmp_path):
    frames = render_route_frames(track, tmp_path, fps=5, dur=1.0)
    assert len(frames) == 5
    for f in frames:
        assert f.exists()


def test_render_route_frames_are_rgba_with_transparency(track, tmp_path):
    frames = render_route_frames(track, tmp_path, fps=2, dur=1.0)
    img = Image.open(frames[0])
    assert img.mode == "RGBA"
    corner_alpha = img.getpixel((0, 0))[3]
    assert corner_alpha == 0


def test_render_route_frames_route_grows_over_time(track, tmp_path):
    frames = render_route_frames(track, tmp_path, fps=10, dur=1.0)
    first = Image.open(frames[0])
    last = Image.open(frames[-1])

    def opaque_pixel_count(img):
        return int((np.array(img)[:, :, 3] > 0).sum())

    assert opaque_pixel_count(last) >= opaque_pixel_count(first)


def test_render_route_frames_respects_custom_resolution(track, tmp_path):
    frames = render_route_frames(track, tmp_path, fps=1, dur=1.0, width=320, height=180)
    img = Image.open(frames[0])
    assert img.size == (320, 180)


def test_render_route_frames_requires_at_least_two_points(tmp_path):
    with pytest.raises(ValueError, match="mindestens 2"):
        render_route_frames([{"lat": 0.0, "lon": 0.0}], tmp_path, fps=1, dur=1.0)
