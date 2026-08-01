# Routen-Prompt-Vorlage

Vorlage, um aus vorhandenen Reiseunterlagen (PDF-Buchungen, Google-Maps-Liste, Notizen,
Tankquittungen) die beiden Routendateien eines Projekts zu erzeugen:

- `projects/<projekt>/route/stages.csv` — die Etappen (`day,date,from,to,via,km,overnight,note`)
- `projects/<projekt>/route/locations.csv` — die Punkte auf der Karte (`name,lat,lon,type,day`)

Du kannst den Prompt einer beliebigen KI vorlegen (auch ohne FrameForge-Kontext) und die
Antwort direkt als CSV ablegen. Danach `/ff-route <projekt>` — der `route-planner`-Agent prüft
Plausibilität und gleicht die Etappen gegen das vorhandene Material ab, bevor
`frameforge assign-places` die Zuordnung schreibt.

## Konventionen

- **Nichts erfinden.** Unbekannte Kilometer oder unsichere Koordinaten bleiben leer bzw. die
  Zeile entfällt. Eine falsche Koordinate fällt erst im gerenderten Video auf.
- **Ortsnamen wie im Zielland geschrieben** (`Flåm`, nicht `Flam`) — sie landen als Text im Bild.
- **Standtage bekommen trotzdem eine Zeile** (`from` = `to`, `km` = 0), sonst reißt die
  Tageszählung.
- `stages.csv` beschreibt **Etappen**, `locations.csv` **Orte**. Ein Ordnername wie
  `2026-07-28_Norwegen_Geiranger-Lom_1_Trollstigen` ist eine Etappe *mit* einem Zwischenstopp —
  Trollstigen gehört als POI nach `locations.csv`, nicht als Ort in die Etappenzeile.

## Prompt

```
Ich gebe dir Reiseunterlagen (Buchungen, Routenliste, Notizen). Erstelle daraus
eine CSV-Datei mit exakt diesen Spalten, ohne zusätzliche Spalten und ohne Kommentare:

day,date,from,to,via,km,overnight,note

Regeln:
- day: fortlaufende Reisetag-Nummer ab 1, lückenlos.
- date: ISO-Format YYYY-MM-DD.
- from/to: Ortsnamen wie im Zielland üblich geschrieben (z. B. "Flåm", nicht "Flam").
- via: wichtigste Zwischenstopps/Passstraßen dieser Etappe, mehrere mit "; " getrennt.
  Leer lassen, wenn es keine gab.
- km: gefahrene Strecke der Etappe als ganze Zahl. Wenn unbekannt, leer lassen –
  NICHT schätzen und nicht erfinden.
- overnight: Ort der Übernachtung nach dieser Etappe.
- note: eine kurze Bemerkung oder leer.
- Standtage (keine Weiterfahrt) bekommen trotzdem eine Zeile: from = to = Ort, km = 0.
- Antworte NUR mit der CSV, beginnend mit der Kopfzeile.

Zusätzlich, als zweiter separater CSV-Block mit den Spalten:
name,lat,lon,type,day
alle Orte, die auf einer Karte markiert werden sollen: Übernachtungen (type=overnight),
Sehenswürdigkeiten/Zwischenstopps (type=poi), größere Städte entlang der Route zur
Orientierung (type=city). Koordinaten in Dezimalgrad. Wenn du eine Koordinate nicht
sicher weißt, lass die Zeile weg statt zu raten.
```

## Beispiel für das Ergebnis

`route/stages.csv`:

```csv
day,date,from,to,via,km,overnight,note
1,2026-07-19,Zuhause,Flensburg,,320,Flensburg,Anreise
2,2026-07-20,Flensburg,Skien,Fähre Hirtshals-Larvik,410,Hütte am See,
9,2026-07-28,Geiranger,Lom,Trollstigen,190,Lom,Passstraße
```

`route/locations.csv`:

```csv
name,lat,lon,type,day
Flensburg,54.7833,9.4333,overnight,1
Trollstigen,62.4581,7.6706,poi,9
Lom,61.8386,8.5669,overnight,9
```
