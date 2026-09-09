"""Design-Tokens -> SVG-Templates -> PNG mit Alpha.

`preload_cairo()` ist der (gegenueber `docs/plans/HANDOVER.md` korrigierte) Fix fuer
den bekannten Fallstrick: `cairosvg` laedt `libcairo` ueber `cairocffi`, das intern
`ctypes.util.find_library()` fragt und bei Fehlschlag bloss den nackten Dateinamen
(`libcairo.2.dylib`) an `ffi.dlopen()` weiterreicht. Auf Apple Silicon liefert
`find_library()` dafuer nichts, weil die Lib nicht im dyld-Cache steht — und ein
CDLL-Preload der Datei hilft *nicht*, weil macOS' Loader beim Nachladen per nacktem
Namen nicht dedupliziert (empirisch geprueft: `ctypes.CDLL(name)` schlaegt danach
weiterhin fehl). Setzen von `DYLD_FALLBACK_LIBRARY_PATH` in `os.environ` zur Laufzeit
wirkt ebenfalls nicht — dyld liest die `DYLD_*`-Variablen nur beim Prozessstart.

Der einzige Ort, an dem wir eingreifen koennen, bevor `cairocffi` (via `cairosvg`)
zum ersten Mal importiert wird: `ctypes.util.find_library` selbst monkeypatchen, sodass
es fuer die von `cairocffi` versuchten Namen (`cairo-2`, `cairo`, `libcairo-2`) den
tatsaechlichen Homebrew-Pfad liefert. `cairocffi` bindet den Namen per
`from ctypes.util import find_library` beim eigenen Modul-Import — der Patch muss also
strikt *vor* dem ersten `import cairosvg`/`import cairocffi` im Prozess passieren.
"""

from __future__ import annotations

import ctypes.util
import glob
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frameforge.project import Project

# Dateiendungen, die als Design-Grafik zaehlen.
_GRAPHIC_EXTS = (".png", ".jpg", ".jpeg", ".svg", ".webp")
# Bildschirm-Dateinamen in prompts.md erkennen (z.B. "logo.png", "marker-icon.png").
_FILENAME_RE = re.compile(r"\b([\w-]+\.(?:png|jpe?g|svg|webp))\b", re.IGNORECASE)

_CAIRO_NAMES = ("cairo-2", "cairo", "libcairo-2")
_CAIRO_LIB_PATTERNS = (
    "/opt/homebrew/lib/libcairo.2.dylib",
    "/usr/local/lib/libcairo.2.dylib",
)

_patched = False


class CairoNotFoundError(RuntimeError):
    """libcairo konnte weder ueber den Loader noch ueber bekannte Homebrew-Pfade gefunden werden."""


def preload_cairo() -> None:
    """Muss vor dem ersten `import cairosvg` aufgerufen werden. Siehe Modul-Docstring."""
    global _patched
    if _patched or ctypes.util.find_library("cairo"):
        return

    lib_path = next(
        (path for pattern in _CAIRO_LIB_PATTERNS for path in glob.glob(pattern)), None
    )
    if lib_path is None:
        raise CairoNotFoundError("libcairo nicht gefunden — 'brew install cairo' ausfuehren")

    original_find_library = ctypes.util.find_library

    def _patched_find_library(name: str) -> str | None:
        if name in _CAIRO_NAMES:
            return lib_path
        return original_find_library(name)

    ctypes.util.find_library = _patched_find_library
    _patched = True


class TemplateError(RuntimeError):
    """Ein SVG-Template referenziert einen Platzhalter, der nicht in `tokens` vorkommt."""


