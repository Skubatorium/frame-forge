# FrameForge — Initialer Struktur- und Aufbauplan

## Context

`/Users/christianskubatz/Workspace/Repos/frame-forge` ist aktuell ein leerer Ordner ohne Git-Repo. Ziel ist ein **generisches, wiederverwendbares Videoschnitt-System**, in dem Claude Code als Orchestrator arbeitet — nicht als Editor. Die eigentliche Verarbeitung machen Python, FFmpeg und lokale CV-/Audio-Bibliotheken.

Konkreter erster Anwendungsfall: ein Norwegen-Roadtrip-Film aus ~100 GB vorsortiertem Roh­material (getrimmte Clips, Fotos, GPX-Route). Das System muss aber **projektunabhängig** sein: neuer Urlaub → neuer Projektordner → gleicher Prozess.

Das zentrale Problem, das der Plan löst: ohne erzwungene Reihenfolge und ohne persistenten Material-Index würde jeder Schnittversuch das gesamte Material neu analysieren (Token-Verbrennung) und der Orchestrator würde ad-hoc FFmpeg-Kommandos raushauen statt einem reproduzierbaren Prozess zu folgen. Deshalb: **State-Machine mit harten Gates, hash-basierter Analyse-Cache, klare Agenten-Rollen.**

Zweites Kernproblem: ein 90-Sekunden-Teaser und ein 15-Minuten-Film sind völlig verschiedene Produkte aus demselben Material. Deshalb Trennung **Projekt** (Material, Index, Designsystem) ↔ **Export** (Brief, Stil, Timeline, Render). Ein Projekt hat n Exporte.

### Getroffene Entscheidungen

| Thema | Entscheidung |
|---|---|
| Render-Ziel | Timeline-JSON → FFmpeg-Render **und** FCPXML/OTIO-Export für DaVinci Resolve |
| Analyse | Hybrid: lokale CV-Metriken + Claude Vision auf Keyframes, hash-gecacht |
| Musik | Eigene Dateien in `music/` + Prompt-Generator für KI-Musik + O-Ton-Erhalt mit Ducking |
| Stack | Python |
| Medien-Ort | Extern, Pfad in Projekt-Config (Repo bleibt klein) |
| Prozess-Durchsetzung | Harte Gates: `PreToolUse`-Hook + `.state.json` |
| Karte | Python + gecachte OSM-Tiles → PNG-Sequenz mit Alpha |
| Text/Grafik | SVG-Templates → PNG mit Alpha → FFmpeg-Overlay |
| Briefing | Slash-Command-Wizard `/ff-brief` |
| Agenten | orchestrator + 7 Sub-Agenten inkl. audio-designer |
| Reihenfolge | M0 Gerüst → M1 Mini-Prototyp → Rest |
| Sprache | Pro Export konfigurierbar; interne Beschreibungen Deutsch |

---

## 1. Repo-Struktur (M0 legt das an)

