"""Rezept fuer die Etappen-Bauchbinden von `vlog-edit`, unten links.

Runde 3 (Nutzer-Feedback 2026-08-08): die Karte unten rechts ist komplett entfallen ("die ist
nicht gross genug, sie lenkt ab -- ich muss leider die Entscheidung treffen, dass wir die Karte
ausbauen"). Als Ersatz uebernimmt die Bauchbinde die Orientierung, die vorher die Karte geben
sollte.

Runde 4 (Nutzer-Feedback 2026-08-09, nach dem 1080p-Preview) -- drei Aenderungen:

1. **Drei Zeilen statt zwei**, Aufbau vom Nutzer vorgegeben:
   - Zeile 1: `Tag N - dd.mm.yyyy` ("Tage entsprechen den Reisetagen, Tag 0 ist vor der
     Abfahrt, Tag 1 der erste Reisetag, wenn ein Tag fehlt wird die Tagesnummer uebersprungen,
     es wird ein Datum des Tages in dd.mm.yyyy angezeigt")
   - Zeile 2: `Fahrt von X nach Y` statt `X › Y` ("das macht es nachvollziehbarer"), an
     Aktivitaetstagen stattdessen die Aktivitaet
   - Zeile 3: `Tagesstrecke: 300 km | Gesamtstrecke: 1234 km`
2. **Panelbreite pro Bauchbinde**, statt einer gemeinsamen festen Box ("wir haben immer sehr
   viel Platz in den blauen Boxen ... sieht ein bisschen verloren aus"). Dazu rendert das
   Skript jede Binde **zweimal**: erst mit unsichtbarem Panel, um die tatsaechliche
   Textbreite an der Alpha-Maske zu messen, dann mit Panel in genau dieser Breite. Die Breite
   aus den Fontmetriken zu schaetzen waere geraten -- cairosvg setzt den Text, also misst man
   auch am gesetzten Text.
3. Panel und Text liegen jetzt in EINEM PNG (vorher `stage-caption-box.png` + Text-PNG). Bei
   variabler Breite gehoeren sie ohnehin zusammen, und `timeline.json` kommt mit einem Overlay
   je Kapitel aus.

Position: unten LINKS (vorher unten rechts ueber dem Karten-Inset). Timing (`tl_in`, `dur`,
Fades) rechnet `rebuild-recipe.py` und schreibt es in `timeline.json`, nicht hier.

`python projects/norwegen-2026/exports/vlog-edit/stage-caption-recipe.py` von Repo-Root aus.
"""

import csv
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
import yaml
from PIL import Image

from frameforge.design import build_svg_from_tokens, overlay_tokens, render_svg_to_png

ROOT = Path("projects/norwegen-2026")
RES = (3840, 2160)

# Unten links, gleicher Sicherheitsabstand wie die Karte vorher rechts hatte (60px).
# Groesse aus der Typo abgeleitet (siehe `main`), nicht geraten: die erste Fassung war mit
# 210px Hoehe und caption-Groesse zu klein und zu gedraengt, um beim Zusehen ablesbar zu sein.
BOX_LEFT_PX = 60
BOX_BOTTOM_PX = RES[1] - 60
PAD_X_PX = 56
PAD_Y_PX = 44
# Untergrenze, damit die kuerzeste Binde ("Tag 0 - 17.07.2026 / Grevenbroich · gepackt") nicht
# als schmaler Streifen neben den breiten steht.
BOX_MIN_W_PX = 900

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
    # Runde 4: "Ruhetag ... finde ich ein bisschen schwierig", Nutzer-Vorschlag "Lazy Day".
    "2026-07-22": "Skien · Lazy Day vor dem Roadtrip",
    "2026-07-25": "Aurland · Fjord & Wikingerdorf",
    "2026-07-27": "Geiranger · Geburtstag & RIB-Safari",
    # Runde 4: "Da steht nur Bogen. Das ist aber Bogenschießen."
    "2026-07-30": "Uvdal · Angeln, Bogenschießen & Kanu",
    "2026-08-03": "Skien · Angeln an der Schärenküste",
}

# Zwischenstationen, die der Nutzer namentlich in der Bauchbinde sehen wollte.
VIA_LABEL = {
    "2026-07-28": "über Trollstigen",
    "2026-07-24": "über Stegastein",
}