# Tokens, die ein Template nutzen darf, ohne dass der Aufrufer sie kennen muss — ohne Wert
# fallen sie ersatzlos weg. Damit macht ein neues **optionales** Element in einem Template
# bestehende Token-Saetze nicht ungueltig (Audit-Befund F5):
# - `background_layer`: optionale Hintergrundgrafik in Titelkarte/Kapitelmarke (Plan §D2)
# - `ascent_label`: kumulierte Hoehenmeter im Karten-HUD (Plan §B1) — fehlt bei Etappen ohne
#   Hoehendaten und bei Aufrufern, die das HUD nicht nutzen
_OPTIONAL_TOKENS = {
    "background_layer": "",
    "ascent_label": "",
    # thought-bubble.svg: zweite Textzeile optional, eine Zeile reicht oft (Plan 0004 §5/§6).
    "bubble_line2": "",
}


def build_svg_from_tokens(template_path: Path, tokens: dict) -> str:
    """Fuellt ein SVG-Template (lower-third, title-card, ...) mit Design-Tokens.

    Einfaches `{{key}}`-Templating, kein Jinja — die Templates sind klein und statisch,
    eine zusaetzliche Abhaengigkeit dafuer lohnt sich nicht. Bricht mit `TemplateError` ab,
    wenn nach dem Ersetzen noch ein `{{...}}`-Platzhalter uebrig ist (fehlender Token), statt
    ihn still im gerenderten SVG stehen zu lassen.

    **Layout-Tokens werden ergaenzt, nicht eingefordert.** Die aufgewerteten Templates (Plan
    0003 §D1) brauchen Werte wie `corner_radius` oder `shadow_blur`, die aeltere Token-Saetze
    nicht kennen — ohne diese Ergaenzung wuerde ein bestehendes Set mit `TemplateError`
    scheitern (Audit-Befund F5, Rueckwaertskompatibilitaet laut Plan §0). Enthaelt `tokens`
    `width`/`height`, werden die fehlenden Layout-Werte daraus abgeleitet (`overlay_tokens`);
    alles, was der Aufrufer selbst mitbringt, gewinnt.
    """
    svg = template_path.read_text()
    filled = {**_OPTIONAL_TOKENS, **tokens}
    if "width" in filled and "height" in filled:
        filled = {
            **overlay_tokens({}, width=int(filled["width"]), height=int(filled["height"])),
            **filled,
        }
    for key, value in filled.items():
        svg = svg.replace(f"{{{{{key}}}}}", str(value))

    remaining = re.findall(r"{{\s*[\w.]+\s*}}", svg)
    if remaining:
        raise TemplateError(f"{template_path.name}: fehlende Tokens {sorted(set(remaining))}")
    return svg


# Bezugshoehe fuer absolute Groessenangaben in `type_scale`. Ein Token von 96 px meint
# "96 px bei 1080p" und wird auf andere Zielhoehen umgerechnet — sonst waere dieselbe
# Bauchbinde im 4K-Final halb so gross wie im 1080p-Preview (Plan 0003 §D1).
REFERENCE_HEIGHT = 1080

_DEFAULT_TYPE_SCALE = {"title": 0.058, "subtitle": 0.030, "caption": 0.022}


def scale_size(value: float, height: int) -> float:
    """Groessenangabe in Pixel fuer `height`.

    Werte `<= 1` sind **Faktoren der Zielhoehe** (`0.058` → 5,8 % der Bildhoehe), groessere
    Werte gelten als Pixel bei `REFERENCE_HEIGHT` und werden mitskaliert. Beide Schreibweisen
    ergeben in 1080p und 2160p dieselbe optische Groesse.
    """
    return value * height if value <= 1 else value * height / REFERENCE_HEIGHT


def background_layer(image_path: Path | str | None, width: int, height: int) -> str:
    """SVG-Schnipsel fuer eine formatfuellende Hintergrundgrafik — leerer String ohne Grafik.

    Damit koennen Titelkarte und Kapitelmarke eine gestaltete Flaeche aufnehmen (Plan 0003 §D2),
    ohne dass das Template zwei Varianten braucht.
    """
    if not image_path:
        return ""
    return (
        f'<image href="{image_path}" x="0" y="0" width="{width}" height="{height}" '
        'preserveAspectRatio="xMidYMid slice"/>'
    )


