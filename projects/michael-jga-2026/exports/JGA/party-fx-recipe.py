"""Rezept fuer die Comic-/Party-FX-Overlays des Exports `JGA` (`michael-jga-2026`) — RUNDE 4.

Muster: `projects/norwegen-2026/exports/vlog-edit/stage-caption-recipe.py`. Das Skript rendert
NUR PNGs (ueber `frameforge.design`) nach `exports/JGA/overlays/`. Kein ffmpeg, kein Render.
Das Compositing (Fade/Position/Timing/Slide/Jitter) macht `frameforge render` aus `timeline.json`.

Runde 4 (Christians 3. Preview-Feedback, `editorial-notes-round4.md`):

* **Text-Look NEU — 3 Ebenen** (ersetzt Gold-Front + Pink-Schatten aus Runde 3):
  1. Front:  **WEISS** (`#ffffff`)
  2. Mitte:  **SCHWARZ**, `-6/-6 px` (@ 4K) -> harte Kante oben-links
  3. Hinten: **PINK** (`#ff2e8a`), `+10/+10 px` -> Schlagschatten unten-rechts
  Keine Weichzeichnung, harte Deckflaechen. Font weiter **Bangers** ueberall.
* **Neigung:** gerade (0) oder von links-unten nach rechts-oben steigend (**negativer**
  SVG-Winkel). NIE nach rechts-unten fallend ("Texte stuerzen ab"). `_slant_for` gibt nie
  einen positiven Wert zurueck.
* **Groesse:** deutlich groesser als im 7:02-Preview; einzelne (biere, wtf, wimm, geniesst)
  besonders gross. `ov-hydrated` dagegen kleiner (war zu gross) + Jitter ab Start.
* **`ov-fx-sterne` geloescht** (Sterne bewegen sich nicht, lagen nur starr drueber).
* **`ov-fx-herzen`** bekommt mehr Herzen, breiter gestreut, mehr Groessenvarianz.
* **Text-/Split-Aenderungen:** `ov-sulemann` -> `ov-sulemann-a` ("Der Mann / des Abends",
  oben links, gerade) + `ov-sulemann-b` ("Pizzamann / Suelemann / Bestermann", unten rechts,
  gross). Neu `ov-mok-detektor` ("MOK Detektor", Bild ~2:48). `ov-raetkeinkaese` -> Text
  "Rede kein Kaese!". Cast #9 nur "Micha". `ov-crewupdate`/`ov-rooftop`/`ov-praesente`/
  `ov-christoph`/`ov-hydrated`/`ov-token`/`ov-wtf`/`ov-weiterziehen`/`ov-gurken`/`ov-wimm`:
  Text/Placement/Groesse laut TEXTS unten.

Aufruf von Repo-Root:  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/party-fx-recipe.py
"""

from __future__ import annotations

import math
import random
import re
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

from frameforge.design import build_svg_from_tokens, overlay_tokens, render_svg_to_png

ROOT = Path("projects/michael-jga-2026")
OUT_DIR = ROOT / "exports" / "JGA" / "overlays"
RES = (3840, 2160)
W, H = RES

TITLE_ONLY = Path("templates/svg/title-only.svg")
SUBTITLE_ONLY = Path("templates/svg/subtitle-only.svg")

WHITE = "#ffffff"
BLACK = "#000000"
CREAM = "#fdf6ec"
GOLD = "#d9a441"
GOLD_HI = "#ffcf5c"
PINK = "#ff2e8a"
PINK_HI = "#ff5cb8"
MICHA_BLUE = "#4fd8ff"

# 3-Ebenen-Versatz bei 4K. Christian Runde 4: schwarze Ebene "3 px" (@1080p Preview) ->
# ~6 px @ 4K; pinke Ebene "5-10 px" -> die +10/+10 aus Runde 3 passen ("hat einen guten Wert").
OUTLINE_DX, OUTLINE_DY = -6, -6
SHADOW_DX, SHADOW_DY = 10, 10

