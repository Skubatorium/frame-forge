"""Tests fuer den `preload_cairo`-Fix (siehe Modul-Docstring in `design.py`) und

fuer das SVG-Templating/PNG-Rendering.
"""

from __future__ import annotations

import ctypes.util
from pathlib import Path

import pytest

from frameforge import design
from frameforge.design import (
    TemplateError,
    background_layer,
    build_svg_from_tokens,
    overlay_tokens,
    render_svg_to_png,
    scale_size,
)

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
    """Alle Templates muessen mit EINEM gemeinsamen, **handgeschriebenen** Token-Set rendern.

    Bei der Umsetzung von D1 wurde dieser Test auf `overlay_tokens` umgestellt, weil die
    aufgewerteten Templates neue Layout-Tokens verlangten — damit war der eigentliche Bruch
    (bestehende Token-Saetze scheitern) verdeckt statt behoben. Seit Audit-Fix F5 ergaenzt
    `build_svg_from_tokens` fehlende Layout-Werte selbst; der Test steht deshalb wieder in
    seiner urspruenglichen Form.
    """
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
        **_TEMPLATE_CONTENT,
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


# -- D1: relative Groessen, Hintergrundgrafik, alle Templates (Plan 0003) -----------

_TEMPLATE_CONTENT = {
    "title": "Trollstigen",
    "subtitle": "Tag 9",
    "chapter_number": "03",
    "chapter_title": "Über den Pass",
    # infocard.svg (seit `a87299a` im Repo) verlangt diese beiden Inhalts-Tokens. Ohne sie
    # scheitern alle sechs Template-Tests an genau dieser Datei -- das war seit dem Commit so
    # und ist beim Umbau der Bauchbinde am 2026-08-09 aufgefallen.
    "info_main": "1.041 m",
    "info_sub": "Hakkesetstølen",
    "day_label": "TAG 9",
    "stage_label": "Geiranger — Lom",
    "date_label": "2026-07-28",
    "km_label": "128 km",
    "elevation_label": "852 m",
    "profile_points": "0,10 40,30 80,5",
    "marker_x": 40,
    "marker_y": 30,
    "value": "190 km",
    "label": "ETAPPE",
    "heading": "Danke an",
    "line1": "Oskar",
    "line2": "Anna",
    "line3": "",
}


def _example_tokens():
    import yaml

    return yaml.safe_load(Path("templates/project/tokens.example.yaml").read_text())


@pytest.mark.parametrize("template", sorted(Path("templates/svg").glob("*.svg")), ids=lambda p: p.name)
@pytest.mark.parametrize("size", [(1920, 1080), (3840, 2160)], ids=["1080p", "2160p"])
def test_every_template_renders_from_one_token_set(template, size, tmp_path):
    """Abnahme D: alle Templates, ein gemeinsames Token-Set, beide Aufloesungen."""
    tokens = overlay_tokens(_example_tokens(), width=size[0], height=size[1], **_TEMPLATE_CONTENT)
    svg = build_svg_from_tokens(template, tokens)
    out = tmp_path / f"{template.stem}.png"
    render_svg_to_png(svg, out)
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_sizes_scale_with_target_height():
    small = overlay_tokens(_example_tokens(), width=1920, height=1080)
    large = overlay_tokens(_example_tokens(), width=3840, height=2160)
    assert large["title_size"] == pytest.approx(small["title_size"] * 2, rel=0.02)
    assert large["margin"] == pytest.approx(small["margin"] * 2, rel=0.02)


def test_scale_size_accepts_factors_and_reference_pixels():
    assert scale_size(0.05, 1080) == pytest.approx(54.0)  # Faktor der Hoehe
    assert scale_size(96, 1080) == pytest.approx(96.0)  # Pixel bei Referenzhoehe
    assert scale_size(96, 2160) == pytest.approx(192.0)  # ... mitskaliert


def test_project_tokens_override_derived_defaults():
    tokens = overlay_tokens({"margin": 7, "text_color": "#123456"}, width=100, height=100)
    assert tokens["margin"] == 7
    assert tokens["text_color"] == "#123456"
    assert "type_scale" not in tokens  # kein Layout-Token, gehoert nicht ins SVG


def test_background_layer_is_optional():
    assert background_layer(None, 100, 50) == ""
    layer = background_layer("design/assets/bg.png", 1920, 1080)
    assert 'href="design/assets/bg.png"' in layer
    assert 'width="1920"' in layer


def test_title_card_can_carry_a_background_graphic(tmp_path):
    tokens = overlay_tokens(
        _example_tokens(),
        width=640,
        height=360,
        **_TEMPLATE_CONTENT,
        background_layer=background_layer("bg.png", 640, 360),
    )
    svg = build_svg_from_tokens(Path("templates/svg/title-card.svg"), tokens)
    assert "<image" in svg


# -- Audit-Fix F5: Token-Saetze von vor Plan 0003 muessen weiter rendern ------------

# Wortgleich der Token-Satz aus dem Stand vor Plan 0003 (Commit 79cb540). Er kennt weder
# corner_radius noch shadow_* noch die Tracking-Werte — genau so schreibt ihn ein Projekt,
# das sein tokens.yaml vor der Aufwertung der Templates angelegt hat.
_PRE_0003_TOKENS = {
    "width": 1920,
    "height": 1080,
    "font_display": "Helvetica",
    "font_text": "Helvetica",
    "title_size": 96,
    "subtitle_size": 36,
    "text_color": "#ffffff",
    "accent_color": "#e0a458",
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
    "line_size": 32,
    "title": "Norwegen 2026",
    "subtitle": "Ein Roadtrip",
    "chapter_number": "Tag 3",
    "chapter_title": "Geirangerfjord",
    "heading": "Danke",
    "line1": "Familie Muster",
    "line2": "Musik: Epic North",
    "line3": "2026",
}


