"""Tests fuer das Timeline-Schema: Feldvalidierung und semantische Pruefung."""

from __future__ import annotations

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
