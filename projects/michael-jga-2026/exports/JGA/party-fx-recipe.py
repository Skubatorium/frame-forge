"""Rezept fuer die Comic-/Party-FX-Overlays des Exports `JGA` (`michael-jga-2026`) — T8.

Muster: `projects/norwegen-2026/exports/vlog-edit/stage-caption-recipe.py`. Das Skript rendert
NUR PNGs (ueber `frameforge.design`) nach `exports/JGA/overlays/`. Kein ffmpeg, kein Render.
Das Compositing (Fade/Position/Timing/Slide) macht `frameforge render` aus `timeline.json`.

Was dieses Skript erzeugt (Runde 2, T8 — erstes Preview mit voller FX-Schicht):

1. Die **18 Text-Einblendungen** (`ov-*.png`), id/text/placement 1:1 aus den
   `OverlayClip`-Eintraegen in `timeline.json` (`tracks.overlay`). Templates: die BESTEHENDEN
   `title-only.svg` / `subtitle-only.svg`. Stil §0.6:
   - Akt 1 -> Poppins SemiBold/Bold, klein, randstaendig, Creme, dezenter Schlagschatten,
     minimal schraeg (-2 Grad).
   - Akt 2 -> Bangers, gross, "funky", staerker schraeg (-3..-5 Grad), Gold/Creme, weicher
     Schatten. Lange Zeilen kleiner (kein Wortumbruch in cairosvg -> `\n` -> `<tspan>`).
   Der animierte Auftritt (Buchstaben/Slide/Fade) laeuft im Render ueber die `anim`-Keys des
   Overlay-Clips (`slide_from_py`/`slide_in_s`/`fade_*`), nicht hier.

2. Die **9 Cast-Intro-Namensstempel** (`ov-cast-*.png`, B9) aus `title-only.svg` (Bangers,
   Creme, alternierend unten links/rechts, alternierend +/-5 Grad schraeg). "Stampft rein"
   laeuft im Render ueber `slide_from_py` + kurzer `fade_in_s`. Micha zuletzt, Stempel
   "Micha im Delirium" in Michas Sonderblau #4fd8ff (Plan 0004 §4.1).
   Namen exakt: Witte · Christoph · Matti · Bartosz · Hagi · Bernhard · André · Skuub ·
   Micha im Delirium. **André mit Akzent** — Bangers rendert den É-Glyph sauber (party-fx
   hat das per Test-PNG geprueft, §0.9-Entscheidung: ueberall "André").

3. Die **4 Comic-FX-Overlays** (`ov-fx-*.png`), sparsam an den im Beat-Sheet/§5 markierten
   Stellen:
   - `ov-fx-sticker-baer`  Stern-Sticker am Pappbaeren (1390) — der EINE Akt-1-Akzent.
   - `ov-fx-delirium`      "Delirium" als zittrige Pink-Neon-Leuchtschrift (1464).
   - `ov-fx-krone-1707`    goldene Krone auf der Dachterrasse (1707).
   - `ov-fx-herz-1706`     Herzchen "vor der Tuer" (1706).
   Speedlines (1621/1635/1637 run-ups) und color_pop (Cast-Cuts, 4835, Werbe-Look 1544)
   sind `Effect`-Eintraege in `VideoClip.effects` — KEINE PNGs, die legt party-fx direkt in
   `timeline.json`.

Aufruf von Repo-Root:  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/party-fx-recipe.py
"""

from __future__ import annotations

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
STICKER = Path("templates/svg/sticker.svg")

CREAM = "#fdf6ec"
GOLD = "#d9a441"
GOLD_HI = "#ffcf5c"
PINK = "#ff2e8a"
PINK_HI = "#ff5cb8"
MICHA_BLUE = "#4fd8ff"
SHADOW_INK = "#0d0722"

# placement -> (x%, y%, text-anchor). 6 % Sicherheitsrand zum Bildrand.
PLACEMENT = {
    "top-left": (6.0, 12.0, "start"),
    "top-right": (94.0, 12.0, "end"),
    "bottom-left": (6.0, 88.0, "start"),
    "bottom-right": (94.0, 88.0, "end"),
    "bottom": (50.0, 88.0, "middle"),
    "top": (50.0, 12.0, "middle"),
    "center": (50.0, 46.0, "middle"),
}


def _text_block(text: str, x_pct: float, size: int) -> tuple[str, int]:
    """Inner-Content fuer <text> — eine Zeile escaped, mehrere als <tspan>. Gibt (markup, n)."""
    lines = text.split("\n")
    if len(lines) == 1:
        return escape(text), 1
    lh = round(size * 1.15)
    spans = [
        f'<tspan x="{x_pct}%" dy="{0 if i == 0 else lh}">{escape(line)}</tspan>'
        for i, line in enumerate(lines)
    ]
    return "".join(spans), len(lines)


