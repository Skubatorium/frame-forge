# Beat-Sheet — Export „JGA" · Micha im Delirium 2026

Quellen: `brief.yaml` (Preset `jga-zweiteiler`, v4-Arc), `editorial-notes.md` (Detail-Regie —
maßgeblich), `index/assets.json` (156 `must`, 50 `nice`, 2 hart gesperrt).

**Gesamtlänge: 8:53,9 (533,9 s).** Die Musik bestimmt die Länge, nicht `target_duration_s: 525`
— die drei Tracks in voller/vorgesehener Nutzung ergeben 533,9 s. Christian: „acht oder neun
Minuten ist egal". QC-Toleranz entsprechend weit fassen.

Musik-Layout (hart):

| Track | Rolle | src_in | genutzt | Film-TC |
|---|---|---|---|---|
| Vivaldi „Der Winter" I. Allegro non molto | Intro + AKT 1 | 0 | 211,5 s (ganz) | 0:00–3:31,5 |
| Galvanize (feat. Q-Tip) [Edit] | AKT 2 | 0 | 271,4 s (ganz) | 3:31,5–8:02,9 |
| Where Is My Mind (2007 Remaster) | Aftermath | ~17 s | 45 s | 8:02,9–8:47,9 |
| (Stille) | Outro-Karte | — | — | 8:47,9–8:53,9 |

Die drei Musik-Sync-Punkte, exakt:

