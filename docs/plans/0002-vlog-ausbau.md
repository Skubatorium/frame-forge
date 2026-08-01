# FrameForge — Ausbauplan „Roadtrip-Vlog" (0002) — ÜBERHOLT

> **Nicht umsetzen.** Dieser Entwurf wurde am selben Tag durch
> [`0003-vlog-ausbau.md`](0003-vlog-ausbau.md) ersetzt (Rückwärtskompatibilität als Grundregel,
> Backfill statt Neu-Indizierung, GPS aus den ungeschnittenen Originalen, Ortsvergabe für
> unklare Zwischenstopps, Route-Agent mit Plausibilitätsprüfung, Höhenprofil, generierte
> Grafiken, Farbangleichung zwischen Clips). Bleibt nur zur Historie liegen.

Erstellt am 2026-08-01, nach dem ersten echten Durchlauf (`norwegen-2026`, Export
`test-timelapse-journey`, ~4 min Teaser).

## Context

Der erste echte Export hat den Kernprozess bestätigt: Ingest, Media-Index, Story→Timeline,
Render und NLE-Export funktionieren am echten Material (255 Assets, 236 Videos / 19 Fotos).
Auswahl und Schnittrhythmus waren laut Nutzer gut.

Das nächste Ziel ist ein **anderes Produkt aus demselben Fundus**: ein ~15-minütiger,
chronologisch erzählter Roadtrip-Vlog („Videotagebuch") — Start zu Hause, über Flensburg nach
Norwegen, Tag für Tag, mit Etappen, Unterkünften und Aktivitäten. Dafür bleibt es beim Projekt
`norwegen-2026`; es entsteht nur ein **neuer Export**. Der Fundus wird vorher erweitert
(Fotoauswahl, Handy-4K60-Clips, Material der Partnerin).

Dieser Plan sammelt die dafür nötigen **Erweiterungen der Werkzeugschicht**. Reine
Regie-/Briefing-Entscheidungen (Tempo, Musikstil, Clip-Auswahl) stehen hier bewusst **nicht** —
die gehören in den Brief des neuen Exports, nicht in den Code.

### Leitprinzip (unverändert aus Plan 0001, §M3)

Der Code liefert **generische Fähigkeiten**, keine projektspezifische Gestaltung. „Wie es
aussieht" (Farben, Icons, Kartenstil, konkrete Marker, konkrete Orte) ist Sache des jeweiligen
Projekts/Designsystems. Kein Norwegen-spezifisches Styling und keine hart codierten Ortsnamen
in `frameforge/`.

---

## Befund aus dem Realbetrieb (belegt, nicht vermutet)

Auswertung von `projects/norwegen-2026/index/assets.json` (255 Einträge):

| Beobachtung | Zahl | Konsequenz |
|---|---|---|
| Assets mit `captured_at` | 19 von 255 | **nur die Fotos.** Kein einziges Video hat eine Aufnahmezeit |
| Videos mit `gps.lat/lon` | 0 von 236 | keine Geodaten aus dem Videomaterial |
| Assets mit `gps.place` | 242 | Ort stammt **aus dem Ordnernamen**, nicht aus Zeit/Position |
| `source` = `drone` | 251 von 255 | plausibel für den Fundus, aber ungeprüft (siehe H2) |

Daraus folgt direkt der vom Nutzer bemerkte Fehler: Ordner wie
`2026-07-28_Norwegen_Geiranger-Lom_1_Trollstigen` liefern Ortswerte wie
`"Geiranger-Lom/Trollstigen"` oder `"Geiranger-Lom"` — ein Ordnername ist eben eine *Etappe*,
kein *Ort*. Clips vom Trollstigen landen dadurch unter „Geiranger". Für einen Teaser egal,
für ein chronologisches Videotagebuch nicht.

**Gute Nachricht:** die Rohdaten sind da, sie werden nur nicht ausgelesen. Die Ordner sind
sauber nach `YYYY-MM-DD_Ort_Thema` benannt, und die Dateinamen tragen die volle Aufnahmezeit
(`DJI_20260720153625_0006_D-…`), teils sogar den Trim-Offset des Vorschnitts.

---

## Arbeitspaket A — Chronologie und Ortszuordnung ehrlich machen

**Ziel:** Jedes Asset kennt seine echte Aufnahmezeit und seine Etappe. Die Zuordnung entsteht
aus Daten (Zeit + Etappenliste + optional GPX), nicht aus einer Ordnernamen-Vermutung.

### A1 — Aufnahmezeit für Videos

`frameforge/probe.py`:

- `probe_video` liest zusätzlich `format.tags.creation_time` bzw.
  `com.apple.quicktime.creationdate` aus dem ffprobe-Ergebnis (beides ist bereits im
  abgefragten JSON enthalten, es wird derzeit nur nicht ausgewertet) und liefert
  `captured_at` im selben ISO-Format wie `probe_photo_exif`.
- Neuer Helfer `captured_at_from_name(path)` für Kamera-Namensmuster mit vollem Zeitstempel:
  `DJI_20260720153625…`, `IMG_20260720_153625…`, `VID_20260720_153625…`,
  `PXL_20260720_153625…`. Reiner Fallback, wenn der Container keine Zeit trägt (re-encodete
  Vorschnitte verlieren sie oft).
- Priorität: Container-Zeit → Dateinamen-Zeit → (bestehend) Datum aus Pfad → `mtime`.

`frameforge/preindex.py`: der Video-Zweig von `_prepare_one` schreibt `captured_at` ins
Prep-Dict (der Foto-Zweig tut das bereits).

**Abnahme:** Für den bestehenden Fundus liefert ein Trockenlauf für ≥ 90 % der 236 Videos eine
Aufnahmezeit; die Werte sind innerhalb eines Ordners monoton (Stichprobe von 3 Ordnern).

### A2 — Etappen als eingebbare Projektdaten

Neue Datei `projects/<name>/route/stages.csv` — das ist der Ort, an dem der Nutzer seine
Streckenliste hinterlegt:

```csv
day,date,from,to,via,km,overnight,note
1,2026-07-19,Zuhause,Flensburg,,320,Flensburg,Anreise
2,2026-07-20,Flensburg,Skien,Fähre,410,Hütte am See,
9,2026-07-28,Geiranger,Lom,Trollstigen,190,Lom,Passstraße
```

`frameforge/gpx.py`:

- `parse_stages(path) -> list[dict]` (analog zum vorhandenen `parse_locations`): validiert
  Pflichtspalten `day,date,from,to`, parst `km` und `date`, klare Fehlermeldung mit Zeilennummer.
- `stage_for(timestamp, stages) -> dict | None`: Etappe eines Zeitpunkts über das Datum.

`locations.csv` (existiert bereits, Spalten `name,lat,lon,type,day`) bleibt zuständig für
Punkte auf der Karte — Übernachtungen, POIs, Zwischenziele wie Trollstigen.

### A3 — Zuordnung als eigener, prüfbarer Schritt

Neues CLI-Kommando `frameforge assign-places <projekt> [--dry-run] [--force]`:

1. Liest `assets.json`, `route/stages.csv`, `route/locations.csv` und — falls vorhanden —
   `route/roadtrip.gpx`.
2. Bestimmt je Asset über `captured_at`: `day`, `stage` (`from`→`to`), und den Ort. Ort-Logik in
   dieser Reihenfolge: echte GPS-Position (Foto/GPX über `nearest_location`) → nächstgelegener
   POI aus `locations.csv` → `overnight`-Ort der Etappe → `unknown`.
3. Schreibt `asset["day"]`, `asset["stage"]`, `asset["gps"]["place"]` zurück (Merge, kein
   Neu-Indizieren, keine Vision-Kosten).
4. Meldet als Report: Assets je Tag/Etappe, Assets ohne Zeit, Assets ohne Ort, sowie
   **Konflikte** — Fälle, in denen der bisherige (aus dem Ordnernamen geratene) Ort dem neu
   berechneten widerspricht. Ohne `--force` werden manuell gesetzte Orte nicht überschrieben.

Neues Schema-Feld: `day` (int) und `stage` (str) je Asset, ergänzend zu `gps.place`. In
Plan 0001 §4 nachtragen.

### A4 — Geführte Eingabe (`/ff-route`)

Neuer Slash-Command `.claude/commands/ff-route.md`: fragt die Etappen konversationell ab
(Tag, Datum, von, nach, über, km, Übernachtung), schreibt `stages.csv` und `locations.csv`,
ruft danach `assign-places --dry-run` und zeigt den Report, bevor real geschrieben wird.
Nimmt als Eingabe auch eine vom Nutzer gelieferte Liste oder Google-Maps-Punkte entgegen.

Der Command läuft **vor** `/ff-brief` und ist optional — Projekte ohne Route funktionieren
weiter wie bisher.

**Abnahme A gesamt:** Nach `/ff-route` + `assign-places` sind die Clips aus
`…Geiranger-Lom_1_Trollstigen` der Etappe *Tag 9, Geiranger→Lom über Trollstigen* zugeordnet
und tragen als Ort *Trollstigen*, nicht *Geiranger*. `frameforge days` zeigt echte Reisetage
statt „unknown".

---

## Arbeitspaket B — Karte: mitfahrender Ausschnitt, Kilometerzähler, Etappen-HUD

**Ziel:** Eine kleine Karte (z. B. unten rechts), auf der ein Marker die Route abfährt, die
Linie hinter sich nachzieht, der **Ausschnitt mitwandert** statt die ganze Tour zu zeigen, und
unter der Karte Tag, Etappenziel und Kilometerstand mitlaufen.

**Stand heute** (`frameforge/map.py`): Die Projektion (`_make_projector`) bildet auf die
Bounding-Box des **gesamten** Tracks ab — der Ausschnitt ist also fix, nur der Marker bewegt
sich. Es gibt keine Distanzberechnung, kein HUD, und `render_basemap` liefert nur ganze
Kachel-Raster (Vielfaches von 256 px), die exakt zur Zielgröße passen müssen.

### B1 — Distanzen

`frameforge/gpx.py`: `haversine_km(a, b)` und `cumulative_km(track) -> list[float]`
(kumulierte Strecke je Trackpunkt). Basis für den Kilometerzähler und für „wie weit ist es
noch bis zum Ziel".

### B2 — Mitwandernder Viewport

`frameforge/map.py`:

- Umstellung der Projektion von Equirectangular auf **Web-Mercator** (`latlon_to_pixel(lat,
  lon, zoom)`), damit Route und OSM-Kacheln im selben Koordinatensystem liegen — Voraussetzung
  dafür, dass eine Basemap unter der Route überhaupt pixelgenau stimmt.
- `render_route_frames(..., viewport="follow", zoom=…, ease_s=…)`: der Bildausschnitt zentriert
  sich auf die aktuelle Position, geglättet (gleitender Mittelwert über `ease_s`), damit die
  Karte nicht zittert. `viewport="fit"` bleibt das heutige Verhalten (Default, rückwärts­
  kompatibel).
- `basemap_viewport(center_latlon, zoom, size, cache_dir, fetcher=None)`: schneidet aus dem
  Kachel-Cache genau den benötigten Ausschnitt in beliebiger Pixelgröße — ersetzt für den
  Follow-Modus die heutige „nur ganze Kachelraster"-Beschränkung.
- Halt an Orten: erreicht der Marker einen POI aus `locations.csv`, pausiert der Reveal für
  eine konfigurierbare Haltezeit (`dwell_s`), damit der Ortsname lesbar ist.

### B3 — Etappen-HUD

Neues SVG-Template `templates/svg/map-hud.svg` (token-parametrisiert wie alle anderen):
Tag, Etappe (`von → nach`, optional `über`), Kilometerstand, optional Uhrzeit.

Gerendert wird **nicht** pro Frame (zu teuer), sondern in Stufen: ein PNG je angefangenem
Kilometer bzw. je Sekunde, als eigene Overlay-Sequenz. Die Karte selbst bleibt eine
Alpha-Ebene (`tracks.map`), das HUD wird als `tracks.overlay` darübergelegt — beide Mechanismen
existieren bereits im Renderer.

### B4 — Integration

`.claude/agents/map-animator.md` um den Follow-Modus, `stages.csv` und das HUD erweitern.

**Abnahme B:** Für Tag 9 (Geiranger→Lom über Trollstigen) entsteht ein Karten-Clip, in dem
der Ausschnitt der Route folgt, die Linie wächst, POIs beschriftet auftauchen, der
Kilometerzähler von 0 auf den Etappenwert läuft und Tag/Ziel im HUD stehen. Ohne
`viewport="follow"` ist die Ausgabe bit-identisch zum heutigen Verhalten (Regressionstest).

---

## Arbeitspaket C — Schwarzblende zwischen zwei Clips

**Stand heute** (`frameforge/render.py`): `_CROSSFADE_TYPES = {fade, dissolve, slow_dissolve,
crossfade}` erzeugt `xfade`; eine Blende **nach/aus Schwarz** gibt es nur ganz außen (erster
und letzter Clip der Timeline). Zwischen zwei beliebigen Clips ist sie nicht möglich.

**Umsetzung:** Neuer Übergangstyp `black` (optional `black_hold`), verarbeitet in
`_join_video_segments` als dritte Variante neben `concat` und `xfade`:
Ausblenden des vorherigen Clips (`fade=t=out`), optionale Haltezeit auf Schwarz, Einblenden des
nächsten (`fade=t=in`). Anders als `xfade` **verlängert** das die Timeline um die Haltezeit —
die Timing-Invariante aus dem Crossfade-Fix gilt hier entsprechend umgekehrt und muss in
`timeline.json` sauber abgebildet sein (`tl_in` der Folgeclips), damit Audio und Overlays nicht
verrutschen. `qc.validate` bekommt eine Regel dafür.

**Abnahme C:** Timeline mit `transition_in: {type: black, dur: 1.0}` in der Mitte rendert eine
sichtbare Schwarzblende; Gesamtdauer stimmt mit `timeline.duration` überein; bestehende
concat-/xfade-Timelines rendern unverändert.

---

## Arbeitspaket D — Grafik-Aufwertung (Bauchbinde, Karten, Badges)

**Stand heute** (`templates/svg/lower-third.svg`): ein Rechteck mit Deckkraft plus zwei
Textzeilen. Mehr nicht — exakt das, was der Nutzer als „transparenter Kasten, Text, fertig"
beschrieben hat.

**Umsetzung** (alles weiterhin rein token-parametrisiert, kein projektspezifisches Styling):

- `lower-third.svg`: Akzentbalken, abgerundete Ecken, Farbverlauf statt Vollton, weicher
  Schlagschatten, optionale Icon-/Logo-Fläche, klar getrennte Typo-Hierarchie, größere
  Default-Maße.
- Neue Templates: `stage-card.svg` (Tages-/Etappenkarte: Datum, Tag N, von→nach),
  `map-hud.svg` (siehe B3), `stat-badge.svg` (km, Höhenmeter, Dauer).
- **Relative Größen:** Tokens für Schrift- und Balkengrößen als Faktor der Zielhöhe statt
  absoluter Pixel, damit dieselben Tokens in 1080p-Preview und 4K-Final gleich wirken.
- Ein-/Ausblenden nutzt das bereits vorhandene `anim.fade_in_s`/`fade_out_s` am `OverlayClip`.

**Abnahme D:** Alle Templates rendern gegen ein gemeinsames Token-Set fehlerfrei zu PNG
(bestehender Testaufbau), in 1080p und 2160p optisch konsistent; visuelle Abnahme durch den
Nutzer an einem Beispiel-Frame.

---

## Arbeitspaket E — `relink`: Pfade nach Umsortieren reparieren

**Warum:** Der Nutzer will die Ordnerstruktur unter `media_root` aufräumen. Der Analyse-Cache
hängt am Datei-Hash und überlebt das Verschieben (keine erneute Vision-Analyse) — der in
`assets.json` gespeicherte **Pfad** wird dabei aber nicht nachgezogen. Der Fehler fiele erst
beim Final-Render auf, weil `render_final` die Originale über genau diesen Pfad auflöst.

**Umsetzung:** `frameforge relink <projekt> [--dry-run]` — scannt `media_root`, matcht per
Hash gegen `assets.json`, aktualisiert geänderte `path`-Werte, meldet verwaiste Einträge
(Datei nicht mehr auffindbar) und neue, noch nicht indizierte Dateien.

**Abnahme E:** Datei verschieben → `relink` → Pfad korrigiert, `assets.json` sonst unverändert,
keine erneute Analyse, Final-Render findet das Original.

---

## Arbeitspaket F — Musik: mehrere Titel, Übergänge, Stille

**Stand heute** (`frameforge/audio.py`): BPM/Beat-Grid/Energiekurve je Track (gecacht),
`duck_curve` für Musik unter O-Ton. Mehrere Musik-Clips **können** in `tracks.audio` liegen und
werden gemischt — es gibt aber keine Ein-/Ausblendung pro Clip und keine Logik für
Kapitelwechsel.

**Umsetzung:**

- `timeline.AudioClip` um `fade_in_s` / `fade_out_s` erweitern; `render.build_filtergraph`
  setzt entsprechende `afade`-Filter (heute gibt es nur konstanten `gain_db` und die
  Ducking-Kette).
- `audio.segment_plan(tracks, sections, *, gap_s=0.0)`: verteilt n Titel auf n Kapitel,
  legt Übergänge auf den nächstgelegenen Beat des ausklingenden Titels und erzeugt
  Ein-/Ausblendwerte; `gap_s > 0` ergibt eine echte Stille zwischen zwei Titeln.

Bewusst **keine** automatische Stilanalyse („passen diese Titel zusammen") — welcher Titel zu
welchem Kapitel gehört, entscheidet der Nutzer bzw. der `audio-designer` im Brief.

**Abnahme F:** Timeline mit drei Titeln über drei Kapitel rendert hörbar sauber: Überblendung
auf dem Beat, definierte Stille am gewünschten Schnitt, kein Pegelsprung.

---

## Arbeitspaket G — Invalidierung bei neuem Material

Übernimmt die am 2026-07-31 in `PROGRESS.md` dokumentierte offene Beobachtung: Plan 0001 §2
sieht vor, dass neues Rohmaterial das Projekt auf `INGESTED` zurückfallen lässt;
`invalidate_project`/`invalidate_export` und das `content_hash`-Feld existieren, werden aber
von niemandem aufgerufen.

**Umsetzung:**

- Zustandsloser Check `pipeline.pending_assets(project)` — `scan_media` gegen die Hashes in
  `assets.json`. Kein Vision-Call, keine Kosten. Wird in `frameforge status` und im Wizard
  angezeigt, unabhängig von der aktuellen Phase.
- Beim Erreichen von `STORYBOARDED` einen Fingerprint über den `assets.json`-Stand im
  vorhandenen `content_hash`-Feld des Exports ablegen; spätere Schritte vergleichen ihn.
- Bei Abweichung **warnen und fragen, nicht still neu bauen** — kein Hintergrund-Worker.

Betroffen ist bewusst nur der Export ab `STORYBOARDED`: `DESIGNED` und `BRIEFED` hängen
inhaltlich nicht am Asset-Inventar.

**Abnahme G:** Neue Datei in `media_root` → `frameforge status` weist sie aus; ein Export, der
vor der Ergänzung storyboarded wurde, meldet beim nächsten Schritt die Abweichung.

---

## Arbeitspaket H — Abschluss-Audit

Ausdrücklicher Wunsch: am Ende prüfen, dass alles stringent ineinandergreift.

- **H1 Konsistenz:** Ein Durchgang über alle neuen Felder (`captured_at`, `day`, `stage`,
  `fade_in_s`, Transition `black`) — sind sie in Plan 0001 §4 dokumentiert, in `qc.validate`
  berücksichtigt, im NLE-Export abgebildet, in `stats`/`report` sichtbar?
- **H2 Datenprüfung am Fundus:** Warum steht bei 251 von 255 Assets `source: drone` — auch bei
  Fotos? Und warum liefert `guess_source` für `DJI_…`-Dateien `camera` statt `drone`, obwohl
  der Dateiname-Fallback greifen müsste? Klären, ggf. korrigieren; betrifft `query --source`
  und die Auswertungen.
- **H3 Regression:** volle Testsuite, `ruff`, `doctor`, plus ein echter End-to-End-Lauf des
  proto-Projekts (`ingest → … → render → nle`).
- **H4 Realer Durchlauf:** eine Etappe des neuen Exports mit Karte, HUD, Schwarzblende und
  neuer Bauchbinde als 60-Sekunden-Preview, visuelle Abnahme durch den Nutzer, bevor die
  vollen 15 Minuten gebaut werden.

---

## Reihenfolge und Abhängigkeiten

```
E (relink)  ─┐
A (Chronologie/Orte) ─┬─→ B (Karte: Viewport, km, HUD) ─┐
D (Grafik)  ──────────┘                                 ├─→ H (Audit)
C (Schwarzblende) ──────────────────────────────────────┤
F (Musik-Segmente) ─────────────────────────────────────┤
G (Invalidierung) ──────────────────────────────────────┘
```

- **E zuerst**, weil der Nutzer die Ordnerstruktur ohnehin gerade umbaut.
- **A vor B** — der Kilometerzähler und das Etappen-HUD brauchen `stages.csv` und echte
  Aufnahmezeiten.
- **D parallel** zu A/B, keine Abhängigkeit.
- **C, F, G** sind unabhängig und können jederzeit dazwischen.
- **H zuletzt**, als eigener Task mit eigenem Commit.

Ein Task, ein Commit, Abnahmekriterium nachweisen, `PROGRESS.md` fortschreiben — wie in
`CLAUDE.md` festgelegt. Die Tabelle für diese Arbeitspakete wird bei Umsetzungsbeginn in
`PROGRESS.md` angelegt.

---

## Bewusst nicht in diesem Plan

- **Automatische Farbangleichung zwischen Kameras** (Drohne vs. Handy vs. Action-Cam auf einen
  gemeinsamen Look ziehen). Der vorhandene Grade wirkt global aus dem Preset, plus optionale
  LUT. Eine echte Clip-zu-Clip-Angleichung ist eine deutlich größere CV-Aufgabe und für das
  Ziel nicht erforderlich.
- **KI-Musikgenerierung**, automatische Untertitel, Musik-Lizenz-Nachweis — bleiben wie in
  Plan 0001 §11 zurückgestellt.
- **Regie-Entscheidungen** für den 15-Minuten-Export (Tempo, Kapitelaufteilung, welcher Clip
  wohin, welche Musik). Die gehören in `brief.yaml` und das Beat-Sheet, nicht in den Code.
- **Beschaffung des Materials** (Export aus iCloud, Material der Partnerin, Vorschnitt). Reine
  Nutzer-Vorarbeit außerhalb des Systems.