```
frame-forge/
├── CLAUDE.md                     # Prozessregeln, Constraints, Token-Disziplin
├── README.md
├── pyproject.toml                # uv/pip, Python 3.12
├── .gitignore                    # media/, proxies/, cache/, output/, .venv/
├── .python-version
│
├── .claude/
│   ├── settings.json             # Hooks, Permissions, Model-Defaults
│   ├── agents/
│   │   ├── media-indexer.md
│   │   ├── story-architect.md
│   │   ├── timeline-builder.md
│   │   ├── design-system.md
│   │   ├── audio-designer.md
│   │   ├── map-animator.md
│   │   ├── render-engineer.md
│   │   └── qc-reviewer.md
│   ├── commands/
│   │   ├── ff-new.md             # neues Projekt anlegen
│   │   ├── ff-ingest.md          # Material einlesen + Proxies
│   │   ├── ff-index.md           # Analyse + .md-Beschreibungen
│   │   ├── ff-design.md          # Designsystem-Wizard
│   │   ├── ff-brief.md           # Export-Briefing-Wizard
│   │   ├── ff-build.md           # Story → Timeline
│   │   ├── ff-preview.md         # 1080p-Proxy-Render
│   │   ├── ff-render.md          # Final-Render
│   │   └── ff-status.md          # State + nächster erlaubter Schritt
│   └── hooks/
│       └── gate.py               # PreToolUse-Gate gegen .state.json
│
├── docs/
│   ├── plans/
│   │   └── 0001-initial-structure.md   # ← dieser Plan, ins Repo kopiert
│   ├── styles/
│   │   └── style-catalog.md      # Stil-Presets (siehe §6)
│   └── process.md                # Der Prozess als Referenz für Menschen
│
├── frameforge/                   # Python-Package (die Werkzeugschicht)
│   ├── __init__.py
│   ├── cli.py                    # einheitlicher Entry: python -m frameforge <cmd>
│   ├── state.py                  # State-Machine, Phase-Übergänge, Locking
│   ├── project.py                # Projekt-/Export-Auflösung, Pfade
│   ├── ingest.py                 # Scan, Hashing, Proxy-Erzeugung
│   ├── probe.py                  # ffprobe, EXIF, GPS, Zeitstempel
│   ├── analyze.py                # Schärfe, Stabilität, Belichtung, Motion, Scenes
│   ├── keyframes.py              # Keyframe-Extraktion für Vision
│   ├── index.py                  # Index-Schreiber (.md + assets.json)
│   ├── gpx.py                    # GPX-Parsing, Zuordnung Asset↔Ort
│   ├── audio.py                  # BPM/Beats/Energie, Ducking-Kurven
│   ├── design.py                 # Design-Tokens → SVG → PNG
│   ├── map.py                    # Karten-Frames, Marker, Route-Reveal
│   ├── timeline.py               # Timeline-Schema, Validierung
│   ├── render.py                 # FFmpeg-Graph-Bau, Proxy-/Final-Render
│   ├── nle.py                    # FCPXML / OTIO Export
│   └── qc.py                     # Timeline-Checks vor Render
│
├── templates/
│   ├── project/                  # Skeleton für neue Projekte
│   ├── svg/                      # lower-third, title-card, chapter, credits
│   └── prompts/                  # Prompt-Vorlagen: Musik, Grafik, Freisteller
│
├── tests/
│   └── fixtures/                 # winzige Test-Clips/Fotos (im Repo, wenige MB)
│
└── projects/
    └── .gitkeep                  # Projekte selbst: .gitignore außer Configs
```

### Projekt-Struktur (pro Videoprojekt)

```
projects/norwegen-2026/
├── project.yaml            # Name, Medien-Root (extern!), Zeitzone, Sprache-Default
├── .state.json             # Phasen-State — vom Hook gelesen, NICHT von Hand ändern
├── design/
│   ├── tokens.yaml         # Farben, Schriften, Spacing, Motion-Kurven
│   ├── fonts/              # tatsächliche Font-Dateien
│   ├── assets/             # Logos, Freisteller (Familie/Auto), Texturen
│   └── prompts.md          # generierte Prompts für fehlende Grafiken
├── index/
│   ├── assets.json         # maschinenlesbar: EIN Eintrag pro Asset
│   ├── assets/
│   │   ├── 20260714-drone-fjord-001.md    # menschenlesbare Beschreibung
│   │   └── ...
│   └── days/
│       └── 2026-07-14.md   # Tageszusammenfassung (Orte, Highlights, Lücken)
├── route/
│   ├── roadtrip.gpx
│   └── locations.csv       # Übernachtungen, POIs, manuelle Korrekturen
├── music/                  # deine lizenzierten Tracks (gitignored)
│   └── analysis/*.json     # BPM, Beat-Grid, Energiekurve — gecacht
└── exports/
    └── teaser-90s/
        ├── brief.yaml      # Ergebnis des /ff-brief-Wizards
        ├── beatsheet.md    # Dramaturgie vom story-architect
        ├── timeline.json   # die Schnittliste (Single Source of Truth)
        ├── overlays/       # gerenderte PNGs mit Alpha
        ├── map/            # gerenderte Karten-Clips
        ├── preview/        # 1080p-Proxy-Renders, versioniert
        ├── final/          # 4K-Export
        └── nle/            # export.fcpxml, export.otio
```

**Rohmedien liegen extern.** `project.yaml` enthält z. B. `media_root: /Volumes/Media/norwegen-2026/`. Proxies und Keyframes landen in einem Cache-Ordner (Standard: `~/.cache/frameforge/<project-hash>/`), damit nichts das Repo aufbläht.

