"""Tests fuer den `preload_cairo`-Fix (siehe Modul-Docstring in `design.py`) und

fuer das SVG-Templating/PNG-Rendering.
"""

from __future__ import annotations

import ctypes.util
from pathlib import Path

import pytest

from frameforge import design
from frameforge.design import TemplateError, build_svg_from_tokens, render_svg_to_png

REPO_ROOT = Path(__file__).resolve().parent.parent
TITLE_CARD = REPO_ROOT / "templates" / "svg" / "title-card.svg"

TOKENS = {
    "width": 1920,
    "height": 1080,
    "font_display": "Helvetica",
    "font_text": "Helvetica",
    "title_size": 96,
    "subtitle_size": 36,
    "text_color": "#ffffff",
    "accent_color": "#e0a458",
    "title": "Norwegen 2026",
    "subtitle": "Ein Roadtrip",
}


def test_preload_cairo_patches_find_library_for_missing_lib(monkeypatch, tmp_path):
    fake_lib = tmp_path / "libcairo.2.dylib"
    fake_lib.write_bytes(b"")

    monkeypatch.setattr(design, "_patched", False)
    monkeypatch.setattr(design, "_CAIRO_LIB_PATTERNS", (str(fake_lib),))
    monkeypatch.setattr(ctypes.util, "find_library", lambda name: None)

    design.preload_cairo()

    assert ctypes.util.find_library("cairo-2") == str(fake_lib)
    assert ctypes.util.find_library("something-else") is None


def test_preload_cairo_raises_when_lib_truly_missing(monkeypatch):
    monkeypatch.setattr(design, "_patched", False)
    monkeypatch.setattr(design, "_CAIRO_LIB_PATTERNS", ())
    monkeypatch.setattr(ctypes.util, "find_library", lambda name: None)

    with pytest.raises(design.CairoNotFoundError):
        design.preload_cairo()


def test_preload_cairo_noop_if_already_found(monkeypatch):
    monkeypatch.setattr(design, "_patched", False)
    monkeypatch.setattr(ctypes.util, "find_library", lambda name: "/usr/lib/libcairo.dylib")

    design.preload_cairo()  # darf nicht werfen, obwohl _CAIRO_LIB_PATTERNS nicht matcht


def test_build_svg_from_tokens_fills_all_placeholders():
    svg = build_svg_from_tokens(TITLE_CARD, TOKENS)
    assert "{{" not in svg
    assert "Norwegen 2026" in svg
    assert "Ein Roadtrip" in svg


def test_build_svg_from_tokens_raises_on_missing_token():
    incomplete = dict(TOKENS)
    del incomplete["title"]
    with pytest.raises(TemplateError):
        build_svg_from_tokens(TITLE_CARD, incomplete)


def test_render_svg_to_png_writes_nonempty_file(tmp_path):
    svg = build_svg_from_tokens(TITLE_CARD, TOKENS)
    out = tmp_path / "title.png"

    render_svg_to_png(svg, out)

    assert out.exists()
    assert out.stat().st_size > 0
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_all_svg_templates_render_with_consistent_tokens(tmp_path):
    """Alle 4 Templates aus Plan §1 muessen mit einem gemeinsamen Token-Set renderbar sein."""
    tokens = {
        **TOKENS,
        "primary_color": "#1c2b3a",
        "margin": 40,
        "bar_y": 900,
        "bar_width": 800,
        "bar_height": 140,
        "bar_opacity": 0.8,
        "text_x": 60,
        "title_y": 950,
        "subtitle_y": 1000,
        "number_size": 48,
        "chapter_number": "Tag 3",
        "chapter_title": "Geirangerfjord",
        "heading": "Danke",
        "line_size": 32,
        "line1": "Familie Muster",
        "line2": "Musik: Epic North",
        "line3": "2026",
    }
    svg_dir = REPO_ROOT / "templates" / "svg"
    for template in sorted(svg_dir.glob("*.svg")):
        svg = build_svg_from_tokens(template, tokens)
        out = tmp_path / f"{template.stem}.png"
        render_svg_to_png(svg, out)
        assert out.stat().st_size > 0
