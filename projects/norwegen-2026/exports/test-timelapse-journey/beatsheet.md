# Beat-Sheet — test-timelapse-journey

3-Min-Überblickstrailer (180 s), chronologisch, beat-getrieben (125 BPM, ~0,48 s/Beat).
Mischung Timelapse-Journey + Punch-Teaser: harte Cuts/Speed-Ramps auf den Beat,
`escalate_to_drop`. Mix ~70 % Landschaft / 30 % Familie. Überwiegend Drohne, Rating ≥ 4.
Musik: `Nordlichter im Sturm - Suno.mp3` (231 s, wir nutzen 0–180 s).

**Karten-Leitmotiv:** 6 kurze Karten-Inserts (je ~2 s) zwischen den Etappen, die Route wächst
Skien → Geilo → Aurland/Flåm → Geiranger → Lom → Uvdal. Marker + Verbindungslinie aus
`route/locations.csv`.

**Familie (30 %):** vor allem Skien (Boot/See, 19 Shots) und Uvdal (Angeln/Discgolf, 13) — passt
an Anfang und Höhepunkt. Rest der Etappen fast rein Landschaft.

## Struktur (Cuts auf Beats, Zeiten ~)

| # | Zeit | Etappe / Inhalt | Tempo | Notiz |
|---|------|-----------------|-------|-------|
| 0 | 0:00–0:12 | **Cold Open Skien** — 1 starker Fjord/See-Establisher, Titel „Norwegen 2026" | langsam, 1 Cut | ruhiger Einstieg über Intro der Musik |
| M | 0:12–0:14 | Karte: Skien-Marker erscheint | — | Insert |
| 1 | 0:14–0:34 | **Skien** — See, Hütte, **Familie im Ruderboot** (Boot/Spiegelung) | mittel→schnell | Familie-Block |
| M | 0:34–0:36 | Karte: Linie Skien→Geilo | — | |
| 2 | 0:36–0:52 | **Geilo** — Berge, Hochebene, Straße | schnell, Beat-Cuts | reine Landschaft |
| M | 0:52–0:54 | Karte: →Aurland/Flåm | — | |
| 3 | 0:54–1:14 | **Aurland/Flåm** — Fjord, Kreuzfahrtschiff, Stegastein — **ACTION-PEAK 1** | sehr schnell + Speed-Ramp | auf ersten Musik-Drop |
| M | 1:14–1:16 | Karte: →Geiranger | — | |
| 4 | 1:16–1:44 | **Geiranger** — Fjord, Wasserfälle, Trollstigen-Serpentinen | schnell, treibend | stärkste Bilder, längster Block |
| M | 1:44–1:46 | Karte: →Lom | — | |
| 5 | 1:46–2:02 | **Lom** — Tal, Fluss, Stabkirche, Brücke | mittel-schnell | |
| M | 2:02–2:04 | Karte: →Uvdal (Route komplett) | — | |
| 6 | 2:04–2:44 | **Uvdal** — Fluss Abendlicht, **Familie** (Angeln/Discgolf/Kanu) — **ACTION-PEAK 2 / Climax** | schnellste Cuts + Speed-Ramps | größter Drop, Familie + Landschaft |
| 7 | 2:44–3:00 | **Outro** — weiter Fjord/Sonnenuntergang, letzter Familien-Moment, Ausblenden | langsam | Auflösung |

## Regieanweisungen für den timeline-builder

- **Chronologie strikt einhalten** (Etappen in obiger Reihenfolge, Datum aus Asset-ID/Ort).
- **Clip-Auswahl je Etappe:** `frameforge query norwegen-2026 --source drone --min-rating 4 --place <Ort>`
  (Orte teils zusammengesetzt, z. B. „Aurland", „Aurland/Flåm" → beide nehmen). Familie über
  `content.people == true` erkennen; ~70/30 Landschaft/Familie über den ganzen Film.
- **Cut auf Beats:** In-/Out-Punkte an das Beat-Grid der Musik legen (BPM 125). Clip-Länge
  0,6–3,5 s; in den Peaks (Block 3, 6) kürzeste Cuts + `speed_ramp`-Übergänge; in Intro/Outro
  längere Einstellungen.
- **Übergänge:** überwiegend `hard_cut`; `speed_ramp` in die Action-Peaks; ein `fade` am
  Anfang (aus Schwarz) und Ende (nach Schwarz).
- **Karten-Inserts (M):** je ein `map`-Track-Clip (~2 s) an den markierten Stellen; der
  map-animator rendert die Route-Reveal-Frames, hier nur die Slots + Zeiten setzen.
- **Text (minimal):** Titel „Norwegen 2026" im Cold Open; kleine Ortslabels beim ersten Clip
  jeder Etappe (Skien, Geilo, Aurland/Flåm, Geiranger, Lom, Uvdal). Keine Fließtexte.
- **Keine Clip-Doppelungen**; ähnliche Motive (mehrere Kreuzfahrtschiff-/Serpentinen-Shots)
  nur einmal, Rest als Alternative liegen lassen.
- **Musik** als Audio-Clip 0–180 s; O-Ton bleibt aus (Musik treibt), leichtes Ducking nicht nötig.
- **Ziel-Gesamtdauer 180 s** (Toleranz ±2 s).
