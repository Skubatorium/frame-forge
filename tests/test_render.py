"""Tests fuer den Filtergraph-Bau (rein string-basiert) und einen echten Proxy-Render."""

from __future__ import annotations

import shutil
import subprocess
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
    # normalize=0, sonst wuerde amix die gesetzten Pegel automatisch mit 1/n skalieren.
    assert "normalize=0" in graph.filter_complex


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
    assert graph.video_label.endswith("_lut")


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
    proxy = proxy_path(media_root / "clip.mp4", proxies_dir, media_root=media_root)
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


def test_build_filtergraph_ducks_all_music_tracks():
    """Audit K5: bei mehreren Musik-Spuren muessen alle geduckt werden, nicht nur die erste."""
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        audio=[
            {"id": "m1", "src": "music/bed1.wav", "tl_in": 0},
            {"id": "m2", "src": "music/bed2.wav", "tl_in": 0},
            {"id": "oton", "asset": "a1", "type": "original", "tl_in": 0.5, "dur": 0.5,
             "duck_music_db": -14},
        ],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert "m0_duck0" in graph.filter_complex
    assert "m1_duck0" in graph.filter_complex


def test_render_final_resolution_override(proj):
    """B3: --resolution rendert in einer anderen Aufloesung als die Timeline."""
    export = proj.export("teaser")
    timeline = Timeline(
        export="teaser", fps=25, resolution=(320, 240), duration=1.0,
        tracks={"video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.0, "tl_in": 0}]},
    )
    out = render_final(proj, export, timeline, resolution=(160, 120), crf=28, preset="ultrafast")
    result = probe_video(out)
    assert result["w"] == 160
    assert result["h"] == 120


def test_build_filtergraph_resolution_override_scales_to_target():
    timeline = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}])
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
        resolution=(1920, 1080),
    )
    assert "scale=1920:1080" in graph.filter_complex
    assert "320:240" not in graph.filter_complex


def test_build_filtergraph_applies_color_grade():

    timeline = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}])
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
        color_grade={"mood": "punchy", "contrast": "high"},
    )
    assert "eq=contrast=" in graph.filter_complex
    assert graph.video_label.endswith("_grade")


def test_grade_filter_unknown_mood_returns_none():
    from frameforge.render import grade_filter

    assert grade_filter({"mood": "gibts-nicht"}) is None
    assert grade_filter(None) is None


def test_grade_filter_new_moods_produce_eq():
    from frameforge.render import grade_filter

    # Von den neuen Presets genutzte Moods muessen eine Gradierung liefern.
    for mood in ("teal_orange", "clean_modern", "soft_pastel", "warm_nostalgic"):
        out = grade_filter({"mood": mood, "contrast": "medium"})
        assert out and out.startswith("eq=")


def test_grade_filter_warm_moods_add_red_not_blue():
    """Warme Moods muessen tatsaechlich waermen: rs positiv (mehr Rot), nicht kuehlen."""
    from frameforge.render import grade_filter

    for mood in ("warm_nostalgic", "teal_orange", "cool_highlights_warm_lights"):
        out = grade_filter({"mood": mood})
        assert "colorbalance=rs=0." in out, f"{mood} kuehlt statt zu waermen: {out}"


