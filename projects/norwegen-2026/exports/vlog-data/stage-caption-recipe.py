"""Rezept fuer die Etappen-Bauchbinden von `vlog-data`, unten links.

Runde 3 (Nutzer-Feedback 2026-08-08): die Karte unten rechts ist komplett entfallen ("die ist
nicht gross genug, sie lenkt ab -- ich muss leider die Entscheidung treffen, dass wir die Karte
ausbauen"). Als Ersatz uebernimmt die Bauchbinde die Orientierung, die vorher die Karte geben
sollte, und zwar in der Form, die der Nutzer aus dem ersten Teaser kannte:

- **Fahrtag:** zwei Zeilen -- "Tag N" oben, darunter "Von -> Nach · XXX km"
  ("wir koennen sowas schreiben wie Tag 0 packen, Tag 1 und dann schreiben wir hin Grevenbroich
  nach Flensburg und vielleicht die Kilometeranzahl, die man gefahren ist").
- **Aktivitaetstag:** "Tag N" oben, darunter "Ort · Aktivitaet" ohne Kilometer
  ("oder es ist ein Aktivitaets-Tag, wo ihr sagt, Tag am Meer oder sowas").

Tag-Nummerierung ist die des Nutzers, nicht die von `stages.csv`: `stages.csv`-Tag 1 (17.07.,
Beladen) ist "Tag 0" -- daher `day - 1`.

Position: unten LINKS (vorher unten rechts ueber dem Karten-Inset). Timing (`tl_in`, `dur`,
Fades) rechnet `rebuild-recipe.py` und schreibt es in `timeline.json`, nicht hier.

`python projects/norwegen-2026/exports/vlog-data/stage-caption-recipe.py` von Repo-Root aus.
"""

import csv
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

from frameforge.design import build_svg_from_tokens, overlay_tokens, render_svg_to_png

ROOT = Path("projects/norwegen-2026")
RES = (3840, 2160)

# Unten links, gleicher Sicherheitsabstand wie die Karte vorher rechts hatte (60px).
# Groesse aus der Typo abgeleitet (siehe `main`), nicht geraten: die erste Fassung war mit
# 210px Hoehe und caption-Groesse zu klein und zu gedraengt, um beim Zusehen ablesbar zu sein.
BOX_LEFT_PX = 60
BOX_BOTTOM_PX = RES[1] - 60
BOX_W_PX = 1560
PAD_X_PX = 56
PAD_Y_PX = 44

# Welche Reisetage im Film ein Kapitel bekommen -- muss zu `DAYS` in `rebuild-recipe.py` passen.
DAY_TO_STAGE = {
    "2026-07-17": 1, "2026-07-18": 2, "2026-07-19": 3, "2026-07-20": 4, "2026-07-21": 5,
    "2026-07-22": 6, "2026-07-23": 7, "2026-07-24": 8, "2026-07-25": 9, "2026-07-26": 10,
    "2026-07-27": 11, "2026-07-28": 12, "2026-07-29": 13, "2026-07-30": 14, "2026-08-01": 16,
    "2026-08-03": 18, "2026-08-04": 19,
}

# Zweite Zeile fuer Tage ohne Etappe (from == to). Kurz und konkret statt "Aktivitaetstag".
# Bildschirmtext, deshalb mit echten Umlauten (die ASCII-Ersatzschreibung aus `stages.csv`-
# Notizen gehoert nicht in den Film).
ACTIVITY_LABEL = {
    "2026-07-17": "Grevenbroich · gepackt",
    "2026-07-20": "Skien · Hütte am See",
    "2026-07-21": "Skien · Tag am Meer",
    "2026-07-22": "Skien · Ruhetag vor dem Roadtrip",
    "2026-07-25": "Aurland · Fjord & Wikingerdorf",
    "2026-07-27": "Geiranger · Geburtstag & RIB-Safari",
    "2026-07-30": "Uvdal · Angeln, Bogen & Kanu",
    "2026-08-03": "Skien · Angeln an der Schärenküste",
}

# Zwischenstationen, die der Nutzer namentlich in der Bauchbinde sehen wollte.
VIA_LABEL = {
    "2026-07-28": "über Trollstigen",
    "2026-07-24": "über Stegastein",
}


