# FrameForge

Orchestrierte, reproduzierbare Videoschnitt-Pipeline. Claude ist hier **Orchestrator und
Entwickler, nicht Editor** — die eigentliche Verarbeitung machen Python, FFmpeg und lokale
CV-/Audio-Bibliotheken.

## Zuerst lesen

Bei jedem Session-Start, in dieser Reihenfolge:

1. `docs/plans/PROGRESS.md` — **wo stehen wir?** Einzige verlässliche Quelle für den Arbeitsstand.
2. `docs/plans/0001-initial-structure.md` — der genehmigte Gesamtplan (Architektur, Datenmodelle,
   State-Machine, Gate-Regeln, Stil-Katalog, Agenten).
3. `docs/plans/HANDOVER.md` — Umgebungs-Fallstricke, die schon einmal Zeit gekostet haben.

Nicht raten, was als Nächstes dran ist. `PROGRESS.md` sagt es.

## Arbeitsregeln

**Ein Task, ein Commit.** Nach jedem abgeschlossenen Task aus `PROGRESS.md`:
1. Abnahmekriterium des Tasks prüfen (steht dort dabei) — Tests laufen lassen, nicht behaupten
2. Zeile in `PROGRESS.md` auf ✅ setzen, Commit-Hash eintragen
3. Committen

Das ist kein Zeremoniell: Sessions enden an Limits. Was nicht committet und in `PROGRESS.md`
vermerkt ist, ist verloren.

**Kein Task gilt als fertig, solange sein Abnahmekriterium nicht nachweislich erfüllt ist.**
Fehlschlagende Tests, halbe Implementierung, ungelöste Fehler → Task bleibt 🔄, und der Grund
kommt in den Notizen-Abschnitt von `PROGRESS.md`.

**Abweichungen vom Plan** gehören in den Notizen-Abschnitt von `PROGRESS.md`, mit Begründung.

## Prozess-Constraints

Der Prozess wird technisch erzwungen, nicht nur dokumentiert (Gate-Hook `.claude/hooks/gate.py`
ist aktiv, siehe `docs/plans/PROGRESS.md` Task 4):

```
INIT → INGESTED → INDEXED → DESIGNED → BRIEFED → STORYBOARDED
     → TIMELINE → ASSETS_BUILT → PREVIEWED → APPROVED → RENDERED
```

- Phasen dürfen **nicht** übersprungen werden. `.state.json` je Projekt hält den Stand.
- **Nackte `ffmpeg`-Aufrufe sind verboten.** Alles läuft über `frameforge.render`, damit
  jeder Render reproduzierbar aus `timeline.json` entsteht.
- `timeline.json` ist Single Source of Truth für Render **und** FCPXML/OTIO-Export. Kein
  zweites Schema, keine Sonderwege.
- Final-Render nur nach expliziter Freigabe (`APPROVED`) durch den Nutzer nach dem Preview.

## Token-Disziplin

Das Material umfasst ~100 GB. Ohne Disziplin verbrennt jeder Schnittversuch die Analyse neu.

1. **Analyse genau einmal pro Datei.** Schlüssel: `sha256(erste 1 MB + Größe + mtime)`.
   Existiert der Eintrag in `assets.json`, wird die Datei nie wieder an ein Modell geschickt.
2. **Vision nur auf Keyframes.** 3 Frames je Clip (10 %, 50 %, 85 %), 768 px lange Kante,
   JPEG q80. Fotos: 1 Frame. Bei Szenenwechseln je 1 Frame pro Szene, gedeckelt auf 6.
3. **Nie ganze Verzeichnisse lesen.** `python -m frameforge query …` mit Filtern liefert
   kompaktes JSON — nicht 400 Markdown-Dateien ins Kontextfenster.
4. **Assets werden über kurze IDs referenziert**, nicht über Pfade: `20260714-drone-fjord-001`.
5. **Previews laufen auf Proxies.** Final-Render mappt automatisch auf die 4K-Originale.
6. **Ergebnisse sind Dateien**, keine Chatverläufe: Beatsheet, Timeline, QC-Report.

## Umgebung

- Python 3.12 in `.venv/` (via `uv`). Immer `.venv/bin/python` oder aktivierte venv nutzen.
- Systemtools via Homebrew: ffmpeg, ffprobe, exiftool, cairo.
- `python -m frameforge doctor` prüft die Umgebung: ffmpeg, ffprobe, exiftool, libcairo,
  Python-Version, Cache-Schreibrechte. Muss grün sein, bevor irgendein Pipeline-Schritt läuft.
- Bekannte Fallstricke bei `numba` und `libcairo`: siehe `docs/plans/HANDOVER.md`.

## Struktur

- `frameforge/` — das Python-Package, die Werkzeugschicht
- `projects/<name>/` — pro Videoprojekt: Config, Index, Designsystem, Exporte.
  Rohmedien liegen **extern**, Pfad steht in `project.yaml`.
- `.claude/agents/` — die Sub-Agenten, an die der Orchestrator delegiert
- `.claude/commands/` — die `/ff-*`-Slash-Commands, ein Wrapper pro Pipeline-Schritt
- `.claude/hooks/gate.py` — erzwingt die State-Machine auch bei direkten Bash-Aufrufen
- `docs/` — Plan, Fortschritt, Prozess, Stil-Katalog

## Aktueller Stand der Werkzeugschicht

M0–M4 sind fertig — jedes Modul in `frameforge/` ist echt implementiert, keine
`NotImplementedError`-Stubs mehr im Package. Offen ist nur noch, was inhärent an einem echten
Projekt mit echtem Material hängt (M5 laut Plan, kein Code-Meilenstein) und die "Offenen
Punkte für später" aus Plan §11 (Gesichtserkennung, automatische Untertitel,
Musik-Lizenz-Nachweis). Genauer Stand inkl. aller Design-Entscheidungen: `docs/plans/PROGRESS.md`.
