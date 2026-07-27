"""Tests fuer die Route-Reveal-Frame-Erzeugung."""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from frameforge.gpx import parse_gpx
from frameforge.map import (
    TILE_SIZE_PX,
    encode_alpha_video,
    fetch_tile,
    latlon_to_tile,
    render_basemap,
    render_route_frames,
)
from frameforge.probe import probe_video

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


def test_encode_alpha_video_produces_probeable_clip(track, tmp_path):
    frames_dir = tmp_path / "frames"
    render_route_frames(track, frames_dir, fps=5, dur=1.0, width=320, height=180)
    out = tmp_path / "map" / "leg-01.mov"

    result = encode_alpha_video(frames_dir, out, fps=5)

    assert result == out
    assert out.exists()
    probed = probe_video(out)
    assert probed["w"] == 320
    assert probed["h"] == 180


# -- Marker-Icon statt Default-Punkt ---------------------------------------


def test_render_route_frames_with_marker_icon_composites_it(track, tmp_path):
    icon = tmp_path / "icon.png"
    Image.new("RGBA", (10, 10), (255, 0, 0, 255)).save(icon)

    frames = render_route_frames(
        track, tmp_path / "frames", fps=2, dur=1.0, width=320, height=180, marker_icon=icon
    )

    img = np.array(Image.open(frames[-1]).convert("RGBA"))
    assert ((img == (255, 0, 0, 255)).all(axis=-1)).any()


def test_render_route_frames_with_basemap_uses_it_as_background(track, tmp_path):
    basemap = Image.new("RGBA", (320, 180), (10, 20, 30, 255))

    frames = render_route_frames(
        track, tmp_path / "frames", fps=1, dur=1.0, width=320, height=180, basemap=basemap
    )

    img = Image.open(frames[0]).convert("RGBA")
    assert img.getpixel((0, 0)) == (10, 20, 30, 255)


def test_render_route_frames_rejects_mismatched_basemap_size(track, tmp_path):
    basemap = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
    with pytest.raises(ValueError, match="passt nicht"):
        render_route_frames(
            track, tmp_path / "frames", fps=1, dur=1.0, width=320, height=180, basemap=basemap
        )


# -- Tile-Cache -------------------------------------------------------------


def _fake_tile_bytes(color=(50, 100, 150, 255)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", (TILE_SIZE_PX, TILE_SIZE_PX), color).save(buf, format="PNG")
    return buf.getvalue()


def test_latlon_to_tile_is_deterministic():
    assert latlon_to_tile(62.1049, 6.9394, 10) == latlon_to_tile(62.1049, 6.9394, 10)


def test_fetch_tile_writes_cache_file_via_injected_fetcher(tmp_path):
    calls = []

    def fetcher(url):
        calls.append(url)
        return _fake_tile_bytes()

    path = fetch_tile(10, 545, 270, tmp_path, fetcher=fetcher)

    assert path == tmp_path / "10" / "545" / "270.png"
    assert path.exists()
    assert len(calls) == 1
    assert "10" in calls[0] and "545" in calls[0] and "270" in calls[0]


def test_fetch_tile_second_call_reuses_cache_without_fetching(tmp_path):
    calls = []

    def fetcher(url):
        calls.append(url)
        return _fake_tile_bytes()

    fetch_tile(10, 545, 270, tmp_path, fetcher=fetcher)
    fetch_tile(10, 545, 270, tmp_path, fetcher=fetcher)

    assert len(calls) == 1


def test_render_basemap_composites_tiles_into_one_image(tmp_path):
    basemap = render_basemap(
        (62.09, 6.90, 62.13, 6.98), zoom=12, cache_dir=tmp_path, fetcher=lambda url: _fake_tile_bytes()
    )
    assert basemap.mode == "RGBA"
    assert basemap.width % TILE_SIZE_PX == 0
    assert basemap.height % TILE_SIZE_PX == 0
    assert basemap.getpixel((0, 0)) == (50, 100, 150, 255)


def test_render_route_frames_with_pois_draws_them(track, tmp_path):
    pois = [{"name": "Geiranger", "lat": track[0]["lat"], "lon": track[0]["lon"]}]
    frames = render_route_frames(track, tmp_path, fps=1, dur=1.0, width=320, height=180, pois=pois)
    # POI-Punkt (weiss) muss irgendwo gezeichnet sein.
    img = np.array(Image.open(frames[0]).convert("RGBA"))
    assert ((img == (255, 255, 255, 255)).all(axis=-1)).any()
