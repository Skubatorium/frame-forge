"""Tests fuer das Timeline-Schema: Feldvalidierung und semantische Pruefung."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from frameforge.timeline import Timeline, TimelineValidationError


def _base_kwargs(**overrides):
    kwargs = {"export": "teaser-90s", "fps": 25, "resolution": (3840, 2160), "duration": 10.0}
    kwargs.update(overrides)
    return kwargs


def test_valid_timeline_passes_semantics():
    tl = Timeline(
        **_base_kwargs(),
        tracks={
            "video": [{"id": "c001", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
            "audio": [{"id": "a001", "src": "music/x.wav", "tl_in": 0, "dur": 10}],
        },
    )
    tl.validate_semantics()  # darf nicht werfen


def test_video_clip_rejects_src_out_not_greater_than_src_in():
    with pytest.raises(ValidationError):
        Timeline(
            **_base_kwargs(),
            tracks={"video": [{"id": "c001", "asset": "a1", "src_in": 5, "src_out": 5, "tl_in": 0}]},
        )


def test_audio_clip_requires_src_or_asset():
    with pytest.raises(ValidationError):
        Timeline(
            **_base_kwargs(),
            tracks={"audio": [{"id": "a001", "tl_in": 0, "dur": 2}]},
        )


def test_duplicate_ids_across_tracks_raise():
    tl = Timeline(
        **_base_kwargs(),
        tracks={
            "video": [{"id": "dup", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
            "overlay": [{"id": "dup", "png": "x.png", "tl_in": 0, "dur": 1}],
        },
    )
    with pytest.raises(TimelineValidationError):
        tl.validate_semantics()


def test_clip_exceeding_timeline_duration_raises():
    tl = Timeline(
        **_base_kwargs(duration=5.0),
        tracks={"video": [{"id": "c001", "asset": "a1", "src_in": 0, "src_out": 8, "tl_in": 0}]},
    )
    with pytest.raises(TimelineValidationError):
        tl.validate_semantics()


def test_video_clip_speed_scales_effective_duration():
    tl = Timeline(
        **_base_kwargs(duration=5.0),
        tracks={
            "video": [
                {"id": "c001", "asset": "a1", "src_in": 0, "src_out": 20, "tl_in": 0, "speed": 4.0}
            ]
        },
    )
    tl.validate_semantics()  # 20s Quellmaterial bei 4x Speed passt in 5s Timeline


def test_load_save_roundtrip(tmp_path):
    tl = Timeline(
        **_base_kwargs(),
        tracks={"video": [{"id": "c001", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}]},
    )
    path = tmp_path / "timeline.json"
    tl.save(path)

    reloaded = Timeline.load(path)
    assert reloaded == tl


# -- Audit-Fix F4: Zusatzfelder ueberleben das Zurueckschreiben ---------------------


def test_unknown_fields_survive_a_roundtrip(tmp_path):
    """`color-match` u.a. schreiben timeline.json zurueck — nichts darf dabei verloren gehen."""
    raw = {
        "version": 1,
        "export": "e",
        "fps": 25,
        "resolution": [320, 240],
        "duration": 2.0,
        "notes": "Kapitelaufteilung siehe beatsheet.md",
        "tracks": {
            "video": [
                {
                    "id": "c1",
                    "asset": "a1",
                    "src_in": 0,
                    "src_out": 1,
                    "tl_in": 0,
                    "kommentar": "bester Take, nicht ersetzen",
                }
            ],
            "audio": [
                {"id": "m1", "src": "music/t.wav", "tl_in": 0, "quelle": "selbst erzeugt"}
            ],
        },
    }
    path = tmp_path / "timeline.json"
    path.write_text(json.dumps(raw))

    timeline = Timeline.load(path)
    timeline.save(path)
    back = json.loads(path.read_text())

    assert back["notes"] == "Kapitelaufteilung siehe beatsheet.md"
    assert back["tracks"]["video"][0]["kommentar"] == "bester Take, nicht ersetzen"
    assert back["tracks"]["audio"][0]["quelle"] == "selbst erzeugt"


def test_roundtrip_keeps_known_fields_unchanged(tmp_path):
    path = tmp_path / "timeline.json"
    original = Timeline(
        export="e",
        fps=25,
        resolution=(320, 240),
        duration=2.0,
        tracks={"video": [{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0}]},
    )
    original.save(path)
    reloaded = Timeline.load(path)
    assert reloaded.model_dump() == original.model_dump()
