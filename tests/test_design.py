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


# -- Design-Asset-Inventar (Resume nach externem Grafik-Erstellen) ------------


def _proj(tmp_path, monkeypatch):
    from frameforge import project as project_module
    from frameforge.project import ProjectConfig, resolve_project

    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    root = projects_dir / "p"
    root.mkdir()
    ProjectConfig(name="p", media_root=tmp_path / "media").save(root / "project.yaml")
    project = resolve_project("p")
    project.design_assets_dir.mkdir(parents=True)
    return project


def test_asset_inventory_matches_requested_and_present(tmp_path, monkeypatch):
    proj = _proj(tmp_path, monkeypatch)
    proj.design_prompts_path.write_text(
        "## Logo\nDateiname: logo.png\n## Marker\nmarker-icon.png\n## Freisteller\nfreisteller.png\n"
    )
    (proj.design_assets_dir / "logo.png").write_bytes(b"x")
    (proj.design_assets_dir / "bonus.png").write_bytes(b"x")

    inv = design.asset_inventory(proj)

    assert set(inv.requested) == {"logo.png", "marker-icon.png", "freisteller.png"}
    assert "logo.png" in inv.present
    assert set(inv.missing) == {"marker-icon.png", "freisteller.png"}
    assert inv.extra == ["bonus.png"]
    assert inv.complete is False


def test_asset_inventory_complete_when_all_present(tmp_path, monkeypatch):
    proj = _proj(tmp_path, monkeypatch)
    proj.design_prompts_path.write_text("marker-icon.png")
    (proj.design_assets_dir / "marker-icon.png").write_bytes(b"x")
    assert design.asset_inventory(proj).complete is True


def test_asset_inventory_no_prompts_is_complete(tmp_path, monkeypatch):
    proj = _proj(tmp_path, monkeypatch)
    inv = design.asset_inventory(proj)
    assert inv.requested == []
    assert inv.complete is True  # nichts angefordert -> nichts fehlt


def test_requested_graphics_is_case_insensitive_and_deduped(tmp_path, monkeypatch):
    proj = _proj(tmp_path, monkeypatch)
    proj.design_prompts_path.write_text("Logo.PNG und nochmal logo.png und marker-icon.png")
    from frameforge.design import requested_graphics

    req = requested_graphics(proj.design_prompts_path)
    assert req.count("logo.png") == 1
    assert "marker-icon.png" in req
