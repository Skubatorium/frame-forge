"""Tests fuer das QC-Regelwerk (Plan §5): Schema, Video-Lücken/Überlappungen,

Audio-Clipping-Risiko, Overlay-Lesbarkeit, Clip-Wiederholung, Brief-Abgleich.
"""

from __future__ import annotations

from frameforge.qc import validate
from frameforge.timeline import Timeline


def _timeline(**tracks) -> Timeline:
    return Timeline(export="teaser", fps=25, resolution=(1920, 1080), duration=10.0, tracks=tracks)


def test_validate_returns_empty_for_valid_timeline():
    tl = Timeline(
        export="teaser-90s",
        fps=25,
        resolution=(3840, 2160),
        duration=10.0,
        tracks={"video": [{"id": "c001", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}]},
    )
    assert validate(tl) == []


def test_validate_reports_clip_exceeding_duration():
    tl = Timeline(
        export="teaser-90s",
        fps=25,
        resolution=(3840, 2160),
        duration=3.0,
        tracks={"video": [{"id": "c001", "asset": "a1", "src_in": 0, "src_out": 8, "tl_in": 0}]},
    )
    issues = validate(tl)
    assert len(issues) == 1
    assert "c001" in issues[0]


# -- Video-Lücken/Überlappungen ------------------------------------------


def test_validate_reports_gap_between_clips():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 2, "tl_in": 5},
        ]
    )
    issues = validate(tl)
    assert any("Lücke" in i for i in issues)


def test_validate_reports_overlapping_clips():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 3, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 2, "tl_in": 1},
        ]
    )
    issues = validate(tl)
    assert any("überlappt" in i for i in issues)


def test_validate_accepts_contiguous_clips():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 3, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 3, "tl_in": 3},
        ]
    )
    assert validate(tl) == []


# -- Audio-Clipping-Risiko -------------------------------------------------


def test_validate_flags_positive_audio_gain():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        audio=[{"id": "au1", "src": "music/x.wav", "tl_in": 0, "gain_db": 3.0}],
    )
    issues = validate(tl)
    assert any("Clipping" in i for i in issues)


def test_validate_accepts_negative_or_missing_gain():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        audio=[
            {"id": "au1", "src": "music/x.wav", "tl_in": 0, "gain_db": -6.0},
            {"id": "au2", "src": "music/y.wav", "tl_in": 0},
        ],
    )
    assert validate(tl) == []


# -- Overlay-Lesbarkeit -----------------------------------------------------


def test_validate_flags_overlay_too_short_to_read():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        overlay=[{"id": "o1", "png": "title.png", "tl_in": 0, "dur": 0.4}],
    )
    issues = validate(tl)
    assert any("lesbar" in i for i in issues)


def test_validate_accepts_long_enough_overlay():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        overlay=[{"id": "o1", "png": "title.png", "tl_in": 0, "dur": 2.0}],
    )
    assert validate(tl) == []


# -- Clip-Wiederholung -------------------------------------------------------


def test_validate_flags_excessive_repetition():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 1, "tl_in": 0},
            {"id": "c2", "asset": "a1", "src_in": 1, "src_out": 2, "tl_in": 1},
            {"id": "c3", "asset": "a1", "src_in": 2, "src_out": 3, "tl_in": 2},
        ]
    )
    issues = validate(tl)
    assert any("a1" in i and "3x" in i for i in issues)


def test_validate_accepts_repetition_within_limit():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 1, "tl_in": 0},
            {"id": "c2", "asset": "a1", "src_in": 1, "src_out": 2, "tl_in": 1},
        ]
    )
    assert validate(tl) == []


# -- Brief-Abgleich -----------------------------------------------------------


def test_validate_without_brief_skips_brief_checks():
    tl = _timeline(video=[{"id": "c1", "asset": "forbidden", "src_in": 0, "src_out": 5, "tl_in": 0}])
    assert validate(tl, brief=None) == []


def test_validate_flags_duration_mismatch_against_brief():
    tl = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}])
    issues = validate(tl, brief={"target_duration_s": 60})
    assert any("Ziellänge" in i for i in issues)


def test_validate_flags_forbidden_shot():
    tl = _timeline(video=[{"id": "c1", "asset": "banned", "src_in": 0, "src_out": 5, "tl_in": 0}])
    issues = validate(tl, brief={"forbidden_shots": ["banned"]})
    assert any("Verbotenes Asset 'banned'" in i for i in issues)


def test_validate_flags_missing_must_shot():
    tl = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}])
    issues = validate(tl, brief={"must_shots": ["hero-shot"]})
    assert any("Muss-Shot 'hero-shot'" in i for i in issues)


def test_validate_passes_matching_brief():
    tl = _timeline(video=[{"id": "hero-shot", "asset": "hero-shot", "src_in": 0, "src_out": 10, "tl_in": 0}])
    issues = validate(
        tl,
        brief={"target_duration_s": 10, "must_shots": ["hero-shot"], "forbidden_shots": ["other"]},
    )
    assert issues == []
