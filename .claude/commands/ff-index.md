---
description: Material analysieren und .md-Beschreibungen erzeugen
argument-hint: <projekt-name>
---

Material für Projekt `$ARGUMENTS` indizieren. Erfordert Projekt-Phase `>= INGESTED`
(`gate_index` in `frameforge/state.py` — bei Verstoß meldet `frameforge index` bzw. der
Gate-Hook den fehlenden Schritt).

Schritte:
1. `frameforge index $ARGUMENTS` ausführen — prüft das Gate, zeigt offene Assets.
2. `frameforge prepare-index $ARGUMENTS [--filter <tag/ordner>] [--limit N]` — extrahiert
   Keyframes + CV-Analyse für noch nicht indizierte Assets (Probe auf Original, CV/Keyframes
   auf Proxy) und legt `prep/<hash>.json` im Cache ab. Bei viel Material etappenweise mit
   `--filter` (ein Reisetag) oder `--limit`. Idempotent — überspringt Vorbereitetes.
3. An den `media-indexer`-Agenten delegieren (Batch statt einzeln, um Tokens zu sparen): er
   liest die Prep-Dateien (`frameforge.preindex.load_prep`) + Keyframes und schreibt
   Beschreibung/Tags/Rating/Quelle via `write_asset`. Assets mit unverändertem Hash **nicht**
   erneut schicken — Kern der Token-Disziplin aus `CLAUDE.md`.
4. `frameforge index $ARGUMENTS` erneut — hebt die Phase auf `INDEXED`, sobald `assets.json`
   alle Assets abdeckt. `frameforge status $ARGUMENTS` sollte dann `INDEXED` zeigen.
5. Zusammenfassen: wie viele Assets neu/übersprungen, Ratings-Verteilung, GPS-Lücken
   (Assets ohne zugeordneten Ort — ggf. `gpx.py`/`route/locations.csv` prüfen).