# placement -> (x%, y%, text-anchor). 6 % Sicherheitsrand zum Bildrand.
PLACEMENT = {
    "top-left": (6.0, 13.0, "start"),
    "top-right": (94.0, 13.0, "end"),
    "bottom-left": (6.0, 87.0, "start"),
    "bottom-right": (94.0, 87.0, "end"),
    "bottom": (50.0, 87.0, "middle"),
    "top": (50.0, 13.0, "middle"),
    "center": (50.0, 46.0, "middle"),
    # Runde 4:
    "right": (86.0, 30.0, "end"),          # ov-hydrated: rechts, fast am Rand
    "letsgo": (60.0, 80.0, "start"),       # ov-letsgo: "L" bei ~60 % Breite, halb ueber Extension
    "bottom-right-half": (92.0, 82.0, "end"),  # ov-sulemann-b: unten rechts, ueber halbe Breite
    "top-left-lo": (6.0, 20.0, "start"),   # grosse mehrzeilige Titel oben links (wtf, praesente)
    "bottom-right-hi": (94.0, 83.0, "end"),  # 2-Zeiler unten rechts, mehr Rand (rooftop)
}

_TEXT_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.DOTALL)


def _slant_for(placement: str) -> float:
    """Default: **gerade**. Runde 4 — keine placement-abhaengige Kippung mehr, und nie
    positiv (das war das "Abstuerzen nach rechts-unten"). Starke Steiger geben `slant`
    explizit mit (negativ)."""
    return 0.0


