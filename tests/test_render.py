"""Tests fuer den Filtergraph-Bau (rein string-basiert) und einen echten Proxy-Render."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from frameforge import project as project_module
from frameforge import render as render_module
from frameforge.index import write_asset
from frameforge.ingest import build_proxies, hash_file, proxy_path
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


def test_build_filtergraph_overlay_slide_defaults_to_static_x():
    """Ohne slide_from_px/drift_px bleibt es beim alten festen x=0 (Rueckwaertskompatibilitaet)."""
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
    assert "overlay=x='0':y='0'" in graph.filter_complex


def test_build_filtergraph_overlay_slide_from_px_builds_time_expression():
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        overlay=[
            {
                "id": "o1",
                "png": "overlays/title.png",
                "tl_in": 0.5,
                "dur": 1.0,
                "anim": {"slide_from_px": "-600", "slide_in_s": "0.4"},
            }
        ],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    # Linear von -600px (bei tl_in) auf 0 (bei tl_in+slide_in_s=0.9), dann konstant 0.
    assert "-600.00*max(0,min(1,(0.900-t)/0.400000))" in graph.filter_complex
    assert "overlay=x='-600.00*max(0,min(1,(0.900-t)/0.400000))':y='0'" in graph.filter_complex


def test_build_filtergraph_overlay_slide_from_py_builds_time_expression():
    """Y-Achse spiegelt dieselbe Slide-in-Mechanik wie X (z.B. Titel kommt von oben)."""
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        overlay=[
            {
                "id": "o1",
                "png": "overlays/title.png",
                "tl_in": 0.5,
                "dur": 1.0,
                "anim": {"slide_from_py": "-400", "slide_in_s": "0.4"},
            }
        ],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert "overlay=x='0':y='-400.00*max(0,min(1,(0.900-t)/0.400000))'" in graph.filter_complex


def test_build_filtergraph_overlay_drift_only_after_slide_in():
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        overlay=[
            {
                "id": "o1",
                "png": "overlays/title.png",
                "tl_in": 0.0,
                "dur": 2.0,
                "anim": {"drift_px": "15", "drift_period_s": "4.0"},
            }
        ],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    # Ohne slide_from_px startet slide_in_s trotzdem beim Default (1.5s) -- Drift setzt danach ein.
    assert "if(gte(t,1.500),15.00*sin(2*PI*(t-1.500)/4.000)," in graph.filter_complex


def test_build_filtergraph_overlay_drift_mode_linear_does_not_reverse():
    """`drift_mode: "linear"` laesst die Drift in EINE Richtung bis zum Clipende weiterlaufen.
    Nutzer-Feedback: der Sinus wirkte als Hin-und-Her und ruckelte an den Umkehrpunkten."""
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        overlay=[
            {
                "id": "o1",
                "png": "overlays/title.png",
                "tl_in": 0.0,
                "dur": 5.5,
                "anim": {"slide_from_px": "-100", "slide_in_s": "1.5",
                         "drift_px": "20", "drift_mode": "linear"},
            }
        ],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    # Rampe ueber die Hold-Phase (dur - slide_in_s = 4.0s), monoton, kein sin().
    assert "20.00*max(0,min(1,(t-1.500)/4.000000))" in graph.filter_complex
    assert "sin(" not in graph.filter_complex


def test_build_filtergraph_duck_fade_ramps_music_instead_of_switching():
    """`duck_fade_s` faehrt die Musik weich runter/hoch statt sie per `enable` hart zu schalten
    (Nutzer-Feedback: "das Absacken muss smooth passieren, ein kleiner Mini-Fade")."""
    timeline = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 20, "tl_in": 0}],
        audio=[
            {"id": "music", "src": "music/track.m4a", "tl_in": 0.0, "dur": 20.0},
            {"id": "otone", "asset": "a1", "tl_in": 5.0, "dur": 4.0,
             "duck_music_db": -6.0, "duck_fade_s": 0.6},
        ],
    )
    graph = build_filtergraph(
        timeline,
        resolve_asset=lambda aid: Path(f"/media/{aid}.mp4"),
        export_root=Path("/export"),
        project_root=Path("/project"),
    )
    assert "volume=eval=frame" in graph.filter_complex
    # Rampe startet `duck_fade_s` VOR dem O-Ton-Fenster und endet genauso danach.
    assert "clip((t-4.400)/0.600,0,1)" in graph.filter_complex
    assert "clip((9.600-t)/0.600,0,1)" in graph.filter_complex
    assert "enable='between(t,5.0,9.0)'" not in graph.filter_complex


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
    assert "setpts=PTS-STARTPTS+1.0/TB" in graph.filter_complex
    assert "between(t,1.0,1.5)" in graph.filter_complex
    # Regression: die Karten-Datei ist oft laenger als ihr Timeline-Fenster; ohne `trim` haengt
    # `overlay` (ohne `shortest=1`, siehe unten) den Dateirest ans Filmende und verlaengert den
    # Gesamtfilm (gefundener Bug: K15-Datei 50s vs. 32,887s Fenster, +17s Schwarzbild am Ende).
    assert "trim=duration=0.500" in graph.filter_complex
    # Regression: `shortest=1` auf dem Karten-Overlay kappt den GESAMTEN bis dahin
    # aufgebauten Video-Pfad auf die Laenge des Karten-Clips, sobald dieser (endliches
    # `-i`-Input, kein `-loop 1`) sein eigenes Dateiende erreicht -- gefundener Bug: Bild fror
    # ein, sobald der erste Karten-Clip zu Ende war, Ton lief unbeeinflusst weiter.
    map_overlay_line = next(
        line for line in graph.filter_complex.split(";") if "map0shift" in line and "overlay=" in line
    )
    assert "shortest=1" not in map_overlay_line


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


def _add_heic_asset(project) -> None:
    """Legt ein echtes HEIC unter `media_root` ab und baut den zugehoerigen Proxy."""
    media_root = project.config.media_root
    shutil.copy(FIXTURES / "photo.heic", media_root / "shot.heic")
    proxies_dir = project.cache_dir / "proxies"
    proxies_dir.mkdir(parents=True, exist_ok=True)
    build_proxies([media_root / "shot.heic"], proxies_dir, media_root=media_root)
    write_asset(
        project,
        {
            "id": "heic1",
            "kind": "photo",
            "path": "shot.heic",
            "hash": hash_file(media_root / "shot.heic"),
        },
    )


def _heic_timeline() -> Timeline:
    return Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.0,
        tracks={"video": [{"id": "c1", "asset": "heic1", "src_in": 0, "src_out": 1.0, "tl_in": 0}]},
    )


@pytest.fixture
def spy_inputs(monkeypatch):
    """Faengt die Eingabedateien ab, die `render_final` tatsaechlich an ffmpeg gibt."""
    seen: list[Path] = []
    original = render_module.build_filtergraph

    def wrapper(timeline, *, resolve_asset, **kwargs):
        def recording(asset_id: str) -> Path:
            path = resolve_asset(asset_id)
            seen.append(path)
            return path

        return original(timeline, resolve_asset=recording, **kwargs)

    monkeypatch.setattr(render_module, "build_filtergraph", wrapper)
    return seen


def test_render_final_uses_jpeg_proxy_for_heic(proj, spy_inputs):
    """Einzige Ausnahme vom Prinzip "Final rendert aus den Originalen" (PROGRESS.md HEIC-4).

    Belegt wird beides: die Eingabedatei ist der `.jpg`-Proxy statt des `.heic`, **und** der
    Render laeuft wirklich durch. Ohne den zweiten Teil saehe der Test den eigentlichen Fehler
    nicht — `-loop 1 -i <heic>` bricht mit "Option loop not found" ab, was in reinen
    String-Assertions unsichtbar bleibt.
    """
    _add_heic_asset(proj)
    export = proj.export("teaser")

    out_path = render_final(proj, export, _heic_timeline())

    assert [p.suffix for p in spy_inputs] == [".jpg"]
    assert spy_inputs[0].parent == proj.cache_dir / "proxies"
    assert out_path.exists()
    result = probe_video(out_path)
    assert result["dur"] == pytest.approx(1.0, abs=0.3)
    assert result["w"] == 320
    assert result["h"] == 240


def test_render_final_heic_without_proxy_raises_named_error(proj):
    """Fehlender HEIC-Proxy ist ein benannter Fehler, keine stille Notloesung aufs Original."""
    _add_heic_asset(proj)
    proxy = proxy_path(
        proj.config.media_root / "shot.heic",
        proj.cache_dir / "proxies",
        media_root=proj.config.media_root,
    )
    proxy.unlink()

    with pytest.raises(RenderError, match="HEIC"):
        render_final(proj, proj.export("teaser"), _heic_timeline())


def test_render_final_still_maps_jpeg_to_the_original(proj, spy_inputs):
    """Regression: fuer JPEG bleibt es beim Original — die Ausnahme gilt nur fuer HEIC."""
    shutil.copy(FIXTURES / "photo.jpg", proj.config.media_root / "shot.jpg")
    write_asset(
        proj,
        {
            "id": "jpg1",
            "kind": "photo",
            "path": "shot.jpg",
            "hash": hash_file(proj.config.media_root / "shot.jpg"),
        },
    )
    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.0,
        tracks={"video": [{"id": "c1", "asset": "jpg1", "src_in": 0, "src_out": 1.0, "tl_in": 0}]},
    )

    render_final(proj, proj.export("teaser"), timeline)

    assert spy_inputs == [proj.config.media_root / "shot.jpg"]


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


# -- render-engineer QC-Fix (2026-08-08): Foto-Ken-Burns crop-to-fill statt Letterbox,
# Pan-Offset-Bug in _kenburns_expr, face-aware Crop-Zentrum -------------------------------


def test_photo_clip_uses_crop_to_fill_not_pad():
    """`_scale_pad` (Letterbox/Pillarbox) ist fuer Foto-Clips Geschichte -- crop-to-fill statt
    schwarzer Balken (QC-Befund: 59/159 vlog-data-Clips hatten bis zu 58% schwarze Flaeche)."""
    tl = _timeline(
        video=[
            {
                "id": "c1",
                "asset": "photo1",
                "src_in": 0,
                "src_out": 2,
                "tl_in": 0,
                "effects": [{"type": "kenburns", "from": [0, 0, 1.0], "to": [0, 0, 1.1]}],
            }
        ]
    )
    graph = build_filtergraph(
        tl,
        resolve_asset=lambda a: Path(f"/m/{a}.jpg"),
        export_root=Path("/e"),
        project_root=Path("/p"),
    )
    assert "force_original_aspect_ratio=increase" in graph.filter_complex
    assert "crop=" in graph.filter_complex
    assert "force_original_aspect_ratio=decrease" not in graph.filter_complex
    assert "pad=" not in graph.filter_complex


def test_kenburns_pan_offset_reaches_zoompan_x_y():
    """Bugfix: `from`/`to` tragen `[x, y, z]`, aber nur `z` (Index 2) landete im Zoompan-Ausdruck
    -- x/y-Pan-Offsets waren wirkungslos. Jetzt muessen die konkreten Pan-Werte im x/y-Ausdruck
    auftauchen, nicht nur im generischen `iw/2-(iw/zoom/2)`-Zentrierungsterm."""
    tl = _timeline(
        video=[
            {
                "id": "c1",
                "asset": "photo1",
                "src_in": 0,
                "src_out": 2,
                "tl_in": 0,
                "effects": [{"type": "kenburns", "from": [0.06, 0.06, 1.0], "to": [-0.02, -0.02, 1.1]}],
            }
        ]
    )
    graph = build_filtergraph(
        tl,
        resolve_asset=lambda a: Path(f"/m/{a}.jpg"),
        export_root=Path("/e"),
        project_root=Path("/p"),
    )
    assert "0.0600" in graph.filter_complex  # x_from/y_from literal im Ausdruck
    # Spannweite x_to - x_from = -0.02 - 0.06 = -0.08, als Faktor auf den Fortschritt
    assert "-0.080000" in graph.filter_complex


def test_kenburns_zero_pan_matches_old_centered_behaviour():
    """Ohne x/y in `from`/`to` (oder x=y=0, wie in allen bisherigen Timelines) bleibt der Zoom
    exakt zentriert -- keine Verhaltensaenderung fuer bestehende Timelines."""
    tl = _timeline(
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
        tl,
        resolve_asset=lambda a: Path(f"/m/{a}.jpg"),
        export_root=Path("/e"),
        project_root=Path("/p"),
    )
    assert "iw/2-(iw/zoom/2)+(0.0000+(min(1,on/50))*0.000000)*iw" in graph.filter_complex


def test_kenburns_ease_smooth_uses_smoothstep_curve():
    """`ease: "smooth"` legt eine Smoothstep-Kurve auf den Fortschritt (Nutzer-Feedback: der
    lineare Schwenk wirkte mechanisch). Ohne `ease` bleibt es linear."""
    def graph_for(effect):
        tl = _timeline(
            video=[{"id": "c1", "asset": "photo1", "src_in": 0, "src_out": 2, "tl_in": 0,
                    "effects": [effect]}]
        )
        return build_filtergraph(
            tl,
            resolve_asset=lambda a: Path(f"/m/{a}.jpg"),
            export_root=Path("/e"),
            project_root=Path("/p"),
        ).filter_complex

    smooth = graph_for({"type": "kenburns", "from": [0, 0, 1.0], "to": [0, 0, 1.1], "ease": "smooth"})
    assert "(3-2*(min(1,on/50)))" in smooth
    linear = graph_for({"type": "kenburns", "from": [0, 0, 1.0], "to": [0, 0, 1.1]})
    assert "3-2*" not in linear


def test_unsafe_face_crop_falls_back_to_blur_fill(monkeypatch):
    """Wenn kein Ausschnitt alle Gesichter ganz enthaelt, darf NICHT auf die Bildmitte gecroppt
    werden (das schneidet garantiert jemanden an) -- dann Blur-Fill. Nutzer-Regel Runde 3:
    "es darf keine Person ausgelassen werden"."""
    from types import SimpleNamespace

    from frameforge import imageio as imageio_module
    from frameforge import render as render_module

    monkeypatch.setattr(render_module, "_face_crop_center", lambda *a, **k: None)
    # Die Bildgroesse wird aus der Datei gelesen; die Testpfade existieren nicht.
    monkeypatch.setattr(imageio_module, "open_image", lambda p: SimpleNamespace(size=(4000, 3000)))
    tl = _timeline(
        video=[{"id": "c1", "asset": "photo1", "src_in": 0, "src_out": 2, "tl_in": 0}]
    )
    graph = build_filtergraph(
        tl,
        resolve_asset=lambda a: Path(f"/m/{a}.jpg"),
        export_root=Path("/e"),
        project_root=Path("/p"),
        faces_by_asset={"photo1": [{"top": 0, "right": 10, "bottom": 10, "left": 0}]},
    )
    assert graph.unsafe_face_crops == ["photo1"]
    assert "gblur" in graph.filter_complex
    assert "crop=320:240:x=" not in graph.filter_complex


def test_explicit_fit_wins_over_unsafe_face_crop_fallback(monkeypatch):
    """Ein bewusst gesetztes `fit` wird vom Blur-Fallback nicht ueberstimmt."""
    from types import SimpleNamespace

    from frameforge import imageio as imageio_module
    from frameforge import render as render_module

    monkeypatch.setattr(render_module, "_face_crop_center", lambda *a, **k: None)
    # Die Bildgroesse wird aus der Datei gelesen; die Testpfade existieren nicht.
    monkeypatch.setattr(imageio_module, "open_image", lambda p: SimpleNamespace(size=(4000, 3000)))
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "photo1", "src_in": 0, "src_out": 2, "tl_in": 0, "fit": "crop"}
        ]
    )
    graph = build_filtergraph(
        tl,
        resolve_asset=lambda a: Path(f"/m/{a}.jpg"),
        export_root=Path("/e"),
        project_root=Path("/p"),
        faces_by_asset={"photo1": [{"top": 0, "right": 10, "bottom": 10, "left": 0}]},
    )
    assert graph.unsafe_face_crops == ["photo1"]
    assert "gblur" not in graph.filter_complex


def test_face_crop_center_defaults_to_image_center_without_faces():
    from frameforge.render import _face_crop_center

    assert _face_crop_center([], 4000, 3000, 1920, 1080) == (0.5, 0.5)


def test_face_crop_center_shifts_toward_face_bbox():
    from frameforge.render import _face_crop_center

    # Gesicht oben links im Bild -> Crop-Fenster muss dorthin verschoben werden (nicht 0.5/0.5).
    faces = [{"top": 100, "right": 800, "bottom": 700, "left": 300}]
    center = _face_crop_center(faces, 3024, 4032, 1920, 1080)
    assert center is not None
    _cx, cy = center
    assert cy < 0.5  # Gesicht liegt im oberen Bildbereich


def test_face_crop_center_returns_none_when_unsafe():
    from frameforge.render import _face_crop_center

    # Zwei Gesichter, weit auseinander in der Achse, die durch den Crop am staerksten
    # beschnitten wird (Hochkant 3:4 -> 16:9 behaelt nur ~42% der Bildhoehe) -> unsicher.
    faces = [
        {"top": 50, "right": 900, "bottom": 500, "left": 500},
        {"top": 3400, "right": 900, "bottom": 3950, "left": 500},
    ]
    assert _face_crop_center(faces, 3024, 4032, 1920, 1080) is None


def test_build_filtergraph_reports_unsafe_face_crops():
    tl = _timeline(
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
    faces_by_asset = {
        "photo1": [
            {"top": 1, "right": 60, "bottom": 20, "left": 5},
            {"top": 44, "right": 60, "bottom": 47, "left": 5},
        ]
    }
    graph = build_filtergraph(
        tl,
        resolve_asset=lambda a: Path(__file__).parent / "fixtures" / "photo.jpg",
        export_root=Path("/e"),
        project_root=Path("/p"),
        faces_by_asset=faces_by_asset,
    )
    assert "photo1" in graph.unsafe_face_crops
