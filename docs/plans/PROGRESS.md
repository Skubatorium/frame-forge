# Fortschritt

**M0–M4 plus Gesichtserkennung (M-Extra) sind fertig (2026-07-27), gefolgt von einem
vollständigen Audit mit umgesetzten Fixes (Abschnitt „Audit-Fixes" unten).** Offen bleibt laut
Plan nur noch M5 (Norwegen-Realbetrieb, kein Code-Meilenstein — echtes Material statt
Test-Fixtures) und, auf Nutzerwunsch zurückgestellt, automatische Untertitel und
Musik-Lizenz-Nachweis aus Plan §11.

Diese Datei ist die **einzige verlässliche Quelle** für den Arbeitsstand. Chat-Verläufe und
Task-Listen überleben ein Session-Limit nicht, diese Datei schon.

Regel: Nach jedem abgeschlossenen Task wird hier abgehakt **und** committet. Wer eine Session
neu startet, liest zuerst diese Datei und macht beim ersten offenen Task weiter.

Plan-Referenz: `docs/plans/0001-initial-structure.md`
Umgebungs-Fallstricke: `docs/plans/HANDOVER.md`

---

## Status

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1 | Repo-Fundament: git init, pyproject, gitignore, venv, Systemtools | ✅ fertig | — |
| 2 | Kern-Module: `state.py`, `project.py`, `timeline.py` | ✅ fertig | `2a2a3d0` |
| 3 | CLI (`cli.py`) + restliche Modul-Stubs | ✅ fertig | `51eda74` |
| 4 | Gate-Hook `.claude/hooks/gate.py` + `settings.json` | ✅ fertig | `ea9190a` |
| 5 | 8 Agenten + 9 Slash-Commands | ✅ fertig | `db3d2b0` |
| 6 | Docs: `CLAUDE.md`, `process.md`, `style-catalog.md`, `README.md`, Templates | ✅ fertig | `a206a81` |
| 7 | Tests + M0-Abnahme | ✅ fertig | `ccc9912` |

Legende: ⬜ offen · 🔄 in Arbeit · ✅ fertig

---

## Plan 0003 — Ausbau „Roadtrip-Vlog" (Arbeitspakete A–I)

Plan-Referenz: `docs/plans/0003-vlog-ausbau.md` (**ersetzt 0002**, das nicht umgesetzt wird).
Harte Bedingung bei **jedem** Paket: Abschnitt 0 des Plans — `projects/norwegen-2026` (255
indizierte Assets) muss ohne Neu-Indizierung weiterlaufen, neue Felder sind optional, neue
Defaults ergeben das heutige Verhalten, `projects/proto/` und die Timeline von
`test-timelapse-journey` bleiben lauffähig.

Reihenfolge laut Plan: E → A0 → A1/A2 → A3/A4 → A5/A6 → B; C, D, F, G, H unabhängig; I zuletzt.

| # | Arbeitspaket | Status | Commit |
|---|------|--------|--------|
| E | `relink` — Pfade nach Umsortieren reparieren | ✅ fertig | `4eb7b94` |
| A0 | Backfill statt Neu-Indizieren (`backfill-metadata`) | ✅ fertig | `e6859f0` + `b9a5ca2` |
| A1 | Aufnahmezeit für Videos (Container/Dateiname/Trim-Offset) | ✅ fertig | `b9a5ca2` |
| A2 | GPS aus den ungeschnittenen Originalen (`originals_root`) | 🔄 Code fertig, Stichprobe am Material offen | `4ea2fe3` |
| A3 | Etappen als Projektdaten (`route/stages.csv`, `templates/prompts/route.md`) | ✅ fertig | `c91232e` |
| A4 | `assign-places` — Tag/Etappe/Ort zuordnen (prüfbar, `--dry-run`) | ✅ fertig (Code), Realdaten fehlen | `243dc8a` |
| A5 | `places-todo` / `set-place` — Lückenliste für unklare Clips | ✅ fertig | `243dc8a` |
| A6 | `/ff-route` + Agent `route-planner` (Plausibilität) | ✅ fertig | `4138e99` |
| B1 | Distanz + Höhenprofil (`haversine_km`, `cumulative_km`, `elevation_profile`) | ✅ fertig | `4138e99` |
| B2 | Mitwandernder Viewport (Web-Mercator, `viewport="follow"`, `dwell_s`) | ✅ fertig | `a314f07` |
| B3 | Etappen-HUD (`templates/svg/map-hud.svg`, stufenweise gerendert) | ✅ fertig | `a314f07` |
| B4 | `map-animator`-Agent erweitern | ✅ fertig | `a314f07` |
| B5 | Routengeometrie beschaffen (GPX / KML-Parser / Routing-Fallback) | ✅ fertig | `4138e99` |
| C | Schwarzblende zwischen zwei Clips (`transition_in: black`) | ✅ fertig | `15c6510` |
| D1 | SVG-Templates aufwerten + relative Größen (`type_scale`) | ✅ fertig | `a314f07` |
| D2 | Generierte Grafiken (Prompt-Bausteine, Hintergrund in Titel/Kapitel) | ✅ fertig | `d07168d` |
| F | Musik: `fade_in_s`/`fade_out_s`, `audio.segment_plan` | ✅ fertig | `450d3ac` |
| G | Invalidierung bei neuem Material (`pipeline.pending_assets`, Fingerprint) | ✅ fertig | `7b746bc` |
| H1 | Farbstatistik messen (`analyze.color_stats` aus vorhandenen Keyframes) | ✅ fertig | `7f86f65` |
| H2 | Farbangleichung (`render.match_filter`, `color_match: off/soft/strong`) | ✅ fertig | `7f86f65` |
| I | Abschluss-Audit (I1–I4 fertig, I5 braucht Nutzer) | 🔄 | `1917325` |

---

## Arbeitspaket HEIC-Unterstützung (2026-08-05)

| # | Schritt | Status | Commit |
|---|------|--------|--------|
| HEIC-1 | ffmpeg-Fähigkeit prüfen (entscheidet den Renderpfad) | ✅ fertig | `8636201` |
| HEIC-2 | `pillow-heif` als Abhängigkeit, HEIF-Opener **einmal** zentral registrieren | ✅ fertig | `658da4d` |
| HEIC-3 | Neues Modul `frameforge/imageio.py`, `analyze`/`keyframes` gehen darüber | ✅ fertig | `658da4d` |
| HEIC-4 | Renderpfad: JPEG-Proxy für HEIC, `render_final` zeigt darauf | ✅ fertig | `658da4d` |
| HEIC-5 | `.dng` — entfernen oder klare Fehlermeldung statt stillem Scheitern | ✅ fertig | `658da4d` |

**Ausgangslage.** `.heic` steht in `ingest.PHOTO_EXTENSIONS`, aber weder Pillow (kein
`pillow-heif` in den Abhängigkeiten) noch OpenCV können HEIC lesen —
`cv2.imread` liefert `None`, `Image.open` wirft `UnidentifiedImageError`. Damit werfen
`keyframes.extract_keyframes` und `analyze.analyze_photo`, `preindex.prepare_index` fängt den
Fehler pro Datei ab, und HEIC-Fotos **verschwinden still aus dem Index**, ohne dass der Lauf
fehlschlägt. Im Fundus stehen 670 HEIC-Dateien an
(`…/2026_Norwegen/01_Rohmaterial/Chris-iPhone/`), im aktuellen `media_root` noch keine.

### HEIC-1 — ffmpeg kann HEIC **nicht** im Foto-Renderpfad verwenden (2026-08-05)

Lokal installiert ist **ffmpeg 8.1.2**. Der naheliegende Test ist irreführend und wurde
verworfen:

```
ffmpeg -demuxers | grep -i heif   →  kein Treffer
```

Daraus folgt **nicht**, dass ffmpeg die Dateien nicht anfassen kann: HEIF ist ISOBMFF, also
greift der `mov,mp4,m4a,3gp,3g2,mj2`-Demuxer, und der `hevc`-Decoder ist vorhanden. Ein
`ffmpeg -i IMG_9323.HEIC -frames:v 1 …` läuft mit Exit 0 durch. Entschieden wurde deshalb am
**echten Renderpfad**, nicht an der Demuxer-Liste.

Zwei Befunde an echten Dateien des Nutzers, die den Renderpfad ausschließen:

1. **`-loop` existiert auf diesem Demuxer nicht.** `render.build_filtergraph` baut für Fotos
   `-loop 1 -framerate <fps> -i <datei>` (Standbild auf Clipdauer ziehen). Gegen ein echtes
   HEIC:

   ```
   Option loop not found.
   Error opening input file …/IMG_0002.HEIC
   rc = 8
   ```

   `-loop` ist eine Option des `image2`-Demuxers; über `mov` ist sie nicht verfügbar. Ohne
   HEIF-Demuxer gibt es für Fotos also keinen Standbild-Input.
2. **Die Stream-Auswahl ist nicht verlässlich.** `ffprobe` meldet je HEIC **118 hevc-Streams**
   (Kacheln 640×896, Thumbnails 512×512/416×312/1024×768, abgeleitete Bilder 2016×1512). Es gibt
   keinen Stream, der erkennbar „das Bild" ist; ffmpegs Default-Auswahl nimmt den größten und
   trifft damit eine Kachel oder ein Derivat, nicht zwingend das Vollbild. Selbst mit
   funktionierendem `-loop` wäre das kein reproduzierbarer Renderpfad.

**Konsequenz:** Schritt 4 des Arbeitspakets greift — `ingest.build_proxies` schreibt für HEIC
einen JPEG-Proxy statt 1:1 zu kopieren, und `render_final` zeigt für diese Assets auf den Proxy
statt aufs Original. Begründung der Abweichung vom Prinzip „Final rendert aus den Originalen"
siehe HEIC-4.

### HEIC-2/HEIC-3 — `frameforge/imageio.py` als einziger Standbild-Lesepfad (2026-08-05)

Neue Abhängigkeit `pillow-heif>=0.21`; der Opener wird **genau einmal** registriert, beim
Import von `frameforge/imageio.py`. Verstreut über `analyze`, `keyframes`, `people` und `map`
hinge die Lesbarkeit einer Datei sonst davon ab, welches Modul zufällig zuerst importiert wurde.

Zwei Funktionen, mehr braucht es nicht: `open_image(path) -> PIL.Image` und
`read_bgr(path) -> np.ndarray` (BGR-`uint8`, das Layout von OpenCV).
`analyze.analyze_photo` nutzt `read_bgr` statt `cv2.imread`, `keyframes.extract_keyframes`
nutzt `open_image` statt `Image.open`. **`cv2.imread` kann HEIC auch mit `pillow-heif` nicht** —
die Registrierung wirkt nur auf Pillow, der Weg muss also über Pillow und dann ins Array laufen.
Ein Test hält genau das fest (`cv2.imread(heic) is None`, `read_bgr(heic)` liefert das Bild).

**Bewusst ohne `ImageOps.exif_transpose`.** Die naheliegende Ergänzung wurde geprüft und
verworfen: `cv2.imread` hat die EXIF-Orientierung nie ausgewertet, ein Nachrüsten würde den
JPEG-Pfad ändern. Nötig ist es auch nicht — `pillow-heif` wendet die HEIF-Transformationsboxen
(`irot`/`imir`) beim Öffnen an. Über **alle 670** HEIC-Dateien des Fundus geprüft: Orientierung
durchweg 1, Hochformat-Größen liegen nativ vor (304× 5712×4284, 216× 4284×5712, …).

**Rückwärtskompatibilität belegt:** `read_bgr` liefert für alle 21 JPEG/PNG der Projekte
(19 in `norwegen-2026`, Fixtures) ein zu `cv2.imread` **bitgleiches** Array
(`np.array_equal`), als Test festgehalten.

### HEIC-4 — Abweichung: der Final-Render nutzt für HEIC den Proxy (2026-08-05)

`ingest.proxy_path` bildet HEIC auf `.jpg` ab; `build_proxies` setzt HEIC in **voller
Auflösung** nach JPEG um (q95) statt 1:1 zu kopieren. `render_final` löst HEIC-Assets auf
diesen Proxy auf — die **einzige** Stelle, an der der Final-Render nicht aus dem Original
rendert.

**Warum die Abweichung vertretbar ist:** Der Grund für das Prinzip ist Qualität — der
Video-Proxy ist auf 1080p heruntergerechnet und im 4K-Final unbrauchbar. Beim HEIC-Proxy
trifft das nicht zu: er hat dieselben Pixelmaße wie das Original (an echten Dateien belegt,
5712×4284 → 5712×4284) und ist bei q95 visuell verlustfrei. Er ist hier nicht „kleiner",
sondern schlicht „lesbar". Die Alternative wäre, HEIC-Fotos im Final gar nicht verwenden zu
können.

**Bewusst nicht zur Laufzeit entschieden.** Naheliegend wäre gewesen, ffmpeg beim Rendern nach
seiner HEIF-Fähigkeit zu fragen und nur im Negativfall auf den Proxy zu gehen. Damit hinge die
Eingabedatei eines Renders an der ffmpeg-Version der jeweiligen Maschine — dasselbe
`timeline.json` ergäbe unterschiedliche Renders. Reproduzierbarkeit ist das Kernversprechen
des Projekts, deshalb: HEIC geht **immer** über den Proxy, ohne Verzweigung. Der entsprechend
gebaute `probe.ffmpeg_supports_heif()` wurde wieder entfernt, statt als toter Zweig
stehenzubleiben (Befunde F3/F7).

Fehlt der Proxy, ist das ein benannter `RenderError` mit Handlungsanweisung
(`frameforge ingest <projekt>`), keine stille Notlösung aufs unlesbare Original.

### HEIC-5 — `.dng` bleibt in `PHOTO_EXTENSIONS`, scheitert aber benannt (2026-08-05)

Entscheidung: **nicht entfernen.** Die Endung zu streichen würde DNG-Dateien schon in
`scan_media` verschwinden lassen — auch das wäre still, nur eine Ebene früher, und genau das
Verhalten, das dieses Arbeitspaket abstellt. Stattdessen nennt `imageio._UNSUPPORTED_HINTS`
das Format beim Namen und die Meldung einen Ausweg (vorher nach JPEG/HEIC exportieren oder
einen RAW-Decoder wie `rawpy` ergänzen). Im Fundus des Nutzers kommt `.dng` nicht vor
(0 Treffer), ein RAW-Decoder wäre also Vorratshaltung ohne Anwendungsfall.

### HEIC — Abnahme (2026-08-05)

**Am echten Material, nicht an Fixtures.** Testprojekt über zwei echte HEIC aus
`…/01_Rohmaterial/Chris-iPhone/` (nach der Abnahme wieder entfernt):

- `ingest` → JPEG-Proxies in voller Auflösung (5712×4284, wie die Originale), 6,5 MB / 5,9 MB.
- `prepare-index` → 1 Keyframe je Foto als **JPEG** im Cache (768×576), Qualitätsmetriken
  gerechnet (`sharpness` 0.155 / 0.518, `exposure` 0.902 / 0.863), Eintrag in `assets.json`.
  Die Keyframes wurden angesehen, nicht nur gezählt: echte, richtig herum stehende Vollbilder.
- `backfill-metadata`: `captured_at` und GPS wurden aus den Einträgen **entfernt** und der
  Backfill neu gefahren — er liest beides aus demselben HEIC nach
  (`2026-07-18T18:39:09` / 54.7887, 9.4370, 2.2 m — Flensburg; `2026-07-27T14:20:11` /
  62.1024, 7.2056, 9.6 m — Geiranger), Quelle `exif`.

**Gegenprobe zum Renderpfad (Lehre aus Befund F8).** Der HEIC-Rendertest wurde gegen die
zurückgebaute Fassung laufen gelassen: er scheitert mit exakt dem Fehler, der am echten
Material gefunden wurde — `ffmpeg fehlgeschlagen: Option loop not found`. Der Test fängt also
wirklich den Bug und läuft nicht an ihm vorbei.

**Fehlerfall statt stillem Überspringen** (Abnahmekriterium): 6 Tests decken es ab, darunter
`test_prepare_index_reports_unreadable_asset_with_reason` — eine unlesbare Datei landet als
`PrepFailure` **mit Dateinamen** im Report, statt wortlos aus dem Index zu fallen.

**Neues Fixture** `tests/fixtures/photo.heic` (923 Bytes, erzeugt von
`tests/fixtures/generate.py`) — sonst hinge der HEIC-Pfad am privaten Fundus des Nutzers.
Bewusst ein Farbverlauf statt einer einfarbigen Fläche: bei Vollton wäre die Schärfe-Metrik
konstant 0 und ein Test darauf belegte nichts.

**Rückwärtskompatibilität (Plan 0003 §0):**
- `relink norwegen-2026 --dry-run` → **286 Assets unverändert**, 0 Änderungen, 0 Waisen;
  `relink proto --dry-run` → 5 unverändert.
- `projects/norwegen-2026/index/assets.json` vor/nach dem gesamten Arbeitspaket **byteweise
  identisch** (`diff` ohne Ausgabe).
- Keines der bestehenden Projekte enthält HEIC (`norwegen-2026`: 267 mp4 + 19 jpg, `proto`:
  3 mp4 + 2 jpg) — der neue Zweig in `render_final` wird für vorhandenes Material also nie
  betreten, der Filtergraph ist dort schon konstruktiv unverändert.
- Beide echten Timelines laden und bestehen `validate_semantics` (172 bzw. 5 Clips);
  `projects/proto/` real durch `ingest` → `preview` gefahren.
- **19 neue Tests, 546 gesamt grün** (vorher 527, per `git stash` gegengezählt), `ruff`
  sauber, `doctor` grün.

---

## Fundus-Erweiterung „Chris-iPhone" (2026-08-06) — **fertig**

689 neue Dateien aus `First-Selection/Chris-iPhone/` (27 GB): **539 HEIC + 150 MOV**
(iPhone, 4K60). Damit waechst `norwegen-2026` von 286 auf **975 Assets**.

| Schritt | Status |
|---|---|
| `ingest` — Proxies | ✅ 975/975 |
| `prepare-index` — Keyframes, CV, `captured_at`, GPS | ✅ 689/689, keine Fehlschlaege |
| Inhaltliche Sichtung (Beschreibung/Tags/Rating) | ✅ **689 von 689** |

**Der HEIC-Weg hat sich am echten Material bewaehrt.** Ohne das Arbeitspaket von 2026-08-05
waeren die 539 Fotos still aus dem Index gefallen. Aufnahmezeit liegt bei **allen 689** vor
(100 %), GPS bei 536 (78 % — die 153 ohne sind die Videos, iPhone-MOV tragen keine
auswertbaren Koordinaten).

**Der Zeitraum waechst an beiden Enden:** bisher 20.07.–31.07., jetzt **17.07.–04.08.**,
19 Reisetage. Neu dazu kommen Anreise (Verladen zu Hause, Fahrt NRW → Flensburg) und Abreise.
`route/stages.csv` deckt diese Tage noch nicht ab — vor `assign-places` ist `/ff-route`
faellig, sonst bleiben die neuen Tage ohne Etappe.

### Fortschritt der Sichtung

Chronologisch, Tag fuer Tag. **Alle 689 Chris-iPhone-Assets sind durchgesichtet, der
Fundus ist komplett.**

| Tag | Chris-iPhone-Assets | indiziert |
|---|---:|---|
| 2026-07-17 | 6 | ✅ 6 — Verladen zu Hause am Abend vor der Abreise |
| 2026-07-18 | 42 | ✅ 42 — Fahrt NRW → Flensburg (Aufbruch, Raststaette, Hamburger Hafen, Nord-Ostsee-Kanal, Ankunft) + Abend am Hafen: Blumenkaesten/Establisher, Restaurant "Gosch" (Essen, Kartenhaus-Spiel, Anstossen), Spaziergang am Hafensteg, Willkommenstafel B&B Hotel Flensburg |
| 2026-07-19 | 33 | ✅ 33 — Abreise vom Hotel, Faehrterminal Color Line, Ueberfahrt (Deck, Bordrestaurant, Brettspiel, Familienselfies), Ankunft bei Freunden/Familie: Pizzaessen, Kinder spielen, Fernsehen |
| 2026-07-20 | 45 | ✅ 45 — Huette/Ferienhaus: Terrasse, Panorama-Portraets, Wanderung (Moltebeeren, Blaubeeren, Weidenroeschen), Ruderboot-Ausflug auf Waldsee, Beerenpfluecken, Grillabend |
| 2026-07-21 | 15 | ✅ 15 — Badebucht mit Felsklippen (Establisher, Familienselfies, Kinder-Portraets), Sandstrand mit vielen Badegaesten, Aufbruch |
| 2026-07-22 | 19 | ✅ 19 — Ruhetag an der Huette: Videospiele, gemeinsames Grillessen mit grosser Gruppe, Kinder spielen/toben, Establisher der dunklen Holzhuette |
| 2026-07-23 | 39 | ✅ 39 — Ausflug zur Stabkirche Heddal (Establisher, Museum, Aexte-Vitrine, Rosemaling), Picknick auf Wiese, Fahrt am Fjord entlang, Wanderung mit Familienselfies, Uebernachtung in Grasdach-Huette (Zimmerschilder) |
| 2026-07-24 | 70 | ✅ 70 — Grosser Ausflugstag: Fjord-Aussichtspunkte (Stegastein-artig), Kreuzfahrtschiff-Hafen, Flaamsbana-Zugfahrt (Wasserfaelle, Tunnel, Serpentinen), Marktplatz, Ferienhaus-Siedlung am Fjord, Abenddaemmerung mit beleuchtetem Ausflugsschiff |
| 2026-07-25 | 106 | ✅ 106 — Camping-Huette am Aurlandsfjord (Fruehstueck, Abendessen), Bootsausflug mit Wasserfaellen und Faehren-Establishern, Elektro-Katamaran "Future of the Fjords" Flaam–Gudvangen (inkl. Kreuzfahrtschiff Artania am Kai), Wikingerdorf Gudvangen (Schwertkampf-Spiel, Bogenschiessen, Grassoden-Haeuser, Handwerksvorfuehrungen, Drachenboot-Nachbauten), Familienselfies auf dem Aussendeck |
| 2026-07-26 | 58 | ✅ 58 — Aufbruch von der Camping-Huette am Aurlandsfjord (Nachtaufnahmen), Faehre "Mannheller", Laerdalstunnel, Wanderung an einem Gletscherfluss, Bergpass mit vielen Wasserfaellen im Nebel, tuerkisfarbene Gletscherseen, Ankunft am Geirangerfjord: ausfuehrliche Portraet-/Familienselfie-Serie auf dem Balkon der Huette (Kaffee, Kuesse, Grimassen), Hafen mit Kreuzfahrtschiffen, Fossen Camping (Grasdach-Rezeption), kurze Wanderung zu altem Bergbauernhof mit Ziegen |
| 2026-07-27 | 61 | ✅ 61 — Geburtstag von Papa/Chris: festlich gedeckter Fruehstueckstisch mit Wimpelgirlande, Geschenken (Brettspiel "Brass: Birmingham"), Pop-up-Karte und Kerzenkuchen, anschliessend Wanderung zum Storsaeterfossen-Wasserfall (Metalltreppen am Wildbach), Ort Geiranger mit Marktplatz, Hafen und Kreuzfahrtschiffen, RIB-Schnellboot-Fjordtour mit Ausruestungsverleih, Familien-/Gruppenselfies auf dem Boot, Sieben-Schwestern-artige Wasserfaelle direkt am Fjord |
| 2026-07-28 | 78 | ✅ 78 — Abschied vom Geirangerfjord, Schlucht Gudbrandsjuvet (Cafe mit Zimtschnecken/Kuchen, Wasser-Steg-Park), Bergpass mit Berghuette im Nebel, spektakulaerer Trollstigen (Aussichtsplattform, Serpentinenstrasse aus der Vogelperspektive, Steinmaennchen, 'No Trolls beyond this point'-Schild), Ankunft am neuen Etappenziel bei Lom: Abendessen (Pizza), Stabkirche Lom mit Friedhof, tuerkisfarbener Fluss mit Bruecken, Bakeriet i Lom, Camping-Spielplatz (Trampolin, Schaukel) |
| 2026-07-29 | 15 | ✅ 15 — Abend in Lom: Angler faengt Fisch im tuerkisfarbenen Fluss, Stabkirche Lom in der Abenddaemmerung gespiegelt, streunende Katze, gruener Ford-Mustang-Oldtimer auf dem Campingplatz; am naechsten Tag Weiterfahrt zu neuer Huette am See (Fruehstueck, Ankunft, Reihe Camping-Huetten am spiegelglatten Wasser), Sonnenuntergang am Fluss, Abendessen (Lachs mit Zitrone) in der neuen Huette |
| 2026-07-30 | 10 | ✅ 10 — Rest des Tages an der neuen Huette am See: Jungen laufen ueber Wiese Richtung Wald, Kind watet/angelt im Fluss unter Holzbruecke, Kinder plantschen auf Kiesbank, Establisher der Holzbruecke, Familien-Pizzaessen am Flussufer bei Abendlicht, dramatischer Sonnenuntergang mit Wolken und Bruecken-Silhouette |
| 2026-07-31 | 15 | ✅ 15 — Wandertag/Ruhetag: Weidenroeschen-Nahaufnahme, Kanufahrt von Mutter und Kind auf See, Bruecke zur Huettensiedlung, Kind mit Tablet im Bett, Tischtennis und Bogenschiessen im Camping-Aktivbereich, Kinder-Portraets und -Aktion am Kiesufer eines Sees (Steine werfen), Selfie-Portraet am See |
| 2026-08-01 | 6 | ✅ 6 — Rennradfahrer auf Passstrasse (Fjell), Dungeon-Brettspielabend mit Familie (Jubel, Detailaufnahmen) |
| 2026-08-02 | 10 | ✅ 10 — Kind mit Kopfhoerern auf Sofa, Schweinebraten-Zubereitung/Tranchieren, Kinder im Wohnzimmer mit Panoramablick, grosses Familienessen, Kinder spielen Videospiel, weiterer Brettspielabend, Beginn Tuer-/Terrassen-Renovierung |
| 2026-08-03 | 20 | ✅ 20 — Rest der Renovierung, Cafeteria-Rast (Eis/Hotdogs), ausfuehrliche Angel-Session an Kuestenfelsen (Fang, Jubel, Establisher-Weitwinkel), Wanderung zur Bucht, Establisher tuerkisfarbene Meeresbucht, Innenaufnahme Treppe |
| 2026-08-04 | 18 | ✅ 18 — Rueckreise: Faehrterminal/-deck am fruehen Morgen, Fahrt im Gegenlicht, Familienselfie im Auto, Hund am Autofenster, Ueberfahrt mit Bordrestaurant (Eis, Fruehstueck, Lego-Bauen mit Jubel), Ankunftshafen Color Line, Routenkarte an Bord, naechtliche Ankunft zuhause mit beladenem Auto als Schlussbild |

**Abschluss (2026-08-07):** Beim Ziehen der Worklist fuer 2026-08-01 fiel per
Hash-Abgleich ein zuvor uebersehenes Asset vom 2026-07-25 auf (`IMG_9762.HEIC`, Blick vom
Achterdeck eines Fjord-Ausflugsschiffs) — nachtraeglich einzeln nachindiziert, die 106 in der
Zeile oben bleiben unveraendert (zaehlt separat). Damit sind alle **689/689**
Chris-iPhone-Assets durchgesichtet, der Gesamtfundus (975 Assets, alle Kameras) ist komplett
inhaltlich indiziert.

**Hinweis zur Zaehlung:** `689` ist die Gesamtzahl der neuen Chris-iPhone-Dateien (aus
`prepare-index`, Pfadpraefix `Chris-iPhone/`). Die Tagestabellen in `assets.json` zeigen pro
Kalendertag oft mehr Eintraege, weil der urspruengliche 286er-Bestand (andere Kameras, bereits
vollstaendig indiziert) dieselben Tage abdeckt — die Tabelle hier zaehlt nur die neuen
Chris-iPhone-Assets, nicht den Tages-Gesamtbestand.

**Selbstkontrolle nach 2026-07-18** (Auftrag: 5 Beschreibungen gegen Keyframes gegenpruefen):
`945bc1`, `e1f63e`, `833dc9`, `b0640a`, `af6f76` geprueft — alle halten, keine Korrektur noetig.

**Fehler bei 2026-07-19 gefunden und korrigiert:** im Block IMG_9372–9382 (7 Assets) griff jeder
`index-asset`-Aufruf auf den Hash des jeweils *naechsten* Fotos statt des gerade gesichteten
zu — Off-by-one beim Abtippen der Hash-Liste. Wurde beim Abschluss-Check bemerkt (Pfad vs.
Beschreibung stimmten nicht ueberein, z. B. Pizzafoto mit Faehr-Selfie-Text), alle 7 Eintraege
neu zugeordnet, dabei auch `IMG_9382` (war nie wirklich gesichtet) korrekt nachgetragen.
**Lehre:** nach jedem Block `assets.json` gegen die Pfad→Beschreibung-Zuordnung stichprobenartig
pruefen, nicht nur auf "indiziert"-Ausgabe vertrauen.

**2026-07-25 abgeschlossen:** Groesster Tag bisher, komplett in 3er-Bloecken durchgesichtet.
Ein Hash-Tippfehler bei `IMG_9868.MOV` (Ziffer `2a0` statt `220` mitten im Hash getippt) fuehrte
zu einem `index-asset`-Fehler, der sofort bei der Ausfuehrung auffiel (Prep-Datei nicht
gefunden) und direkt korrigiert wurde, bevor weitergemacht wurde — kein stiller Fehleintrag.
Mehrere Stichproben (nach je ca. 15-30 Assets) bestaetigten korrekte Pfad-Hash-Zuordnung.
Inhaltlich: Fjordausflug mit zwei Booten (kleinerer Sightseeing-Trip morgens, dann
Elektro-Katamaran "Future of the Fjords" Flaam–Gudvangen mit vielen Wasserfall-Cutaways), und
ausfuehrlicher Nachmittag im Wikingerdorf Gudvangen mit Aktivitäten fuer Kinder.

**2026-07-26 abgeschlossen, mit Off-by-one-Korrektur:** In drei separaten 3er-Bloecken (Items rund um IMG_9960/9964/9965/9967, IMG_9988/9990/9994/9995 und IMG_0016/0021/0022/0024) wurde die Beschreibung des jeweils ersten gesichteten Bildes versehentlich auf den Hash des *zweiten* Assets im Block geschrieben (statt des ersten) — derselbe Fehlermodus wie am 2026-07-19, diesmal aber mit einer zusaetzlichen Verkettung: das dadurch "uebersprungene" vierte Bild im naechsten Bloecken wurde nie tatsaechlich gesichtet, bekam aber trotzdem einen (falschen) Text zugewiesen. Beim Abschluss-Check (`assets.json`-Hashes gegen Worklist abgeglichen) fielen 3 fehlende Assets auf; alle betroffenen Bilder (insgesamt 9 Eintraege: 3 fehlende + 6 mit vertauschtem Text) wurden erneut einzeln gesichtet und korrekt zugeordnet. **Lehre:** nach jedem Batch nicht nur Stichproben pruefen, sondern die vollstaendige Hash-Liste der Worklist gegen `assets.json` abgleichen (`set(todo) - set(existing)`), das deckt fehlende Eintraege zuverlaessiger auf als visuelle Stichproben.

**2026-07-27 abgeschlossen:** Derselbe Off-by-one-Fehlermodus trat noch einmal auf (ein 3er-Block IMG_0088/0089/0091/0092, RIB-Bootstour), wurde diesmal aber sofort durch den Voll-Hash-Abgleich (siehe Lehre oben) gefunden und korrigiert, statt erst am Tagesende. Ab der zweiten Tageshaelfte wurde konsequent auf Einzelzuordnung mit Dateinamen-Kommentar pro `index-asset`-Aufruf umgestellt (`# IMG_XXXX -> hash-praefix`), das verhinderte weitere Vorfaelle. Inhaltlich: Geburtstag von Papa/Chris an der Camping-Huette in Geiranger (Fruehstueckstisch mit Dekoration, Geschenke, Kerzenkuchen), Vormittagswanderung zum Storsaeterfossen, Nachmittag im Ort Geiranger (Markt, Hafen, Katze), RIB-Schnellboot-Tour auf dem Fjord mit spektakulaeren Wasserfaellen direkt an der Felswand.

**2026-07-28 abgeschlossen:** Trotz Dateinamen-Kommentaren trat der Fehlermodus noch zweimal auf, diesmal als Kaskade ueber zwei aufeinanderfolgende 3er-Bloecke (IMG_0227-0230, dann IMG_0230-0235 erneut verschoben) — 7 Eintraege betroffen (1 fehlend, 6 mit vertauschtem Text, 1 nie gesichtetes Bild in der Kette). Ursache: der Dateinamen-Kommentar wurde vor dem Lesen der Bilder geschrieben, aber die Zuordnung von Bildinhalt zu Kommentar erfolgte danach aus dem Gedaechtnis und verschob sich. **Verbesserte Lehre:** den Hash-Abgleich (`set(todo) - set(existing)`) nicht erst nach 15-20 Assets, sondern nach *jedem* 3er-Block laufen lassen — das haette die Kaskade sofort beim ersten Block gestoppt, statt sie ueber zwei Bloecke akkumulieren zu lassen. Inhaltlich: Abschied vom Geirangerfjord, Schlucht Gudbrandsjuvet mit Cafe, nebelverhangener Trollstigen mit Aussichtsplattform, Ankunft bei der Stabkirche Lom.

**Arbeitsweise, die sich bewaehrt hat** (fuer die naechste Sitzung):

1. Offene Assets eines Tages aus den Prep-Dateien ziehen (`captured_at[:10]` filtern,
   nach `hash not in assets.json`), sortiert nach Zeit — der Tagesablauf erzaehlt die
   Geschichte und macht die Beschreibungen praeziser.
2. **Volle Hashes** holen: `index-asset` akzeptiert keine Kurzpraefixe.
3. Keyframes in Bloecken von 3 sichten. Bei Videos reicht der **mittlere** Keyframe
   (`kf01`/`kf02`); nur bei unklarem Inhalt weitere ansehen.
4. Pro Block ein `index-asset`-Aufruf je Asset, danach den Stand hier fortschreiben.

Rating-Massstab, wie bisher vergeben: 4 = traegt eine Szene (Establisher, emotionaler
Moment), 3 = brauchbares B-Roll/Detail, 2 = nur als Lueckenfueller (Stau, unruhige
Handaufnahme).

### Beobachtung: `source_guess` liegt bei iPhone-Videos daneben

Die provisorischen IDs der MOV-Dateien lauten `20260718-**camera**-…`, obwohl es
iPhone-Aufnahmen sind; das gesetzte Feld `source` ist korrekt `phone`. Die ID entsteht in
`preindex._provisional_id` aus `probe.guess_source`, das bei `IMG_*.MOV` keinen Hinweis
findet — dieselbe Klasse von Abweichung wie Audit-Punkt I2. **Kein Handlungsbedarf:** die ID
ist nur ein stabiler Schluessel, die inhaltliche Wahrheit steht in `source`. Ein Umbenennen
wuerde bestehende Referenzen brechen, der Nutzen waere kosmetisch.

### Hintergrund-Laeufe brechen ohne Meldung ab

Zweimal wurde ein im Hintergrund gestarteter Lauf beendet, ohne Ausgabe und ohne Fehler
(`ingest` nach ~55 min bei 882/975, `prepare-index` nach ~10 min bei 476/689). Beide Male
war die Ausgabedatei 0 Bytes. **Ursache ungeklaert** — ein Zeitlimit passt nicht zu den
unterschiedlichen Laufzeiten; naheliegend, aber unbelegt, ist Speicherdruck (`vm_stat` zeigte
~209 MB freie Seiten). Im **Vordergrund** lief derselbe Schritt jeweils durch.

Praktische Konsequenz, keine Codeaenderung noetig: `ingest` und `prepare-index` sind
idempotent und nehmen den Faden dort wieder auf, wo sie standen. Lange Laeufe daher besser im
Vordergrund starten oder nach einem Abbruch schlicht erneut anstossen.

## Audit Plan 0003 (2026-08-01, Opus)

Unabhängige Prüfung der Commits `b9a5ca2..ca596c5` gegen den Plan — Logik, Grenzfälle,
Rückwärtskompatibilität, Zusammenspiel, Testtiefe, Timing. Befunde und Fixes einzeln:

| # | Schwere | Befund | Status |
|---|---|---|---|
| F1 | kritisch | Ken-Burns vervielfachte die Renderdauer (`zoompan d=frames` → `frames²`) | ✅ `1d13e2a` |
| F2 | hoch | `assign-places` erfindet Orte über den GPX-Track ohne Zeittoleranz | ✅ `0f21d5e` |
| F3 | hoch | Dauer-Invariante nirgends geprüft, `black_transition_extra_s` ohne Aufrufer | ✅ `fa87597` |
| F4 | mittel | `color-match` verliert unbekannte Felder in `timeline.json` | ✅ `318d208` |
| F5 | mittel | Alte Token-Sets rendern nicht mehr (neue Pflicht-Tokens in `lower-third.svg`) | ✅ `805075c` |
| F6 | mittel | `render_hud_frames` stürzt bei leerem Track ab (`IndexError`) | ✅ `45df317` |
| F7 | niedrig | `total_ascent_m` ohne Aufrufer — Plan B1 „kumulierte Höhenmeter" fehlt im HUD | ✅ `6cddf04` |
| F8 | niedrig | HUD-/Template-Tests prüfen nur Anzahl/Existenz, keinen Inhalt | ✅ `c8948f3` |
| F9 | niedrig | `segment_plan`: letzter Titel ohne Ausblendung bei `gap_s=0` | ✅ `b6c8a36` |
| F10 | niedrig | `frameforge build` setzt `TIMELINE`, ohne `timeline.json` zu parsen | ✅ `4628f6a` |

**Geprüft und in Ordnung:** Defaults aller neuen Felder (`hold`, `fade_in_s`/`fade_out_s`,
`color_match`, `originals_root`, `viewport="fit"`, `require_time=True`) verhalten sich wie vor
Plan 0003; keine Doppelrechnung (`_dwell_schedule` in Karte und HUD ist bewusst dieselbe
Zeitbasis); `status` kostet mit `pending_assets` 1,3 s bei 255 Dateien.

### F1 — Ken-Burns vervielfachte die Renderdauer (2026-08-01)

`zoompan` hält **jeden Eingabeframe** `d` Ausgabeframes lang. Der Foto-Zweig erzeugt über
`trim=duration=…` bereits `dur*fps` Frames; mit `d={frames}` wurde daraus `frames²`:

```
Foto 1,0 s @ 25 fps mit kenburns:  soll = 2,00 s   ist = 25,96 s
dieselbe Timeline ohne kenburns:   soll = 2,00 s   ist =  2,00 s
```

`qc.validate` meldete „OK", und **es gab bereits einen End-to-End-Test**
(`test_render_crossfade_and_kenburns_end_to_end`) — der prüfte aber nur `probe_video(out)["w"]
== 320`, also die Breite, nie die Dauer. Genau der Testtyp aus Befund F8: er rannte durch den
Bug hindurch, ohne ihn zu sehen.

Fix: `d=1` (ein Ausgabeframe je Eingabeframe); der Zoom läuft weiterhin über `on` und damit über
die volle Clipdauer. Zwei Tests: Filtergraph-Assertion (`:d=1:`, kein `:d=50:`) und ein echter
Render, der die Dauer prüft; der bestehende E2E-Test hat die fehlende Dauer-Assertion bekommen.

Der Fehler stammt aus Ausbaustufe B1, nicht aus Plan 0003 — keine der beiden echten Timelines
nutzt `effects`, deshalb ist nie ein falsches Video entstanden. Kombinationsfall danach geprüft
(Schwarzblende + Crossfade + Ken-Burns + Audio-Fades in einer Timeline): `timeline.duration`
4,60 s, gerendert 4,60 s.

### F10 — `build` hob die Phase ohne Prüfung der Timeline (2026-08-02)

Der in G ergänzte Phasenaufstieg prüfte nur, ob `timeline.json` **existiert**. Eine kaputte
Datei (ungültiges JSON, oder ein Clip, der über die Timeline-Dauer hinausragt) führte damit zu
`TIMELINE` — der Status behauptete „fertig gebaut", der Fehler kam erst beim Preview.

Jetzt lädt `build` die Datei und ruft `validate_semantics()`, bevor die Phase steigt. Fehler
werden benannt, der Export bleibt `STORYBOARDED` (das Beat-Sheet ist ja da) und das Kommando
endet mit Exit 1. 1 Test über alle drei Fälle: kaputtes JSON, schema-gültig aber semantisch
falsch, repariert.

### F9 — Letzter Musiktitel endete hart (2026-08-02)

`segment_plan` setzte `fade_out_s = 0`, wenn der letzte Titel ohne geplante Stille endete — die
Musik brach am Filmende also unvermittelt ab. Die Asymmetrie war weder begründet noch
dokumentiert. Jetzt blendet **jeder** Titel aus; nur der Einsatz des ersten bleibt hart, weil
der Film ohnehin bei Null beginnt. Ein bewusst harter Schluss ist weiterhin möglich —
`fade_out_s` am Clip auf 0 setzen, wie im Docstring vermerkt.

2 neue Tests (alle Titel blenden aus, Blende überschreitet nie die Clip-Länge).

### F8 — Abnahme D war nur behauptet (2026-08-02)

Der Abnahmesatz aus Plan §D lautet „in 1080p und 2160p **optisch konsistent**". Geprüft wurde
davon nichts: der Test rendert beide Auflösungen und schaut nur, ob die Datei mit den
PNG-Magic-Bytes beginnt. Ein Template mit absoluten Pixelwerten hätte das genauso bestanden —
und genau diese Testsorte hat den Ken-Burns-Fehler (F1) durchgelassen.

Jetzt geprüft wird die **Bounding-Box des sichtbaren Inhalts in relativen Koordinaten**: sie
muss in 1080p und 2160p auf 2 % übereinstimmen. Dazu zwei weitere Regeln: nichts läuft über den
Bildrand hinaus (sonst ist Text im Film angeschnitten), und — als Gegenprobe — ein absichtlich
kaputtes Template mit festen Pixelwerten **fällt durch** die Prüfung. Ohne diese Gegenprobe
wüsste man nicht, ob der Test überhaupt etwas fangen kann.

Alle 7 Templates bestehen: die Auflösungsunabhängigkeit aus D1 ist damit belegt statt behauptet.
15 neue Tests (3 Regeln × 7 Templates parametrisiert, plus Gegenprobe).

### F7 — Kumulierte Höhenmeter fehlten im HUD (2026-08-02)

Plan 0003 §B1 nennt als HUD-Werte „aktuelle Höhe, kumulierte Höhenmeter aufwärts,
Etappenprofil". `gpx.total_ascent_m` war dafür geschrieben, hatte aber **keinen Aufrufer** —
das HUD zeigte nur die aktuelle Höhe. Jetzt rechnet `render_hud_frames` je Stufe die Höhenmeter
über den **bereits gefahrenen** Teil der Etappe (`heights[:index+1]`), sodass der Wert mitwächst,
und stellt ihn als `↑ 640 m` dar; ohne Anstieg bleibt die Angabe leer.

`ascent_label` ist ein **optionales** Token (wie `background_layer`) — ein neues Element im
Template darf bestehende Token-Sätze nicht ungültig machen. Genau diesen Fehler hätte der Fix
sonst wiederholt: die erste Fassung ließ drei Template-Tests scheitern, die mit fremden
Token-Sätzen rendern.

2 neue Tests: steigende vs. ebene Strecke ergeben unterschiedliche HUD-Bilder, und ein
Token-Satz ohne `ascent_label` rendert weiterhin.

### F6 — HUD stürzte ohne Trackpunkte ab (2026-08-02)

`render_hud_frames([])` warf `IndexError` (`km_at[index]` auf leerer Liste), `_dwell_schedule`
zusätzlich `ValueError` (`min(range(0))`), sobald POIs übergeben wurden. Eine Etappe ohne
aufgezeichnete Spur ist aber kein Fehlerfall — das HUD soll dann Tag und Etappe zeigen und den
Kilometerstand weglassen.

Fix: leerer Track liefert einen leeren `km_label` und überspringt die Haltezeit-Logik. Drei
Tests, darunter einer, der **Verhalten statt Existenz** prüft (Befund F8): der Kilometerstand
muss sich über die Stufen ändern und *innerhalb* einer Stufe identisch bleiben — genau die
Zusicherung „ein SVG-Rendering je `step_s`", die bisher nur behauptet war.

### F5 — Bestehende Token-Sätze scheiterten an den neuen Templates (2026-08-02)

Die in D1 aufgewertete `lower-third.svg` verlangte `corner_radius`, `shadow_dy`, `shadow_blur`,
`shadow_opacity`, `accent_width`, `title_tracking` und `subtitle_tracking`. Ein Projekt, dessen
Token-Satz vor Plan 0003 entstanden ist, bekam damit `TemplateError` — ein klarer Verstoß gegen
Plan §0 („neue Defaults ergeben das heutige Verhalten").

**Der Bruch war bei der Umsetzung sichtbar und wurde falsch behandelt:** der bestehende Test
`test_all_svg_templates_render_with_consistent_tokens` ist damals genau daran gescheitert, und
ich habe **den Test** auf `overlay_tokens` umgestellt, statt den Bruch zu beheben. Das hat den
Nachweis der Rückwärtskompatibilität an der einzigen Stelle entfernt, an der er stand.

Fix: `build_svg_from_tokens` **ergänzt** fehlende Layout-Tokens, statt sie einzufordern —
enthält das Token-Set `width`/`height`, werden die restlichen Layout-Werte über `overlay_tokens`
daraus abgeleitet. Werte des Aufrufers gewinnen immer; fehlende **Inhalts**-Tokens (`title` …)
bleiben ein Fehler.

Der umgestellte Test steht wieder in seiner ursprünglichen Form (handgeschriebene Pixelwerte).
Dazu neu: der wortgleiche Token-Satz aus Commit `79cb540` rendert **alle 7 Templates**
(parametrisiert), plus je ein Test für „Aufrufer-Wert gewinnt" und „fehlender Inhalts-Token
wirft weiterhin".

### F4 — Zurückschreiben verlor Felder in `timeline.json` (2026-08-01)

`frameforge color-match` ist das erste Kommando, das eine `timeline.json` **zurückschreibt**.
Weder `Timeline` noch die Clip-Modelle erlaubten Zusatzfelder (Pydantic-Default: unbekannte
Schlüssel werden still verworfen), also gingen sie beim Schreiben verloren:

```
top-level "notes" erhalten: False | clip-feld "kommentar" erhalten: False
```

Stiller Datenverlust in der Single Source of Truth — betrifft auch `Timeline.save`. Fix:
`extra="allow"` auf `Timeline`, `Tracks` und allen vier Clip-Modellen. Gegenüber vorher gibt es
keinen Nachteil: ein Tippfehler im Feldnamen wurde auch bisher nicht gemeldet, nur verworfen —
jetzt bleibt er wenigstens in der Datei stehen und fällt beim Lesen auf.

Am echten Material gegengeprüft: `test-timelapse-journey` (172 Clips) laden + speichern →
**kein Schlüssel verloren**. 2 neue Tests in `tests/test_timeline.py`.

### F3 — Dauer-Invariante und toter Code (2026-08-01)

`render.black_transition_extra_s` wurde für Paket C geschrieben und hatte **keinen Aufrufer** in
`frameforge/` — nur Tests. Damit war die Abnahme aus Plan §C („Gesamtdauer stimmt mit
`timeline.duration` überein") nur an einem Beispiel im Test belegt, nicht als Regel.

Neue QC-Regel `_check_video_length_consistency`: die **sequenzielle** Renderlänge der Video-Spur
(Summe der Clipdauern − Crossfades + Schwarzblenden-Standzeiten) muss dort enden, wo der letzte
Clip laut `tl_in` endet. Die Einzelprüfungen decken jeden Übergang für sich ab; diese Regel ist
die Gesamtsumme und fängt auch aufaddierte Abweichungen mehrerer Übergangstypen.

**Erster Entwurf war zu streng und wurde verworfen:** er verglich gegen `timeline.duration` und
hätte 9 bestehende Tests sowie den legitimen Fall „Musik läuft nach dem letzten Bild weiter"
gebrochen. Empirisch geprüft: Timeline mit 1 s Bild und 4 s Musik rendert 4,0 s — der Ausklang
ist gewollt, nicht kaputt. Zu *kurz* deklarierte Dauern fängt weiterhin
`Timeline.validate_semantics`.

4 neue Tests (gemischte Übergänge korrekt/verschoben, Musik-Ausklang, leere Video-Spur). Beide
echten Timelines (`proto/teaser`, `test-timelapse-journey`) bestehen die Regel unverändert.

### F2 — GPX-Position ohne Zeittoleranz (2026-08-01)

`_place_for` nahm den zeitlich nächsten Trackpunkt als Position — ohne jede Grenze.
`gpx.nearest_location` dokumentiert ausdrücklich, dass die Toleranz Sache des Aufrufers ist;
gesetzt hat sie niemand:

```
Asset vom 01.01., Track nur vom 28.07.  →  ('Trollstigen', 'gpx')
```

Der Ort sah belastbar aus (`place_source: gpx`), tauchte **nicht** in `places-todo` auf und war
trotzdem geraten — genau das, was Plan 0003 („nie raten") und Paket A5 verhindern sollen. Bei
255 Assets ohne eigenes GPS wäre das der Normalfall gewesen, nicht die Ausnahme.

Fix: `DEFAULT_GPX_TOLERANCE_S = 1800` (30 Minuten, deckt Standzeiten und Aufnahmepausen ab,
ohne über eine Fahretappe hinwegzugehen), konfigurierbar über
`assign-places --gpx-tolerance-min`. Außerhalb der Toleranz bleibt es bei `unknown` und das
Asset landet in der Lückenliste.

Nebenbei gefunden: `gpx.nearest_location` warf `TypeError`, sobald ein Trackpunkt keine Zeit
trug. Vor Plan 0003 unmöglich (`parse_gpx` filterte zeitlose Punkte immer heraus), seit
`require_time=False` (B5) erreichbar. Jetzt werden zeitlose Punkte übersprungen; `None` ist die
richtige Antwort, kein Absturz.

4 neue Tests in `tests/test_places.py`, 1 in `tests/test_gpx.py`.

### E — Notizen (2026-08-01)

Neues Modul `frameforge/relink.py` + Kommando `frameforge relink <projekt> [--dry-run]`.
`plan_relink` rechnet nur (kein Schreiben), `apply_relink` schreibt — so treffen `--dry-run`
und der echte Lauf garantiert dieselbe Entscheidung.

Entscheidungslogik pro Asset, in dieser Reihenfolge:

1. **Eingetragener Pfad existiert → unverändert**, bewusst *ohne* Hash-Vergleich. Beim ersten
   Lauf gegen `projects/proto/` meldete die hash-first-Variante alle 5 Assets als Waisen *und*
   dieselben 5 Dateien als „neu": `hash_file` nimmt `mtime` mit auf (Plan 0001 §3), ein
   git-Checkout ändert sie. Relink repariert **Pfade, nicht Hashes** — ein existierender Pfad
   ist nie ein Waise.
2. Pfad weg → Suche per Hash. Genau ein Treffer → `path` korrigieren. Mehrere Treffer
   (echte Duplikate) → als `ambiguous` melden, **nichts raten**. Kein Treffer → Waise (Eintrag
   bleibt stehen, relink löscht nie).
3. Dateien, deren Hash in keinem Asset vorkommt → als „neu, noch nicht indiziert" melden.

`media_root` nicht erreichbar (Platte nicht gemountet) wirft `FileNotFoundError`, statt jedes
Asset als Waise zu melden.

**Abweichung vom Plan (auf Nutzer-Entscheidung, Frage vorab gestellt): Proxies wandern mit.**
`ingest.proxy_path` hängt den Hash des *relativen Pfads* an den Proxy-Namen (Audit-Fix K1) —
nach einem Verschieben wäre der vorhandene Proxy verwaist und würde beim nächsten `ingest` neu
transkodiert. Bei ~100 GB ist das der teuerste Schritt der Pipeline, deshalb benennt
`apply_relink` den Proxy im Cache mit um (`_move_proxy`, meldet `moved_proxies`). Fehlt der
Proxy oder existiert das Ziel schon, passiert nichts — kein Fehler.

Nebenbei `index.py` refaktoriert (kein Verhaltenswechsel): `save_assets` (ganze Liste, sortiert)
und `write_asset_md` (Notizen-Merge) als öffentliche Bausteine herausgezogen, `write_asset` nutzt
beide. Relink schreibt `assets.json` damit genau einmal statt einmal pro geändertem Asset.

**Abnahme E erfüllt:** 13 Tests in `tests/test_relink.py`, darunter der End-to-End-Nachweis
(`test_final_render_finds_original_after_relink`): verschobenes Original → `render_final` bricht
mit „Original-Asset nicht gefunden" ab → nach `relink` läuft derselbe Render durch. Weiter
abgedeckt: nur `path` ändert sich (Diff-Vergleich aller übrigen Felder), Freitext-Notizen in der
`.md` bleiben, Waisen/Neu/Mehrdeutig, Proxy-Umzug, mtime-Änderung ist kein Waise.

**Rückwärtskompatibilität (Plan 0003 §0) nachgewiesen:** `relink norwegen-2026 --dry-run` meldet
255 Assets unverändert, 0 Änderungen, 0 Waisen; `relink proto --dry-run` 5 unverändert.
`projects/proto/` läuft weiterhin bis zum Preview durch (`ingest` → `preview` real ausgeführt).
326 Tests grün, `ruff` sauber, `doctor` grün.

### A0 — Notizen (2026-08-01)

Neues Modul `frameforge/backfill.py` + Kommando `frameforge backfill-metadata <projekt>
[--dry-run]`. Gleiche Bauart wie E: `plan_backfill` probt und rechnet, `apply_backfill` schreibt.

**Positivliste statt Ausschlussliste.** `_TECH_FIELDS` nennt die einzigen beschreibbaren Felder
(`captured_at`, `captured_at_source`, `duration`, `probe`, `gps.lat/lon/elevation_m`);
`apply_backfill` wirft, wenn ein Update auf ein anderes Feld zeigt. Damit ist „`content`,
`rating`, `source`, `gps.place` bleiben unangetastet" nicht nur Absicht, sondern erzwungen.
`.md`-Freitext bleibt über `index.write_asset_md` erhalten.

`probe_photo_exif` liefert jetzt zusätzlich `gps.elevation_m` (GPSAltitude, inkl.
`"… m Below Sea Level"`) — gehört zu den in Plan 0003 §A0 genannten technischen Feldern.

**Realer Lauf gegen `norwegen-2026` (255 Assets):** 56 Assets ergänzt, Diff enthält
ausschließlich technische Felder — `probe` (37), `captured_at_source` (19), `gps` (19).
`content`, `rating`, `source`, `hash`, `path` und `gps.place` sind bei allen 255 Assets bitgleich
zu vorher (per Skript verglichen, nicht behauptet). Kein Vision-Call.

**Nebenbefund, deckt Plan-Punkt I2 teilweise auf:** bei 37 Videos stand `probe.source_guess:
"camera"`, obwohl der Dateiname mit `DJI_…` beginnt. Ursache ist nicht `guess_source`, sondern
das Alter der Einträge — sie wurden indiziert, bevor `guess_source` den `name_hint` (Dateiname)
auswertete. Der Backfill korrigiert genau das. `asset["source"]` (vom media-indexer gesetzt)
bleibt davon unberührt.

**Abnahme A0 zunächst nur zur Hälfte erfüllt** (Bitgleichheit ja, Aufnahmezeit 0/236) — die
zweite Hälfte kam mit A1, siehe dort: der zweite Backfill-Lauf liefert 236/236 (100 %).
7 Tests in `tests/test_backfill.py`, 333 Tests gesamt grün, `ruff` sauber.

### I — Abschluss-Audit (2026-08-01)

**I1 Konsistenz.** Alle neuen Felder sind durchgezogen: dokumentiert in Plan 0001 §4
(`captured_at_source`, `gps.elevation_m`, `gps.source`, `day`, `stage`, `place_source`,
`color_stats`), berücksichtigt in `qc.validate` (Schwarzblenden-Timing), abgebildet im
NLE-Export (`color_match` und `transition_in` wandern als Clip-Metadaten mit — vorher nur im
Renderer sichtbar), sichtbar in `stats`/`report`: Tageszusammenfassungen zeigen Reisetag und
Etappe, das Export-Datenblatt zeigt Farbangleichung (Anzahl + maximale Auslenkung) und
Schwarzblenden.

**I2 Datenprüfung am Fundus — geklärt und korrigiert.** Zwei getrennte Ursachen:
1. `probe.source_guess` stand bei 37 Videos auf `camera`, obwohl der Dateiname mit `DJI_`
   beginnt. Kein Fehler in `guess_source`: die Einträge stammen aus der Zeit **vor** dem
   `name_hint`. Der Backfill (A0) hat sie korrigiert — jetzt 255/255 `drone`.
2. `asset["source"]` (vom `media-indexer` gesetzt, nicht geraten) war bei **4** Assets falsch:
   3 Videos als `camera` und ein DJI-Foto (EXIF `Make: DJI FC9589`) als `phone`. Neues
   Kommando `frameforge set-source <projekt> <asset-id> <quelle>` korrigiert so etwas ohne
   Neu-Indizierung; die vier sind korrigiert. **Die 18 Fotos mit `source: drone` sind kein
   Fehler** — es sind echte Drohnenfotos (EXIF `DJI FC9589`), die ursprüngliche Vermutung im
   Plan („auch bei Fotos?") war unbegründet.

**I3 Rückwärtskompatibilität nachgewiesen.**
- `projects/proto/` komplett end-to-end über die echte CLI: `ingest → preview → approve →
  render → nle` — alles grün, inklusive Final-Render und Datenblatt.
- Für `test-timelapse-journey` (2,6 GB 4K-Final) wurde **nicht** neu gerendert, sondern das
  verglichen, was die Ausgabebytes bestimmt: der komplette **Filtergraph** (Inputliste +
  `filter_complex`, 55 KB) aus dem Stand **vor** Plan 0003 (Commit `79cb540`, über ein
  git-Worktree) gegen den heutigen — **byteweise identisch**. Gleiche Inputs plus gleicher
  Filtergraph plus gleiche Encoder-Settings ergeben dieselbe Datei; ein 46-Minuten-Re-Render
  hätte dieselbe Aussage teurer geliefert. Die bestehende `timeline.json` lädt unverändert ins
  erweiterte Schema (alle neuen Felder haben Defaults).

**I4 Regression:** 455 Tests grün, `ruff` sauber, `doctor` grün.

**I5 offen — braucht den Nutzer.** Der 60-Sekunden-Beispiel-Preview mit Karte, HUD,
Höhenprofil, Schwarzblende, neuer Bauchbinde und Farbangleichung setzt `route/stages.csv` und
`route/locations.csv` voraus (Etappen dürfen nicht geraten werden, Plan 0003 §A3/§A6) —
und die visuelle Abnahme ist ohnehin Sache des Nutzers. Nächster Schritt: `/ff-route
norwegen-2026`.

### D2 — Notizen (2026-08-01)

Kein neuer Code nötig — die Infrastruktur (`design/prompts.md`, `design.asset_inventory`,
`frameforge design-status`) stand bereits. Ergänzt wurde:

- **Prompt-Bausteine** in `templates/prompts/graphics.md` für die neuen Typen:
  Titelkarten-Hintergrund, Kapitelmarke, Landes-/Regionsmotiv, Karten-Rahmen,
  Fahrzeug-/Positions-Icon — jeweils mit der Regel, die Textzone ruhig zu halten, und dem
  Hinweis, Bitmaps in Zielauflösung zu liefern (Text skaliert relativ, Bitmaps nicht).
- **Hintergrundgrafik** in `title-card.svg`/`chapter.svg` über `design.background_layer`
  (in D1 gebaut) — optional, bestehende Token-Sets bleiben gültig.
- Der `design-system`-Agent **schlägt jetzt aktiv vor**, welche Grafiken einen Export aufwerten
  würden (max. 3–4, immer als optional gekennzeichnet), und nutzt `overlay_tokens` statt
  handgeschriebener Pixelwerte.

Das Erzeugen der Bilder bleibt bewusst außerhalb des Codes (Leitprinzip: keine
projektspezifische Gestaltung in `frameforge/`).

### H1/H2 — Notizen (2026-08-01)

**H1 messen (kostenlos).** `analyze.color_stats(frames)` liest die **bereits vorhandenen**
Keyframe-JPEGs: Mittelwert/Streuung je Kanal, Luma und ein Farbtemperatur-Indikator
`(mean_r - mean_b) / 255`. Kein neues Decoding, kein Vision-Call. Der Backfill (A0) trägt das
Feld nach, ohne bestehende Werte zu überschreiben.

**H2 angleichen.** `render.reference_stats` bildet den **Median** über die im Export
verwendeten Clips (nicht über den Fundus — ein Export ist die relevante Einheit; Median statt
Mittelwert, damit ein einzelner Nachtclip die Referenz nicht wegzieht).
`render.color_match_for` erzeugt daraus je Clip milde, **gedeckelte** Werte
(`COLOR_MATCH_LIMITS`: soft ±0.08 Helligkeit / ±0.15 Sättigung / ±0.08 Temperatur, strong das
Doppelte, off gar nichts). `render.match_filter` setzt sie als `eq`+`colorbalance` **vor** dem
Stil-Grade in die Clip-Kette — ein Test prüft genau diese Reihenfolge, denn andersherum wäre
„kühl" eine Aussage über die Kameramischung statt über den Film.

**Die Werte stehen pro Clip in `timeline.json`** (`VideoClip.color_match`), nicht als versteckte
Renderer-Magie: `frameforge color-match <projekt> <export> [--strength off|soft|strong]`
schreibt sie, der Brief steuert den Default (`color_match: soft`). Damit sind sie
nachvollziehbar, von Hand überschreibbar, reproduzierbar und gehen in den NLE-Export mit.

**Realer Lauf gegen `norwegen-2026`:** Backfill ergänzt `color_stats` für alle 255 Assets
(kein Vision-Call). Referenz-Luma 107.8, Referenz-Temperatur 0.0; die berechneten Korrekturen
liegen zwischen −0.08 und +0.08 (Deckel), Median 0.0 — die Masse des Materials wird also kaum
angefasst, nur die Ausreißer. Der visuelle Vergleich am Testschnitt gehört zu I5.

14 neue Tests, 452 gesamt grün.

### G — Notizen (2026-08-01)

Schließt die seit 2026-07-31 dokumentierte Lücke (Plan 0001 §2: neues Material soll auffallen).

- `pipeline.pending_assets(project)` — `scan_media` gegen die Hashes in `assets.json`, kein
  Vision-Call, keine Zustandsänderung; läuft deshalb in `frameforge status` **in jeder Phase**
  mit. Ein nicht gemounteter Datenträger liefert bewusst eine leere Liste statt „alles neu".
- `pipeline.asset_inventory_fingerprint` hasht **IDs + Hashes**, nicht die Bytes von
  `assets.json`. Sonst hätte jeder Backfill (A0) und jede Ortszuordnung (A4) eine Warnung
  ausgelöst, obwohl sich am Inventar nichts geändert hat — die Warnung wäre binnen eines Tages
  Rauschen gewesen.
- `pipeline.asset_drift` vergleicht den beim Storyboarding abgelegten Fingerprint mit dem
  aktuellen und liefert eine **Meldung**, keine Aktion: `status`, `preview` und `render` zeigen
  sie an, gebaut wird nichts von selbst (Plan: „warnen und fragen, nicht still neu bauen").

**Dafür musste `frameforge build` erstmals eine Phase setzen.** Bisher war es ein reiner
Gate-Wrapper, der immer mit Exit 1 endete — kein Kommando erreichte je `STORYBOARDED` oder
`TIMELINE`, also gab es auch keinen Zeitpunkt, an dem sich der Inventarstand festhalten ließ.
Jetzt: Beat-Sheet vorhanden → `STORYBOARDED` + Fingerprint, zusätzlich `timeline.json`
vorhanden → `TIMELINE`. Ohne Beat-Sheet bleibt es beim bisherigen Hinweis samt Exit 1.

7 neue Tests, 438 gesamt grün.

### F — Notizen (2026-08-01)

`AudioClip.fade_in_s`/`fade_out_s` (Default 0 → bestehende Timelines unverändert);
`render.build_filtergraph` setzt `afade` **vor** `adelay`, weil `afade` in Clip-Zeit rechnet und
nicht in Timeline-Zeit — hinter `adelay` läge die Blende um `tl_in` verschoben.

`audio.segment_plan(tracks, sections, gap_s=…, crossfade_s=…)` verteilt n Titel 1:1 auf n
Kapitel und liefert fertige `AudioClip`-Dicts. Der Ausklang wird über `nearest_beat` auf den
nächstgelegenen Beat **des jeweiligen Titels** gezogen (eine Blende mitten im Takt hört man
sofort), `gap_s` erzeugt echte Stille. Ein Titel, der kürzer ist als sein Kapitel, wird
**nicht** geloopt oder gestreckt — das ist eine Regie-Entscheidung des `audio-designer`, keine
Rechenoperation. Ebenso bewusst keine Stilanalyse („passen die Titel zusammen").

10 neue Tests, darunter ein echter Render mit Ein-/Ausblendung und ein Regressionstest, dass
ohne Blenden kein einziger `afade` im Filtergraph steht.

### C — Notizen (2026-08-01)

Neuer Übergangstyp `black` mit optionaler Standzeit (`Transition.hold`, Default 0 → alle
bestehenden Timelines unverändert). `_join_video_segments` behandelt ihn als dritte Variante
neben `concat` und `xfade`: `fade=t=out:color=black` auf dem vorigen Clip, optional
`tpad=stop_duration=<hold>:stop_mode=add:color=black` als echte schwarze Frames,
`fade=t=in:color=black` auf dem nächsten, dann `concat`. Bewusst **kein** `xfade` — hier blendet
nichts ineinander.

**Timing-Invariante umgekehrt:** `xfade` *verkürzt* die Timeline, `black` *verlängert* sie um
`dur + hold`. `render.black_transition_extra_s` rechnet das aus, und `qc._check_video_coverage`
prüft die passende Regel: der Folgeclip muss um exakt die Standzeit später beginnen. Ohne diese
Regel wäre die Lücke als Fehler gemeldet worden — und mit falschem `tl_in` liefen Audio und
Overlays weg.

**Abnahme C nachgewiesen:** echter Render (`render_proxy`) einer Timeline mit
`transition_in: {type: black, dur: 0.3, hold: 1.0}` in der Mitte → Gesamtdauer 3.0 s wie
erwartet (2× 1 s Material + 1 s Schwarz), und ein bei 1.5 s extrahierter Frame ist mit
Maximalhelligkeit < 16 praktisch schwarz. Regressionstest: eine Timeline ohne `black` erzeugt
weiterhin exakt `concat` ohne jeden `fade`-Filter. Beim ersten Lauf einen echten Syntaxfehler
gefunden (`tpad:` statt `tpad=`), den nur der Render — nicht die String-Tests — zeigt.

8 neue Tests, 426 gesamt grün.

### B2 + B3 + B4 + D1 — Notizen (2026-08-01)

**B2 Follow-Viewport.** `map.latlon_to_pixel`/`pixel_to_latlon` (Web-Mercator, subpixelgenau —
`latlon_to_tile` ist genau das abgerundet; ein Test hält diese Beziehung fest, weil davon
abhängt, ob Kachelkarte und Route deckungsgleich sind). `render_route_frames` bekommt
`viewport="follow"`, `zoom`, `ease_s`, `dwell_s`, `tile_cache_dir`; `smooth_centers` glättet die
Kamerafahrt über ein gleitendes Fenster. `basemap_viewport` schneidet beliebige Pixelgrößen aus
dem Kachel-Cache (die „nur ganze 256er-Raster"-Beschränkung von `render_basemap` gilt nur noch
für den Fit-Modus) und behandelt Datumsgrenze und Pol.

**Haltezeit ohne Zeitdehnung:** `_dwell_schedule` pausiert den Reveal an jedem POI, verkürzt
dafür die Bewegung dazwischen — `dur` bleibt exakt. Sonst wäre jede Timeline-Position hinter
dem Karten-Clip verrutscht.

**Regression:** `viewport="fit"` ist Default; ein Test rendert dieselbe Szene einmal ohne und
einmal mit den neuen Parametern und vergleicht die PNGs **byteweise**.

**B3 HUD.** `templates/svg/map-hud.svg` + `map.render_hud_frames`: ein SVG→PNG je `step_s`
(Default 1 s) statt pro Frame — die Zahlen ändern sich langsam, pro Frame wäre es hunderte
Cairo-Renderings für dasselbe Bild. Das HUD ist eine **eigene** Overlay-Sequenz
(`tracks.overlay`) über der Karte (`tracks.map`), beide Mechanismen gab es im Renderer schon.
Höhenprofil als Polyline mit Positionsmarker (`_profile_polyline`), km aus `cumulative_km`.

**Fund beim Rendern (echtes Bild angesehen, nicht nur Tests):** `cairosvg` rendert `→` (U+2192)
mit den hier verfügbaren Schriften als leeres Kästchen — `—` und `·` gehen. Deshalb
`gpx.stage_label(stage, arrow=…)` konfigurierbar und `map.HUD_ARROW = "—"` als Default für
Bildtexte; in `assets.json` und Reports bleibt der echte Pfeil. Im `map-animator` dokumentiert.

**D1 Templates.** `lower-third.svg` neu: Akzentbalken, abgerundete Ecken, Farbverlauf statt
Vollton, weicher Schlagschatten, Typo-Hierarchie mit Tracking. Neu: `stage-card.svg`,
`map-hud.svg`, `stat-badge.svg`. `design.overlay_tokens(tokens, width=…, height=…)` leitet
**alle** Layout-Tokens relativ zur Zielhöhe ab — das Projekt liefert nur noch Farben, Schriften
und Inhalt. `type_scale` ist damit erstmals echt verdrahtet (`scale_size`: Werte ≤ 1 sind
Faktoren der Bildhöhe, größere gelten als Pixel bei 1080p und werden mitskaliert), sodass
1080p-Preview und 4K-Final optisch identisch wirken. `background_layer()` erlaubt eine optionale
Hintergrundgrafik in Titelkarte/Kapitelmarke (D2-Vorarbeit); `_OPTIONAL_TOKENS` sorgt dafür,
dass bestehende Token-Sets ohne dieses Feld weiterhin gültig bleiben.

**Abnahme D (Teil 1):** parametrisierter Test rendert **alle 7 Templates × 2 Auflösungen**
(1080p/2160p) aus einem gemeinsamen Token-Set fehlerfrei zu PNG; zusätzlich geprüft, dass
Größen mit der Zielhöhe skalieren. Die visuelle Abnahme durch den Nutzer steht noch aus
(Beispielframe der neuen Bauchbinde wurde gerendert und geprüft).

32 neue Tests, 418 gesamt grün.

### A6 + B1 + B5 — Notizen (2026-08-01)

Zusammen umgesetzt, weil `/ff-route` und der `route-planner`-Agent ohne die
Beschaffungswege für die Routengeometrie ins Leere verwiesen hätten.

**A6:** `.claude/commands/ff-route.md` (Stand zeigen → Eingabe holen → an Agent delegieren →
`assign-places --dry-run` prüfen → real ausführen → Lücken über `places-todo`/`set-place`) und
`.claude/agents/route-planner.md` mit der vollständigen Prüfliste: lückenlose Tage, monotone
Daten, Anschluss `to`→`from`, Übernachtung, **km gegen Luftlinie** (`haversine_km`), Tage ohne
Material und Material an Tagen ohne Etappe. Harte Regel im Agenten: **nie raten** — Unsicheres
wird als Rückfrage gemeldet, das Feld bleibt leer.

**B1:** `gpx.cumulative_km` (Kilometerzähler), `gpx.elevation_profile` (GPX-`ele`, Lücken über
einen **injizierbaren** Höhendienst) und `gpx.total_ascent_m`. `route.elevations_for` cacht
projektweit in `route/elevation.json` — genau eine Abfrage je Koordinate, nie erneut, dieselbe
Disziplin wie beim Analyse-Cache. Getestet wird ausschließlich mit injizierten Fakes: kein Test
geht ins Netz.

**B5:** `gpx.parse_kml` (Google-Maps-Export; `gpxpy` liest nur GPX), `gpx.write_gpx` und
`route.build_route_gpx` (Routing über die Etappenpunkte, Dienst injizierbar, Default OSRM).
Alle drei Wege enden in derselben `route/roadtrip.gpx` — der Rest der Pipeline sieht keinen
Unterschied. Orte ohne Koordinate werden **gemeldet, nicht geraten**. Neues Kommando
`frameforge route-build <projekt> [--from-kml datei.kml]`.

**Rückwärtskompatibilität:** `parse_gpx` hat einen neuen Parameter `require_time` mit Default
`True` — exakt das bisherige Verhalten (zeitlose Punkte fliegen raus, Rest chronologisch).
Nur die Geometrie-Pfade rufen mit `require_time=False`; ein Regressionstest hält das fest.

21 neue Tests (`tests/test_route.py`), 386 Tests gesamt grün.

### A4/A5 — Notizen (2026-08-01)

Gemeinsam umgesetzt, ein Commit: beide Pakete arbeiten auf demselben neuen Modul
`frameforge/places.py` und derselben Testdatei — sie getrennt zu committen hätte einen
Zwischenstand hinterlassen, dessen Abnahme ohne den jeweils anderen Teil nicht prüfbar wäre.

**Ort-Kaskade** (`_place_for`): echte GPS-Position des Assets → POI aus `locations.csv` innerhalb
`--tolerance-km` (Default 5 km, `gpx.haversine_km`/`gpx.nearest_poi`) → Position aus
`roadtrip.gpx` zum Aufnahmezeitpunkt → dieselbe POI-Prüfung → Fahretappe: `unterwegs: A → B` →
Standtag: der Ort des Standtags → `unknown`. Jede Zuordnung schreibt `place_source`
(`gps`/`gpx`/`leg`/`stage`/`manual`/`unknown`), damit im Nachhinein sichtbar ist, worauf ein Ort
beruht. **Ohne Toleranzgrenze** bekäme ein Clip mitten auf der Passstraße den Namen der 80 km
entfernten Übernachtung — genau der Fehler aus dem Realbetrieb.

`assign-places` meldet **Konflikte** (bisheriger, aus dem Ordnernamen geratener Ort ≠ berechneter)
statt sie still zu überschreiben; `--dry-run` zeigt denselben Report ohne zu schreiben.
Manuell gesetzte Orte (`place_source: "manual"`) bleiben ohne `--force` unangetastet.
`places-todo` listet alles, was `unknown` oder nur `leg` ist (Gegenstück zu `index-todo`),
`set-place <asset-id|hash> --place … [--kind stop|leg]` schreibt einen Ort von Hand.

**Status:** 11 Tests decken jeden Zweig ab, inklusive des Abnahme-Falls aus dem Plan (Clip am
Trollstigen → Tag 9, Etappe *Geiranger → Lom*, Ort *Trollstigen*, Konflikt gemeldet). Der
**reale** Nachweis am Fundus fehlt noch: `projects/norwegen-2026/route/stages.csv` existiert
nicht, und die Etappenliste darf nicht geraten werden (Plan: „nie raten"). Sie entsteht über
A6 (`/ff-route`) mit dem Nutzer.

### A3 — Notizen (2026-08-01)

`gpx.parse_stages` (Pflichtspalten `day,date,from,to`, optional `via,km,overnight,note`,
Fehler mit Zeilennummer, `km` leer → `None` statt geschätzt), `gpx.stage_for` (Datum → Etappe)
und `gpx.stage_label` (`"Geiranger → Lom"`, bei Standtagen nur der Ort).
`Project.stages_csv_path` neu. Neue Vorlage `templates/prompts/route.md` (Etappen- **und**
POI-CSV, mit der ausdrücklichen Regel „unsichere Koordinate weglassen statt raten").
Die neuen Asset-Felder sind in Plan 0001 §4 nachgetragen. 10 neue Tests in `tests/test_gpx.py`.

### A2 — Notizen (2026-08-01)

`ProjectConfig.originals_root` (optional, `None` = alles wie bisher; `save()` schreibt keine
`null`-Felder mehr). `probe.original_name_from_trimmed` schneidet das
`-HH.MM.SS.mmm-…-segN`-Suffix ab, `probe.probe_media_gps` liest GPS **auch für Videos** per
`exiftool` (ffprobe gibt die DJI-/QuickTime-GPS-Tags nicht aus). Im Backfill:
`index_originals` baut einmal pro Lauf `{Stem: Pfad}` über `originals_root`,
`_gps_from_original` schlägt nur für Videos **ohne** Koordinaten nach und markiert Treffer mit
`gps.source: "original"`. Vorhandene Koordinaten werden nie überschrieben; ohne Treffer bleibt
das Asset ohne Koordinaten (Eingabe für A5, nichts wird geraten). Fehlt `originals_root` oder ist
der Ordner nicht gemountet, ist der Zweig inaktiv — kein Abbruch.

**Status 🔄:** 3 Tests decken den Mechanismus ab (Treffer, kein `originals_root`, kein
auffindbares Original). Die Abnahme des Plans verlangt eine **Stichprobe von 10 echten Clips mit
vorhandenem Original** — dafür muss der Nutzer `originals_root` in `projects/norwegen-2026/
project.yaml` eintragen (Migrationsschritt 3). Solange das nicht existiert, ist der reale
Nachweis nicht führbar; der Code läuft ohne Konfiguration unverändert wie bisher.

### A1 — Notizen (2026-08-01)

`probe.py`: `captured_at_from_name` (`DJI_20260720153625…`, `IMG_/VID_/PXL_20260720_153625…`),
`trim_offset_from_name` (`-00.02.10.556-00.02.18.774-seg5` → `(130.556, 138.774)`) und
`captured_at_for_video` mit der Prioritätskette aus dem Plan: Container-Tag → Dateinamen-Zeit →
Datum aus dem Pfad → `mtime`, plus In-Punkt aus dem Trim-Suffix. `probe_video` liefert
`captured_at` + `captured_at_source` (und `trim_in_s`/`trim_out_s`, wo vorhanden);
`preindex._prepare_one` schreibt beides jetzt auch im Video-Zweig.

**Zeitbasis — am echten Material geprüft, nicht angenommen.** Die Container-Zeit ist echte UTC
(`2026-07-20T13:36:26Z`), die Dateinamen-Zeit die lokale Kamerauhr (`…153625` = 15:36:25). Beide
beschreiben denselben Moment, der Start des Originalclips. Die bestehenden 19 Foto-Einträge
tragen EXIF-Lokalzeit, die `probe_photo_exif` mit `+00:00` etikettiert. Hätte A1 für Videos
stumpf die Container-UTC geschrieben, lägen Videos und Fotos desselben Moments zwei Stunden
auseinander — die Tages- und Etappenzuordnung (A4) hätte an Tagesgrenzen still falsch sortiert.
Deshalb: **Container liefert den Zeitpunkt, der Dateiname den Zonen-Offset**, Ergebnis ist die
lokale Wanduhrzeit (Quelle `container+name`). Das hält die Plan-Priorität ein *und* erhält eine
einheitliche Zeitbasis. Fehlt die Dateinamen-Zeit, bleibt es bei der Container-Zeit (Quelle
`container`) — möglicherweise um den Zonen-Offset verschoben, aber nichts geraten, und
`captured_at_source` macht es sichtbar.

**Abnahme A0 + A1 erfüllt (realer Lauf gegen `norwegen-2026`):** zweiter
`backfill-metadata`-Lauf → **236/236 Videos (100 %) mit Aufnahmezeit**, Plan verlangt ≥ 90 %.
Quellen: `container+name+trim` 224, `container+name` 12, `exif` 19 (Fotos). Zeitraum
2026-07-20 bis 2026-07-31, 11 Drehtage — plausibel. `content`, `rating`, `source` und
`gps.place` erneut bei allen 255 Assets bitgleich (Skript-Vergleich). 14 neue Tests in
`tests/test_probe.py`, 347 Tests gesamt grün, `ruff` sauber.

---

## M1 — Mini-Prototyp end-to-end

Ziel laut Plan Abschnitt 8: `projects/proto/` mit 3–5 Clips, 2 Fotos, kurzer GPX-Spur,
komplett durch die Pipeline bis zu einem abspielbaren 60–90-s-Preview. Eigene
Task-Nummerierung (M1.1, M1.2, ...), da M0 abgeschlossen ist.

| # | Schritt | Status | Commit |
|---|------|--------|--------|
| M1.1 | `probe.py` (ffprobe/exiftool-Wrapper), `ingest.scan_media`/`build_proxies`, winzige Test-Fixtures (`tests/fixtures/clip.mp4`, `photo.jpg` + `generate.py`), Gate-Hook-Heredoc-Bugfix | ✅ fertig | `216d303` |
| M1.2 | `analyze.py` (Schärfe/Stabilität/Belichtung/Scenes), `keyframes.py` | ✅ fertig | `6b5e9af` |
| M1.3 | `index.write_asset` (echt), Merge-Logik für `.md`-Freitext, `cli.py` `ingest`/`index` funktionsfähig gemacht | ✅ fertig | `6b6b824` |
| M1.4 | `gpx.py` (Parsing, Asset↔Ort-Zuordnung) | ✅ fertig | `0ad8142` |
| M1.5 | `design.py` Rendering (SVG→PNG), minimale SVG-Templates | ✅ fertig | `f6bf4de` |
| M1.6 | `map.py` Route-Reveal-Frames | ✅ fertig | `0b4f4f0` |
| M1.7 | `render.py` (Filtergraph-Bau, Proxy-Render), `cli.py` `preview` verdrahtet | ✅ fertig | `44fffda` |
| M1.8 | `projects/proto/` anlegen, komplett durch die Pipeline bis zum Preview | ✅ fertig | `ee50426` |

---

## M2 — Story-Engine vertiefen

Plan Abschnitt 8: "Beat-Sheet-Logik, Clip-Scoring gegen Brief-Ziele, Vermeidung von
Wiederholung, Musik-Sync auf Beat-Grid, `qc-reviewer` mit echtem Regelsatz." Beat-Sheet-Logik
und Clip-Scoring sind kreative Agenten-Entscheidungen (`story-architect`/`timeline-builder`,
LLM-getrieben) — die deterministischen Code-Bausteine dafür sind hier Aufgabe.

| # | Schritt | Status | Commit |
|---|------|--------|--------|
| M2.1 | `audio.py` (BPM/Beat-Grid/Energiekurve echt, gecacht; `duck_curve`) | ✅ fertig | `76f4f0a` |
| M2.2 | `qc.py` echtes Regelsatz (schwarze Frames, Audio-Clipping, Clip-Doppler, Text-Lesbarkeit) | ✅ fertig | `6a68c6f` |

---

## M3 — Karte & Grafik ausbauen

**Nutzer-Klarstellung (2026-07-27):** M3 liefert die generische *Fähigkeit* (Tile-Cache,
Marker-Typen, Kapitelkarten, Bauchbinden-Varianten) — **keine** projektspezifische Gestaltung.
"Wie es aussieht" (Farben, Icons, Kartenstil, konkrete Marker) ist Sache des jeweiligen
Projekts/Designsystems, nicht dieses Codes. Kein Norwegen-spezifisches Styling.

| # | Schritt | Status | Commit |
|---|------|--------|--------|
| M3.1 | `map.py`: Tile-Cache (XYZ, injizierbarer Fetcher), `render_basemap`, generischer Marker (Icon statt fest verdrahtetem Punkt) | ✅ fertig | `b87925f` |

### M3.1 — Notizen (2026-07-27)

`map.py` erweitert, nichts Neues an Dateien:

- **Tile-Cache**: `fetch_tile(z, x, y, cache_dir, *, tile_server_url=..., fetcher=None)` lädt
  eine XYZ-Kachel und cached sie unter `cache_dir/<z>/<x>/<y>.png`. `fetcher` ist injizierbar
  (`Callable[[str], bytes]`) — Tests/CI laufen komplett offline gegen einen Fake-Fetcher,
  nichts hier hängt an echtem Netzwerkzugriff während `pytest`. Ohne eigenen `fetcher` lädt
  `_default_tile_fetcher` per `urllib` gegen `DEFAULT_TILE_SERVER` (OpenStreetMap) — bei
  produktivem Einsatz Nutzungsbedingungen/eigenen Tile-Server beachten, das ist bewusst nicht
  Teil dieses Codes (projektspezifische Entscheidung).
- **`render_basemap(bbox, zoom, cache_dir, ...)`**: setzt eine Basiskarte aus gecachten Kacheln
  zu einem RGBA-Bild zusammen (`latlon_to_tile` = Standard-Slippy-Map/Web-Mercator-Formel).
- **Marker generalisiert**: `render_route_frames(..., marker_icon=None, basemap=None, route_color=ROUTE_COLOR, route_width_px=ROUTE_WIDTH_PX)`.
  Ohne `marker_icon` unverändertes M1-Verhalten (Punkt, `MARKER_COLOR`/`MARKER_RADIUS_PX`).
  Mit `marker_icon`: beliebiges PNG-Icon (Auto, Figur, was auch immer das Projekt liefert)
  wird mittig auf die aktuelle Position gestempelt — **kein** Icon ist hier hart codiert.
  `basemap` ersetzt den transparenten Hintergrund durch ein vorgerendertes Kartenbild
  (Größen-Mismatch wirft `ValueError`, nicht stiller Crop/Stretch).

**Kapitelkarten/Bauchbinden-Varianten brauchten keinen neuen Code.** Die SVG-Templates aus
Task 5 (`templates/svg/chapter.svg`, `lower-third.svg`) sind bereits vollständig
token-parametrisiert (Position, Farben, Schrift, Größe) — "Varianten" sind schon heute nur
ein anderes Tokens-Set, keine Code-Änderung. Damit ist der einzige noch offene M3-Punkt aus
Plan Abschnitt 8 mit echtem Code-Bedarf der Tile-Cache/Marker-Teil gewesen.

13 neue/erweiterte Tests in `tests/test_map.py` (Marker-Icon-Kompositing, Basemap-Nutzung,
Größen-Validierung, Tile-Cache-Hit/Miss, Basemap-Zusammensetzung — alle mit injiziertem
Fake-Fetcher, kein echter Netzwerkzugriff). 140 Tests insgesamt grün, `ruff` sauber, `doctor`
grün.

---

## M4 — Final-Pipeline

Plan Abschnitt 8: "4K-Mapping auf die Originale, Farbkorrektur-Stufe, Loudness-Normalisierung
(EBU R128), NLE-Export FCPXML + OTIO, Render-Versionierung."

| # | Schritt | Status | Commit |
|---|------|--------|--------|
| M4.1 | `render.render_final` (4K-Mapping, EBU-R128-Loudnorm, optionale LUT, Render-Versionierung), `cli.py` `render` verdrahtet | ✅ fertig | `4cb21aa` |
| M4.2 | `nle.py` (FCPXML/OTIO-Export), `cli.py nle`-Kommando | ✅ fertig | `4cb21aa` |

### M4.1 — Notizen (2026-07-27)

`render_final(project, export, timeline, *, lut_path=None)`: löst Assets über `assets.json`
direkt auf die **Original**-Dateien unter `project.config.media_root` auf (kein Proxy-Downscale
— das "4K-Mapping" ist damit einfach die Konsequenz aus "kein Downscale", `build_filtergraph`
skaliert ohnehin generisch auf `timeline.resolution`, dafür war kein Sonder-Code nötig).

`build_filtergraph` um zwei generische Hooks erweitert (M3-Prinzip: Infrastruktur, keine feste
Optik):
- `lut_path`: optionale 3D-LUT (`.cube`) über den `lut3d`-Filter — keine Grade ist hier fest
  eingebaut, das liefert das Projekt (Plan §11: "Farbmanagement bei HLG/D-Log-Material").
- `loudness_normalize`: EBU-R128-Normalisierung (`loudnorm`, Ziel -16 LUFS/-1.5 dBTP) auf
  den gemischten Audio-Output — nur in `render_final` aktiv, `render_proxy` bleibt unverändert
  (Preview muss nicht normiert sein).

**Render-Versionierung**: `_next_version_path` scannt `exports/<export>/final/` nach
`<export>_v<N>.mp4` und wählt das nächste `N` — überschreibt nie einen vorherigen Final-Render.

`cli.py render` rief bisher nur den Platzhalter-Text auf (wie `preview` vor M1.7) — ruft jetzt
`render.render_final` echt auf, setzt Export-Phase auf `RENDERED`. Kompletter End-to-End-Flow
manuell verifiziert: `new → ingest → preview → render (vor approve, blockiert) → approve →
render (nach approve, erfolgreich)`.

13 neue Tests (`tests/test_render.py`: 3 String-Tests für `lut_path`/`loudness_normalize`,
3 echte Render-Tests inkl. Versionierung und fehlendem Original). 145 Tests insgesamt grün.

### M4.2 — Notizen (2026-07-27)

`nle.py`: `build_otio_timeline` baut aus `Timeline` eine `opentimelineio`-Timeline (eine
Video-Spur, N parallele Audio-Spuren), `export_otio`/`export_fcpxml` schreiben sie als
natives `.otio` (JSON, OTIO-Core) bzw. FCPXML.

**Abhängigkeits-Fund:** der FCPXML-Adapter ist seit OTIO 0.17 nicht mehr im Core enthalten
(aus `opentimelineio-contrib` ausgelagert). Gefunden über `uv pip install --dry-run` einiger
Kandidaten-Paketnamen — `otio-fcpx-xml-adapter` (Adapter-Name `fcpx_xml`, FCPX-Format statt
des älteren FCP7-XML, wird von DaVinci Resolve ebenfalls importiert) existiert und ist
installierbar. Als Dependency in `pyproject.toml` ergänzt.

**Zwei echte Bugs beim ersten Lauf gegen `projects/proto/` gefunden:**

1. **Fehlende `available_range`.** Der `fcpx_xml`-Adapter braucht `media_reference.
   available_range` (die volle Dauer des Quellmaterials), nicht nur `source_range` (den
   genutzten Ausschnitt) — ohne das: `AttributeError: 'NoneType' object has no attribute
   'duration'`. Da `resolve_asset` nur einen Pfad liefert, keine Metadaten, ist die
   konservative Annahme `available_range = source_range` (mindestens das Genutzte ist
   verfügbar) — keine echte Asset-Gesamtdauer, aber ausreichend für einen validen Export.
2. **Überlappende Audio-Clips in einem Track.** `otio.schema.Track`-Items dürfen sich nicht
   überlappen (wie unsere Video-Spur) — Musikbett + gleichzeitiger O-Ton wurden aber beide in
   einen einzigen Audio-Track geschrieben, was den `fcpx_xml`-Adapter mit `AttributeError:
   'NoneType' object has no attribute 'get'` zum Absturz brachte (kaputte
   Offset-Berechnung bei impliziten Overlaps). Fix: `_pack_lanes()` (Greedy-Interval-Packing)
   verteilt überlappende Audio-Clips auf so viele parallele Audio-Spuren wie nötig — exakt
   wie ein NLE das normalerweise darstellt.

`cli.py` neues Kommando `nle <projekt> <export> --format fcpxml|otio`, schreibt nach
`exports/<export>/nle/<export>.<format>`. `.gitignore` um `projects/*/exports/*/nle/`
ergänzt (generiertes Artefakt aus `timeline.json`, wie `preview/`/`final/`).

Nebenbei denselben Bug-Typ wie in M1.3 (`write_asset({})`) noch einmal gefunden und gefixt:
`cli.py design` rief `design.build_svg_from_tokens(tokens.yaml-Pfad, {})` auf — seit
`build_svg_from_tokens` in M1.5 echt ist, ist das kein sinnvoller Aufruf mehr (Tokens-Datei
wird nicht als SVG-Template gelesen). Fix: `design` prüft jetzt, ob `design/tokens.yaml`
existiert, und setzt bei Erfolg die Projekt-Phase auf `DESIGNED` — kein Platzhalter-Aufruf
mehr. `tests/test_stubs.py` gelöscht: nach M4.2 gibt es im gesamten Package keine
`NotImplementedError`-Stubs mehr, die Datei hatte keinen Zweck mehr.

16 neue Tests (`tests/test_nle.py`: 9, `tests/test_cli.py`: 7 neue für `design`/`nle`).
157 Tests insgesamt grün, `ruff` sauber, `doctor` grün.

**M4 ist damit komplett — alle Punkte aus Plan Abschnitt 8 (M0–M4) umgesetzt**, inklusive der
generischen M3-Infrastruktur. Was laut Plan explizit offen bleibt: M5 (Norwegen-Realbetrieb —
echtes Material, kein Code-Meilenstein) und die in Plan §11 gelisteten "Offenen Punkte für
später" (Gesichtserkennung, automatische Untertitel, Musik-Lizenz-Nachweis).

---

## M-Extra — Gesichtserkennung (Plan §11, auf Nutzerwunsch vorgezogen)

**Nutzer-Entscheidung (2026-07-27):** Von den vier "Offenen Punkten für später" nur
Gesichtserkennung jetzt umsetzen, automatische Untertitel und Musik-Lizenz-Nachweis bleiben
zurückgestellt. M5 (Norwegen-Realbetrieb) startet erst mit echtem Material.

| # | Schritt | Status | Commit |
|---|------|--------|--------|
| ME.1 | `people.py` (Gesichtserkennung + Clustering), `cli.py faces`-Kommando (Opt-in) | ✅ fertig | `d2bd4a5` |

### ME.1 — Notizen (2026-07-27)

**Datenschutz zuerst:** `people.py` wird **nicht** automatisch von `frameforge index`
aufgerufen — Gesichtserkennung verarbeitet biometrische Daten, das ist ein expliziter Opt-in
(`frameforge faces <projekt>`). Ergebnisdateien (`index/people.json`,
`index/people_clusters.json`, enthalten 128-d-Encodings) sind per `.gitignore` vom Tracking
ausgeschlossen, obwohl `index/` sonst getrackt wird — die Encodings sind biometrische Daten,
die nie in ein (hier: öffentliches) GitHub-Repo gehören.

**Installations-Fallstricke, beide gelöst:**
1. `face_recognition` zieht `dlib` — kompiliert aus C++ (kein vorgebautes Wheel für diese
   Plattform), Build-Dauer ~3:20 Min (LTO-Linking des finalen `.so` ist der langsamste Schritt).
   Kein Bug, nur Geduld nötig.
2. `face_recognition_models` nutzt intern noch `from pkg_resources import resource_filename` —
   `setuptools >= 81` hat `pkg_resources` entfernt, das aktuelle venv hatte `setuptools==83`.
   Fix: `setuptools<81` als direkte Dependency gepinnt (analog zum `numba`-Pin aus
   HANDOVER.md — beides "transitive Abhängigkeit braucht eine ältere Version, die von selbst
   nicht aufgelöst worden wäre").

**Umsetzung:** `detect_faces(path)` — echt, via `face_recognition`/`dlib` (HOG-Detektor +
128-d-Encodings pro Gesicht), kein Mock. `cluster_people(faces_by_asset, tolerance=0.6)` —
reine Vektor-Arithmetik (Greedy-Clustering gegen Cluster-Centroide via `face_recognition.
face_distance`), ordnet Gesichter über Assets hinweg Personen zu (`person_1`, `person_2`, ...
— welche Person das ist, z.B. "Oskar", liefert der Nutzer/Orchestrator, nicht dieses Modul).

**Test-Strategie ohne echte Gesichtsfotos im Repo:** `detect_faces` wird nur gegen die
bestehende Solid-Color-Fixture (`photo.jpg`, 0 Gesichter — echter Negativ-Test) und den
Fehlerfall (fehlende Datei) getestet. `cluster_people` ist reine Vektor-Arithmetik und wird
mit synthetischen 128-d-Zufallsvektoren getestet (zwei "Personen"-Cluster um verschiedene
Zentren, mit Rauschen) — keine echten/fremden Gesichter nötig, um die Clustering-Logik zu
verifizieren.

17 neue Tests (`tests/test_people.py`: 6, `tests/test_cli.py`: 2 neue für `faces`, plus
Aktualisierungen). 165 Tests insgesamt grün, `ruff` sauber, `doctor` grün.

---

## Audit-Fixes (2026-07-27, Opus)

Nach Abschluss von M0–M4 + Gesichtserkennung ein vollständiges Audit (Code, Gate-Hook,
State-Machine, Render-/Ingest-Pfad, Security/Prozess). Alle Findings umgesetzt und mit Tests
abgesichert; das komplette proto-Projekt danach end-to-end (`ingest → … → render → nle`)
über die echte CLI validiert. **201 Tests grün, `ruff` sauber, `doctor` grün.**

| Fix | Finding | Commit |
|---|---|---|
| K1 | Proxy-Namenskollision (gleicher Basename in versch. Ordnern → falsches Material) — Proxy-Name trägt jetzt Pfad-Hash | `c10df4f` |
| K3 | Ingest ohne Timeout/Resume — pro-Datei-Timeout, Fehler überspringen statt abbrechen, existierende Proxies überspringen | `c10df4f` |
| K2 | `amix` ohne `normalize=0` halbierte die Pegel — Gains/Ducking gelten jetzt wie gesetzt | `e62fccf` |
| P1 | `design` übersprang INGESTED/INDEXED — neues `gate_design` (erfordert INDEXED) | `04a7774` |
| P1b | kein Kommando erreichte je INDEXED — `index` hebt die Phase, sobald nichts mehr pending ist | `04a7774` |
| P5 | Ingest warf die Phase zurück — `ensure_project_at_least` (forward-only) | `04a7774` |
| S1 | Path-Traversal über Projekt-/Export-Namen — `validate_name` | `d5d944b` |
| S2 | Path-Traversal über `asset["path"]` aus assets.json — `resolve_media_path` (bounds-check) | `d5d944b` |
| P3 | Final-Render vertraute stale APPROVED — Timeline-Fingerprint bei approve, Prüfung + QC-Wiederholung bei render | `9672670` |
| P2 | Content-Hash-Mechanismus war ungenutzt — erstmals real verdrahtet (Timeline-Fingerprint) | `9672670` |
| P4 | State read-modify-write nicht transaktional — `ProjectState.transaction` (Lock über die ganze Transaktion) | `47fca91` |
| K4 | `map.encode_alpha_video` ohne Timeout — ergänzt | `47fca91` |
| K5 | Ducking traf nur die erste Musik-Spur — jetzt alle | `47fca91` |
| K6 | QC prüfte Asset-Existenz nicht — `known_asset_ids`-Check | `47fca91` |
| Q1 | LUT-Hook war CLI-seitig tot — `frameforge render --lut` | `47fca91` |
| Q4 | Gate-Hook crashte bei kaputtem venv — fail-open (nackte ffmpeg-Sperre bleibt) | `47fca91` |
| S4 | kein Lockfile — `uv.lock` committet, README auf `uv sync` | `ca2aa03` |
| Q2 | veraltete "kommt in M1"-Kommentare — bereinigt | `ca2aa03` |

**Bewusst offen gelassen (dokumentiert, nicht "Bug"):**
- **P2 (brief.yaml-Invalidierung):** „brief geändert → Export zurück auf BRIEFED" ist nicht
  automatisiert, weil `brief`/`build` agentengetriebene Platzhalter sind (kein CLI-Kommando
  schreibt `brief.yaml`). Die risikoreichere Variante — Timeline nach Freigabe geändert — ist
  über den Fingerprint (P3) geschlossen.
- **S3 (Gate-Hook-Umgehbarkeit):** `bash -c "ffmpeg …"`, `uv run frameforge`, `$(…)` etc.
  umgehen den Hook. Er ist bewusst **Belt-and-suspenders gegen ein Versehen des
  Orchestrators**, keine adversariale Grenze — die CLI erzwingt die Gates ohnehin selbst.

---

## Wizard & visueller Status (2026-07-27, auf Nutzerwunsch)

Nutzer wollte eine geführte, abbrechbare, resumierbare Bedienung („Wizard") mit
Status-/Fortschritts-Übersicht. Bewusst **kein Web-Frontend**: die kreativen Schritte (Index,
Design, Brief, Story→Timeline) brauchen Claude/die Agenten, eine Website wäre nur eine zweite
Steuerungsebene, die vom `.state.json` abdriften kann. Stattdessen auf der bestehenden
State-Machine aufgesetzt:

- **`frameforge/pipeline.py`** (neu): leitet aus dem `ProjectState` die Pipeline-Karte ab —
  pro Schritt `✓`/`→`/` `, Projekt-Ebene + je Export eine Spur, plus den nächsten fälligen
  Befehl. Reine Ableitung, kein I/O, voll testbar (7 Tests in `tests/test_pipeline.py`).
- **`frameforge status`** zeigt jetzt diese visuelle Karte (farbige Marker) statt einer nackten
  Phasen-Tabelle. `frameforge/pipeline.py` ist die gemeinsame Quelle für Status und Wizard,
  damit „du bist hier" nie auseinanderläuft.
- **`/ff-wizard [projekt]`** (neu): geführter Ablauf — Stand zeigen, nächsten Schritt erklären,
  nur die dafür nötigen Eingaben abfragen, ausführen, Status erneut zeigen, weiter/pausieren
  fragen. Jederzeit abbrechbar (Stand in `.state.json`), resumierbar. Behandelt den
  „Design-Tokens extern erstellen → ablegen → später weiter"-Fall als bewusste Pause.
- `/ff-status` aktualisiert (visuelle Karte + Verweis auf `/ff-wizard`), README um Wizard-
  Callout und Beispiel-Ausgabe ergänzt.

208 Tests grün, `ruff` sauber, `doctor` grün.

## Ausbaustufen A–D (2026-07-28, "alle in sinnvoller Reihenfolge")

Auf Nutzerwunsch die komplette vorgeschlagene Erweiterungsliste umgesetzt:

- **A1 Stil-Presets als Daten:** `presets/*.yaml` (6 Presets) + `frameforge/presets.py`
  (list/load/`apply_preset`) + `frameforge presets`. Der Brief wählt per `preset:`-Slug, die
  Parameter (pacing/color_grade/transitions/music_energy/ken_burns …) werden untergelegt.
- **A3 Brief-Schema:** `frameforge/brief.py` (Pydantic, validiert Preset-Slug + Dauer,
  `merged()` löst Preset auf); preview/render laden den Brief darüber (klare Fehler).
- **A2 Design-Themes:** `themes/*.yaml` (Nordic Cold, Warm Sunset, Mono Editorial, Vibrant
  Roadtrip) + `frameforge themes` / `apply-theme`.
- **B3 Render-Qualität:** `render --resolution/--crf/--preset`; `build_filtergraph` nimmt eine
  Ziel-Auflösung.
- **B2 Color-Grade aus Preset:** `render.grade_filter` (mood+contrast → eq/colorbalance),
  automatisch in Preview und Final, LUT kommt obendrauf.
- **B1 Übergänge + Ken-Burns:** `xfade` bei `transition_in` fade/dissolve, `zoompan` bei
  `kenburns`-Effekt auf Fotos; ohne Transition/Effekt exakt wie bisher (concat).
- **C1 locations.csv:** `gpx.parse_locations` + POI-Marker in `map.render_route_frames`.
- **C2 Tageszusammenfassungen:** `stats.day_summaries`/`write_day_summaries` + `frameforge days`
  → `index/days/<datum>.md`.
- **D1–D5:** `ingest --dry-run`, `frameforge clean`, doctor-Plattenplatz-Check,
  persistenter `cache/ingest-report.json`, `frameforge clone-export`.

Nebenbei gefixt: `ingest._path_key` löst beide Seiten auf, sonst fanden Ingest und Render den
Proxy bei symlink-behaftetem `media_root` (macOS `/var`, Mounts) nicht.

292 Tests grün, `ruff` sauber, `doctor` grün, proto weiterhin end-to-end ok.

## Statistik & Report (2026-07-27, auf Nutzerwunsch)

Nutzer wollte einen Überblick über den indizierten Fundus und ein „was-wurde-hier-gemacht"-
Datenblatt pro Export (neben dem MP4). Beides rein aus vorhandenen Daten abgeleitet
(`frameforge/stats.py`, kein Neu-Analysieren):

- **`frameforge stats <projekt>`**: Fundus-Umfang (Video/Foto), Deckung indiziert vs. Dateien
  im Quellordner (media_root offline → sauber übersprungen), Rohmaterial-Dauer, Ø-Qualität,
  Rating-Verteilung, Auflösungen, Codecs, Orte, Personen-Assets, plus Nutzung je Export +
  Gesamt-Deckung.
- **`frameforge report <projekt> <export>`** und **automatisch beim Final-Render**
  (`<export>_vN.report.md` neben dem MP4): Markdown-Datenblatt mit Quelle/Umfang, genutzten
  Clips (In/Out + Beschreibung) und %-Anteil am Fundus, Dramaturgie (Preset/Länge/Beat-Sheet),
  Audio (Musik/O-Ton/Ducking), Design (Schrift/Farben), Technik (Auflösung/Spuren/Ø-Qualität).

`exports/*/report.md` ist gitignored (regenerierbar); der Render-Report liegt ohnehin im
gitignorierten `final/`. 14 neue Tests (`tests/test_stats.py`: 7, `tests/test_cli.py`: 3 für
stats/report, Rest Regression). 215 Tests grün, `ruff` sauber.

## Personen-Index (Naming) + Inhalts-Komposition (2026-07-27, auf Nutzerwunsch)

Nutzer wollte (a) benennbare Personen („mehr Oskar") und (b) Anteile im Fundus (Landschaft vs.
Personen, Drohne vs. Handheld, Motive) mit Prozenten.

**Personen benennen** (`people.py` erweitert): `cluster_people_detailed` behält pro Cluster die
genauen Mitglieder `(asset_id, face_index)`, damit bei Gruppenfotos das richtige Gesicht
gecroppt wird. `write_representative_crops` legt pro Cluster einen Gesichts-Ausschnitt in den
Cache (fürs Ansehen/Benennen). Namensverwaltung projektweit in `index/people_names.json`
(`set_person_name`, `load_people_names`, `assets_for_person` — case-insensitiv, Umbenennen über
den alten Namen). CLI: `frameforge people` (Cluster-Tabelle), `frameforge name-person`,
`frameforge faces` schreibt jetzt zusätzlich Crops + zeigt die Tabelle, `frameforge query
--person <name>` filtert. Der Wizard führt das Benennen konversationell (Claude sieht die
Crops, fragt „wer ist das?", ruft `name-person`).

**Inhalts-Komposition** (`stats.py`): `content_composition` liefert Anteile nach Art
(Video/Foto), Personen (mit/ohne, in Sekunden), Kamera/Motion (`motion.type`) und Top-Motiven
(Tags); `person_presence` zählt pro benannter Person Assets + Video-Sekunden. `frameforge stats`
zeigt beides mit %-Anteilen; das Export-Datenblatt bekommt eine „Fundus-Zusammensetzung"-Sektion.

21 neue Tests. 229 Tests grün, `ruff` sauber, `doctor` grün.

### Nachtrag: Design-Asset-Inventar + Prompt-Vorlagen (2026-07-27)

Damit der Wizard-Pausenfall „Grafiken extern erstellen → ablegen → weiter" idiotensicher ist:
`design.asset_inventory` gleicht die in `design/prompts.md` angeforderten Grafik-Dateinamen
gegen `design/assets/` ab (requested/present/missing/extra). Neues read-only-Kommando
`frameforge design-status` zeigt tokens.yaml-Status, Schriften und das Grafik-Inventar
(✓ abgelegt / ✗ fehlt noch); `frameforge design` zeigt es nach dem Übernehmen ebenfalls. Der
Wizard prüft beim Wiedereinstieg `design-status`, bevor er `design` ausführt. Kein
Hintergrund-Warten — Stand in `.state.json`, Nutzer sagt „weiter".

Zusätzlich Starter-Prompt-Vorlagen (`templates/prompts/graphics.md`, `music.md`) und
`templates/project/tokens.example.yaml`; `design-system`/`audio-designer`-Agenten verweisen
darauf. Grafiken/Musik sind optional — Text-Overlays laufen ohne. 5 neue Tests. 246 Tests grün.

### Nachtrag: feste Quelle/Kamera-Kategorie (2026-07-27)

Nutzer wollte „nur Drohnen-Shots" als saubere, wiederholbare Auswahl. Neues kontrolliertes
Vokabular `asset["source"]` = `drone`/`phone`/`camera`/`action_cam`/`unknown`
(`probe.SOURCE_TYPES`). `probe.guess_source` schlägt es aus EXIF-/Container-Kamera-Angaben vor
(DJI→drone, iPhone→phone, GoPro→action_cam …), `probe_video`/`probe_photo_exif` liefern
`source_guess` mit; der `media-indexer`-Agent setzt `source` (Vorschlag übernehmen, außer die
Keyframes zeigen klar etwas anderes). Auswahl: `frameforge query --source drone`. `stats` +
Report zeigen die Quelle-Verteilung (Sekunden + %). 4 neue Tests (guess_source, by_source,
query --source), proto-Fixtures mit `source` versehen. 241 Tests grün.

### M2.1 — Notizen (2026-07-27)

`audio.py`: `analyze_track` nutzt `librosa.beat.beat_track` (BPM + Beat-Grid) und
`librosa.feature.rms` (Energiekurve), auf `0.5s`-Schritte heruntergesampelt — die native
RMS-Auflösung wäre für Sync-Zwecke unnötig groß. `analyze_and_cache` cached das Ergebnis
unter `music/analysis/<hash>.json`, Hash über `ingest.hash_file` — dieselbe
Token-Disziplin-Regel ("Analyse genau einmal pro Datei") wie bei Video-/Foto-Assets, jetzt
auch für Musik. `duck_curve` liefert Gain-Keyframes mit sanften Rampen (`fade_s`, Default
0.3s) statt harter Sprünge.

**Ducking-Kurve noch nicht in `render.py` verdrahtet.** `render.build_filtergraph` nutzt
weiterhin die in M1.7 gebaute statische `volume`-Filterkette mit `enable`-Fenstern (harte
Sprünge, keine Rampen). `duck_curve` liefert die Datengrundlage für eine sanftere Umsetzung,
die Integration in den Filtergraph ist bewusst zurückgestellt (kein Teil von M2 laut Plan,
eher eine spätere Politur-Aufgabe an `render.py`).

Neue Test-Fixture `tests/fixtures/tone.wav` (4s Sinuston mit Tremolo — erzeugt eine
sichtbare Energiekurve, ohne dass die BPM-Erkennung an echtem Musikmaterial hängt, das nicht
im Repo landen darf).

**Kleiner Testfehler beim Schreiben selbst gefunden:** `hash_file` nimmt `size + mtime` in
den Hash auf (Plan §3) — eine per `shutil.copy` (ohne `2`) kopierte Datei hat trotz
identischem Inhalt eine andere `mtime` und damit einen anderen Cache-Schlüssel. Das ist
beabsichtigtes Verhalten des Cache-Schlüssels, nicht ein Bug; der ursprüngliche Test ging
fälschlich von reiner Inhaltsdeduplizierung aus. Korrigiert auf `shutil.copy2` (erhält
`mtime`), Testname und Kommentar angepasst.

119 Tests grün, `ruff` sauber, `doctor` grün.

### M2.2 — Notizen (2026-07-27)

`qc.validate(timeline, *, brief=None)` — Signatur um optionales `brief`-Dict erweitert,
rückwärtskompatibel (ohne Brief laufen nur die timeline-internen Regeln). Neue Checks:

- **Video-Lücken/Überlappungen** statt echter "schwarzer Frames": der M1-Renderer schneidet
  Clips hart hintereinander unabhängig von `tl_in` (Plan/PROGRESS M1.7) — eine Lücke in der
  Timeline führt dort zu fehlendem Inhalt, nicht zu einem sichtbaren schwarzen Frame. Der
  Check prüft deshalb Lücken/Überlappungen zwischen `tl_in`-Positionen der Video-Clips
  (sortiert), das ist das, was aus reinen Timeline-Daten *tatsächlich* prüfbar ist. Echte
  Schwarzbild-Erkennung (`ffmpeg`-`blackdetect` auf einem gerenderten Preview) bräuchte einen
  fertigen Render als Eingabe — bewusst nicht Teil dieser Funktion, die synchron vor dem
  Render laufen soll.
- **Audio-Clipping-Risiko**: jeder `AudioClip` mit `gain_db > 0` wird geflaggt — die Pipeline
  soll nur abschwächen, nie verstärken; positiver Gain ist der einzige aus Timeline-Metadaten
  ableitbare Clipping-Indikator ohne echte Pegel-Analyse.
- **Text-Lesbarkeit**: Overlays unter `MIN_OVERLAY_READABLE_S = 1.2s` gelten als kaum lesbar.
- **Clip-Wiederholung**: mehr als `MAX_ASSET_REPEATS = 2` Verwendungen desselben Assets in der
  Video-Spur werden geflaggt.
- **Brief-Abgleich** (nur falls `brief` übergeben): Ziellänge (`target_duration_s`, Toleranz
  `DURATION_TOLERANCE_S = 2.0`), verbotene Shots (`forbidden_shots`), fehlende Muss-Shots
  (`must_shots`).

`cli.py preview` lädt jetzt `brief.yaml` (falls vorhanden) und reicht es an `qc.validate`
durch — vorher wurde der Brief bei der QC-Prüfung komplett ignoriert.

Gegen `projects/proto/` (aus M1.8) verifiziert: `validate(timeline, brief=brief)` liefert
`[]` — das Testprojekt besteht die neuen Regeln, ohne neu gebaut werden zu müssen.

16 neue Tests in `tests/test_qc.py` (vorher 2, jetzt jede Regel einzeln negativ+positiv
geprüft). 133 Tests insgesamt grün, `ruff` sauber, `doctor` grün.

### M1.1 — Notizen (2026-07-27)

`probe.py`: `probe_video` (ffprobe `-show_format -show_streams`, parst `r_frame_rate` wie
`"30000/1001"`), `probe_photo_exif` (exiftool `-j`, GPS in Dezimalgrad, `DateTimeOriginal`
→ ISO). Beide werfen `ProbeError` bei fehlender Datei/leerem Ergebnis statt still `None`
zurückzugeben.

`ingest.py`: `scan_media` (rekursiv, ignoriert versteckte Dateien und Nicht-Medienformate),
`build_proxies` (Video → 1080p H.264 `veryfast`/CRF 23 via `ffmpeg` **intern per
`subprocess`**, Fotos werden 1:1 kopiert statt transcodiert — sie brauchen keinen Proxy für
den Schnitt-Workflow).

**Wichtige Klarstellung zum ffmpeg-Verbot:** Der Gate-Hook aus Task 4 blockte den Versuch,
Test-Fixtures per nacktem `ffmpeg`-Bash-Aufruf zu erzeugen (korrektes Verhalten). Das
CLAUDE.md-Verbot ("Alles läuft über `frameforge.render`") gilt für **Bash-Aufrufe des
Orchestrators** und für **Render-Ergebnisse aus `timeline.json`** — nicht dafür, dass
Python-Module intern `subprocess` + `ffmpeg` nutzen (Proxy-Transcoding in `ingest.py`,
später Rendering in `render.py`). Deshalb: `tests/fixtures/generate.py` ruft `ffmpeg` per
`subprocess` aus einem committeten Python-Skript auf (`.venv/bin/python
tests/fixtures/generate.py`), nicht direkt aus Bash.

**Nebenbei gefundener Gate-Hook-Bug (behoben):** Beim Versuch, diesen Commit zu erstellen,
blockte `gate.py` den `git commit`-Aufruf fälschlich mit "Nackter ffmpeg-Aufruf verboten" —
obwohl gar kein `ffmpeg` in der eigentlichen Kommandozeile vorkam. Ursache: `_command_segments`
splittete den kompletten Bash-String naiv an jedem `\n`, *bevor* `shlex` zum Zug kam. Die
Commit-Message wurde per Heredoc (`git commit -m "$(cat <<'EOF' ... EOF)"`) übergeben und
enthielt eine Zeile, die mit dem Wort "ffmpeg" begann — die wurde dadurch als eigenständiges
Bash-Segment mit `ffmpeg` als Programmname fehlinterpretiert. Fix: `_strip_heredocs()`
entfernt Heredoc-Rumpfinhalte vor der Segmentierung, echte mehrzeilige Befehle (Newline als
Befehlstrenner ohne Heredoc) werden weiterhin korrekt pro Zeile geprüft. Zwei neue
Regressionstests in `tests/test_gate_hook.py`.

78 Tests grün (`tests/test_probe.py`, `tests/test_ingest.py` neu/erweitert, `tests/test_gate_hook.py`
um den Heredoc-Fix ergänzt), `ruff` sauber.

### M1.2 — Notizen (2026-07-27)

`analyze.py`: Heuristiken statt ML — Schärfe über Laplacian-Varianz (normiert, gedeckelt bei
1.0), Belichtung über Nähe des mittleren Grauwerts zu Mittelgrau (128), Stabilität über die
mittlere Frame-zu-Frame-Differenz dreier Sample-Frames (10/50/85 % der Dauer). Bewusst grob —
Ziel ist Material grob zu sortieren, nicht präzise Bildqualität zu messen. `detect_scenes`
nutzt `scenedetect.ContentDetector`, Fallback: eine Szene über die ganze Clip-Dauer, falls
keine Schnitte erkannt werden. `analyze_photo` liefert nur `quality` (kein `motion`/`scenes` —
nicht anwendbar auf Standbilder).

`keyframes.py`: 3 Frames je Video (10/50/85 % der Dauer) plus 1 Frame pro erkannter Szene
(Szenen-Mittelpunkt), auf `MAX_KEYFRAMES = 6` gedeckelt und dedupliziert; Fotos liefern 1
Frame (das Foto selbst). Alle Keyframes auf 768 px lange Kante skaliert, JPEG q80 — exakt die
Werte aus der Token-Disziplin-Regel in `CLAUDE.md`.

Manuell gegen die Fixtures verifiziert (`clip.mp4`: 2s Testsrc → 3 Keyframes 320×240 unter
768px, daher unskaliert; `photo.jpg`: 1 Keyframe). 85 Tests grün (`tests/test_analyze.py`,
`tests/test_keyframes.py` neu), `ruff` sauber, keine Deprecation-Warnings.

### M1.3 — Notizen (2026-07-27)

`index.write_asset`: Upsert nach `asset["id"]` in `assets.json` (Liste, sortiert nach ID für
stabile Diffs). `.md`-Datei wird neu generiert, aber alles nach dem Marker `<!-- ff:notes -->`
bleibt über Re-Indexierung erhalten (`_existing_notes()` liest den bestehenden Freitext vor
dem Überschreiben aus) — genau das Merge-Verhalten aus Plan §1.

**Zwei kaputte CLI-Kommandos beim Verdrahten gefunden und mitgefixt** (Bug, keine
Scope-Erweiterung — beide waren durch die vorherigen Stub-Exceptions verdeckt):
- `frameforge index` rief bisher `index_module.write_asset(proj, {})` als Platzhalter auf.
  Seit `write_asset` echt ist, wirft das `KeyError: 'id'` statt der vorherigen sauberen
  `NotImplementedError`. Neues Verhalten: `index` scannt Medien, vergleicht Hashes gegen
  `assets.json`, meldet, wie viele Assets noch keine Beschreibung haben — schreibt aber
  bewusst noch nichts, weil `content.summary`/`tags`/`rating` den `media-indexer`-Agenten
  (Claude Vision) brauchen. Phase wird hier noch nicht auf `INDEXED` gesetzt.
- `frameforge ingest` rief `ingest_module.scan_media(...)` auf und **verwarf das Ergebnis**,
  seit `scan_media` kein Stub mehr ist — tat also nichts Sichtbares und advancte nie die
  Phase, wodurch jeder folgende Schritt an einem Gate hängen geblieben wäre, ohne dass der
  Grund ersichtlich war. Jetzt: scannt, baut Proxies über `ingest.build_proxies` in
  `<cache_dir>/proxies/`, setzt Projekt-Phase auf `INGESTED`.

Beide manuell end-to-end mit den Fixtures verifiziert (`frameforge new` → `ingest` → `index`
→ `status` zeigt `INGESTED`, Proxies liegen im Cache-Verzeichnis). Neue Tests in
`tests/test_cli.py` (Typer `CliRunner`) und `tests/test_index.py` (Upsert, Markdown-Inhalt,
Notizen-Erhalt).

92 Tests grün, `ruff` sauber, `doctor` grün.

### M1.4 — Notizen (2026-07-27)

`gpx.py`: `parse_gpx` liest alle Tracks/Segmente über `gpxpy`, filtert Punkte ohne Zeitstempel
(nutzlos für Zeit-basierte Zuordnung) und sortiert chronologisch. `nearest_location` wählt den
zeitlich nächsten Punkt (`min` über absolute Zeitdifferenz), ohne Toleranzgrenze — ein Asset
weit außerhalb der Tour bekommt trotzdem den nächsten Punkt zugeordnet; eine sinnvolle
Toleranz zu setzen ist Sache des Aufrufers (Ingest-Pipeline), nicht dieser Funktion.

Neue Fixture `tests/fixtures/route.gpx` (3 Punkte, eine Etappe). 94 Tests grün, `ruff`
sauber.

### M1.5 — Notizen (2026-07-27)

`design.py`: `build_svg_from_tokens` ersetzt `{{key}}`-Platzhalter per einfachem String-Replace
(kein Jinja — Templates sind klein und statisch, eine Template-Engine wäre unnötiges Gewicht).
Bricht mit `TemplateError` ab, wenn nach dem Ersetzen noch ein `{{...}}` übrig ist, statt den
Platzhalter still im SVG stehen zu lassen. `render_svg_to_png` ruft `preload_cairo()` auf und
delegiert an `cairosvg.svg2png`.

4 minimale SVG-Templates unter `templates/svg/` (`title-card`, `lower-third`, `chapter`,
`credits`) laut Plan §1 — alle mit `{{width}}`/`{{height}}`/Farb-/Font-Tokens parametrisiert,
damit ein gemeinsames Tokens-Set aus `design/tokens.yaml` für alle vier reicht.

98 Tests grün (`tests/test_design.py` erweitert um Templating/Rendering-Tests, inkl. PNG-Magic-
Byte-Check und allen 4 Templates gegen ein gemeinsames Token-Set), `ruff` sauber.

### M1.6 — Notizen (2026-07-27)

`map.py`: PNG-Sequenz mit Alpha, Route als wachsende Linie über die Dauer (`reveal_count`
proportional zum Frame-Fortschritt) plus Positions-Marker am aktuellen Ende. Projektion ist
eine einfache Equirectangular-Projektion auf die Bounding-Box des Tracks — **kein
Tile-Fetch**. Bewusste Scope-Entscheidung: Plan Abschnitt 8 listet "Tile-Cache" explizit erst
unter M3 ("Route-Reveal mit Easing, Marker-Typen, Figur/Auto entlang der Spur, Tile-Cache,
Kapitelkarten"), eine Basiskarte aus OSM-Tiles ist damit kein M1-Abnahmekriterium. Für den
Mini-Prototyp reicht die Routen-Linie als eigene Alpha-Ebene, die später über Video gelegt
wird — passt zum Datenmodell (`MapClip.blend`).

`staticmap` bleibt als Dependency in `pyproject.toml` für M3 stehen, wird in M1 nicht
importiert (keine Netzwerkabhängigkeit in Tests).

102 Tests grün (`tests/test_map.py` neu: Frame-Anzahl, RGBA-Transparenz, wachsende Route,
konfigurierbare Auflösung, Fehler bei <2 Punkten), `ruff` sauber, `doctor` grün.

### M1.7 — Notizen (2026-07-27)

`render.py`: `build_filtergraph` baut Input-Liste + `-filter_complex`-String rein aus
`Timeline` + einem `resolve_asset`-Callback (kein I/O, daher ohne echte Dateien testbar).
Video-Spur: pro Clip `trim`/`setpts` (Fotos: `-loop 1` + `trim=duration=…`), dann
`scale+pad` auf `timeline.resolution`, hart aneinandergeschnitten (`concat`). Overlay-PNGs
und Karten-Clips werden per `overlay`-Filter mit `enable='between(t,…)'`-Zeitfenstern
komponiert (Karten-Clips zusätzlich per `setpts=PTS+{tl_in}/TB` auf ihre Timeline-Position
verschoben, da sie als eigenständige Clips bei `t=0` beginnen). Audio: pro Clip
`atrim`/`adelay`/`volume`, alle Spuren per `amix` gemischt; Ducking ist eine statische
`volume`-Filterkette mit `enable`-Fenstern auf der Musikspur (kein echtes Sidechain-
Compressing).

**Bewusst nicht in M1:** `transition_in`/`effects` (Crossfades, Ken-Burns-Zoompan) werden aus
der Timeline gelesen, aber noch nicht gerendert — harte Schnitte reichen für "abspielbares
Video, das den Brief erfüllt" (Plan §10-Abnahme), echte Übergänge/Zoompan sind Kandidat für
M2. Kein Rendering von `transition_in`/`transition_out` heißt: die entsprechenden JSON-Felder
sind schema-gültig, werden vom Renderer aber ignoriert.

Nebenbei zwei kaputte CLI-Stellen geschlossen: `cli.py preview` rief bisher nur den
Platzhalter-Text auf — ruft jetzt `render.render_proxy` echt auf und setzt die Export-Phase
auf `PREVIEWED`. `render_proxy` löst Asset-IDs über `assets.json` + `ingest.proxy_path` auf
(nicht per Dateiname-Glob — Asset-IDs und Dateinamen sind unterschiedliche Namensräume).

End-to-end manuell verifiziert: `frameforge new` → `ingest` → (Asset per `write_asset`
eingetragen, Timeline von Hand geschrieben) → `frameforge preview` erzeugt ein abspielbares
320×240-MP4 (~1.5s, H.264), Export-Phase springt korrekt auf `PREVIEWED`.

111 Tests grün (`tests/test_render.py` neu: 7 reine Filtergraph-String-Tests + 2 Tests mit
echtem `ffmpeg`-Lauf gegen die Fixture, inkl. `probe_video`-Verifikation der Ausgabe), `ruff`
sauber, `doctor` grün.

---

## Details zu den offenen Tasks

### Task 2 — Kern-Module
Rückgrat, alles andere hängt daran. Reihenfolge innerhalb des Tasks:
1. `frameforge/state.py` — Phasen `INIT → INGESTED → INDEXED → DESIGNED → BRIEFED →
   STORYBOARDED → TIMELINE → ASSETS_BUILT → PREVIEWED → APPROVED → RENDERED`,
   Lesen/Schreiben von `.state.json`, Prüffunktion `require(phase)`, Invalidierungslogik
   (Brief geändert → Export zurück auf `BRIEFED`; neues Material → Projekt auf `INGESTED`)
2. `frameforge/project.py` — Auflösung Projekt-/Export-Pfade, `project.yaml` laden,
   externes `media_root`, Cache-Verzeichnis `~/.cache/frameforge/<project-hash>/`
3. `frameforge/timeline.py` — Pydantic-Modelle für das Schema aus Plan §4. Wird von
   `render.py` **und** `nle.py` gelesen — beide dürfen kein eigenes Schema bekommen.

**Abnahme:** `pytest` deckt verbotene Phasensprünge und Schema-Validierung ab.

### Task 3 — CLI + Stubs
`cli.py` mit typer: `doctor`, `status`, `new`, `ingest`, `index`, `query`, `design`, `brief`,
`build`, `preview`, `render`, `approve`. Übrige Module aus Plan §1 als Stubs mit Signaturen
und Docstrings (`ingest`, `probe`, `analyze`, `keyframes`, `index`, `gpx`, `audio`, `design`,
`map`, `render`, `nle`, `qc`).

`doctor` prüft: ffmpeg, ffprobe, exiftool, libcairo (siehe HANDOVER — Preload nötig),
Python-Version, Schreibrechte im Cache.

**Abnahme:** `python -m frameforge doctor` grün.

### Task 4 — Gate-Hook
`PreToolUse` auf `Bash`. Erkennt `ffmpeg`/`ffprobe`/`frameforge`-Aufrufe, liest `.state.json`,
blockt bei Verstoß mit Exit-Code 2 und einer Meldung, die den nächsten fälligen Schritt nennt.
Nackte `ffmpeg`-Aufrufe ausserhalb von `frameforge.render` sind immer blockiert.

**Abnahme:** verfrühter `render`-Aufruf wird nachweislich abgelehnt.

### Task 5 — Agenten + Commands
8 Agenten laut Plan §5 (Modellzuordnung beachten: `story-architect` und `qc-reviewer` = Opus,
Rest Sonnet). 9 Slash-Commands laut Plan §1.

### Task 6 — Docs
`CLAUDE.md` erweitern (Prozessregeln, Token-Disziplin aus Plan §3), `docs/process.md`,
`docs/styles/style-catalog.md` mit den 6 Presets aus Plan §6, `README.md`,
Projekt-Skeleton unter `templates/project/`.

### Task 7 — Abnahme M0
`pytest tests/ -v` grün, `doctor` grün, Gate-Test bestanden. Danach ist M0 fertig und M1
(Mini-Prototyp) beginnt.

---

## Notizen / Entscheidungen während der Umsetzung

### Task 2 — Nachbesserung (2026-07-27)

Die drei Punkte aus der Prüfung sind behoben:

**1. Gate-Loch geschlossen.** Neuer Sentinel-Wert `Phase.NEW = -1` (keine echte Prozessphase,
liegt unterhalb `INIT`) ist jetzt der Default für `ExportState.phase`. `ProjectState` trennt
Lesen (`_peek_export`, nicht-mutierend) von Schreiben (`advance_export`, `setdefault` nur dort).
`export_phase()`/`require_export()`/die Gates lesen jetzt nur noch — kein Phantom-Eintrag mehr
in `.state.json`. `gate_build(state, "gibts-nicht")` wirft korrekt `GateError`.

**2. Tests ergänzt.** `tests/test_state.py` (Phasensprünge, Gate-Loch als Regressionstest,
Persistenz-Roundtrip), `tests/test_timeline.py` (Feld- und Semantik-Validierung, Roundtrip),
`tests/test_project.py` (Pfadauflösung, `project.yaml`-Roundtrip). 26 Tests, alle grün,
`ruff` sauber.

**3. Designentscheidung getroffen:** `gate_render_final` bleibt bei strikter Gleichheit
(`!= APPROVED`). Grund: Plan Abschnitt 2 verlangt wörtlich "Export-Phase = APPROVED", und
CLAUDE.md fordert explizite Freigabe nach jedem Preview — auch ein Re-Render eines bereits
`RENDERED`-Exports muss also erneut durch `APPROVED`. Kommentar im Code verweist auf diese
Begründung, damit die Entscheidung nicht erneut aufgemacht wird.

### Task 3 — CLI + Stubs (2026-07-27)

`cli.py` (typer) mit `doctor`, `new`, `status`, `list`, `ingest`, `index`, `query`, `design`,
`brief`, `build`, `preview`, `render`, `approve`. Jedes gate-pflichtige Kommando ruft die
passende `gate_*`-Funktion aus `state.py` selbst auf (Gürtel + Hosenträger vor dem Hook aus
Task 4). Übrige Module als Stubs — `probe`, `analyze`, `keyframes`, `gpx`, `audio`, `map`,
`render`, `nle` werfen `NotImplementedError` mit Verweis auf den zuständigen Meilenstein.
Drei Module haben bereits echte (kleine) Implementierung statt reinem Stub, weil sie ohne
CV-/FFmpeg-Pipeline auskommen: `ingest.hash_file` (Cache-Schlüssel aus Plan §3),
`index.query_assets`/`load_assets` (liest/filtert `assets.json`), `qc.validate` (delegiert an
`Timeline.validate_semantics()`).

**Cairo-Fix aus HANDOVER.md korrigiert.** Der dort vorgeschlagene Ansatz (libcairo per
`ctypes.CDLL(pfad, RTLD_GLOBAL)` vorladen) wurde beim Implementieren empirisch widerlegt —
macOS' Loader dedupliziert beim Nachladen per nacktem Namen (`libcairo.2.dylib`) nicht über
bereits geladene Images, egal mit welchem `mode`. Ebenso wirkungslos: `DYLD_FALLBACK_LIBRARY_PATH`
zur Laufzeit in `os.environ` setzen — dyld liest `DYLD_*` nur beim Prozessstart, nicht bei
jedem `dlopen`. Tatsächlicher Fix in `frameforge/design.py::preload_cairo()`: `cairocffi`
importiert `find_library` aus `ctypes.util` beim eigenen Modul-Import und nutzt dessen
Rückgabewert für `ffi.dlopen()`. Patcht man `ctypes.util.find_library`, bevor `cairosvg`/
`cairocffi` zum ersten Mal importiert werden, damit es für `cairo-2`/`cairo`/`libcairo-2` den
Homebrew-Pfad liefert, funktioniert `import cairosvg` reproduzierbar. Verifiziert über
`python -m frameforge doctor` (libcairo-Check jetzt grün) und `tests/test_design.py`.
**HANDOVER.md ist an dieser Stelle veraltet** — der dortige Codeblock beschreibt den
verworfenen Ansatz, nicht den tatsächlich verwendeten.

**Abnahme erfüllt:** `python -m frameforge doctor` grün (Exit 0, alle 6 Checks OK). Gate-Test
manuell verifiziert: `render` vor `approve` liefert `GateError` (Export-Phase NEW, erforderlich
APPROVED), `index` vor `ingest` liefert `GateError` (Projekt-Phase INIT, erforderlich INGESTED).
55 Tests grün, `ruff` sauber.

### Task 4 — Gate-Hook (2026-07-27)

`.claude/hooks/gate.py` als `PreToolUse`-Hook auf `Bash`, verdrahtet in `.claude/settings.json`
über `$CLAUDE_PROJECT_DIR/.venv/bin/python $CLAUDE_PROJECT_DIR/.claude/hooks/gate.py` (Pfade
über die von Claude Code bereitgestellte Variable, damit der Hook unabhängig vom `cwd` der
Session funktioniert).

Der Hook zerlegt `tool_input.command` in einzelne Segmente (getrennt durch `&&`, `;`, `|`,
Zeilenumbrüche) und blockt mit Exit-Code 2, sobald ein Segment:
- `ffmpeg`/`ffprobe` nackt aufruft (immer verboten, unabhängig vom Pfad/Argumenten), oder
- einen `frameforge`-Unterbefehl (`index`, `brief`, `build`, `preview`, `render`) mit einem
  Projekt/Export aufruft, dessen `.state.json`-Phase die jeweilige `gate_*`-Funktion aus
  `state.py` nicht erfüllt — dieselbe Logik, die `cli.py` bereits selbst prüft.

Bewusst **kein** eigenes Regelwerk im Hook — er importiert `frameforge.state`/`frameforge.project`
direkt, damit Gate-Logik nur an einer Stelle gepflegt wird.

**Abnahme erfüllt:** 15 neue Tests in `tests/test_gate_hook.py`, davon zwei End-to-End über
echten Subprozess-Aufruf mit JSON-Payload (verifiziert Exit-Code 2 + Meldung auf stderr für
einen nackten `ffmpeg`-Aufruf, Exit-Code 0 für Nicht-Bash-Tools). Unit-Tests decken blockierte
und erlaubte `ffmpeg`-Varianten, alle fünf gate-pflichtigen `frameforge`-Unterbefehle vor/nach
Phasenerreichung sowie unbekannte Projekte ab. 70 Tests insgesamt grün, `ruff` sauber.

### Task 5 — Agenten + Commands (2026-07-27)

8 Agenten unter `.claude/agents/` laut Plan §5, Modellzuordnung wie vorgegeben:
`story-architect` und `qc-reviewer` = `model: opus`, Rest `model: sonnet`. Tool-Zugriff pro
Agent aus der Plan-Tabelle übernommen (`qc-reviewer` z.B. nur `Read, Bash`, kein `Write` —
er prüft, er ändert nichts; `story-architect` nur `Read, Write`, kein `Bash` — er trifft
Entscheidungen, führt keine Kommandos aus).

9 Slash-Commands unter `.claude/commands/` (`ff-new`, `ff-ingest`, `ff-index`, `ff-design`,
`ff-brief`, `ff-build`, `ff-preview`, `ff-render`, `ff-status`) — jeder verweist auf die
passenden `frameforge`-CLI-Kommandos aus Task 3 und die Agenten, an die delegiert wird.
`ff-status` leitet aus der State-Machine-Phase explizit den nächsten erlaubten Schritt ab
(Tabelle Phase → Befehl), statt nur den rohen State auszugeben.

Kein `pytest`-Abnahmekriterium für diesen Task (reine Markdown-Definitionen) — verifiziert
über ein Skript, das alle 17 Dateien parst und das YAML-Frontmatter validiert (`name`/
`description`/`tools`/`model` bei Agenten, `description`/`argument-hint` bei Commands).
Bestehende 70 Tests weiterhin grün, `ruff` unverändert sauber (diese Dateien sind kein
Python-Code).

### Task 6 — Docs (2026-07-27)

`CLAUDE.md` erweitert: "ab Task 4"-Vorbehalt beim Prozess-Constraint-Abschnitt entfernt
(Gate-Hook ist jetzt aktiv), `doctor`-Beschreibung präzisiert, neuer Abschnitt "Aktueller
Stand der Werkzeugschicht" (welche Module echt implementiert vs. Stub sind, Verweis auf
PROGRESS.md), `.claude/commands/` und `.claude/hooks/` in der Struktur ergänzt.

Neu: `docs/process.md` (Prozess als Referenz für Menschen — Phasentabelle, Gate-Tabelle,
Invalidierung, Agenten-Rollen), `docs/styles/style-catalog.md` (alle 6 Presets aus Plan §6
als YAML-Fragmente), `README.md` (Setup, Nutzung, Struktur), `templates/project/README.md`
(dokumentiert die von `frameforge new` erzeugte Struktur — kein Template-Engine-Input, `new`
baut die Ordner direkt in `cli.py`).

Keine funktionalen Code-Änderungen. 70 Tests weiterhin grün, `ruff` sauber, `doctor` grün.

### Task 7 — M0-Abnahme (2026-07-27)

Alle Kriterien aus Plan §10 erfüllt:

- `pytest tests/ -v` — **70/70 grün**.
- `ruff check frameforge/ tests/ .claude/hooks/gate.py` — sauber.
- `python -m frameforge.cli doctor` — **Exit 0**, alle 6 Checks (Python, ffmpeg, ffprobe,
  exiftool, libcairo, Cache-Verzeichnis) grün.
- Gate-Test auf beiden Durchsetzungs-Ebenen verifiziert (frisches Test-Projekt `proto`,
  danach wieder entfernt): `frameforge render proto teaser-90s` vor jedem vorgelagerten
  Schritt → Exit 1, Meldung "Export-Phase NEW — erforderlich mindestens: APPROVED". Derselbe
  Aufruf simuliert als Hook-Payload (`echo '{"tool_name":"Bash",...}' | gate.py`) → Exit 2,
  identische Meldung auf stderr. Nackter `ffmpeg`-Aufruf über den Hook → Exit 2, Verweis auf
  `frameforge render`/`preview`.

**Abweichung von Plan §10 dokumentiert:** Die dortige Beispielsyntax
(`frameforge render --project proto --export teaser-90s`) nutzt Flag-Optionen; `cli.py`
(Task 3) implementiert `project`/`export` als **positionale** Argumente
(`frameforge render proto teaser-90s`). Funktional identisch, nur andere Aufrufsyntax —
wurde beim Schreiben von `cli.py` so entschieden (typer-Konvention für Pflichtargumente)
und hier nachträglich vermerkt, weil Plan §10 das Original-Beispiel zeigt.

**M0 ist damit fertig.** Alle 7 Tasks abgeschlossen und gepusht. Nächster Schritt laut Plan:
M1 — Mini-Prototyp end-to-end (`projects/proto/` mit 3–5 Clips, 2 Fotos, kurzer GPX-Spur,
komplett durch die Pipeline bis zu einem abspielbaren 60–90-s-Preview). Das erfordert, die
bisherigen Stubs (`ingest.scan_media`, `probe.py`, `analyze.py`, `keyframes.py`, `index.
write_asset`, `render.build_filtergraph`/`render_proxy`, `design.build_svg_from_tokens`/
`render_svg_to_png`, `map.render_route_frames`) durch echte Implementierungen zu ersetzen.

### M1.8 — Notizen (2026-07-27)

`projects/proto/` komplett durch die Pipeline gebaut: `new` → `ingest` → `index` (CV-Analyse +
Keyframes + Beschreibungen für 3 Clips + 2 Fotos, deterministisch statt über den
`media-indexer`-Agenten — siehe unten) → `design` (Tokens) → `brief` → Beat-Sheet →
`timeline.json` (5 Video-Clips, 1 Titel-Overlay, 1 Karten-Clip, Musik + 1 O-Ton-Fenster mit
Ducking) → `frameforge preview` liefert ein abspielbares 10.5s/320×240-H.264-MP4.

**Abweichung vom Plan, bewusst und begründet:** Das Testmaterial
(`tests/fixtures/proto_media/`, winzige synthetische FFmpeg-Testsrc-Clips + generierte
Fotos) ist absichtlich sekundenkurz — echtes 60–90s-Footage für einen "Norwegen-Roadtrip"
zu simulieren wäre unehrlich. `brief.yaml` setzt `target_duration_s: 12` statt der
60–90s aus Plan §8; die Pipeline-Mechanik (Gates, Ingest, Index, Design, Brief, Timeline,
Render mit Overlay/Karte/Audio-Mix/Ducking) ist dieselbe, die auch ein echtes Projekt
durchläuft. Aufbau-Skript: `tests/fixtures/build_proto_project.py` (reproduzierbar via
`.venv/bin/python tests/fixtures/build_proto_project.py`).

**`media-indexer`-Agent nicht live aufgerufen.** Asset-Beschreibungen/Tags/Ratings für die
5 synthetischen Test-Assets sind im Build-Skript hart codiert statt von Claude Vision
generiert — bei reinem FFmpeg-Testsrc-Rauschen und Einfarb-Fotos gäbe es nichts Sinnvolles
zu beschreiben. Die reale Nutzung über `/ff-index` mit dem `media-indexer`-Agenten ist davon
unberührt (Task 5), dieses Skript ersetzt sie nur für das Test-Fixture.

**Zwei Bugs beim ersten echten End-to-End-Lauf gefunden und behoben, beide in
`render.build_filtergraph`:**

1. **Runaway (unendliche Render-Laufzeit).** `ffmpeg`s `overlay`-Filter hat einen eigenen
   `shortest`-Parameter (default `0`), unabhängig vom globalen `-shortest`-Flag. Das
   Titel-Overlay-PNG kommt als `-loop 1`-Input ohne Ende herein; ohne `shortest=1` am
   Overlay-Filter wartet `ffmpeg` auf das Ende des **längeren** Inputs (des unendlichen
   Bildes) statt auf das Ende des kürzeren Hauptvideos — der Render lief 30+ Minuten und
   wuchs unbegrenzt (38 MB und weiter), bis er manuell gekillt wurde. Fix: `shortest=1` an
   beiden `overlay`-Aufrufen (Titel- und Karten-Kompositing).
2. **Deadlock im ffmpeg-Scheduler** (nach Fix 1 reproduziert, mit `sample`/`sch_wait`
   diagnostiziert): der komplexe Graph mit 9 Inputs (davon zwei `-loop 1`-Bilder, eines
   *ohne* `-framerate`) blockierte den internen Scheduler dauerhaft — 0 % CPU, keine
   Fortschritt über 5+ Minuten. Fix: `-framerate {timeline.fps}` auch am Overlay-PNG-Input
   gesetzt (Konsistenz mit den bereits `-framerate`-versehenen Foto-Inputs der Video-Spur).
   Nach beiden Fixes lief der komplette 9-Input-Graph durch, ohne zu hängen.

**Zusätzliches Sicherheitsnetz ergänzt:** `render._run_ffmpeg` hat jetzt ein Timeout
(`max(120, duration*30)` Sekunden) und wirft `RenderError` statt den Prozess unbegrenzt
laufen zu lassen — hätte Bug 1 automatisch nach 315s abgebrochen statt manuellen Eingriff
zu brauchen. Regressionstests: `tests/test_render.py` prüft jetzt explizit `shortest=1` im
generierten Filtergraph und rendert einen echten Clip mit Overlay End-to-End.

**Nebenbei gefundener Infrastruktur-Bug:** die editable Installation aus Task 1
(`uv pip install -e ".[dev]"`) hatte keinen funktionierenden Editable-Finder in
`site-packages` — `import frameforge` funktionierte nur zufällig, weil `pytest` und
`python -m frameforge` immer mit `cwd` = Repo-Root liefen (das setzt `sys.path[0]`
implizit auf den Ort, an dem `frameforge/` liegt). Ein eigenständiges Skript wie
`build_proto_project.py`, aus einem anderen Verzeichnis oder direkt per Dateipfad gestartet,
schlug fehl. Fix: `uv pip install -e ".[dev]" --reinstall-package frameforge` — legt jetzt
`_editable_impl_frameforge.pth` in `site-packages` an. Kein Code-Fix nötig, reine
Umgebungskorrektur; für zukünftige Sessions relevant, falls `.venv/` neu aufgesetzt wird.

`.gitignore` um `projects/*/.state.lock` ergänzt (Lock-Datei-Artefakt, gehört nicht ins Repo).

**M1 (Mini-Prototyp end-to-end) ist damit komplett.** Alle 8 Teilschritte fertig. `pytest`
grün (113 Tests), `ruff` sauber, `doctor` grün, `projects/proto/` mit Config/Index/Design/
Route/Brief/Beatsheet/Timeline im Repo (Render-Artefakte wie gehabt via `.gitignore`
draussen). Nächster Meilenstein laut Plan: M2 — Story-Engine vertiefen (Clip-Scoring,
Musik-Sync auf Beat-Grid, `qc-reviewer` mit echtem Regelsatz, echte Übergänge/Ken-Burns im
Renderer).

### Hinweis zu Commit `849ff6d`

Der Initial-Commit hat den damals frisch geschriebenen Task-2-Code versehentlich mit
eingesammelt (zwei Sessions liefen kurzzeitig parallel im selben Repo). Die Commit-Message
sagt deshalb fälschlich, es gäbe noch keinen Anwendungscode. Rein kosmetisch — nicht
nachträglich reparieren, der nächste Commit stellt es gerade.

**Regel daraus:** immer nur eine Session gleichzeitig in diesem Repo arbeiten lassen.

---

## M5 — Norwegen-Realbetrieb: offener Punkt aus dem ersten echten Lauf (2026-07-31)

Beim ersten echten `frameforge ingest norwegen-2026` (Nutzer-Rückfrage: was passiert, wenn
während/nach der Pipeline noch neues Rohmaterial in `media_root` dazukommt, z.B. Videos/Fotos
gegen Ende des Urlaubs) beim Nachlesen des Codes eine Lücke zwischen Plan und Implementierung
gefunden — **kein Bug im engeren Sinn, nichts ist kaputt, aber noch nicht gebaut**:

Plan Abschnitt 2 (Zeile 165) sagt: *"Kommt neues Rohmaterial dazu, fällt das Projekt auf
INGESTED zurück — aber der Analyse-Cache bleibt, es werden nur die neuen Hashes verarbeitet."*
`state.py` hat dafür bereits `invalidate_project()`/`invalidate_export()` sowie einen
`content_hash`-Parameter auf `advance_project()`/`advance_export()` — **beides wird aktuell
von keinem Aufrufer benutzt.** `ensure_project_at_least()` (Audit-Fix P5) springt bewusst nur
vorwärts, das war zum Schutz gegen versehentliches Zurückfallen bei erneutem `ingest`/`index`
gedacht (Audit-Finding), verhindert aber als Nebeneffekt auch die im Plan vorgesehene
Rückwärts-Invalidierung bei echtem neuem Material.

**Eingrenzung, was davon betroffen wäre** (nicht pauschal "alles neu machen"):

- `DESIGNED` (Tokens/Farben/Fonts) und `BRIEFED` (Kreativ-Brief) hängen inhaltlich nicht vom
  Asset-Inventar ab — neues Material macht sie nicht ungültig.
- `STORYBOARDED` ist der erste Schritt, der `query_assets()` gegen `assets.json` nutzt
  (`story-architect`) — hier könnte neues Material tatsächlich ein besseres Beatsheet
  ermöglichen, das der Export sonst nie sieht. `TIMELINE` und alles danach ist nur indirekt
  betroffen (nur falls das Beatsheet neu gebaut wird).
- Der sinnvolle Ansatzpunkt ist also der **Export-Status ab STORYBOARDED**, nicht die globale
  Projekt-Phase.

**Vorgeschlagener Mechanismus** (noch nicht umgesetzt, Nutzer-Entscheidung: erstmal nur
dokumentieren, `M5` läuft ja gerade real):

1. Billiger, zustandsloser Check (`scan_media()` gegen Hashes in `assets.json`), der
   unabhängig von der aktuellen Phase überall (z.B. in `frameforge status`) mitlaufen kann —
   kein Vision-Call, keine Kosten.
2. Beim Erreichen von `STORYBOARDED` einen Hash über den aktuellen `assets.json`-Stand im
   bereits vorhandenen `content_hash`-Feld ablegen; bei späteren Schritten vergleichen.
3. Bei Abweichung **warnen und fragen, nicht still neu bauen** — kein Hintergrund-Worker,
   explizite Rückfrage an den Nutzer (passt zum bestehenden Wizard-Prinzip: "Stand zeigen,
   nächsten Schritt erklären, fragen").

**Bis dahin manuell:** nach neuem Material in `media_root` erneut `/ff-ingest` + `/ff-index`
anstoßen — beides ist idempotent/inkrementell (übersprungene Proxies, nur ungehashte Assets
gehen an den `media-indexer`-Agenten), aber es passiert nicht von selbst, und ein bereits über
`INDEXED` hinaus fortgeschrittenes Projekt merkt eine neue unindizierte Datei nicht
automatisch.

---

## Fundus-Erweiterung „Christina-iPhone" (2026-08-07) — **fertig (Fotos + Videos)**

Neuer Ordner `Christina-iPhone/` im `media_root`, vom Nutzer vorsortiert: **127 HEIC + 30 JPG
= 157 Fotos** bereits vorbereitet (Keyframes + CV-Analyse per Skript unter Umgehung von
`ingest`). Die **65 MOV/MP4-Videos** waren zunächst vom Nutzer zurückgehalten (noch nicht
selbst gesichtet/geschnitten); nach Freigabe am 2026-08-07 waren es beim tatsächlichen
`ingest`-Lauf **47 Videos** (Nutzer hatte zwischenzeitlich selbst vorsortiert/geschnitten,
u. a. `IMG_2889` in zwei Cuts geteilt).

| Schritt | Status |
|---|---|
| `prepare-index` (Fotos, per Skript) — Keyframes, CV, `captured_at`, GPS | ✅ 157/157 |
| Inhaltliche Sichtung Fotos (Beschreibung/Tags/Rating/Source) | ✅ **157 von 157** |
| `ingest` Videos (47 MOV/MP4, Proxies) | ✅ 47/47 |
| `prepare-index` Videos — Keyframes, CV | ✅ 47/47 |
| Inhaltliche Sichtung Videos (Beschreibung/Tags/Rating/Source) | ✅ **47 von 47** (2 parallele media-indexer-Batches) |

**Datumslücke bei geschnittenen Videos:** 37 der 47 Videos hatten `captured_at_source:
container` (aus dem MOV-Container gelesen, nicht EXIF) — beim Schneiden/Trimmen gehen bei
manchen Tools die iPhone-Metadaten verloren, `captured_at` fiel dann auf das Kopierdatum
(heute) zurück. Bei 24 davon lag das Datum nachweislich außerhalb des Reisezeitraums
(20.07.–04.08.). Nutzer-Entscheidung: **manuell zuordnen statt automatisch/ignorieren.**
10 eindeutig zum Cluster Aurlandsfjord/Flaamsbana (24.–25.07.) passende Clips (Fjordblick,
Regenbogen, Wasserfall+Ruine, Kreuzfahrtschiff×2, Fähre, Schafherde, Passstraße,
Bogenschießen) wurden per Skript auf `captured_at_source: manual` gesetzt, Uhrzeit geschätzt
(Reihenfolge plausibel, keine Sekundengenauigkeit). **14 Videos bleiben mit unplausiblem
Datum offen** — IMG_3587, 3590, 3304, 3610, 3260, 3104, 3061, 3434, 3270, 3462, 2864, 2867,
2889_Cut-2, 2824 — Zuordnung zu Etappen-Cluster vom Nutzer noch zu klären.

**Ratingverteilung Videos grob:** einige starke Establisher (Fjord mit Fähre/Nebel,
Regenbogen über Fjord, Wasserfall mit Ruine, Berggipfel über See) mit 4–5, viel Autofahrt-/
Passstraßen-B-Roll mit 2–3, zwei lange monotone Tunneldurchfahrten (`IMG_2886`, ~4 Min;
`IMG_2889_Cut-2`, ~67s) markiert als Timelapse/Speed-Ramp-Kandidaten (Tag `lang-monoton`,
siehe Editing-Präferenz unten).

**Neue Nutzer-Vorgabe für den Schnitt:** lange, inhaltlich monotone Clips (Tunnelfahrten,
lange Autofahrten) nicht einfach kürzen, sondern per Timelapse/Speed-Ramp (Verzögerung →
Beschleunigung, Wechsel in Slow-Mo bei epischen Momenten) filmisch verdichten. Relevant für
`story-architect`/`timeline-builder`, noch nicht in Style-Katalog nachgezogen.

## Routen-/Kilometer-Aufbereitung (2026-08-07)

Auf Nutzerwunsch: Fotos/Videos (Chris- + Christina-iPhone), Tagebuch (`route/diary.md`),
Google-Maps-Screenshot der Roadtrip-Schleife und die bereits erfassten `stages.csv`/
`locations.csv` zu einem plausiblen Gesamtbild kombiniert.

**Zwei GPX-Dateien, unterschiedlicher Zweck:**
- `route/photo-points.gpx` — 663 echte GPS-Punkte aus Chris-/Christina-iPhone-EXIF, gesamter
  Reisezeitraum (17.07.–04.08.) lückenlos. Für „wo wurde was aufgenommen" (Asset-Platzierung),
  **nicht** als Streckengeometrie geeignet (Standtage erzeugen durch GPS-Rauschen künstliche
  Kilometer, roher Punktabstand kam auf 3532 km).
- `route/roadtrip.gpx` — echtes Straßen-Routing (OSRM) über die Etappenpunkte,
  117.845 Punkte. Gut für die Kartenlinie. Fährtage (2, 18) treibt der Autorouter auf absurde
  Landumwege hoch — für die Gesamt-km unbrauchbar, dafür gilt `stages.csv`.

**Kilometer-Korrektur nach Nutzer-Feedback (zwei Runden):** Tag 2 (Flensburg→Skien) und Tag 18
(Skien→Grevenbroich) in Fahrt-Etappen aufgeteilt (Anfahrt zum Fährhafen + Weiterfahrt nach der
Überfahrt). Aktivitätstage (3, 4, 5, 10, 13) hatten fälschlich 0 km — Nutzer bestätigte reale
Kurzstrecken (Hütten-/Küstenausflüge, Einkaufsfahrten), jetzt 10–40 km je Tag statt 0.

Erste Runde: Fährstrecke zunächst mit 0 km angesetzt (keine gefahrene Strecke). **Zweite Runde,
Nutzer-Korrektur:** doch mitzählen — „überwundene Kilometer", auch wenn nicht selbst gefahren,
nur klar als Seeweg kennzeichnen. Fährdistanz Hirtshals–Larvik als Luftlinie ermittelt
(`gpx.haversine_km`, 162,5 km), in Tag 2 und Tag 18 zum jeweiligen Auto-Anteil addiert statt
als eigene Zeile (Schema kennt nur eine Etappe je Kalendertag), im `via`-Text und in der `note`
explizit als „Auto" vs. „Fähre (Seeweg)" aufgeschlüsselt. Neue Summe: **3829 km** (390+162,5
Tag 2, 890+162,5 Tag 18). Ursprünglicher Nutzer-Bauchgefühl „knapp bei 4000" damit näher
getroffen als die reine Auto-Summe (3504 km).

**Fehlende Koordinaten ergänzt** in `locations.csv`: `Valdresflye (Fv51)` mit **echter
GPS-Koordinate** aus `Christina-iPhone/IMG_3437.HEIC` (61.42736, 8.80273, 1183 m — höchster
real gemessener Punkt der ganzen Reise), `Lærdalstunnel` und `Storsæterfossen` (geschätzte
Koordinaten, keine Fotobelegung). Bewusst **nicht** geraten: `Numedal` (Talregion, kein
Punkt), `Fv40` (Straßenbezeichnung, kein Punkt), `Hütte` als Via-Punkt an Tag 16 (uneindeutig,
welche Hütte gemeint ist) — bleiben als Lücken in `route-build`-Warnungen sichtbar statt
falsch aufgelöst zu werden.

**Höhenprofil:** `route.elevations_for` (Open-Meteo, 301 Stichproben entlang der Route,
projektweit gecacht in `elevation.json`) bestätigt den höchsten Punkt unabhängig: 1157 m
(gegen 1183 m aus der echten GPS-Messung — Abweichung durch Downsampling/Streckenabschnitt
statt exaktem Fotopunkt). Kumulierter Anstieg über die Stichprobe: ~14.200 Höhenmeter — grobe
Schätzung, keine kontinuierliche Aufzeichnung.

**Zeitraum:** 2026-07-20 bis 2026-08-04, deckt sich mit dem bestehenden Reisezeitraum
(Chris-iPhone-Fundus 17.07.–04.08.). Aufnahmeort-Cluster grob: Waldsee-Huette (20.–23.07.),
Aurlandsfjord/Flaamsbana (24.–25.07.), Geirangerfjord/Trollstigen (26.–28.07.), Lom/Stabkirche
(28.–30.07.), Huette am Fluss mit historischer Bruecke (29.07.–02.08.), Kuestenbucht mit
Angeln/Baden (03.–04.08.), Ruecktransfer/Faehre (04.08.).

**Quellenzuordnung (`source`):** 127 Fotos hatten `source_guess: phone` (IMG_*.HEIC/JPG mit
Apple-EXIF), 30 zeigten `source_guess: unknown` (UUID-Dateinamen ohne verwertbare EXIF —
vermutlich über Messenger/AirDrop geteilte Fotos ohne Metadaten-Erhalt). Da die Motive
inhaltlich klar zum selben Fundus gehören (gleiche Reise, gleiche Personen, gleiche
Bildsprache wie die benannten IMG_*-Dateien), wurde bei allen 30 `unknown`-Faellen manuell
auf `phone` gesetzt — keiner zeigte Anzeichen einer anderen Aufnahmequelle (keine
Drohnen-Vogelperspektive, keine Action-Cam-Weitwinkel-Verzerrung).

**Ratingverteilung grob:** viele starke Establisher (Fjord-Panoramen, Regenbogen ueber dem
Fjord, Geirangerfjord-Aussichtspunkte, Trollstigen-Vogelperspektive, beleuchtete Bruecke bei
Nacht, tuerkise Kuestenbucht) mit 4–5, dazwischen viel Familien-B-Roll (Angeln, Wandern,
Faehrfahrten) mit 3–4, sowie einige reine Cutaways/Meilensteine (Navi-Display,
Kilometerstand-Fotos) mit 1–2.

**Zwei Auffaelligkeiten waehrend der Sichtung:**
1. Die anfaengliche Worklist-Momentaufnahme enthielt zunaechst nur 145 der 157 Fotos; 12
   weitere (IMG_3458–IMG_3609, luecke zwischen 29.07. und 01.08.) tauchten erst bei einer
   spaeteren `index-todo`-Abfrage auf und wurden nachtraeglich einzeln gesichtet und
   indiziert. Alle 157 sind bestaetigt in `assets.json` (`grep -c Christina-iPhone` = 157).
2. **Keine Video-Datei aus `Christina-iPhone/` erschien in `index-todo`** — die Erwartung im
   Auftrag ("falls doch eine MOV/MP4-Prep-Datei erscheint, waere das ein Bug") ist nicht
   eingetreten. Die Vorbereitung war sauber auf die 157 Fotos beschraenkt.

**Naechster Schritt:** Sobald der Nutzer die 65 Christina-iPhone-Videos vorbereitet
(`ingest` + `prepare-index`), erscheinen sie ueber `index-todo norwegen-2026` und koennen wie
gewohnt an den `media-indexer` gegeben werden — bis dahin bleibt der Christina-iPhone-Fundus
bei 157/222 (Fotos komplett, Videos offen).

---

## Export-Vorbereitung Norwegen-2026 (2026-08-07) — Status fuer Session-Uebergabe

Fundus ist vollstaendig indiziert (975 Assets). Vier Exporte geplant, mit dem Nutzer
besprochen und Namen/Laengen festgelegt:

| Export | Laenge | Inhalt |
|---|---|---|
| `drone-edit` | 10–14 Min. (flexibel, Material entscheidet) | nur Drohnenmaterial, keine Karte, Schwarzblende Anfang+Ende |
| `vlog-edit` | ~20 Min. | Vollversion mit Karten-HUD, Etappen-/Kilometerdetails |
| `vlog-pur` | ~20 Min. | gleicher Schnitt wie `vlog-edit`, ohne Karte/Detail-Layer (nur Ortsnamen) |
| `teaser` | offen, straff, nicht hart auf 5 Min. | Highlight-Mix, 80/20 Landschaft/Personen, **keine** inhaltlich redundanten Cutaways (Lehre aus einem frueheren Testschnitt: 5 Szenen vom selben Kreuzfahrtschiff an einem Tag wirkte repetitiv) |

**Reihenfolge:** mit `drone-edit` anfangen (kleinster Scope, kein Kartenbau/Ortszuordnung
noetig, testet den vollen Pfad Brief→Beatsheet→Timeline→Preview zuerst am billigsten Fall).

### Route nachgezogen

`route/stages.csv` deckte den 2026-07-17 (Verladen zuhause, 6 Assets) nicht ab — per
`route-planner`-Agent ergaenzt (neue Zeile Tag 1, alle Folgetage day-Nummer +1,
`locations.csv`-Day-Referenzen mitgezogen). Dry-Run von `assign-places` bestaetigt: 07-17
nicht mehr in der "Tag fehlt"-Liste. **Noch nicht committet.**

### Bekannter Datenfehler: 14 Christina-iPhone-Videos mit falschem Aufnahmedatum

Beim Schneiden/Export auf dem iPhone hat Apple beim Re-Encode ein neues Container-Datum
geschrieben (Schnitt- statt Aufnahmedatum) — betrifft laut Nutzer-Erinnerung ca. 46 Videos,
32 davon wurden in einer frueheren Sitzung bereits manuell auf das richtige Datum korrigiert
(`captured_at_source: manual`). **14 sind noch offen**, alle mit `captured_at` faelschlich auf
"heute" (Datum des jeweiligen Chat-Tages, hier 2026-08-07) statt des echten Aufnahmetags:
`IMG_2824, IMG_2864, IMG_2867, IMG_2889_Cut-2, IMG_3061, IMG_3104, IMG_3260, IMG_3270,
IMG_3304, IMG_3434, IMG_3462, IMG_3587, IMG_3590, IMG_3610` (alle `Christina-iPhone/`).
Kein automatisches Matching moeglich (keine ungeschnittenen Geschwister-Dateien mit gleicher
IMG-Nummer im Index gefunden). Inhalte laut Sichtung streuen ueber mehrere Tage (Tunnel+Faehre
+Fjord passt zu 07-26, Hochebenen koennten 07-24 oder 07-29 sein, Campingplatz-Teich mit Kind
eher 07-30/31) — **muss einzeln mit dem Nutzer per Keyframe geklaert werden**, keine Prioritaet
fuer `drone-edit` (nutzt kein iPhone-Material).

### Musik

`music/` enthaelt Originals (Interpret/Album/Titel-Unterordner) + KI-Generated:

| Track | Ordner | BPM | Laenge | Status |
|---|---|---|---|---|
| Naturaleza (Mose Edit) | Originals/Mose & Danit | 68,9 | 7:25 | Pflicht |
| Cuatro Vientos | Originals/Danit | 147,7 | 7:27 | Pflicht, **schnell** — Kandidat fuer `teaser` |
| Aguila de Oro (Ecstatic Mix) | Originals/Little Whale, Sariel Orenda & UAK | 82,0 | 6:15 | Kandidat |
| Tejedora Cósmica | Originals/Little Whale | 143,6 | 6:52 | Kandidat, **schnell** |
| Nordlichter im Sturm (Suno) | KI Generated | 125,0 | 3:52 | KI-generiert, Referenz-Stil fuer weitere KI-Prompts |

Alle 5 analysiert (BPM/Beat-Grid/Energiekurve, `frameforge.audio.analyze_and_cache`), Cache
liegt unter `music/analysis/`. M4A liest `librosa` problemlos ueber den `audioread`/ffmpeg-Pfad,
keine Konvertierung noetig.

**Gefundene Luecke:** kein CLI-Kommando fuer Musik-Analyse — der `audio-designer`-Agent
(`.claude/agents/audio-designer.md`) geht davon aus, dass er sie "ueber die CLI ausloest",
es existiert aber keine `frameforge`-Subcommand dafuer. Analyse wurde stattdessen direkt per
Python (`frameforge.audio.analyze_and_cache`) angestossen. Kein Blocker fuer den ersten Export
(Cache ist jetzt gefuellt), aber fuer neue Tracks spaeter faellt die Luecke wieder auf —
Nachtrag waere ein kleiner CLI-Befehl `frameforge analyze-music <projekt> <datei>`.

### Brief-Vorgaben fuer `drone-edit` (vom Nutzer, 2026-08-07)

- Keine Karte, Schwarzblende am Anfang und am Ende.
- Ramps/Slow-Motion erwuenscht, nicht zu viele harte Cuts, Drohnenbilder duerfen atmen (nicht
  zu schnell geschnitten).
- Laenge flexibel 10–14 Min., je nach Material.
- Audio nicht hart abschneiden: Ein-/Ausblenden (~3 s), erster Track startet ruhig.
- Musik: die zwei Pflicht-Tracks (Naturaleza Mose Edit, Cuatro Vientos), keiner davon komplett
  durchlaufen lassen, fliessender Uebergang dazwischen — evtl. 3 Abschnitte à ca. 4 Min.
- Intro-Grafik: "Norwegen 2026" (oder "Norwegen"), darunter kleiner/versetzt "Drone Edit",
  eventuell norwegische Flagge, langsames ruhiges Einblenden. Falls das bestehende
  Titel-Template das nicht hergibt, Grafik-Prompt an den Nutzer statt selbst zu improvisieren.

**Naechster Schritt:** `/ff-brief norwegen-2026 drone-edit` mit obigen Vorgaben, danach
Beat-Sheet + Timeline bauen.

### Beat-Sheet + Timeline fuer `drone-edit` gebaut (2026-08-07)

`/ff-build norwegen-2026 drone-edit` durchlaufen. Export ist jetzt **TIMELINE** (Gate
`frameforge build` gruen).

- **Beat-Sheet** (`story-architect`, Opus): 10 Kapitel K0–K9, 720 s Ziellaenge, chronologisch,
  reiner Drohnen-Pool (`source=drone`, `rating>=3`, 280 Clips verfuegbar).
  - 25.07. und 27.07. ohne Drohnenmaterial (Regen bzw. reines iPhone-Doku in Geiranger) — ueber
    Nachbartage erzaehlt.
  - `exclude: true`-Clips respektiert (u. a. 31.07.-Clip "Drohne in Ast").
  - `original_audio_policy: ambience_only` aus dem Preset fuer diesen Export unbrauchbar
    (Drohnen-Rotorgeraeusch) — bewusst auf reine Musik umgestellt.
  - Intro-Grafik: Template deckt Titel/Unterzeile/Einblenden ab, aber nicht "versetzte
    Unterzeile" oder Flaggen-Motiv. Nutzer hat sich fuer **Fallback** (Template pur, keine
    Flagge) entschieden statt Grafik-Prompt zu beauftragen.
- **Timeline** (`timeline-builder`, Sonnet): 719,76 s, 97 Video-Clips (95 Assets), 3 Audio-Clips,
  1 Titel-Overlay. K8 (01.08., "letzte Passstrasse") entfallen — indiziertes Material war
  Motorradtreffen statt der vorgesehenen Solo-Szene; Budget auf K7/K9 verteilt (Beat-Sheet-eigene
  Fallback-Regel). K5 (Trollstigen-Klimax) nutzt denselben 152s-Clip 3x als Sub-Segmente
  (slow-mo/ramp/slow-mo) — einziges taugliches Material fuer den Moment, jetzt per
  `intentional_repeat: true`-Marker dokumentiert statt als QC-Fehler markiert.
- **Schema-Erweiterung:** `AudioClip.src_in` in `frameforge/timeline.py` ergaenzt (Source-Offset
  in Sekunden, analog `VideoClip.src_in`), `render.py` entsprechend angepasst
  (`atrim=start={src_in}`). Grund: Beat-Sheet brauchte zwei verschiedene Ausschnitte desselben
  Tracks (Naturaleza Mose Edit, Anfang + spaeterer ruhigerer Abschnitt fuer den Ausklang) — das
  Schema kannte bislang nur Trackanfang. Rueckwaertskompatibel (Default 0). Tests: 135 passed.
- **QC-Nacharbeit:** `qc.validate()` fand 4 Probleme (Rundungs-Overlap K0/K1, zwei
  Mikro-Luecken im K5-Klimax-Segment, Asset-3-fach-Nutzung) — alle vor dem Gate-Build gefixt.
  `frameforge/qc.py` um Ausnahme fuer `intentional_repeat: true` erweitert (generischer
  Mechanismus, kein Einzelfall-Hack).

**Naechster Schritt:** `/ff-preview norwegen-2026 drone-edit` — Proxy-Render pruefen, danach
Freigabe. Danach vlog-edit, vlog-pur (~20 Min, identischer Schnitt, nur Map-Layer
unterschiedlich), dann teaser.

### Preview v1 gesichtet, Timeline Revision 2 (2026-08-08)

Erster Proxy-Preview gerendert und vom Nutzer gesichtet. Feedback fuehrte zu einer kompletten
Timeline-Revision (Beat-Sheet + timeline.json neu gebaut), danach zweiter Preview-Render
erfolgreich (`exports/drone-edit/preview/drone-edit_preview.mp4`, 568,0 s, 80 Video-Clips,
2,02 GB, `qc.validate()` leer, `validate_semantics()` ok). Export steht bei **PREVIEWED**,
wartet auf Nutzer-Freigabe (`approve`) vor dem Final-Render.

**Aenderungen gegenueber Revision 1** (alle aus Nutzer-Feedback nach dem ersten Preview):

- **Keine Fotos/Ken-Burns mehr** — reiner Drohnen-Video-Reel, wie im Brief eigentlich schon
  gefordert; Revision 1 hatte faelschlich 2 Foto-Assets mit Ken-Burns in K4 eingebaut.
- **Nur noch 2 Audio-Abschnitte statt 3** (Naturaleza Mose Edit + Cuatro Vientos, kein
  Naturaleza-Reprise-Abschnitt mehr) — der dritte Abschnitt/zweite Crossfade klang hallig/
  "schallend". Ziellaenge dadurch von 720 s auf 568 s reduziert (`brief.yaml`
  `target_duration_s`/`structure_hint` angepasst).
- **Kein `speed > 1.0` mehr im ganzen Film** — Nutzer mochte die Hyperlapse-/Timelapse-Ramps im
  Preview nicht (`transition_vocabulary` in `brief.yaml` um `speed_ramp` gekuerzt). Slow-Mo
  (`speed < 1.0`) an einzelnen epischen Momenten bleibt erlaubt. **Widerspricht der bisherigen
  Editing-Praeferenz** (Timelapse/Ramps statt Kuerzen bei langen Clips, siehe
  Session-Memory `project_norwegen_editing_prefs`) — die ist nach dieser Sichtung entsprechend
  revidiert.
- **Generelles Qualitaetskriterium ergaenzt:** Clips nicht nur nach Gesamt-Stabilitaets-Score im
  Index auswaehlen, sondern auf unruhige Schwenks *mitten im Take* pruefen (Beispiel:
  `20260730-drone-4abe2d`, Bruecke/Kinder, Stabilitaet 0.0) — bei Verdacht `src_in`/`src_out`
  enger um den ruhigen Teil legen statt ganzen Clip verwerfen. Als Session-Memory
  `feedback_shaky_clips` festgehalten, da laufendes Kriterium fuer kuenftige Timeline-Bauten.
  Der Index liefert bislang nur einen Stabilitaets-Wert pro Clip, keine Segment-Aufloesung —
  offener Verbesserungspunkt fuer spaeter.
- **Mehr Top-Down/Vogelperspektive-Shots** eingebaut (6 Slots definiert, alle gefunden, u. a.
  der vom Nutzer explizit gelobte senkrechte Fluss-Shot in Lom).
- **Neuer Clip:** `20260803-drone-574c7c` (Moewe an Felseninsel, Angelplatz Langesund) als
  eigener Beat in K9 eingebaut, `src_in≈26.5-34.2`.
- **K8 (01.08., Motorrad-Rastplatz Uvdal→Skien) entfernt** — der `timeline-builder` hatte es
  zunaechst wieder eingebaut (Rating/Exclude-Kriterien erfuellt), aber Sichtpruefung zeigte
  eindeutig Menschen-/Fahrzeug-lastiges Material (Dutzende Motorraeder/Fahrer), das den
  fast-menschenfreien Stil ausserhalb K7/K9 gebrochen haette. Manuell entfernt, Zeit an
  K7-Schlussclip angehaengt (Timeline-Laenge/Audio-Sync-Punkte unveraendert).
- **Crossfade-Timing gestrafft** — Default-Dissolve innerhalb von Kapiteln von 1,2 s auf
  0,5-0,7 s verkuerzt (verhindert den "Schlier"-Effekt bei Bewegung-auf-Bewegung-Ueberblendung),
  mehrere Kapitieluebergaenge auf harten Schnitt umgestellt. Der gelobte Wind-Uebergang
  K2→K3 (1,2 s) blieb unangetastet.
- **Neues Render-Feature: animierte Overlays.** `OverlayClip.anim` unterstuetzt jetzt
  `slide_from_px`/`slide_in_s`/`drift_px`/`drift_period_s` (generischer Mechanismus, nicht
  Einzelfall-Hack) — Intro-Titel "Norwegen 2026" kommt von links, Unterzeile "Drone Edit" von
  rechts eingeflogen, konvergieren zur Mitte, driften leicht gegenlaeufig waehrend der
  Hold-Phase, blenden gemeinsam aus. Zwei neue SVG-Templates (`title-only.svg`,
  `subtitle-only.svg`) statt einem kombinierten Titel-Card-Template fuer diesen Export.
  `frameforge/render.py`: `build_filtergraph` baut jetzt eine Zeitausdruck-Expression fuer
  `overlay`s `x`-Parameter statt fest `x=0`; ohne die neuen `anim`-Felder unveraendertes
  Verhalten (getestet gegen bestehende `test-timelapse-journey`-Overlays). 3 neue Regressionstests
  in `tests/test_render.py`.
- **Font geaendert:** `design/tokens.yaml` `font_display`/`font_text` von "Helvetica Neue" auf
  "Avenir Next", `title-card.svg`/die neuen Only-Templates mit `font-weight` 900 (Titel) bzw.
  700 (Unterzeile) — Nutzer fand die vorherige Schrift zu zart, wollte kraeftiger/moderner,
  nicht kursiv. Farben (helles Blau/Orange) unveraendert, waren schon passend.

**Naechster Schritt:** Nutzer sichtet `drone-edit_preview.mp4`, gibt frei oder gibt weiteres
Feedback. Bei Freigabe: `/ff-render norwegen-2026 drone-edit` fuer den 4K-Final.

### `drone-edit` fertig gerendert (2026-08-08)

Preview v2 freigegeben, `frameforge approve` + `frameforge render` durchgelaufen. Export ist
**RENDERED**, Pipeline fuer `drone-edit` komplett:
`projects/norwegen-2026/exports/drone-edit/final/drone-edit_v1.mp4` (4K, 5,77 GB, 568 s), Report
unter `.../final/drone-edit_v1.report.md`.

**Naechster Schritt:** vlog-edit, vlog-pur (~20 Min, identischer Schnitt, nur Map-Layer
unterschiedlich), dann teaser — kein Re-Ingest/Index/Design noetig, gleiche Materialbasis.

### `vlog-edit` gebrieft (2026-08-08)

`exports/vlog-edit/brief.yaml` geschrieben, Export auf **BRIEFED**. Preset `nordic-cinematic`
mit Overrides: `map_usage: leitmotif` (Karte unten rechts durchgehend), Ziellaenge 1200 s
(~20 Min). Wichtigste Vorgaben aus dem Nutzer-Briefing:

- **Cold Open, 30 s:** reiner Wind-/Ambient-Teil von "Cuatro Vientos" (erster von drei
  Pflicht-Tracks), dazu eine Karten-Overview-Animation (Route Deutschland→Daenemark→Norwegen
  waechst), danach leichte Blende ins erste Norwegen-Bild. Bild-Schnittfrequenz zieht erst an,
  wenn das Audio lauter/hoeher wird. Zusaetzlich eine Infokarte mit Reisedaten. **Kein neuer
  Sub-Agent dafuer** — bleibt ein Beat im Beat-Sheet, gebaut von story-architect +
  timeline-builder + map-animator wie jeder andere Abschnitt auch; ein eigener
  "Intro-Editor"-Agent haette keinen Zustaendigkeitsbereich, den diese drei nicht schon
  abdecken.
- **Musik:** feste Reihenfolge Cuatro Vientos → Naturaleza (Mose Edit) → Aguila de Oro
  (Ecstatic Mix), fliessende Crossfades, aber zuegig (~10 s, keine 30-s-Doppel-Ueberlagerung).
- **Karte:** unten rechts (`render_inset_frames`), **keine Hoehenmeter** — `heights=None` beim
  Aufruf reicht, bestehender Mechanismus, kein neuer Code noetig. Nur Ortsname/Etappe +
  gesamt gefahrene Strecke bis zur aktuellen Position (`cumulative_km`, das liefert das
  Template ohnehin schon als `km_label`).
- **Ken Burns:** darf nie schwarzen Hintergrund zeigen — Bildflaeche muss immer voll gefuellt
  sein.
- **Redundanz:** dieselbe Szene nicht aus zu vielen Perspektiven hintereinander (Beispiel aus
  der Sichtung: Bruecke mehrfach aus verschiedenen Winkeln direkt hintereinander).
- **Fehlende Video-Timestamps:** viele iPhone-Videos (Chris-iPhone, Christina-iPhone) ohne
  `captured_at`-EXIF. Laut Nutzer sind die Dateien innerhalb ihres jeweiligen Ordners in
  echter Erlebnis-Reihenfolge — Dateisystem-/Namensreihenfolge als Fallback-Sortierung nutzen.

**Naechster Schritt:** `/ff-build norwegen-2026 vlog-edit` (story-architect → timeline-builder,
plus map-animator fuer die Cold-Open-Kartenanimation und die durchgehende Karte).

### `vlog-edit` Timeline gebaut, QC gefixt, Preview gerendert (2026-08-08)

`/ff-build norwegen-2026 vlog-edit` durchlaufen, Export auf **TIMELINE** (`09115087a`): 159
Video-Clips, 14 Map-Clip-Referenzen, 7 Audio-Clips, 2 Overlays, 1103,887 s. Fixpunkte
(Cold-Open 40 s, Crossfade 395 s, harter Schnitt 730 s, Klimax 996 s, Filmende) sitzen.

- **Karten-/Grafik-Render** (`a87299a2`): Cold-Open-Overview (K0, `generated-map-k0-cold-open`)
  als neues Asset indiziert, 14 Karten-Insets (K2-K15, `heights=None`) + Titel-/Infokarte
  gerendert. Neues Template `templates/svg/infocard.svg`.
- **Render-Fix, projektuebergreifend** (`6212b8af`): Foto-Ken-Burns padden bisher mit schwarzen
  Balken bei Nicht-16:9-Fotos (37 % der Clips in diesem Export betroffen) —
  `_scale_pad` durch `_scale_crop` (increase+crop) ersetzt. Neue `_face_crop_center()` legt das
  Crop-Fenster auf erkannte Gesichter (`index/people.json`, `frameforge faces` — **die
  Gesichtserkennung war zu diesem Zeitpunkt bereits fertig**, wird hier erstmals im Render
  genutzt), 15 %-Sicherheitsrand fuer Ken-Burns-Pan, faellt ohne Gesichter auf zentrierten Crop
  zurueck. Bonus-Fix: `_kenburns_expr` interpolierte x/y-Pan-Offsets bisher nicht, jetzt schon.
- **QC-Runde 1** (`b13aef7c`): 7 blockierende Befunde gefixt — Rundungsfehler an zwei
  Fixpunkten (550,4 s/730,0 s), falsches Klimax-Motiv (Trollstigen statt Lom-Nacht), fehlende
  Tunnelausfahrt bei 730 s, Renderabbruch durch tonlosen Atmo-Clip, K12 komplett falsch belegt,
  Kreuzfahrtschiff-Redundanz mehrfach ueber Deckel, fehlender Fischfang-Beat in K15.
  Photoserien-/Selfie-/Wasserfall-Deckel fuer K2-K5/K9/K10/K14 bewusst zurueckgestellt
  (dokumentiert, nicht blockierend).
- **QC-Runde 2** (`3ea2e39d`): 3 Clip-Swaps — 730 s-Fixpunkt war invertiert (hell→dunkel statt
  dunkel→hell), Wasserfall- und Bruecken-Aufnahme je einmal doppelt verwendet. Alle drei
  getauscht, Timing/Fixpunkte unveraendert.
- **Preview:** `/ff-preview norwegen-2026 vlog-edit` gerendert,
  `exports/vlog-edit/preview/vlog-edit_preview.mp4` (186 MB). Export steht bei **PREVIEWED**,
  wartet auf Nutzer-Freigabe.
- **Notiz zur Session:** Notebook-Speicher lief waehrend eines vorherigen Preview-Versuchs voll
  (24 GB durch VS Code + andere Apps + Claude), System abgestuerzt, `.state.json`/Commits blieben
  konsistent, nur `PROGRESS.md` und der Preview-Render selbst (0-Byte-Datei) hingen nach. Zweiter
  Preview-Versuch nach Neustart erfolgreich (Plattenplatz zwischenzeitlich knapp bei 4 GB frei,
  danach wieder auf 10 GB erholt). Kein Hinweis auf Datenverlust bei Timeline/Assets/Commits.
- **Hinweis, nicht blockierend:** `frameforge status` meldet, dass sich das Asset-Inventar seit
  dem Storyboard von `drone-edit` und `vlog-edit` geaendert hat (neues Asset
  `map-k0-cold-open.mp4` seither indiziert). Fuer `vlog-edit` ist das erwartet — Cold-Open-Karte
  wurde bewusst nachtraeglich generiert und ist bereits Teil der Timeline. Fuer `drone-edit`
  (bereits gerendert) irrelevant.

**Naechster Schritt:** Nutzer sichtet `vlog-edit_preview.mp4`, gibt frei oder gibt Feedback. Bei
Freigabe: `/ff-render norwegen-2026 vlog-edit` fuer den 4K-Final. Danach `vlog-pur` (identischer
Schnitt, nur Map-Layer anders), dann teaser.

### `vlog-edit` Preview-Feedback Runde 1: Karten-HUD, Cold-Open, Titel (2026-08-08)

Nutzer sichtete den PREVIEWED-Stand (Screenshot) und meldete drei Befunde zurueck.

- **Leeres `HÖHE`-Label im Karten-HUD:** `render_inset_frames` zeigte trotz `heights=None`
  (Brief verbietet Hoehenmeter) weiterhin Caption+Platzhalter ("HÖHE"/"—") rechts im
  Werteband, weil `frameforge/design.py` den Token `elevation_caption` immer setzt.
  `frameforge/map.py`: `elevation_label`/`elevation_caption` sind jetzt leer, wenn `heights`
  fehlt — die ganze Spalte verschwindet, kein Platzhalter mehr. Neuer Test
  `test_inset_hides_elevation_column_without_heights` (`tests/test_map.py`). Alle 14
  Karten-Insets (K2-K15) ueber `projects/norwegen-2026/route/map-animator-recipe.py` neu
  gerendert.
- **"Hochkant"/falsche Rotation im ersten Preview:** Nachrecherchiert (Output-Datei direkt
  per `ffprobe`/Frame-Extraktion geprueft) — die gerenderte Datei war durchgehend korrekt
  3840×2160, 16:9, ohne Rotationsmetadaten, Karten-Inset korrekt unten rechts. Kein
  Pipeline-Bug gefunden; vermutlich ein QuickTime/macOS-Anzeigeglitch direkt nach dem
  Systemcrash aus der vorherigen Session. Zweiter Preview-Render zeigte dasselbe (korrekte)
  Bild.
- **Cold-Open-Kartenanimation (K0) raus, komplett** (Nutzerentscheidung, nicht nur Stilwechsel):
  Strassenkarten-Look der OSM-Tiles bei Laendermassstab wirkte "verzerrt"/unlesbar. Ersetzt
  durch ein reines Schwarzbild (neues generiertes Asset `generated-cold-open-black`,
  `_generated/cold-open-black.jpg`) bei unveraenderten Timing-Fixpunkten (0-40 s, Dissolve
  38-40 s in K1) — Wind-Intro von "Cuatro Vientos" laeuft weiter unveraendert. Karten-Cold-Open
  als Konzept (3D/topografische/isometrische Kartenanimation) bewusst zurueckgestellt, kein
  Ersatzstil sofort gebaut.
- **Titelkarte komplett neu:** "Roadtrip" aus dem Titel raus (nur noch "Norwegen"), "2026" als
  eigene Zeile, "Roadtrip Edition" als kleine Caption nachgeschoben. Infocard
  (Reisedaten/km) komplett entfernt — Nutzer fand die Zusatzinfo unnoetig und schlecht lesbar.
  Lesbarkeit generell gefixt: `title-only.svg`/`subtitle-only.svg` bekommen ein
  halbtransparentes Panel hinter dem Text (dieselbe Panel-Farbe/-Deckkraft wie die
  Bauchbinden), neue Layout-Tokens `title_panel_y/h`, `subtitle_panel_y/h` in
  `frameforge/design.py`.
- **Render-Engine erweitert, generisch:** `frameforge/render.py` konnte Overlay-Slide-in bisher
  nur horizontal (`_overlay_x_expr`). Auf `_overlay_axis_expr(from_key, drift_key)`
  refaktoriert, `_overlay_x_expr`/neue `_overlay_y_expr` sind duenne Wrapper darueber —
  Overlays koennen jetzt auch von oben/unten einlaufen (`slide_from_py`/`drift_py` in
  `OverlayClip.anim`), ohne Sonderfall-Code. "Norwegen" kommt jetzt von oben, "2026" von
  rechts, beide konvergieren zur Mitte (wie beim `drone-edit`-Titel, nur mit vertikaler statt
  zwei-horizontalen Bewegungen). 4 neue/angepasste Tests in `tests/test_render.py`.
- **Pre-existing, nicht angefasst:** `tests/test_design.py` hat 6 vorbestehende Fehlschlaege um
  `infocard.svg` (fehlende `info_main`/`info_sub`-Default-Tokens), verifiziert auch auf dem
  Stand vor dieser Session (`git stash` + Testlauf). Nicht Teil dieser Aenderung, da `infocard`
  fuer `vlog-edit` ohnehin entfernt wurde — Fix bei Bedarf spaeter, wenn `infocard.svg` wieder
  gebraucht wird.
- **Preview neu gerendert**, alle drei Befunde visuell verifiziert (Frame-Checks bei Cold-Open,
  Titel, Karten-HUD). Export bleibt PREVIEWED, wartet auf Freigabe.
- **Disk-Space-Warnung:** Beim Neu-Rendern der 14 Karten-Insets blieben 13 GB PNG-Frames im
  Scratchpad liegen (Platte fiel auf 538 MB frei) — sofort geloescht. Nutzer arbeitet mit sehr
  wenig freiem Plattenplatz (~12-13 GB) nach dem Notebook-Crash aus der vorherigen Session;
  `test-timelapse-journey`-Export (RENDERED, 2,5 GB) als Loeschkandidat identifiziert, Nutzer
  hat noch nicht entschieden.

**Naechster Schritt:** Nutzer sichtet den ueberarbeiteten Preview, gibt frei oder gibt weiteres
Feedback (offen: ob/wie ein neues Cold-Open-Konzept mit Karte kommen soll).

### `vlog-edit` Preview-Feedback Runde 2: Render-Bug, Cold-Open kuerzer, Titel-Choreo, Karten-Stil, Bauchbinden (2026-08-08)

**Session per Nutzerwunsch hier abgebrochen (Token/Kontext sparen) — siehe "Offener Punkt beim
Abbruch" unten.** Alles bis dahin ist committet und funktioniert einzeln (Tests gruen), nur der
**finale Voll-Preview mit allen Aenderungen zusammen wurde noch nie erfolgreich durchgerendert.**

**Gefundener Bug (kritisch, betraf vermutlich auch Runde 1 im Hintergrund):** Der Karten-Clip-
Layer in `build_filtergraph` (`frameforge/render.py`) nutzte `shortest=1` auf dem `overlay`-
Filter. Der Karten-Clip ist aber ein endliches `-i`-Input (kein `-loop 1` ohne `-t` wie das
Text-Overlay, wo `shortest=1` tatsaechlich noetig ist) — `shortest=1` kappt den KOMPLETTEN
bisher aufgebauten Video-Pfad, sobald eines der beiden Inputs sein Ende erreicht. Der erste
Karten-Clip (K2, endete bei 132s) schnitt so den gesamten restlichen Film ab; Audio lief
unbeeinflusst weiter. Ergebnis: Preview-Datei mit korrektem Audio (voller Laenge) aber Video-
Track nur ~132-142s lang — QuickTime zeigt sowas als eingefrorenes Bild/verzerrtes
Player-Fenster an, **das war sehr wahrscheinlich auch die Ursache des "Hochkant"-Befunds aus
Runde 1**, nicht ein Anzeige-Glitch wie dort vermutet (mein Frame-Check damals lag zufaellig vor
der Kapp-Stelle bei ~90s). Fix: `shortest=1` bei der Karten-Overlay-Zeile entfernt, Regressions-
test ergaenzt (`tests/test_render.py`). **Folge:** die tatsaechliche Preview-Datei ist jetzt
~7x groesser als vorher gedacht (voller Frame-Count statt ~140s) — ca. 1,6-2 GB statt 200 MB,
das hat die Platte beim ersten Vollrender-Versuch dieser Runde gesprengt (`No space left on
device`, Datei korrupt, geloescht).

**Weiteres Nutzerfeedback umgesetzt** (Timeline, Templates, Recipes — alles committet):

- **Cold-Open halbiert:** 40s -> 10s reines Schwarzbild, alles danach um 30s nach vorne
  verschoben (`c000.src_out`, alle spaeteren `tl_in` in `video`/`map`/`audio` minus 30,
  `brief.yaml` `target_duration_s` von 1104 auf 1074 korrigiert). Neue Gesamtlaenge 1073,887s.
- **Titel komplett neu choreografiert** (Nutzer wollte diagonal-dynamisch statt zentriert-
  gestapelt): EINE schmale Box (nur "2026"-Breite) unten rechts, "Norwegen" (weiss, gross, noch
  15% groesser als vorher) fliegt von links ein und ragt oben drueber hinaus, "2026" (weiss,
  75% von Norwegens Groesse) und "Roadtrip Edition" (Akzentfarbe/gelb, 75% von 2026, verzoegert)
  sitzen als zwei Zeilen in/auf der Box, alles mit leichtem Drift waehrend der Hold-Phase.
  Templates `title-only.svg`/`subtitle-only.svg` generisch auf frei positionierbare Texte
  umgebaut (`text_x_pct`/`text_y_pct`/`text_anchor`, `subtitle_fill`) statt fest zentriert;
  neues `box-only.svg` fuer ein eigenstaendiges Panel, unabhaengig vom Text positionierbar.
  Reproduzierbares Rezept: `exports/vlog-edit/title-recipe.py`. Vor dem Einbau in die echte
  Timeline mit einer synthetischen Mini-Timeline (nur 12s) probegerendert, um nicht wieder einen
  vollen 18-Minuten-Render zu verschwenden — Methode fuer kuenftige Overlay-Iterationen merken.
- **XML-Kommentar-Falle gefunden:** `--` (doppelter Bindestrich) in SVG-Kommentaren bricht
  cairosvgs strikten XML-Parser ("not well-formed"). In den drei neuen/geaenderten Templates
  durch Kommas ersetzt. Gilt fuer alle kuenftigen Template-Kommentare in diesem Projekt.
- **Karten-Insets ueberarbeitet:** Zoom je Kapitel um +2 erhoeht (naeher dran, Strassen-
  /Ortsnamen lesbar), Box-Groesse 640x360 -> 768x432 (+20%), Route/Positionsmarker von Orange
  auf Blau (`INSET_ROUTE_COLOR`/`INSET_MARKER_COLOR` in `route/map-animator-recipe.py`),
  Ortsnamen-Labels von Weiss auf Schwarz (`INSET_LABEL_COLOR`) — `frameforge/map.py` bekam dafuer
  neue Parameter `marker_color`/`label_color` (vorher hart auf `MARKER_COLOR` verdrahtet, Route
  und Beschriftung liessen sich nicht unabhaengig einfaerben). Karten-Positions-Rand in
  `render.py` von 20px auf 60px vergroessert (Nutzer wollte mehr Abstand). Alle 14 Insets neu
  gerendert (`rebuild_map_insets.py`-Muster, nicht committet, siehe unten).
  **Bekannte Grenze, keine Fehlkonfiguration:** Strassenfarben etc. AUF der Kachelkarte selbst
  (z.B. der orange Fernstrassen-Belag) kommen aus dem OSM-Rasterkachel-Stil und sind nicht
  einfaerbbar, ohne den Tile-Server/-Stil zu wechseln — nur unsere EIGENE gezeichnete
  Fortschritts-Route + Marker + Labels sind parametrisiert.
- **Neue Bauchbinden bei der Karte:** "Tag N · Ort" blendet kurz (4s) ein, wenn ein neues
  Karten-Kapitel beginnt, dann wieder aus (Kilometerstand bleibt der einzige Dauer-Text).
  Tag-Zaehlung ist die des Nutzers (Tag 0 = Beladen 17.07., nicht `stages.csv`-Tag 1) —
  `last_day - 1`. K12 ausgelassen (reine Wiederholung von K11/Lom). Reproduzierbares Rezept:
  `exports/vlog-edit/stage-caption-recipe.py`.

**Commits dieser Runde:** `6e67be7` (shortest=1-Fix + Regressionstest), Rest (Templates,
map.py-Parameter, render.py-Margin, Timeline-Umbau, Recipes, brief.yaml) **noch NICHT
committet** — siehe naechster Abschnitt.

**Offener Punkt beim Abbruch:** Preview mit ALLEN Aenderungen dieser Runde zusammen wurde noch
nie erfolgreich durchgerendert (erster Versuch lief in den Platz-Fehler wegen des frisch
gefixten shortest=1-Bugs, danach hat der Nutzer die Session zum Tokensparen abgebrochen, bevor
der zweite Versuch fertig war — laufender ffmpeg-Prozess wurde sauber gekillt, keine Daten-
verluste). **Naechster Schritt fuer die Folgesession:**
1. `git status` pruefen — falls die Aenderungen unten noch nicht committet sind, zuerst
   `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_design.py` (muss 501 gruen sein,
   die 6 `infocard.svg`-Fehlschlaege in `test_design.py` sind vorbestehend, siehe oben) und dann
   committen.
2. Vor dem Render: `df -h /` pruefen. Erwartete Preview-Groesse jetzt **~1,6-2 GB** (nicht mehr
   200 MB wie vor dem shortest=1-Fix!) — bei < 4 GB frei erst Platz schaffen (z.B. mit dem
   Nutzer klaeren, ob weitere fertige Exporte wie `drone-edit`s Preview-Zwischendateien weg
   koennen), sonst droht wieder "No space left on device".
3. `.venv/bin/frameforge preview norwegen-2026 vlog-edit` — laeuft laut bisherigen Versuchen
   >2 Minuten (Timeout), also mit `run_in_background` planen.
4. Nach Erfolg: Frame-Checks bei Cold-Open (sollte jetzt bei ~10s in K1 uebergehen), Titel-
   Sequenz (~t=12-24s: Box, dann Norwegen/2026 diagonal, dann Roadtrip Edition), Karten-Insets
   (blaue Route/Marker, schwarze Ortsnamen, kein HÖHE-Label, 60px Rand) und Bauchbinden (kurz
   nach jedem Kapitel-Start).
5. Dem Nutzer den fertigen Preview zur Sichtung geben.

### `vlog-edit` Preview-Feedback Runde 3: Zeitstempel-Befund, Karte raus, Blur-Fill (2026-08-08)

Sehr umfangreiches Nutzer-Feedback zur Preview-Runde 2 (Sichtung mit Pausen, ~60 Einzelpunkte
mit Zeitmarken). Der Grossteil liess sich auf **drei Ursachen** zuruecktrainieren, statt auf 60
Einzelfehler — das ist der eigentliche Ertrag dieser Runde.

**Befund 1 (wichtig, gilt fuer das ganze Projekt): iPhone-VIDEOS tragen `captured_at` in UTC,
iPhone-FOTOS und DJI-Dateien in Ortszeit (CEST, +2h).** QuickTime speichert `creation_time` in
UTC, die HEIC-Fotos derselben Kamera dagegen `DateTimeOriginal` als Ortszeit. Verifiziert an drei
unabhaengigen Tagen ueber Szenen, die beide Geraete aufgenommen haben:

| Szene | iPhone-Video | iPhone-Foto / Quelle | Differenz |
|---|---|---|---|
| 18.07. Kartenhaus fertig | `camera-bacc27` 16:39 | `phone-5439f6` 18:39 | genau 2:00 |
| 25.07. Bogenschiessen | `camera-4e8191` 12:25 | `phone-d56ddb` 14:24 | ~2:00 |
| 27.07. RIB-Tour | `camera-847bd7` 13:06 | `stages.csv` "RIB-Safari 15:00" | ~2:00 |

**Die Korrektur laesst sich NICHT am `source`- oder `source_guess`-Feld festmachen.**
`source_guess == "camera"` umfasst hier zwei ganz verschiedene Gruppen: 187 `Chris-iPhone/*.MOV`
bzw. `Christina-iPhone/*.MOV` (iPhone-Videos ohne EXIF-`make`, darum als "camera" geraten, +2h
noetig) und 37 `DJI_*.MP4` aus den Drohnen-Ordnern, deren Dateiname die Ortszeit traegt
(`DJI_20260720140953` zu `captured_at` 14:09, also KEINE Korrektur). Ausserdem stehen einige
`Christina-iPhone/*.MP4` unter `source_guess == "unknown"`, brauchen die Korrektur aber genauso.
Deshalb entscheidet in `rebuild-recipe.py` (`needs_utc_offset`) der **Pfad**: iPhone-Ordner +
Video-Endung. Achtung: Christinas Geraet weicht zusaetzlich anders ab (`20260807-camera-7c5d12`
passt auch mit +2h nicht zum Kjosfossen-Halt) — dort wurde der Clip von Hand einsortiert.

**Befund 2: die Clips waren innerhalb der Reisetage praktisch unsortiert.** Beispiel 19.07.:
13:16, 09:32, 15:04, 16:11, 13:04, 14:33, 18:58, 12:39, 18:14, 10:00, 06:40 — das Flensburg-
Morgenbild stand als LETZTER Clip des Tages. Fast alle vom Nutzer gemeldeten "Spruenge" und
"Logikfehler" gehen darauf zurueck (Wikingerdorf-Aktivitaeten vor der Ankunft ueber die Bruecke,
Unterkunft vor der Anfahrt, Grillen mitten im Seeausflug, Treppen- und RIB-Block verschraenkt).
Mit Befund 1 + chronologischer Sortierung ergibt sich die vom Nutzer gewuenschte Dramaturgie an
den meisten Stellen von selbst; die bewussten Abweichungen stehen als Kommentar im Rezept und
werden beim Lauf als "N Paar(e) bewusst gegen die Aufnahmezeit" gemeldet.

**Befund 3: Hochkant-Material war die Ursache fuer BEIDE Bildbeschwerden.** Fotos liefen ueber
`_scale_crop` (crop-to-fill) — das schnitt Personen an, sobald die Gesichtserkennung eine nicht
gefunden hatte, was bei Kindern mit Kappe/Sonnenbrille die Regel ist (Beispiel
`20260720-phone-01214e`: 3 Personen im Bild, 2 Gesichter in `people.json`, der Ausschnitt legt
sich auf die Union der 2 und schneidet genau Oskar weg — "man sieht nur seine Kaeppi"). Videos
liefen ueber `_scale_pad` (Letterbox) — die "dicken schwarzen Balken links und rechts".
Neu: `VideoClip.fit = "blur"` legt das **ungeschnittene** Bild zentriert auf eine formatfuellend
vergroesserte, weichgezeichnete Kopie. Kein Bildverlust, keine schwarzen Flaechen. 26 Clips
nutzen es (alle mit Seitenverhaeltnis < 1.05). Mit einem Mini-Render (3 Clips, 12s) gegen die
alte Variante geprueft, bevor es in die Timeline ging.

**Weitere Renderer-Aenderungen:**

- **Ken Burns hatte keine Varianz:** ALLE 59 Fotos trugen exakt dieselben Parameter
  (`from [0.06,0.06,1.0]` → `to [-0.02,-0.02,1.12]`), linear. Jeder Schnitt setzte den Schwenk
  auf denselben Startpunkt zurueck — genau das las der Nutzer als "geht nach rechts und dann
  nach links wiederum". Jetzt sechs Varianten (Zoom rein/raus, sanftes Pan, zwei Diagonalen),
  jede monoton in EINE Richtung, nie zweimal dieselbe hintereinander, plus `ease: "smooth"`
  (Smoothstep 3n²-2n³ statt linear). Default bleibt linear, bestehende Timelines unveraendert.
- **Overlay-Drift pendelte:** `drift_px` war ein `sin()` um die Endposition. Weil `overlay` die
  Position auf ganze Pixel rundet, sieht die Umkehr an den Sinus-Extrema (wo die Bewegung fast
  stillsteht) wie Ruckeln aus — der Nutzer: "das darf nicht so hin und her pixellig wirken, die
  sollen schon in ihre Richtung weitergehen". Neu `drift_mode: "linear"`: gleichmaessige Rampe
  in Slide-in-Richtung bis zum Clipende. Amplitude von 8 auf 56 px (4K) erhoeht, weil der Nutzer
  ausdruecklich MEHR Restbewegung wollte.
- **Ducking schaltete hart:** `volume=...:enable='between(t,a,b)'` wechselt den Pegel in einem
  Frame. Neu `duck_fade_s` — Rampe VOR und NACH dem O-Ton-Fenster
  (`volume=eval=frame:volume='1-G*clip(...)*clip(...)'`), damit der O-Ton ueber seine ganze
  Laenge den vollen Platz hat und die Musik weich runter- und wieder hochfaehrt.
- **Karten-Trim (war aus der Vorsession noch offen, jetzt committet):** die Kartendateien sind
  laenger als ihr Zeitfenster; ohne `trim=duration=` hing `overlay` den Dateirest ans Filmende.
  Das waren die ~17s Schwarzbild am Ende, die der Nutzer als "15 Sekunden Schwarzbild" gemeldet
  hat (1091,0s Datei vs. 1073,9s Timeline). Moot, weil die Karte jetzt ganz weg ist, aber der
  Fix bleibt drin.

**Schnittfassung neu gebaut** — `exports/vlog-edit/rebuild-recipe.py` (neu). Die Schnittfassung
steht dort als Asset-Liste je Reisetag mit Begruendung pro Abweichung; Timing, Uebergaenge,
Ken-Burns-Parameter, Bauchbinden-Timing und Audio rechnet das Skript daraus. Handarbeit an 168
Clips waere nicht wiederholbar gewesen.

- **Karte komplett ausgebaut** (Nutzer: "die ist nicht gross genug, sie lenkt ab — ich muss
  leider die Entscheidung treffen, dass wir die Karte ausbauen"). `tracks.map` bleibt als leere
  Liste im Schema, die 14 Insets unter `map/` bleiben liegen, werden aber nicht gerendert.
- **Bauchbinde uebernimmt die Orientierung**, unten links statt unten rechts, zweizeilig:
  "Tag N" (Akzentfarbe, Unterzeilen-Groesse) ueber "Von › Nach · XXX km" bzw. bei
  Aktivitaetstagen "Ort · Aktivitaet" ("Skien · Tag am Meer"). Tagesnummer ist die des Nutzers
  (`stages.csv`-Tag minus 1, Tag 0 = Beladen am 17.07.). Neues Template
  `templates/svg/stage-caption.svg`, Defaults dafuer in `design.overlay_tokens` (`stage_*`).
- **168 Clips** (vorher 159). 13 raus: angeschnittene Gesichter, Hochkant mit Balken, Doppelungen
  "Video dann Standbild derselben Szene" (Kartenhaus, Deck, Moewe), ein statischer Drohnenshot,
  der misslungene Bogenschuss, das Tablet-Foto, die Beeren-Nahaufnahme, die "hilflose"
  Bootsfahrt, ein doppelt verwendetes Asset (`20260727-drone-50a966` lief zweimal). 22 dazu:
  Kaffee + Hamburger Hafen auf der Strecke Tag 1, Blumenbeet vor Flensburg, Flaamsbahn-
  Establisher, Wikingerdorf-Ankunft, Geiranger-Ankunftsshot, Lom-Stabkirche aus der Luft +
  Angler mit Fisch, zwei Trollstigen-Talblicke, der gute Bogenschuss, vier Schaerenkuesten-
  Shots, Auffahrt aufs Faehrdeck, und ein **neues Kapitel 01.08. Uvdal › Skien** fuer den
  Uebergang, den der Nutzer vermisst hat.
- **Trollstigen umgebaut** (der Kern des Feedbacks): Aussichtsplattform vorgezogen, danach die
  Ausblicke, dann der Blick durchs Wolkenfenster ins Tal (`20260728-drone-c91b2a`) als Hoehepunkt
  an der richtigen Stelle und mit 14s Standzeit — vorher stand er als Nachklapp am Kapitelende.
- **Ducking nur noch an zwei Stellen** (Faehre/Oskar im Wind, Gitarre/Kitzeln). Raus bei
  Zugfahrt, Treppenaufstieg und Uvdal — alle drei hatte der Nutzer explizit abgelehnt. O-Ton von
  -18 auf **-6 dB** hoch, Musikabsenkung von -12 auf **-7 dB** ("nicht das eine leiser machen,
  sondern das andere ein bisschen hochziehen"), 0,7s-Rampen.
- **Titel:** "Norwegen" von 1.15x auf **2.2x** der Basisgroesse ("bestimmt doppelt so gross
  fast"). "2026"/"Roadtrip Edition" bleiben, der Groessenkontrast war gewollt.
- **Schlussschwarzbild 3s** mit Ausfaden.

Dauer **1073,500s** (Ziel aus `brief.yaml`: 1074) — die Pacing-Kurve des alten Schnitts
(vorne ruhig ~8s/Clip, im Roadtrip bis ~5,8s) ist absichtlich beibehalten, das Tempo hatte der
Nutzer nicht kritisiert.

**Tests:** 504 gruen. Die 6 `infocard.svg`-Fehlschlaege in `test_design.py` sind vorbestehend
(siehe oben). Neu abgedeckt: Blur-Fill-Statements, Ken-Burns-Easing, linearer Drift,
Duck-Rampen, Karten-Trim.

**Zwei Template-Fallen wieder zugeschlagen** (beide kosten sonst je einen Fehlversuch, siehe
auch `HANDOVER.md`): `--` in SVG-Kommentaren bricht cairosvgs XML-Parser; ein `&` in einem
Label (hier "Fjord & Wikingerdorf") ebenso, weil `build_svg_from_tokens` roh substituiert —
deshalb `xml.sax.saxutils.escape` im Rezept. Zusaetzlich neu: **Avenir Next hat keinen
`→`-Glyph**, cairosvg setzt ein Ersatzkaestchen (im ersten Bauchbinden-Render als Tofu-Box
sichtbar geworden). Geprueft, welche Trennzeichen die Schrift hat: `–`, `—`, `›`, `»`, `•`, `·`
rendern, `→` nicht. Verwendet wird jetzt `›`.

**Offener Punkt fuer die Rueckfrage an den Nutzer:** die "Moewen-Verfolgungsjagd", die er am
Schluss laenger sehen wollte, ist im Index nicht auffindbar — eine Volltextsuche ueber alle 1181
Assets nach Moewe/Vogel/Verfolgung liefert am Reiseende (03./04.08.) keinen Treffer. Muss er
zeigen bzw. benennen.

### Warum die `vlog-edit`-Preview-Renders abgebrochen sind (2026-08-09) — Ursache gefunden

Mehrere Renders waren "ohne Erklaerung" gestorben (Nutzer: vier bis fuenf Mal im Hintergrund,
einmal im Vordergrund durchgelaufen). Statt weiter zu raten, gemessen — und die Vermutung
"Hintergrund-Ausfuehrungspfad" war **falsch**:

| Zeitpunkt | Swap benutzt | frei auf / | ffmpeg |
|---|---|---|---|
| vor dem Start | 3,0 GB | 15 GB | — |
| +1 min | 9,8 GB | 8,3 GB | 428% CPU, RSS 1,8 GB |
| +4 min | 11,2 GB | 7,3 GB | laeuft |
| nach `kill -9` | 3,2 GB | 15 GB | — |

macOS legte beim Renderstart sieben neue Swapfiles an; nach dem Kill fiel alles sofort zurueck.
Es ist reiner Speicherdruck: der Render fuellt den RAM, das System swappt, die Platte laeuft
voll, dann stirbt der Prozess (oder das System — genau das hatte der Nutzer in einer frueheren
Sitzung schon einmal). Ob ein Lauf durchkommt, ist damit Zufall der uebrigen Systemlast, nicht
eine Frage von Vordergrund oder Hintergrund.

**Drei Ursachen, alle behoben:**

1. **`render_proxy` gab in 4K aus**, obwohl Name und Doku "1080p-Proxy-Render" sagen —
   `resolution` wurde nie an `build_filtergraph` uebergeben, also galt `timeline.resolution`
   (3840x2160). Jeder Frame ist damit in JEDER Stufe viermal so gross: Decode,
   Ken-Burns-Oversampling, Blur-Fill, die Kette aus 169 verschachtelten `xfade`, Encoder. Bei
   170 Segmenten und 213 gleichzeitig offenen Inputs ist das der dominante Posten. Der Preview
   war deshalb auch ~2,5 GB gross und entsprechend langsam.
   Damit ein kleinerer Render richtig aussieht, skaliert `build_filtergraph` jetzt mit: die
   Overlay-PNGs (die entstehen formatfuellend in Timeline-Auflaesung) und die Pixelwerte in
   `anim` (`slide_from_px`/`slide_from_py`/`drift_px`/`drift_py`) sowie den Karten-Rand. Ohne das
   liegt ein 4K-Titel in Originalgroesse auf einem 1080p-Bild und schiebt viermal zu weit.
   `_preview_resolution` deckelt auf 1080p Hoehe, skaliert nie hoch, haelt gerade Kantenlaengen.
   `render_final` bleibt unangetastet 4K.
2. **`_kenburns_expr` skalierte pauschal auf die doppelte Zielgroesse** — bei 4K also 7680x4320,
   ~100 MB je Frame, fuer 62 Foto-Clips. `zoompan` schneidet `iw/zoom` heraus, ein Oversampling
   um `max_zoom` (+15% Reserve) genuegt also exakt; mehr bringt keine Schaerfe. Bei Zoom 1.13
   sind das 1.30x statt 2x.
3. **Preview-Encoder** laeuft jetzt auf `preset=veryfast`/`crf=26` statt Default `medium`.

**Zwei Folgefunde beim Nachmessen:**

- `_kenburns_expr` klemmte `z_to` auf `z_from + 0.001` hoch. **Jeder Zoom-heraus war damit ein
  Standbild** — zwei der sechs neuen Ken-Burns-Varianten aus Runde 3 haetten stillschweigend
  nicht funktioniert. Beide Richtungen sind jetzt erlaubt.
- Die Rundung der Ken-Burns-Zwischengroesse auf gerade Kantenlaengen verschiebt das
  Seitenverhaeltnis minimal; `zoompan` gibt das als SAR weiter (304:303) und `concat` bricht mit
  "parameters do not match" ab. Deshalb `setsar=1` hinter `zoompan`.

**Und ein Fehler im eigenen Rezept:** `rebuild-recipe.py` rechnete die Titel-Drift als `* 7` auf
den vorhandenen Wert. Das Skript liest aber die bestehende `timeline.json` — es multiplizierte
also bei jedem Lauf erneut. Nach acht Laeufen stand `drift_px` bei 8 * 7^8 = 46.118.408 px; im
Kontaktbogen war "Norwegen" nur von 13,0 bis 14,5s zu sehen und schoss dann aus dem Bild, statt
ueber die vollen 11s zu stehen. Amplitude jetzt absolut in `TITLE_DRIFT_PX`.
**Regel fuer das Rezept: alles, was es aus der alten Datei uebernimmt, muss idempotent sein oder
absolut gesetzt werden.** Betrifft ausser der Drift auch die `src_in`-Uebernahme (die ist
idempotent, weil sie nur liest und unveraendert zurueckschreibt).

**Wichtige Einschraenkung zu diesem Abschnitt (nachtraeglich, gleiche Sitzung):** Die oben
beschriebene Diagnose "Render haengt" stuetzte sich auf eine stehende Ausgabedatei (2.097.200
Bytes, `mtime` zehn Minuten eingefroren) bei gleichzeitig 441% CPU. **Dieses Kriterium ist
falsch.** Ein anschliessender 30-Clip-Testlauf, der sauber durchlief, zeigte genau dasselbe
Verhalten und schrieb seine 13,5 MB praktisch komplett erst beim Schliessen der Datei — der
mp4-Muxer puffert in grossen Bloecken und setzt den `moov`-Atom am Ende.

Folge: die drei abgebrochenen Renders waren mit hoher Wahrscheinlichkeit **gesund** und wurden
unnoetig gekillt (43 Minuten CPU-Zeit bei 441% entsprechen ~10 Minuten Laufzeit, bei 0,80x
Echtzeit also etwa der Haelfte des Films). Der Speicherdruck war real und messbar, aber ob er
je zum Abbruch gefuehrt haette, ist offen.

Der `-t`-Fix an den Foto-Inputs ist **sachlich richtig** (ein unbegrenzter `-loop 1`-Input ist
ein Fehler, der Overlay-Zweig macht es seit immer anders), aber es wurde **nie A/B gemessen**,
ob er den Durchsatz veraendert. Die Behauptung "das war die Ursache" im zugehoerigen Commit ist
nicht belegt. Wer das klaeren will: denselben 30-Clip-Chunk einmal mit und einmal ohne `-t`
rendern und die Laufzeit vergleichen.

**Arbeitsweise, die sich bewaehrt hat:** Overlay- und Fit-Aenderungen an einer synthetischen
Mini-Timeline (2-5 Clips) durch `build_filtergraph` + `_run_ffmpeg` pruefen und die Frames mit
`cv2` als Kontaktbogen ansehen — nie am Vollrender. So wurden der Titel-Drift-Fehler, die
1080p-Overlay-Skalierung und das Blur-Fill jeweils in unter einer Minute verifiziert.

### `vlog-edit` Runde-3-Preview erfolgreich gerendert und geprueft (2026-08-09, 02:17)

**Datei:** `exports/vlog-edit/preview/vlog-edit_preview.mp4` — 582,8 MB, **1920x1080**,
1085,366s (18:05), 30 fps, 4,5 Mbit/s. Laufzeit 25 Minuten (0,72x Echtzeit).
Das ist der erste Preview, der die Runde-3-Aenderungen tatsaechlich enthaelt.

**Achtung, geaendert gegenueber allen frueheren Previews:** die Datei ist jetzt **1080p**, nicht
4K (siehe `_preview_resolution`). Deshalb auch 583 MB statt 2,5 GB.

**Geprueft (nicht behauptet):**

| Punkt | Ergebnis |
|---|---|
| Bewegung ueber den ganzen Film | 12 Stichproben, alle bewegt; Schwarz nur bei 5s (Cold-Open) und 1084s (Ausblende) |
| Titelsequenz 12-24s | Einlauf, Halten mit langsamer Drift in EINE Richtung, Ausblenden bei 22,8s — vollstaendig |
| Bauchbinden | alle 17 vorhanden, Text/Tag/Etappe/km korrekt, unten links |
| Trollstigen-Hoehepunkt 14:17,7 | Wolkenfenster-Blick ins Tal, 14s Standzeit, laeuft durch |
| Moewen-Verfolgung 17:15,6-17:24,2 | Moewe ueber dem glitzernden Wasser, Drohne folgt |
| Naher Vorbeiflug 17:23,8-17:27,4 | Moewe kreuzt diagonal, am groessten bei 17:26,9-17:27,3, harter Schnitt danach |
| Ducking (2 Stellen) | Musik faehrt weich von ~-17 dB auf ~-23 dB und zurueck, keine Sprungstelle |
| Ken-Burns-Varianz | 8 verschiedene Parametersaetze (vorher 1), haeufigste nur 13x von 62 |
| Blur-Fill | 29 Clips, in den Bauchbinden-Stichproben sichtbar korrekt (kein Balken, nichts angeschnitten) |

**Neue QC-Regel greift:** `qc.validate(..., asset_durations=...)` ist in beiden CLI-Aufrufstellen
verdrahtet. Waere sie vorher da gewesen, haette sie den 26,7s-Fehlrender sofort verhindert.

**Offen fuer die naechste Runde (Nutzer-Sichtung):**
- Ob der O-Ton an den zwei Ducking-Stellen jetzt laut genug ist (gemessen liegt er drin, die
  Beurteilung "laut/klar genug" kann nur der Nutzer treffen).
- Ob die Blur-Raender bei 29 Clips im Fluss stoeren oder ob einzelne davon lieber raus sollen.
- Der `/ff-build`-Hinweis beim Render ("Beat-Sheet kennt das neue Material nicht") steht noch:
  `beatsheet.md` ist der Stand vor Runde 3. Bewusst so gelassen — die Schnittfassung steht in
  `rebuild-recipe.py`, das Beat-Sheet waere nur Doku. Bei Gelegenheit nachziehen.

### Runde 4 — Nutzer-Feedback zum 1080p-Preview (2026-08-09)

**Export `vlog-data` heisst jetzt `vlog-edit`** (Nutzerwunsch, parallel zu `drone-edit`).
Verzeichnis, Rezepte, `.state.json` und die Referenzen in diesen Dokumenten wurden mitgezogen;
der Preview aus Runde 3 liegt als `preview/vlog-edit_preview.mp4`. Im Bild bleibt "Roadtrip
Edition" unveraendert.

Sieben Punkte, alle umgesetzt, Laufzeit jetzt **18:00,35** (vorher 18:05,37):

| Punkt | Befund | Loesung |
|---|---|---|
| Titel "tickert" 18-23s | `overlay` positioniert **ganzzahlig**; 56px Drift ueber 9,7s = 5,8 px/s = ein Sprung alle 5 Frames | neues `anim.drift_dur_s`: dieselbe Strecke in 1,5s (37 px/s, >1 px je Frame), danach steht der Titel |
| Bauchbinde 15:57 | "Uvdal · Angeln, **Bogen** & Kanu" | "… Bogenschießen & Kanu" |
| Bauchbinde 4:51 | "Ruhetag vor dem Roadtrip" | "Lazy Day vor dem Roadtrip" |
| Bild 4:11 | Familie am gedeckten Tisch | ersetzt durch `20260720-phone-9f4dbe` (17:27, Vater am Kugelgrill) |
| Blaue Boxen zu leer | eine feste Boxbreite fuer alle | Breite **pro Bauchbinde** an der gemessenen Textbreite; drei Zeilen statt zwei |
| Tag 13 → Tag 15 | kein Rechenfehler | 31.07. (Tag 14) und 02.08. (Tag 16) haben Material im Index, kamen aber nicht in den Schnitt. Nutzer: so gewollt. Das Datum steht jetzt in Zeile 1, damit der Sprung erklaerbar ist |
| Ton endet zu frueh, ~5s zu lang | **echter Fehler**, siehe unten | Musikeinsatz nachgerechnet, Meeres-O-Ton am Schluss, 5s gekuerzt |

**Der Tonfehler am Filmende — gemessen, nicht vermutet.** `Aguila de Oro` ist **374,70s** lang,
die Timeline verlangte ab `src_in` 0,743s aber **385,35s**. Die Musik endete also bei 1073,96s,
der Film lief bis 1085,35s: **11,4 Sekunden Stille**, ohne Fehlermeldung, ohne dass die
geplante 10s-Ausblendung je stattfand. Genau derselbe Fehlermodus wie beim zu langen `src_out`
(Runde 3), nur auf der Tonspur.

- `rebuild-recipe.py` misst die Datei jetzt (`probe.probe_duration`, neu — `probe_video` wirft
  bei reinen Audiodateien) und richtet den **Einsatz** danach aus, statt die Dauer aus der
  Timelinelaenge zu rechnen: `music-03` startet 705,65s statt 700s und endet exakt bei 1080,35s.
  Der Vorgaengertitel wird passend verlaengert (Deckung geprueft: 445,27s Quelle reichen).
- Neue QC-Regel `_check_music_coverage` (+ `music_durations` in `qc.validate`, in beiden
  CLI-Aufrufstellen verdrahtet): meldet sowohl "Track kuerzer als verlangt" als auch "Musik
  endet mehr als 1s vor dem Film". Waere sie vorher da gewesen, haette der Nutzer den Fehler
  nicht selbst hoeren muessen.
- Der Song klingt zusaetzlich **von sich aus** aus (gemessen: ab 1065s faellt er von -17 auf
  -37 dBFS). Deshalb traegt am Schluss neu der O-Ton `atmo-meer-schluss` (Blick von Bord aufs
  offene Meer, `20260804-camera-59ef0c`), 13,8s bis ins Schlussschwarz. Der ist mit -34 dBFS RMS
  sehr leise aufgenommen und braucht **+6 dB** — die Anhebung ist am gerenderten Ausschnitt
  gegengemessen (Spitzenpegel im Schlussfenster -4,2 dBFS, Summe ~-28 statt -40 dBFS RMS) und
  traegt dafuer `gain_verified: true` in der Timeline. `qc._check_audio_clipping_risk` kennt
  diese Ausnahme jetzt, gleiche Bauart wie `intentional_repeat` bei den Videoclips.
- Die 5 Sekunden kommen aus dem Schluss: 04.08. von 8,4s auf 6,9s je Clip (alle drei Bilder
  bleiben drin) und das Schlussschwarz von 3,0s auf 2,5s.

**Bauchbinden neu, drei Zeilen** (Aufbau vom Nutzer vorgegeben):
`Tag 13 - 30.07.2026` / `Uvdal · Angeln, Bogenschießen & Kanu` bzw. `Fahrt von X nach Y ueber Z`
/ `Tagesstrecke: 266 km  |  Gesamtstrecke: 2.205 km`. Die Panelbreite entsteht in **zwei
Durchgaengen**: erst rendert `stage-caption-recipe.py` die Binde mit unsichtbarem Panel und
misst die Textbreite an der Alpha-Maske, dann mit Panel in genau dieser Breite (900-1374px statt
einheitlich 1560px). Panel und Text stecken damit in EINEM PNG, `timeline.json` hat ein Overlay
je Kapitel statt zwei. Gesamtstrecke ist die Summe aus `stages.csv` bis einschliesslich des
Tages, Faehrstrecken inklusive (3.829 km am Reiseende).

**Gegengeprueft am Bild, nicht behauptet** — drei 1080p-Mini-Render aus der echten Timeline
(Ausschnitt auf t=0 geschoben, `build_filtergraph` + `_run_ffmpeg`, Kontaktbogen mit `cv2`):
Titel laeuft ein, rollt bis 15,8s aus und steht danach pixelgleich (16/18/20/22s identisch);
Bauchbinde dreizeilig, Text vollstaendig im Panel; Grillbild getauscht; Schlussblock mit
Pegelmessung je 2s-Fenster.

**Nebenbefund:** `templates/svg/infocard.svg` (seit `a87299a` im Repo) verlangt `info_main` und
`info_sub`. Beide fehlten im Token-Satz der Template-Tests, seitdem waren **6 Tests rot** —
unbemerkt, weil in Runde 3 nur gezielt einzelne Testdateien liefen. Ergaenzt; 601 Tests gruen.

### Der 4K-Final-Render von `vlog-edit` scheitert am Ein-Pass-Graphen (2026-08-09) — Messwerte

Freigabe erteilt (`APPROVED`), `frameforge render norwegen-2026 vlog-edit --crf 18` gestartet,
nach 42 Sekunden abgebrochen — **nicht** vom Watchdog, sondern von Hand, weil die Lage eindeutig
war:

| Zeitpunkt | frei auf / | Swap benutzt | ffmpeg |
|---|---|---|---|
| Start | 17,1 GB | 0,18 GB | — |
| +33 s | 7,5 GB | — | RSS 1,8 GB, 38 % CPU, Ausgabedatei 0 Bytes |
| +42 s | 6,2 GB | **12,1 GB** | RSS 1,4 GB, **3,1 % CPU** (Thrashing) |
| nach `kill` | 13 GB | 4,2 GB | — |

**Die Ursache ist die Zahl der gleichzeitig offenen Inputs, nicht die Dateigroesse.** Gegenprobe
mit einem echten 4K-Chunk aus den Originalen (Filmzeit 600-700 s, Video + Overlays, ohne Ton):

| | Inputs | RSS | Ergebnis |
|---|---|---|---|
| Chunk 103,6 s | 19 | **5,9 GB** | laeuft in ~4 min sauber durch, 840 MB, Swap waechst nicht |
| ganzer Film | 213 | hochgerechnet ~50 GB | unmoeglich bei 17,2 GB RAM |

Ein Rechnerneustart aendert daran nichts — 213 offene 4K-Decoder plus die Kette aus 169
verschachtelten `xfade` passen nicht in 17 GB, egal was sonst laeuft.

**Nebenbefund zur Dateigroesse (die Sorge war unbegruendet):** 840 MB / 103,6 s = 8,1 MB/s,
hochgerechnet **~8,8 GB fuer 18:00** bei CRF 18. Der `drone-edit`-Final liegt bei 5,7 GB fuer
8 Minuten (11,9 MB/s), also dieselbe Groessenordnung. 18 GB frei reichen dafuer.

**Der Weg, der daraus folgt — Chunk-Render (umgesetzt 2026-08-09, siehe Abschnitt darunter):**

1. Film in ~10 Stuecke à ~110 s zerlegen, jedes einzeln in 4K aus den Originalen rendern
   (je ~19-25 Inputs, ~6 GB RSS), Video **ohne Ton**.
2. Schnittpunkte **in der Mitte eines Clips** waehlen, nie an einem Uebergang und nie waehrend
   eines Overlays — sonst geht die Blende verloren bzw. die Overlay-Animation startet neu.
3. Chunks per `concat`-Demuxer **ohne Neukodierung** zusammenfuegen.
4. Ton **in einem eigenen, einzigen Durchgang** rendern (nur 6 Inputs: 3 Musiktitel + 3
   O-Ton-Assets, kostet praktisch nichts) und ans fertige Video muxen. Grund: `loudnorm` wuerde
   je Chunk unterschiedlich normalisieren, das gaebe an jeder Nahtstelle einen hoerbaren
   Pegelsprung. Nebeneffekt: die Chunk-Grenzen muessen auf der Tonspur gar nicht mehr passen.
5. Sinnvoller Ort dafuer ist `frameforge.render` (`render_final(..., chunk_s=...)` +
   CLI-Option), damit der Weg reproduzierbar bleibt und nicht als Einzelskript neben der
   Pipeline liegt.

**Stand:** `vlog-edit` ist `APPROVED`, `timeline.json` ist final (18:00,35), QC sauber,
601 Tests gruen, alles committet. Offen ist ausschliesslich der Chunk-Render.
`exports/vlog-edit/final/` ist leer (die 48-Byte-Ruine des Fehlversuchs wurde entfernt).

**Ausserdem in dieser Runde korrigiert:** `brief.yaml` `target_duration_s` von 1085 auf 1080 —
die QC-Regel "Ziellaenge" hatte den Render sonst zu Recht blockiert, weil die 5 Sekunden
Kuerzung im Brief nicht nachgezogen waren.

### Chunk-Render in `frameforge.render` (2026-08-09)

`render_final(..., chunk_s=...)` bzw. `frameforge render <projekt> <export> --chunk-s 110`.
Ohne `--chunk-s` bleibt alles exakt wie bisher (Ein-Pass-Graph), der neue Weg ist ein Opt-in.

Ablauf, genau nach dem Plan im Abschnitt darueber:

1. `chunk_boundaries(timeline, chunk_s)` sucht die Schnittzeitpunkte. Zulaessig ist nur die
   **Mitte eines Video-Clips** — `cut_windows()` baut die erlaubten Fenster und zieht ab:
   Clipraender (`CHUNK_EDGE_MARGIN_S`, 1 s), Uebergaenge des Clips **und** der Nachbarn
   (`xfade`/Schwarzblende inkl. `hold`), Clips mit Effekten (Ken-Burns wuerde in beiden
   Haelften neu anfangen) sowie jedes Overlay- und Karten-Fenster (Animation startet sonst
   neu). Die Zielmarken liegen gleichmaessig, jede wandert auf den naechstgelegenen erlaubten
   Punkt; findet sich fuer eine keiner, waechst der Chunk (korrekt, nur speicherhungriger).
2. `slice_timeline(timeline, start, end)` schneidet das Stueck als eigenstaendige Timeline auf
   `tl_in = 0`: Randclips werden ueber `src_in`/`src_out` getrimmt (mit `speed` gerechnet) und
   verlieren ihr `transition_in`/`transition_out` — ein angeschnittener Clip darf weder ein-
   noch ausblenden, die Blende gehoert dem Nachbarchunk. Overlays/Karten muessen ganz im
   Fenster liegen, sonst `RenderError` (Doppelsicherung zu Schritt 1). Ton bleibt weg.
3. Jeder Chunk laeuft durch dasselbe `build_filtergraph` + `_run_ffmpeg` wie sonst, mit
   denselben Encoder-Settings — Voraussetzung dafuer, dass Schritt 4 kopieren kann.
4. `concat`-Demuxer, `-c copy`, keine Neukodierung. Die Chunk-Dateien werden **sofort danach**
   geloescht: sonst liegen Chunks + zusammengesetztes Video + Endfassung gleichzeitig auf der
   Platte, beim Vlog dreimal ~9 GB — mehr als frei ist (23 GB).
5. Ton in einem einzigen Durchgang: `build_audio_filtergraph()` (aus `build_filtergraph`
   herausgeloest, gemeinsamer `_build_audio_chain`) baut die Tonspur ohne jeden Video-Input,
   `loudnorm` rechnet damit einmal ueber den ganzen Film. `_mux` legt sie per `-c copy` auf das
   Video — **ohne `-shortest`**, sonst kappt ein Ton, der vor dem Schlussbild endet, das Bild
   (im Test nachgestellt: 4 s Ton unter 8 s Film).

Zwischendateien liegen in `final/.<name>_v<N>_chunks/` und werden nach Erfolg geloescht —
bleibt das Verzeichnis liegen, ist der Lauf gescheitert. `--chunk-s` meldet je Schritt eine
Zeile (Chunknummer, Zeitfenster, Zahl der Inputs).

14 neue Tests in `tests/test_render.py`, darunter zwei echte Chunk-Renders (mit und ohne Ton)
gegen die Fixtures; 615 Tests gruen.

### Der 4K-Final von `vlog-edit` steht (2026-08-09) — und was der Weg dahin gelehrt hat

`exports/vlog-edit/final/vlog-edit_v1.mp4`, **6,78 GiB**, 3840x2160, 30 fps, **18:00,4**
(Soll 18:00,35), h264 + AAC-Stereo ueber die volle Laenge. Phase `RENDERED`, Report daneben.

**Gegengeprueft, nicht behauptet:** an jeder der 9 Chunk-Nahtstellen je ein Frame 0,15 s davor
und danach aus der fertigen Datei gezogen (`cv2`): keine schwarzen oder fehlenden Frames, die
Helligkeit laeuft stetig durch (z.B. 135,3 -> 133,7 bei 102,6 s), die Pixeldifferenzen
entsprechen der Bewegung im Bild. Der Ton kommt aus **einem** Durchgang, an den Grenzen kann
es deshalb per Konstruktion keinen `loudnorm`-Sprung geben.

Drei Dinge, die beim naechsten langen Render Zeit sparen:

1. **Lange Laeufe muessen fortsetzbar sein.** Der erste Lauf wurde nach 50 Minuten und
   6 Chunks vom Harness abgeraeumt — ohne Wiederaufnahme waeren ~40 Minuten Rechenzeit
   verloren gewesen. Jetzt liegen die Chunks in `final/.<export>_chunks/` (bewusst **ohne**
   Versionsnummer im Namen, sonst findet der zweite Lauf sie nicht), `params.json` bindet sie
   an Schnittpunkte/CRF/Preset/Aufloesung/LUT/Grade, und eine Laengenpruefung je Chunk sortiert
   halbe Dateien aus. Der abgebrochene chunk_005 wurde genau so erkannt und neu gerendert.
2. **Hintergrundlaeufe abkoppeln.** `nohup … & disown` statt eines vom Harness verwalteten
   Hintergrund-Tasks; der Fortschritt wird per `Monitor` aus der Logdatei gelesen. Der erste
   Lauf starb genau daran. (`setsid` gibt es auf macOS nicht.)
3. **`python -m frameforge` funktionierte nie.** Die Form steht an ~10 Stellen in CLAUDE.md
   und im Plan, es fehlte aber `frameforge/__main__.py` — nur das Konsolenskript
   (`.venv/bin/frameforge`) und `python -m frameforge.cli` liefen. Nachgereicht und mit einem
   Subprozess-Test abgesichert, damit es nicht wieder still kaputtgeht.

Plattenplatz bleibt die zweite Ressource neben RAM: Chunks + zusammengesetztes Video +
Endfassung sind drei Kopien. Deshalb loescht der Lauf die Chunks direkt nach dem `concat`.
Vor einem 4K-Lauf `df -h /` pruefen — beim Vlog waren ~7 GB in Bewegung.

---

## Reise-Website `web/` (2026-08-10)

Zusatzbereich neben der Pipeline: pro Reiseprojekt eine kleine, passwortgeschuetzte Website
mit den fertigen Filmen. Pilot: `web/sites/norwegen-2026/` fuer https://norwegen.skubus.de.

| Schritt | Status |
|---|---|
| Struktur `web/` + Design-Prompt | ✅ `856d481` |
| Designsystem-Export (5 Seiten, Tokens, Komponenten) | ✅ `f13d623`, `8a26491` |
| `public/` mit echten Bildern aus dem Material | ✅ `16e5072`, `96b71bd` |
| Umbau nach Nutzer-Feedback (Plan `docs/plans/0002-website-feedback.md`) | ✅ |
| Zweisprachig DE/EN (`public/` + `public/en/`, Umschalter in der Kopfzeile) | ✅ |
| Schriften (Schibsted Grotesk, Source Serif 4) | ⬜ Netzzugriff gesperrt, Nutzer laedt sie |
| Videos auf den Server | ⬜ Nutzer, 4 Dateien / ~14 GB |
| Traefik Basic Auth | ⬜ Nutzer, Infrastruktur-Ebene |

### Aenderungen an der Pipeline, die dafuer noetig waren

1. **`faststart`** (`40990a1`): Die Finals hatten das moov-Atom am Dateiende — ein Browser
   haette die komplette Datei laden muessen, bevor er das erste Bild zeigt. Jetzt bei
   Ein-Pass-Render, Chunk-Concat und Mux gesetzt.
2. **Aufloesung im Dateinamen** (`40990a1`): `vlog-edit_4k.mp4` / `vlog-edit_1080p.mp4` statt
   `_v1`/`_v2`. Von einem Export existieren mehrere Fassungen nebeneinander; eine blosse
   Versionsnummer sagt nicht, welche man vor sich hat. `_next_version_path` ist entfallen,
   `resolution_label` ist neu. Eine Nummer kommt nur bei erneutem Render derselben Fassung
   dazu, die vorhandene Datei bleibt unangetastet.
3. **Gate: Zweitfassung ohne neues Preview** (`c83c675`): `gate_render_final` laesst Phase
   RENDERED zu, wenn der Timeline-Fingerprint dem beim Approve gespeicherten entspricht — ein
   zweites Deliverable derselben Freigabe, kein zweiter Schnitt. Geaenderte Timeline blockiert
   weiterhin. `.claude/hooks/gate.py` gibt den Fingerprint mit.

### Runde 2: Umbau nach dem ersten Deployment (2026-08-10)

Vollstaendige Liste in `docs/plans/0002-website-feedback.md`. Die Punkte, die ueber Text
hinausgehen:

1. **Standbilder sind jetzt reproduzierbar** (`deploy/grab-stills.py`): Teaser, Seitenkoepfe,
   Video-Poster und die Routenkarte entstehen aus Asset-IDs bzw. den fertigen Filmen. FFmpeg
   laeuft dabei ueber `frameforge.render._run_ffmpeg_cmd`, nicht nackt. Die Poster sind die
   echten Titelbilder der Filme (Vlog Sekunde 19, Drone Sekunde 13; Quelle fuer die Zeitpunkte:
   `timeline.json`, Overlay `ov-title-*`).
2. **Hero-Rotator**: Das Kreuzfahrtschiff ist raus, fuenf Szenen statt sechs. Der beim Laden
   sichtbare „Doppel-Zoom" kam daher, dass Szene 1 eingezoomt startete, waehrend dasselbe Bild
   ungezoomt als `background-image` darunter lag. Szenen starten jetzt auf `scale(1)`.
3. **Flagge in der Kopfzeile** war ein waagerechter Streifenverlauf und damit keine
   Norwegen-Flagge. Ersetzt durch dasselbe SVG wie im Favicon (`.flagmark--flag`).
4. **Gemessene Zahlen statt Schaetzungen**: 30 fps (nicht 60 — die Timeline steht auf 30),
   1,8 / 7,3 / 1,5 / 5,8 GB, 13 / 54 / 21 / 82 Mbit/s. Quelle `frameforge.probe.probe_video`.
5. **Rundkurs 1.332 km / 22 h 40 min** — der Nutzer hat `index/final-route.png` gegen den
   richtigen Screenshot getauscht (Rueckweg identisch ueber Heddal statt Schleife ueber
   Kongsberg). Alle Stellen nachgezogen, auch `content/facts.md` und `deploy/README.md`.
6. **Geviertstriche komplett raus.** Ausdruecklicher Wunsch: liest sich wie maschinell erzeugt.

### Runde 3: Zweisprachig DE/EN (2026-08-10)

Deutsch in der Wurzel, Englisch unter `public/en/` mit denselben Dateinamen. Kein JavaScript,
kein Build — zwei vollstaendige Seitensaetze, gemeinsame CSS/Schriften/Bilder. Der Umschalter
(`.lang-switch`, Kopfzeile rechts) bildet den Gegenpart mechanisch aus dem Pfad.

Voraussetzung dafuer war, **alle Pfade absolut ab Docroot** zu machen (`/assets/…`,
`/film-vlog.html`) — relative Pfade zeigen unter `en/` ins Leere. `hreflang`-Verweise stehen
paarweise im `<head>`.

Der Umschalter zeigt **Miniflaggen statt Kuerzel** (Deutschland, Vereinigtes Koenigreich), als
Inline-SVG in `background-image` — keine zusaetzlichen Requests. Die inaktive Flagge ist
entsaettigt und abgedunkelt, die aktive traegt einen Akzentring. Beide Flaggen behalten ihr
eigenes Seitenverhaeltnis (5:3 bzw. 2:1); auf eine gemeinsame Box gestreckt saehen sie falsch
aus. Der Sprachname steht als `aria-label` am Bild, damit Screenreader nicht nur "Link" hoeren.

Zwei bewusste Entscheidungen:

- Das englische Impressum ist eine Lesehilfe und sagt das auch: verbindlich bleibt die
  deutsche Fassung, auf die es verlinkt.
- Der Kartenscreenshot bleibt in beiden Faellen derselbe und damit deutsch beschriftet
  („Norwegen"). Ein zweiter Screenshot waere die einzige Alternative.

`deploy-norway-site.sh` musste nicht angefasst werden: `rsync` von `public/` nimmt `en/` mit.

### Stolperstellen

- **`_generated/` unter `media_root` war verschwunden.** Der 1080p-Lauf des Vlogs brach sofort
  ab (`generated-cold-open-black` nicht gefunden). Beide Dateien lagen noch im Proxy-Cache und
  wurden von dort zurueckgeholt. Wer `media_root` aufraeumt, trifft auch generierte Assets —
  sie stehen in `assets.json` wie jedes andere Material.
- **Netzzugriff ist aus der Arbeitsumgebung gesperrt.** Schriften und andere externe Dateien
  muss der Nutzer selbst beschaffen. (Stand 2026-08-10: `curl` nach aussen geht wieder, die
  Live-Seite laesst sich also direkt pruefen.)
- **Cloudflare cacht die Assets vier Stunden, die HTML nicht.** Nach dem Deploy der
  Flaggen-Aenderung war der Sprachumschalter leer: HTML aktuell (`cf-cache-status: DYNAMIC`),
  `components.css` aber vom Vortag (`HIT`, `age: 6631`, `max-age=14400`) und damit ohne die
  Flaggen-Regeln. Der Upload war vollstaendig — nachweisbar, indem man dieselbe Datei mit
  einem beliebigen Query-String holt (`?bust=…` → `MISS`, 22341 statt 16959 Bytes).
  Seitdem haengt `deploy/cache-bust.py` an jeden Asset-Verweis einen Inhalts-Hash, und
  `deploy-norway-site.sh` laedt das Ergebnis statt `public/` direkt hoch.
- **`url()` in einer Custom Property** wird relativ zu dem Stylesheet aufgeloest, in dem die
  *Verwendung* steht, nicht die Deklaration. `--header-image: url('assets/img/...')` im
  `<style>`-Block der Seite, benutzt in `components.css`, ergab
  `/assets/css/assets/img/...` → 404. Deshalb dort absolute Pfade ab Docroot.
- **Bitraten der 1080p-Fassungen** liegen bei CRF 20 hoeher als erwartet: vlog 1,7 GB
  (~12,6 Mbit/s), drone 1,4 GB (~20 Mbit/s). Bewusst so belassen — geschaut wird am grossen
  Bildschirm, nicht unterwegs.

## Farbraum-Fehler im `vlog-edit` (2026-08-10) — **behoben**

Nutzer-Report: im hochgeladenen `vlog-edit` sind bei 2:46 die Gesichter der drei Personen auf
dem Schiffsdeck „einfach nur rot", bei 1:43 springt die Farbigkeit hart um, Fotos wirken
uebersaettigt. **Lokal in QuickTime/macOS-Vorschau war nichts davon zu sehen** — der Fehler
zeigte sich nur im Chromium-basierten Browser. Genau diese Diskrepanz war der entscheidende
Hinweis: es lag nicht am Bildinhalt, sondern an den Farb-Metadaten der Datei.

### Befund

```
drone-edit_1080p/4k.mp4 : yuv420p  range=tv  bt709/bt709/bt709   <- korrekt
vlog-edit_1080p/4k.mp4  : yuvj420p range=pc  bt470bg, kein trc   <- falsch
```

Ursache: `_run_ffmpeg` setzte nur `-pix_fmt yuv420p` und **keine** Farbtags, und der
Filtergraph normalisierte die Quellen nicht. Der `vlog-edit` zieht 61 HEIC-Foto-Proxies als
MJPEG-Inputs (`yuvj420p`, Full-Range, `bt470bg`); deren Metadaten haben sich durch die
ffmpeg-Aushandlung auf den gesamten Film durchgesetzt. `-pix_fmt yuv420p` greift dagegen
nicht, weil ffmpeg `yuv420p` und `yuvj420p` als kompatibel behandelt. Der `drone-edit` hat
keine Fotos und ausschliesslich BT.709-Quellen — deshalb war er unauffaellig und musste **nicht**
neu gerendert werden.

Player, die die Tags befolgen (Chromium), dekodieren dann mit BT.601-Matrix im
Full-Range-Modus → kraeftiger Rot-/Saettigungs-Shift, am staerksten auf Hauttoenen. Player, die
sie ignorieren (QuickTime), zeigen dieselbe Datei unauffaellig.

Farbraeume im `vlog-edit`: 41 Clips iPhone-HLG (`bt2020nc`/`arib-std-b67`, 10 bit), 65 Clips
Drohne (`bt709`), 61 HEIC-Fotos (Display P3). Drei Raeume, bis dahin null Konvertierung.

### Fix

- **Neu: `frameforge/color.py`.** `normalize_chain(path)` bringt jedes Segment an der Quelle
  nach BT.709/TV — HLG ueber eine erzeugte 3D-LUT, Full-Range-JPEG ueber explizites
  `scale=in_range=full:in_color_matrix=bt470bg:…`, BT.709-Material nur mit `setparams`.
  Danach existiert im Graphen genau ein Farbraum, und Look-Filter arbeiten auf definierten
  Werten.
- **Kein `zscale`** — der Homebrew-ffmpeg dieser Umgebung ist ohne libzimg gebaut, und der
  `colorspace`-Filter kennt `arib-std-b67` nicht (`Unable to parse "itrc" option value`).
  HLG→BT.709 laeuft deshalb ueber eine in Numpy gerechnete `.cube`-LUT im Cache.
- **HLG-Kurve ohne OOTF (Systemgamma 1.0)**, auf Diffusweiss normiert, weiche Schulter ab 70 %.
  Mit BT.2100-γ=1.2 plus Filmkurve landete Diffusweiss bei 0.71 statt 0.94 — die Clips waeren
  deutlich dunkler geworden als im bisherigen Export. Der Nutzer hat am Bild der Videoclips
  nichts auszusetzen; der Fix stellt den Farbraum richtig, er baut den Look nicht um.
- **`_run_ffmpeg` taggt den Output explizit** (`-colorspace/-color_primaries/-color_trc bt709`,
  `-color_range tv`), und der Graph endet auf `format=yuv420p,setparams=…`.
- **`colorbalance=rs/bs` war der falsche Filter.** `rs`/`bs` sind die **Schatten**-Regler fuer
  Rot/Blau, keine Farbtemperatur: der Code hob Rot in den dunklen Partien an und senkte Blau,
  Lichter blieben unberuehrt — deshalb sahen Fotos „qualitativ schlechter" aus. Ersetzt durch
  `colortemperature` (neu: `render.temperature_filter`).
- **Vorzeichenkonvention vereinheitlicht.** `_MOOD_MAP` hatte „negativ = waermer",
  `match_filter` schon „positiv = waermer" — dasselbe Feld mit entgegengesetzter Bedeutung.
  Jetzt ueberall **positiv = waermer**.
- **Kalibrierung `_KELVIN_PER_UNIT = 2000`.** Gemessen entsprechen ~100 K etwa 1.5 Punkten
  R−B. Die Mood-Werte waren fuer den viel schwaecheren Schatten-Regler getunt; mit 4000 K je
  Einheit haette `cool_highlights_warm_lights` ~+7 R−B ergeben, also genau den beanstandeten
  Warmstich. 2000 K → 6380 K ≈ +3.5 R−B.
- **`ingest._write_heif_proxy`: HEIC jetzt farbverwaltet nach sRGB.** Alle iPhone-HEICs tragen
  ein Display-P3-Profil; `convert("RGB")` hat es nur weggeworfen, die Werte blieben P3 und
  wurden downstream als sRGB gelesen. Jetzt `ImageCms.profileToProfile` + eingebettetes
  sRGB-Profil. Die 667 vorhandenen Foto-Proxies wurden geloescht und neu erzeugt.

### Nachweis

- `tests/test_color.py` (10 Tests): Zielformat je Quellklasse, LUT-Einbindung, Full-Range-
  Konvertierung, Monotonie/Neutralitaet der HLG-Kurve, Diffusweiss > 0.9, `.cube`-Format,
  Idempotenz. `tests/test_render.py`: der Warm-Mood-Test prueft jetzt die **Wirkung**
  (Kelvin < 6500) statt eines Filternamens. Gesamt 630 Tests gruen.
- Smoke-Render (HLG-Clip + HEIC-Foto + Drohnen-Clip in einem Graphen) liefert
  `yuv420p / tv / bt709 / bt709 / bt709`.
- Foto `IMG_9374` (Deck-Selfie, 2:46), R−B gegen das Original (+5.0): alter Export **+13.3**,
  neue Pipeline ohne Grade **+8.8**, mit Grade **~+12** bei 4000 K/Einheit → auf 2000 K
  halbiert.

### Offen

`drone-edit` bleibt wie er ist (korrekt getaggt, keine HLG-Quellen). Der `vlog-edit`-4K-Export
traegt dieselben falschen Tags wie die 1080p und muesste bei Bedarf ebenfalls neu gerendert
werden — auf Nutzerwunsch zunaechst nur die 1080p.

### Neu gerendert (2026-08-10, 17:27)

`vlog-edit_1080p.mp4` neu erzeugt (1080,4 s, 1,06 GB — vorher 1,78 GB, der Unterschied kommt
aus dem sauberen Limited-Range-Signal). Farbtags am fertigen File geprueft:

```
pix_fmt=yuv420p  color_range=tv  bt709 / bt709 / bt709
```

Stichproben gegen die Quellen: HLG-Clips sind hoerbar—sichtbar heller als vorher (die
Nicht-Konvertierung hatte sie zu dunkel gehalten), Hauttoene neutral, keine ausgefressenen
Lichter. `vlog-edit_4k.mp4` traegt weiterhin die alten, falschen Tags — auf Nutzerwunsch nur
die 1080p neu gerendert.

### Schwarzbild ab 8:51 im Ein-Pass-Render (2026-08-10) — **behoben durch Chunk-Render**

Der erste Neurender lief ohne Fehlermeldung durch und war formal 1080,4 s lang, ab 530,7 s
(Clip `c076`) aber durchgehend schwarz — die halbe Laufzeit. Aufgefallen ist es dem Nutzer an
der Dateigroesse: 1,06 GB statt 1,78 GB, weil Schwarzbild praktisch nichts kostet. **Mein
Fehler in der Verifikation:** ich hatte nur an den drei vom Nutzer genannten Zeitmarken
stichprobiert, und die liegen alle vor 3:00.

Ursache ist nicht das Material und nicht ein einzelner Clip: der alte 4K-Export ist an
derselben Stelle intakt, und derselbe Ausschnitt (8:31–9:16) isoliert nachgerendert lief
sauber durch. Es ist die Groesse des Graphen — 213 gleichzeitig offene Inputs, dazu jetzt je
HLG-Clip zwei zusaetzliche Stufen (`format=gbrp` + `lut3d`). Genau die Grenze, an der laut
`CHUNK_EDGE_MARGIN_S` schon der 4K-Render gescheitert ist. ffmpeg bricht dabei **nicht** ab,
es schreibt ab dem Punkt schwarze Frames weiter — die Stille ist das eigentlich Gefaehrliche.

Neu gerendert mit `--chunk-s 120`: 9 Chunks mit 22–25 Inputs statt 213.

Verifikation des fertigen Files (jetzt vollstaendig, nicht stichprobenhaft):
- Tags `yuv420p / tv / bt709 / bt709 / bt709`, Dauer 1080,4 s, 32.411 Frames (= 30 fps)
- Abtastung alle 5 s ueber den ganzen Film: schwarz nur bei 0 s/5 s (Cold-Open) und 1080 s
  (Schlussschwarz) — beides gewollt
- alle 8 Chunk-Nahtstellen bildstetig (Mittelwert vorher/nachher innerhalb 3 %)

**Offen:** die Datei ist mit 2,57 GB / 19 Mbit/s deutlich groesser als die alte 1080p
(1,78 GB / 13 Mbit/s). Zwei Gruende: die HLG-Clips tragen nach der Konvertierung mehr
Zeichnung (vorher flau und dunkel = billig zu kodieren), und der Chunk-Render kodiert je
Stueck getrennt. Die Website nennt an zwei Stellen noch „1,8 GB · 13 Mbit/s".

### Zitternde Fotos im 1080p-Export (2026-08-10) — **behoben, Render laeuft**

Nutzer-Report: in der neuen 1080p zittern alle Foto-Clips (Ken Burns), Videoclips nicht.
Gemessen per Phasenkorrelation, auf gleiche Betrachtungsgroesse normiert — Ruck je Frame:
Fotos 0,118/0,176 px (neue 1080p) gegen 0,055/0,049 px (alte 4K), Videoclips 0,019 px.

Ursache: `zoompan` rastet den Ausschnitt auf ganze **Quell**pixel. Das Zwischenbild war nur
`max_zoom * 1.15` gross, ein Quellpixel entsprach damit 0,77 Ausgabepixeln — der Zoom kann
sich nicht feiner bewegen. In 4K faellt derselbe Fehler beim Herunterskalieren auf einen
1080p-Schirm zur Haelfte weg, deshalb war er dort nie auffaellig.

**Kein Folgefehler des Farb-Fixes** — dieser Codepfad war unangetastet. Ein direktes A/B mit
der alten 1080p ist nicht mehr moeglich, sie wurde geloescht.

Fix: die Reserve haengt jetzt an der Zielhoehe. `<= 1200 px` bekommt 3.0 statt 1.15 (~0,29
statt 0,77 Ausgabepixel je Rastschritt), 4K bleibt bei 1.15 — dort waeren es sonst wieder
~600 MB je Frame. Bezahlbar ist das erst, seit der Final-Render in Chunks laeuft
(~24 offene Inputs statt 213).

### Offen: Wiedergabe bricht im Browser bei 2:59 ab

**Nicht die Datei.** Geprueft: `moov` vor `mdat` (faststart), 32.411 Video-Pakete mit streng
monotonem DTS ohne Luecken, Dekodierung bei 2:58-3:18 und 17:30-Ende fehlerfrei, und die
Datei auf dem Server ist mit 2.567.131.664 Bytes byteidentisch zur lokalen — der Upload ist
vollstaendig.

2:59 entspricht Byte 259.033.839, also 10 % der Datei. Zusammen mit dem zweiten Symptom
(Scrubbing wirft auf Sekunde 0 zurueck) deutet das auf **fehlende HTTP-Range-Unterstuetzung**
in der Auslieferung: der Browser kann nicht springen, laedt von vorn, und haelt am Ende
seines Puffers an. `norwegen.skubus.de` liegt hinter Cloudflare + traefik-Basic-Auth, von
aussen nicht pruefbar (401). Test mit Zugangsdaten:

```
curl -sI -u BENUTZER:PASSWORT -r 2000000000-2000065535 \
  https://norwegen.skubus.de/videos/vlog-edit_1080p.mp4 | head -5
```

`206` + `Accept-Ranges: bytes` = Auslieferung in Ordnung, weitersuchen. `200` = Ranges werden
nicht durchgereicht, Ursache sitzt in traefik/Cloudflare.

**Verifikation des Renders mit der neuen Reserve (2026-08-10, 23:28):**

| | vorher (Reserve 1.15) | nachher (Reserve 3.0) |
|---|---|---|
| Foto c002, Ruck je Frame | 0,118 px (max 0,42) | **0,096 px (max 0,17)** |
| Foto c003, Ruck je Frame | 0,176 px (max 0,51) | **0,106 px (max 0,22)** |
| Videoclip c001 (Referenz) | 0,019 px | 0,019 px |

Der Ausreisser je Frame ist damit auf ein Drittel gefallen — das ist der Wert, der als
Zittern sichtbar wird. Die vorhergesagten 0,29 statt 0,77 Ausgabepixel je Rastschritt decken
sich mit dem gemessenen Faktor 2,3.

Weiter geprueft: Tags `yuv420p / tv / bt709 / bt709 / bt709`, 1080,4 s, 32.411 Frames,
Schwarzbild-Abtastung alle 5 s nur bei 0/5 s (Cold-Open) und 1080 s (Schlussschwarz), alle 8
Chunk-Nahtstellen unauffaellig. 2,55 GB bei 18,9 Mbit/s — die Angaben auf der Website
(2,6 GB / 19 Mbit/s) stimmen weiterhin.

---

## Plan 0004 — JGA Brüssel (v2, in Planung)

Plan-Referenz: `docs/plans/0004-jga-brussel-video.md`. Reiner Planungs-/Vorbereitungsstand,
v2 nach Rückfragen überarbeitet (2026-09-07). Wichtigster Befund: `frameforge`-Befehle lassen
sich aus der Geräte-Anbindung heraus **nicht ausführen** (Python-venv + Homebrew-Tools liegen
außerhalb des gemounteten Ordners) — Projekt-Anlage (`frameforge new`) muss der Nutzer selbst
im Mac-Terminal oder einer nativen Claude-Code-Session anstoßen. Reine Dateiarbeit (Doku,
Presets als YAML, Website-HTML/CSS) ist dagegen von hier aus möglich.

Zwei genuine Neuentwicklungen: Prioritätsstufen für Assets (`must`/`nice`/`ok`, jetzt
dateinamen- statt hash-basiert, Paket J2) und ein wiederverwendbarer Comic/Party-FX-Baukasten
inkl. neuer Cast-Intro-Mechanik (Freeze-Frame + Stempel-Text + SFX, Paket J6). Design-System-
Vorschlag (Farben/Fonts/Bild-Prompts) liegt bereits fertig in Plan §4. Subdomain bestätigt:
`micha-jga.skubus.de`.

| # | Arbeitspaket | Phase | Status |
|---|---|---|---|
| J1 | Projekt `michael-jga-2026` anlegen | 1 (Nutzer/native Session) | ✅ fertig (2026-09-07, `frameforge new` gelaufen, Phase INIT) |
| J2 | Prioritätsstufen (`content.priority`, dateinamen-basiert + Bulk-Import) | Dev | ✅ Code steht (`index.py`/`preindex.py`/`cli.py`/`stats.py`, `set-priority`-Befehl, `timeline-builder.md` angepasst) — funktional gegen echte Aufrufe getestet, End-to-End-CLI/echter Fundus noch offen (§18) |
| J3 | Ingest + Index (inkl. iPhone-Zeitzonen-Check) | 2 | ⬜ offen — braucht echtes Material |
| J4 | Designsystem (`tokens.yaml`, Fonts, Bild-Prompts — Vorschlag steht in Plan §4) | 0/2 | 🔄 `tokens.yaml`-Entwurf + Fonts liegen bereit, `frameforge design` erst nach ingest+index möglich |
| J5 | Custom Preset `jga-zweiteiler` (dreiteiliger Arc) | 0 | ✅ fertig, gegen echten Preset-Loader/`_MOOD_MAP` geprüft — dabei einen ungueltigen `color_grade.mood`-Wert gefunden und korrigiert (§18) |
| J6 | Comic/Party-FX-Baukasten + Cast-Intro (neuer Agent, Denkblasen/Sticker/Speedlines/Farb-Pop/Cartoon-Outline) | Dev | ✅ Code steht (3 neue SVG-Templates, 2 neue `render.py`-Effekte, neuer Agent `party-fx.md`) — bewusst OHNE neue `fx`-Spur, siehe Architektur-Korrektur §18; funktional getestet, echtes Rendering noch offen |
| J7 | Brief + Beat-Sheet (Muss-Shot-Liste, drei Akte + Cast-Intro) | 0/2 | 🔄 Entwurf liegt in `projects/michael-jga-2026/brief-notes.md`, echter `beatsheet.md` erst nach Ingest/Index/Export-Anlage möglich |
| J8 | Audio (3 Musik-Tracks + 1-2 SFX, Ducking) | 1/2 | 🔄 Outro-Musik-Prompt liegt in `projects/michael-jga-2026/design/prompts.md`; Vivaldi/Pulp-Fiction-Datei + genauer Songtitel weiterhin bei Christian |
| J9 | Build → Preview → Freigabe → Render | 2 | ⬜ offen — braucht echtes Material |
| J10 | Website `web/sites/michael-jga-2026/` + Deploy + DNS/Basic-Auth | 0/2 | ✅ `public/` gebaut (3 Seiten + Assets, Pfade auf root-relativ normalisiert), `deploy-jga-site.sh` + `deploy/cache-bust.py` stehen — DNS/Traefik-Basic-Auth (Server-seitig) und die inhaltlichen TODOs (Datum, echte Namen/Cast-Fotos, Songtitel, Impressum-Adresse) offen |

**Update v3 (2026-09-07, zweite Runde):** Ziellänge ist ein offener Richtwert (circa
6-7 statt starrer 5,5 Minuten). Cast-Intro sitzt inhaltlich in der Karaoke-Bar „Red",
mitten in Akt 2, nicht am Akt-Übergang. Christian liefert zusätzlich ein Intro- und ein
Outro-Standbild als fertige Design-Assets. Ein Stilreferenz-Bild von Christian liegt unter
`web/sites/michael-jga-2026/design/reference/style-reference-jga-poster.png` und hat den
Designsystem-Vorschlag (Gold als Hauptakzent statt Pink, Indigo-Purpur-Basis, Neon-Doodle-
Sticker-Optik) präzisiert — siehe `docs/plans/0004-jga-brussel-video.md` §4.

**Offen vor Start von J1:** exakter `media_root`-Pfad (Platzhalter reicht für `frameforge
new`), genauer Pulp-Fiction-Songtitel.

**Update v4 (2026-09-07, dritte Runde):** Design-System-Export (aus externem Tool, auf Basis
von `PROMPT-designsystem.md` + Stilreferenz-Bild + Plan §4-Farben) ist da und vollständig
(Tokens/Theme/Base/Components-CSS, echte Bangers-/Poppins-Fontdateien inkl. Lizenzen, 3
HTML-Seiten, JSX-Komponenten core/film/site, 20 Guideline-Seiten). War zunächst versehentlich
in `projects/michael-jga-2026/design/` (Video-Projekt) statt `web/sites/michael-jga-2026/design/`
(Website) gelandet — korrigiert: Website-Dateien liegen jetzt in
`web/sites/michael-jga-2026/design/` (neben der schon vorhandenen `PROMPT-designsystem.md`/
`README.md`/Referenzbild), die Bangers-/Poppins-`.ttf`-Dateien zusätzlich nach
`projects/michael-jga-2026/design/fonts/` kopiert (für `frameforge design`/SVG-Rendering im
Video). `projects/michael-jga-2026/design/` enthält jetzt wieder nur `tokens.yaml` + `fonts/`
(erwartete flache FrameForge-Struktur). Hinweis: die generierten Bilder im Export
(`hero.jpg`, `poster.jpg`, `film-poster.jpg`, `cast-01..10.jpg`) sind laut Export-eigenem
Readme aus dem einen Referenzbild abgeleitete Platzhalter, keine echten Einzelfotos der zehn
Freunde — für die Website erstmal nutzbar, für die tatsächliche Cast-Intro-Sequenz im Video
werden später echte Einzelfotos gebraucht.

**Update v5 (2026-09-07, vierte Runde):** Auf Nutzerwunsch alles umgesetzt, was nicht an
echtem Videomaterial hängt (siehe Plan §18 für Details): Website `public/` fertig gebaut und
deploybar; J2 (Prioritätsstufen) und J6 (Comic/Party-FX inkl. Cast-Intro) als echter
FrameForge-Code geschrieben und funktional gegengetestet (echte Funktionsaufrufe gegen eine
separat installierte reine-Python-Umgebung, nicht nur Syntax-Checks — `frameforge` selbst
bleibt aus dieser Session heraus nicht ausführbar, §0); dabei zwei echte Korrekturen: keine
neue `fx`-Spur nötig (bestehendes Overlay-/Effect-/Audio-Schema reicht), und der
Preset-Entwurf hatte einen ungültigen `color_grade.mood`-Wert, der sonst still wirkungslos
geblieben wäre. Zusätzlich Preset gegen den echten Loader geprüft, ein Beat-Sheet-/
Muss-Shot-Entwurf (`projects/michael-jga-2026/brief-notes.md`) und ein Outro-Musik-Prompt
(`design/prompts.md`) vorbereitet. Bleibt vor J3/J9: Ingest/Index mit echtem Material,
danach ein kurzer Test-Export der neuen Effekte, bevor `party-fx` sie für ganz Akt 2 einsetzt.

**Update v6 (2026-09-08, /ff-wizard-Session mit echtem Material):**
- **J3 erledigt.** `frameforge ingest` (329 Assets, 329 Proxies) und `frameforge index`
  (329/329 indiziert, Phase INDEXED). Indizierung über 6 parallele `media-indexer`-Agenten
  (je ~55 Assets) + 6 Nachzügler seriell.
- **Bugfix beim Parallel-Index:** `index.write_asset`/`save_assets` schrieben `assets.json`
  ohne Lock und nicht atomar → bei 6 gleichzeitigen Agenten reproduzierbar korrupt
  (`Extra data` / abgeschnittenes JSON), einzelne Einträge gingen durch Fremd-Writes
  verloren. Behoben: `flock` um das Read-modify-write + tmp-Datei + `os.replace`
  (Commit zusammen mit J2). Danach alle 329 Einträge sauber, keine verwaisten `.md`.
- **J4 erledigt.** `projects/michael-jga-2026/design/tokens.yaml` 1:1 aus der Web-Mini-Site
  übernommen (Farbrollen aus `theme-jga-2026.css`, Bangers/Poppins, natürliche Palette).
  `frameforge design` gelaufen, Phase DESIGNED. Keine Grafiken angefordert (Text-Overlays
  reichen); Intro-/Outro-Standbild `JGA_INTRO.png`/`JGA_OUTRO.png` liegen in
  `design/assets/img/` (gitignored), Skalierung 1672×941 → Zielauflösung beim Build klären.
- **Fundus-Lage:** gediegener Auftakt stark (Grand Place, Schokolade/Waffel, Pizza,
  Bierverkostung); Partynacht reichlich aber dunkel/neonstichig (meist Rating 2–3, Karaoke
  nur Screen + 1–2 Videos); ruhiger Ausklang dünn (gute Sonnenuntergang-Panoramen fürs
  Outro, kaum ruhige Innen-/Abreise-Shots); ~20 Fotos mit falscher EXIF-Rotation (Rating
  gedämpft, Tag gesetzt). Kein Drohnenmaterial.
- **Offen:** J7 Brief/Beat-Sheet (Export anlegen), J8 Musik-Dateien (3 Tracks liegen in
  `music/`, Analyse läuft im Build), J9 Build→Preview→Render. Nachzügler-Fotos + Christians
  Muss-Foto-Auswahl kommen vor dem Build per `ingest`-Nachlauf + `set-priority`.

**Update v7 (2026-09-09) — J9 Preview lief, Christians Feedback-Runde 2:**
Erstes Preview `exports/JGA/preview/JGA_preview.mp4` (8:53) gebaut, Export-Phase `PREVIEWED`.
Christian hat gesichtet und umfangreiches Voice-Feedback gegeben → keine Freigabe, zurück zu
Bild. Vollständig transkribiert und strukturiert in
**`projects/michael-jga-2026/exports/JGA/editorial-notes-round2.md`** (überschreibt Runde 1
punktuell). Kernpunkte:
- **Musik komplett getauscht:** Vivaldi → **Champions League Theme** (181,5 s), Galvanize →
  **Miserlou** (Dick Dale, 136,1 s → als loop-verlängerte Datei ~196 s), Where Is My Mind
  bleibt unverändert. Neue Filmlänge ~7:08 statt 8:53 → ~1:45 müssen raus (Kürzung über
  `priorities.csv` + Streichliste Runde 2).
- **Ducking überall raus** (Christian explizit). Keine Duck-Clips mehr.
- **Ken Burns pro Clip variieren** (alt: immer gleicher langsamer Zoom-in — Hauptkritik).
- **Hochkantbilder `fit: "blur"`** (Blur-Extend seitlich) statt Überskalieren.
- **Text-Overlays:** nicht mittig, nie über Gesichtern, animierter Auftritt (Buchstaben
  einzeln), muss vor dem Fade weg sein; Schatten, schräg, bold.
- **Speed-Ramps** in Akt-2-Videos (Dynamik + Zeitgewinn).
- Zahlreiche Reihenfolge-/Streich-Entscheidungen, Aftermath komplett neu geordnet, Ende neu.
- **`thought-bubble.svg` / `sticker.svg` / `speedlines.svg`** haben 16 rote Tests in
  `tests/test_design.py` (unfertiges Vorgänger-WIP, kein Fremdcode-Problem: Content-Tokens
  ohne Fixture, FX-Tokens ohne Default im Pre-0003-Pfad). `frameforge/design.py` trägt einen
  uncommitteten Halb-Fix. Diese Templates + `.claude/agents/party-fx.md` sind noch untracked.

### Plan 0004 — JGA Runde 2 (Rework nach Preview-Feedback)

| # | Task | Abnahme | Status | Commit |
|---|------|---------|--------|--------|
| T1 | 3 FX-Templates (`thought-bubble`/`sticker`/`speedlines.svg`) + `design.py` + Test-Fixture reparieren | `pytest tests/test_design.py` grün (99/99), `ruff` sauber; `party-fx.md` + SVGs committed | ✅ fertig | `fb1631d` |
| T2 | `editorial-notes-round2.md` + diese PROGRESS-Sektion + `brief.yaml`-Musik/Target anpassen | Doku committed, `brief.yaml` referenziert neue Tracks | ✅ fertig | `8655cee` |
| T3 | Cast-Intro-SFX: 3 Dateien (`whoosh`/`stamp`/`stamp-micha`) lizenzsicher (Pixabay/Mixkit) nach `music/sfx/` | Dateien da, 48 kHz WAV, ~−12 dBFS, Lizenzvermerk notiert | ✅ fertig | `b9d51e9` |
| T4 | Miserlou-Loop-Datei `music/01 Miserlou (loop-196).m4a` (nahtlose interne Wdh., ~196 s, endet auf Downbeat) | Naht unhörbar, Länge 196±4 s, Analyse gecacht | ✅ 195,93 s, Region 43,2→103,2 s dupliziert, Nahtstellen ~103,2/163,2 s (RMS-stetig), Analyse gecacht — Ohrenprobe im Preview | `3104c99` |
| T5 | `audio-plan.md` neu: 3 neue Tracks, BPM/Beatgrid frisch, neue Anker, **kein Ducking**, Cast-SFX auf Miserlou-Grid | audio-designer, Datei konsistent zu `editorial-notes-round2.md` §0 | ✅ fertig | `a1d8088` |
| T6 | `beatsheet.md` neu: 3-Akt-Struktur auf ~7:08, Runde-2-Regie eingearbeitet | story-architect, Kapitelsummen = neue Musiklängen | ✅ fertig | `1dec782` |
| T7 | `timeline.json` neu bauen (timeline-builder): Reorder/Cuts, `fit: blur`, variables Ken Burns, Text-Regeln, Speed-Ramps, Aftermath-Order, Ende | `frameforge` validate_semantics grün, QC-Gate grün, Länge ~7:08 | ✅ fertig | `b2e93ea` |
| T8 | party-fx: Denkblasen/Sticker/Kronen/Herzchen/Speedlines/„Delirium"-Schrift, André-Konsistenz, Overlays neu rendern | Overlays gebaut, FX-Budget eingehalten | ✅ fertig | `b2e93ea` |
| T9 | `frameforge preview` neu, altes `JGA_preview.mp4` löschen, Audio gegenhören, an Christian | Neues Preview liegt, PROGRESS + Memory fortgeschrieben, Push | ✅ fertig | `ddd9a4d` |

Reihenfolge: T1 → T2 → (T3 ∥ T4) → T5 → T6 → T7 → T8 → T9. Commit + ggf. Push nach jedem Task.
`design/uploads/style-reference-jga-poster.png` ist jetzt versioniert (Stilreferenz, 2,7 MB).
Der Ordner `web/sites/.../Micha im Delirium — JGA Design System/` enthielt nur macOS-Müll
(`.DS_Store` / `.thumbnail`, beide jetzt in `.gitignore`) — kein echter Inhalt.

**T6 fertig (2026-09-09).** `beatsheet.md` Runde 2 neu geschrieben (story-architect, 682 Zeilen).
Gesamtlänge **428,40 s = 7:08,4**, Anker-Abgleich sauber: Intro+Akt 1 unter CL Theme 181,45 ✔ ·
Miserlou 181,45→377,38 = 195,93 ✔ · WIMM 377,38→422,38 = 45,00 ✔ · Stille 6,02 ✔. Loop-Nähte
(~284,7 / ~344,7 s) bewusst unter regulären Beat-Cuts. Untergebracht: **145/156 must · 14/50
nice · 1 ok (IMG_1449) · 0 forbidden · 0 Ducking-Stellen.**

- **Abweichung: 11 `must` gestrichen** — jede mit wörtlicher „raus"-Anweisung aus
  `editorial-notes-round2.md` belegt (Tabelle im Beat-Sheet §Bilanz): 1257, 1265, 1352, 1386,
  1391, 1393, 1395, **1445** (Bécasse-Eingang → 4817 trägt den Einstieg), 1664, 1703, 1705.
  Runde 2 überschreibt punktuell, daher Vorrang vor der `must`-Garantie. Falls Christian `must`
  absolut will: ~28 s müssten anderswo raus (v.a. B10-Videofenster).
- **6 Zeitstempel→Asset-ID-Zuordnungen sind abgeleitet**, nicht verifiziert (Runde 2 nennt nur
  `M:SS` aus dem alten Preview): 1352 (Kranbild), 1257 (nur das Bett), 1265 (2. Haus-Bild),
  1386 (Waffeln von vorn), 1697 (~8:11 Michael), 1706 (~8:30 vor der Tür). `timeline-builder`
  in T7 gegen die Keyframes gegenprüfen.
- **Struktur-Umbau:** Rooftop (B4–B6) und Karaoke (B8–B10) hart getrennt, Burger-Stop (B7)
  dazwischen; 1706 „vor der Tür" aus dem Aftermath in den Rooftop-Abgang; 1508 in die Mitte
  der Rooftop-Sequenz (hebt Runde-1-Zwang „1508 spät" auf); Aftermath in Christians diktierter
  Folge mit „Where is my mind?" auf Bild 1; Gurken-Ende 1660→1656→1658→1659→1661.
- **`target_duration_s: 534` in `brief.yaml` weiter veraltet** — in T7 auf ~428,4 nachziehen
  (sonst QC-Längenprüfung ±2 s, HANDOVER).

**T7 + T8 fertig (2026-09-10).** `timeline.json` Runde 2 komplett neu (timeline-builder),
danach FX-Schicht (party-fx). Beide QC-grün, Export-Phase `TIMELINE`.
- **timeline.duration 428,40 s.** video 172 · overlay 31 · audio 25 (3 music + 4 oton +
  18 sfx) · map 0. `qc.validate(...)` → leere Liste. `frameforge build` → „'JGA' ist TIMELINE".
- **Musik komplett getauscht**, alle Duck-Felder entfernt, `oton-01-img1395` + `oton-05-img1641`
  entfallen (4 O-Ton-Clips: 1460/1613/1637/4835, negatives `gain_db`, kein Ducking).
- **Abweichung von `audio-plan.md` §2.3:** WIMM-Clip `dur 51,02` (bis Filmende) statt 45,0,
  `fade_out_s 10,0` statt 4,0 — QC `_check_music_coverage` verbietet >1 s Stille am Schluss;
  der Song ist per Fade ~10 s vor Ende hörbar aus, „Stille unter der Danke-Karte" bleibt
  praktisch erhalten. Als `note` am Clip vermerkt.
- `brief.yaml` `target_duration_s` 534 → **428.4**.
- Ken Burns pro Clip variiert (Pan L/R, hoch/runter, rein/**raus**, ~jedes 3. Bild ohne),
  `fit:"blur"` auf allen Hochkant-Motiven, Speed-Ramps an 1621/1635/1637 (je 2 Sub-Clips
  `speed 1.6`+`1.0`, alle `intentional_repeat: true`).
- **André = „André"** mit Akzent (Bangers rendert É sauber, party-fx-Test-PNG geprüft).
- **31 Overlay-PNGs** in `exports/JGA/overlays/` (gitignored, reproduzierbar über
  `party-fx-recipe.py`): 18 Text + 9 Cast-Namen + 4 Comic-FX (Sticker Bär, Delirium-Schrift,
  Krone 1707, Herz 1706).
- **Offen fürs Preview (Feedback-Punkte):**
  - **IMG_8337 bleibt ungedreht** — Schema hat kein Rotate-Feld, Preview zeigt den Clip ggf.
    seitlich. `note` am Clip. Wenn Christian ihn drin haben will → Render braucht ein
    Rotate-Feature oder ein vorgedrehtes Derivat.
  - Cast-Namen ragen ~0,3 s ins Folgefoto (QC-Untergrenze `MIN_OVERLAY_READABLE_S 1,2` >
    0,9-s-Fotofenster) — nur über den Ausblend-Fade vor dem Cut gelöst, Beat-Grid unangetastet.
  - FX-Stärke (Herz/Krone/Glow), `color_pop`/`speedlines` nie real gerendert → im Preview prüfen.
  - „Buchstaben einzeln" ist über Slide+Fade angenähert, kein echter Per-Letter-Stagger.
  - `ov-sulemann` = „Suleman Pizza-Star" (falls „Süleman" gewünscht: `text` in der Timeline
    ändern + PNG neu).
- **Abweichung Prozess:** T7 wurde nicht vor T8 committet (Agenten liefen sequenziell ohne
  Zwischen-Checkpoint) → **ein** gemeinsamer T7+T8-Commit, beide Task-Zeilen zeigen denselben Hash.

**T9 fertig (2026-09-10).** `frameforge preview michael-jga-2026 JGA` (nohup+disown, ~8 min,
Ein-Pass-Graph 172 Inputs). Neues `exports/JGA/preview/JGA_preview.mp4`: **428,43 s = 7:08**,
71,8 MB, 1080p30. QC beim Preview-Gate ohne Meldung, ffmpeg-Log ohne Error/Warning. Altes
Runde-1-Preview (8:53) überschrieben, Backup entfernt. Export-Phase wieder `PREVIEWED` (8) —
Christian kann nach dem Sichten `frameforge approve` geben (dann T-Final).

**Runde 2 (T1–T9) komplett — wartet auf Christians Preview-Feedback.** Prüf-/Feedback-Punkte:
- **IMG_8337** (Clip v066) wird **nicht gedreht** — Schema hat kein Rotate-Feld, im Preview
  ggf. seitlich. Entweder Rotate-Feature ergänzen, vorgedrehtes Derivat einlegen, oder Clip raus.
- **Cast-Namen** ragen ~0,3 s ins Folgefoto (QC `MIN_OVERLAY_READABLE_S 1,2` > 0,9-s-Fotos).
- **FX-Stärke** (Herz/Krone/Glow), `color_pop`, `speedlines` zum ersten Mal real gerendert →
  Optik/Intensität gegen das Nachtmaterial prüfen.
- „Buchstaben einzeln" = Slide+Fade angenähert, kein echter Per-Letter-Stagger.
- `ov-sulemann` sagt „Suleman Pizza-Star" — falls „Süleman" gewünscht: `text` in der Timeline
  ändern + PNG neu rendern.
- **WIMM-Ausklang** (dur 51 / fade 10 statt 45 / 4) am Schluss gegenhören — soll die Danke-
  Karte wirklich in „gefühlter Stille" stehen.
- Loop-Nähte Miserlou bei ~284,6 s / ~344,5 s (unter Beat-Cuts) auf Hörbarkeit prüfen.

**Stand 2026-09-09 (Kontext):**
- T1–T6 fertig. T6 committet ohne Hash in der Task-Zeile (Hash-Merke unten), Hash im
  Folgecommit nachtragen.
- **T7:** `timeline.json` neu bauen (timeline-builder). Eingaben: neues `beatsheet.md` +
  beide `editorial-notes*.md` + `audio-plan.md` §2/§6 (3 Musik-Clips, 4 O-Ton-`oton`-Clips
  ohne Ducking-Feld, 18 Cast-SFX-Clips). Die „Offene Konflikte" #4–#8 im Beat-Sheet abarbeiten
  (abgeleitete IDs prüfen, Videofenster gegen echte Clipdauern, Speed-Ramp-`src_out`).
- **T7:** Export-Phase steht auf `PREVIEWED` (8). Für den Neubau der `timeline.json`
  muss zurück auf `TIMELINE`/`STORYBOARDED` — `frameforge build` erneut laufen lassen bzw.
  Gate-Weg prüfen (`.claude/hooks/gate.py`). Altes Preview `preview/JGA_preview.mp4` erst in
  T9 löschen. Vor `frameforge preview`: `df -h /` + `sysctl -n vm.swapusage`, ≥4 GB frei
  (HANDOVER — Preview-Render ist speicherfragil, ~20 min).
- **Hash-Merke:** in PROGRESS die Task-Zeile NICHT per `git commit --amend` mit dem eigenen
  Hash füllen (Hash ändert sich durch den Amend). Tick ohne Hash committen, Hash im
  Folgecommit nachtragen.

### Plan 0004 — JGA Runde 3 (Rework nach 2. Preview-Feedback, 2026-09-10)

Christian hat das 7:08-Preview (T9 / `ddd9a4d`) live gesichtet, Voice-Feedback mit Zeitmarken.
Urteil: „deutlich besseres Ergebnis, mega gut" — **Feinschliff, kein Neubau.** Struktur bleibt
(Intro+Akt 1 / Akt 2 / Aftermath, 3 Tracks unverändert). Vollständig transkribiert +
Clip-ID-Mapping in **`projects/michael-jga-2026/exports/JGA/editorial-notes-round3.md`**
(überschreibt Runde 1+2 punktuell). Kernpunkte:
- **Ken Burns:** viele „Bewegungen" bewegen sich real nicht — reiner Pan bei Zoom ~1.0 hat
  kein Crop-Fenster (11 Clips betroffen). Fix im Code (Mindest-Zoom bei Pan, neue Kurve
  `ease:"in"`) + Regie (2/3 der Fotos bewegt, Zoom+Pan gekoppelt, Richtung wechseln, `ease`
  mischen).
- **Blur-Extend auch für Videos** (Hochkant-Party-Videos mit schwarzen Balken).
- **Text-Overlays kompletter Neu-Look:** Bangers überall (auch Akt 1), Gold-Front +
  **harter Pink-Schatten +10/+10 px**, ≥ 2× Größe (WIMM-Titel ~5×), Slant-Vorzeichen nach
  Placement, Zitter-Effekt für „Stay hydrated"/„Delirium".
- **FX vielfältiger:** Herzchen-Cluster (Knutsch-Szene), drehende Sterne, Speedlines/Glows
  sichtbar machen.
- **Musik-Lücken:** tote Stille ~2:56–3:01 (CL→Miserlou) und ~6:05–6:19 (Miserlou→WIMM) —
  Crossfades, WIMM weich einblenden ab ~6:13, Danke-Karte 2–3 s länger.
- **~15 Streichungen / Umsortierungen / Text-Umformulierungen** (Detail in round3-Notes §1–4).
- **`ov-kunstfigur` / `ov-fx-krone-1707` / `ov-fx-delirium` löschen**; neu `ov-raetkeinkaese`,
  `ov-wimm` als großer Titel.
- **R4-T10 (blockiert):** nach Freigabe 4K-Final (Chunks) + Website + SSH-Upload — Ziel-Pfad/
  Benennung offen, **Frage an Christian**. Zwei Videos getrennt halten.

| # | Task | Abnahme | Status | Commit |
|---|------|---------|--------|--------|
| R3-T1 | `editorial-notes-round3.md` + diese Sektion + Bier-Recherche | Doku committed | ✅ fertig | — |
| R3-T2 | `render.py`: Pan-Mindestzoom, `ease:"in"`, `fit:blur` auf Video verifiziert | `pytest` grün (4 neue Tests), `doctor` grün, Mini-Render Portrait-Video ohne Balken | ✅ fertig | `0b4949f` |
| R3-T3 | `party-fx-recipe.py` Neu-Look (Bangers, Doppelebene, Größen, Slant, Streich/Neu-Overlays, Herz/Stern-Cluster), alle 30 PNGs neu | PNGs gebaut + visuell geprüft, `ov-kunstfigur`/`ov-fx-krone`/`ov-fx-delirium` weg | ✅ fertig | `ffdba90`,`3fc7b22` |
| R3-T4 | Bier-Zahl recherchieren | im round3-Notes vermerkt (500+ Biere / 50+ Brauereien) | ✅ fertig | `da0c046` |
| R3-T5+T6 | **In R3-T7 gefaltet** — `audio-plan.md`/`beatsheet.md` bekommen einen Runde-3-Delta-Block, aber die konkreten Musik-/Beat-Zeiten setzt der Timeline-Umbau direkt (Länge verschiebt sich durch die Cuts, Henne-Ei). Kein eigener Agentenlauf. | Delta-Notiz in beiden Dateien, `timeline.json`-Audio konsistent | 🔄 | |
| R3-T7 | `timeline.json` neu: alle Reorder/Cuts/Adds, `fit:blur` (Foto+Video), KB-Regie (Zoom+Pan gekoppelt, `ease` gemischt, ~2/3 bewegt), Text-Overlays neu verdrahtet + größer + neue Placements, Swaps (v117/118, v156/157, Rooftop-Order, v100 vor v098), La-Red ans Karaoke-Ende, Video-Trims (v069 +1s) + 5:48-Vorzug (v144/145 nach v137), Zoom/Ausschnitt-Fixes, Musik-Crossfades CL→Miserlou (~2:57) & Miserlou→WIMM (~6:11–6:13), Danke +2–3 s, Cast-Fenster ~1,4 s | `validate_semantics` + `qc.validate` leer, Länge ~7:0x, `brief.yaml` `target_duration_s` nachgezogen | 🔄 | |
| R3-T8 | party-fx-Effektpass auf neuer Timeline (Speedlines-Blitz, Cast-Farb-Pop) | Overlays + Effekte gesetzt, QC leer | ✅ fertig | `ad6c9da` |
| R3-T9 | `frameforge preview` neu, altes Preview ersetzen, PROGRESS+Memory, Push | Neues Preview liegt, gepusht | ✅ fertig | (dieser Commit) |
| R3-T10 | **Freigabe → 4K-Final (Chunks) + Website + SSH-Upload** | wartet auf Christians Sichtung + Server-Pfad | ⛔ blockiert | |

Reihenfolge: R3-T1 → R3-T2 → R3-T3 → R3-T7 (inkl. Audio) → R3-T8 → R3-T9. Commit nach jedem
Task.

**R3-T9 fertig (2026-09-10).** `frameforge preview michael-jga-2026 JGA` (nohup+disown, ~9 min,
Ein-Pass-Graph 223 Inputs). Neues `exports/JGA/preview/JGA_preview.mp4`: **422,23 s = 7:02**,
77,6 MB, 1920×1080, 12667 Frames + AAC. QC beim Preview-Gate leer, ffmpeg exit 0. Altes
Runde-2-Preview (7:08) überschrieben (Backup im Scratchpad). Export-Phase bleibt `PREVIEWED` (8).
Kontroll-Frames gesichtet (t=6/40/105/190/266/320/382): Blur-Extend auf Hochkant (Foto + Video)
greift, „LET'S GO!"/„500+ BIERE" im neuen Bangers-Gold/Pink-Look, Speedlines-Blitz sichtbar,
Ken Burns aktiv. **Wartet auf Christians Sichtung.**

**Prüf-/Feedback-Punkte fürs Sichten:**
- Ken Burns: jetzt „echte" Bewegung (Zoom+Pan gekoppelt, `ease:"in"`), ~1/3 Fotos bewusst
  statisch. Gesamteindruck + Richtungswechsel prüfen.
- Text-Overlays: Bangers überall, Gold-Front + harter Pink-Schatten, ~2× groß. Positionen
  (letsgo oben rechts, praesente/wtf oben links, christoph unten links) + Lesbarkeit prüfen.
- Musik-Übergänge: CL→Miserlou ~2:54 (1-s-Crossfade statt Loch — Miserlou läuft ~9 s unter den
  letzten Akt-1-Bildern), Miserlou→WIMM ~6:04–6:11 (Crossfade). Gegenhören: keine toten Stellen
  mehr, aber Miserlou-Downbeat sitzt nicht mehr exakt auf dem Crew-Update-Cut.
- Aftermath: 2–3 Kopf-Anschnitte (v162/v168/v169 Bereich) evtl. noch `pad` statt `blur`.
- „Delirium"-Bild-Wackel fehlt noch (Renderer kennt keinen Video-Jitter — Schema-Erweiterung
  nötig, falls gewünscht).
- Cast-Namen jetzt 2× groß + Fenster 1,4 s; Speedlines evtl. zu kräftig/dicht.

**R3-T10 (blockiert, Frage an Christian):** nach `frameforge approve` → 4K-Final in Chunks
(`render --resolution 3840x2160 --chunk-s ~90`, Muster
`web/sites/norwegen-2026/deploy/render-web-versions.sh`) + 1080p-Streaming-Fassung. Dann
Website `web/sites/michael-jga-2026/public/` (Video-Block + Download-Link wie
`norwegen-2026/public/film-vlog.html`). **Videos liegen getrennt vom Website-Build** unter
`/videos/` auf dem Server, benannt `JGA_1080p.mp4` + `JGA_4k.mp4`, per `rsync -avP` nach
`user@host:<video-verzeichnis>/`. **Offen: exakter SSH-Host + Server-Pfad für
`micha-jga.skubus.de/videos/`** (Norwegen-README hat nur einen Platzhalter), Traefik-Basic-Auth
serverseitig. Zwei Videos-Sätze (Norwegen / JGA) strikt getrennt halten.

---

### Plan 0004 — JGA Runde 4 (Rework nach 3. Preview-Feedback, 2026-09-10)

Christian hat das **7:02-Preview** (R3-T9 / `49cfced`) live gesichtet. Urteil: **"deutlich,
deutlich besser, gefällt mir sehr gut."** Feinschliff, kein Neubau. Struktur bleibt.
Vollständig transkribiert + Clip-Mapping in
**`projects/michael-jga-2026/exports/JGA/editorial-notes-round4.md`** (überschreibt Runde 1–3
punktuell). **Session endete am Wochen-Limit, bevor gebaut wurde — R4 ist reine Doku, Umsetzung
steht komplett aus.** Kernpunkte:

- **Text-Look NEU — 3 Ebenen** (überschreibt round3 Gold+Pink): Weiß-Front / Schwarz −3/−3 px /
  Pink +10/+10 px. Bangers bleibt. Alle Overlays vereinheitlichen.
- **Text-Neigung:** gerade oder von links-unten nach rechts-oben steigend — **nie nach
  rechts-unten fallend** ("Texte stürzen ab"). Ersetzt das placement-abhängige Slant aus R3.
- **Text-Größe:** regulär ×2 ggü. Preview `49cfced` (einzelne mehr; `ov-hydrated` −15 %).
- **Ken Burns noch ruhiger:** pro Clip **nur eine Aktion** (rein ODER raus), **eine Richtung**,
  Bewegung ab Frame 1 konstant oder leicht `ease:"in"`, keine Dreiecks-/Zickzack-Bewegung.
  Auch "statische" Fotos bekommen Mini-Zoom. Global prüfen.
- **Hochkant global:** alle Hochkantbilder als Hochkant + `fit:"blur"`, nicht reingezoomt.
  Nachkontrolle auf schwarze Balken. Namentlich: 0:49–0:52, 1:24, 2:44, 2:48, 3:14, 3:58,
  4:35, 5:59, 6:13 + alle Cast-Bilder.
- **Musik:** (1) Intro — erster Audio-Ausschlag auf den Bild-Fade-in. (2) Neuer Soundtrack
  **exakt bei 3:03** (Akt-1-Musik bis ~3:02 dehnen, max 1–2 s Stille) — ersetzt den ~2:57-
  Crossfade aus R3. (3) Akt-2-Video ~3:19 an den 3:03-Titelstart vorziehen. (4) Miserlou→WIMM
  wie R3. (5) Outro +2–3 s.
- **FX:** `ov-fx-sterne` / `sparkles` **komplett raus** (bewegen sich nicht). `ov-fx-herzen`
  mehr + verschiedene Größen, links+rechts. Stripes am Cast-Ende ~50 % weiter außen; Stripes
  bei ~5:21 raus.
- **Streichungen:** Bild 3:53 (Dach, gedoppelt), Bild nach `ov-christoph`, Bild 4:22
  (Downtown, prüfen).
- **Swaps:** 2:11↔2:14, 2:17↔2:18, 6:05-Bild↔Gurkenbild.
- **Text-Umformulierungen:** `ov-sulemann` "Der Mann / des Abends" (o.l., gerade) +
  "Pizzamann Sülemann Bestermann" (u.r., groß); `ov-praesente` "Süße Geschenke / für den /
  Junggesellen"; `ov-crewupdate` "Crew Update / die verlorenen Söhne / stoßen dazu" (rechts);
  `ov-gurken` "…mag Gurken. / Gib mir Gurken. / Er braucht sie dringend."; `ov-raetkeinkaese`
  → **"Rede kein Käse!"**; Cast #9 nur **"Micha"**; neu `ov-mok-detektor` ("MOK Detektor",
  Bild 2:48).
- **Positions-Fixes:** `ov-letsgo` unten rechts / weit links reingezogen ("L" bei ~60 %);
  `ov-rooftop` unten rechts; `ov-hydrated` ~20–25 % weiter nach rechts + Jitter ab Frame 1;
  `ov-christoph` gerade, unten links; `ov-wimm` auf Bild ~6:17, Zeilen enger; `ov-weiterziehen`
  auf Bild 5:52–5:53.

| # | Task | Abnahme | Status | Commit |
|---|------|---------|--------|--------|
| R4-T1 | `editorial-notes-round4.md` + diese Sektion + Memory | Doku committed | ✅ fertig | `3608fad` |
| R4-T2 | `party-fx-recipe.py`: 3-Ebenen-Renderer, Neigungslogik, Größen hoch, `ov-mok-detektor` neu, `ov-fx-sterne` löschen, Texte korrigieren, `ov-fx-herz-1706` Cluster erweitern, alle PNGs neu | PNGs gebaut + Edge-Clip-Check sauber | ✅ fertig | `7aeb6d5`,`43569be` |
| R4-T3 | `render.py`-Check | keine Änderung nötig — `ease:"linear"`/`"in"` + `_PAN_MIN_ZOOM` schon da, kein `sparkles`/`hearts` im Renderer. 93 render-Tests + `doctor` grün | ✅ fertig | (in `7659620`) |
| R4-T4 | `timeline.json` neu (`round4-timeline.py`): KB 1 Aktion/1 Richtung + Mini-Zoom, `fit:"blur"` auf allen 140 Fotos, Streichungen v089/v094/v106, Swaps v041b↔v043 + v044↔v045, v069+oton-01 an 3:03, Overlays neu verdrahtet + Positionen, `brief.yaml` nachgezogen | `validate_semantics` + `qc.validate` leer, Länge 419,5 s | ✅ fertig | `7659620` |
| R4-T5 | Audio: `music-01` fade_in 2,0→0,6 (Ausschlag auf Bild-Einblenden) + Ende ~3:01,4; `music-02` tl_in 183,0 (3:03, ~1,6 s Stille davor); `music-03` weich rein ~6:06; Outro-Karte +2,5 s | in `timeline.json` konsistent, QC leer | ✅ fertig | (in `7659620`) |
| R4-T6 | `frameforge preview` neu, altes 7:02-Preview ersetzen, Kontroll-Frames sichten, PROGRESS+Memory, Push | Neues Preview liegt, gepusht | ✅ fertig | (dieser Commit) |
| R4-T7 | **Freigabe → 4K-Final (Chunks) + Website + SSH-Upload** (= altes R3-T10) | wartet auf Christians Sichtung + Server-Pfad | ⛔ blockiert | |

Reihenfolge erledigt: R4-T1 → R4-T2 → R4-T3 → R4-T4/T5 → R4-T6.

**R4-T6 fertig (2026-09-11).** `frameforge preview michael-jga-2026 JGA` — **419,53 s = 6:59,5**,
1920×1080, 12586 Frames, 73,7 MB, ffmpeg exit 0, QC-Gate sauber. Altes 7:02-Preview ersetzt
(gitignored, kein Commit). **Fallstrick bestätigt:** ein per `nohup &`/Background-Task
gestarteter Lauf brach nach ~1 min ohne Meldung ab (0-Byte-Datei) — im **Vordergrund** lief er
durch (~9 min). Also weiter im Vordergrund starten.
Kontroll-Frames gesichtet (t=7,5/33/103/168/186/236/300/353/359/373): 3-Ebenen-Text
(Weiß/Schwarz/Pink) überall, Neigung steigend (nie fallend), Blur-Extension auf **allen** Fotos
(keine angeschnittenen Köpfe, keine schwarzen Balken), „CREW UPDATE" rechte Seite, „WTF?" pink
+ volles Bild, „WHERE IS MY / MIND?" Zeilen enger. Ken Burns ruhig (eine Richtung).

**Prüf-/Feintuning-Punkte fürs Sichten (bekannte kleine Abweichungen):**
- `ov-wimm` sitzt ~6:11–6:15 statt exakt „6:17–6:19" — ggf. +3 s später.
- `ov-crewupdate` Text berührt rechts fast den Rand (Bangers „STOßEN"/„SÖHNE" breit).
- Ken-Burns-Amplitude bewusst klein — falls zu wenig Bewegung, `PAN`/`ZD` in
  `round4-timeline.py` hochziehen und neu bauen.
- „stay hydrated"-Jitter läuft über `anim.drift_mode:"sine"` `period 0,45 s` — Stärke ggf.
  über `drift_px`/`drift_py` justieren.
- Musik: Downbeat Miserlou sitzt durch den 3:03-Start nicht mehr exakt auf dem
  Crew-Update-Cut (Christian-Wunsch „Titel exakt 3:03" gewinnt).
- `ov-sulemann-a`/`-b`, `ov-mok-detektor`, `ov-token` (2 Zeilen) zum ersten Mal real —
  Position/Größe gegenprüfen.

Christian will "heute Nacht" die Umsetzung, "morgen früh ein fertiges neues Preview". ✅ liegt.

---

### Plan 0004 — JGA Runde 5 (Rework nach 4. Preview-Feedback, 2026-09-11)

Christian hat das **6:59,5-Preview** (R4-T6 / `a31095a`) live gesichtet. Urteil: **"schon
wirklich großartig … hier geht es mehr um Präzision."** Reiner Feinschliff. Vollständig
transkribiert + Clip-Mapping in
**`projects/michael-jga-2026/exports/JGA/editorial-notes-round5.md`** (überschreibt Runde 1–4
punktuell). Kernpunkte:

- **Text-Look:** 3-Ebenen bleibt, aber **Front IMMER weiß** — `ov-geniesst` (war gelb) +
  `ov-wtf` (war pink) fixen, Gold/Orange-Front-Ausnahme entfällt komplett.
- **Erstes Bild `v003` × 2** (4,0 → 8,0 s). Nur **`v008` (0:21) gestrichen**. 30-Sekunden-Anker
  (`v011`) durch Trim von `v004`–`v007` halten.
- **KB noch ruhiger:** nie zwei Fotos hintereinander beide Zoom-OUT; `v028`/`v029` + Near-static-
  Set nur Mini-Zoom ohne Pan; `v039` Out; `v003`–`v015` fast unverändert; `v040` unangetastet.
- **Reihenfolge:** Schoko-Block `v041b→v041→v043→v044→v045→v046` (macht R4-Swaps rückgängig);
  `v097↔v100`; `v157↔v156`; `v159→v158` (Gurkenbild vor „Ich war es nicht"); `v117` vor `v122`.
- **Audio:** `music-01` bis ~1 s vor 3:03 (≤1 s Stille); 3:03-Cut unverändert; **Miserlou
  stoppt ~6:03** (nicht 6:15); **WIMM startet im Schwarz** (~1–2 s vor `v161`); Intro-Ausschlag
  auf `v003`-Einblenden.
- **Overlays:** `ov-hydrated` mittig + ×2; `ov-crewupdate` +10 % +Standzeit; `ov-geniesst`
  weiß +10 % tiefer; `ov-wtf` weiß +20 % tiefer schräger; `ov-mok-detektor` 2-zeilig groß;
  `ov-praesente`/`ov-christoph`/`ov-gurken`/`ov-raetkeinkaese` Text neu; `ov-token` rechts;
  `ov-lampen`/`ov-natuerlich`/`ov-sulemann-*` +Standzeit; `ov-weiterziehen`→`v153`;
  `ov-wimm`→`v162` tiefer + länger.
- **FX:** Speedlines 5:15 + 5:21 raus, neu auf `v143` (5:29); Cast-Linien-Kern ~30 % größer
  (oder kürzer).
- **Outro:** `jga-outro-card` +1,5 s; neue Schluss-Karte **`ov-thanks`** ("THANKS FOR WATCHING"
  / "No animals were harmed in the making of this movie."), **bleibt am Ende stehen**, nicht
  auf Schwarz enden.

| # | Task | Abnahme | Status | Commit |
|---|------|---------|--------|--------|
| R5-T1 | `editorial-notes-round5.md` + diese Sektion + Memory | Doku committed | ✅ fertig | `ccc8252` |
| R5-T2 | `party-fx-recipe.py` → Runde 5: Front überall weiß, Texte/Größen/Placements laut §5, `ov-thanks` neu, Cast-Linien-Kern, PNGs neu | PNGs gebaut + Edge-Clip-Check sauber | ✅ fertig | `08275b2` |
| R5-T3 | `render.py`-Check (End-Karte „bleibt stehen" durch QC/`validate_semantics`) | keine Änderung nötig — Overlay-PNGs sind formatfüllend bei x=0/y=0, End-Karte = `generated-black` + Overlay (bestehendes Muster). 134 Tests grün | ✅ fertig | (in `08275b2`) |
| R5-T4 | `round5-timeline.py`: `v003`×2, `v008` raus, Reihenfolge-Swaps, KB-Ruhe, Overlay-Retimes, Speedlines, Outro-Karte, `brief.yaml` | `validate_semantics` + `qc.validate` leer, Länge 423,3 s | ✅ fertig | `08275b2` |
| R5-T5 | Audio in `timeline.json`: `music-01` bis 3:03, `music-02` Stopp ~6:03, `music-03` im Schwarz, Intro-Sync | QC leer | ✅ fertig | (in `08275b2`) |
| R5-T6 | `frameforge preview` neu (Vordergrund!), altes 6:59,5-Preview ersetzen, Kontroll-Frames sichten, PROGRESS+Memory, Push | Neues Preview liegt, gepusht | ✅ fertig | (dieser Commit) |
| R5-T7 | **Freigabe → FHD (1080p) + 4K-Download (Chunks) + Website + SSH-Upload** | wartet auf Christians Sichtung + Server-Pfad | ⛔ blockiert | |

Reihenfolge erledigt: R5-T1 → R5-T2 → R5-T3 → R5-T4/T5 → R5-T6.

**R5-T6 fertig (2026-09-11).** `frameforge preview michael-jga-2026 JGA` — **423,33 s = 7:03,3**,
1920×1080, 30 fps, 73,15 MB, ffmpeg exit 0, QC-Gate sauber. Altes 6:59,5-Preview ersetzt
(gitignored). **Fallstrick-Update:** der Vordergrund-Lauf lief ~14:30 min (Harness hat ihn nach
10 min als Task weitergeführt — derselbe Prozess, sauber durchgelaufen, Exit 0). Kein `nohup`/
Detach — das bleibt der Abbruch-Modus, nicht die Harness-Task-Weiterführung.
Kontroll-Frames gesichtet (t=8/13/31,9/106/158,5/167,6/182,6/186,5/235,4/240/327,9/347,6/352,5/
359,2/363,4/371,5/410,5/421): erstes Bild 8 s + Blur-Extension; „LET'S GO!"; 30-s-Anker (v011)
bei 31,9 unverändert; **Front überall weiß** — `ov-geniesst` (war gelb) und `ov-wtf` (war pink)
gefixt; `ov-hydrated` mittig + ×2; `ov-mok-detektor` 2-zeilig; `ov-gurken` „Der Micha mag
Gurken. / Gib mir die Gurken. / Er braucht sie dringend."; `ov-raetkeinkaese` „Red kein Käse!";
`ov-crewupdate` rechts, steigend; Schwarzblende 6:02 = reine Stille; Schluss-Karte
„THANKS FOR WATCHING / No animals were harmed in the making of this movie." bleibt am Ende
stehen (kein Schwarz-Ende).

**Prüf-/Feintuning-Punkte fürs Sichten (bekannte kleine Abweichungen):**
- `v069`/Miserlou-Cut sitzt bei **182,0 s = 3:02,0** (Toleranz 3:02–3:05 eingehalten; der
  Akt-1-Tail wurde ~1,3 s geschrumpft, damit die Stille vor dem Cut ≤ 0,8 s bleibt).
- `ov-crewupdate` „STOSSEN" berührt rechts fast den Rand (Bangers breit) — wie Runde 4.
- `ov-geniesst` sitzt relativ hoch (y ~25 %); ragt nicht mehr raus, aber ggf. noch 2–3 %
  tiefer.
- `ov-thanks`-Disclaimer-Zeile ist klein (Font-Size 66 @ 4K) — lesbar, aber grenzwertig;
  ggf. auf ~80 hoch.
- Intro-Musik: `music-01` startet weiter bei `tl_in` 0 (erster Ausschlag ~2 s vor
  `v003`-Einblenden). Christian-Wunsch „Ausschlag auf Bild-Einblenden" nur grob getroffen —
  Feintuning über `src_in`-Offset möglich, falls es stört.
- Near-static-KB-Set (v006/v013/v020/v028/v029/v034/v049/v135/v150/v167) hat bewusst fast
  keinen Zoom — falls zu tot, `to`-Zoom in `round5-timeline.py` von 1.022 leicht hoch.

Christian will danach **FHD (1080p) + 4K-Download-Version — erst nach Freigabe dieses Previews**
(R5-T7).

---

### Plan 0004 — JGA Runde 6 (Rework nach 5. Preview-Feedback, 2026-09-11)

Christian hat das **7:03,3-Preview** (R5-T6 / `c7669ec`) live gesichtet. Urteil: **"schon
wirklich großartig … Feinschliff."** Transkript + Mapping in
**`projects/michael-jga-2026/exports/JGA/editorial-notes-round6.md`**. Zwei übergreifende
Themen + Einzel-Fixes:

- **Akt-1→Akt-2-Stille MUSS weg** (Hauptproblem, seit Runde 3 offen): `music-01` (CL) läuft
  ~1 s in Akt 2 hinein, `music-02` (Miserlou) setzt 0,5 s vor dem `v069`-Cut ein → ~1,5 s
  Überlappung, kein Loch. Dafür **`v007` (~0:23) + `v022` (~1:11) gestrichen** (~6 s). `v069`
  rutscht von 3:02 auf ~2:58 (ok laut Christian).
- **Kein Text ragt ins nächste Bild** (durchgängige Regel): Host-Foto wächst, textfreie
  Nachbarn werden gekürzt. Betroffen: `ov-crewupdate` (Host `v058` +1,7 s), `ov-token`
  (`v110` +1,1 s), `ov-natuerlich` (Video `v145` +1,8 s), `ov-weiterziehen` (auf `v153`,
  +2,2 s; Taxi-`v154` vorne gekürzt), Gurken-Cluster (`v159` +1,0 s, `v158` +0,8 s).
  **Ausnahme:** `ov-wimm` darf über zwei Fotos.
- **Einzel:** Intro-Karte `v001` +2,0 s · `ov-mok-detektor` 3-zeilig „MOK/DETEKTOR/AKTIV" mit
  Abstand · `ov-hydrated` −35 % + oben rechts · Schwarzblende `v160` +1,5 s (Musik danach).

| # | Task | Abnahme | Status | Commit |
|---|------|---------|--------|--------|
| R6-T1 | `editorial-notes-round6.md` + diese Sektion | Doku committed | ✅ fertig | (dieser Commit) |
| R6-T2 | `party-fx-recipe.py` Runde 6: `ov-mok-detektor` 3-zeilig, `ov-hydrated` klein/o.r. | PNGs gebaut, kein Edge-Clip | ✅ fertig | (dieser Commit) |
| R6-T3 | `round6-timeline.py`: 2 Streichungen, Host-Verlängerungen + Nachbar-Kürzungen, `v001`/`v160` +, Anti-Bleed-Sicherung, Audio aneinanderschieben, `brief.yaml` | `validate_semantics` + `qc.validate` leer, 134 Tests grün | ✅ fertig | (dieser Commit) |
| R6-T4 | `frameforge preview` neu (Vordergrund!), altes 7:03,3-Preview ersetzen, Kontroll-Frames sichten, PROGRESS+Memory, Push | Neues Preview liegt, gepusht | 🔄 | |
| R6-T5 | **Freigabe → FHD (1080p) + 4K-Download (Chunks) + Website + SSH-Upload** | wartet auf Christians Sichtung + Server-Pfad | ⛔ blockiert | |

Ergebnis `round6-timeline.py`: Dauer **425,05 s = 7:05,05**, video 160 / overlay 34 / audio 25.
`music-01`-Ende 179,03 s / `music-02`-Start 177,53 s → 1,5 s Überlappung, kein stiller Spalt.
`v069` bei 178,03 s (2:58,03). Anti-Bleed-Klemme musste nichts kürzen (Host-Streckung reichte).
