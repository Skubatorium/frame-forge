# Handover — Stand M0 (Teil 1 von 7 erledigt)

Erstellt am 2026-07-26. Übergabe von der Desktop-Session an eine Terminal-Session.

## Was fertig ist

**Task 1 — Repo-Fundament: erledigt.**

- `git init` gelaufen (noch **kein** Commit — Working Tree ist unversioniert)
- `.gitignore` — trackt Projekt-Configs und Index, ignoriert Medien/Proxies/Renders/Musik/Fonts
- `pyproject.toml` — Package `frameforge`, Python ≥ 3.12, Entrypoint `frameforge = frameforge.cli:app`
- `.python-version` → 3.12
- `.venv/` mit CPython 3.12.13 (via `uv venv`)
- Alle Dependencies installiert (`uv pip install -e ".[dev]"`) und importierbar
- Ordnerstruktur laut Plan angelegt
- Systemtools: **ffmpeg 8.1.2**, **ffprobe**, **exiftool**, **cairo 1.18.4** via Homebrew installiert
- Plan liegt als `docs/plans/0001-initial-structure.md` im Repo

## Zwei gelöste Fallstricke — nicht erneut hineinlaufen

**1. `librosa` → `numba`.** Ohne expliziten Pin löst uv auf `numba 0.53.1` auf, das Python 3.12 nicht baut (`RuntimeError: Cannot install on Python version 3.12.13`). In `pyproject.toml` steht deshalb `numba>=0.61` als direkte Dependency. Nicht entfernen.

**2. `cairosvg` findet libcairo nicht.** `brew install cairo` reicht auf Apple Silicon nicht — `ctypes.util.find_library()` durchsucht `/opt/homebrew/lib` nicht, und `DYLD_*`-Umgebungsvariablen werden von SIP beim Prozessstart entfernt.

Verifiziert funktionierend:
```bash
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib .venv/bin/python -c "import cairosvg"
```

**Update Task 3 (2026-07-27): dieser Ansatz ist widerlegt, nicht mehr verwenden.** CDLL-Preload
per absolutem Pfad dedupliziert auf macOS nicht gegen einen späteren `dlopen` per nacktem Namen.
Der tatsächlich funktionierende Fix (Monkeypatch von `ctypes.util.find_library` vor dem ersten
`import cairosvg`) steht in `frameforge/design.py::preload_cairo()` und ist in
`docs/plans/PROGRESS.md` unter Task 3 begründet. Codeblock unten nur noch zur Historie.

**Ursprünglich geplante (verworfene) Lösung:**

```python
import ctypes.util, ctypes, glob

def _preload_cairo() -> None:
    if ctypes.util.find_library("cairo"):
        return
    for pattern in ("/opt/homebrew/lib/libcairo.2.dylib", "/usr/local/lib/libcairo.2.dylib"):
        for path in glob.glob(pattern):
            ctypes.CDLL(path, mode=ctypes.RTLD_GLOBAL)
            return
```

Der `doctor`-Befehl soll diesen Fall prüfen und bei Fehlschlag `brew install cairo` vorschlagen.

## Was noch offen ist

`frameforge/`, `.claude/agents/`, `.claude/commands/`, `.claude/hooks/`, `templates/`, `tests/` sind **leere Ordner**. Es existiert noch keine Zeile Anwendungscode.

Offene Tasks in Plan-Reihenfolge:

2. **Kern-Module** — `state.py` (State-Machine + Gates), `project.py` (Pfadauflösung), `timeline.py` (Pydantic-Schema). Alles andere hängt daran, deshalb zuerst.
3. **CLI + Modul-Stubs** — `cli.py` mit `doctor`/`status`/`new`/`ingest`/`index`/`query`/`build`/`preview`/`render`; übrige Module als Stubs mit Signaturen.
4. **Gate-Hook** — `.claude/hooks/gate.py` als `PreToolUse` auf `Bash`, verdrahtet in `.claude/settings.json`.
5. **Agenten + Slash-Commands** — 8 Agenten, 9 Commands.
6. **Docs** — `CLAUDE.md`, `docs/process.md`, `docs/styles/style-catalog.md`, `README.md`, Projekt-Templates.
7. **Tests + M0-Abnahme** — State-Übergänge, Timeline-Schema, `doctor` grün, Gate blockiert verfrühten `render` nachweislich.

## So geht es im Terminal weiter

```bash
cd /Users/christianskubatz/Workspace/Repos/frame-forge && claude
```

Dann als erste Nachricht:

> Lies docs/plans/0001-initial-structure.md und docs/plans/HANDOVER.md. Task 1 ist fertig. Setze M0 ab Task 2 fort: Kern-Module state.py, project.py, timeline.py.

Der Plan enthält Datenmodelle (`assets.json`, `timeline.json`), die State-Machine, die Gate-Regeln, den Stil-Katalog und die Agenten-Tabelle — die Terminal-Session braucht keinen weiteren Kontext aus der Desktop-Session.

## Nach M0

Der Rest folgt dem Plan: M1 (Mini-Prototyp end-to-end mit 3–5 Clips → 60–90 s Video) ist die erste echte Bewährungsprobe. Vorher lohnt kein volles Norwegen-Material.