def test_render_final_with_color_grade_still_renders(proj):
    export = proj.export("teaser")
    timeline = Timeline(
        export="teaser", fps=25, resolution=(320, 240), duration=1.0,
        tracks={"video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.0, "tl_in": 0}]},
    )
    out = render_final(proj, export, timeline, color_grade={"mood": "vivid", "contrast": "high"},
                       crf=28, preset="ultrafast")
    assert probe_video(out)["w"] == 320


# -- B1: Uebergaenge (xfade) + Ken-Burns (zoompan) ----------------------------


def test_no_transitions_uses_single_concat():
    tl = _timeline(video=[
        {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 1, "tl_in": 0},
        {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 1, "tl_in": 1},
    ])
    graph = build_filtergraph(tl, resolve_asset=lambda a: Path(f"/m/{a}.mp4"),
                              export_root=Path("/e"), project_root=Path("/p"))
    assert "concat=n=2:v=1:a=0" in graph.filter_complex  # rueckwaertskompatibel
    assert "xfade" not in graph.filter_complex


def test_crossfade_transition_emits_xfade():
    tl = _timeline(video=[
        {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0},
        {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 2, "tl_in": 1.5,
         "transition_in": {"type": "fade", "dur": 0.5}},
    ])
    graph = build_filtergraph(tl, resolve_asset=lambda a: Path(f"/m/{a}.mp4"),
                              export_root=Path("/e"), project_root=Path("/p"))
    assert "xfade=transition=fade:duration=0.500:offset=1.500" in graph.filter_complex


def test_kenburns_effect_emits_zoompan():
    tl = _timeline(video=[
        {"id": "c1", "asset": "photo1", "src_in": 0, "src_out": 2, "tl_in": 0,
         "effects": [{"type": "kenburns", "from": [0, 0, 1.0], "to": [0, 0, 1.12]}]},
    ])
    graph = build_filtergraph(tl, resolve_asset=lambda a: Path(f"/m/{a}.jpg"),
                              export_root=Path("/e"), project_root=Path("/p"))
    assert "zoompan=" in graph.filter_complex


def test_render_crossfade_and_kenburns_end_to_end(proj):
    """Echter Render mit Crossfade (clip->foto) und Ken-Burns auf dem Foto."""
    export = proj.export("teaser")
    shutil.copy(FIXTURES / "photo.jpg", proj.config.media_root / "photo.jpg")
    from frameforge.index import write_asset
    from frameforge.ingest import hash_file, proxy_path
    write_asset(proj, {"id": "photo1", "kind": "photo", "path": "photo.jpg",
                       "hash": hash_file(proj.config.media_root / "photo.jpg")})
    px = proxy_path(proj.config.media_root / "photo.jpg", proj.cache_dir / "proxies",
                    media_root=proj.config.media_root)
    shutil.copy(proj.config.media_root / "photo.jpg", px)

    timeline = Timeline(export="teaser", fps=25, resolution=(320, 240), duration=3.0, tracks={
        "video": [
            {"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.5, "tl_in": 0},
            {"id": "c2", "asset": "photo1", "src_in": 0, "src_out": 2.0, "tl_in": 1.0,
             "transition_in": {"type": "fade", "dur": 0.5},
             "effects": [{"type": "kenburns", "from": [0, 0, 1.0], "to": [0, 0, 1.12]}]},
        ]})
    out = render_proxy(proj, export, timeline)
    result = probe_video(out)
    assert result["w"] == 320
    # 1.5s + 2.0s - 0.5s Crossfade = 3.0s. Ohne diese Assertion lief der Ken-Burns-Bug
    # (zoompan d=frames -> frames^2) hier jahrelang unbemerkt durch (Audit 2026-08-01).
    assert result["dur"] == pytest.approx(3.0, abs=0.2)


# -- C: Schwarzblende zwischen zwei Clips (Plan 0003) ------------------------------


def _black_timeline(hold: float = 0.0, dur: float = 0.5):
    from frameforge.timeline import Timeline

    return Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=2.0 + hold,
        tracks={
            "video": [
                {"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 1.0, "tl_in": 0},
                {
                    "id": "c2",
                    "asset": "clip1",
                    "src_in": 0,
                    "src_out": 1.0,
                    "tl_in": 1.0 + hold,
                    "transition_in": {"type": "black", "dur": dur, "hold": hold},
                },
            ]
        },
    )


def test_black_transition_builds_fade_out_and_in():
    graph = build_filtergraph(
        _black_timeline(),
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert "fade=t=out" in graph.filter_complex
    assert "color=black" in graph.filter_complex
    assert "fade=t=in" in graph.filter_complex
    assert "xfade" not in graph.filter_complex  # Schwarzblende ist kein Crossfade


def test_black_transition_hold_adds_tpad():
    graph = build_filtergraph(
        _black_timeline(hold=1.0),
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert "tpad" in graph.filter_complex
    assert "stop_duration=1.000" in graph.filter_complex


def test_black_transition_extra_duration():
    from frameforge.render import black_transition_extra_s

    clips = _black_timeline(hold=1.5, dur=0.5).tracks.video
    assert black_transition_extra_s(clips) == pytest.approx(2.0)  # dur + hold


def test_black_transition_renders_a_visible_black_frame(proj):
    """Abnahme C: in der Mitte des Renders ist tatsaechlich Schwarz zu sehen."""
    import numpy as np
    from PIL import Image

    export = proj.export("teaser")
    export.ensure_dirs()
    out_path = render_proxy(proj, export, _black_timeline(hold=1.0, dur=0.3))

    result = probe_video(out_path)
    # 2x 1s Material + 1s Standzeit auf Schwarz
    assert result["dur"] == pytest.approx(3.0, abs=0.3)

    frame = export.preview_dir / "mitte.png"
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "1.5", "-i", str(out_path), "-frames:v", "1",
         "-loglevel", "error", str(frame)],
        check=True,
        timeout=60,
    )
    assert np.array(Image.open(frame).convert("L")).max() < 16  # praktisch schwarz


def test_existing_concat_timeline_is_unchanged_by_the_black_support():
    """Regression Plan 0003 §0: ohne `black` bleibt der Filtergraph exakt wie vorher."""
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
    assert "concat=n=2:v=1:a=0" in graph.filter_complex
    assert "fade=" not in graph.filter_complex


# -- F: Ein-/Ausblenden von Audio-Clips (Plan 0003) --------------------------------


def _audio_timeline(**audio_extra):
    from frameforge.timeline import Timeline

    return Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=2.0,
        tracks={
            "video": [{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
            "audio": [{"id": "m1", "src": "music/theme.wav", "tl_in": 0, "dur": 2.0, **audio_extra}],
        },
    )


def _graph(timeline):
    return build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )


def test_audio_fades_are_rendered():
    graph = _graph(_audio_timeline(fade_in_s=1.0, fade_out_s=0.5))
    assert "afade=t=in:st=0:d=1.000" in graph.filter_complex
    assert "afade=t=out:st=1.500:d=0.500" in graph.filter_complex


def test_audio_without_fades_is_unchanged():
    """Regression Plan 0003 §0: ohne Blenden exakt die bisherige Filterkette."""
    assert "afade" not in _graph(_audio_timeline()).filter_complex


def test_audio_fade_renders_end_to_end(proj):
    export = proj.export("teaser")
    export.ensure_dirs()
    proj.music_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / "tone.wav", proj.music_dir / "theme.wav")

    timeline = _audio_timeline(fade_in_s=0.5, fade_out_s=0.5)
    timeline.tracks.video[0].asset = "clip1"
    out_path = render_proxy(proj, export, timeline)
    assert probe_video(out_path)["dur"] == pytest.approx(2.0, abs=0.3)


# -- H2: Farbangleichung zwischen Clips (Plan 0003) ---------------------------------

_DARK_COOL = {"luma": 60.0, "temperature": -0.10, "std": {"r": 20.0, "g": 20.0, "b": 20.0}}
_BRIGHT_WARM = {"luma": 140.0, "temperature": 0.10, "std": {"r": 40.0, "g": 40.0, "b": 40.0}}
_MIDDLE = {"luma": 100.0, "temperature": 0.0, "std": {"r": 30.0, "g": 30.0, "b": 30.0}}


def test_reference_is_the_median_of_the_used_clips():
    from frameforge.render import reference_stats

    reference = reference_stats([_DARK_COOL, _MIDDLE, _BRIGHT_WARM])
    assert reference["luma"] == 100.0
    assert reference["temperature"] == 0.0
    assert reference_stats([{}, {}]) == {}


def test_color_match_moves_towards_the_reference():
    from frameforge.render import color_match_for

    dark = color_match_for(_DARK_COOL, _MIDDLE)
    bright = color_match_for(_BRIGHT_WARM, _MIDDLE)
    assert dark.brightness > 0  # dunkler Clip wird aufgehellt
    assert bright.brightness < 0
    assert dark.temperature > 0  # kuehler Clip wird waermer gezogen
    assert bright.temperature < 0


def test_color_match_is_capped():
    """Eine Nachtaufnahme darf nicht auf Tageslicht gezogen werden."""
    from frameforge.render import COLOR_MATCH_LIMITS, color_match_for

    night = {"luma": 5.0, "temperature": -0.9, "std": {"r": 2.0, "g": 2.0, "b": 2.0}}
    day = {"luma": 200.0, "temperature": 0.4, "std": {"r": 60.0, "g": 60.0, "b": 60.0}}
    soft = color_match_for(night, day, strength="soft")
    max_brightness, max_saturation, max_temperature = COLOR_MATCH_LIMITS["soft"]
    assert abs(soft.brightness) <= max_brightness
    assert abs(soft.temperature) <= max_temperature
    assert abs(soft.saturation - 1.0) <= max_saturation

    strong = color_match_for(night, day, strength="strong")
    assert abs(strong.brightness) > abs(soft.brightness)  # staerker, aber weiterhin gedeckelt


def test_color_match_off_and_unknown_strength():
    from frameforge.render import color_match_for

    assert color_match_for(_DARK_COOL, _MIDDLE, strength="off") is None
    assert color_match_for({}, _MIDDLE) is None  # ohne Statistik keine Korrektur
    with pytest.raises(ValueError, match="strength"):
        color_match_for(_DARK_COOL, _MIDDLE, strength="krass")


def test_match_filter_is_applied_before_the_style_grade():
    from frameforge.timeline import ColorMatch

    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}]
    )
    timeline.tracks.video[0].color_match = ColorMatch(
        brightness=0.05, saturation=1.1, temperature=0.05
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
        color_grade={"mood": "cool", "contrast": "high"},
    )
    per_clip = graph.filter_complex.index("brightness=0.0500")
    style = graph.filter_complex.index("_grade")
    assert per_clip < style  # erst angleichen, dann der Look


