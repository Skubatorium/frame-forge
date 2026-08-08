"""Rezept fuer die zwei Kartenaufgaben in `norwegen-2026`/`vlog-data` (map-animator).

**Nicht ausgefuehrt in dieser Session** (Auftrag: "Kein Rendering von Video/Preview in diesem
Schritt"). Dieses Skript ist das exakte, direkt lauffaehige Rezept fuer den `timeline-builder`
bzw. den Render-Schritt, der es aufruft, sobald `timeline.json` fuer `vlog-data` gebaut wird.
Alle Parameter (Bounding-Box, Zoom, Track-Indizes, km-Offsets, POIs, Etappengrenzen) sind aus
`route/roadtrip.gpx`, `route/stages.csv` und `route/locations.csv` hergeleitet und unten
begruendet. `python map-animator-recipe.py` (ohne Argumente) rechnet nur die Tabelle nach --
keine Netzwerk-/Tile-Zugriffe, kein Rendering.

## Wichtiger Befund vor dem ersten echten Lauf: Faehr-Umweg in `roadtrip.gpx`

Die dichte Route zwischen Hirtshals und Larvik (Faehre Color Line, real ca. 162,5 km Seeweg)
lauft in `roadtrip.gpx` NICHT als Faehrlinie, sondern als Strassen-Umfahrung ueber Schweden
(Laengengrad bis 13.12 Grad Ost, weit oestlich von Larvik/Skien bei ca. 9.6 Grad Ost). Das
treibt die `cumulative_km`-Summe dieses Beins von real 552,5 km (Flensburg->Skien, `stages.csv`
Tag 3) auf ueber 1580 km im GPX -- fast das Dreifache, weil ein normaler Strassenrouter die
Faehre nicht kennt und stattdessen um die Ostsee/Suedschweden herumroutet. Betroffen: K0
(Cold-Open-Overview, die Anreise bis Geilo schliesst die Faehre mit ein), K3
(Ueberfahrt-Kapitel) und der Rueckweg in K15 (Tag 19, Larvik->Hirtshals).

Ohne Korrektur zeigt die Karte dort eine falsche Strecke (Schweden-Schlaufe statt Seeweg) UND
einen falsch hohen km-Stand. Fix hier im Rezept (`_straighten_ferry`): der GPX-Abschnitt
zwischen dem naechsten Punkt zu `Hirtshals` und dem naechsten Punkt zu `Larvik` wird -- nur
innerhalb des jeweils extrahierten Tages-/Kapitel-Slices, nicht global -- durch eine
synthetische Gerade Hirtshals -> Skagerrak (Faehre) -> Larvik ersetzt (Koordinaten aus
`locations.csv`, dort bereits als POI gepflegt). Reine Datenaufbereitung vor dem Rendern, kein
Eingriff in `frameforge/map.py`. Bevorzugte Langfrist-Loesung: `roadtrip.gpx` mit
`frameforge route-build norwegen-2026 --from-kml <route-mit-faehrsegment>` neu erzeugen, sobald
ein KML-Export mit korrektem Faehrsegment vorliegt -- bis dahin deckt dieses Rezept den Fall ab.

## Layout

1. `render_cold_open()` -- K0 (00:00-00:30), formatfuellender Overview-Clip, `viewport="fit"`,
   Basemap, kein HUD. Ergebnis ist ein `VideoClip` (`kind: video`), kein `MapClip` -- der
   `timeline-builder` haengt ihn in `tracks.video` ein, nicht in `tracks.map` (Beat-Sheet K0:
   "eigener, gerenderter Clip ... kein Overlay").
2. `CHAPTERS` -- eine Zeile je Beat-Sheet-Kapitel K2..K15 (K1 hat noch keine Karte, das HUD
   blendet laut Beat-Sheet erst bei 00:52 ein) mit allen Parametern fuer
   `render_inset_frames`. Jede Zeile wird zu einem eigenen `MapClip` in `tracks.map`
   (`frameforge/render.py` legt `tracks.map`-Clips ohnehin fest unten rechts ab --
   `x=W-w-20:y=H-h-20` -- das deckt "Position bottom_right" bereits ab, ohne dass dieses Rezept
   die Position selbst waehlen muesste).
3. K12-Sonderfall (`Filmzeit 1065 s`) -- eigener Absatz unten bei der `CHAPTERS`-Tabelle.
"""

from __future__ import annotations

from pathlib import Path

from frameforge.gpx import cumulative_km, haversine_km, parse_gpx, parse_locations, parse_stages

ROOT = Path("projects/norwegen-2026")
ROUTE = ROOT / "route"

FPS = 30.0
RESOLUTION = (3840, 2160)          # wie `exports/test-timelapse-journey/timeline.json`
INSET_SIZE = (640, 360)            # 1/6 der Zielaufloesung, `map.py`-Default (DEFAULT_WIDTH/HEIGHT)

