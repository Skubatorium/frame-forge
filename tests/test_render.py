"""Tests fuer den Filtergraph-Bau (rein string-basiert) und einen echten Proxy-Render."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from frameforge import project as project_module
from frameforge.index import write_asset
from frameforge.ingest import hash_file, proxy_path
from frameforge.probe import probe_video
from frameforge.project import ProjectConfig, resolve_project
from frameforge.render import (
    FilterGraph,
    RenderError,
    build_filtergraph,
    render_final,
    render_proxy,
)
from frameforge.timeline import Timeline

FIXTURES = Path(__file__).parent / "fixtures"


def _timeline(**tracks) -> Timeline:
    return Timeline(export="teaser", fps=25, resolution=(320, 240), duration=2.0, tracks=tracks)


# -- build_filtergraph: reine String-Assertions, keine Datei noetig ------------------


def test_build_filtergraph_video_only_concats_clips():
    timeline = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 1, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 1, "tl_in": 1},
        ]
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert isinstance(graph, FilterGraph)
    assert len(graph.input_args) == 2
    assert "concat=n=2:v=1:a=0" in graph.filter_complex
    assert graph.audio_label is None


def test_build_filtergraph_photo_asset_uses_loop_input():
    timeline = _timeline(
        video=[{"id": "c1", "asset": "photo1", "src_in": 0, "src_out": 2, "tl_in": 0}]
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.jpg"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert graph.input_args[0][:2] == ["-loop", "1"]
    assert "trim=duration=2.000" in graph.filter_complex


def test_build_filtergraph_no_video_clips_raises():
    timeline = _timeline()
    with pytest.raises(RenderError):
        build_filtergraph(
            timeline,
            resolve_asset=lambda aid: Path("/x"),
            export_root=Path("/export"),
            project_root=Path("/project"),
        )


def test_build_filtergraph_overlay_adds_input_and_enable_window():
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        overlay=[{"id": "o1", "png": "overlays/title.png", "tl_in": 0.5, "dur": 1.0}],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert graph.input_args[1] == [
        "-loop", "1", "-framerate", "25.0", "-i", "/export/overlays/title.png",
    ]
    assert "between(t,0.5,1.5)" in graph.filter_complex
    assert "shortest=1" in graph.filter_complex, (
        "overlay-Filter braucht shortest=1, sonst laeuft ffmpeg mit einem '-loop 1'-Bild "
        "als unendlichem Input nie ab (siehe PROGRESS.md M1.8 — Runaway-Bug)"
    )


def test_build_filtergraph_map_clip_shifts_by_tl_in():
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        map=[{"id": "m1", "clip": "map/leg-01.mov", "tl_in": 1.0, "dur": 0.5}],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert "setpts=PTS+1.0/TB" in graph.filter_complex
    assert "between(t,1.0,1.5)" in graph.filter_complex


def test_build_filtergraph_audio_mixes_and_applies_gain():
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        audio=[{"id": "au1", "src": "music/track.wav", "tl_in": 0, "gain_db": -6}],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert graph.audio_label == "aout"
    assert "/project/music/track.wav" in str(graph.input_args)
    assert "amix=inputs=1" in graph.filter_complex


def test_build_filtergraph_duck_window_reduces_music_volume():
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        audio=[
            {"id": "au1", "src": "music/track.wav", "tl_in": 0},
            {
                "id": "au2",
                "asset": "a1",
                "type": "original",
                "tl_in": 0.5,
                "dur": 0.5,
                "duck_music_db": -14,
            },
        ],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert "volume=volume=" in graph.filter_complex
    assert "between(t,0.5,1.0)" in graph.filter_complex
    assert "amix=inputs=2" in graph.filter_complex


def test_build_filtergraph_lut_path_applies_lut3d_filter():
    timeline = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}])
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
        lut_path=Path("/luts/log-to-rec709.cube"),
    )
    assert "lut3d=file='/luts/log-to-rec709.cube'" in graph.filter_complex
    assert graph.video_label.endswith("_graded")


def test_build_filtergraph_without_lut_path_skips_lut3d():
    timeline = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}])
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert "lut3d" not in graph.filter_complex


def test_build_filtergraph_loudness_normalize_appends_loudnorm():
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        audio=[{"id": "au1", "src": "music/track.wav", "tl_in": 0}],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
        loudness_normalize=True,
    )
    assert "loudnorm=I=-16:TP=-1.5:LRA=11" in graph.filter_complex
    assert graph.audio_label == "aout_norm"


# -- render_proxy: echter ffmpeg-Lauf gegen die Fixture ------------------------------


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    cache_root = tmp_path / "cache"
    monkeypatch.setattr(project_module, "CACHE_ROOT", cache_root)

    media_root = tmp_path / "media"
    media_root.mkdir()
    shutil.copy(FIXTURES / "clip.mp4", media_root / "clip.mp4")

    root = projects_dir / "proto"
    root.mkdir()
    ProjectConfig(name="proto", media_root=media_root).save(root / "project.yaml")
    project = resolve_project("proto")

    proxies_dir = project.cache_dir / "proxies"
    proxies_dir.mkdir(parents=True)
    proxy = proxy_path(media_root / "clip.mp4", proxies_dir)
    shutil.copy(media_root / "clip.mp4", proxy)

    write_asset(
        project,
        {"id": "clip1", "kind": "video", "path": "clip.mp4", "hash": hash_file(media_root / "clip.mp4")},
    )
    return project


def test_render_proxy_produces_playable_video(proj):
    export = proj.export("teaser")
    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.5,
        tracks={"video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.5, "tl_in": 0}]},
    )

    out_path = render_proxy(proj, export, timeline)

    assert out_path.exists()
    result = probe_video(out_path)
    assert result["dur"] == pytest.approx(1.5, abs=0.3)
    assert result["w"] == 320
    assert result["h"] == 240


def test_render_proxy_with_overlay_terminates(proj):
    """Regressionstest: `-loop 1`-Overlay-PNG darf `ffmpeg` nicht endlos laufen lassen

    (siehe PROGRESS.md M1.8 — Runaway-Bug, gefunden beim Bau von `projects/proto/`).
    """
    export = proj.export("teaser")
    export.overlays_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / "photo.jpg", export.overlays_dir / "title.png")

    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.5,
        tracks={
            "video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.5, "tl_in": 0}],
            "overlay": [{"id": "o1", "png": "overlays/title.png", "tl_in": 0.0, "dur": 1.5}],
        },
    )

    out_path = render_proxy(proj, export, timeline)

    result = probe_video(out_path)
    assert result["dur"] == pytest.approx(1.5, abs=0.3)


def test_render_proxy_missing_asset_raises(proj):
    export = proj.export("teaser")
    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.0,
        tracks={"video": [{"id": "c1", "asset": "gibts-nicht", "src_in": 0, "src_out": 1, "tl_in": 0}]},
    )
    with pytest.raises(RenderError):
        render_proxy(proj, export, timeline)


# -- render_final: mappt auf Originale, Loudness-Normalisierung, Versionierung -------


def test_render_final_maps_to_original_and_normalizes_audio(proj):
    export = proj.export("teaser")
    proj.music_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / "tone.wav", proj.music_dir / "theme.wav")
    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.5,
        tracks={
            "video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.5, "tl_in": 0}],
            # `clip.mp4` (Fixture) hat keinen eigenen Audio-Stream — Musik-Track statt
            # "original"-O-Ton, um trotzdem echt durch die Loudnorm-Kette zu laufen.
            "audio": [{"id": "au1", "src": "music/theme.wav", "tl_in": 0, "gain_db": -6}],
        },
    )

    out_path = render_final(proj, export, timeline)

    assert out_path.name == "teaser_v1.mp4"
    assert out_path.parent == export.final_dir
    result = probe_video(out_path)
    assert result["dur"] == pytest.approx(1.5, abs=0.3)
    assert result["w"] == 320
    assert result["h"] == 240


def test_render_final_versions_instead_of_overwriting(proj):
    export = proj.export("teaser")
    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.5,
        tracks={"video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.5, "tl_in": 0}]},
    )

    first = render_final(proj, export, timeline)
    second = render_final(proj, export, timeline)

    assert first.name == "teaser_v1.mp4"
    assert second.name == "teaser_v2.mp4"
    assert first.exists()
    assert second.exists()


def test_render_final_missing_original_raises(proj, tmp_path):
    # Proxy existiert (aus der `proj`-Fixture), das Original unter media_root wurde entfernt.
    (proj.config.media_root / "clip.mp4").unlink()

    export = proj.export("teaser")
    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.5,
        tracks={"video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.5, "tl_in": 0}]},
    )
    with pytest.raises(RenderError, match="Original-Asset"):
        render_final(proj, export, timeline)