def _decorate(svg: str, pivot: tuple[int, int], slant_deg: float, *,
              glow: str | None = None, glow_blur: int = 40) -> str:
    """Fuegt Schlagschatten/Glow (<defs><filter>) + Schraegstellung (rotate um `pivot`) hinzu.

    Reine String-Manipulation am fertigen SVG — kein neues Template, keine Token-Abuse.
    """
    px, py = pivot
    if glow:
        prim = (f'<feDropShadow dx="0" dy="0" stdDeviation="{glow_blur}" '
                f'flood-color="{glow}" flood-opacity="0.9"/>')
    else:
        prim = (f'<feDropShadow dx="0" dy="{round(H * 0.004)}" stdDeviation="{round(H * 0.004)}" '
                f'flood-color="{SHADOW_INK}" flood-opacity="0.5"/>')
    defs = (f'<defs><filter id="fffx" x="-60%" y="-60%" width="220%" height="220%">'
            f'{prim}</filter></defs>')
    svg = svg.replace(">", ">" + defs, 1)  # direkt hinter dem oeffnenden <svg ...>
    attr = f' transform="rotate({slant_deg} {px} {py})" filter="url(#fffx)"'
    return svg.replace("<text ", "<text" + attr + " ")


def _pivot(x_pct: float, y_pct: float) -> tuple[int, int]:
    return round(x_pct / 100 * W), round(y_pct / 100 * H)


def render_text(out_name: str, template: Path, text: str, placement: str, *,
                font: str, size: int, fill: str, slant: float,
                glow: str | None = None, glow_blur: int = 40) -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    x_pct, y_pct, anchor = PLACEMENT[placement]

    inner, n_lines = _text_block(text, x_pct, size)
    # Bei mehrzeiligem Text an einer unteren/zentralen Position den Startpunkt anheben,
    # damit der Block im sicheren Bereich bleibt.
    lh_pct = (size * 1.15) / H * 100
    y_eff = y_pct
    if n_lines > 1:
        if y_pct >= 80:
            y_eff = y_pct - (n_lines - 1) * lh_pct
        elif 40 <= y_pct <= 60:
            y_eff = y_pct - (n_lines - 1) * lh_pct / 2

    extra = dict(
        text_x_pct=x_pct, text_y_pct=round(y_eff, 2), text_anchor=anchor,
        font_display=font, font_text=font,
    )
    if template == TITLE_ONLY:
        extra.update(title=inner, title_size=size, text_color=fill)
    else:
        extra.update(subtitle=inner, subtitle_size=size, subtitle_fill=fill)

    svg = build_svg_from_tokens(template, overlay_tokens(tokens, width=W, height=H, **extra))
    svg = _decorate(svg, _pivot(x_pct, y_pct), slant, glow=glow, glow_blur=glow_blur)
    render_svg_to_png(svg, OUT_DIR / out_name)
    print(f"  {out_name}")


def render_sticker(out_name: str, glyph: str, *, x_pct: float, y_pct: float,
                   size: int, fill: str, glow: str) -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    svg = build_svg_from_tokens(
        STICKER,
        overlay_tokens(
            tokens, width=W, height=H,
            glyph=escape(glyph), sticker_x_pct=x_pct, sticker_y_pct=y_pct,
            sticker_size=size, sticker_fill=fill,
            sticker_glow_color=glow, sticker_glow_blur=round(H * 0.014, 1),
            font_display="Apple Symbols",
        ),
    )
    render_svg_to_png(svg, OUT_DIR / out_name)
    print(f"  {out_name}")


# ---------------------------------------------------------------------------
# Akt 1 — Poppins, klein, randstaendig, Creme, -2 Grad, dunkler Schatten.
ACT1 = [
    ("ov-letsgo.png",     TITLE_ONLY,    "Let's go",                              "bottom-right", 92),
    ("ov-sulemann.png",   SUBTITLE_ONLY, "Der Mann des Abends:\nSuleman Pizza-Star", "bottom-left", 60),
    ("ov-biere.png",      TITLE_ONLY,    "~250 Biere",                            "bottom-right", 88),
    ("ov-praesente.png",  SUBTITLE_ONLY, "Praesente fuer den Junggesellen",       "bottom-left",  54),
    ("ov-geniesst.png",   SUBTITLE_ONLY, "Ein bisschen\ngeniesst er es\nja schon", "top-left",    60),
    ("ov-kunstfigur.png", TITLE_ONLY,    "Die wandelnde Kunstfigur",              "bottom-right", 70),
]

