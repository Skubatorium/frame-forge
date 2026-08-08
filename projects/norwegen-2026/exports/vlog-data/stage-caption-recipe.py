"""Rezept fuer die Etappen-Bauchbinden von `vlog-data` ("Tag N · Ort", kurz ueber dem
Karten-Inset unten rechts).

Nutzer-Feedback (2026-08-08, Preview-Runde 1): die Karte zeigte bisher nur den Kilometerstand,
kein Ortsbezug -- kurze Einblendung von Tag+Ziel pro Kapitel gibt Kontext, ohne dauerhaft
Platz zu beanspruchen. Tag-Nummerierung ist die des Nutzers, nicht die von `stages.csv`:
`stages.csv`-Tag 1 (17.07., Beladen) ist "Tag 0", `stages.csv`-Tag 2 (18.07., erster
Fahrtag) ist "Tag 1" -- daher `last_day - 1`. K12 ist bewusst ausgelassen: reine Wiederholung
von K11 (Lom), keine neue Information.

Erzeugt EIN gemeinsames `stage-caption-box.png` (immer dieselbe Geometrie, direkt ueber dem
768x432-Karten-Inset mit 60px Rand -- siehe `frameforge/render.py`
`overlay=x=W-w-60:y=H-h-60`) und je Kapitel ein `stage-caption-<K>.png` mit dem Text.

Timing (`tl_in`, `dur`, Fade) sitzt in `timeline.json` (`tracks.overlay`,
`ov-stage-box-*`/`ov-stage-text-*`), nicht hier.

`python stage-caption-recipe.py` von Repo-Root aus lauffaehig.
"""

import csv
from pathlib import Path

import yaml

from frameforge.design import build_svg_from_tokens, overlay_tokens, render_svg_to_png

ROOT = Path("projects/norwegen-2026")
RES = (3840, 2160)

# Direkt ueber dem Karten-Inset (768x432 Box, 60px Rand unten rechts), 24px Luft dazwischen.
BOX_RIGHT_PX = RES[0] - 60
BOX_BOTTOM_PX = RES[1] - 60 - 432 - 24
BOX_W_PX = 680
BOX_H_PX = 100

CHAPTERS_DAYS = {
    "K2": [1, 2], "K3": [3], "K4": [4], "K5": [5, 6], "K6": [7], "K7": [8], "K8": [9],
    "K9": [10], "K10": [11], "K11": [12], "K13": [13], "K14": [14, 15], "K15": [16, 17, 18, 19],
}  # K12 bewusst ausgelassen -- direkte Wiederholung von K11 (Lom), keine neue Info.


def main() -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    out_dir = ROOT / "exports" / "vlog-data" / "overlays"
    out_dir.mkdir(parents=True, exist_ok=True)

    box_x_pct = (BOX_RIGHT_PX - BOX_W_PX) / RES[0] * 100
    box_y_pct = (BOX_BOTTOM_PX - BOX_H_PX) / RES[1] * 100
    box_w_pct = BOX_W_PX / RES[0] * 100
    box_h_pct = BOX_H_PX / RES[1] * 100
    text_x_pct = (BOX_RIGHT_PX - BOX_W_PX / 2) / RES[0] * 100
    text_y_pct = (BOX_BOTTOM_PX - BOX_H_PX / 2) / RES[1] * 100

    box_svg = build_svg_from_tokens(
        Path("templates/svg/box-only.svg"),
        overlay_tokens(
            tokens, width=RES[0], height=RES[1],
            box_x_pct=box_x_pct, box_y_pct=box_y_pct, box_w_pct=box_w_pct, box_h_pct=box_h_pct,
        ),
    )
    render_svg_to_png(box_svg, out_dir / "stage-caption-box.png")

    caption_size = round(overlay_tokens(tokens, width=RES[0], height=RES[1])["caption_size"] * 0.8, 1)
    rows = list(csv.DictReader(open(ROOT / "route" / "stages.csv")))
    byday = {int(r["day"]): r for r in rows}

    for chapter_id, days in CHAPTERS_DAYS.items():
        last_day = days[-1]
        row = byday[last_day]
        label = f"Tag {last_day - 1} · {row['to']}"
        svg = build_svg_from_tokens(
            Path("templates/svg/subtitle-only.svg"),
            overlay_tokens(
                tokens, width=RES[0], height=RES[1], subtitle=label,
                subtitle_size=caption_size, text_x_pct=text_x_pct, text_y_pct=text_y_pct,
                text_anchor="middle", subtitle_fill=tokens.get("text_color", "#ffffff"),
            ),
        )
        render_svg_to_png(svg, out_dir / f"stage-caption-{chapter_id}.png")
        print(chapter_id, label)

    print("stage-caption-box.png +", len(CHAPTERS_DAYS), "Text-PNGs geschrieben nach", out_dir)


if __name__ == "__main__":
    main()
