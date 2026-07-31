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
3. An den `media-indexer`-Agenten delegieren, in kleinen Batches (8–10 Assets, damit nichts
   hängenbleibt): er holt die Worklist via `frameforge index-todo <projekt> [--limit N]`, sieht
   je Asset EIN Keyframe an und schreibt sofort mit `frameforge index-asset <projekt> <hash>
   --summary … --tags … --rating … --source …`. Bei viel Material den Agenten pro Batch neu
   beauftragen. Assets mit unverändertem Hash landen nicht in der Worklist — Token-Disziplin.
4. `frameforge index $ARGUMENTS` erneut — hebt die Phase auf `INDEXED`, sobald `assets.json`
   alle Assets abdeckt. `frameforge status $ARGUMENTS` sollte dann `INDEXED` zeigen.
5. Zusammenfassen: wie viele Assets neu/übersprungen, Ratings-Verteilung, GPS-Lücken
   (Assets ohne zugeordneten Ort — ggf. `gpx.py`/`route/locations.csv` prüfen).