---

## 2. Der erzwungene Prozess (State-Machine)

```
INIT → INGESTED → INDEXED → DESIGNED → BRIEFED → STORYBOARDED
     → TIMELINE → ASSETS_BUILT → PREVIEWED → APPROVED → RENDERED
```

`.state.json` hält pro Projekt die erreichte Phase, pro Export einen eigenen Sub-State ab `BRIEFED`, plus Content-Hashes der Eingaben.

**Gate-Regeln (Auszug):**

| Aktion | Vorbedingung |
|---|---|
| `ff-index` | Phase ≥ INGESTED |
| `ff-brief` | Phase ≥ INDEXED **und** DESIGNED |
| `ff-build` | Export-Phase ≥ BRIEFED, `brief.yaml` validiert |
| `ff-preview` | `timeline.json` existiert **und** besteht `qc.validate()` |
| `ff-render` (final) | Export-Phase = APPROVED (explizite Freigabe durch dich nach Preview) |
| direkter `ffmpeg`-Aufruf | **immer blockiert** außer aus `frameforge.render` heraus |

**Durchsetzung:** `.claude/hooks/gate.py` als `PreToolUse`-Hook auf `Bash`. Er inspiziert das Kommando, erkennt `ffmpeg`/`ffprobe`/`python -m frameforge …`, liest `.state.json` und gibt bei Verstoß Exit-Code 2 mit einer Meldung zurück, die dem Orchestrator sagt, **welcher Schritt zuerst fällig ist**. Ergänzend prüft jedes Python-Modul seine Vorbedingung selbst (Gürtel + Hosenträger, falls Hooks mal deaktiviert sind).

**Invalidierung:** Ändert sich `brief.yaml`, fällt der Export auf `BRIEFED` zurück. Kommt neues Rohmaterial dazu, fällt das Projekt auf `INGESTED` — aber der Analyse-Cache bleibt, es werden nur die neuen Hashes verarbeitet.

---

## 3. Token-Disziplin (harte Regeln in `CLAUDE.md`)

1. **Analyse genau einmal pro Datei.** Schlüssel ist `sha256(erste 1 MB + Dateigröße + mtime)`. Existiert der Eintrag in `assets.json`, wird die Datei nie wieder an ein Modell geschickt.
2. **Vision nur auf Keyframes.** Standard: 3 Frames je Clip (10 %, 50 %, 85 %), auf 768 px lange Kante skaliert, JPEG q80. Fotos: 1 Frame. Bei erkannten Szenenwechseln zusätzlich je 1 Frame pro Szene, gedeckelt auf 6.
3. **Agenten lesen niemals ganze Verzeichnisse.** Sie fragen `python -m frameforge query …` mit Filtern (Tag, Datum, Ort, Rating, Dauer) und bekommen kompaktes JSON zurück — nicht 400 Markdown-Dateien.
4. **Keine Rohmedien-Pfade ins Modell-Kontextfenster außer als IDs.** Asset-IDs sind stabil und kurz: `20260714-drone-fjord-001`.
5. **Preview-Renders laufen immer auf Proxies.** Final-Render mappt automatisch auf die 4K-Originale.
6. **Ergebnisse persistieren.** Beatsheet, Timeline, QC-Report sind Dateien, keine Chatverläufe.

---

## 4. Datenmodell

### `assets.json` — ein Eintrag pro Asset

```json
{
  "id": "20260714-drone-fjord-001",
  "hash": "sha256:…",
  "path": "video/day03/DJI_0042.MP4",
  "kind": "video",
  "captured_at": "2026-07-14T09:12:33+02:00",
  "gps": { "lat": 62.1049, "lon": 6.9394, "place": "Geirangerfjord" },
  "tech": { "w": 3840, "h": 2160, "fps": 29.97, "dur": 18.4, "bitrate": 98000000, "codec": "hevc" },
  "quality": { "sharpness": 0.81, "stability": 0.93, "exposure": 0.72, "score": 0.84 },
  "motion": { "type": "drone_forward", "speed": 0.4 },
  "scenes": [{ "start": 0.0, "end": 18.4 }],
  "content": {
    "summary": "Drohnenflug über den Geirangerfjord, Sonne von links, Kreuzfahrtschiff klein im Bild.",
    "tags": ["fjord", "drohne", "wasser", "berge", "sonnig", "weitwinkel"],
    "people": false, "usable_as": ["establisher", "b-roll", "outro"]
  },
  "audio": { "has_speech": false, "ambience": "wind", "keep_original": false },
  "rating": 4,
  "md": "index/assets/20260714-drone-fjord-001.md"
}
```

