# FrameForge — Ausbauplan „Roadtrip-Vlog" (0003)

Erstellt am 2026-08-01. **Ersetzt `0002-vlog-ausbau.md`** (erster Entwurf desselben Tages) —
0002 bleibt nur zur Historie liegen und wird nicht umgesetzt.

## Context

Der erste echte Export hat den Kernprozess bestätigt: Ingest, Media-Index, Story→Timeline,
Render und NLE-Export funktionieren am echten Material (255 Assets, 236 Videos / 19 Fotos).
Auswahl und Schnittrhythmus waren gut.

Nächstes Ziel: ein ~15-minütiger, chronologisch erzählter Roadtrip-Vlog („Videotagebuch") aus
demselben Fundus — Start zu Hause, über Flensburg nach Norwegen, Tag für Tag, mit Etappen,
Zwischenstopps, Unterkünften und Aktivitäten. Es bleibt beim Projekt `norwegen-2026`; es
entsteht ein **neuer Export**. Der Fundus wird vorher erweitert (Fotoauswahl, Handy-4K60-Clips,
Material der Partnerin).

Dieser Plan beschreibt die dafür nötigen **Erweiterungen der Werkzeugschicht**. Reine
Regie-Entscheidungen (Tempo, Kapitelaufteilung, Clip-Auswahl, Musikstil) gehören in den Brief
des Exports, nicht in den Code.

### Leitprinzip (unverändert aus Plan 0001, §M3)

Der Code liefert **generische Fähigkeiten**, keine projektspezifische Gestaltung. Farben,
Icons, Kartenstil, konkrete Orte kommen aus Projektdaten und Designsystem — nicht aus
`frameforge/`. Kein Norwegen-spezifisches Styling, keine hart codierten Ortsnamen.

---

## 0. Grundregel: Rückwärtskompatibilität

**Das bestehende Projekt `norwegen-2026` muss ohne Neu-Indizierung weiterlaufen.** Die 255
bereits indizierten Assets haben Beschreibungen, Tags und Ratings, die durch Claude Vision
entstanden sind — dieser Aufwand darf nicht verloren gehen. Konkret gilt für jedes
Arbeitspaket:

1. **Alle neuen Asset-Felder sind optional.** `captured_at`, `day`, `stage`, `elevation_m`,
   `color_stats` — fehlt eines, verhält sich der Code wie bisher. Kein Feld wird zur Pflicht.
2. **Alle neuen Timeline-Felder haben Defaults, die das heutige Verhalten ergeben.**
   `AudioClip.fade_in_s` default 0, Transition-Typ `black` nur wenn explizit gesetzt,
   `map.render_route_frames(viewport="fit")` als Default. Eine bestehende `timeline.json`
   rendert bit-identisch weiter.
3. **Nachtragen statt neu erzeugen.** Fehlende technische Metadaten werden per Backfill (A0)
   ergänzt, ohne `content`, `rating` oder `source` anzufassen und ohne einen einzigen
   Vision-Call.
4. **`.state.json`** bleibt bei `schema_version: 1`; neue Felder bekommen Defaults über
   Pydantic, alte Dateien laden unverändert.
5. **Regressionstest als Abnahmebedingung jedes Pakets:** `projects/proto/` und die bestehende
   Timeline von `test-timelapse-journey` müssen unverändert durchlaufen.

Was der Nutzer nach der Umsetzung einmalig ausführen muss (kein Neu-Indizieren), steht am Ende
unter „Migration des bestehenden Projekts".

---

## Befund aus dem Realbetrieb (belegt, nicht vermutet)

Auswertung von `projects/norwegen-2026/index/assets.json` (255 Einträge):

| Beobachtung | Zahl | Konsequenz |
|---|---|---|
| Assets mit `captured_at` | 19 von 255 | **nur die Fotos.** Kein Video hat eine Aufnahmezeit |
| Videos mit `gps.lat/lon` | 0 von 236 | keine Geodaten im vorgeschnittenen Videomaterial |
| Assets mit `gps.place` | 242 | Ort stammt **aus dem Ordnernamen**, nicht aus Zeit/Position |
| `source` = `drone` | 251 von 255 | auch bei Fotos — ungeprüft, siehe I2 |

Daraus folgt der bemerkte Fehler: ein Ordner wie
`2026-07-28_Norwegen_Geiranger-Lom_1_Trollstigen` beschreibt eine **Etappe**, keinen **Ort** —
und liefert Werte wie `"Geiranger-Lom/Trollstigen"`. Trollstigen-Clips landen unter
„Geiranger".

**Die Rohdaten sind aber vorhanden, sie werden nur nicht ausgelesen:**

- Die Ordner sind sauber nach `YYYY-MM-DD_Ort_Thema` benannt.
- Die Dateinamen tragen die volle Aufnahmezeit: `DJI_20260720153625_0006_D-…`
- Sie tragen sogar den Trim-Offset des Vorschnitts:
  `…_D-00.02.10.556-00.02.18.774-seg5.MP4` — also In- und Out-Punkt im Originalclip. Damit ist
  die exakte Aufnahmezeit des Ausschnitts rekonstruierbar: Originalzeit + In-Punkt.
- Der Originaldateiname ist durch Abschneiden des `-HH.MM.SS.mmm-…-segN`-Suffix eindeutig
  ableitbar — die Brücke zu den ungeschnittenen Originalen mit intakten GPS-Daten.

---

## Arbeitspaket A — Chronologie, Ort und Etappen

**Ziel:** Jedes Asset kennt seine echte Aufnahmezeit, seinen Tag, seine Etappe und einen
sinnvollen Ort. Die Zuordnung entsteht aus Daten (Zeit + Etappenliste + GPS), nicht aus einer
Ordnernamen-Vermutung — und wo Daten fehlen, aus einer bewussten Entscheidung des Nutzers statt
aus einer stillen Annahme.

### A0 — Backfill statt Neu-Indizieren

Neues Kommando `frameforge backfill-metadata <projekt> [--dry-run]`. Liest `assets.json`,
probt die Originaldateien erneut und ergänzt **ausschließlich technische Felder**
(`captured_at`, `gps.lat/lon`, `elevation_m`, `tech`). `content`, `tags`, `rating`, `source`
und die Freitext-Notizen in den `.md`-Dateien bleiben unangetastet. Kein Vision-Call.

Das ist der Mechanismus, der Regel 0.3 umsetzt — und die Voraussetzung dafür, dass A1–A4 auf
dem bestehenden Fundus überhaupt greifen können.

**Abnahme:** Nach dem Lauf haben ≥ 90 % der 236 Videos eine Aufnahmezeit; `content`/`rating`
sind bitgleich zu vorher (Diff auf `assets.json` zeigt nur technische Felder).

### A1 — Aufnahmezeit für Videos

`frameforge/probe.py`:

- `probe_video` liest zusätzlich `format.tags.creation_time` bzw.
  `com.apple.quicktime.creationdate` (beides steckt bereits im abgefragten ffprobe-JSON, wird
  nur nicht ausgewertet) und liefert `captured_at` im selben ISO-Format wie `probe_photo_exif`.
- Neuer Helfer `captured_at_from_name(path)` für Kameramuster mit vollem Zeitstempel:
  `DJI_20260720153625…`, `IMG_20260720_153625…`, `VID_…`, `PXL_…`.
- Neuer Helfer `trim_offset_from_name(path)` für das Vorschnitt-Suffix
  `-HH.MM.SS.mmm-HH.MM.SS.mmm-segN` → `(in_s, out_s)`. Wo vorhanden, wird der In-Punkt auf die
  Aufnahmezeit des Originals addiert; das macht die Chronologie **innerhalb** eines Drehtags
  korrekt, nicht nur tagesgenau.
- Priorität: Container-Zeit → Dateinamen-Zeit (+ Trim-Offset) → Datum aus dem Pfad → `mtime`.
  Welche Quelle gegriffen hat, wird als `captured_at_source` mitgeschrieben — für die
  Plausibilitätsprüfung in A5 relevant.

`frameforge/preindex.py`: der Video-Zweig von `_prepare_one` schreibt `captured_at` (der
Foto-Zweig tut das bereits).

### A2 — GPS aus den ungeschnittenen Originalen holen

Der Vorschnitt hat die Metadaten weitgehend verloren (0 von 236 Videos haben Koordinaten). Die
Originale liegen aber noch vor und tragen sie.

- `project.yaml` bekommt ein **optionales** Feld `originals_root`. Fehlt es, verhält sich alles
  wie heute.
- Neuer Schritt in A0: für jedes Video ohne GPS wird über den aus dem Dateinamen abgeleiteten
  Originalnamen (Suffix abschneiden) die Originaldatei unter `originals_root` gesucht und per
  `exiftool` auf GPS/Zeit geprüft. Treffer werden übernommen und mit
  `gps.source: "original"` markiert.
- Findet sich kein Original, bleibt das Asset ohne Koordinaten — das ist kein Fehler, sondern
  Eingabe für A5.

**Abnahme:** Für eine Stichprobe von 10 Clips mit vorhandenem Original werden Koordinaten
übernommen; für Clips ohne Original passiert nichts Stilles, sie erscheinen in der Lückenliste.

### A3 — Etappen als eingebbare Projektdaten (+ Prompt-Vorlage)

Neue Datei `projects/<name>/route/stages.csv` — hier hinterlegt der Nutzer seine Streckenliste:

```csv
day,date,from,to,via,km,overnight,note
1,2026-07-19,Zuhause,Flensburg,,320,Flensburg,Anreise
2,2026-07-20,Flensburg,Skien,Fähre Hirtshals-Larvik,410,Hütte am See,
9,2026-07-28,Geiranger,Lom,Trollstigen,190,Lom,Passstraße
```

`frameforge/gpx.py`:

- `parse_stages(path)` — analog zum vorhandenen `parse_locations`: validiert Pflichtspalten
  `day,date,from,to`, parst `km` und `date`, Fehlermeldung mit Zeilennummer.
- `stage_for(timestamp, stages)` — Etappe eines Zeitpunkts über das Datum.

`locations.csv` (existiert bereits: `name,lat,lon,type,day`) bleibt zuständig für Punkte auf
der Karte: Übernachtungen, POIs, Zwischenziele wie Trollstigen.

**Neue Prompt-Vorlage `templates/prompts/route.md`** — damit der Nutzer seine Reiseunterlagen
(PDF-Buchungen, Google-Maps-Liste, Notizen) einer beliebigen KI vorlegen und das fertige CSV
zurückbekommen kann. Analog zu den bestehenden `templates/prompts/graphics.md` und `music.md`.
Inhalt als Startfassung:

```
Ich gebe dir Reiseunterlagen (Buchungen, Routenliste, Notizen). Erstelle daraus
eine CSV-Datei mit exakt diesen Spalten, ohne zusätzliche Spalten und ohne Kommentare:

day,date,from,to,via,km,overnight,note

Regeln:
- day: fortlaufende Reisetag-Nummer ab 1, lückenlos.
- date: ISO-Format YYYY-MM-DD.
- from/to: Ortsnamen wie im Zielland üblich geschrieben (z. B. "Flåm", nicht "Flam").
- via: wichtigste Zwischenstopps/Passstraßen dieser Etappe, mehrere mit "; " getrennt.
  Leer lassen, wenn es keine gab.
- km: gefahrene Strecke der Etappe als ganze Zahl. Wenn unbekannt, leer lassen –
  NICHT schätzen und nicht erfinden.
- overnight: Ort der Übernachtung nach dieser Etappe.
- note: eine kurze Bemerkung oder leer.
- Standtage (keine Weiterfahrt) bekommen trotzdem eine Zeile: from = to = Ort, km = 0.
- Antworte NUR mit der CSV, beginnend mit der Kopfzeile.

Zusätzlich, als zweiter separater CSV-Block mit den Spalten:
name,lat,lon,type,day
alle Orte, die auf einer Karte markiert werden sollen: Übernachtungen (type=overnight),
Sehenswürdigkeiten/Zwischenstopps (type=poi), größere Städte entlang der Route zur
Orientierung (type=city). Koordinaten in Dezimalgrad. Wenn du eine Koordinate nicht
sicher weißt, lass die Zeile weg statt zu raten.
```

Neues Schema-Feld je Asset: `day` (int) und `stage` (str), ergänzend zu `gps.place`. In Plan
0001 §4 nachtragen.

### A4 — Zuordnung als eigener, prüfbarer Schritt

Neues Kommando `frameforge assign-places <projekt> [--dry-run] [--force]`:

1. Liest `assets.json`, `route/stages.csv`, `route/locations.csv` und — falls vorhanden —
   `route/roadtrip.gpx`.
2. Bestimmt je Asset über `captured_at`: `day`, `stage` (`from`→`to`), Ort. Ort-Logik in dieser
   Reihenfolge:
   echte GPS-Position (Asset selbst oder GPX über `nearest_location`) → nächstgelegener POI aus
   `locations.csv` innerhalb einer Toleranz → bei Fahretappen der Vermerk
   `unterwegs: <from> → <to>` → `unknown`.
3. Schreibt `day`, `stage`, `gps.place` zurück (Merge, keine Vision-Kosten). Manuell gesetzte
   Orte werden ohne `--force` nicht überschrieben.
4. Report: Assets je Tag/Etappe, ohne Zeit, ohne Ort, sowie **Konflikte** — Fälle, in denen der
   bisherige (aus dem Ordnernamen geratene) Ort dem berechneten widerspricht.

### A5 — Lückenliste und Ortsvergabe für unklare Clips („Roadtrip-Shots")

Das eigentliche Restproblem: Zwischenstopps auf einer Fahretappe. Sie sind erzählerisch
wertvoll („kurz angehalten, ein paar Aufnahmen gemacht"), aber gerade dort ist am wenigsten
klar, wo genau man war.

Neues Kommando `frameforge places-todo <projekt> [--day N]` — kompakte Liste aller Assets, deren
Ort unklar ist (kein GPS, kein POI in Reichweite), mit Zeit, Etappe, Nachbar-Assets und
Keyframe-Pfad. Gegenstück zum bestehenden `index-todo`, gleiche Bauart.

Neues Kommando `frameforge set-place <projekt> <asset-id|hash> --place "…" [--kind stop|leg]`
schreibt den Ort. `--kind leg` erzeugt die Etappen-Schreibweise `unterwegs: Geiranger → Lom`,
`--kind stop` einen benannten Zwischenstopp.

Der Ablauf ist derselbe wie beim Indizieren: Liste holen → Keyframes ansehen → schreiben. Ich
kann die Clips dabei ansehen und Vorschläge machen (der Keyframe zeigt oft eindeutig
Wasserfall/Pass/Fjord); die Entscheidung bestätigt der Nutzer.

**Abnahme A gesamt:** Nach `/ff-route` + `assign-places` sind die Clips aus
`…Geiranger-Lom_1_Trollstigen` dem Tag 9 und der Etappe *Geiranger→Lom* zugeordnet und tragen
als Ort *Trollstigen*, nicht *Geiranger*. `frameforge days` zeigt echte Reisetage statt
„unknown". Kein Asset hat stillschweigend einen geratenen Ort.

### A6 — Geführte Eingabe und Plausibilitätsprüfung

Neuer Slash-Command `.claude/commands/ff-route.md`: fragt die Etappen konversationell ab bzw.
nimmt die vom Nutzer (oder von einer anderen KI per `templates/prompts/route.md`) gelieferte
Liste entgegen, schreibt `stages.csv` und `locations.csv`, ruft `assign-places --dry-run` und
zeigt den Report, bevor real geschrieben wird.

Neuer Agent `.claude/agents/route-planner.md`. Aufgaben:

- **Plausibilität prüfen:** lückenlose Tage, monotone Daten, Ankunftsort = Startort des
  Folgetags, Kilometerangaben im Verhältnis zur Luftlinie plausibel (nicht 40 km für eine
  Strecke, die 200 km Luftlinie hat), Übernachtungsort passt zum Etappenende.
- **Abgleich gegen das Material:** Gibt es Tage in `stages.csv` ohne ein einziges Asset? Gibt es
  Assets an Tagen, die in der Etappenliste fehlen? Beides deutet auf einen Eingabefehler.
- **Routengeometrie beschaffen** (siehe B5) und fehlende Koordinaten für Orte ergänzen.
- **Nie raten:** fehlende oder unsichere Werte werden als Rückfrage gemeldet, nicht erfunden.
  Eine falsche Koordinate ist schlimmer als eine fehlende — sie fällt erst im gerenderten Video
  auf.

---

## Arbeitspaket B — Karte: mitfahrender Ausschnitt, Kilometer, Höhenprofil

**Ziel:** Eine kleine Karte (z. B. unten rechts), auf der ein Marker die Route abfährt, die
Linie hinter sich nachzieht, der **Ausschnitt mitwandert** statt die ganze Tour zu zeigen, und
darunter Tag, Etappenziel, Kilometerstand und Höhe mitlaufen.

**Stand heute** (`frameforge/map.py`): Die Projektion (`_make_projector`) bildet auf die
Bounding-Box des **gesamten** Tracks ab — der Ausschnitt ist fix, nur der Marker bewegt sich.
Es gibt keine Distanz- und keine Höhenberechnung, kein HUD, und `render_basemap` liefert nur
ganze Kachelraster (Vielfaches von 256 px), die exakt zur Zielgröße passen müssen.

### B1 — Distanz und Höhe

`frameforge/gpx.py`:

- `haversine_km(a, b)` und `cumulative_km(track)` — kumulierte Strecke je Trackpunkt.
- `elevation_profile(track)` — Höhe je Punkt. GPX-Trackpunkte tragen `<ele>`; `gpxpy` liefert
  das über `point.elevation`. Fehlt die Höhe (etwa bei einer aus Wegpunkten rekonstruierten
  Route), wird sie über einen Höhen-Dienst nachgeschlagen und **im Projekt gecacht**
  (`route/elevation.json`) — genau eine Abfrage je Koordinate, nie erneut. Der Dienst ist
  injizierbar wie schon beim Tile-Fetcher, damit Tests offline laufen.
- Abgeleitete Werte für das HUD: aktuelle Höhe, kumulierte Höhenmeter aufwärts, Etappenprofil.

### B2 — Mitwandernder Viewport

`frameforge/map.py`:

- Umstellung der Projektion von Equirectangular auf **Web-Mercator**
  (`latlon_to_pixel(lat, lon, zoom)`), damit Route und OSM-Kacheln im selben Koordinatensystem
  liegen — Voraussetzung dafür, dass eine Basiskarte unter der Route pixelgenau stimmt.
- `render_route_frames(..., viewport="follow", zoom=…, ease_s=…)`: der Bildausschnitt zentriert
  sich auf die aktuelle Position, geglättet über ein gleitendes Fenster, damit die Karte nicht
  zittert. `viewport="fit"` bleibt Default und damit exakt das heutige Verhalten.
- `basemap_viewport(center_latlon, zoom, size, cache_dir, fetcher=None)`: schneidet aus dem
  Kachel-Cache den benötigten Ausschnitt in beliebiger Pixelgröße — ersetzt für den
  Follow-Modus die „nur ganze Kachelraster"-Beschränkung.
- **Halt an Orten:** erreicht der Marker einen POI, pausiert der Reveal für eine
  konfigurierbare Haltezeit (`dwell_s`), damit der Ortsname lesbar ist.

### B3 — Etappen-HUD

Neues SVG-Template `templates/svg/map-hud.svg` (token-parametrisiert wie alle anderen): Tag,
Etappe (`von → nach`, optional `über`), Kilometerstand, Höhe, optional ein kleines
Höhenprofil-Diagramm der Etappe mit Positionsmarkierung.

Gerendert wird **nicht** pro Frame (zu teuer), sondern in Stufen — ein PNG je angefangenem
Kilometer bzw. je Sekunde — als eigene Overlay-Sequenz. Die Karte bleibt eine Alpha-Ebene
(`tracks.map`), das HUD wird als `tracks.overlay` darübergelegt; beide Mechanismen existieren
im Renderer bereits.

### B4 — Integration

`.claude/agents/map-animator.md` um Follow-Modus, `stages.csv`, HUD und Höhenprofil erweitern.

### B5 — Routengeometrie beschaffen

Für eine Karte, auf der wirklich die gefahrene Straße nachgezeichnet wird, braucht es mehr als
die Etappen-Eckpunkte. Drei Wege, in dieser Reihenfolge:

1. **Echter GPX-Track**, falls vorhanden — beste Qualität, inkl. Zeit und Höhe.
2. **Export aus Google Maps** (die Route als KML/GPX herunterladen und unter `route/` ablegen).
   Der Nutzer macht das im Browser; ein neuer Parser für KML wird ergänzt, da `gpxpy` nur GPX
   liest.
3. **Routing aus den Etappenpunkten**: Straßenverlauf zwischen `from`, `via` und `to` über
   einen Routing-Dienst berechnen, Ergebnis als GPX unter `route/` ablegen und cachen. Das ist
   die Rückfallebene, wenn kein Track existiert.

Das Ergebnis ist in allen drei Fällen dieselbe Datei — der Rest der Pipeline sieht keinen
Unterschied. Größere Städte zur Orientierung kommen als `type=city` aus `locations.csv`.

**Abnahme B:** Für Tag 9 (Geiranger→Lom über Trollstigen) entsteht ein Karten-Clip, in dem der
Ausschnitt der Route folgt, die Linie wächst, POIs beschriftet auftauchen, Kilometerzähler und
Höhe mitlaufen und Tag/Ziel im HUD stehen. Ohne `viewport="follow"` ist die Ausgabe identisch
zum heutigen Verhalten (Regressionstest).

---

## Arbeitspaket C — Schwarzblende zwischen zwei Clips

**Stand heute** (`frameforge/render.py`): `_CROSSFADE_TYPES = {fade, dissolve, slow_dissolve,
crossfade}` erzeugt `xfade`; eine Blende nach/aus Schwarz gibt es nur ganz außen (erster und
letzter Clip der Timeline).

**Umsetzung:** Neuer Übergangstyp `black` mit optionaler Haltezeit, verarbeitet in
`_join_video_segments` als dritte Variante neben `concat` und `xfade`: Ausblenden des
vorherigen Clips, optionale Haltezeit auf Schwarz, Einblenden des nächsten. Anders als `xfade`
**verlängert** das die Timeline — die Timing-Invariante aus dem Crossfade-Fix gilt umgekehrt
und muss sich sauber in den `tl_in`-Werten der Folgeclips niederschlagen, damit Audio und
Overlays nicht verrutschen. `qc.validate` bekommt eine Regel dafür.

**Abnahme C:** Timeline mit `transition_in: {type: black, dur: 1.0}` in der Mitte rendert eine
sichtbare Schwarzblende; Gesamtdauer stimmt mit `timeline.duration` überein; bestehende
concat-/xfade-Timelines rendern unverändert.

---

## Arbeitspaket D — Grafik-Aufwertung

**Stand heute** (`templates/svg/lower-third.svg`): ein Rechteck mit Deckkraft plus zwei
Textzeilen. Mehr nicht — exakt das beschriebene „transparenter Kasten, Text, fertig".

### D1 — Templates aufwerten

Weiterhin rein token-parametrisiert, kein projektspezifisches Styling:

- `lower-third.svg`: Akzentbalken, abgerundete Ecken, Farbverlauf statt Vollton, weicher
  Schlagschatten, optionale Icon-/Logo-Fläche, klare Typo-Hierarchie, größere Default-Maße.
- Neue Templates: `stage-card.svg` (Datum, Tag N, von→nach), `map-hud.svg` (siehe B3),
  `stat-badge.svg` (km, Höhenmeter, Dauer).
- **Relative Größen:** Tokens für Schrift- und Balkenmaße als Faktor der Zielhöhe statt
  absoluter Pixel, damit dieselben Tokens in 1080p-Preview und 4K-Final gleich wirken. Die
  vorhandene `type_scale` in `tokens.yaml` ist heute reserviert und ungenutzt — sie wird hier
  echt verdrahtet.
- Ein-/Ausblenden nutzt das bereits vorhandene `anim.fade_in_s`/`fade_out_s` am `OverlayClip`.

### D2 — Generierte Grafiken statt reiner Typo

Für Elemente, bei denen reiner Text zu nüchtern wirkt (Titelkarte, Kapitelmarken, Marker):
gestaltete Grafiken, die extern erzeugt und in `design/assets/` abgelegt werden.

Die Infrastruktur dafür ist bereits vollständig vorhanden und wird nur erweitert:
`design/prompts.md` (angeforderte Grafiken), `templates/prompts/graphics.md` (Prompt-Vorlage),
`design.asset_inventory` + `frameforge design-status` (Abgleich angefordert ↔ abgelegt).

Zu ergänzen:

- Prompt-Bausteine in `graphics.md` für die neuen Typen: Titelkarten-Hintergrund,
  Kapitelmarke, Landesflaggen-/Wappen-Motiv, Karten-Rahmen, Fahrzeug-/Positions-Icon.
- Der `design-system`-Agent schlägt aktiv vor, welche Grafiken ein Export aufwerten würden,
  statt nur auf Nachfrage zu reagieren.
- Titelkarte und Kapitelmarken können eine Hintergrundgrafik aufnehmen (heute nur Farbfläche).

Nicht Teil des Codes: das Erzeugen der Bilder selbst — das läuft über einen Bildgenerator bzw.
die vorhandene `canvas-design`-Fähigkeit, das Ergebnis legt der Nutzer ab. So bleibt der Code
frei von projektspezifischer Gestaltung (Leitprinzip).

**Abnahme D:** Alle Templates rendern gegen ein gemeinsames Token-Set fehlerfrei zu PNG, in
1080p und 2160p optisch konsistent; visuelle Abnahme durch den Nutzer an einem Beispielframe.

---

## Arbeitspaket E — `relink`: Pfade nach Umsortieren reparieren

**Warum:** Die Ordnerstruktur unter `media_root` wird gerade umgebaut. Der Analyse-Cache hängt
am Datei-Hash und überlebt das Verschieben (keine erneute Vision-Analyse) — der in
`assets.json` gespeicherte **Pfad** wird aber nicht nachgezogen. Der Fehler fiele erst beim
Final-Render auf, weil `render_final` die Originale über genau diesen Pfad auflöst.

**Umsetzung:** `frameforge relink <projekt> [--dry-run]` — scannt `media_root`, matcht per Hash
gegen `assets.json`, aktualisiert geänderte `path`-Werte, meldet verwaiste Einträge (Datei
nicht mehr auffindbar) und neue, noch nicht indizierte Dateien.

**Abnahme E:** Datei verschieben → `relink` → Pfad korrigiert, `assets.json` sonst unverändert,
keine erneute Analyse, Final-Render findet das Original.

---

## Arbeitspaket F — Musik: mehrere Titel, Übergänge, Stille

**Stand heute** (`frameforge/audio.py`): BPM/Beat-Grid/Energiekurve je Track (gecacht),
`duck_curve` für Musik unter O-Ton. Mehrere Musik-Clips können in `tracks.audio` liegen und
werden gemischt — es gibt aber keine Ein-/Ausblendung pro Clip und keine Logik für
Kapitelwechsel.

**Umsetzung:**

- `timeline.AudioClip` um `fade_in_s` / `fade_out_s` erweitern; `render.build_filtergraph`
  setzt entsprechende `afade`-Filter (heute nur konstanter `gain_db` plus Ducking-Kette).
- `audio.segment_plan(tracks, sections, *, gap_s=0.0)`: verteilt n Titel auf n Kapitel, legt
  Übergänge auf den nächstgelegenen Beat des ausklingenden Titels, erzeugt Ein-/Ausblendwerte;
  `gap_s > 0` ergibt eine echte Stille zwischen zwei Titeln.

Bewusst **keine** automatische Stilanalyse („passen diese Titel zusammen") — welcher Titel zu
welchem Kapitel gehört, entscheidet der Nutzer bzw. der `audio-designer` im Brief.

**Abnahme F:** Timeline mit drei Titeln über drei Kapitel rendert hörbar sauber: Überblendung
auf dem Beat, definierte Stille am gewünschten Schnitt, kein Pegelsprung.

---

## Arbeitspaket G — Invalidierung bei neuem Material

Übernimmt die am 2026-07-31 in `PROGRESS.md` festgehaltene Beobachtung: Plan 0001 §2 sieht vor,
dass neues Rohmaterial das Projekt auf `INGESTED` zurückfallen lässt;
`invalidate_project`/`invalidate_export` und das `content_hash`-Feld existieren, werden aber von
niemandem aufgerufen.

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

## Arbeitspaket H — Farbangleichung zwischen Clips

Im ersten Entwurf noch ausgeklammert, auf ausdrücklichen Wunsch aufgenommen: der Fundus mischt
Drohne, Handy und Kamera. Jede Quelle hat ihre eigene Grundstimmung; über 15 Minuten fällt das
als Unruhe auf, auch wenn jeder Clip für sich gut aussieht.

**Stand heute:** `render.grade_filter` legt **einen** Grade aus dem Preset über den gesamten
Export, optional plus LUT. Eine Angleichung der Clips **untereinander** gibt es nicht.

**Umsetzung in zwei Stufen, in dieser Reihenfolge im Filtergraph:**

- **H1 Messen (kostenlos).** `analyze.color_stats(frames)` — Mittelwert und Streuung je Kanal,
  Farbtemperatur-Indikator, aus den **bereits vorhandenen Keyframes**. Kein neues Decoding, kein
  Vision-Call. Ergebnis als `asset["color_stats"]`, nachrüstbar über den Backfill aus A0.
- **H2 Angleichen.** `render.match_filter(asset_stats, reference)` erzeugt je Clip einen
  milden `eq`/`colorbalance`-Korrekturschritt gegen eine gemeinsame Referenz. Die Referenz ist
  der Median über die im Export verwendeten Clips (nicht über den ganzen Fundus — ein Export ist
  die relevante Einheit), alternativ ein im Brief benannter Hero-Clip.
- **Reihenfolge:** erst angleichen (`match`), dann der Stil-Grade aus dem Preset, dann die
  optionale LUT. Nur so bleibt „kühl" oder „satte Farben" eine Aussage über den Film und nicht
  über die zufällige Kameramischung.
- **Begrenzung und Abschaltbarkeit.** Die Korrektur wird gedeckelt (eine Nachtaufnahme darf
  nicht auf Tageslicht gezogen werden) und ist im Brief abschaltbar
  (`color_match: off|soft|strong`, Default `soft`). Die berechneten Werte landen **pro Clip in
  `timeline.json`**, nicht als versteckte Renderer-Magie — nachvollziehbar, überschreibbar,
  reproduzierbar, und sie gehen in den NLE-Export mit.

**Abnahme H:** Ein Testschnitt aus drei Clips unterschiedlicher Quellen zeigt nach `soft`
sichtbar weniger Sprünge in Helligkeit und Farbtemperatur; mit `off` ist der Render bitgleich
zum heutigen Verhalten; kein Clip wird um mehr als den Deckelwert verschoben.

---

## Arbeitspaket I — Abschluss-Audit

- **I1 Konsistenz:** Durchgang über alle neuen Felder (`captured_at`, `day`, `stage`,
  `elevation_m`, `color_stats`, `fade_in_s`, Transition `black`) — dokumentiert in Plan 0001 §4,
  berücksichtigt in `qc.validate`, abgebildet im NLE-Export, sichtbar in `stats`/`report`?
- **I2 Datenprüfung am Fundus:** Warum steht bei 251 von 255 Assets `source: drone` — auch bei
  Fotos? Und warum liefert `guess_source` für `DJI_…`-Dateien `camera` statt `drone`, obwohl der
  Dateinamen-Fallback greifen müsste? Klären und korrigieren; betrifft `query --source` und alle
  Auswertungen.
- **I3 Rückwärtskompatibilität nachweisen:** `projects/proto/` end-to-end
  (`ingest → … → render → nle`), plus ein Re-Render der bestehenden Timeline von
  `test-timelapse-journey` mit Byte-Vergleich gegen den bisherigen Stand.
- **I4 Regression:** volle Testsuite, `ruff`, `doctor`.
- **I5 Realer Durchlauf:** eine Etappe des neuen Exports mit Karte, HUD, Höhenprofil,
  Schwarzblende, neuer Bauchbinde und Farbangleichung als 60-Sekunden-Preview — visuelle Abnahme
  durch den Nutzer, bevor die vollen 15 Minuten gebaut werden.

---

## Reihenfolge und Abhängigkeiten

```
E (relink) ─┐
A0 Backfill ─→ A1/A2 (Zeit, GPS) ─→ A3/A4 (Etappen, Zuordnung) ─→ A5/A6 (Lücken, Agent)
                                              │
                                              └─→ B (Karte: Viewport, km, Höhe, HUD) ─┐
D (Grafik) ───────────────────────────────────────────────────────────────────────────┤
C (Schwarzblende) ────────────────────────────────────────────────────────────────────┼─→ I (Audit)
H (Farbangleichung) ──────────────────────────────────────────────────────────────────┤
F (Musik-Segmente) ───────────────────────────────────────────────────────────────────┤
G (Invalidierung) ────────────────────────────────────────────────────────────────────┘
```

- **E zuerst**, weil die Ordnerstruktur ohnehin gerade umgebaut wird.
- **A0 vor allem anderen in A** — ohne Backfill greifen A1–A5 nicht auf dem bestehenden Fundus.
- **A vor B**: Kilometerzähler, Höhenprofil und Etappen-HUD brauchen `stages.csv`, echte
  Aufnahmezeiten und die Routengeometrie.
- **C, D, F, G, H** sind unabhängig und können jederzeit dazwischen.
- **I zuletzt**, als eigener Task mit eigenem Commit.

Ein Task, ein Commit, Abnahmekriterium nachweisen, `PROGRESS.md` fortschreiben — wie in
`CLAUDE.md` festgelegt. Die Tabelle für diese Arbeitspakete wird bei Umsetzungsbeginn in
`PROGRESS.md` angelegt.

---

## Migration des bestehenden Projekts

Was nach der Umsetzung einmalig auszuführen ist — **ohne Neu-Indizierung, ohne Vision-Kosten:**

1. Material konsolidieren und Ordnerstruktur aufräumen (Nutzer).
2. `frameforge relink norwegen-2026` — Pfade nachziehen (E).
3. `originals_root` in `project.yaml` eintragen, falls die ungeschnittenen Originale verfügbar
   sind (A2).
4. `frameforge backfill-metadata norwegen-2026` — Aufnahmezeiten, GPS, Farbstatistik nachtragen
   (A0/H1).
5. `/ff-route norwegen-2026` — Etappen erfassen, Plausibilität prüfen lassen (A3/A6).
6. `frameforge assign-places norwegen-2026 --dry-run`, Report prüfen, dann real ausführen (A4).
7. `frameforge places-todo norwegen-2026` — verbleibende unklare Clips gemeinsam durchgehen (A5).
8. `/ff-ingest` + `/ff-index` für das **neu hinzugekommene** Material — nur die neuen Dateien
   gehen an den `media-indexer`.
9. `/ff-brief norwegen-2026 <neuer-export>` — der neue 15-Minuten-Export beginnt hier.

---

## Bewusst nicht in diesem Plan

- **Automatische Untertitel** — bleibt wie in Plan 0001 §11 zurückgestellt.
- **Musik-Lizenz-Nachweis** — **gestrichen.** Der ursprüngliche Gedanke war eine
  Nachweisführung für fremde Musik. Da die Musik selbst per KI erzeugt und damit nutzbar ist,
  gibt es nichts nachzuweisen. Auch in Plan 0001 §11 streichen.
- **Regie-Entscheidungen** für den 15-Minuten-Export (Tempo, Kapitelaufteilung, welcher Clip
  wohin, welche Musik) — gehören in `brief.yaml` und das Beat-Sheet.
- **Beschaffung des Materials** (Export aus iCloud, Material der Partnerin, Vorschnitt) — reine
  Nutzer-Vorarbeit außerhalb des Systems.
