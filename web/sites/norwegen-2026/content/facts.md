# Inhaltsquellen — Norwegen 2026

Die vollständigen Fakten stehen im Prompt: `../design/PROMPT-designsystem.md`, Abschnitt
„Die Fakten für die Norwegen-Ausprägung". Diese Datei hält nur fest, **woher** sie stammen,
damit sie bei Korrekturen an einer Stelle nachgezogen werden können.

| Inhalt der Seite | Quelle im Repo |
|---|---|
| Etappen, Kilometer, Übernachtungen | `projects/norwegen-2026/route/stages.csv` |
| Roadtrip-Log, Erlebnisse, Stimmung | `projects/norwegen-2026/route/diary.md` |
| Kartenpunkte | `projects/norwegen-2026/route/locations.csv` |
| GPS-Track der gefahrenen Strecke | `projects/norwegen-2026/route/roadtrip.gpx` |
| Höhenprofil | `projects/norwegen-2026/route/elevation.json` |
| Filmfakten Vlog (Länge, Clips, Musik, Technik) | `projects/norwegen-2026/exports/vlog-edit/final/vlog-edit_v1.report.md` |
| Filmfakten Drone (dito) | `projects/norwegen-2026/exports/drone-edit/final/drone-edit_v2.report.md` |
| Dramaturgie / Kapitel | `exports/*/beatsheet.md` |
| Titelgrafiken 4K (Norwegen 2026 / Roadtrip bzw. Drone Edit) | `exports/*/overlays/title.png`, `title-card.png` |
| Farb- und Schrift-Tokens der Filme | `projects/norwegen-2026/design/tokens.yaml` |
| Kartenbild des Rundkurses | `projects/norwegen-2026/index/final-route.png` |

## Abgeleitete Zahlen

- **26.900 Höhenmeter** kumulierter Aufstieg — Summe der positiven Differenzen über die
  1.089 Stützpunkte in `route/elevation.json`. Grober Richtwert, kein Tachowert.
- **3.829 km** Gesamtstrecke — Summe der `km`-Spalte aus `stages.csv` (inkl. ca. 325 km
  Fährstrecke).
- **1.332 km / 22 h 40 min** Roadtrip-Rundkurs — Angabe aus dem Google-Maps-Screenshot.

## Kartenbild

Liegt vor: `media/route-map-source.png` (2276 × 1844, Quelle:
`projects/norwegen-2026/index/final-route.png`).

Zeigt **nur den Roadtrip-Rundkurs** ab/bis Skien — 1.332 km, 22 h 40 min. Google Maps
erlaubt maximal zehn Wegpunkte, mehr Stationen hätten die Strecke verzerrt. Die Gesamtstrecke
enthält zusätzlich Grevenbroich → Hamburg → Flensburg → Hirtshals, die Fähre nach Larvik und
den identischen Rückweg — insgesamt ca. 3.829 km.

Für die Website als `public/assets/img/route-map.jpg` aufbereiten (JPEG, ~1600 px breit).

Maps-Link des Rundkurses (für den optionalen „in Google Maps öffnen"-Link):

```
https://www.google.com/maps/dir/Tiedemannsjordet+16,+3727+Skien,+Norwegen/Hakkesetvegen+73,+3580+Geilo,+Norwegen/Bj%C3%B8rgavegen+23,+5745+Aurland,+Norwegen/Laukifossen,+Oldeelva,+Stryn,+Norwegen/Geirangervegen+200+moh,+Fv63+14,+6216+Geiranger,+Norwegen/Trollstigen,+6300+%C3%85ndalsnes,+Norwegen/Nordal+tourist+center,+Riksvei+15+79,+2686+Fossbergom,+Norwegen/Uvdalsvegen+966,+3632+Uvdal,+Norwegen/Stabkirche+Heddal,+Heddalsvegen+412,+3676+Notodden,+Norwegen/Tiedemannsjordet+16,+3727+Skien,+Norwegen
```

## Bilder für die Seite

Freigegeben laut Absprache: Landschafts- und Drohnenbilder, Familienfotos, die
Film-Titelgrafiken. Quelle sind die bereits erzeugten Keyframes
(`~/.cache/frameforge/*/keyframes/`) und die Originale im `media_root`. Auswahl und
Zuschnitt erfolgen, sobald die Bildliste aus dem Design-System vorliegt.

**Nicht verwenden** (Regel aus `diary.md`): Tachostand-Fotos, das Snack-Einkaufsfoto.
