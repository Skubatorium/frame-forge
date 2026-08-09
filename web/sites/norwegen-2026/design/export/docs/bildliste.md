# Bildliste

Alle Bilder kommen aus dem Filmmaterial (3840 × 2160). Format **JPEG, Qualität ~78**,
sRGB, ohne EXIF. Zielgröße je Datei: **unter 300 KB**, Hero-Bilder unter 400 KB — damit
bleibt jede Seite unter 1,5 MB.

Im Projekt liegen unter `site/assets/img/` derzeit **Platzhalter** mit genau diesen
Dateinamen. Einfach überschreiben.

| Datei | Maße | Seitenverhältnis | Motiv / Zweck |
|---|---|---|---|
| `hero-01.jpg` | 2560 × 1440 | 16:9 | Fjord, weiter Blick — erstes Bild, auch Standbild bei `prefers-reduced-motion` |
| `hero-02.jpg` | 2560 × 1440 | 16:9 | Trollstigen, Serpentinen von oben |
| `hero-03.jpg` | 2560 × 1440 | 16:9 | Hochebene Valdresflye |
| `hero-04.jpg` | 2560 × 1440 | 16:9 | Nærøyfjord vom Boot oder aus der Luft |
| `hero-05.jpg` | 2560 × 1440 | 16:9 | Schärenküste bei Langesund |
| `hero-06.jpg` | 2560 × 1440 | 16:9 | Geiranger / Sieben Schwestern |
| `teaser-vlog.jpg` | 1600 × 1200 | 4:3 | Teaser Roadtrip — Bild verträgt Text im unteren Drittel |
| `teaser-drone.jpg` | 1600 × 1200 | 4:3 | Teaser Drone Edit — dito |
| `vlog-poster.jpg` | 1920 × 1080 | 16:9 | Poster des Players, idealerweise das erste Bild nach dem Cold Open |
| `drone-poster.jpg` | 1920 × 1080 | 16:9 | Poster des Players, ruhige Totale |
| `route-map.jpg` | 2276 × 1844 | ~5:4 | Google-Maps-Screenshot des Rundkurses, quer |
| `favicon.svg` | 22 × 16 | — | liegt bereits vor (Flaggenmarke) |

## Hinweise zum Zuschnitt

- **Hero:** Der Titel sitzt links unten. Die linke untere Bildhälfte sollte ruhig sein
  (Wasser, Himmel, Fels ohne Detail), sonst kämpft der Text mit dem Motiv. Der Schutzverlauf
  fängt viel ab, aber nicht alles.
- **Teaser:** Werden formatfüllend beschnitten (`object-fit: cover`) und im unteren Drittel
  stark abgedunkelt. Wichtiges Motiv nach oben legen.
- **Poster:** Kein Text im Bild, kein Play-Symbol — das setzt der Browser.
- **Karte:** Bitte den Screenshot ohne Google-UI (Suchfeld, Buttons) beschneiden; die
  Bildunterschrift auf der Seite erklärt, dass nur der norwegische Rundkurs zu sehen ist.

Optional, wenn du Lust hast: zusätzlich eine `*-960.jpg`-Variante je Hero-Bild; dann kann
`srcset` ergänzt werden. Nötig ist es nicht.
