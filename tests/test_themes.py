"""Tests fuer die Design-Token-Themes."""

from __future__ import annotations

import pytest
import yaml

from frameforge.themes import ThemeNotFoundError, apply_theme, list_themes, load_theme, theme_tokens

EXPECTED = {"nordic-cold", "warm-sunset", "mono-editorial", "vibrant-roadtrip"}


def test_list_themes():
    slugs = {t["slug"] for t in list_themes()}
    assert slugs == EXPECTED
    for t in list_themes():
        assert t["name"] and t["description"]


def test_load_theme_has_core_tokens():
    theme = load_theme("nordic-cold")
    for key in ("primary_color", "accent_color", "text_color", "font_display", "font_text"):
        assert key in theme


def test_theme_tokens_strips_metadata():
    tokens = theme_tokens("nordic-cold")
    assert "slug" not in tokens and "name" not in tokens and "description" not in tokens
    assert "primary_color" in tokens


def test_load_theme_unknown_raises():
    with pytest.raises(ThemeNotFoundError):
        load_theme("gibts-nicht")


def test_apply_theme_writes_valid_yaml(tmp_path):
    out = apply_theme("warm-sunset", tmp_path / "design" / "tokens.yaml")
    assert out.exists()
    data = yaml.safe_load(out.read_text())
    assert data["accent_color"] == "#f2b04c"
    assert "slug" not in data