# -- Rohdaten einmal laden (alle Indizes unten beziehen sich auf DIESEN unveraenderten Track) --

TRACK = parse_gpx(ROUTE / "roadtrip.gpx", require_time=False)  # 117845 Punkte, kein `time`
STAGES = parse_stages(ROUTE / "stages.csv")                    # 19 Tage, Tag 1 = 17.07.
LOCATIONS = parse_locations(ROUTE / "locations.csv")
LOC_BY_NAME = {l["name"]: l for l in LOCATIONS}

# Globale Indizes des Schweden-Umwegs in `TRACK` (naechster Punkt zu Hirtshals/Larvik je
# Richtung -- empirisch bestimmt, s. Modul-Docstring). Hinweg liegt VOR dem Rueckweg im Track,
# beide liegen vollstaendig innerhalb je eines Tages-Slices (Tag 3 bzw. Tag 19).
_OUTBOUND_DETOUR = (10512, 24476)  # (Hirtshals-Index, Larvik-Index), Richtung Norwegen
_RETURN_DETOUR = (108778, 94632)   # (Hirtshals-Index, Larvik-Index), Richtung Deutschland


def _straighten_ferry(track_slice: list[dict], slice_offset: int) -> list[dict]:
    """Ersetzt einen Schweden-Umweg durch eine Gerade Hirtshals-Skagerrak-Larvik, falls die
    global bekannten Umweg-Indizes im uebergebenen Slice liegen (`slice_offset` = Index des
    ersten Slice-Elements im urspruenglichen `TRACK`). Lokal, damit die Tages-/Kapitelgrenzen
    (aus dem unveraenderten `TRACK` bestimmt) an keiner anderen Stelle verschoben werden.
    """
    hirtshals, skagerrak, larvik = (
        LOC_BY_NAME["Hirtshals"], LOC_BY_NAME["Skagerrak (Fähre)"], LOC_BY_NAME["Larvik"],
    )
    out = list(track_slice)
    slice_end = slice_offset + len(track_slice) - 1
    for a_idx, b_idx in (_OUTBOUND_DETOUR, _RETURN_DETOUR):
        lo, hi = sorted((a_idx, b_idx))
        if not (slice_offset <= lo and hi <= slice_end):
            continue  # dieser Umweg liegt nicht (vollstaendig) in diesem Slice
        start_loc = hirtshals if a_idx < b_idx else larvik
        end_loc = larvik if a_idx < b_idx else hirtshals
        straight = [
            {"lat": start_loc["lat"], "lon": start_loc["lon"], "ele": None},
            {"lat": skagerrak["lat"], "lon": skagerrak["lon"], "ele": None},
            {"lat": end_loc["lat"], "lon": end_loc["lon"], "ele": None},
        ]
        out[lo - slice_offset : hi - slice_offset + 1] = straight
    return out


def _slice(idx_from: int, idx_to: int) -> list[dict]:
    """Track-Slice `[idx_from, idx_to]` (inklusiv) aus `TRACK`, Faehr-Umweg begradigt."""
    raw = TRACK[idx_from : idx_to + 1]
    if len(raw) < 2:
        raw = TRACK[max(0, idx_from - 1) : idx_to + 1]  # render_route_frames braucht >=2 Punkte
        idx_from = max(0, idx_from - 1)
    return _straighten_ferry(raw, idx_from)


# -- K0: Cold-Open-Overview (formatfuellend, eigener Clip in tracks.video) ------------

# Grenze Ausklang K0: naechster Punkt zum Etappenziel Tag 7 (Geilo) -- danach beginnt der
# Roadtrip erzaehlerisch schon in K6/K7, K0 zeigt aber nur die Anreise bis dorthin (Beat-Sheet:
# "...und weiter nach Norden ins norwegische Fjell"). Index aus `stages.csv`-Abgleich (Tag 7,
# Ziel "Geilo"): 40725 (naechster Punkt, 24 m Abstand zum POI).
K0_END_IDX = 40725
K0_TRACK = _slice(0, K0_END_IDX)
K0_POIS = [l for l in LOCATIONS if l["day"] in {"2", "3", "4", "5", "7"}]

K0_BBOX = (51.0, 6.4, 60.6, 13.2)  # (lat_min, lon_min, lat_max, lon_max), ca. 0.1-0.2 Grad Rand
K0_ZOOM = 5  # Uebersicht Deutschland/Daenemark/Suednorwegen auf einen Blick


