# FrameForge

Orchestrierte, **reproduzierbare** Videoschnitt-Pipeline für Reise- und Projektfilme. Claude
Code arbeitet als **Orchestrator** — er entscheidet, delegiert an Sub-Agenten und prüft
Ergebnisse. Die eigentliche Verarbeitung machen Python, FFmpeg und lokale CV-/Audio-
Bibliotheken. Jeder Schnitt entsteht reproduzierbar aus einer `timeline.json`, ein
Prozess mit harten Gates verhindert, dass Schritte übersprungen oder Material doppelt
analysiert wird.

- **Vollständiger Plan / Architektur:** `docs/plans/0001-initial-structure.md`
- **Arbeitsstand & Design-Entscheidungen:** `docs/plans/PROGRESS.md`
- **Prozess als Referenz:** `docs/process.md`
- **Stil-Presets:** `docs/styles/style-catalog.md`

---

## 1. Das mentale Modell (kurz, aber wichtig)

**Projekt ≠ Export.** Ein *Projekt* ist das Material samt Index und Designsystem (z. B.
„norwegen-2026"). Ein *Export* ist ein konkretes Produkt daraus (z. B. „teaser-90s",
„hauptfilm"). **Ein Projekt hat beliebig viele Exporte** — derselbe Fundus, verschiedene Filme.

**Das Rohmaterial liegt außerhalb des Repos.** Im Projekt steht nur ein Pfad darauf
(`media_root` in `project.yaml`). Das Repo bleibt klein; Proxies/Renders landen im Cache
(`~/.cache/frameforge/`) bzw. in gitignorierten Export-Unterordnern.

**Der Prozess ist eine erzwungene Reihenfolge** (State-Machine). Man kann keinen Schritt
überspringen — jedes Kommando prüft, ob der vorige erreicht ist:

```
INIT → INGESTED → INDEXED → DESIGNED → BRIEFED → STORYBOARDED
     → TIMELINE → ASSETS_BUILT → PREVIEWED → APPROVED → RENDERED
```

`INIT`–`DESIGNED` gelten fürs ganze **Projekt**; ab `BRIEFED` läuft die Phase **pro Export**.

**Zwei Bedienwege:**
- **In Claude Code über `/ff-*`-Slash-Commands** — der empfohlene Weg. Die kreativen Schritte
  (Material *beschreiben*, Designsystem, Briefing, Story→Timeline) brauchen Claude/die
  Sub-Agenten. Claude ruft dabei intern die CLI auf.
- **Direkt über die `frameforge`-CLI** — für die deterministischen Schritte (ingest, preview,
  render, nle) und zum Nachvollziehen. **Nie** `ffmpeg` von Hand aufrufen — das ist per Hook
  blockiert und würde die Reproduzierbarkeit brechen.

---

## 2. Einmalige Einrichtung

Voraussetzungen: **Python 3.12**, [uv](https://github.com/astral-sh/uv), und die Systemtools
per Homebrew:

```bash
brew install ffmpeg exiftool cairo
```

Dann im Repo:

```bash
uv sync --extra dev                       # installiert exakt aus uv.lock (reproduzierbar)
.venv/bin/python -m frameforge doctor     # muss GRÜN sein, bevor irgendwas läuft
```

`doctor` prüft ffmpeg, ffprobe, exiftool, libcairo, Python-Version und Cache-Schreibrechte.
Läuft er nicht grün, siehe **Abschnitt 8 (Troubleshooting)**.

> Gesichtserkennung (optional, `frameforge faces`) zieht `dlib` — das kompiliert einmalig
> einige Minuten aus C++. Für die Kern-Pipeline nicht nötig.

---

## 3. Schritt für Schritt: von null zum fertigen Film

> **Der einfachste Weg: `/ff-wizard`.** In Claude Code startest du
> `/ff-wizard [projekt-name]` und wirst geführt — der Wizard zeigt die Pipeline-Karte, sagt dir
> den nächsten Schritt, fragt genau das ab, was er braucht, und führt ihn aus. **Jederzeit
> abbrechbar**, der Stand bleibt erhalten (`.state.json`); beim nächsten `/ff-wizard` geht es
> dort weiter. Die folgenden manuellen Schritte sind das, was der Wizard unter der Haube macht —
> nützlich zum Verstehen und für gezielte Einzelaktionen.
>
> Jederzeit `frameforge status <projekt>` (oder `/ff-status <projekt>`) zeigt die Pipeline als
> Karte: `✓` erledigt · `→` jetzt dran · ` ` offen, plus den nächsten Befehl.

Beispiel-Projekt „norwegen-2026", Beispiel-Export „teaser-90s". In Claude Code tippst du die
`/ff-*`-Befehle; die zugehörige CLI steht jeweils darunter.

### Schritt 0 — Material bereitlegen

Lege dein Rohmaterial in einen **externen** Ordner (nicht ins Repo), z. B.:

```
/Volumes/Media/norwegen-2026/
├── video/day01/DJI_0001.MP4
├── video/day02/...
└── fotos/...
```

Unterordner sind erlaubt und erwünscht (der Ingest scannt rekursiv). Gleiche Dateinamen in
verschiedenen Ordnern sind kein Problem — Proxies werden kollisionsfrei benannt.

### Schritt 1 — Projekt anlegen

```
/ff-new norwegen-2026 /Volumes/Media/norwegen-2026
```
```bash
frameforge new norwegen-2026 --media-root /Volumes/Media/norwegen-2026 \
    --timezone Europe/Oslo --language de
```

Das legt `projects/norwegen-2026/` mit der Ordnerstruktur und `project.yaml` an (Phase `INIT`).
`media_root` muss zum Zeitpunkt `new` noch nicht existieren — erst beim Ingest.

**Jetzt, vor dem Ingest, die projektweiten Zutaten an ihren Platz legen:**

| Was | Wohin | Nötig? |
|---|---|---|
| **Musik** (lizenzierte Tracks) | `projects/norwegen-2026/music/*.wav` | für Audio |
| **GPX-Route** (Roadtrip-Track) | `projects/norwegen-2026/route/roadtrip.gpx` | für Karten |
| **Orte/POIs** (manuelle Korrekturen) | `projects/norwegen-2026/route/locations.csv` | optional |
| **Design-Assets** (Logo, Freisteller, Marker-Icon) | `projects/norwegen-2026/design/assets/` | optional |
| **Schriften** | `projects/norwegen-2026/design/fonts/` | optional |

### Schritt 2 — Ingest (Scan + Proxies)

```
/ff-ingest norwegen-2026
```
```bash
frameforge ingest norwegen-2026
```

Scannt `media_root` rekursiv, erzeugt 1080p-Proxies (schnelles Preset) im Cache. Idempotent
und fehlertolerant: erneut ausführbar, überspringt vorhandene Proxies, meldet einzelne kaputte
Dateien statt abzubrechen. → Phase `INGESTED`.

### Schritt 3 — Index (Analyse + Beschreibung)

```
/ff-index norwegen-2026
```

Hier arbeitet der **`media-indexer`-Agent**: CV-Metriken (Schärfe, Stabilität, Belichtung,
Szenen) laufen per Code, dann sieht Claude die Keyframes an und schreibt pro Asset eine
Beschreibung, Tags und ein Rating nach `index/assets.json` + eine `.md`-Datei. Jedes Asset
wird **genau einmal** analysiert (Hash-Cache). → Phase `INDEXED`, sobald alle Assets erfasst
sind.

Danach kannst du den Fundus abfragen:
```bash
frameforge query norwegen-2026 --tag fjord --min-rating 4
```

### Schritt 4 — Designsystem

```
/ff-design norwegen-2026
```

Der **`design-system`-Agent** führt durch Stimmung → Farbpalette → Typo → Motion und schreibt
`design/tokens.yaml` (Aufbau als Referenz: `templates/project/tokens.example.yaml`). → Phase
`DESIGNED`.

**Was Claude macht vs. was du machst:**
- **Farben/Schrift/Motion** (`tokens.yaml`) — macht Claude im Gespräch, **kein externes Tool**.
- **Text-Overlays** (Titel, Bauchbinde, Kapitelkarte, Credits) — entstehen **automatisch** aus
  `tokens.yaml` + den SVG-Vorlagen (`templates/svg/`). Gestaltest du nicht selbst.
- **Echte Grafiken** (Logo, Marker-Icon, Freisteller) — das Einzige „extern" und **optional**:
  der Agent schreibt fertige Prompts nach `design/prompts.md` (Vorlage:
  `templates/prompts/graphics.md`, Konvention PNG mit Alpha). Du erzeugst die Bilder in einem
  Bildgenerator und legst sie **unter den Namen aus `prompts.md`** in `design/assets/`.
  Ohne eigene Grafiken läuft das Projekt trotzdem durch.
- **Eigene Schriftdatei** (statt System-Schrift): `.ttf` nach `design/fonts/`.

**Pausieren & Wiedereinstieg:** Der Ablauf *wartet nicht* im Hintergrund — er pausiert und der
Stand bleibt in `.state.json`. Du legst die Grafiken ab, wann immer du willst, und sagst dann
„weiter" (oder startest `/ff-wizard` neu). `frameforge design-status norwegen-2026` zeigt
jederzeit, was schon da ist und was fehlt:

```
tokens.yaml: ✓ vorhanden
Design-Grafiken (design/assets/)
  logo.png         ✓ abgelegt
  marker-icon.png  ✗ fehlt noch
```

`tokens.yaml` speist alle SVG-Overlays — **ein** Designsystem für alle Exporte des Projekts,
damit Teaser und Hauptfilm wie eine Familie wirken.

### Schritt 5 — Export briefen

```
/ff-brief norwegen-2026 teaser-90s
```

Der **`/ff-brief`-Wizard** fragt Stil-Preset, Ziellänge, Muss-/verbotene Shots ab und schreibt
`exports/teaser-90s/brief.yaml`. Der Brief ist das, was den einen Export vom anderen
unterscheidet. → Export-Phase `BRIEFED`. (Aufbau siehe **Abschnitt 5**.)

### Schritt 6 — Story → Timeline

```
/ff-build norwegen-2026 teaser-90s
```

`story-architect` (Opus) baut aus Brief + Index ein Beat-Sheet (`beatsheet.md`),
`timeline-builder` übersetzt es in `exports/teaser-90s/timeline.json` — die **Single Source of
Truth** für Render und NLE-Export. Bei Bedarf ziehen `audio-designer` (Musik/Ducking) und
`map-animator` (Karten-Clips aus der GPX) zu. → Export-Phase `TIMELINE`.

### Schritt 7 — Preview ansehen

```
/ff-preview norwegen-2026 teaser-90s
```
```bash
frameforge preview norwegen-2026 teaser-90s
```

QC prüft die Timeline (Lücken, Clipping-Risiko, Textlesbarkeit, verbotene/fehlende Shots,
Asset-Existenz). Besteht sie, rendert ein 1080p-Proxy-Preview nach
`exports/teaser-90s/preview/`. **Ansehen.** → Export-Phase `PREVIEWED`.

### Schritt 8 — Freigeben

```bash
frameforge approve norwegen-2026 teaser-90s
```

Bewusste manuelle Freigabe (interaktive Rückfrage). Sie wird an den **exakten Timeline-Stand**
gebunden: änderst du `timeline.json` danach noch, verweigert der Final-Render und verlangt ein
erneutes Preview + Approve. → Export-Phase `APPROVED`.

### Schritt 9 — Final-Render (4K)

```
/ff-render norwegen-2026 teaser-90s
```
```bash
frameforge render norwegen-2026 teaser-90s
# optional mit Farbkorrektur-LUT (z. B. Log-Material):
frameforge render norwegen-2026 teaser-90s --lut /pfad/zu/log-to-rec709.cube
```

Mappt auf die 4K-Originale (kein Proxy), EBU-R128-Loudness-Normalisierung, versionierte
Ausgabe (`teaser-90s_v1.mp4`, `_v2` …, nie überschrieben) nach `exports/teaser-90s/final/`.
→ Export-Phase `RENDERED`.

### Schritt 10 — Export für DaVinci Resolve / Final Cut (optional)

```bash
frameforge nle norwegen-2026 teaser-90s --format fcpxml   # oder: otio
```

Schreibt dieselbe Timeline als FCPXML/OTIO nach `exports/teaser-90s/nle/`, damit du in einem
NLE weiterschneiden kannst.

### Jederzeit — Status & nächster Schritt

```bash
frameforge status norwegen-2026     # visuelle Pipeline-Karte + nächster Befehl
frameforge list                     # alle Projekte
```

Beispiel-Ausgabe:

```
Pipeline  norwegen-2026

  [✓] ingest
  [✓] index
  [→] design

Naechster Schritt: design: /ff-design norwegen-2026
```

Sobald Exporte existieren, zeigt die Karte pro Export eine eigene Spur
(brief → build → preview → approve → render) mit eigener „du bist hier"-Markierung.
`/ff-wizard norwegen-2026` übernimmt von hier die Führung durch den nächsten Schritt.

### Optional — Personen erkennen & benennen („mehr Oskar")

Opt-in (nicht Teil von `index`, weil biometrische Daten). Nur mit Einverständnis der
abgebildeten Personen nutzen. Ergebnis (`index/people*.json`) ist gitignored.

```bash
frameforge faces norwegen-2026            # erkennt Gesichter, bildet Cluster + Ausschnitte
frameforge people norwegen-2026           # zeigt die Cluster (person_1, person_2 …)
frameforge name-person norwegen-2026 person_1 Oskar   # Cluster benennen
frameforge query norwegen-2026 --person Oskar         # Assets mit Oskar
```

`faces` bildet aus den Gesichtern **Cluster** und legt pro Cluster einen Gesichts-Ausschnitt
in den Cache. Über `/ff-wizard` zeigt Claude dir die Ausschnitte und fragt „wer ist das?" —
deine Antwort wird als Name **projektweit** gemerkt. Danach steuerst du Exporte über Namen:
im Brief „mehr Oskar" / „keine Personen", und `frameforge query --person <name>` löst den
Namen zu den passenden Assets auf. `frameforge stats` zeigt zusätzlich, **wie viele Sekunden**
jede benannte Person im Fundus hat.

---

## 3a. Weitere Exporte aus derselben Basis (Quereinstieg)

Der wichtigste Punkt fürs Wiederverwenden: **Material, Index und Designsystem machst du nur
einmal — sie gehören dem Projekt.** Ein *Export* ist nur „welcher Film aus diesem Fundus". Ein
neuer Film (Trailer, 15-Minuten-Fassung, Landschaften-Version, Einzelszenen zum Verkauf …)
bedeutet **keinen** neuen Durchlauf, sondern nur einen neuen Export ab `brief`:

```bash
frameforge brief   norwegen-2026 landschaften-4k    # neuer Export, Projekt ist schon DESIGNED
frameforge build   norwegen-2026 landschaften-4k
frameforge preview norwegen-2026 landschaften-4k
frameforge approve norwegen-2026 landschaften-4k
frameforge render  norwegen-2026 landschaften-4k
```

Kein Re-Ingest, kein Re-Index, kein Re-Design. `frameforge status` zeigt für ein fertiges
Projekt aktiv den Hinweis „Optional: weiteren Export anlegen"; `/ff-wizard norwegen-2026` bietet
es geführt an. Jeder Export bekommt eine eigene Spur in der Status-Karte.

Solche Varianten sind einfach ein anderer Brief; `story-architect`/`timeline-builder` filtern
den Fundus via `frameforge query`:

- **„Nur Drohnen-Shots"** → `frameforge query norwegen-2026 --source drone` (Quellen:
  `drone` / `phone` / `camera` / `action_cam`). Die Quelle setzt der `media-indexer` beim
  Indizieren automatisch (aus EXIF/Kamera-Angaben; DJI → drone, iPhone → phone, GoPro →
  action_cam …).
- **„Nur Landschaften, keine Personen"** → verbotene Shots über die Personen-Cluster
  (`frameforge faces`) oder über Tags/`content.people`.
- Kombinierbar mit `--tag`, `--place`, `--min-rating`, `--person`.

## 3b. Audio & Musik — wo, was, wann

Die Audio-Entscheidungen fallen im **`build`-Schritt** (der `audio-designer` wählt Tracks, setzt
Ducking, der `timeline-builder` schreibt die Audio-Spur in `timeline.json`). Also **vor dem
Build** klären:

| Audio-Quelle | Wo / wie |
|---|---|
| **Eigene Musik** (lizenziert) | Datei nach `projects/<projekt>/music/*.wav` legen. Projektweit — alle Exporte können daraus wählen. |
| **KI-Musik** (kein Track zur Hand) | Der `audio-designer` schreibt einen Prompt (Vorlage `templates/prompts/music.md`: instrumental, Länge, Energieverlauf). Du erzeugst den Track extern (z. B. Suno/Udio), lädst ihn herunter, legst ihn nach `music/` — der Ablauf pausiert und macht danach weiter (wie bei den Design-Tokens). |
| **O-Ton** (Ton aus den Clips) | Kommt automatisch, wo der Brief es vorsieht; die Musik wird an diesen Stellen automatisch abgesenkt (**Ducking**). |

Ein neuer Export mit **anderem Sound** braucht also nur andere Tracks in `music/` (oder eine
andere Auswahl/Energie im Brief). BPM/Beats/Energiekurve jedes Tracks werden einmalig analysiert
und in `music/analysis/` gecacht, damit die Musik auf den Schnitt gelegt werden kann.

## 3c. Statistik & Report — Überblick über den Fundus und jeden Export

**Index-Statistik** (was liegt im Projekt, wie wurde es analysiert, wie viel wird genutzt):

```bash
frameforge stats norwegen-2026
```

Zeigt: Anzahl Assets (Video/Foto), wie viele der Dateien im Quellordner schon indiziert sind,
Rohmaterial-Gesamtdauer, durchschnittliche Qualität (Schärfe/Stabilität/Belichtung),
Rating-Verteilung, Auflösungen, Codecs, Orte, und **pro Export, wie viele Assets genutzt
werden** (plus „gesamt genutzt" über alle Exporte).

**Export-Datenblatt** (ein Markdown-Report, der beschreibt, was in diesem Film passiert ist):

```bash
frameforge report norwegen-2026 teaser-90s      # schreibt exports/teaser-90s/report.md
```

Beim **Final-Render entsteht der Report automatisch** neben dem MP4 (`teaser-90s_v1.report.md`).
Er enthält: Projekt & Quellordner, Umfang, **welche Clips genutzt wurden** (mit In/Out und
Beschreibung) und wie viel Prozent des Fundus, Dramaturgie (Preset, Länge, Beat-Sheet), Audio
(Tracks, O-Ton, Ducking), Design (Schrift, Farben), und Technik (Auflösung, Spuren,
Fundus-Qualität). Ein „was-wurde-hier-gemacht"-Bericht zum Nachschlagen und Weitergeben.

---

## 4. Verzeichnis-Referenz eines Projekts

```
projects/norwegen-2026/
├── project.yaml          # Config (Name, media_root, Zeitzone, Sprache)  ← du/ff-new
├── .state.json           # Prozess-Stand — NICHT von Hand ändern
├── design/
│   ├── tokens.yaml       # Design-Tokens (Farbe/Typo/Motion)             ← ff-design
│   ├── prompts.md        # Prompts für fehlende Grafiken                 ← ff-design
│   ├── assets/           # Logo, Freisteller, Marker-Icon                ← du
│   └── fonts/            # Schriftdateien                                ← du
├── index/
│   ├── assets.json       # ein Eintrag pro Asset (maschinenlesbar)       ← ff-index
│   └── assets/*.md       # menschenlesbare Beschreibung je Asset         ← ff-index
├── route/
│   ├── roadtrip.gpx      # GPS-Track                                     ← du
│   └── locations.csv     # Übernachtungen/POIs (optional)                ← du
├── music/                # deine Tracks (gitignored) + analysis/ (Cache) ← du
└── exports/
    └── teaser-90s/
        ├── brief.yaml    # Stil, Ziellänge, Muss-/verbotene Shots        ← ff-brief
        ├── beatsheet.md  # Dramaturgie                                   ← ff-build
        ├── timeline.json # die Schnittliste (Single Source of Truth)     ← ff-build
        ├── overlays/     # gerenderte PNGs (gitignored)
        ├── map/          # gerenderte Karten-Clips (gitignored)
        ├── preview/      # 1080p-Proxy-Render (gitignored)               ← ff-preview
        ├── final/        # 4K-Export, versioniert (gitignored)           ← ff-render
        └── nle/          # export.fcpxml / .otio (gitignored)            ← frameforge nle
```

Getrackt werden nur Config und Index; alles Schwere (Medien, Proxies, Renders, Musik, Fonts,
biometrische Daten) bleibt per `.gitignore` draußen.

---

## 5. `brief.yaml` — so beschreibst du einen Export

Der Brief macht aus demselben Material verschiedene Filme. Aufbau (Presets siehe
`docs/styles/style-catalog.md`):

```yaml
preset: nordic-cinematic     # nordic-cinematic | punch-teaser | chronikel |
                             # thematisch-assoziativ | diary-handheld | timelapse-journey
target_duration_s: 90        # Ziellänge in Sekunden (harte Grenze, keine Empfehlung)
language: de                 # Sprache für Text/Overlays (überschreibt project.yaml)
must_shots: []               # Asset-IDs, die vorkommen MÜSSEN (z. B. 20260714-drone-fjord-001)
forbidden_shots: []          # Asset-IDs, die NICHT vorkommen dürfen
```

Die sechs Presets im Überblick (Details + überschreibbare Parameter im Stil-Katalog):

| Preset | Charakter | Passt zu |
|---|---|---|
| **nordic-cinematic** | langsam, weite Establisher, sparsamer Text | 15-Minuten-Reisefilm |
| **punch-teaser** | harte Cuts auf den Beat, große Typo | 60–90 s Trailer |
| **chronikel** | strikt chronologisch, Tages-Kapitelkarten | Familien-„was-haben-wir-gemacht" |
| **thematisch-assoziativ** | nach Motiv gruppiert, Match-Cuts | Zweitfassung mit anderem Blick |
| **diary-handheld** | roh, O-Ton dominant, Musik nur Bett | persönlich/intim |
| **timelapse-journey** | bewegungslastig, Karte als Leitmotiv | Roadtrip-Fokus |

> Ein Preset ist Ausgangspunkt, keine Zwangsjacke — der `story-architect` weicht begründet ab,
> wenn Brief/Material es verlangen.

---

## 6. `project.yaml` und `tokens.yaml` — Referenz

`project.yaml` (von `ff-new` erzeugt, selten von Hand nötig):

```yaml
name: norwegen-2026
media_root: /Volumes/Media/norwegen-2026    # EXTERN, absolut
timezone: Europe/Oslo
language: de
```

`design/tokens.yaml` (von `ff-design` erzeugt) — speist alle SVG-Overlays:

```yaml
primary_color: '#12222f'
accent_color: '#e0a458'
text_color: '#ffffff'
font_display: Helvetica          # Display-/Titelschrift
font_text: Helvetica             # Fließtextschrift
```

---

## 7. Der erzwungene Prozess (Gates)

Jeder Schritt prüft seine Vorbedingung doppelt: in der CLI (Gürtel) und im
`PreToolUse`-Hook (Hosenträger).

| Aktion | Vorbedingung |
|---|---|
| `index` | Projekt-Phase ≥ INGESTED |
| `design` | Projekt-Phase ≥ INDEXED |
| `brief` | Projekt-Phase ≥ DESIGNED |
| `build` | Export-Phase ≥ BRIEFED |
| `preview` | `timeline.json` existiert **und** besteht QC |
| `approve` | Export-Phase == PREVIEWED (interaktive Freigabe) |
| `render` (final) | Export-Phase == APPROVED **und** Timeline seit Freigabe unverändert |
| nackter `ffmpeg`/`ffprobe`-Aufruf | **immer blockiert** |

---

## 8. Troubleshooting

- **`doctor` meldet `libcairo` FEHLT:** `brew install cairo`. Auf Apple Silicon löst
  FrameForge den Ladepfad selbst (siehe `frameforge/design.py`), ein `brew install` genügt.
- **`import frameforge` schlägt fehl nach venv-Neuaufbau:** `uv sync --extra dev` (oder
  `uv pip install -e ".[dev]"`) — das Package muss editable installiert sein.
- **Ein Kommando blockt mit „Phase … erforderlich":** Das ist gewollt — führe den genannten
  vorigen Schritt aus. `frameforge status <projekt>` zeigt, wo du stehst.
- **„timeline.json wurde seit der Freigabe geändert":** Nach einer Timeline-Änderung erneut
  `preview` und `approve`, dann `render`.

---

## 8a. Kommando-Referenz (Auswahl)

**Stil & Look:**
- `frameforge presets` — 12 Stil-Presets (Slug, Beispiel, Bogen); im `brief.yaml` per `preset: <slug>`.
- `frameforge preset-new <slug>` — eigenes Preset gerüstet (`~/.frameforge/presets/`), dann bearbeiten.
  Alternativ Parameter direkt ins `brief.yaml` schreiben (ohne `preset:`).
- `frameforge themes` / `frameforge apply-theme <projekt> <slug>` — 9 Design-Token-Themes anzeigen
  bzw. als Startpunkt nach `design/tokens.yaml` schreiben.
- `frameforge theme-new <slug>` — eigenes Design-Theme gerüstet, dann bearbeiten.
- `frameforge design-status <projekt>` — tokens.yaml + Grafik-Inventar (was fehlt noch).

**Auswahl aus dem Fundus:**
- `frameforge query <projekt> [--source drone] [--person Oskar] [--tag …] [--place …] [--min-rating N] [--kind video]`
- `frameforge people <projekt>` / `frameforge name-person <projekt> <cluster> <name>` — Personen benennen.

**Überblick:**
- `frameforge stats <projekt>` — Fundus-Statistik (Umfang, Qualität, Zusammensetzung, Nutzung).
- `frameforge days <projekt>` — Tageszusammenfassungen nach `index/days/`.
- `frameforge report <projekt> <export>` — Export-Datenblatt (auch automatisch beim Render).

**Render-Optionen (final):**
- `frameforge render <projekt> <export> [--resolution 1920x1080] [--crf 18] [--preset medium] [--lut datei.cube]`
  — Übergänge (Crossfade), Ken-Burns und der Color-Grade aus dem Preset werden automatisch
  gerendert; `--lut` legt eine eigene Farbkorrektur obendrauf.

**Betrieb:**
- `frameforge ingest <projekt> --dry-run` — vorab zeigen, was gefunden würde (Anzahl/Größe).
- `frameforge clean <projekt>` — Cache (Proxies/Keyframes) löschen, alles regenerierbar.
- `frameforge clone-export <projekt> <src> <dst>` — neuen Export aus einem bestehenden Brief.

---

## 9. Entwicklung

```bash
.venv/bin/python -m pytest tests/ -q          # Tests
.venv/bin/ruff check frameforge/ tests/       # Lint
```

Struktur: `frameforge/` (Werkzeugschicht), `.claude/agents/` + `.claude/commands/` +
`.claude/hooks/` (Orchestrierung für Claude Code), `docs/` (Plan, Fortschritt, Prozess,
Stil-Katalog), `templates/` (Projekt-Skeleton, SVG-Overlays, Prompt-Vorlagen).
