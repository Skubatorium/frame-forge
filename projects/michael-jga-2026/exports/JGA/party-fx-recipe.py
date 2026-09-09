"""Rezept fuer die Comic-/Party-FX-Overlays des Exports `JGA` (`michael-jga-2026`).

Muster: `projects/norwegen-2026/exports/vlog-edit/stage-caption-recipe.py`. Das Skript rendert
NUR PNGs (ueber `frameforge.design`) nach `exports/JGA/overlays/`. Kein ffmpeg, kein Render.
Das Compositing (Fade/Position/Timing) macht `frameforge render` aus `timeline.json`.

Was dieses Skript in dieser Runde erzeugt (erste Preview, bewusst begrenzt):

1. Die **12 Text-Einblendungen**, die der `timeline-builder` als `OverlayClip`-Stubs mit
   `template`/`text`/`placement` in `tracks.overlay` angelegt hat (PNG-Pfade `overlays/ov-*.png`
   waren noch leer). Templates: die BESTEHENDEN `title-only.svg` / `subtitle-only.svg` /
   `title-card.svg`. Akt 1 klein und randstaendig (Poppins/Creme, ~Caption-Groesse), Akt 2
   gross und fetzig (Bangers, ~Title-Groesse, Gold-Akzent).

2. Die **9 Cast-Intro-Namensstempel** (B9, Red-Bar) als eigene PNGs `overlays/ov-cast-*.png`
   aus dem BESTEHENDEN `title-only.svg` (reiner Text, Bangers, zentriert). "Stampft rein" laeuft
   im Render ueber die bestehenden `anim`-Schluessel (kurzer `slide_from_py` von oben +
   `fade_in_s`) — keine neue Animationslogik. Micha zuletzt, Stempel "Micha im Delirium" in
   Michas Sonderblau #4fd8ff (Plan 0004 §4.1). Namen exakt:
   Witte · Christoph · Matti · Bartosz · Hagi · Bernhard · André · Skuub · Micha im Delirium.

Die `color_pop` / `cartoon_outline` `Effect`-Eintraege sind KEINE PNGs — sie stehen direkt in
`VideoClip.effects` in `timeline.json` (von `party-fx` dort eingetragen, `frameforge/render.py`
`_color_pop_expr` / `_cartoon_outline_expr` interpretiert sie).

--------------------------------------------------------------------------------------------
TODO NAECHSTE RUNDE (bewusst NICHT in dieser Preview — `thought-bubble.svg` / `sticker.svg` /
`speedlines.svg` haben rote Tests in `tests/test_design.py`, fremdes WIP: Content-Tokens
`bubble_line1` / `glyph` ohne Default). Erst nach gruenen Tests umsetzen. Wunschstellen aus
editorial-notes.md / beatsheet.md:

  - 1381  Sprechblase "Design Award 2026"  (der EINE erlaubte Akt-1-Akzent; Clip c037,
          tl ~106.5 s — vom builder als "einziger Akt-1 FX-Akzent" markiert)
  - 1390  kleiner Sticker am Pappbaeren (NUR falls 1381 gestrichen wird — nicht beide)
  - 1455 / c079  "Timmermans" — Pfeile + "Nebengewerbe", Wortspiel mit "Witte"
  - 1464 / c086  "Delirium" als zittrig nachgemalte Leuchtschrift
  - 1544 / c112  Corona-Extra "Werbe"-Look, Fluessigkeitslinie = Horizont
  - 1514 / c113  "Wo ist Christoph?" zusaetzlich als FX (Pfeil auf die fehlende Person)
  - 1512 / 1514  "Wo ist Christoph?" (Text-Overlay ist schon drin: ov-christoph)
  - 1621 / 1635 / 1637 / 4835  Speedlines auf den lautesten Beats (Tanz/Gesang/Tequila) —
          color_pop ist in dieser Runde schon gesetzt, Speedlines kommen dazu
  - 1650 / c178  dezenter Text zu den "Kotz-Kandidaten"
  - 1706 / c194  Herzchen + goldene Kronen (einziger Aftermath-Effekt)
  - 1707 / c104? Kronen/Herzchen auf der Dachterrasse (Rooftop)
  - Cast-Intro: per-Cut `color_pop` auf allen 9 Fotos + 9 SFX-`AudioClip`s (type "sfx") —
          in dieser Runde nur color_pop auf Michas Cut gesetzt (Budget ~6-8 Effekte/Film);
          SFX-Dateien fehlen komplett (`music/sfx/` existiert nicht), siehe audio-plan.md §5.
--------------------------------------------------------------------------------------------

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

TEMPLATE = {
    "title-only": Path("templates/svg/title-only.svg"),
    "subtitle-only": Path("templates/svg/subtitle-only.svg"),
    "title-card": Path("templates/svg/title-card.svg"),
}

# placement-Schluessel aus den OverlayClip-Stubs -> (x%, y%, text-anchor). 6 % Sicherheitsrand.
PLACEMENT = {
    "top-left": (6.0, 12.0, "start"),
    "top-right": (94.0, 12.0, "end"),
    "bottom-left": (6.0, 88.0, "start"),
    "bottom-right": (94.0, 88.0, "end"),
    "bottom": (50.0, 88.0, "middle"),
    "top": (50.0, 12.0, "middle"),
    "center": (50.0, 50.0, "middle"),
}

# Die 12 Text-Einblendungen. id/text/template/placement 1:1 aus den timeline.json-Stubs
# (tracks.overlay). `act` steuert Groesse/Farbe: 1 = klein/creme/randstaendig, 2 = gross/fetzig.
# `size_scale` daempft ueberlange Zeilen (kein Wortumbruch in cairosvg).
TEXT_OVERLAYS = [
    {"id": "ov-letsgo",    "template": "title-only",    "text": "Let’s go",              "placement": "top-left",     "act": 1},
    {"id": "ov-sulemann",  "template": "subtitle-only", "text": "Es lebe Sülemann",       "placement": "bottom-left",  "act": 1},
    {"id": "ov-biere",     "template": "title-only",    "text": "~250 Biere",                 "placement": "bottom-right", "act": 1},
    {"id": "ov-praesente", "template": "subtitle-only", "text": "Präsente für den Junggesellen", "placement": "bottom", "act": 1, "size_scale": 0.85},
    {"id": "ov-genuss",    "template": "title-only",    "text": "Genuss pur",                 "placement": "bottom-right", "act": 1},
    {"id": "ov-rooftop",   "template": "title-card",    "text": "Rooftop Bar 58 — wir kommen", "placement": "center",  "act": 2, "size_scale": 0.72},
    {"id": "ov-hydrated",  "template": "subtitle-only", "text": "Stay hydrated",              "placement": "top-right",    "act": 2},
    {"id": "ov-christoph", "template": "title-only",    "text": "Wo ist Christoph?",          "placement": "center",       "act": 2, "size_scale": 0.85},
    {"id": "ov-token",     "template": "subtitle-only", "text": "Frische Token",              "placement": "top-left",     "act": 2},
    {"id": "ov-lampen",    "template": "subtitle-only", "text": "Gehen hier etwa schon die Lampen aus?", "placement": "center", "act": 2, "size_scale": 0.9},
    {"id": "ov-wtf",       "template": "title-only",    "text": "WTF?",                       "placement": "center",       "act": 2},
    {"id": "ov-gurken",    "template": "subtitle-only", "text": "Der Michael mag Gurken. Gib mir Gurken. Der Michael braucht Gurken.", "placement": "bottom", "act": 2, "size_scale": 0.55},
]

# B9 Cast-Intro — Reihenfolge/Namen exakt (beatsheet.md B9). Micha zuletzt, Sonderblau.
CAST = [
    ("01", "witte",    "Witte",             "#fdf6ec"),
    ("02", "christoph", "Christoph",         "#fdf6ec"),
    ("03", "matti",     "Matti",             "#fdf6ec"),
    ("04", "bartosz",   "Bartosz",           "#fdf6ec"),
    ("05", "hagi",      "Hagi",              "#fdf6ec"),
    ("06", "bernhard",  "Bernhard",          "#fdf6ec"),
    ("07", "andre",     "André",         "#fdf6ec"),
    ("08", "skuub",     "Skuub",             "#fdf6ec"),
    ("09", "micha",     "Micha im Delirium", "#4fd8ff"),
]


def _render(template_key: str, out_name: str, tokens: dict, **extra) -> None:
    svg = build_svg_from_tokens(
        TEMPLATE[template_key],
        overlay_tokens(tokens, width=RES[0], height=RES[1], **extra),
    )
    render_svg_to_png(svg, OUT_DIR / out_name)
    print(f"  {out_name}")


def main() -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = overlay_tokens(tokens, width=RES[0], height=RES[1])

    print("Text-Einblendungen:")
    for ov in TEXT_OVERLAYS:
        x, y, anchor = PLACEMENT[ov["placement"]]
        scale = ov.get("size_scale", 1.0)
        text = escape(ov["text"])
        if ov["template"] == "title-only":
            # Akt 1: ~Caption-Groesse, Creme. Akt 2: ~Title-Groesse (fetzig), Creme.
            size = base["caption_size"] * 1.15 if ov["act"] == 1 else base["title_size"] * 0.92
            _render(
                "title-only", f"{ov['id']}.png", tokens,
                title=text, title_size=round(size * scale, 1),
                text_color="#fdf6ec",
                text_x_pct=x, text_y_pct=y, text_anchor=anchor,
            )
        elif ov["template"] == "subtitle-only":
            # Akt 1: Caption-Groesse, Creme (dezent). Akt 2: gross, Gold-Akzent.
            if ov["act"] == 1:
                size, fill = base["caption_size"] * 1.1, "#fdf6ec"
            else:
                size, fill = base["subtitle_size"] * 1.65, "#d9a441"
            _render(
                "subtitle-only", f"{ov['id']}.png", tokens,
                subtitle=text, subtitle_size=round(size * scale, 1),
                subtitle_fill=fill,
                text_x_pct=x, text_y_pct=y, text_anchor=anchor,
            )
        else:  # title-card (ov-rooftop): grosser Zweizeiler-Rahmen, nur Titelzeile genutzt
            _render(
                "title-card", f"{ov['id']}.png", tokens,
                title=text, subtitle="",
                title_size=round(base["title_size"] * scale, 1),
            )

    print("Cast-Intro-Namensstempel (B9):")
    stamp_size = base["title_size"] * 0.95
    for n, key, name, fill in CAST:
        _render(
            "title-only", f"ov-cast-{n}-{key}.png", tokens,
            title=escape(name),
            title_size=round(stamp_size * (0.7 if name == "Micha im Delirium" else 1.0), 1),
            text_color=fill,
            text_x_pct=50.0, text_y_pct=52.0, text_anchor="middle",
        )

    n = len(TEXT_OVERLAYS) + len(CAST)
    print(f"{n} PNG(s) geschrieben nach {OUT_DIR}")


if __name__ == "__main__":
    main()
