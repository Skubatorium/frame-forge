"""Rezept fuer die Comic-/Party-FX-Overlays des Exports `JGA` (`michael-jga-2026`) — RUNDE 3.

Muster: `projects/norwegen-2026/exports/vlog-edit/stage-caption-recipe.py`. Das Skript rendert
NUR PNGs (ueber `frameforge.design`) nach `exports/JGA/overlays/`. Kein ffmpeg, kein Render.
Das Compositing (Fade/Position/Timing/Slide/Jitter) macht `frameforge render` aus `timeline.json`.

Runde 3 (Christians 2. Preview-Feedback, `editorial-notes-round3.md`):

* **Eine Schrift ueberall: Bangers** (auch Akt 1, auch "Where is my mind"). Kein Poppins mehr.
* **Doppelebene fuer harten Schatten:** jeder Text = zwei Deckflaechen. Vorne Gold
  (`#d9a441`), dahinter derselbe Text in **Pink** (`#ff2e8a`), **+10/+10 px** versetzt (bei
  4K), KEIN Weichzeichner — Sticker-Optik. Ist die Frontfarbe Pink (WTF), wird der Schatten
  Gold.
* **Deutlich groesser:** alle Overlays ~2x der Runde-2-Groessen; "Where is my mind"-Titel ~5x,
  "mind?" darin nochmal ~4x.
* **Slant-Vorzeichen nach Placement:** `*-right` kippt nach links (negativ), `*-left` nach
  rechts (positiv) — Christian: "Schrift rechts muss nach links gekippt sein".
* **Geloescht:** `ov-kunstfigur` (kein Text an der Stelle), `ov-fx-krone-1707` (Krone raus),
  `ov-fx-delirium` (steht im Foto; Bild wackelt stattdessen).
* **Neu:** `ov-raetkeinkaese` ("Raet kein Kaese", Antwort auf den Gurken-Gag), `ov-wimm` als
  grosser Titel.
* **Text-/Positions-Aenderungen:** siehe TEXTS unten (Suelemann mit ue+nn, "500+ Biere",
  Crew-Update zweizeilig, "natuerlich"/"(noch) nicht", "Noch ahnten sie nicht"/"wie toll die
  Nacht wird", Lampen zweizeilig, letsgo top-right, praesente top-left, wtf top-left,
  christoph bottom-left, ichwaresnicht bottom-right).
* **FX-Cluster** statt Einzel-Icons: `ov-fx-herzen` (viele rosa Herzen, Knutsch-Szene),
  `ov-fx-sterne` (drehende Gold/Pink-Sterne, an lebendigen Akt-2-Stellen). `ov-fx-herz-1706`
  bleibt als kleiner Einzel-Sticker.

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

CREAM = "#fdf6ec"
GOLD = "#d9a441"
GOLD_HI = "#ffcf5c"
PINK = "#ff2e8a"
PINK_HI = "#ff5cb8"
MICHA_BLUE = "#4fd8ff"

# Harter Versatz-Schatten (Sticker-Optik), bei 4K. Christian: "10 Pixel rechts, 10 runter".
SHADOW_DX = 10
SHADOW_DY = 10

# placement -> (x%, y%, text-anchor). 6 % Sicherheitsrand zum Bildrand.
PLACEMENT = {
    "top-left": (6.0, 13.0, "start"),
    "top-right": (94.0, 13.0, "end"),
    "bottom-left": (6.0, 87.0, "start"),
    "bottom-right": (94.0, 87.0, "end"),
    "bottom": (50.0, 87.0, "middle"),
    "top": (50.0, 13.0, "middle"),
    "center": (50.0, 46.0, "middle"),
}

_TEXT_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.DOTALL)


def _slant_for(placement: str, magnitude: float = 4.0) -> float:
    """Rechts platzierter Text kippt nach links (negativ), links nach rechts (positiv).
    Christian Runde 3: "wenn die Schrift rechts ist, muss sie mehr nach links gekippt sein"."""
    if placement.endswith("right"):
        return -magnitude
    if placement.endswith("left"):
        return magnitude
    return -magnitude  # zentrierte: leichte Linkskippung wie bisher


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
              front_fill: str, shadow_fill: str,
              glow: str | None = None, glow_blur: int = 44) -> str:
    """Ersetzt das eine `<text>` des Templates durch zwei Deckflaechen: erst den versetzten
    Pink-(bzw. Gold-)Schatten, dann die Frontface. Beide um `pivot` schraeg gestellt, damit
    ein Wackel-`anim` im Render beide synchron bewegt (Christian: "im gleichen Rhythmus")."""
    px, py = pivot
    m = _TEXT_RE.search(svg)
    if not m:
        return svg
    attrs, inner = m.group(1), m.group(2)
    base_attrs = re.sub(r'\s*fill="[^"]*"', "", attrs)
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

    shadow = (
        f'<text{base_attrs} fill="{shadow_fill}" '
        f'transform="{rot} translate({SHADOW_DX} {SHADOW_DY})">{inner}</text>'
    )
    front = f'<text{base_attrs} fill="{front_fill}"{front_filter} transform="{rot}">{inner}</text>'
    svg = svg.replace(m.group(0), shadow + front, 1)
    if defs:
        svg = svg.replace(">", ">" + defs, 1)
    return svg


def render_text(out_name: str, template: Path, text: str, placement: str, *,
                size: float, front: str = GOLD, slant: float | None = None,
                inner_markup: str | None = None, glow: str | None = None) -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    x_pct, y_pct, anchor = PLACEMENT[placement]
    if slant is None:
        slant = _slant_for(placement)
    shadow = GOLD if front == PINK else PINK

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
    svg = _decorate(svg, _pivot(x_pct, y_pct), slant, front_fill=front, shadow_fill=shadow, glow=glow)
    render_svg_to_png(svg, OUT_DIR / out_name)
    print(f"  {out_name}")


def render_cluster(out_name: str, glyphs: list[str], fills: list[str], *,
                   count: int, seed: int, size_lo: int, size_hi: int,
                   area: tuple[float, float, float, float] = (10, 10, 90, 90)) -> None:
    """Comic-FX-Cluster: viele Glyphen (Herzen/Sterne) verschiedener Groesse/Drehung ueber
    eine Bildregion gestreut, mit weichem Glow. Deterministisch ueber `seed`. Christian
    Runde 3: "nicht so kleine einzelne Icons, ein paar mehr Icons zusammen"."""
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
    Kern in der Mitte. `render.py` kennt keinen `speedlines`-Effekt (Runde-2-`Effect`-Eintraege
    liefen ins Leere -> Christian: "Speedlines habe ich ueberhaupt nicht gesehen"). Deshalb als
    kurzer Overlay-Blitz statt als Clip-Effekt."""
    rnd = random.Random(seed)
    cx, cy = W / 2, H / 2
    inner = min(W, H) * 0.16   # freier Kern
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
# Reine Text-Overlays. (out, template, text, placement, size @4K, front-fill)
# Groessen ~2x Runde 2. Slant automatisch nach Placement.
TEXTS = [
    # -- Intro / Akt 1 --
    ("ov-letsgo.png",     TITLE_ONLY,    "Let's go!",                       "top-right",    200, GOLD),
    ("ov-sulemann.png",   SUBTITLE_ONLY, "Der Mann des Abends\nPizzamann Sülemann", "bottom-left", 130, GOLD),
    ("ov-biere.png",      TITLE_ONLY,    "500+ Biere",                      "bottom-right", 190, GOLD),
    ("ov-praesente.png",  SUBTITLE_ONLY, "Präsente für den\nJunggesellen",  "top-left",     120, GOLD),
    ("ov-geniesst.png",   SUBTITLE_ONLY, "Ein bisschen\ngenießt er es\nja schon", "top-left", 118, GOLD),
    # -- Akt 2 --
    ("ov-crewupdate.png",   SUBTITLE_ONLY, "Crew-Update\nDie verlorenen Söhne stoßen dazu", "bottom-left", 108, CREAM),
    ("ov-rooftop.png",      TITLE_ONLY,    "Rooftop Bar 58\nwir kommen!",     "top-left",     170, PINK),
    ("ov-hydrated.png",     TITLE_ONLY,    "stay\nhydrated",                  "top",          230, GOLD),
    ("ov-christoph.png",    TITLE_ONLY,    "Wo ist\nChristoph???",            "bottom-left",  180, GOLD),
    ("ov-token.png",        SUBTITLE_ONLY, "wolle Token kaufen ???",          "bottom-left",  150, GOLD),
    ("ov-lampen.png",       SUBTITLE_ONLY, "Gehen hier etwa schon\n        die Lampen aus?", "bottom-right", 108, CREAM),
    ("ov-natuerlich.png",   SUBTITLE_ONLY, "natürlich\n(noch) nicht",         "bottom-right", 128, CREAM),
    ("ov-weiterziehen.png", SUBTITLE_ONLY, "Noch ahnten sie nicht\nwie toll die Nacht wird", "bottom", 108, CREAM),
    ("ov-wtf.png",          TITLE_ONLY,    "WTF?",                            "top-left",     460, PINK),
    ("ov-ichwaresnicht.png", SUBTITLE_ONLY, "Ich war es\nnicht.",             "bottom-right", 190, CREAM),
    ("ov-gurken.png",       SUBTITLE_ONLY, "Der Michael mag Gurken.\nGib mir Gurken.\nDer Michael braucht Gurken.", "bottom-left", 108, CREAM),
    ("ov-raetkeinkaese.png", TITLE_ONLY,   "Rät kein Käse",                   "top-right",    120, GOLD),
]

