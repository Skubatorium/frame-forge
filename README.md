# FrameForge

Orchestrierte, reproduzierbare Videoschnitt-Pipeline. Claude Code arbeitet hier als
**Orchestrator und Entwickler, nicht als Editor** — die eigentliche Verarbeitung übernehmen
Python, FFmpeg und lokale CV-/Audio-Bibliotheken. Ein Prozess mit harten Gates und einem
hash-gecachten Analyse-Index sorgt dafür, dass kein Schnittversuch das Material neu
analysiert und kein Render an `timeline.json` vorbei entsteht.

Ausführlicher Kontext, Datenmodelle und Begründungen: `docs/plans/0001-initial-structure.md`.
Arbeitsstand: `docs/plans/PROGRESS.md`. Prozess als Referenz für Menschen: `docs/process.md`.

## Voraussetzungen

- Python 3.12
- [uv](https://github.com/astral-sh/uv)
- Homebrew-Tools: `brew install ffmpeg exiftool cairo`

## Setup

```bash
uv sync --extra dev    # reproduzierbar aus uv.lock
.venv/bin/python -m frameforge doctor
```

`uv sync` installiert exakt die in `uv.lock` festgehaltenen Versionen (reproduzierbare
Umgebung). `doctor` muss grün sein, bevor irgendein Pipeline-Schritt läuft.

`face_recognition`/`dlib` werden aus C++ kompiliert (einmalig einige Minuten). Nach einem
Neuaufbau von `.venv` das Package editable installieren, damit `import frameforge` von überall
funktioniert: `uv pip install -e ".[dev]"` bzw. `uv sync` verwendet es bereits als lokales Paket.

## Nutzung

Alle Schritte laufen über die `frameforge`-CLI bzw. die passenden `/ff-*`-Slash-Commands in
Claude Code — nie über direkte `ffmpeg`-Aufrufe (das ist per Hook blockiert):

```bash
frameforge new <projekt> --media-root /pfad/zu/rohmaterial
frameforge ingest <projekt>
frameforge index <projekt>
frameforge design <projekt>
frameforge brief <projekt> <export>
frameforge build <projekt> <export>
frameforge preview <projekt> <export>
frameforge approve <projekt> <export>
frameforge render <projekt> <export>
frameforge status <projekt>
```

Der Prozess erzwingt eine feste Reihenfolge (State-Machine, siehe `docs/process.md`):

```
INIT → INGESTED → INDEXED → DESIGNED → BRIEFED → STORYBOARDED
     → TIMELINE → ASSETS_BUILT → PREVIEWED → APPROVED → RENDERED
```

## Entwicklung

```bash
.venv/bin/python -m pytest tests/ -v
.venv/bin/ruff check frameforge/ tests/
```

## Struktur

- `frameforge/` — Python-Package, die Werkzeugschicht
- `projects/<name>/` — pro Videoprojekt: Config, Index, Designsystem, Exporte (Rohmedien
  liegen extern, Pfad in `project.yaml`)
- `.claude/agents/`, `.claude/commands/`, `.claude/hooks/` — Sub-Agenten, Slash-Commands,
  Gate-Hook für Claude Code
- `docs/` — Plan, Fortschritt, Prozess, Stil-Katalog
- `templates/` — Projekt-Skeleton, SVG-Templates, Prompt-Vorlagen