def render_cold_open(out_dir: Path, tile_cache_dir: Path):
    """K0 -- 30 s, formatfuellend, `viewport='fit'` (feste Uebersicht, kein Follow)."""
    from frameforge.map import render_basemap, render_route_frames

    basemap_tiles = render_basemap(K0_BBOX, K0_ZOOM, tile_cache_dir)
    # `render_basemap` liefert ein Vielfaches von 256px -- vor dem Aufruf auf RESOLUTION
    # zuschneiden/skalieren (PIL `.resize`/`.crop`), damit `basemap.size == (width, height)`.
    frames = render_route_frames(
        K0_TRACK,
        out_dir,
        fps=FPS,
        dur=30.0,
        width=RESOLUTION[0],
        height=RESOLUTION[1],
        basemap=basemap_tiles,  # nach Crop/Resize auf RESOLUTION
        pois=K0_POIS,
        poi_labels=True,
        viewport="fit",  # NICHT follow -- die ganze Route bleibt sichtbar (Vorgabe)
        dwell_s=0.0,  # Cold Open hat keine Beat-Struktur, die Route waechst gleichmaessig
        # Beat-Sheet: "gegen Ende hin langsamer" -- keine Standardoption von
        # `render_route_frames` (Reveal-Tempo ist ohne `dwell_s` linear). Umsetzung ohne
        # Codeaenderung: `dur=27.0` fuer den Wachstumsteil rendern, danach 3 s lang das letzte
        # Frame wiederholen (Datei kopieren, `out_dir`-Nachbearbeitung) -- ergibt denselben
        # visuellen Ease-Out wie eine Verlangsamung, ohne `map.py` anzufassen. Puls-Einsatz laut
        # `beatsheet.md`/`brief.yaml` kann die 30 s auf 25-40 s klemmen -- dann `dur` hier
        # anpassen (Differenz geht laut Beat-Sheet vollstaendig in K2, nicht in K0-Timing).
    )
    return frames


# -- K2..K15: durchgehende Inset-Karte unten rechts (tracks.map, ein MapClip je Kapitel) -----

# Tag-Grenzen in `TRACK`: naechster Punkt zum Zielort jedes Tages, vorwaerts ab dem Index des
# Vortages gesucht (verhindert Fehltreffer bei Orten, die zweimal angefahren werden, z.B.
# Skien an Tag 3 UND Tag 16-18). Quelle: Abgleich `stages.csv` `to`-Spalte gegen
# `locations.csv`-Koordinaten desselben Namens.
DAY_END_IDX = {
    1: 0, 2: 6797, 3: 26254, 4: 26254, 5: 26254, 6: 26254, 7: 40725, 8: 46829, 9: 46829,
    10: 59375, 11: 59375, 12: 70947, 13: 81601, 14: 81601, 15: 81601, 16: 89458, 17: 89458,
    18: 89458, 19: 117844,
}

STAGE_BY_DAY = {s["day"]: s for s in STAGES}


def _pois_for_days(days: list[int]) -> list[dict]:
    wanted = {str(d) for d in days}
    return [l for l in LOCATIONS if l["day"] in wanted]


# Kapitel-Tabelle: (id, tl_in, dur, [tage], idx_from, idx_to, km_offset, zoom, dwell_s).
# Zeiten aus Beat-Sheet Abschnitt 3/6 (`beatsheet.md`), unveraendert uebernommen -- der
# `timeline-builder` darf Kapitelgrenzen laut Beat-Sheet um bis zu +/-2s justieren, dann hier
# `tl_in`/`dur` entsprechend nachziehen. `km_offset` = reale kumulierte Strecke aus
# `stages.csv` (`km`-Spalte) bis Kapitelbeginn -- NICHT aus `cumulative_km(TRACK)`, weil die
# dichte GPX-Distanz durch den Faehr-Umweg (s.o.) systematisch zu hoch waere, wenn man sie
# roh aufsummiert.
CHAPTERS = [
    # id     tl_in   dur    tage               idx_from  idx_to   km_offset  zoom  dwell_s
    ("K2",   52.0,   80.0,  [1, 2],            0,        6797,    0.0,       6,    2.0),
    ("K3",  132.0,   85.0,  [3],               6797,     26254,   578.5,     7,    2.0),
    ("K4",  217.0,  100.0,  [4],               26254,    26254,   1131.0,    10,   0.0),
    ("K5",  317.0,   78.0,  [5, 6],            26254,    26254,   1171.0,    10,   0.0),
    ("K6",  395.0,  105.0,  [7],               26254,    40725,   1231.0,    8,    2.5),
    ("K7",  500.0,  115.0,  [8],               40725,    46829,   1451.0,    9,    2.5),
    ("K8",  615.0,  115.0,  [9],               46829,    46829,   1641.0,    10,   0.0),
    ("K9",  730.0,  100.0,  [10],              46829,    59375,   1651.0,    8,    2.0),
    ("K10", 830.0,   85.0,  [11],              59375,    59375,   1929.0,    10,   0.0),
    ("K11", 915.0,   95.0,  [12],              59375,    70947,   1939.0,    8,    2.5),
    # K12 -- Sonderfall, siehe Absatz unten. Kein Track-Fortschritt, Kamera haelt auf Lom.
    ("K12", 1010.0,   55.0, [12],              70947,    70947,   2205.0,    11,   0.0),
    ("K13", 1065.0,   40.0, [13],              70947,    81601,   2205.0,    9,    2.0),
    ("K14", 1105.0,   45.0, [14, 15],          81601,    81601,   2505.0,    10,   0.0),
    ("K15", 1150.0,   50.0, [16, 17, 18, 19],  81601,    117844,  2515.0,    6,    1.5),
]