Die `.md`-Datei je Asset enthält dasselbe menschenlesbar plus Freitext-Notizen, die du selbst ergänzen kannst — deine Ergänzungen überleben Re-Indexierung (Merge statt Überschreiben).

### `timeline.json` — Single Source of Truth für Render **und** NLE-Export

```json
{
  "version": 1,
  "export": "teaser-90s",
  "fps": 25, "resolution": [3840, 2160], "duration": 92.0,
  "tracks": {
    "video": [
      { "id": "c001", "asset": "20260714-drone-fjord-001",
        "src_in": 3.2, "src_out": 7.4, "tl_in": 0.0,
        "speed": 1.0, "transition_in": {"type": "fade", "dur": 0.5},
        "effects": [{"type": "kenburns", "from": [0,0,1.0], "to": [0.05,0.02,1.12]}] }
    ],
    "overlay": [
      { "id": "o001", "png": "overlays/title-main.png", "tl_in": 1.0, "dur": 3.5,
        "anim": {"in": "slide_up", "out": "fade"} }
    ],
    "map": [
      { "id": "m001", "clip": "map/leg-01.mov", "tl_in": 22.0, "dur": 6.0, "blend": "over" }
    ],
    "audio": [
      { "id": "a001", "src": "music/epic-north.wav", "tl_in": 0.0, "gain_db": -6 },
      { "id": "a002", "asset": "20260715-waterfall-002", "type": "original",
        "tl_in": 41.0, "dur": 4.0, "duck_music_db": -14 }
    ]
  }
}
```

`frameforge.render` baut daraus den FFmpeg-Filtergraph; `frameforge.nle` schreibt dieselbe Struktur als FCPXML/OTIO. Beide lesen **nur** dieses Schema — damit kann Render und Resolve-Export nie auseinanderlaufen.

---

## 5. Agenten

Der **Orchestrator** ist die Haupt-Session. Er implementiert nichts selbst und ruft kein FFmpeg auf. Er liest `.state.json`, entscheidet den nächsten Schritt, delegiert, prüft Ergebnisse gegen die Gates.

| Agent | Modell | Aufgabe | Darf |
|---|---|---|---|
| `media-indexer` | Sonnet 5 | Keyframes ansehen, Beschreibung + Tags + Rating erzeugen, `.md` und `assets.json` schreiben | Read, Write, Bash (nur `frameforge`-CLI) |
| `story-architect` | Opus 5 | Aus Brief + Index ein Beat-Sheet bauen: Kapitel, Bögen, Pacing, Musik-Sync-Punkte | Read, Write |
| `timeline-builder` | Sonnet 5 | Beat-Sheet → gültige `timeline.json`, Clip-Auswahl, In/Out-Punkte | Read, Write, Bash |
| `design-system` | Sonnet 5 | Tokens, SVG-Templates, Grafik-Prompts | Read, Write, Bash |
| `audio-designer` | Sonnet 5 | Track-Auswahl, Beat-Mapping, O-Ton-Selektion, Ducking-Kurven, Musik-Prompts | Read, Write, Bash |
| `map-animator` | Sonnet 5 | GPX → Karten-Clips mit Route, Markern, Figur | Read, Write, Bash |
| `render-engineer` | Sonnet 5 | FFmpeg-Graphen, Encoding-Settings, Fehlerdiagnose bei Renderabbrüchen | Read, Write, Bash |
| `qc-reviewer` | Opus 5 | Timeline gegen Brief prüfen: Länge, Clip-Doppler, schwarze Frames, Audio-Clipping, Lesbarkeit von Text | Read, Bash |

Opus gezielt für Dramaturgie und QC — das sind die Stellen mit vielen Abhängigkeiten. Alles andere Sonnet.

---

## 6. Stil-Katalog (`docs/styles/style-catalog.md`)

Der Brief-Wizard bietet diese Presets an; jedes ist ein YAML-Fragment mit Pacing-, Schnitt-, Farb- und Typo-Parametern, das du überschreiben kannst.