# Akt 2 — Bangers, gross/funky. (out, template, text, placement, size, fill, slant)
ACT2 = [
    ("ov-crewupdate.png",   SUBTITLE_ONLY, "Crew-Update - die verlorenen Soehne stossen dazu", "bottom-left", 66, CREAM, -3),
    ("ov-rooftop.png",      TITLE_ONLY,    "Rooftop Bar 58 - wir kommen",          "top-left",     150, GOLD,  -4),
    ("ov-hydrated.png",     TITLE_ONLY,    "stay\nhydrated",                       "top-right",    190, GOLD,  -4),
    ("ov-christoph.png",    TITLE_ONLY,    "Wo ist Christoph???",                  "bottom-right", 150, CREAM, -4),
    ("ov-token.png",        SUBTITLE_ONLY, "wolle Token kaufen ???",               "bottom-left",  130, GOLD,  -4),
    ("ov-lampen.png",       SUBTITLE_ONLY, "Gehen hier etwa schon die Lampen aus?", "bottom-right", 92, CREAM, -3),
    ("ov-natuerlich.png",   SUBTITLE_ONLY, "Natuerlich ... (noch nicht)",          "bottom-right", 108, CREAM, -4),
    ("ov-weiterziehen.png", SUBTITLE_ONLY, "Noch ahnen sie nicht, wie toll der Abend wird", "bottom-right", 64, CREAM, -3),
    ("ov-wtf.png",          TITLE_ONLY,    "WTF?",                                 "bottom-right", 240, GOLD,  -5),
    ("ov-ichwaresnicht.png", SUBTITLE_ONLY, "Ich war es nicht.",                   "bottom-right", 120, CREAM, -4),
    ("ov-gurken.png",       SUBTITLE_ONLY, "Der Michael mag Gurken.\nGib mir Gurken.\nDer Michael braucht Gurken.", "bottom-left", 92, CREAM, -3),
]

# B9 Cast — (nn, key, name, placement, slant, fill, size)
CAST = [
    ("01", "witte",    "Witte",             "bottom-left",  -5, CREAM,      200),
    ("02", "christoph", "Christoph",         "bottom-right",  5, CREAM,      200),
    ("03", "matti",     "Matti",             "bottom-left",  -5, CREAM,      200),
    ("04", "bartosz",   "Bartosz",           "bottom-right",  5, CREAM,      200),
    ("05", "hagi",      "Hagi",              "bottom-left",  -5, CREAM,      200),
    ("06", "bernhard",  "Bernhard",          "bottom-right",  5, CREAM,      200),
    ("07", "andre",     "André",             "bottom-left",  -5, CREAM,      200),
    ("08", "skuub",     "Skuub",             "bottom-right",  5, CREAM,      200),
    ("09", "micha",     "Micha im Delirium", "bottom-left",  -5, MICHA_BLUE, 120),
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Akt 1 (Poppins, dezent):")
    for out, tpl, text, place, size in ACT1:
        render_text(out, tpl, text, place, font="Poppins", size=size, fill=CREAM, slant=-2)

    print("Akt 2 (Bangers, funky):")
    for out, tpl, text, place, size, fill, slant in ACT2:
        glow = PINK_HI if fill == PINK else None
        render_text(out, tpl, text, place, font="Bangers", size=size, fill=fill, slant=slant)

    print("Aftermath:")
    render_text("ov-wimm.png", SUBTITLE_ONLY, "Where is my mind?", "bottom-left",
                font="Poppins", size=64, fill=CREAM, slant=-2)

    print("Cast-Intro-Namensstempel (B9):")
    for nn, key, name, place, slant, fill, size in CAST:
        render_text(f"ov-cast-{nn}-{key}.png", TITLE_ONLY, name, place,
                    font="Bangers", size=size, fill=fill, slant=slant)

    print("Comic-FX (sparsam):")
    render_sticker("ov-fx-sticker-baer.png", "★", x_pct=70.0, y_pct=26.0,
                   size=150, fill=GOLD, glow=GOLD_HI)
    render_text("ov-fx-delirium.png", TITLE_ONLY, "Delirium", "center",
                font="Bangers", size=170, fill=PINK, slant=-3, glow=PINK_HI, glow_blur=55)
    render_sticker("ov-fx-krone-1707.png", "♛", x_pct=30.0, y_pct=24.0,
                   size=240, fill=GOLD, glow=GOLD_HI)
    render_sticker("ov-fx-herz-1706.png", "♥", x_pct=72.0, y_pct=30.0,
                   size=240, fill=PINK, glow=PINK_HI)

    total = len(ACT1) + len(ACT2) + 1 + len(CAST) + 4
    print(f"{total} PNG(s) geschrieben nach {OUT_DIR}")


if __name__ == "__main__":
    main()
