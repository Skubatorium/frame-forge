"""Tests fuer die (bisher schema-basierte) QC-Pruefung."""

from __future__ import annotations

from frameforge.qc import validate
from frameforge.timeline import Timeline


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