def test_without_color_match_the_filtergraph_is_unchanged():
    """Regression Plan 0003 §0/§H: ohne Angleichung kein zusaetzlicher Filter."""
    graph = _graph(_audio_timeline())
    assert "brightness=" not in graph.filter_complex


# -- Audit-Fix: Ken-Burns darf die Clipdauer nicht vervielfachen -------------------


def test_kenburns_holds_each_input_frame_exactly_once():
    """`zoompan` haelt jeden Eingabeframe `d` Frames — mit d>1 wird aus dur*fps das Quadrat."""
    timeline = _timeline(
        video=[
            {
                "id": "c1",
                "asset": "photo1",
                "src_in": 0,
                "src_out": 2,
                "tl_in": 0,
                "effects": [{"type": "kenburns"}],
            }
        ]
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.jpg"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert ":d=1:" in graph.filter_complex
    assert ":d=50:" not in graph.filter_complex  # 2 s * 25 fps


def test_kenburns_photo_renders_the_declared_duration(proj):
    """Regression: 1-s-Foto mit Ken-Burns ergab 25 s Video (Audit 2026-08-01)."""
    from frameforge.index import write_asset
    from frameforge.ingest import hash_file, proxy_path

    export = proj.export("teaser")
    export.ensure_dirs()
    shutil.copy(FIXTURES / "photo.jpg", proj.config.media_root / "photo.jpg")
    write_asset(proj, {"id": "photo1", "kind": "photo", "path": "photo.jpg",
                       "hash": hash_file(proj.config.media_root / "photo.jpg")})
    shutil.copy(
        proj.config.media_root / "photo.jpg",
        proxy_path(proj.config.media_root / "photo.jpg", proj.cache_dir / "proxies",
                   media_root=proj.config.media_root),
    )
    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(160, 120),
        duration=2.0,
        tracks={
            "video": [
                {
                    "id": "c1",
                    "asset": "photo1",
                    "src_in": 0,
                    "src_out": 1.0,
                    "tl_in": 0,
                    "effects": [{"type": "kenburns"}],
                },
                {"id": "c2", "asset": "clip1", "src_in": 0, "src_out": 1.0, "tl_in": 1.0},
            ]
        },
    )
    out_path = render_proxy(proj, export, timeline)
    assert probe_video(out_path)["dur"] == pytest.approx(2.0, abs=0.2)
