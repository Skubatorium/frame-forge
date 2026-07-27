"""Tests fuer die ladbaren Stil-Presets."""

from __future__ import annotations

import pytest

from frameforge.presets import (
    PRESET_PARAM_KEYS,
    PresetNotFoundError,
    apply_preset,
    list_presets,
    load_preset,
)

EXPECTED_SLUGS = {
    "nordic-cinematic",
    "punch-teaser",
    "chronikel",
    "thematisch-assoziativ",
    "diary-handheld",
    "timelapse-journey",
}


def test_list_presets_returns_all_six():
    slugs = {p["slug"] for p in list_presets()}
    assert slugs == EXPECTED_SLUGS
    for p in list_presets():
        assert p["name"] and p["description"]  # Metadaten gesetzt


def test_load_preset_has_all_param_keys():
    preset = load_preset("nordic-cinematic")
    for key in PRESET_PARAM_KEYS:
        assert key in preset


def test_load_preset_unknown_raises():
    with pytest.raises(PresetNotFoundError):
        load_preset("gibts-nicht")


def test_apply_preset_fills_params_from_preset():
    merged = apply_preset({"preset": "nordic-cinematic"})
    assert merged["color_grade"]["mood"] == "cool_highlights_warm_lights"
    assert merged["pacing"]["rhythm"] == "slow"


def test_apply_preset_brief_overrides_win():
    merged = apply_preset({"preset": "nordic-cinematic", "text_density": "bold_large"})
    assert merged["text_density"] == "bold_large"  # Override bleibt


def test_apply_preset_without_preset_is_passthrough():
    assert apply_preset({"target_duration_s": 90}) == {"target_duration_s": 90}


def test_apply_preset_unknown_preset_is_passthrough():
    brief = {"preset": "gibts-nicht", "target_duration_s": 90}
    assert apply_preset(brief) == brief


def test_apply_preset_does_not_mutate_input():
    brief = {"preset": "chronikel"}
    apply_preset(brief)
    assert "color_grade" not in brief  # Original unberuehrt