def overlay_tokens(tokens: dict, *, width: int, height: int, **extra) -> dict:
    """Vollstaendiges Token-Set fuer die SVG-Templates — Geometrie relativ zur Zielhoehe.

    Nimmt das Designsystem eines Projekts (`design/tokens.yaml`: Farben, Schriften,
    `type_scale`) und leitet daraus alle Layout-Tokens ab, die die Templates brauchen.
    Reihenfolge: abgeleitete Defaults < Tokens aus `tokens.yaml` < `extra` (Inhalt des
    konkreten Overlays). Das Projekt kann also jeden Wert ueberschreiben, muss aber keinen.
    """
    type_scale = {**_DEFAULT_TYPE_SCALE, **(tokens.get("type_scale") or {})}
    title = scale_size(type_scale["title"], height)
    subtitle = scale_size(type_scale["subtitle"], height)
    caption = scale_size(type_scale["caption"], height)
    margin = round(height * 0.055)
    bar_height = round(title + subtitle + height * 0.045)

    derived = {
        "width": width,
        "height": height,
        "title_size": round(title, 1),
        "subtitle_size": round(subtitle, 1),
        "caption_size": round(caption, 1),
        "number_size": round(subtitle, 1),
        "line_size": round(subtitle, 1),  # credits.svg
        "title_tracking": round(title * 0.01, 2),
        "subtitle_tracking": round(subtitle * 0.06, 2),
        # title-only/subtitle-only/box-only: frei positionierbare Text-/Panel-Layer (Default
        # reproduziert das alte zentrierte Layout; ein Aufrufer, der mehrere Layer diagonal
        # zueinander versetzen will, ueberschreibt diese Werte pro Layer selbst).
        "text_x_pct": 50,
        "text_y_pct": 50,
        "text_anchor": "middle",
        "subtitle_fill": tokens.get("accent_color", "#e0a458"),
        "box_x_pct": 10,
        "box_y_pct": 40,
        "box_w_pct": 80,
        "box_h_pct": 20,
        # stage-caption.svg: zweizeilige Etappen-Bauchbinde unten links. Defaults ergeben ein
        # fertiges Layout in der linken unteren Ecke, alle Werte relativ zur Zielgroesse -- der
        # Aufrufer (`stage-caption-recipe.py`) setzt die exakte Geometrie passend zur Box.
        "stage_day_size": round(caption * 1.15, 1),
        "stage_route_size": round(caption * 0.82, 1),
        "stage_day_x_pct": 2.8,
        "stage_day_y_pct": 88.0,
        "stage_route_x_pct": 2.8,
        "stage_route_y_pct": 94.0,
        "stage_day_fill": tokens.get("accent_color", "#e0a458"),
        "stage_route_fill": tokens.get("text_color", "#ffffff"),
        # Dritte Zeile (Tages-/Gesamtstrecke). `km_label` ist bewusst leer vorbelegt: ein neues
        # Element im Template darf bestehende Token-Saetze nicht ungueltig machen (Audit-F5/F7).
        "km_label": "",
        "stage_km_size": round(caption * 0.72, 1),
        "stage_km_x_pct": 2.8,
        "stage_km_y_pct": 97.0,
        "stage_km_fill": tokens.get("text_color", "#ffffff"),
        "margin": margin,
        "corner_radius": round(height * 0.008),
        "shadow_dy": round(height * 0.004, 1),
        "shadow_blur": round(height * 0.006, 1),
        "shadow_opacity": 0.45,
        "bar_opacity": 0.82,
        "panel_opacity": 0.72,
        "bar_y": round(height * 0.74),
        "bar_height": bar_height,
        "bar_width": round(width * 0.52),
        "accent_width": max(3, round(height * 0.006)),
        "text_x": margin + round(height * 0.028),
        "title_y": round(height * 0.74) + round(title * 1.15),
        "subtitle_y": round(height * 0.74) + round(title * 1.15 + subtitle * 1.35),
        # stage-card
        "panel_y": round(height * 0.58),
        "panel_height": round(height * 0.42),
        "accent_y": round(height * 0.66),
        "accent_bar_width": round(width * 0.06),
        "accent_height": max(3, round(height * 0.006)),
        "day_y": round(height * 0.72),
        "date_y": round(height * 0.86),
        # map-hud
        "panel_width": round(width * 0.34),
        "stage_y": round(height * 0.78),
        "stats_y": round(height * 0.84),
        "profile_stroke": max(2, round(height * 0.003)),
        "profile_marker_r": max(3, round(height * 0.005)),
        # map-inset (Karten-Fenster im Bild, eigene Pixelgroesse — hier ist `width`/`height`
        # die Groesse der Box, nicht die des Films)
        "inset_bar_y": round(height * 0.62),
        "inset_bar_height": round(height * 0.38),
        "km_size": round(caption * 1.5, 1),
        "inset_caption": round(caption * 0.72, 1),
        "km_y": round(height * 0.82),
        "caption_y": round(height * 0.93),
        "inset_left_x": round(width * 0.06),
        "inset_right_x": round(width * 0.94),
        "km_caption": "GEFAHREN",
        "elevation_caption": "HÖHE",
        "border_inset": 1,
        "border_width": width - 2,
        "border_height": height - 2,
        "border_stroke": max(1, round(height * 0.005)),
        # stat-badge
        "badge_width": round(width - 2 * margin),
        "badge_height": round(height - 2 * margin),
        "value_x": round(width / 2),
        "value_y": round(height * 0.55),
        "label_y": round(height * 0.78),
        "background_layer": "",
        # thought-bubble.svg (Plan 0004 §5/§6, Comic/Party-FX-Baukasten): Default oben rechts
        # im Bild, damit die Blase die Handlung in der Bildmitte nicht verdeckt. Die drei
        # Schwaenzchen-Kreise laufen diagonal von der Blasen-Unterkante Richtung Bildmitte
        # (zur sprechenden/denkenden Person). Ein Aufrufer, der mehrere Blasen in einem Export
        # braucht (oder die Blase woanders platzieren will), ueberschreibt `bubble_*` pro
        # Instanz wie bei jedem anderen Template -- ABER: `bubble_x_pct_center`/
        # `bubble_text1_y_pct`/`bubble_text2_y_pct`/`tail*` sind aus `bubble_x_pct`/
        # `bubble_y_pct`/`bubble_w_pct`/`bubble_h_pct` ABGELEITET und muessen bei einer
        # Repositionierung MIT neu berechnet werden (wie `stage-caption-recipe.py` es fuer
        # seine Box-Geometrie tut) -- sonst zeigen Schwaenzchen-Kreise oder Text ins Leere.
        "bubble_x_pct": 58.0,
        "bubble_y_pct": 8.0,
        "bubble_w_pct": 36.0,
        "bubble_h_pct": 18.0,
        "bubble_x_pct_center": 58.0 + 36.0 / 2,
        "bubble_text1_y_pct": 8.0 + 18.0 * 0.34,
        "bubble_text2_y_pct": 8.0 + 18.0 * 0.68,
        "bubble_corner_radius": round(height * 0.035),
        "bubble_opacity": 0.95,
        "bubble_fill": tokens.get("text_color", "#fdf6ec"),
        "bubble_stroke": tokens.get("primary_color", "#1e1640"),
        "bubble_stroke_width": max(2, round(height * 0.0035)),
        "bubble_text_size": round(caption * 1.1, 1),
        "tail_r1": max(3, round(height * 0.014)),
        "tail_r2": max(2, round(height * 0.008)),
        "tail_r3": max(1, round(height * 0.0045)),
        "tail1_x_pct": 52.0,
        "tail1_y_pct": 27.0,
        "tail2_x_pct": 47.0,
        "tail2_y_pct": 32.0,
        "tail3_x_pct": 43.0,
        "tail3_y_pct": 36.0,
        # sticker.svg (Plan 0004 §5/§6): zentrierter Glyph-Sticker, Default mittig/groß genug
        # zum Erkennen — ein Aufrufer setzt `x_pct`/`y_pct` pro Instanz fuer "sprudelnde"
        # mehrfach platzierte Sticker (Herzchen etc.).
        "sticker_x_pct": 50.0,
        "sticker_y_pct": 50.0,
        "sticker_size": round(title * 0.5, 1),
        "sticker_fill": tokens.get("accent_color", "#d9a441"),
        "sticker_glow_color": tokens.get("secondary_color", "#ff2e8a"),
        "sticker_glow_blur": round(height * 0.012, 1),
        # speedlines.svg (Plan 0004 §5/§6): Default weiss/dezent-transparent, wie ein kurzer
        # Kamerablitz -- Aufrufer kann pro Einsatz `speedline_color` auf `accent_color` o.ae.
        # umstellen, wenn eine Farbvariante gebraucht wird.
        "speedline_color": tokens.get("text_color", "#ffffff"),
        "speedline_opacity": 0.55,
        "speedline_width": max(2, round(height * 0.006)),
    }
    ignored = {"type_scale", "motion"}  # kein Layout-Token, gehoert nicht ins SVG
    return derived | {k: v for k, v in tokens.items() if k not in ignored} | extra