@pytest.mark.parametrize(
    "template",
    sorted((REPO_ROOT / "templates" / "svg").glob("*.svg")),
    ids=lambda p: p.name,
)
def test_pre_plan0003_token_sets_still_render(template, tmp_path):
    """Plan 0003 §0: ein bestehender Token-Satz darf nicht ploetzlich TemplateError werfen."""
    tokens = {**_PRE_0003_TOKENS, **{k: v for k, v in _TEMPLATE_CONTENT.items()}}
    svg = build_svg_from_tokens(template, tokens)
    out = tmp_path / f"{template.stem}.png"
    render_svg_to_png(svg, out)
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_caller_values_win_over_derived_layout():
    """Die Ergaenzung darf eigene Werte des Aufrufers nie ueberschreiben."""
    svg = build_svg_from_tokens(
        REPO_ROOT / "templates" / "svg" / "lower-third.svg",
        {**_PRE_0003_TOKENS, "margin": 40, "bar_width": 800},
    )
    assert 'x="40"' in svg
    assert 'width="800"' in svg


def test_missing_content_token_still_raises():
    """Fehlende **Inhalts**-Tokens bleiben ein Fehler — ergaenzt wird nur Layout."""
    with pytest.raises(TemplateError, match="title"):
        build_svg_from_tokens(
            REPO_ROOT / "templates" / "svg" / "title-card.svg", {"width": 1920, "height": 1080}
        )


# -- Audit-Fix F8: Templates inhaltlich pruefen, nicht nur "es kommt ein PNG raus" --


def _alpha_bbox(png_path: Path):
    """Bounding-Box des sichtbaren Inhalts (Alpha > 0) als relative Anteile der Bildgroesse."""
    import numpy as np
    from PIL import Image

    alpha = np.array(Image.open(png_path).convert("RGBA"))[..., 3]
    rows = np.nonzero(alpha.any(axis=1))[0]
    cols = np.nonzero(alpha.any(axis=0))[0]
    assert rows.size and cols.size, f"{png_path.name}: nichts gezeichnet"
    height, width = alpha.shape
    return (
        cols[0] / width,
        rows[0] / height,
        (cols[-1] + 1) / width,
        (rows[-1] + 1) / height,
    )


@pytest.mark.parametrize(
    "template",
    sorted((REPO_ROOT / "templates" / "svg").glob("*.svg")),
    ids=lambda p: p.name,
)
def test_template_layout_is_resolution_independent(template, tmp_path):
    """Abnahme D: „in 1080p und 2160p optisch konsistent" — bisher nur behauptet.

    Geprueft wird die Bounding-Box des sichtbaren Inhalts in **relativen** Koordinaten: sie
    muss in beiden Aufloesungen praktisch deckungsgleich sein. Genau das ist die Zusage hinter
    `type_scale`/`overlay_tokens`, und genau das faengt ein PNG-Magic-Byte-Check nicht.
    """
    boxes = []
    for width, height in ((1920, 1080), (3840, 2160)):
        tokens = overlay_tokens(_example_tokens(), width=width, height=height, **_TEMPLATE_CONTENT)
        out = tmp_path / f"{template.stem}-{height}.png"
        render_svg_to_png(build_svg_from_tokens(template, tokens), out)
        boxes.append(_alpha_bbox(out))

    for small, large in zip(boxes[0], boxes[1], strict=True):
        assert small == pytest.approx(large, abs=0.02)


@pytest.mark.parametrize(
    "template",
    sorted((REPO_ROOT / "templates" / "svg").glob("*.svg")),
    ids=lambda p: p.name,
)
def test_template_content_stays_inside_the_frame(template, tmp_path):
    """Nichts darf ueber den Bildrand hinauslaufen — sonst ist Text im Film abgeschnitten."""
    tokens = overlay_tokens(_example_tokens(), width=1920, height=1080, **_TEMPLATE_CONTENT)
    out = tmp_path / f"{template.stem}.png"
    render_svg_to_png(build_svg_from_tokens(template, tokens), out)

    left, top, right, bottom = _alpha_bbox(out)
    assert left >= 0.0
    assert top >= 0.0
    assert right <= 1.0
    assert bottom <= 1.0


def test_layout_check_catches_a_broken_template(tmp_path):
    """Gegenprobe: ein Template mit absoluten Pixelwerten faellt durch die Konsistenzpruefung."""
    broken = tmp_path / "broken.svg"
    broken.write_text(
        '<svg width="{{width}}" height="{{height}}" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="100" y="100" width="400" height="200" fill="#fff"/></svg>'
    )
    boxes = []
    for width, height in ((1920, 1080), (3840, 2160)):
        out = tmp_path / f"broken-{height}.png"
        render_svg_to_png(
            build_svg_from_tokens(broken, {"width": width, "height": height}), out
        )
        boxes.append(_alpha_bbox(out))
    assert boxes[0] != pytest.approx(boxes[1], abs=0.02)
