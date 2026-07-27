"""Tests fuer den FCPXML/OTIO-Export."""

from __future__ import annotations

from pathlib import Path

import opentimelineio as otio

from frameforge.nle import build_otio_timeline, export_fcpxml, export_otio
from frameforge.timeline import Timeline


def _resolve(asset_id: str) -> Path:
    return Path(f"/media/{asset_id}.mp4").resolve()


def _timeline(**tracks) -> Timeline:
    return Timeline(export="teaser", fps=25, resolution=(1920, 1080), duration=5.0, tracks=tracks)


def test_build_otio_timeline_has_one_clip_per_video_track_entry():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 2, "tl_in": 2},
        ]
    )
    otio_tl = build_otio_timeline(tl, resolve_asset=_resolve, project_root=Path("/project").resolve())

    video_track = otio_tl.tracks[0]
    clips = [c for c in video_track if isinstance(c, otio.schema.Clip)]
    assert [c.name for c in clips] == ["c1", "c2"]


def test_build_otio_timeline_inserts_gap_for_tl_in_gap():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 2, "tl_in": 5},
        ]
    )
    otio_tl = build_otio_timeline(tl, resolve_asset=_resolve, project_root=Path("/project").resolve())

    video_track = otio_tl.tracks[0]
    kinds = [type(item).__name__ for item in video_track]
    assert kinds == ["Clip", "Gap", "Clip"]


def test_build_otio_timeline_adds_audio_track_only_if_present():
    without_audio = build_otio_timeline(
        _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}]),
        resolve_asset=_resolve,
        project_root=Path("/project").resolve(),
    )
    assert len(without_audio.tracks) == 1

    with_audio = build_otio_timeline(
        _timeline(
            video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
            audio=[{"id": "au1", "src": "music/theme.wav", "tl_in": 0, "dur": 5}],
        ),
        resolve_asset=_resolve,
        project_root=Path("/project").resolve(),
    )
    assert len(with_audio.tracks) == 2
    assert with_audio.tracks[1].kind == otio.schema.TrackKind.Audio


def test_build_otio_timeline_media_reference_has_available_range():
    """Ohne `available_range` schlagen manche Adapter (z.B. `fcpx_xml`) fehl — Regressionstest."""
    tl = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 1, "src_out": 3, "tl_in": 0}])
    otio_tl = build_otio_timeline(tl, resolve_asset=_resolve, project_root=Path("/project").resolve())

    clip = next(c for c in otio_tl.tracks[0] if isinstance(c, otio.schema.Clip))
    assert clip.media_reference.available_range is not None


def test_export_otio_writes_loadable_file(tmp_path):
    tl = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}])
    out_path = tmp_path / "export.otio"

    export_otio(tl, out_path, resolve_asset=_resolve, project_root=Path("/project").resolve())

    assert out_path.exists()
    loaded = otio.adapters.read_from_file(str(out_path))
    assert loaded.name == "teaser"


def test_export_fcpxml_writes_valid_xml(tmp_path):
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        audio=[{"id": "au1", "src": "music/theme.wav", "tl_in": 0, "dur": 2}],
    )
    out_path = tmp_path / "export.fcpxml"

    export_fcpxml(tl, out_path, resolve_asset=_resolve, project_root=Path("/project").resolve())

    assert out_path.exists()
    text = out_path.read_text()
    assert text.startswith("<?xml")
    assert "fcpxml" in text


def test_build_otio_timeline_overlapping_audio_uses_separate_lanes():
    """Regressionstest: Musikbett + gleichzeitiger O-Ton in EINEM Track brachte den

    `fcpx_xml`-Adapter zum Absturz (siehe PROGRESS.md M4.2) — muessen auf getrennte
    parallele Audio-Tracks (Lanes) verteilt werden.
    """
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 10, "tl_in": 0}],
        audio=[
            {"id": "music", "src": "music/theme.wav", "tl_in": 0, "dur": 10},
            {"id": "oton", "asset": "a1", "type": "original", "tl_in": 4, "dur": 2},
        ],
    )
    otio_tl = build_otio_timeline(tl, resolve_asset=_resolve, project_root=Path("/project").resolve())

    audio_tracks = [t for t in otio_tl.tracks if t.kind == otio.schema.TrackKind.Audio]
    assert len(audio_tracks) == 2
    names_per_track = [{c.name for c in t if isinstance(c, otio.schema.Clip)} for t in audio_tracks]
    assert {"music"} in names_per_track
    assert {"oton"} in names_per_track


def test_export_fcpxml_with_overlapping_audio_does_not_crash(tmp_path):
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 10, "tl_in": 0}],
        audio=[
            {"id": "music", "src": "music/theme.wav", "tl_in": 0, "dur": 10},
            {"id": "oton", "asset": "a1", "type": "original", "tl_in": 4, "dur": 2},
        ],
    )
    out_path = tmp_path / "overlap.fcpxml"

    export_fcpxml(tl, out_path, resolve_asset=_resolve, project_root=Path("/project").resolve())

    assert out_path.exists()


def test_export_fcpxml_empty_timeline_produces_valid_empty_sequence(tmp_path):
    """Anders als `render.build_filtergraph` (das leere Video-Spuren ablehnt) spiegelt der

    NLE-Export die Timeline 1:1 — eine leere Timeline ergibt eine leere, aber valide Sequenz.
    """
    tl = Timeline(export="empty", fps=25, resolution=(1920, 1080), duration=1.0, tracks={})
    out_path = tmp_path / "empty.fcpxml"

    export_fcpxml(tl, out_path, resolve_asset=_resolve, project_root=Path("/project"))

    assert "<spine/>" in out_path.read_text()