1. **0:00 — Vivaldi kommt langsam hoch** (`fade_in_s: 2`) unter Schwarz/Intro-Standbild.
2. **3:31,5 — HARTER Cut Vivaldi → Galvanize.** Kein Crossfade. Vivaldi endet auf dem letzten
   Akt-1-Bild (Zusteiger-Selfie `F9615661-…1429`). Galvanize startet bei src_in 0, sein
   ruhiges Intro (~9 s) liegt unter Kneipe + Bierkarte (1445 → 4817 → 1448 → 1449).
   **3:40,5 — BEAT DROP:** genau auf 1451 („Gläser werden vollgeschüttet"). Ab hier Beat-Cuts.
3. **8:02,9 — ABRUPTER Cut in die Stille**, Galvanize bricht ab, Where Is My Mind setzt bei
   src_in ~17 s ein (direkt in die traurige Stelle). Fade-out über die letzten 4 s
   (8:43,9–8:47,9), Musik ist aus, **bevor** die Danke-Karte steht.

Stil-Entwicklung über den Film (aus `arc` / `music_energy_curve: build_drop_calm`):

| Abschnitt | Anteil | Schnittrhythmus | Energie | FX | Text |
|---|---|---|---|---|---|
| Intro | 1 % | Standbild + weiche Blenden | 0 | keine | Titel |
| AKT 1 | 38,5 % | 2,6–4,5 s, ruhige Ken-Burns | steigend, warm | max. 1 dezenter Akzent | klein, randständig |
| AKT 2 | 50,9 % | 0,4–2,0 s Beat-Cuts, kaum Bewegung | Drop → Dauerdruck → Höhepunkt Karaoke | aktiv, als Akzent | groß, fetzig |
| Aftermath | 8,4 % | 3–5 s, nahezu statisch | Absturz, leer | keine (außer 1706) | keiner |
| Outro | 1,1 % | Standbild → Schwarz | Stille | keine | „Danke" |

Legende: `[M]` = must, `[N]` = nice, `[O]` = ok/Füller. Dauern sind Richtwerte für den
`timeline-builder`; die **Kapitelsummen sind bindend**, weil sie an der Musik hängen.

---

## INTRO — 0:00–0:06 (6,0 s)

| TC | Inhalt | Dauer |
|---|---|---|
| 0:00,0 | **Schwarz** (`transition_in: black`), Vivaldi setzt leise ein | 1,0 |
| 0:01,0 | weiche Blende in `design/assets/img/JGA_INTRO.png` — Titel „Micha im Delirium", Subtitle „JGA · Brüssel 2026" (im Standbild enthalten, kein zusätzlicher Text nötig) | 3,5 |
| 0:04,5 | weiche Schwarzblende, Vivaldi ist oben | 1,5 |

Kein Cold Open (`cold_open_s: 0`). Danach direkt Akt 1.

---

# AKT 1 — „Gediegen" · 0:06–3:31,5 (205,5 s)

Vivaldi trägt. Warm, langsam, ruhige Ken-Burns-Ausschnitte, Übergänge `cut` mit gelegentlichem
weichem `fade`. Text trocken, klein, **am Bildrand** — kein roter Rahmen aus der Mitte.
**FX: höchstens ein einziger dezenter Akzent im ganzen Akt** (Vorschlag: Sprechblase auf 1381).

> **Dichte-Hinweis (bewusst):** 63 Muss-Assets in 205,5 s. Basis-Standzeit **2,95 s** je Foto,
> Hero-Shots 4,0–4,5 s. Das liegt **unter** dem im Brief genannten Fenster 3,5–6 s — siehe
> „Offene Konflikte" am Ende. Akt 1 ist voll, `ok`-Füller entfallen komplett.

## A1.1 Anreise — 0:06–0:16,5 (10,5 s)
Ruhig, aber mit Vorfreude. Erster Bildkontakt nach der Blende.

- **IMG_4734** `[M]` 4,5 s — allererster Shot Rohmaterial, Abholung zu Hause. `Text: „Let's go"` (oben).
- **`1646D950-…777E.jpg`** `[M]` 3,0 s — Grimassen im Auto. **Zwangsfolge: direkt nach 4734.**
- **IMG_1699** `[M]` (Hagi, kein Zeitstempel) 3,0 s — Ankunft Unterkunft, helle Küche.

## A1.2 Unterkunft Freitag — 0:16,5–0:37 (20,5 s)
Ankommen, auspacken, „wir sind schon ziemlich alt geworden".

Reihenfolge: **1252** `[M]` Wohnzimmer → **1253** `[M]` rosa Hoodie in der Küche →
**1256** `[M]` / **1257** `[M]` Schlafzimmer → **1262** `[M]` Treppenhaus von oben →
**1265** `[M]` Wohn-Essbereich → **1281** `[M]` sechs Männer im Kreis von oben (Kapitel-Schluss).
Je ~2,9 s.

## A1.3 Pizza-Abend — 0:37–0:50 (13,0 s)
Erster kleiner Gag des Films, trocken gesetzt.

- **IMG_1309** `[M]` 4,0 s (Hero) — Uber-Eats-Fahrer, unscharf, Nacht. `Text: „Es lebe Sülemann"`, zittrig, klein, randständig.
- **IMG_1310** `[M]` 3,0 s — Pizzakartons-Stapel.
- **IMG_1312** `[M]` 3,0 s — Pizza-Nahaufnahme.
- **IMG_1264** `[M]` 3,0 s — Nachtaufnahme Fensterfront, schließt den Abend („ruhig ins Bett"). Weicher Fade auf den Schnitt zum Frühstück.

## A1.4 Samstag — Frühstück & Aufbruch — 0:50–0:59 (9,0 s)
- **IMG_1321** `[M]` 3,0 s Frühstückstisch → **IMG_1323** `[M]` 3,0 s pinke Café-Front „Marie"
  → **IMG_1325** `[M]` 3,0 s Gruppe auf dem Bürgersteig.

## A1.5 Stadtbummel / Mont des Arts — 0:59–1:19,5 (20,5 s)
Vivaldis erste Verdichtung; hier darf Ken Burns leicht ziehen.

**1328** `[M]` Straßenbahn+Fassaden → **1331** `[M]` bärtiges Selfie → **4763** `[M]` fünf Männer
Arm in Arm am Mont des Arts → **1340** `[M]` formaler Garten Kunstberg → **1338** `[M]` SW-Wandbild
Fabelfigur → **1341** `[M]` Parkpromenade Platanen → **4773** `[M]` Parkweg Schattenlicht. Je ~2,9 s.
(Optionaler weicher Zoom-Übergang 1337 → 1340 → 1338 entfällt aus Zeitgründen — 1337 ist `ok`.)

## A1.6 Einkaufsstraße & Galeries — 1:19,5–1:31,5 (12,0 s)
**1343** `[M]` Gruppe mit Rucksäcken → **1344** `[M]` „Gaufre de Bruxelles" → **1347** `[M]`
Galeries Royales innen → **4814** `[M]` Gruppe bei blauem Himmel Richtung Innenstadt. Je 3,0 s.
**1385 (2. Galeries-Perspektive) bewusst NICHT hier** — steht in A1.7.

## A1.7 Grand Place / Belgian Beer Weekend — 1:31,5–2:00,5 (29,0 s)
Emotionaler Zwischenhöhepunkt von Akt 1; hier sitzt der einzige FX-Akzent.

**1356** `[M]` Rathausturm 3,0 → **1359** `[M]` Hopfendolden 2,8 → **1360** `[M]` Zunfthäuser 3,2
→ **1362** `[M]` Lederhelme/Fliegerbrillen 3,0 → **1379** `[M]` Banner „Belgian Beer Weekend"
3,5 (`Text: „~250 Biere"`, bekritzelt/handgemalt, dynamisch, am Rand) → **1381** `[N]` belgische
Fahne als Bierglas-Aufkleber 2,5 (`FX:` Sprechblase „Design Award 2026" — **der eine erlaubte
Akt-1-Akzent**) → **1376** `[M]` Zunfthaus-Fassadendetail 2,8 → **1358** `[M]` Blick über die
Grand Place 3,0 → **1385** `[M]` Galeries innen, 2. Perspektive 2,8 → **1386** `[M]` Waffel-
Nahaufnahme mit Erdbeeren 3,0 (Brücke ins nächste Kapitel).

**Nicht doppeln:** 1356 und 1358 stehen mit 6 Bildern Abstand — Reihenfolge nicht umstellen.
Optionaler `Text:` „Belgien · Bier · Weekend" fetzig, nicht mittig, auf 1379 oder 1358.

## A1.8 Waffeln & Schokolade — 2:00,5–2:36 (35,5 s)
Längstes Akt-1-Kapitel, erstes Video.

**1387** `[M]` Waffel-Gruppentisch von oben 3,0 → **8320** `[M]` Tisch voller Waffeln, alle am
Handy 3,2 → **1389** `[M]` Gruppen-Selfie leere Teller 2,8 → **1390** `[M]` Pappbär-Aufsteller
2,8 (`FX:` kleiner Sticker — nur falls der 1381-Akzent gestrichen wird, **nicht beide**) →
**1391** `[M]` Pralinen-Vitrine 2,6 → **1392** `[M]` zwei Männer in der Boutique 2,8 →
**4790** `[M]` Schokolade kaufen 2,6 → **1393** `[M]` Marcolini-Schachtel 2,8 →
**IMG_1395** `[M]` (MOV) **Cut 0–7 s** — Praliniere wird herumgereicht.
**O-Ton-Fenster 1:** nur der „da-da-da-da"-String am Anfang (~0–2 s) ducken/hörbar, danach Musik
wieder hoch, Rest leise mitlaufen → **4793** `[M]` Schokomousse mit Erdbeeren 2,6 →
**1397** `[M]` Waffelauslage 3,0.

## A1.9 Duck Store / Manneken Pis / Genuss — 2:36–3:00,5 (24,5 s)
**1399** `[M]` „Brussels Duck Store"-Schild 2,8 → **1409** `[N]` Manneken Pis im orangen Trikot
2,5 (`FX:` leichter Farb-Pop, Original kontrastarm) → **1401** `[M]` weiße Manneken-Pis-
Nachbildung im Schaufenster 2,8 → **1403** `[M]` Schoko-Waffel am Stiel 3,0
(`Text: „Präsente für den Junggesellen"`) → **IMG_1404** `[M]` (MOV) **Cut 25–35 s**
(rein bei ~25, Biss bei ~30, raus bei ~35) 10,0 → **1406** `[M]` Still, genüsslich reinbeißen
3,2 (`Text: „Genuss pur"`).

**Nicht doppeln:** 1410 (MOV) und 1411 sind aus Budgetgründen **nicht eingeplant** — damit ist
die Manneken-Pis-Wiederholung ohnehin aufgelöst. Fällt Zeit an, zuerst **1411** nachrücken,
und zwar **frühestens 3 Bilder nach 1409**.

## A1.10 Architektur & Spiegelungen — 3:00,5–3:10,5 (10,0 s)
**1416** `[M]` steiler Blick in die Straßenschlucht („V wie Berge") 3,0 → **1420** `[M]`
Eckgebäude mit Kuppelturm 2,8 → **1423** `[M]` **Hero 4,0 s** — Thomas in Grau mit Kapuze über
Kopfsteinpflaster, „ultimatives Muss-Bild". `Text:` etwas Lustiges zur „Kunstfigur" (party-fx
darf formulieren) — klein, am Rand.

## A1.11 MOK Coffee — 3:10,5–3:22,5 (12,0 s)
Letztes Durchatmen vor dem Kippen.

**4813** `[M]` Kaffee-Verkostung auf der Terrasse 3,0 → **1430** `[M]` Männerrunde am runden
Außentisch 3,0 → **1435** `[M]` Schaufenster „100 Best Coffee Shops" 3,0 → **1440** `[M]`
Gruppe geht an Bars („London Bar") entlang 3,0 — das Bild leitet schon auf den Abend zu.

## A1.12 Pommes → Übergang — 3:22,5–3:31,5 (9,0 s)
Vivaldi läuft aus; letztes Bild endet exakt auf 211,5 s.

- **IMG_1444** `[M]` 3,0 s — kopfüber gedrehter Blick auf die Frietland-Terrasse. **Zwang: vor 1443.**
- **IMG_1443** `[M]` 3,0 s — zwei Pommes-Tüten mit Saucen.
- **`F9615661-…1429.jpg`** `[M]` 3,0 s — **Zusteiger-Selfie**, drei Männer in der sonnigen
  Fußgängerzone. **Zwang: direkt vor 1445.** Letztes Bild unter Vivaldi.

---

# MUSIKWECHSEL — 3:31,5 (HART)

Vivaldi endet ohne Ausblendung. **Harter Schnitt.** Galvanize [Edit] ab src_in 0. Die ersten
~9 s (Galvanize-Intro, „fängt super an") liegen noch auf ruhigen Kneipenbildern; der Schnitt
zieht erst mit dem Beat an. Kein langer Crossfade, `transition: cut`.

---

# AKT 2 — „Eskalation" · 3:31,5–8:02,9 (271,4 s)

Beat-Cuts 0,4–2,0 s, kaum bis keine Ken-Burns-Bewegung, `hard_cut`/`whip_pan` als Vokabular.
Comic-FX aktiv, aber **als Akzent** — Details liefert `party-fx`, hier stehen nur die
Wunschstellen aus `editorial-notes.md`. Text groß und fetzig. Mehr Videos: sie tragen den
Rhythmus mit, aber **nie Video an Video** — immer Fotos dazwischen.

## B1 Erste Kneipe (à la Bécasse) + BEAT DROP — 3:31,5–3:51,5 (20,0 s)

**Galvanize-Intro-Fenster 3:31,5–3:40,5 (9 s), noch ruhig geschnitten:**
- **IMG_1445** `[M]` 2,5 s — Eingang à la Bécasse.
- **4817** `[M]` 2,0 s — enge Zugangsgasse. **Zwang: 1445 → 4817.**
- **IMG_1448** `[M]` 2,0 s — Innenraum, traditionelles Bierkafé.
- **IMG_1449** `[O→Sync]` 2,5 s — große belgische Bierkarte. **Letztes Bild vor dem Drop.**

**3:40,5 — BEAT DROP. Ab hier Party-Rhythmus:**
- **IMG_1451** `[M]` 1,5 s Kwak im Holzständer — **der Cut sitzt auf dem Beat.**
- **IMG_1452** `[M]` 1,5 s Steinzeugkrug → **IMG_1453** `[M]` 1,5 s einschenken →
  **IMG_1454** `[M]` 1,5 s Krug + Gläser („vollgeschüttet").
- **8337** `[M]` 1,2 s Nah-Selfie, Zunge raus.
- **8648** `[M]` (HEIC) 2,0 s Gruppen-Selfie am langen Holztisch — „wo das Ganze losgeht".
- **IMG_1455** `[M]` 1,8 s Emailleschild „Timmermans". **Zwang: nach dem Laden platzieren.**
  `Text:`/`FX:` Wortspiel mit „Witte" (Pfeile + „Nebengewerbe").

## B2 Delirium / Bierverkostung — 3:51,5–4:15,5 (24,0 s)
- **1459** `[N]` 1,2 s blauer Leucht-Haarreif.
- **IMG_1460** `[M]` (MOV) 5,0 s — **Michas wahnsinniges Lachen. O-Ton-Fenster 2: an.**
- **1461** `[M]` 1,6 → **1463** `[M]` 1,8 (Brett mit 9 Gläsern) → **4824** `[M]` 2,2 (Bar innen
  mit Kreidetafel) → **2636** `[M]` 1,6 (Kreidetafel Craft-Bier-Liste) → **1464** `[M]` 2,6
  (pinkes Delirium-Neon mit Elefant, `FX:` „Delirium" zittrig nachgemalte Leuchtschrift) →
  **1465** `[M]` 1,6 (Daumen hoch) → **1466** `[M]` 1,6 (Tisch voller leerer Gläser) →
  **1474** `[O]` 1,2 (Kriek) → **1473** `[M]` 1,6 (fast leeres Glas) → **1475** `[M]` 1,8
  (extreme Nahaufnahme Delirium-Glas).

**Nicht doppeln:** 2636 hier, 2642 in B4, 2644 im Aftermath — nie als Serie.

## B3 Kreisbilder / Weg zur Rooftop-Bar — 4:15,5–4:22,5 (7,0 s)
**1497** `[M]` 2,5 Froschperspektive aus der Kreismitte → **1499** `[N]` 1,5 Untersicht
Hochhaustürme → **1476** `[M]` 2,0 Delirium-Gasse voller Bar-Schilder → **1478** `[O]` 1,2
Drug-Opera-Fassade (streichen, wenn der Schnitt zu fetzig dafür ist).

## B4 Rooftop Bar 58 — Aufstieg & goldene Stunde — 4:22,5–4:50,5 (28,0 s)
- **IMG_1500** `[M]` 3,0 s Aufzug-Selfie. `Text:` **groß über die Köpfe: „Rooftop Bar 58 — wir kommen"**.
- **4829** `[M]` (HEIC) 2,0 s Glühbirnen-Ziffern „58" — direkt nach dem Hochfahren.
- **1501** `[M]` 1,8 Holzdeck → **1502** `[M]` 1,8 Dachpanorama → **1509** `[M]` 2,0 Kirchturm im
  warmen Licht (**Zwang: 1509 früh in der Sequenz**) → **1503** `[M]` 1,8 Terrasse mit Palme/
  Lichterketten → **1505** `[M]` 1,8 Dächer mit Kirchturm → **1506** `[N]` 1,5 Skyline mit
  Atomium → **1511** `[M]` 1,8 Selfie drei Männer → **1707** `[M]` (Hagi) 2,2 Selfie zwei Männer
  auf der Dachterrasse (`FX:` Kronen/Herzchen) → **8649.HEIC** `[N]` 1,3 → **8652.HEIC** `[N]` 1,3
  → **1519** `[O]` 1,7 Gruppenfoto (`Text:` optional „Düsseldorfer Reisegruppe") →
  **2642** `[O]` 1,3 Sonnenuntergang → **1549** `[N]` (MOV) 3,0 s Ausschnitt volle Dachterrasse.

## B5 Rooftop — Corona & Gruppe — 4:50,5–5:10,5 (20,0 s)
- **IMG_1524** `[M]` 2,5 s — Untersicht in den Kreis, alle stoßen mit Corona an („super toll"),
  **Sync auf einen Galvanize-Akzent legen**.
- **1531** `[N]` 1,5 Anstoßen, Christoph wieder da.
- **1543** `[M]` 2,0 Zunge raus neben Corona. `Text:` oben rechts „Stay hydrated".
- **1544** `[N]` 2,5 Corona gegen den Sonnenuntergang. `FX:` Werbe-Look, Flüssigkeitslinie = Horizont.
- **1514** `[M]` 2,5 ganze Gruppe als Breitbild-Reihe. `Text:`/`FX:` „Wo ist Christoph?"
- **1515** `[N]` 1,6 Hochkant-Gruppenfoto (groß skalieren, oben nur Himmel).
- **1548** `[N]` 1,5 → **8654** `[N]` 1,4 → **1540** `[O]` 1,0 / **1541** `[O]` 1,0 →
  **4839** `[N]` (MOV) 3,0 s (**0–5 s** oder **10 s–Ende**, ein Teil genügt).

## B6 Blaue Stunde & Abgang — 5:10,5–5:28,5 (18,0 s)
Farbwechsel golden → blau; hier atmet Akt 2 einmal kurz durch (Cuts an die obere Grenze, 2 s).

**1551** `[N]` 1,5 → **1554** `[M]` 1,8 Brüstung, blaue Stunde → **1555** `[M]` 1,8 blaue Stunde
→ **1557** `[M]` 1,8 Froschperspektive drei Männer im Kreis → **1588** `[N]` 1,5 blau beleuchtete
Gebäudekante → **4840** `[N]` (MOV) 2,0 → **IMG_1508** `[M]` 3,0 **feuriger Sonnenuntergang —
Zwang: spät, kurz vor dem Verlassen der Bar** → **IMG_1518** `[M]` 2,2 feurig-oranger
Sonnenuntergang mit Silhouette → **IMG_1556** `[M]` 2,4 nächtliche Dachterrasse, blau
angestrahlte Fassade. **Zwang: 1518 direkt vor 1556.** 1556 schließt die Rooftop-Sequenz.

**Nicht doppeln:** Die Sonnenuntergänge 1502/1505/1506/1509/2642 (B4) sind bewusst von
1508/1518 (B6) getrennt — keine zwei fast gleichen hintereinander.

## B7 Nachtstraßen / Burger — 5:28,5–5:43,5 (15,0 s)
**1589** `[M]` 2,5 „More than a beer museum" bei Nacht → **1591** `[N]` 1,2 O'Reilly's →
**1592** `[N]` 1,0 Neon „Down Town" (Spiegelung, gut für schnellen Schnitt) → **1594** `[M]` 1,8
Burger + Bier → **1596** `[M]` 1,6 Burger-Nahaufnahme → **1597** `[M]` 2,2 Gruppe am Stehtisch →
**1598** `[M]` 2,7 Nacht-Selfie vor Juwelier (`Text:` links/oben „Frische Token") →
**1607** `[O]` 1,2 Stehtische, blaues Neon (Übergang in die Red-Bar).

## B8 Red Karaoke-Bar I — Ankunft & Aufheizen — 5:43,5–6:15,5 (32,0 s)
- **1608** `[M]` 1,8 grinsender Mann stößt an („der Tequila ist da").
- **1610** `[N]` (MOV) 3,0 s — **ab ~28 s** („Was machst du, was machst du"), Rest weg.
- **1611** `[M]` 1,8 rotes Neon „KARAOKE".
- **IMG_1613** `[M]` (MOV) **Cut ~10–24 s**, 14,0 s — **ganze Szene zusammenhalten, nicht
  zerschneiden**; das „Füßchen" bei **~21 s muss drin sein**. **O-Ton-Fenster 3: an.**
- **1614** `[N]` 1,5 vier Männer Porträt (Christians Wunschbild) → **1617** `[M]` 1,5 lachender
  Mann auf Barhocker → **1619** `[M]` 1,6 „La Pod" → **1620** `[M]` 1,6 LED-Haarreif-Porträt →
  **8656.HEIC** `[N]` 1,2 Karaoke-Screen „I Want It That Way" → **8656.MP4** `[N]` 2,5 s
  (**früher raus bei ~2,5 s**, Pausen weg) → **1622** `[M]` 1,5 Bartheke, blaues Licht.

## B9 CAST-INTRO — 6:15,5–6:24,5 (9,0 s) ⭐ eigener Beat
**Mitten in der Red-Bar-Sequenz**, wie im Preset-Arc vorgesehen. Neun Standbilder, je ein
Sonnenbrillen-Foto, Name „stampft" rein (Bangers), kurzer SFX, `color_pop` beim Cut erlaubt.
Umsetzung: `party-fx`. Cuts hart auf den Galvanize-Beat.

| # | Person | Foto | Dauer |
|---|---|---|---|
| 1 | Witte | IMG_1624 | 0,9 |
| 2 | Christoph | IMG_1625 | 0,9 |
| 3 | Matti | IMG_1627 | 0,9 |
| 4 | Bartosz | IMG_1628 | 0,9 |
| 5 | Hagi | IMG_1629 | 0,9 |
| 6 | Bernhard | IMG_1630 | 0,9 |
| 7 | André | IMG_1631 | 0,9 |
| 8 | Skuub | IMG_1632 | 0,9 |
| 9 | **Micha** | IMG_1626 | 1,8 |

Micha zuletzt und länger; Stempel „Micha im Delirium", optional in Michas Sonderblau `#4fd8ff`.
Namen exakt so schreiben. Danach geht die Eskalation ohne Atempause weiter.

## B10 Red Bar II — HÖHEPUNKT (Tanz / Gesang / Tequila) — 6:24,5–7:34,5 (70,0 s)
Das energetische Zentrum des Films. Videolastig, dazwischen konsequent Fotos.

| Reihenfolge | Asset | Fenster / Dauer |
|---|---|---|
| 1 | **IMG_1621** `[M]` (MOV) Teil A | ~1–7 s (Lichter gehen an, Grimassen) — 6,0 |
| 2 | **1636** `[M]` Gruppenfoto blau-violett | 1,5 |
| 3 | **IMG_1621** Teil B | ~20–24 s (Arme hoch) — 4,0 |
| 4 | **1634** `[M]` Gruppe in blau-rotem Neon | 1,8 · `Text:` „Gehen hier etwa schon die Lampen aus?" |
| 5 | **IMG_1621** Teil C | ~29 s–Ende — 4,0 |
| 6 | **IMG_1623** `[M]` (MOV) | 0–6 s (max. 8) — 6,0 |
| 7 | **1639** `[M]` Dart, „Arm hoch" | 1,2 |
| 8 | **IMG_1635** `[M]` (MOV) Teil A | ~0–5 s (Dance-Move) — 5,0 · `FX:` Farb-Pop/Speedlines auf den Beat |
| 9 | **8655** `[N]` Bar-Bild | 1,2 |
| 10 | **IMG_1635** Teil B | ~8–13 s (runtergehen) — 5,0 |
| 11 | **1640** `[M]` rote japanische Leuchtschrift („Lichter an", unscharf, absolutes Muss) | 1,5 |
| 12 | **IMG_1637** `[M]` (MOV) **Hauptstelle 2:22–2:37** | 15,0 — **die wichtigste Sekunde des Films. O-Ton-Fenster 4: an.** Ducking über die volle Länge. Das Umdrehen bei ~2:22 auf einen Galvanize-Akzent legen. |
| 13 | **IMG_1638** `[M]` (MOV) | ~0–3 s (oder ~8–9 s, Bräutigam drückt jemanden) — 3,0 |
| 14 | **IMG_1641** `[M]` (MOV) | ~0:24–0:29 — 5,0 · **O-Ton-Fenster 5: an** |
| 15 | **IMG_4835** `[M]` (MOV) | **ab ~8 s**, Tequila-Shot wird genommen und hochgehalten **bis zum Ende** — 8,0 · **O-Ton-Fenster 6: an** · `FX:` Farb-Pop |

Puffer 1,8 s für Feinjustage auf den Beat. **4840** `[N]` bzw. ein zweiter 4839-Teil sind
Reserve, falls ein Videofenster kürzer ausfällt.

## B11 Weiterziehen (Delirium Village / Dubliner) — 7:34,5–7:43,5 (9,0 s)
**1646** `[M]` 2,0 nächtlicher Kopfsteinpflaster-Platz → **1648** `[M]` 2,5 Neon „Delirium
Village" mit Elefant → **1649** `[M]` 2,2 „The Dubliner" → **1650** `[M]` 2,3 zwei Männer
posieren nachts. `Text:` dezent, party-fx formuliert („Noch ahnen sie nicht, wie toll der Abend
wird" / „Sie lassen sich den Abend nochmal durch die Nase gehen").

## B12 Taxi — 7:43,5–7:53,5 (10,0 s)
- **1652** `[M]` 2,0 s — Blick von der Rückbank zur Frontscheibe.
- **IMG_1653** `[M]` (MOV) **Cut ~10–18 s** — 8,0 s. Kamera dreht, Hände hoch.
  **KEIN Ducking** (Christian explizit) — Galvanize läuft ungedämpft durch. Das ist die
  letzte laute Strecke vor dem Abbruch.

## B13 Abgeschossen im Bett & Gurken-Gag — 7:53,5–8:02,9 (9,4 s)
- **1656** `[N]` 1,5 lümmeln lachend auf Betten.
- **1658** `[M]` 2,2 Gruppen-Selfie von oben, schwarze Crew-Shirts.
- **1659** `[N]` 1,5 Arme aus („ich war's nicht").
- **IMG_1660** `[M]` 2,2 — Gurken vor dem offenen Kühlschrank. `Text:` nur **„WTF?"**.
- **IMG_1661** `[M]` 2,0 — zwei Männer albern am Kühlschrank, drei Gurken in der Hand.
  `Text:` „Der Michael mag Gurken. Gib mir Gurken. Der Michael braucht Gurken."
  **Letztes Bild von Akt 2** — der Cut auf 8:02,9 ist der Musikabbruch.

---

# AFTERMATH / OUTRO — 8:02,9–8:47,9 (45,0 s)

**8:02,9 — abrupter Cut in die Stille.** Where Is My Mind ab src_in ~17 s. Sehr langsam,
nahezu statisch, kein Ken Burns, keine FX außer dem einen Herzchen/Kronen-Akzent auf 1706.
Kein Text. Übergänge weich.

| Reihenfolge | Asset | Dauer | Notiz |
|---|---|---|---|
| 1 | **1663** `[M]` | 3,0 | Gruppe tagsüber auf den Sofas — „alle erledigt" |
| 2 | **1664** `[M]` | 3,5 | Ledersofas, der neue Tag |
| 3 | **1697** `[N]` (Hagi) | 3,0 | Mann mit Koffer am Bordstein — Christoph, dezent von hinten |
| 4 | **1665** `[M]` | 3,0 | beugt sich über … (hell, Airbnb) — Kotz-Andeutung, dezent |
| 5 | **1703** `[M]` (Hagi) | 3,5 | „richtig gutes Gefühl" |
| 6 | **1705** `[M]` (Hagi) | 3,0 | |
| 7 | **1666** `[M]` | 3,5 | Micha total zerstört |
| 8 | **1667** `[M]` | 3,5 | „mir geht's gut", drückt den Bauch |
| 9 | **1706** `[M]` (Hagi) | 4,5 | absolutes Muss-Bild. `FX:` Herzchen + goldene Kronen (einziger Aftermath-Effekt) |
| 10 | **1668** `[M]` | 3,0 | warten mit Rucksäcken auf dem Bürgersteig |
| 11 | **2644** `[M]` | 3,5 | einer liegt auf der Couch, einer Daumen hoch — **Zwang: ans Ende** |
| 12 | **`93638dac-…5F53.jpg`** `[M]` | 4,0 | Auto-Schlaf, angeschnallt. **Zwang: zuerst** |
| 13 | **`c12b0d91-…EA4B.jpg`** `[M]` | 4,0 | Auto-Schlaf mit Nackenkissen. **Zwang: danach** |

**Zwangsfolge eingehalten:** 1663/1664 → … → 1666 → 1667 → 2644 → 5F53 → EA4B.
**Musik-Fade-out 8:43,9–8:47,9** (`fade_out_s: 4`) über die beiden Auto-Fotos. Bei 8:47,9 ist es still.

## SCHLUSS — 8:47,9–8:53,9 (6,0 s)
- `design/assets/img/JGA_OUTRO.png` („Danke") 4,5 s, **in Stille**.
  Falls die Karte kein „Danke" trägt: danach schlichte credits-/title-card „Danke"
  (bestehendes SVG-Template), dafür 2,5 s aus der Standzeit abzweigen.
- 1,5 s Blende → **Schwarz** (`transition_out: black`). Ende bei 8:53,9.

---

# Zwangsfolgen (wörtlich aus `editorial-notes.md` §Reihenfolge-Zwänge)

1. 4734 → …777E (ganz am Anfang) — *A1.1*
2. F9615661…1429 **direkt vor** 1445 — *A1.12 → B1*
3. 1445 → 4817 (Bécasse: Eingang dann Zugangsgasse) — *B1*
4. 1444 **vor** 1443 (Pommes) — *A1.12*
5. 1455 **nach** dem Laden platzieren — *B1, letztes Bild des Kapitels*
6. 1509 früh, **1508 spät** (kurz vor Verlassen der Rooftop-Bar) — *B4 bzw. B6*
7. 1518 **direkt vor** 1556 — *B6*
8. Cast-Intro **in** der Red-Bar-Sequenz, Micha zuletzt — *B9, zwischen B8 und B10*
9. Aftermath: 1663/1664 → … → 1666 → 1667 → 2644
10. Schluss: …5F53 → …EA4B → JGA_OUTRO → Schwarz

# Nicht-doppeln (eingehalten)

- **1356 / 1358** (Grand Place): in A1.7 durch 6 Bilder getrennt — nicht umsortieren.
- **1409 / 1410 / 1411** (Manneken Pis): nur **1409** eingeplant, 1410/1411 nicht — Wiederholung
  entfällt. Beim Nachrücken: mindestens 3 Bilder Abstand.
- **2636 / 2642 / 2644**: verteilt auf B2 / B4 / Aftermath — nie als Serie.
- **Rooftop-Sonnenuntergänge** (1502/1505/1506/1509/2642 vs. 1508/1518): auf B4 und B6 gestreut,
  dazwischen liegen B5 (Corona) und der Farbwechsel in die blaue Stunde.
- **8646.HEIC/.MP4** (Auto-Schlaf/„die Kaputten") **nicht eingeplant** — Duplikat-Gefahr zu
  5F53/EA4B im Outro, so ausdrücklich in den Notes gewarnt.
- 1256/1257 (Schlafzimmer) stehen zwar nebeneinander, zeigen aber unterschiedliche Räume —
  bei sichtbarer Ähnlichkeit im Preview 1257 nach hinten in A1.2 ziehen.

# O-Ton-Fenster (Musik ducken)

| # | Clip | Fenster | Kapitel | Regel |
|---|---|---|---|---|
| 1 | IMG_1395 | nur ~0–2 s („da-da-da-da") | A1.8 | danach Musik wieder hoch, Rest leise |
| 2 | IMG_1460 | ganzer Ausschnitt (5 s) | B2 | Michas Lachen |
| 3 | IMG_1613 | 10–24 s | B8 | Szene zusammenhalten, „Füßchen" bei ~21 s |
| 4 | IMG_1637 | 2:22–2:37 | B10 | Hauptstelle, tiefstes Ducking |
| 5 | IMG_1641 | 0:24–0:29 | B10 | |
| 6 | IMG_4835 | ab 8 s bis Ende | B10 | Tequila |
| — | **IMG_1653** | 10–18 s | B12 | **AUSNAHME: KEIN Ducking**, Musik durchlaufen lassen |

IMG_1621 und IMG_1635 laufen ohne Ducking (Musik trägt) — `original_audio_policy: accent`.

# Verbotene Shots

Die 67 Dateien aus `brief.yaml:forbidden_shots` sind **nirgends** eingeplant und dürfen vom
`timeline-builder` auch nicht als Ersatz nachgezogen werden. Die zwei hart gesperrten Assets
(IMG_4745, IMG_8338) stehen ohnehin nicht im verfügbaren Pool.

---

# Report

## Kapitel-Liste

| Kapitel | TC | Dauer | must | nice |
|---|---|---|---|---|
| Intro | 0:00–0:06 | 6,0 | (Standbild) | — |
| A1.1 Anreise | 0:06–0:16,5 | 10,5 | 3 | 0 |
| A1.2 Unterkunft Freitag | 0:16,5–0:37 | 20,5 | 7 | 0 |
| A1.3 Pizza-Abend | 0:37–0:50 | 13,0 | 4 | 0 |
| A1.4 Frühstück & Aufbruch | 0:50–0:59 | 9,0 | 3 | 0 |
| A1.5 Stadtbummel / Mont des Arts | 0:59–1:19,5 | 20,5 | 7 | 0 |
| A1.6 Einkaufsstraße & Galeries | 1:19,5–1:31,5 | 12,0 | 4 | 0 |
| A1.7 Grand Place / Beer Weekend | 1:31,5–2:00,5 | 29,0 | 9 | 1 |
| A1.8 Waffeln & Schokolade | 2:00,5–2:36 | 35,5 | 10 | 0 |
| A1.9 Duck Store / Manneken / Genuss | 2:36–3:00,5 | 24,5 | 5 | 1 |
| A1.10 Architektur | 3:00,5–3:10,5 | 10,0 | 3 | 0 |
| A1.11 MOK Coffee | 3:10,5–3:22,5 | 12,0 | 4 | 0 |
| A1.12 Pommes → Übergang | 3:22,5–3:31,5 | 9,0 | 3 | 0 |
| **B1 Erste Kneipe + BEAT DROP** | 3:31,5–3:51,5 | 20,0 | 10 | 0 |
| B2 Delirium / Bierverkostung | 3:51,5–4:15,5 | 24,0 | 10 | 1 |
| B3 Kreisbilder / Weg | 4:15,5–4:22,5 | 7,0 | 2 | 1 |
| B4 Rooftop — goldene Stunde | 4:22,5–4:50,5 | 28,0 | 9 | 4 |
| B5 Rooftop — Corona & Gruppe | 4:50,5–5:10,5 | 20,0 | 3 | 6 |
| B6 Blaue Stunde & Abgang | 5:10,5–5:28,5 | 18,0 | 6 | 3 |
| B7 Nachtstraßen / Burger | 5:28,5–5:43,5 | 15,0 | 5 | 2 |
| B8 Red Karaoke-Bar I | 5:43,5–6:15,5 | 32,0 | 7 | 4 |
| **B9 CAST-INTRO** | 6:15,5–6:24,5 | 9,0 | 9 | 0 |
| **B10 Höhepunkt (Tanz/Gesang/Tequila)** | 6:24,5–7:34,5 | 70,0 | 11 | 1 |
| B11 Weiterziehen | 7:34,5–7:43,5 | 9,0 | 4 | 0 |
| B12 Taxi | 7:43,5–7:53,5 | 10,0 | 2 | 0 |
| B13 Abgeschossen & Gurken | 7:53,5–8:02,9 | 9,4 | 3 | 2 |
| Aftermath | 8:02,9–8:47,9 | 45,0 | 12 | 1 |
| Schluss (Danke → Schwarz) | 8:47,9–8:53,9 | 6,0 | (Standbild) | — |
| **Gesamt** | | **533,9 s = 8:53,9** | **156** | **27** |

## Bilanz

- **must: 156 / 156 untergebracht** (Akt 1: 62 + Zusteiger-Foto = 63, Akt 2: 81, Aftermath: 12).
- **nice: 27 / 50 untergebracht** — Akt 2 fast vollständig (24), Akt 1 nur 2, Aftermath 1.
- `ok`-Füller: 6 (1449, 1474, 1478, 1519, 2642, 1540/1541, 1607) — nur dort, wo die
  editorial-notes sie ausdrücklich vorsehen (v.a. 1449 als Sync-Bild).
- Verbotene Shots: 0 eingeplant.

## Offene Konflikte

1. **Akt-1-Pacing sprengt das Brief-Fenster.** `brief.yaml` nennt 3,5–6 s je Foto in Akt 1.
   63 Muss-Assets in 205,5 s ergeben rechnerisch **2,95 s Basis-Standzeit** (Hero-Shots 4,0–4,5 s).
   Entweder das Fenster wird auf **2,6–4,5 s** korrigiert (mein Vorschlag, so ist das Beat-Sheet
   gebaut, bleibt innerhalb `pacing.min_s: 0.4 / max_s: 6`) — oder ~15 Akt-1-Musts müssten
   gestrichen werden. Ich habe nichts gestrichen.
2. **Akt-1-`nice` fallen fast komplett raus** (17 von 19): 8306, 8310, 8321, 1322, 1348, 1353,
   1410, 1411, 1412, 1419, 1425, 1427, 1439, 4754, 4782, 4783, 4804. Kein Platz unter Vivaldi.
   Nachrück-Priorität, falls Zeit frei wird: **1439** (nasses Kopfsteinpflaster, „sehr gut") →
   **1411** → **1348** → **4754**.
3. **Aftermath-Pacing** liegt bei 3,0–4,5 s statt der im Brief genannten 4–8 s: 12 Musts in 45 s.
   Ich habe Where Is My Mind auf die **Obergrenze 45 s** gezogen (Brief erlaubt 35–45), mehr
   geht nicht, ohne Musts zu streichen. 1700/1702/1704 `[N]` (Hagi) entfallen.
4. **Gesamtlänge 533,9 s liegt 8,9 s über `target_duration_s: 525`.** Laut Brief ist das ein
   offener Richtwert, Musik bestimmt die Länge — QC-Toleranz muss ≥ ±15 s sein, sonst schlägt
   das Gate an.
5. **Videofenster sind Schätzungen aus den Notes**, nicht am Material verifiziert (kein Bash).
   Kritisch: IMG_1637 (Hauptstelle 2:22–2:37 setzt eine Clipdauer > 2:37 voraus), IMG_1621
   (Teil C „~29 s–Ende" — Restlänge unbekannt, ich rechne mit 4 s), IMG_4835 („ab 8 s bis Ende"
   — ich rechne mit 8 s Rest). Der `timeline-builder` muss diese drei gegen die echten
   Clipdauern prüfen; Abweichungen federt der 1,8-s-Puffer in B10 ab.
6. **FX-Akzent in Akt 1:** Brief erlaubt genau einen. Die Notes nennen zwei Kandidaten (1381
   Sprechblase, 1390 Sticker). Ich habe **1381** gesetzt und 1390 FX-frei gelassen — party-fx
   darf tauschen, aber **nicht beide** bespielen.
7. **1449** ist im Index `ok`, trägt aber den Musikwechsel-Sync. Es steht bewusst als
   `ok→Sync`-Ausnahme im Plan und darf nicht als Füller wegoptimiert werden.