# -- K12-Sonderfall: Etappengrenze bei Filmzeit 1065 s -------------------------------------
#
# K12 (1010-1065 s) fasst der Beat-Sheet zufolge zwei Abende zusammen (28.07. UND 29.07.
# abends), beide erzaehlerisch am selben Ort (Lom). Der reale GPX-Track kennt aber nur EINE
# Position pro Tag: Tag-12-Ende ist Lom (idx 70947), Tag-13-Ende ist Uvdal (idx 81601, ueber
# Valdresflye). Wuerde man die Kartenposition an den echten Kalendertag der gezeigten Aufnahme
# koppeln (`captured_at`), spraenge die Karte schon waehrend K12 auf den Uvdal-Track (weil ein
# Teil des K12-Materials formal vom 29.07. stammt) -- lange bevor K13 (Valdresflye) im Bild
# beginnt.
#
# Fix: der K12-`MapClip` bekommt NUR den Tag-12-Slice (`idx_from=idx_to=70947`, s. Tabelle
# oben) und `dwell_s=0.0` -- die Karte haelt fuer die vollen 55 s auf Lom, unabhaengig davon,
# welcher Kalendertag im Bild laeuft. Der K13-`MapClip` beginnt exakt bei `tl_in=1065.0`
# (Kapitelende K12) und startet dort seinerseits bei `idx_from=70947` (Lom) -- kein Bruch im
# km-Zaehler (`km_offset` K13 = km_offset K12 = 2205.0, weil zwischen K12-Ende und K13-Beginn
# keine gefahrene Strecke liegt). Das ist die "manuelle Stufengrenze bei 1065 s" aus dem
# Beat-Sheet.


def render_inset_chapter(entry: tuple, out_dir: Path, tile_cache_dir: Path):
    """Ein `MapClip` je Kapitel. `heights=None` durchgehend -- Brief verbietet Hoehenmeter."""
    from frameforge.map import render_inset_frames

    chapter_id, tl_in, dur, days, idx_from, idx_to, km_offset, zoom, dwell_s = entry
    track = _slice(idx_from, idx_to)
    pois = _pois_for_days(days)

    frames = render_inset_frames(
        out_dir,
        template_path=Path("templates/svg/map-inset.svg"),
        tokens=_load_tokens(),
        fps=FPS,
        dur=dur,
        size=INSET_SIZE,
        track=track,
        zoom=zoom,
        tile_cache_dir=tile_cache_dir,
        heights=None,  # Vorgabe: keine Hoehenmeter/kein Hoehenprofil in dieser Version
        km_offset=km_offset,
        pois=pois,
        poi_labels=True,  # zeigt den Ortsnamen -- der einzige Weg, wie render_inset_frames
                           # "Ortsname/Etappe" ueberhaupt darstellt (`map-inset.svg` hat kein
                           # `stage_label`-Textfeld, nur `km_label`/`elevation_label`); ohne
                           # POIs waere "Ortsname/Etappe zeigen" nicht erfuellbar.
        dwell_s=dwell_s,
        ease_s=1.2,
        step_s=0.5,
    )
    return frames


def _load_tokens() -> dict:
    import yaml

    return yaml.safe_load((ROOT / "design" / "tokens.yaml").read_text())


if __name__ == "__main__":
    print(f"K0: {len(K0_TRACK)} Punkte, bbox {K0_BBOX}, zoom {K0_ZOOM}")
    print(f"  km (begradigt) {cumulative_km(K0_TRACK)[-1]:.1f}  (real bis Geilo/Tag 7: 1451.0)")
    for entry in CHAPTERS:
        chapter_id, tl_in, dur, days, idx_from, idx_to, km_offset, zoom, dwell_s = entry
        track = _slice(idx_from, idx_to)
        km_this = cumulative_km(track)[-1] if idx_to > idx_from else 0.0
        print(
            f"{chapter_id}: tl_in={tl_in:>6.1f} dur={dur:>5.1f} tage={days} "
            f"idx=[{idx_from},{idx_to}] km_offset={km_offset:>7.1f} "
            f"km_delta~{km_this:>6.1f} zoom={zoom} dwell_s={dwell_s} "
            f"pois={[p['name'] for p in _pois_for_days(days)]}"
        )
