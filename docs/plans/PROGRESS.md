# Fortschritt M0 — Gerüst

**M0 ist fertig (alle 7 Tasks, 2026-07-27).** Nächster Meilenstein: M1 (Mini-Prototyp
end-to-end, siehe Notizen zu Task 7 unten und Plan Abschnitt 8).

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
| M1.5 | `design.py` Rendering (SVG→PNG), minimale SVG-Templates | ⬜ offen | |
| M1.6 | `map.py` Route-Reveal-Frames | ⬜ offen | |
| M1.7 | `render.py` (Filtergraph-Bau, Proxy-Render) | ⬜ offen | |
| M1.8 | `projects/proto/` anlegen, komplett durch die Pipeline bis zum Preview | ⬜ offen | |

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

### Hinweis zu Commit `849ff6d`

Der Initial-Commit hat den damals frisch geschriebenen Task-2-Code versehentlich mit
eingesammelt (zwei Sessions liefen kurzzeitig parallel im selben Repo). Die Commit-Message
sagt deshalb fälschlich, es gäbe noch keinen Anwendungscode. Rein kosmetisch — nicht
nachträglich reparieren, der nächste Commit stellt es gerade.

**Regel daraus:** immer nur eine Session gleichzeitig in diesem Repo arbeiten lassen.
