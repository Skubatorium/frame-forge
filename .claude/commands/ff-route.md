---
description: Reiseroute erfassen und prüfen - Etappen, Kartenpunkte, Zuordnung
argument-hint: <projekt-name>
---

Route für Projekt `$ARGUMENTS` erfassen bzw. prüfen. Ergebnis sind zwei Dateien unter
`projects/$ARGUMENTS/route/`: `stages.csv` (Etappen) und `locations.csv` (Punkte auf der Karte).
Grundlage für Tag-/Etappen-/Ortszuordnung (`frameforge assign-places`), Kilometerzähler und
Karten-HUD.

Ablauf:

1. **Stand zeigen:** `frameforge assign-places $ARGUMENTS --dry-run`. Existiert noch keine
   `stages.csv`, sagt das Kommando es. `frameforge days $ARGUMENTS` zeigt, an welchen Tagen
   überhaupt Material entstanden ist — das ist die Gegenprobe zur Etappenliste.
2. **Eingabe holen** — drei Wege, der Nutzer wählt:
   - Er diktiert die Etappen konversationell (Tag für Tag: von, nach, über, km, Übernachtung).
   - Er hat die Liste schon (z. B. über `templates/prompts/route.md` von einer anderen KI) und
     gibt sie als CSV.
   - Er legt Unterlagen (Buchungen, Screenshots, Notizen) vor und lässt sie auswerten.
3. **An `route-planner` delegieren:** schreibt `stages.csv` + `locations.csv`, prüft
   Plausibilität (lückenlose Tage, Anschluss `to`→`from`, km gegen Luftlinie, Übernachtung,
   Tage ohne Material und umgekehrt) und meldet Unsicheres als Rückfrage, statt es zu erfinden.
4. **Trockenlauf ansehen:** `frameforge assign-places $ARGUMENTS --dry-run` — Assets je Tag,
   Ortsquellen (`gps`/`gpx`/`leg`/`stage`/`unknown`) und die Konfliktliste (bisheriger, aus dem
   Ordnernamen geratener Ort vs. berechneter). Erst wenn der Report plausibel ist:
   `frameforge assign-places $ARGUMENTS` real ausführen.
5. **Lücken schließen:** `frameforge places-todo $ARGUMENTS [--day N]` listet die Clips, deren
   Ort unklar blieb (kein GPS, kein POI in Reichweite). Keyframes ansehen, Vorschlag machen,
   der Nutzer bestätigt, dann `frameforge set-place $ARGUMENTS <asset-id> --place "…"
   [--kind stop|leg]`.
6. **Optional Routengeometrie:** liegt ein echter GPX-Track oder ein Google-Maps-Export vor,
   unter `route/` ablegen (KML wird gelesen). Sonst `frameforge route-build $ARGUMENTS` — baut
   `route/roadtrip.gpx` aus `stages.csv` + `locations.csv`.

Regeln:

- **Nie raten.** Fehlende Kilometer bleiben leer, unsichere Koordinaten entfallen. Eine
  erfundene Zahl ist im fertigen Video nicht mehr als solche erkennbar.
- Ortsnamen so schreiben, wie sie im Bild stehen sollen (`Flåm`, nicht `Flam`).
- Ein Ordnername wie `2026-07-28_Norwegen_Geiranger-Lom_1_Trollstigen` ist eine **Etappe mit
  Zwischenstopp**: Geiranger→Lom gehört nach `stages.csv`, Trollstigen als POI nach
  `locations.csv`.
- Nichts wird still überschrieben: manuell gesetzte Orte bleiben ohne `--force` unangetastet.