# B9 Cast — (nn, key, name, placement, fill, size). Slant automatisch nach Placement
# (bottom-left -> +, bottom-right -> -). Groesse 2x.
CAST = [
    ("01", "witte",     "Witte",             "bottom-left",  CREAM,      260),
    ("02", "christoph",  "Christoph",         "bottom-right", CREAM,      260),
    ("03", "matti",      "Matti",             "bottom-left",  CREAM,      260),
    ("04", "bartosz",    "Bartosz",           "bottom-right", CREAM,      260),
    ("05", "hagi",       "Hagi",              "bottom-left",  CREAM,      260),
    ("06", "bernhard",   "Bernhard",          "bottom-right", CREAM,      260),
    ("07", "andre",      "André",             "bottom-left",  CREAM,      260),
    ("08", "skuub",      "Skuub",             "bottom-right", CREAM,      260),
    ("09", "micha",      "Micha im Delirium", "bottom-left",  MICHA_BLUE, 150),
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Text-Overlays (Bangers, Gold-Front + Pink-Schatten, 2x):")
    for out, tpl, text, place, size, front in TEXTS:
        render_text(out, tpl, text, place, size=size, front=front)

    print("Aftermath — grosser WIMM-Titel ('mind?' nochmal 4x):")
    # "Where is my" normal, "mind?" ~4x in eigenem tspan; placement top-left.
    x_pct = PLACEMENT["top-left"][0]
    wimm_inner = (
        f'<tspan x="{x_pct}%" dy="0">Where is my</tspan>'
        f'<tspan x="{x_pct}%" dy="620" font-size="620">mind?</tspan>'
    )
    render_text("ov-wimm.png", TITLE_ONLY, "Where is my\nmind?", "top-left",
                size=170, front=GOLD, inner_markup=wimm_inner)

    print("Cast-Intro-Namensstempel (B9, 2x, Slant nach Placement):")
    for nn, key, name, place, fill, size in CAST:
        render_text(f"ov-cast-{nn}-{key}.png", TITLE_ONLY, name, place, size=size, front=fill)

    print("Comic-FX-Cluster:")
    # Knutsch-Szene (~4:57): viele rosa Herzen, sprudeln aus der Mitte.
    # Nur `♥` (U+2665) — `❤` (U+2764) hat in Apple Symbols via cairosvg keinen Glyph (Tofu).
    render_cluster("ov-fx-herzen.png", ["♥"], [PINK, PINK_HI, "#ff8ac4"],
                   count=40, seed=457, size_lo=110, size_hi=360, area=(16, 12, 84, 88))
    # Drehende Gold/Pink-Sterne, an lebendigen Akt-2-Stellen. Nur `★` (Tofu-sicher).
    render_cluster("ov-fx-sterne.png", ["★"], [GOLD, GOLD_HI, PINK_HI],
                   count=18, seed=1621, size_lo=120, size_hi=320, area=(12, 12, 88, 78))
    # Einzelner Herz-Sticker "vor der Tuer" (1706) bleibt.
    render_cluster("ov-fx-herz-1706.png", ["♥"], [PINK, PINK_HI],
                   count=3, seed=1706, size_lo=200, size_hi=300, area=(60, 20, 82, 40))
    # Speedlines-Blitz (render.py kennt keinen speedlines-Effekt) -- kurzer Overlay.
    render_speedlines("ov-fx-speedlines.png")

    total = len(TEXTS) + 1 + len(CAST) + 4
    print(f"{total} PNG(s) geschrieben nach {OUT_DIR}")


if __name__ == "__main__":
    main()
