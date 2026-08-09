"""Rezept fuer die Titel-Overlays von `vlog-edit` (K1, "Norwegen 2026 / Roadtrip Edition").

Erzeugt vier PNGs unter `overlays/`: `title-box.png` (das eine gemeinsame Panel), `title.png`
("Norwegen", kommt von links), `subtitle.png` ("2026", kommt von rechts, 75% der Norwegen-
Groesse, weiss statt Akzentfarbe) und `caption.png` ("Roadtrip Edition", 75% der 2026-Groesse,
Akzentfarbe/gelb, verzoegert von links). Diagonal-Layout aus Nutzer-Feedback (2026-08-08,
Preview-Runde 1): Box nur so breit wie "2026", Norwegen ragt gross oben links darueber hinaus,
2026 + Roadtrip Edition sitzen als zwei Zeilen in/auf der Box unten rechts.

Timing/Animation (Slide-in, Drift) sitzt NICHT hier, sondern in `timeline.json`
(`tracks.overlay`, `ov-title-*`) -- dieses Skript baut nur die statischen Bild-Layer.

`python title-recipe.py` von Repo-Root aus lauffaehig.
"""

from pathlib import Path

import yaml

from frameforge.design import build_svg_from_tokens, overlay_tokens, render_svg_to_png

ROOT = Path("projects/norwegen-2026")
RES = (3840, 2160)


def main() -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    out_dir = ROOT / "exports" / "vlog-edit" / "overlays"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Runde 3: "Ich finde das Wort Norwegen muesste auf jeden Fall noch groesser, also bestimmt
    # doppelt so gross fast." 1.15 (Runde 2) -> 2.2 vom Basis-`title_size`. "2026" und
    # "Roadtrip Edition" bleiben bei ihren relativen Groessen, wachsen also nicht mit -- sonst
    # sprengt die Zeile die Box, und der Groessenkontrast war ausdruecklich gewollt.
    base_title = overlay_tokens(tokens, width=RES[0], height=RES[1])["title_size"]
    title_size = round(base_title * 2.2, 1)
    year_size = round(base_title * 1.15 * 0.75, 1)
    caption_size = round(year_size * 0.75, 1)

    box_svg = build_svg_from_tokens(
        Path("templates/svg/box-only.svg"),
        overlay_tokens(
            tokens, width=RES[0], height=RES[1],
            box_x_pct=63, box_y_pct=49, box_w_pct=20, box_h_pct=18,
        ),
    )
    render_svg_to_png(box_svg, out_dir / "title-box.png")

    title_svg = build_svg_from_tokens(
        Path("templates/svg/title-only.svg"),
        overlay_tokens(
            tokens, width=RES[0], height=RES[1], title="Norwegen",
            title_size=title_size, text_x_pct=18, text_y_pct=42, text_anchor="start",
        ),
    )
    render_svg_to_png(title_svg, out_dir / "title.png")

    year_svg = build_svg_from_tokens(
        Path("templates/svg/subtitle-only.svg"),
        overlay_tokens(
            tokens, width=RES[0], height=RES[1], subtitle="2026",
            subtitle_size=year_size, text_x_pct=81, text_y_pct=55, text_anchor="end",
            subtitle_fill=tokens.get("text_color", "#ffffff"),
        ),
    )
    render_svg_to_png(year_svg, out_dir / "subtitle.png")

    caption_svg = build_svg_from_tokens(
        Path("templates/svg/subtitle-only.svg"),
        overlay_tokens(
            tokens, width=RES[0], height=RES[1], subtitle="Roadtrip Edition",
            subtitle_size=caption_size, text_x_pct=79, text_y_pct=63, text_anchor="end",
        ),
    )
    render_svg_to_png(caption_svg, out_dir / "caption.png")
    print("title-box.png, title.png, subtitle.png, caption.png geschrieben nach", out_dir)


if __name__ == "__main__":
    main()