| Preset | Schnittrhythmus | Charakter | Passt zu |
|---|---|---|---|
| **Nordic Cinematic** | 4–8 s, langsam | Weite Establisher, Slow-Push, kalte Highlights/warme Lichter, viel Ambiente, sparsamer Text | Der 15-Minuten-Norwegen-Film |
| **Punch Teaser** | 0,4–1,5 s, beat-getrieben | Harte Cuts auf den Beat, Whip-Pans, große Typo, Escalation zum Drop | 60–90 s Trailer |
| **Chronikel** | 3–6 s | Strikt chronologisch, Tages-Kapitelkarten, Karte zwischen den Etappen, ruhig erzählt | Der „was haben wir gemacht"-Film für Familie |
| **Thematisch/Assoziativ** | 2–5 s | Nicht chronologisch, gruppiert nach Motiv (Wasser, Straßen, Essen, Abende), Match-Cuts | Zweitfassung mit anderem Blick |
| **Diary / Handheld** | 1,5–4 s | Roher Look, O-Ton dominant, Musik nur Bett, handschriftliche Typo | Persönlicher, intimer Schnitt |
| **Timelapse Journey** | variabel | Bewegungslastig, Karte als Leitmotiv, Zeitraffer-Blöcke, minimaler Text | Roadtrip-Fokus |

Jedes Preset legt fest: `pacing`, `transition_vocabulary`, `color_grade`, `text_density`, `music_energy_curve`, `map_usage`, `photo_treatment` (Ken Burns Intensität), `original_audio_policy`.

**Wichtig:** Preset ≠ Zwangsjacke. `brief.yaml` = Preset + deine Overrides + Muss-Shots + verbotene Shots.

---

## 7. Designsystem pro Projekt

Ja — lohnt sich, weil Norwegen und z. B. Toskana visuell nichts gemeinsam haben. `/ff-design` führt durch:

1. **Stimmung** (3–5 Adjektive) → Vorschlag für Farbpalette + 2 Schriftfamilien
2. **Typo**: Display + Text, Größenskala, Tracking. Für Norwegen z. B. eine geometrische Grotesk mit hohem Gewicht, keine Serifen.
3. **Farbe**: Primär, Sekundär, Akzent, Text-auf-Bild-Kontrast, Safe-Area-Regeln
4. **Motion**: Ein-/Ausblendkurven, Standardlängen
5. **Assets-Inventur**: Was fehlt? → generiert `design/prompts.md` mit fertigen Prompts für Freisteller (Familie, Auto), Logo, Kartenmarker, Texturen. Du besorgst die Bilder, legst sie in `design/assets/`, Wizard erkennt sie beim nächsten Lauf.

Tokens landen in `design/tokens.yaml` und speisen die SVG-Templates. Dieselben Tokens gelten für alle Exporte eines Projekts → Teaser und Hauptfilm sehen wie eine Familie aus.

---

## 8. Milestones

### M0 — Gerüst (kein Video, nur Fundament)
- `git init`, `.gitignore`, `pyproject.toml`, venv via `uv`
- Systemabhängigkeiten prüfen/installieren: **ffmpeg fehlt aktuell** (`brew install ffmpeg exiftool`)
- Python-Deps: `opencv-python`, `scenedetect`, `librosa`, `numpy`, `Pillow`, `pyexiv2`, `gpxpy`, `pyyaml`, `pydantic`, `rich`, `typer`, `staticmap`, `cairosvg`, `opentimelineio`
- Komplette Ordnerstruktur + alle Modul-Stubs mit Signaturen und Docstrings
- `CLAUDE.md` mit Prozessregeln und Token-Disziplin
- Alle 8 Agenten-Definitionen, alle 9 Slash-Commands, `gate.py`-Hook
- `docs/plans/0001-initial-structure.md` (dieser Plan) + `docs/process.md` + `docs/styles/style-catalog.md`
- `python -m frameforge doctor` prüft die Umgebung und meldet Fehlendes
- **Fertig wenn:** `/ff-status` läuft, `doctor` grün, Gate blockiert einen verfrühten `ff-render`-Versuch nachweislich

