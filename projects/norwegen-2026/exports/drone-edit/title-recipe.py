"""Rezept fuer die Titel-Overlays von `drone-edit` ("Norwegen 2026 / Drone Edition").

Baugleich zu `exports/vlog-edit/title-recipe.py` — Nutzer-Wunsch 2026-08-09: "Den Anfang
moechte ich genauso haben vom Stil wie der Anfang vom vlog-edit", nur mit "Drone Edition"
statt "Roadtrip Edition". Alle Groessen, Positionen und Farben sind deshalb bewusst
identisch uebernommen; wer dort etwas aendert, muss es hier nachziehen (und umgekehrt).

Erzeugt vier PNGs unter `overlays/`: `title-box.png` (blaues Panel), `title.png`
("Norwegen", kommt von links), `subtitle.png` ("2026", von rechts, weiss) und `caption.png`
("Drone Edition", Akzentfarbe, verzoegert von links).

Timing/Animation (Slide-in, Drift) sitzt NICHT hier, sondern in `timeline.json`
(`tracks.overlay`, `ov-title-*`) — dieses Skript baut nur die statischen Bild-Layer.

`python projects/norwegen-2026/exports/drone-edit/title-recipe.py` von Repo-Root aus lauffaehig.
"""

from pathlib import Path

import yaml

from frameforge.design import build_svg_from_tokens, overlay_tokens, render_svg_to_png

ROOT = Path("projects/norwegen-2026")
RES = (3840, 2160)


def main() -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    out_dir = ROOT / "exports" / "drone-edit" / "overlays"
    out_dir.mkdir(parents=True, exist_ok=True)

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
            tokens, width=RES[0], height=RES[1], subtitle="Drone Edition",
            subtitle_size=caption_size, text_x_pct=79, text_y_pct=63, text_anchor="end",
        ),
    )
    render_svg_to_png(caption_svg, out_dir / "caption.png")
    print("title-box.png, title.png, subtitle.png, caption.png geschrieben nach", out_dir)


if __name__ == "__main__":
    main()
