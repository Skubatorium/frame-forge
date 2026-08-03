"""Tests fuer die Route-Reveal-Frame-Erzeugung."""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from frameforge.gpx import parse_gpx
from frameforge.map import (
    TILE_SIZE_PX,
    _dwell_schedule,
    _profile_polyline,
    basemap_viewport,
    encode_alpha_video,
    fetch_tile,
    latlon_to_pixel,
    latlon_to_tile,
    pixel_to_latlon,
    render_basemap,
    render_hud_frames,
    render_route_frames,
    smooth_centers,
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


# -- B2: Web-Mercator, mitwandernder Viewport, Haltezeit (Plan 0003) ----------------


def test_latlon_to_pixel_matches_tile_index():
    """Weltpixel/256 muss exakt der Kachelindex sein — sonst passt die Route nicht zur Karte."""
    lat, lon, zoom = 62.4581, 7.6706, 10
    px, py = latlon_to_pixel(lat, lon, zoom)
    assert (int(px // 256), int(py // 256)) == latlon_to_tile(lat, lon, zoom)


def test_pixel_to_latlon_roundtrip():
    lat, lon, zoom = 62.4581, 7.6706, 12
    back = pixel_to_latlon(*latlon_to_pixel(lat, lon, zoom), zoom)
    assert back[0] == pytest.approx(lat, abs=1e-6)
    assert back[1] == pytest.approx(lon, abs=1e-6)


def test_smooth_centers_removes_jitter():
    jittery = [(0.0, 0.0), (10.0, 0.0), (0.0, 0.0), (10.0, 0.0), (0.0, 0.0)]
    smoothed = smooth_centers(jittery, 3)
    assert smooth_centers(jittery, 1) == jittery  # window <= 1: unveraendert
    middle = [x for x, _ in smoothed[1:-1]]
    assert all(2.0 < x < 8.0 for x in middle)  # Ausschlaege gedaempft


def test_follow_viewport_centers_on_the_marker(tmp_path):
    track = [{"lat": 62.0 + i * 0.05, "lon": 7.0 + i * 0.05} for i in range(10)]
    frames = render_route_frames(
        track, tmp_path / "follow", fps=2, dur=2, width=200, height=200,
        viewport="follow", zoom=10, ease_s=0,
    )
    assert len(frames) == 4
    for frame in frames:
        image = Image.open(frame).convert("RGBA")
        # Der Marker ist im Follow-Modus per Definition in der Bildmitte.
        assert image.getpixel((100, 100))[3] > 0


def test_follow_requires_zoom(tmp_path):
    track = [{"lat": 62.0, "lon": 7.0}, {"lat": 62.1, "lon": 7.1}]
    with pytest.raises(ValueError, match="zoom"):
        render_route_frames(track, tmp_path / "x", fps=1, dur=1, viewport="follow")


def test_unknown_viewport_raises(tmp_path):
    track = [{"lat": 62.0, "lon": 7.0}, {"lat": 62.1, "lon": 7.1}]
    with pytest.raises(ValueError, match="viewport"):
        render_route_frames(track, tmp_path / "x", fps=1, dur=1, viewport="zoomies")


def test_fit_viewport_is_unchanged_by_the_new_parameters(tmp_path):
    """Regression Plan 0003 §0: Default-Aufruf rendert exakt wie vorher."""
    track = [{"lat": 62.0 + i * 0.05, "lon": 7.0 + i * 0.05} for i in range(6)]
    before = render_route_frames(track, tmp_path / "a", fps=2, dur=1, width=120, height=120)
    after = render_route_frames(
        track, tmp_path / "b", fps=2, dur=1, width=120, height=120,
        viewport="fit", dwell_s=0.0,
    )
    assert [p.read_bytes() for p in before] == [p.read_bytes() for p in after]


def test_dwell_pauses_at_pois_without_changing_duration(tmp_path):
    track = [{"lat": 62.0 + i * 0.02, "lon": 7.0} for i in range(20)]
    pois = [{"name": "Mitte", "lat": 62.2, "lon": 7.0}]
    frames = render_route_frames(
        track, tmp_path / "dwell", fps=4, dur=3, width=120, height=120,
        pois=pois, dwell_s=1.0,
    )
    assert len(frames) == 12  # Dauer unveraendert: 4 fps * 3 s

    schedule = _dwell_schedule(track, pois, frame_count=12, fps=4, dwell_s=1.0)
    assert len(schedule) == 12
    assert schedule == sorted(schedule)  # Reveal geht nie rueckwaerts
    assert max(schedule.count(v) for v in set(schedule)) >= 4  # eine echte Pause (>= 1 s)


def test_basemap_viewport_returns_exact_pixel_size(tmp_path):
    calls: list[str] = []

    def fake_fetcher(url: str) -> bytes:
        calls.append(url)
        buffer = io.BytesIO()
        Image.new("RGBA", (256, 256), (10, 20, 30, 255)).save(buffer, format="PNG")
        return buffer.getvalue()

    image = basemap_viewport(
        (62.4581, 7.6706), 10, (300, 200), tmp_path / "tiles", fetcher=fake_fetcher
    )
    assert image.size == (300, 200)
    assert image.getpixel((150, 100))[:3] == (10, 20, 30)
    assert calls  # Kacheln wurden geholt ...
    basemap_viewport((62.4581, 7.6706), 10, (300, 200), tmp_path / "tiles", fetcher=fake_fetcher)
    assert len(calls) == len(set(calls))  # ... und beim zweiten Mal aus dem Cache gelesen


# -- B3: Etappen-HUD als eigene Overlay-Sequenz -------------------------------------


def test_render_hud_frames_writes_one_png_per_frame(tmp_path):
    import yaml

    tokens = yaml.safe_load(Path("templates/project/tokens.example.yaml").read_text())
    track = [{"lat": 62.0 + i * 0.02, "lon": 7.0} for i in range(10)]
    stage = {"day": 9, "date": date(2026, 7, 28), "from": "Geiranger", "to": "Lom", "via": ""}

    frames = render_hud_frames(
        tmp_path / "hud",
        template_path=Path("templates/svg/map-hud.svg"),
        tokens=tokens,
        fps=4,
        dur=2,
        width=640,
        height=360,
        track=track,
        stage=stage,
        heights=[100.0 + i * 20 for i in range(10)],
        step_s=1.0,
    )
    assert len(frames) == 8
    assert all(f.exists() for f in frames)
    image = Image.open(frames[0]).convert("RGBA")
    assert image.size == (640, 360)
    assert np.array(image)[..., 3].max() > 0  # es ist etwas gezeichnet


def test_hud_without_stage_or_heights_still_renders(tmp_path):
    import yaml

    tokens = yaml.safe_load(Path("templates/project/tokens.example.yaml").read_text())
    track = [{"lat": 62.0, "lon": 7.0}, {"lat": 62.1, "lon": 7.0}]
    frames = render_hud_frames(
        tmp_path / "hud2",
        template_path=Path("templates/svg/map-hud.svg"),
        tokens=tokens,
        fps=2,
        dur=1,
        width=320,
        height=180,
        track=track,
    )
    assert len(frames) == 2


def test_profile_polyline_maps_heights_into_the_box():
    polyline, marker = _profile_polyline([100.0, 200.0, 150.0], (10, 20, 100, 40), 1)
    xs_ys = [tuple(map(float, p.split(","))) for p in polyline.split()]
    assert len(xs_ys) == 3
    assert xs_ys[0] == (10.0, 60.0)  # niedrigster Wert -> Boden der Box
    assert xs_ys[1] == (60.0, 20.0)  # hoechster Wert -> Oberkante
    assert marker in xs_ys


def test_profile_polyline_without_data_is_empty():
    assert _profile_polyline([None, None], (0, 0, 10, 10), 0)[0] == ""


# -- Audit-Fix F6: HUD ohne Trackpunkte ---------------------------------------------


def _tokens():
    import yaml

    return yaml.safe_load(Path("templates/project/tokens.example.yaml").read_text())


def test_hud_without_track_renders_stage_only(tmp_path):
    """Eine Etappe ohne aufgezeichnete Spur ist kein Fehler — vorher: IndexError."""
    stage = {"day": 9, "date": date(2026, 7, 28), "from": "Geiranger", "to": "Lom", "via": ""}
    frames = render_hud_frames(
        tmp_path / "hud",
        template_path=Path("templates/svg/map-hud.svg"),
        tokens=_tokens(),
        fps=2,
        dur=1,
        width=320,
        height=180,
        track=[],
        stage=stage,
    )
    assert len(frames) == 2
    assert all(f.exists() for f in frames)


def test_dwell_schedule_without_track_does_not_raise():
    assert _dwell_schedule([], [{"lat": 1.0, "lon": 1.0}], frame_count=3, fps=2, dwell_s=1.0) == [
        2,
        2,
        2,
    ]


def test_hud_km_label_grows_with_the_route(tmp_path):
    """Der Kilometerstand muss sich ueber die Stufen tatsaechlich aendern, nicht nur rendern."""
    track = [{"lat": 62.0 + i * 0.05, "lon": 7.0} for i in range(10)]
    frames = render_hud_frames(
        tmp_path / "hud2",
        template_path=Path("templates/svg/map-hud.svg"),
        tokens=_tokens(),
        fps=2,
        dur=4,
        width=320,
        height=180,
        track=track,
        heights=[100.0 + i * 30 for i in range(10)],
        step_s=1.0,
    )
    assert len(frames) == 8
    # Erste und letzte Stufe muessen sich unterscheiden — sonst steht das HUD still.
    assert frames[0].read_bytes() != frames[-1].read_bytes()
    # ... und innerhalb einer Stufe identisch bleiben (ein SVG-Rendering je `step_s`).
    assert frames[0].read_bytes() == frames[1].read_bytes()


def test_hud_shows_cumulative_ascent(tmp_path):
    """Plan B1 nennt die kumulierten Hoehenmeter als HUD-Wert — `total_ascent_m` war ungenutzt."""
    track = [{"lat": 62.0 + i * 0.05, "lon": 7.0} for i in range(6)]
    climbing = [100.0, 200.0, 300.0, 400.0, 500.0, 600.0]
    flat = [100.0] * 6

    steigend = render_hud_frames(
        tmp_path / "steigend", template_path=Path("templates/svg/map-hud.svg"),
        tokens=_tokens(), fps=1, dur=3, width=320, height=180, track=track, heights=climbing,
    )
    eben = render_hud_frames(
        tmp_path / "eben", template_path=Path("templates/svg/map-hud.svg"),
        tokens=_tokens(), fps=1, dur=3, width=320, height=180, track=track, heights=flat,
    )
    # Anstieg wird angezeigt, ebene Strecke laesst die Angabe weg -> unterschiedliche Bilder.
    assert steigend[-1].read_bytes() != eben[-1].read_bytes()


def test_ascent_label_is_optional_for_other_callers():
    """Ein Token-Satz ohne `ascent_label` darf am HUD-Template nicht scheitern (vgl. F5)."""
    from frameforge.design import build_svg_from_tokens

    svg = build_svg_from_tokens(
        Path("templates/svg/map-hud.svg"),
        {
            "width": 320, "height": 180,
            "font_display": "Helvetica", "font_text": "Helvetica",
            "primary_color": "#111", "accent_color": "#e0a458", "text_color": "#fff",
            "day_label": "TAG 9", "stage_label": "A — B", "km_label": "12 km",
            "elevation_label": "800 m", "profile_points": "0,0 1,1",
            "marker_x": 1, "marker_y": 1,
        },
    )
    assert "{{" not in svg


def test_hud_profile_sits_inside_the_panel(tmp_path):
    """Realbetrieb-Fund: das Hoehenprofil schwebte oben links, das Panel lag unten."""
    from frameforge.design import overlay_tokens

    width, height = 960, 540
    track = [{"lat": 62.0 + i * 0.05, "lon": 7.0} for i in range(8)]
    frames = render_hud_frames(
        tmp_path / "hud", template_path=Path("templates/svg/map-hud.svg"), tokens=_tokens(),
        fps=1, dur=2, width=width, height=height, track=track,
        heights=[100.0 + i * 50 for i in range(8)],
    )
    layout = overlay_tokens(_tokens(), width=width, height=height)

    # Sichtbarer Inhalt darf nicht oberhalb des Panels liegen (Toleranz: Schattenrand).
    image = np.array(Image.open(frames[-1]).convert("RGBA"))[..., 3]
    rows = np.nonzero(image.any(axis=1))[0]
    assert rows[0] >= layout["panel_y"] - height * 0.03
    # ... und nicht rechts neben dem Panel herausragen.
    cols = np.nonzero(image.any(axis=0))[0]
    assert cols[-1] <= layout["margin"] + layout["panel_width"] + width * 0.03


def test_hud_uses_only_renderable_glyphs():
    """`→` und `↑` fehlen in den Fonts — im Bild wuerde ein leeres Kaestchen stehen."""
    from frameforge.map import HUD_ARROW, HUD_ASCENT_PREFIX

    assert "→" not in HUD_ARROW
    assert "↑" not in HUD_ASCENT_PREFIX
