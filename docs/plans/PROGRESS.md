# Fortschritt M0 — Gerüst

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
| 2 | Kern-Module: `state.py`, `project.py`, `timeline.py` | ⬜ offen | |
| 3 | CLI (`cli.py`) + restliche Modul-Stubs | ⬜ offen | |
| 4 | Gate-Hook `.claude/hooks/gate.py` + `settings.json` | ⬜ offen | |
| 5 | 8 Agenten + 9 Slash-Commands | ⬜ offen | |
| 6 | Docs: `CLAUDE.md`, `process.md`, `style-catalog.md`, `README.md`, Templates | ⬜ offen | |
| 7 | Tests + M0-Abnahme | ⬜ offen | |

Legende: ⬜ offen · 🔄 in Arbeit · ✅ fertig

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

<!-- Hier festhalten, was vom Plan abweicht und warum. -->