def main() -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    out_dir = ROOT / "exports" / "vlog-data" / "overlays"
    out_dir.mkdir(parents=True, exist_ok=True)

    base = overlay_tokens(tokens, width=RES[0], height=RES[1])
    # "Tag N" in Unterzeilen-Groesse, die Etappe knapp darunter in Caption-Groesse -- deutlich
    # groesser als die erste Fassung, damit die Binde im Vorbeischauen lesbar ist.
    day_size = base["subtitle_size"]
    route_size = base["caption_size"]
    line_gap = round(day_size * 0.30)
    box_h_px = round(PAD_Y_PX * 2 + day_size + line_gap + route_size)
    box_top_px = BOX_BOTTOM_PX - box_h_px

    box_x_pct = BOX_LEFT_PX / RES[0] * 100
    box_y_pct = box_top_px / RES[1] * 100
    box_w_pct = BOX_W_PX / RES[0] * 100
    box_h_pct = box_h_px / RES[1] * 100
    text_x_pct = (BOX_LEFT_PX + PAD_X_PX) / RES[0] * 100
    # `dominant-baseline: middle` => y ist die Zeilenmitte, nicht die Grundlinie.
    day_y_pct = (box_top_px + PAD_Y_PX + day_size / 2) / RES[1] * 100
    route_y_pct = (BOX_BOTTOM_PX - PAD_Y_PX - route_size / 2) / RES[1] * 100

    box_svg = build_svg_from_tokens(
        Path("templates/svg/box-only.svg"),
        overlay_tokens(
            tokens, width=RES[0], height=RES[1],
            box_x_pct=box_x_pct, box_y_pct=box_y_pct, box_w_pct=box_w_pct, box_h_pct=box_h_pct,
        ),
    )
    render_svg_to_png(box_svg, out_dir / "stage-caption-box.png")

    rows = {int(r["day"]): r for r in csv.DictReader(open(ROOT / "route" / "stages.csv"))}

    for date, stage_day in sorted(DAY_TO_STAGE.items()):
        row = rows[stage_day]
        day_label = f"Tag {stage_day - 1}"
        if date in ACTIVITY_LABEL:
            route_label = ACTIVITY_LABEL[date]
        else:
            km = float(row["km"])
            # Kein "→": Avenir Next hat keinen Pfeil-Glyph, cairosvg setzt dafuer ein
            # Ersatzkaestchen (im ersten Render als Tofu-Box sichtbar geworden). "›" ist in der
            # Schrift vorhanden und liest sich genauso als Richtung; "·" bleibt der Trenner
            # vor der Kilometerangabe.
            route_label = f"{row['from']} › {row['to']}"
            if date in VIA_LABEL:
                route_label += f" {VIA_LABEL[date]}"
            route_label += f" · {km:,.0f} km".replace(",", ".")

        # Zwei Zeilen = zwei PNGs waeren zwei Overlays pro Kapitel; stattdessen beide Texte in
        # EIN SVG, damit `timeline.json` pro Kapitel bei Box + Text bleibt.
        svg = build_svg_from_tokens(
            Path("templates/svg/stage-caption.svg"),
            overlay_tokens(
                tokens, width=RES[0], height=RES[1],
                # `build_svg_from_tokens` substituiert roh in den SVG-Text -- ein "&" im Label
                # (z.B. "Fjord & Wikingerdorf") laesst cairosvgs strikten XML-Parser mit
                # "not well-formed" abbrechen. Gleiche Klasse von Falle wie das "--" in
                # SVG-Kommentaren aus Runde 2, deshalb hier explizit escapen.
                day_label=escape(day_label), stage_day_size=day_size,
                stage_day_x_pct=text_x_pct, stage_day_y_pct=day_y_pct,
                stage_label=escape(route_label), stage_route_size=route_size,
                stage_route_x_pct=text_x_pct, stage_route_y_pct=route_y_pct,
            ),
        )
        render_svg_to_png(svg, out_dir / f"stage-caption-{date}.png")
        print(f"{date}  {day_label} · {route_label}")

    print(f"stage-caption-box.png + {len(DAY_TO_STAGE)} Text-PNGs geschrieben nach {out_dir}")


if __name__ == "__main__":
    main()
