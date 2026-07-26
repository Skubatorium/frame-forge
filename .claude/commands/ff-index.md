---
description: Material analysieren und .md-Beschreibungen erzeugen
argument-hint: <projekt-name>
---

Material für Projekt `$ARGUMENTS` indizieren. Erfordert Projekt-Phase `>= INGESTED`
(`gate_index` in `frameforge/state.py` — bei Verstoß meldet `frameforge index` bzw. der
Gate-Hook den fehlenden Schritt).

Schritte:
1. `frameforge index $ARGUMENTS` ausführen — prüft das Gate selbst.
2. Für jedes Asset ohne aktuellen Hash in `assets.json`: Keyframes extrahieren
   (`frameforge.keyframes`), dann an den `media-indexer`-Agenten delegieren (Batch statt
   einzeln, um Tokens zu sparen). Assets mit unverändertem Hash **nicht** erneut schicken —
   das ist der Kern der Token-Disziplin aus `CLAUDE.md`.
3. Nach Abschluss: `frameforge status $ARGUMENTS` sollte Phase `INDEXED` zeigen.
4. Zusammenfassen: wie viele Assets neu/übersprungen, Ratings-Verteilung, GPS-Lücken
   (Assets ohne zugeordneten Ort — ggf. `gpx.py`/`route/locations.csv` prüfen).
