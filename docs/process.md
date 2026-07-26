# Der Prozess

Referenz für Menschen. Die technische Quelle der Wahrheit ist `frameforge/state.py`
(Phasen, Gates) und `.claude/hooks/gate.py` (Durchsetzung). Der Plan mit allen
Datenmodellen und Begründungen steht in `docs/plans/0001-initial-structure.md`.

## Ablauf

```
INIT → INGESTED → INDEXED → DESIGNED → BRIEFED → STORYBOARDED
     → TIMELINE → ASSETS_BUILT → PREVIEWED → APPROVED → RENDERED
```

`INIT` bis `DESIGNED` sind **Projekt-Phasen** — sie gelten für das ganze Projekt (Material,
Index, Designsystem). Ab `BRIEFED` ist die Phase pro **Export** getrennt: ein Projekt kann
gleichzeitig einen Teaser in `TIMELINE` und einen Hauptfilm in `PREVIEWED` haben.

| Phase | Ausgelöst durch | Bedeutet |
|---|---|---|
| `INIT` | `/ff-new` | Projekt angelegt, noch kein Material gesichtet |
| `INGESTED` | `/ff-ingest` | Material gescannt, Proxies erzeugt |
| `INDEXED` | `/ff-index` | Jedes Asset hat Metadaten, CV-Analyse, Beschreibung |
| `DESIGNED` | `/ff-design` | Designsystem (Tokens, SVG-Templates) steht |
| `BRIEFED` | `/ff-brief` | Export hat Stil, Ziellänge, Muss-/verbotene Shots |
| `STORYBOARDED` | `story-architect` | Beat-Sheet steht |
| `TIMELINE` | `timeline-builder` / `/ff-build` | `timeline.json` ist gültig |
| `ASSETS_BUILT` | `render-engineer` | Overlays, Karten-Clips, Audio-Kurven fertig gerendert |
| `PREVIEWED` | `/ff-preview` | 1080p-Proxy-Render existiert und wurde angesehen |
| `APPROVED` | manuelle Freigabe (`frameforge approve`) | Nutzer hat den Preview explizit freigegeben |
| `RENDERED` | `/ff-render` | 4K-Final-Export existiert |

## Gates

Jeder Schritt prüft sein eigenes Gate zweifach — einmal in `cli.py` (Gürtel), einmal im
`PreToolUse`-Hook `gate.py` (Hosenträger), falls der Orchestrator versucht, den Schritt
oder `ffmpeg` direkt in Bash aufzurufen statt über die CLI.

| Aktion | Vorbedingung |
|---|---|
| `ff-index` | Projekt-Phase ≥ `INGESTED` |
| `ff-brief` | Projekt-Phase ≥ `DESIGNED` |
| `ff-build` | Export-Phase ≥ `BRIEFED` |
| `ff-preview` | `timeline.json` existiert und `qc.validate()` liefert keine Probleme |
| `ff-render` (final) | Export-Phase = `APPROVED` (jedes Mal neu, auch nach `RENDERED`) |
| jeder nackte `ffmpeg`/`ffprobe`-Aufruf | immer blockiert |

## Invalidierung

- `brief.yaml` eines Exports ändert sich → Export fällt zurück auf `BRIEFED`. Beat-Sheet und
  `timeline.json` sind damit veraltet und werden neu gebaut.
- Neues Rohmaterial kommt dazu → Projekt fällt zurück auf `INGESTED`. Der Analyse-Cache
  (`assets.json`) bleibt erhalten — `ff-index` verarbeitet nur die neuen Hashes.

## Rollen

Der **Orchestrator** (die Haupt-Session) implementiert nichts selbst, ruft kein `ffmpeg` auf
und delegiert an Sub-Agenten (`.claude/agents/`). Slash-Commands (`.claude/commands/`) sind
die Einstiegspunkte pro Schritt — sie rufen die `frameforge`-CLI auf und delegieren bei
Bedarf weiter.

| Agent | Modell | Rolle |
|---|---|---|
| `media-indexer` | Sonnet | Keyframes → Beschreibung, Tags, Rating |
| `story-architect` | Opus | Brief + Index → Beat-Sheet |
| `timeline-builder` | Sonnet | Beat-Sheet → `timeline.json` |
| `design-system` | Sonnet | Tokens, SVG-Templates, Grafik-Prompts |
| `audio-designer` | Sonnet | Track-Wahl, Beat-Mapping, Ducking |
| `map-animator` | Sonnet | GPX → Karten-Clips |
| `render-engineer` | Sonnet | FFmpeg-Graphen, Encoding, Fehlerdiagnose |
| `qc-reviewer` | Opus | Timeline gegen Brief prüfen, blockiert bei Problemen |

Opus gezielt für Dramaturgie (`story-architect`) und Qualitätssicherung (`qc-reviewer`) —
die Stellen mit den meisten Abhängigkeiten und dem größten Schaden bei einem Fehlurteil.
Alles andere läuft mit Sonnet.