def _text_block(text: str, x_pct: float, size: float) -> str:
    """Inner-Content fuer <text> — eine Zeile escaped, mehrere als <tspan>."""
    lines = text.split("\n")
    if len(lines) == 1:
        return escape(text)
    lh = round(size * 1.12)
    return "".join(
        f'<tspan x="{x_pct}%" dy="{0 if i == 0 else lh}">{escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )


def _pivot(x_pct: float, y_pct: float) -> tuple[int, int]:
    return round(x_pct / 100 * W), round(y_pct / 100 * H)


def _decorate(svg: str, pivot: tuple[int, int], slant_deg: float, *,
              front_fill: str, mid_fill: str = BLACK, back_fill: str = PINK,
              glow: str | None = None, glow_blur: int = 44) -> str:
    """Ersetzt das eine `<text>` des Templates durch **drei** deckungsgleiche Ebenen:
    ganz hinten der Pink-Schatten (`+10/+10`), darueber die schwarze Kante (`-6/-6`), vorne
    die weisse Frontface. Alle drei um `pivot` gleich schraeg gestellt, damit ein Wackel-
    `anim` im Render sie synchron bewegt (Christian: "im gleichen Rhythmus")."""
    px, py = pivot
    m = _TEXT_RE.search(svg)
    if not m:
        return svg
    attrs, inner = m.group(1), m.group(2)
    base_attrs = re.sub(r'\s*fill="[^"]*"', "", attrs)
    slant_deg = min(0.0, slant_deg)  # nie nach rechts-unten fallend
    rot = f"rotate({slant_deg:g} {px} {py})"

    defs = ""
    front_filter = ""
    if glow:
        defs = (
            f'<defs><filter id="fffx" x="-80%" y="-80%" width="260%" height="260%">'
            f'<feDropShadow dx="0" dy="0" stdDeviation="{glow_blur}" '
            f'flood-color="{glow}" flood-opacity="0.9"/></filter></defs>'
        )
        front_filter = ' filter="url(#fffx)"'

    back = (f'<text{base_attrs} fill="{back_fill}" '
            f'transform="{rot} translate({SHADOW_DX} {SHADOW_DY})">{inner}</text>')
    mid = (f'<text{base_attrs} fill="{mid_fill}" '
           f'transform="{rot} translate({OUTLINE_DX} {OUTLINE_DY})">{inner}</text>')
    front = f'<text{base_attrs} fill="{front_fill}"{front_filter} transform="{rot}">{inner}</text>'
    svg = svg.replace(m.group(0), back + mid + front, 1)
    if defs:
        svg = svg.replace(">", ">" + defs, 1)
    return svg


def render_text(out_name: str, template: Path, text: str, placement: str, *,
                size: float, front: str = WHITE, back: str = PINK, slant: float | None = None,
                inner_markup: str | None = None, glow: str | None = None) -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    x_pct, y_pct, anchor = PLACEMENT[placement]
    if slant is None:
        slant = _slant_for(placement)

    inner = inner_markup if inner_markup is not None else _text_block(text, x_pct, size)
    n_lines = text.count("\n") + 1
    lh_pct = (size * 1.12) / H * 100
    y_eff = y_pct
    if n_lines > 1:
        if y_pct >= 80:
            y_eff = y_pct - (n_lines - 1) * lh_pct
        elif 40 <= y_pct <= 60:
            y_eff = y_pct - (n_lines - 1) * lh_pct / 2

    extra = {
        "text_x_pct": x_pct, "text_y_pct": round(y_eff, 2), "text_anchor": anchor,
        "font_display": "Bangers", "font_text": "Bangers",
    }
    if template == TITLE_ONLY:
        extra.update(title=inner, title_size=size, text_color=front)
    else:
        extra.update(subtitle=inner, subtitle_size=size, subtitle_fill=front)

    svg = build_svg_from_tokens(template, overlay_tokens(tokens, width=W, height=H, **extra))
    svg = _decorate(svg, _pivot(x_pct, y_pct), slant, front_fill=front, back_fill=back, glow=glow)
    render_svg_to_png(svg, OUT_DIR / out_name)
    print(f"  {out_name}")


def render_cluster(out_name: str, glyphs: list[str], fills: list[str], *,
                   count: int, seed: int, size_lo: int, size_hi: int,
                   area: tuple[float, float, float, float] = (10, 10, 90, 90)) -> None:
    """Comic-FX-Cluster: viele Glyphen (Herzen) verschiedener Groesse/Drehung ueber eine
    Bildregion gestreut, mit weichem Glow. Deterministisch ueber `seed`."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = area
    _glow = round(H * 0.010)
    parts = [
        (f'<defs><filter id="cl" x="-60%" y="-60%" width="220%" height="220%">'
         f'<feDropShadow dx="0" dy="0" stdDeviation="{_glow}" '
         f'flood-color="{fills[0]}" flood-opacity="0.85"/></filter></defs>')
    ]
    for _ in range(count):
        gx = rnd.uniform(x0, x1)
        gy = rnd.uniform(y0, y1)
        sz = rnd.randint(size_lo, size_hi)
        rot = rnd.uniform(-35, 35)
        fill = rnd.choice(fills)
        glyph = escape(rnd.choice(glyphs))
        px, py = gx / 100 * W, gy / 100 * H
        parts.append(
            f'<text x="{px:.0f}" y="{py:.0f}" font-family="Apple Symbols" font-size="{sz}" '
            f'fill="{fill}" text-anchor="middle" dominant-baseline="middle" '
            f'transform="rotate({rot:.1f} {px:.0f} {py:.0f})" filter="url(#cl)">{glyph}</text>'
        )
    svg = f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'
    render_svg_to_png(svg, OUT_DIR / out_name)
    print(f"  {out_name}")


def render_speedlines(out_name: str, *, seed: int = 1621, n: int = 90,
                      color: str = "#fdf6ec") -> None:
    """Comic-Speedlines: viele duenne, zur Bildmitte hin ausgerichtete Striche mit freiem
    Kern in der Mitte. Kurzer Overlay-Blitz (render.py kennt keinen `speedlines`-Effekt)."""
    rnd = random.Random(seed)
    cx, cy = W / 2, H / 2
    inner = min(W, H) * 0.16
    outer = max(W, H) * 0.62
    parts = []
    for _ in range(n):
        ang = rnd.uniform(0, 2 * math.pi)
        r0 = inner * rnd.uniform(0.9, 1.6)
        r1 = outer * rnd.uniform(0.75, 1.15)
        x0 = cx + math.cos(ang) * r0
        y0 = cy + math.sin(ang) * r0
        x1 = cx + math.cos(ang) * r1
        y1 = cy + math.sin(ang) * r1
        w = rnd.choice([5, 7, 9, 12, 16])
        op = rnd.uniform(0.35, 0.9)
        col = rnd.choice([color, GOLD_HI, PINK_HI])
        parts.append(
            f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" '
            f'stroke="{col}" stroke-width="{w}" stroke-linecap="round" opacity="{op:.2f}"/>'
        )
    svg = (f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
           f'{"".join(parts)}</svg>')
    render_svg_to_png(svg, OUT_DIR / out_name)
    print(f"  {out_name}")


# ---------------------------------------------------------------------------
# Reine Text-Overlays. (out, template, text, placement, size @4K, front, slant)
# slant None -> gerade (0). Negativ -> steigend links-unten -> rechts-oben.
TEXTS = [
    # -- Intro / Akt 1 --
    ("ov-letsgo.png",      TITLE_ONLY,    "Let's go!",                       "letsgo",              320, WHITE, -3),
    ("ov-sulemann-a.png",  SUBTITLE_ONLY, "Der Mann\ndes Abends",            "top-left",            150, WHITE, 0),
    ("ov-sulemann-b.png",  TITLE_ONLY,    "Pizzamann\nSülemann\nBestermann", "bottom-right-half",   215, WHITE, -3),
    ("ov-biere.png",       TITLE_ONLY,    "500+ Biere",                      "bottom-right",        360, WHITE, -3),
    ("ov-praesente.png",   SUBTITLE_ONLY, "Süße Geschenke\nfür den\nJunggesellen", "top-left-lo",   160, WHITE, -12),
    ("ov-geniesst.png",    SUBTITLE_ONLY, "Ein bisschen\ngenießt er es\nja schon", "top-left",      205, GOLD_HI, -8),
    ("ov-mok-detektor.png", TITLE_ONLY,   "MOK Detektor",                    "top-left",            150, WHITE, 0),
    # -- Akt 2 --
    ("ov-crewupdate.png",  TITLE_ONLY,    "Crew Update\ndie verlorenen Söhne\nstoßen dazu", "top-right", 150, WHITE, -10),
    ("ov-rooftop.png",     TITLE_ONLY,    "Rooftop Bar 58\nwir kommen!",     "bottom-right-hi",     170, WHITE, -10),
    ("ov-hydrated.png",    TITLE_ONLY,    "stay\nhydrated",                  "right",               195, WHITE, 0),
    ("ov-christoph.png",   TITLE_ONLY,    "Wo ist\nChristoph???",            "bottom-left",         205, WHITE, 0),
    ("ov-token.png",       SUBTITLE_ONLY, "wolle Token\nkaufen ???",         "bottom-left",         175, WHITE, -10),
    ("ov-lampen.png",      SUBTITLE_ONLY, "Gehen hier etwa schon\n        die Lampen aus?", "bottom-right", 120, WHITE, -4),
    ("ov-natuerlich.png",  SUBTITLE_ONLY, "natürlich\n(noch) nicht",         "bottom-right",        155, WHITE, -4),
    ("ov-weiterziehen.png", SUBTITLE_ONLY, "Noch ahnten sie nicht\nwie toll die Nacht wird", "bottom", 128, WHITE, -4),
    ("ov-wtf.png",         TITLE_ONLY,    "WTF?",                            "top-left-lo",         430, PINK, -12),
    ("ov-ichwaresnicht.png", TITLE_ONLY,  "Ich war es\nnicht!",              "bottom-right",        230, WHITE, -4),
    ("ov-gurken.png",      SUBTITLE_ONLY, "Der Michael mag Gurken.\nGib mir Gurken.\nEr braucht sie dringend.", "bottom-left", 128, WHITE, -4),
    ("ov-raetkeinkaese.png", TITLE_ONLY,  "Rede kein Käse!",                 "top-right",           150, WHITE, -4),
]

# Cast — (nn, key, name, placement, front, size). Runde 4: gerade (slant 0), Groesse hoch,
# #9 nur "Micha".
CAST = [
    ("01", "witte",    "Witte",    "bottom-left",  WHITE,      210),
    ("02", "christoph", "Christoph", "bottom-right", WHITE,     210),
    ("03", "matti",     "Matti",    "bottom-left",  WHITE,      210),
    ("04", "bartosz",   "Bartosz",  "bottom-right", WHITE,      210),
    ("05", "hagi",      "Hagi",     "bottom-left",  WHITE,      210),
    ("06", "bernhard",  "Bernhard", "bottom-right", WHITE,      210),
    ("07", "andre",     "André",    "bottom-left",  WHITE,      210),
    ("08", "skuub",     "Skuub",    "bottom-right", WHITE,      210),
    ("09", "micha",     "Micha",    "bottom-left",  MICHA_BLUE, 210),
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Text-Overlays (Bangers, 3 Ebenen Weiss/Schwarz/Pink):")
    for out, tpl, text, place, size, front, slant in TEXTS:
        render_text(out, tpl, text, place, size=size, front=front, slant=slant)

    print("Aftermath — grosser WIMM-Titel ('mind?' gross, Zeilen enger):")
    x_pct = PLACEMENT["top-left"][0]
    wimm_inner = (
        f'<tspan x="{x_pct}%" dy="0">Where is my</tspan>'
        f'<tspan x="{x_pct}%" dy="430" font-size="430">mind?</tspan>'
    )
    render_text("ov-wimm.png", TITLE_ONLY, "Where is my\nmind?", "top-left",
                size=200, front=WHITE, slant=-6, inner_markup=wimm_inner)

    print("Cast-Intro-Namensstempel (Runde 4: gerade, gross):")
    for nn, key, name, place, front, size in CAST:
        render_text(f"ov-cast-{nn}-{key}.png", TITLE_ONLY, name, place, size=size,
                    front=front, slant=0)

    print("Comic-FX-Cluster:")
    # Knutsch-Szene (~4:57): viele rosa Herzen, verschiedene Groessen, breit gestreut.
    # Nur `♥` (U+2665) — `❤` hat in Apple Symbols via cairosvg keinen Glyph (Tofu).
    render_cluster("ov-fx-herzen.png", ["♥"], [PINK, PINK_HI, "#ff8ac4", "#ffffff"],
                   count=64, seed=457, size_lo=70, size_hi=420, area=(8, 8, 92, 92))
    # Einzelner Herz-Sticker "vor der Tuer" (1706) bleibt.
    render_cluster("ov-fx-herz-1706.png", ["♥"], [PINK, PINK_HI],
                   count=3, seed=1706, size_lo=200, size_hi=300, area=(60, 20, 82, 40))
    # Speedlines-Blitz.
    render_speedlines("ov-fx-speedlines.png")
    # ov-fx-sterne: GELOESCHT (Runde 4 — Sterne bewegten sich nicht).
    stale = OUT_DIR / "ov-fx-sterne.png"
    if stale.exists():
        stale.unlink()
        print("  ov-fx-sterne.png entfernt")
    stale2 = OUT_DIR / "ov-sulemann.png"
    if stale2.exists():
        stale2.unlink()
        print("  ov-sulemann.png entfernt (-> a/b)")

    total = len(TEXTS) + 1 + len(CAST) + 3
    print(f"{total} PNG(s) geschrieben nach {OUT_DIR}")


if __name__ == "__main__":
    main()