def _de(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%d.%m.%Y")


def _km(value: float) -> str:
    return f"{value:,.0f} km".replace(",", ".")


def _text_right_edge_px(svg: str, tmp_png: Path) -> int:
    """Rechte Kante des tatsaechlich gesetzten Textes in Pixeln.

    Gemessen an der Alpha-Maske des gerenderten PNGs; das Panel ist in diesem Durchgang mit
    `panel_opacity=0` unsichtbar und traegt deshalb kein Alpha bei.
    """
    render_svg_to_png(svg, tmp_png)
    alpha = np.array(Image.open(tmp_png).convert("RGBA"))[:, :, 3]
    columns = np.nonzero(alpha.any(axis=0))[0]
    if columns.size == 0:
        raise ValueError("Bauchbinde ohne sichtbaren Text gerendert")
    return int(columns[-1])


def main() -> None:
    tokens = yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())
    out_dir = ROOT / "exports" / "vlog-edit" / "overlays"
    out_dir.mkdir(parents=True, exist_ok=True)

    base = overlay_tokens(tokens, width=RES[0], height=RES[1])
    # "Tag N - Datum" in Unterzeilen-Groesse, Etappe knapp darunter, Kilometer als leiseste
    # Zeile -- deutlich groesser als die erste Fassung, damit die Binde im Vorbeischauen
    # lesbar ist.
    day_size = base["subtitle_size"]
    route_size = base["caption_size"]
    # 0.78 war im 1080p-Testrender an der Grenze der Lesbarkeit; 0.86 haelt den
    # Groessenkontrast zur Etappenzeile und bleibt beim Vorbeischauen lesbar.
    km_size = round(route_size * 0.86, 1)
    line_gap = round(day_size * 0.30)
    km_gap = round(route_size * 0.45)
    box_h_px = round(PAD_Y_PX * 2 + day_size + line_gap + route_size + km_gap + km_size)
    box_top_px = BOX_BOTTOM_PX - box_h_px

    box_x_pct = BOX_LEFT_PX / RES[0] * 100
    box_y_pct = box_top_px / RES[1] * 100
    box_h_pct = box_h_px / RES[1] * 100
    text_x_pct = (BOX_LEFT_PX + PAD_X_PX) / RES[0] * 100
    # `dominant-baseline: middle` => y ist die Zeilenmitte, nicht die Grundlinie.
    day_y_pct = (box_top_px + PAD_Y_PX + day_size / 2) / RES[1] * 100
    route_y_pct = (box_top_px + PAD_Y_PX + day_size + line_gap + route_size / 2) / RES[1] * 100
    km_y_pct = (BOX_BOTTOM_PX - PAD_Y_PX - km_size / 2) / RES[1] * 100

    rows = {int(r["day"]): r for r in csv.DictReader(open(ROOT / "route" / "stages.csv"))}
    # Gesamtstrecke = alles, was bis einschliesslich diesem Reisetag gefahren wurde, inklusive
    # der Faehrstrecken (die stehen in `stages.csv` in `km` mit drin und sind dort als Seeweg
    # ausgewiesen).
    cumulative_km = {}
    running = 0.0
    for day in sorted(rows):
        running += float(rows[day]["km"])
        cumulative_km[day] = running

    tmp_png = out_dir / ".measure.png"
    for date_iso, stage_day in sorted(DAY_TO_STAGE.items()):
        row = rows[stage_day]
        # Tag 0 = Beladen am Vorabend, deshalb `day - 1`. Faellt ein Reisetag im Schnitt aus,
        # bleibt seine Nummer weg -- der Nutzer wollte das ausdruecklich so ("es ist ok, dass
        # wir hier Tage auslassen, wenn da nichts spannendes passiert ist"), das Datum in
        # derselben Zeile macht den Sprung erklaerbar.
        day_label = f"Tag {stage_day - 1} - {_de(date_iso)}"

        day_km = float(row["km"])
        if date_iso in ACTIVITY_LABEL:
            route_label = ACTIVITY_LABEL[date_iso]
        else:
            route_label = f"Fahrt von {row['from']} nach {row['to']}"
            if date_iso in VIA_LABEL:
                route_label += f" {VIA_LABEL[date_iso]}"

        total_label = f"Gesamtstrecke: {_km(cumulative_km[stage_day])}"
        # An Standtagen ist die "Tagesstrecke" nur die geschaetzte Einkaufs-/Ausflugsfahrt --
        # die zu betonen waere irrefuehrend, deshalb faellt sie unter 25 km weg.
        km_label = (
            f"Tagesstrecke: {_km(day_km)}  |  {total_label}" if day_km >= 25 else total_label
        )

        def svg_for(
            box_w_pct: float,
            panel_opacity: float,
            *,
            day_label: str = day_label,
            route_label: str = route_label,
            km_label: str = km_label,
        ) -> str:
            return build_svg_from_tokens(
                Path("templates/svg/stage-caption.svg"),
                overlay_tokens(
                    tokens, width=RES[0], height=RES[1],
                    # `build_svg_from_tokens` substituiert roh in den SVG-Text -- ein "&" im
                    # Label (z.B. "Fjord & Wikingerdorf") laesst cairosvgs strikten XML-Parser
                    # mit "not well-formed" abbrechen. Gleiche Klasse von Falle wie das "--" in
                    # SVG-Kommentaren aus Runde 2, deshalb hier explizit escapen.
                    day_label=escape(day_label), stage_day_size=day_size,
                    stage_day_x_pct=text_x_pct, stage_day_y_pct=day_y_pct,
                    stage_label=escape(route_label), stage_route_size=route_size,
                    stage_route_x_pct=text_x_pct, stage_route_y_pct=route_y_pct,
                    km_label=escape(km_label), stage_km_size=km_size,
                    stage_km_x_pct=text_x_pct, stage_km_y_pct=km_y_pct,
                    box_x_pct=box_x_pct, box_y_pct=box_y_pct,
                    box_w_pct=box_w_pct, box_h_pct=box_h_pct,
                    panel_opacity=panel_opacity,
                ),
            )

        # Pass 1: Panel unsichtbar, nur um die gesetzte Textbreite zu messen.
        right_px = _text_right_edge_px(svg_for(box_w_pct=1.0, panel_opacity=0), tmp_png)
        box_w_px = max(BOX_MIN_W_PX, right_px - BOX_LEFT_PX + PAD_X_PX)
        # Pass 2: dasselbe Layout mit Panel in gemessener Breite.
        svg = svg_for(box_w_pct=box_w_px / RES[0] * 100, panel_opacity=base["panel_opacity"])
        render_svg_to_png(svg, out_dir / f"stage-caption-{date_iso}.png")
        print(f"{date_iso}  [{box_w_px:>4} px]  {day_label} · {route_label} · {km_label}")

    tmp_png.unlink(missing_ok=True)
    # Die gemeinsame Box ist entfallen -- jede Bauchbinde bringt ihr Panel jetzt selbst mit.
    (out_dir / "stage-caption-box.png").unlink(missing_ok=True)
    print(f"{len(DAY_TO_STAGE)} Bauchbinden-PNGs geschrieben nach {out_dir}")


if __name__ == "__main__":
    main()