### M1 — Mini-Prototyp end-to-end
Testprojekt `projects/proto/` mit 3–5 Clips, 2 Fotos, kurzer GPX-Spur:
- `ff-ingest` → Proxies (1080p, H.264, schnelles Preset)
- `ff-index` → CV-Metriken + Vision-Beschreibungen + `.md`-Dateien
- `ff-design` → minimales Tokenset
- `ff-brief` → Preset „Nordic Cinematic", 60–90 s
- `ff-build` → `timeline.json`
- Karten-Clip für eine Etappe, ein Titel-Overlay, ein Musiktrack, zwei O-Ton-Fenster mit Ducking
- `ff-preview` → 1080p MP4
- **Fertig wenn:** ein abspielbares 60–90-s-Video existiert, das den Brief erfüllt

### M2 — Story-Engine vertiefen
Beat-Sheet-Logik, Clip-Scoring gegen Brief-Ziele, Vermeidung von Wiederholung, Musik-Sync auf Beat-Grid, `qc-reviewer` mit echtem Regelsatz.

### M3 — Karte & Grafik ausbauen
Route-Reveal mit Easing, Marker-Typen, Figur/Auto entlang der Spur, Tile-Cache, Kapitelkarten, Bauchbinden-Varianten.

### M4 — Final-Pipeline
4K-Mapping auf Originale, Farbkorrektur-Stufe, Loudness-Normalisierung (EBU R128), NLE-Export FCPXML + OTIO, Render-Versionierung.

### M5 — Norwegen-Realbetrieb
Volles Material indexieren (batchweise, mit Fortschritts-Resume), Hauptfilm + Teaser als zwei Exporte aus einem Projekt.

Optional danach: Werkzeugschicht als MCP-Server kapseln (`analyze_video`, `build_chapter`, `render_preview` …). Erst sinnvoll, wenn die CLI stabil ist.

---

## 9. Kritische Dateien (Reihenfolge der Erstellung in M0)

1. `pyproject.toml`, `.gitignore` — Fundament
2. `frameforge/state.py` — die State-Machine, alles andere hängt daran
3. `frameforge/project.py` — Pfadauflösung
4. `.claude/hooks/gate.py` + `.claude/settings.json` — Durchsetzung
5. `CLAUDE.md` — Regeln, die der Orchestrator jede Session liest
6. `frameforge/timeline.py` — Schema als Pydantic-Modell, gemeinsame Basis von Render und NLE
7. Restliche Module als Stubs
8. Agenten + Commands

---

## 10. Verifikation

**M0:**
```bash
cd /Users/christianskubatz/Workspace/Repos/frame-forge && python -m frameforge doctor
```
Erwartung: alle Abhängigkeiten grün, ffmpeg-Version gemeldet.

Gate-Test (muss **fehlschlagen**):
```bash
python -m frameforge render --project proto --export teaser-90s
```
Erwartung: Abbruch mit Meldung „Phase INIT — erforderlich: ingest → index → design → brief → build → preview → approve".

**M1:**
```bash
python -m frameforge doctor && python -m frameforge status --project proto
```
Danach `/ff-preview proto teaser-90s` und die erzeugte Datei unter `projects/proto/exports/teaser-90s/preview/` ansehen.

Automatisiert:
```bash
pytest tests/ -v
```
Deckt ab: State-Übergänge inkl. verbotener Sprünge, Timeline-Schema-Validierung, Hash-Cache (zweiter Index-Lauf macht null Vision-Calls), FFmpeg-Graph-Erzeugung gegen erwarteten String, FCPXML-Roundtrip.

**Manuelle Abnahme M1:** Video läuft durch, kein schwarzer Frame, Titel lesbar, Musik nicht übersteuert, O-Ton hörbar an den zwei markierten Stellen.

---

## 11. Offene Punkte für später

- **Gesichts-/Personenerkennung** für „zeig mehr von Oskar" — technisch machbar (face_recognition), aber Datenschutz-/Aufwandsfrage. Nicht in M0–M4.
- **Automatische Untertitel** aus O-Ton (Whisper lokal) — sinnvoll, wenn ihr im Film sprecht.
- **Farbmanagement** bei HLG/D-Log-Drohnenmaterial — braucht LUT-Handling, in M4 einplanen wenn dein Material Log ist.
- **Musik-Lizenz-Nachweis** je Export als Textdatei mitschreiben, falls du veröffentlichst.
