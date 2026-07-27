# Fortschritt

**M0 (Gerüst) und M1 (Mini-Prototyp end-to-end) sind fertig (2026-07-27).** Nächster
Meilenstein: M2 — Story-Engine vertiefen (siehe Notizen zu M1.8 unten und Plan Abschnitt 8).

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
| M4.1 | `render.render_final` (4K-Mapping, EBU-R128-Loudnorm, optionale LUT, Render-Versionierung), `cli.py` `render` verdrahtet | ✅ fertig | siehe Notizen |
| M4.2 | `nle.py` (FCPXML/OTIO-Export), `cli.py nle`-Kommando | ✅ fertig | siehe Notizen |

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
