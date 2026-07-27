"""Tests fuer das Brief-Schema."""

from __future__ import annotations

import pytest
import yaml

from frameforge.brief import Brief, BriefError


def _write(tmp_path, data):
    p = tmp_path / "brief.yaml"
    p.write_text(yaml.safe_dump(data))
    return p


def test_load_valid_brief(tmp_path):
    p = _write(tmp_path, {"preset": "nordic-cinematic", "target_duration_s": 900})
    brief = Brief.load(p)
    assert brief.preset == "nordic-cinematic"
    assert brief.target_duration_s == 900
    assert brief.language == "de"  # Default


def test_unknown_preset_raises(tmp_path):
    p = _write(tmp_path, {"preset": "gibts-nicht"})
    with pytest.raises(BriefError, match="Unbekanntes Preset"):
        Brief.load(p)


def test_negative_duration_raises(tmp_path):
    p = _write(tmp_path, {"target_duration_s": -5})
    with pytest.raises(BriefError):
        Brief.load(p)


def test_extra_overrides_are_kept(tmp_path):
    p = _write(tmp_path, {"preset": "nordic-cinematic", "color_grade": {"mood": "warm"}})
    brief = Brief.load(p)
    merged = brief.merged()
    assert merged["color_grade"] == {"mood": "warm"}  # Override gewinnt gegen Preset


def test_merged_pulls_preset_params(tmp_path):
    p = _write(tmp_path, {"preset": "punch-teaser", "target_duration_s": 90})
    merged = Brief.load(p).merged()
    assert merged["pacing"]["rhythm"] == "beat_driven"
    assert merged["music_energy_curve"] == "escalate_to_drop"


def test_brief_without_preset_is_valid(tmp_path):
    p = _write(tmp_path, {"target_duration_s": 60, "must_shots": ["a1"]})
    brief = Brief.load(p)
    assert brief.preset is None
    assert brief.merged()["must_shots"] == ["a1"]
