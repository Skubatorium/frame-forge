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

# Mitgelieferte Presets (eigene unter ~/.frameforge/presets koennen dazukommen).
BUNDLED_SLUGS = {
    "nordic-cinematic",
    "punch-teaser",
    "chronikel",
    "thematisch-assoziativ",
    "diary-handheld",
    "timelapse-journey",
    "action-adrenalin",
    "epic-trailer",
    "vlog-dynamic",
    "calm-meditative",
    "retro-super8",
    "beat-music-video",
}


def test_list_presets_includes_all_bundled():
    slugs = {p["slug"] for p in list_presets()}
    assert BUNDLED_SLUGS <= slugs
    for p in list_presets():
        assert p["name"] and p["description"]  # Metadaten gesetzt


def test_bundled_presets_have_example_and_arc():
    by_slug = {p["slug"]: p for p in list_presets()}
    for slug in BUNDLED_SLUGS:
        assert by_slug[slug]["example"], f"{slug} ohne Beispiel"
        assert by_slug[slug]["arc"], f"{slug} ohne Bogen"


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


def test_scaffold_and_load_custom_preset(tmp_path, monkeypatch):
    import frameforge.presets as pm

    user_dir = tmp_path / "presets"
    monkeypatch.setattr(pm, "USER_PRESETS_DIR", user_dir)
    path = pm.scaffold_preset("mein-stil")
    assert path.exists()
    # Erscheint in der Liste, als eigen markiert, per Slug ladbar.
    entry = next(p for p in pm.list_presets() if p["slug"] == "mein-stil")
    assert entry["custom"] is True
    assert "pacing" in pm.load_preset("mein-stil")


def test_scaffold_preset_refuses_overwrite(tmp_path, monkeypatch):
    import frameforge.presets as pm

    monkeypatch.setattr(pm, "USER_PRESETS_DIR", tmp_path / "presets")
    pm.scaffold_preset("dup")
    with pytest.raises(FileExistsError):
        pm.scaffold_preset("dup")


def test_user_preset_overrides_bundled(tmp_path, monkeypatch):
    import frameforge.presets as pm

    user_dir = tmp_path / "presets"
    user_dir.mkdir()
    (user_dir / "chronikel.yaml").write_text(
        "slug: chronikel\nname: Mein Chronikel\ndescription: x\npacing: {min_s: 9}\n"
    )
    monkeypatch.setattr(pm, "USER_PRESETS_DIR", user_dir)
    assert pm.load_preset("chronikel")["name"] == "Mein Chronikel"