def render_svg_to_png(svg: str, out_path: Path) -> None:
    """Rendert SVG-Markup zu PNG mit Alphakanal. Ruft vorher `preload_cairo()` auf."""
    preload_cairo()
    import cairosvg

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(out_path))


# -- Design-Asset-Inventar (fuer Resume nach externem Grafik-Erstellen) -------


@dataclass
class AssetInventory:
    """Abgleich: welche in `prompts.md` angeforderten Grafiken liegen schon in `design/assets/`?"""

    requested: list[str]  # in prompts.md genannte Dateinamen
    present: list[str]  # tatsaechlich in design/assets/ vorhandene Grafiken
    missing: list[str]  # angefordert, aber noch nicht abgelegt
    extra: list[str]  # abgelegt, aber nicht in prompts.md genannt

    @property
    def complete(self) -> bool:
        """True, wenn nichts Angefordertes mehr fehlt (auch True, wenn nichts angefordert war)."""
        return not self.missing


def requested_graphics(prompts_md: Path) -> list[str]:
    """Dateinamen der in `prompts.md` angeforderten Grafiken (aus dem Freitext extrahiert)."""
    if not prompts_md.exists():
        return []
    found = _FILENAME_RE.findall(prompts_md.read_text())
    # dedupliziert, Reihenfolge stabil
    return list(dict.fromkeys(name.lower() for name in found))


def present_graphics(assets_dir: Path) -> list[str]:
    """Grafiken, die tatsaechlich in `design/assets/` liegen."""
    if not assets_dir.is_dir():
        return []
    return sorted(
        p.name for p in assets_dir.iterdir() if p.is_file() and p.suffix.lower() in _GRAPHIC_EXTS
    )


def asset_inventory(project: Project) -> AssetInventory:
    """Gleicht angeforderte Grafiken (`design/prompts.md`) gegen vorhandene (`design/assets/`) ab.

    Damit sieht man beim Wiedereinstieg sofort, welche extern erstellten Grafiken schon abgelegt
    sind und welche noch fehlen (Resume nach dem Bildgenerator-Schritt).
    """
    requested = requested_graphics(project.design_prompts_path)
    present = present_graphics(project.design_assets_dir)
    present_lower = {p.lower() for p in present}
    missing = [r for r in requested if r not in present_lower]
    extra = [p for p in present if p.lower() not in set(requested)]
    return AssetInventory(requested=requested, present=present, missing=missing, extra=extra)
