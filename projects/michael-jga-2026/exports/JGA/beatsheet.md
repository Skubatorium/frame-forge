# Beat-Sheet — Export „JGA" · Micha im Delirium 2026 — **RUNDE 2**

Löst die Runde-1-Fassung (8:53,9, Vivaldi + Galvanize + Ducking) vollständig ab.

Quellen (in dieser Rangfolge):
`editorial-notes-round2.md` (Preview-Feedback, **überschreibt punktuell**) →
`editorial-notes.md` (Runde-1-Detailregie, Basis) → `audio-plan.md` (Runde 2, Musik-Anker
**bindend**) → `brief.yaml` (Preset `jga-zweiteiler`, forbidden_shots, Cast-Reihenfolge) →
`priorities.csv` / `index/assets.json` (156 `must`, 50 `nice`, 2 hart gesperrt).

**Gesamtlänge: 7:08,4 (428,4 s).** Die drei Musiktracks bestimmen die Länge. Gegenüber
Runde 1 sind **105,5 s (~1:45) raus** — Kürzung nach `ok` → `nice` → (nur wo Runde 2 es
ausdrücklich sagt) `must`. Streichliste: siehe „Bilanz" / „Offene Konflikte".

## Musik-Layout (hart, aus `audio-plan.md` §1 — Kapitelsummen hängen daran)

| Track | Rolle | src_in | genutzt | Timeline | Ein/Aus |
|---|---|---|---|---|---|
| **Champions League Theme** | Intro + AKT 1 | 0,0 | **181,45 s** (ganz) | 0,00–181,45 | `fade_in_s: 2` · **hartes Ende** |
| **Miserlou (loop-196)** | AKT 2 | 0,0 | **195,93 s** | 181,45–377,38 | **harter Cut beidseitig** |
| **Where Is My Mind (2007 Rem.)** | Aftermath / Outro | **17,0** | **45,0 s** | 377,38–422,38 | kein fade_in · `fade_out_s: 4` |
| *(Stille)* | Schluss-Standbild | — | ~6,0 s | 422,38–428,40 | — |

Die drei Anker, exakt:

1. **0,00 — CL Theme kommt hoch** (`fade_in_s: 2,0`) unter Schwarz → `JGA_INTRO.png`.
   Erste Blende darf gestreckt sein; die **zweite** (raus aus dem Standbild) ist deutlich
   kürzer als in Runde 1 (1,2 s statt 1,5 s + Vorlauf).
2. **181,45 — HARTER Cut CL Theme → Miserlou.** Kein Crossfade. Das CL Theme endet **auf
   dem Pommes-Schwenk** (IMG_1443 steht ab 181,40). Miserlou `src_in 0`.
   **183,53 — Bild-Cut auf „3 Personen Daumen hoch"** (Zusteiger `F9615661-…1429`) liegt
   auf Miserlous erstem Downbeat (`src ≈ 2,078 s`). Der Pommes-Schwenk füllt 181,45–183,53.
   Ab hier alle Cuts auf dem Miserlou-Beat-Grid (Track-Zeit = Timeline − 181,45).
3. **377,38 — HARTER Cut Miserlou → Where Is My Mind.** Der Gurken-Block sitzt in den
   letzten ~4 s von Miserlou; auf 377,38 bricht die Musik ab, es beginnt die Schwarzblende,
   und aus deren Mitte steigt WIMM (`src_in 17,0`) ein. Fade-out 418,38–422,38 — Musik ist
   **aus**, bevor `JGA_OUTRO.png` steht.

**Loop-Nähte** der Miserlou-Datei bei Timeline **~284,7 s** und **~344,7 s**. Beide sind im
Beat-Sheet bewusst mit einem **normalen Beat-Cut** überdeckt (284,60 = Cut 1611→1619;
344,50 = Cut 1637→1638). Dort **kein** Hard-Break, keine Stille, kein Schwarzbild.

## Stil-Entwicklung über den Film (aus `arc` / `music_energy_curve: build_drop_calm`)

| Abschnitt | Anteil | Schnittrhythmus | Ken Burns (§0.4) | Energie | FX | Text (§0.6) |
|---|---|---|---|---|---|---|
| Intro | 1,3 % | Standbild + 2 weiche Blenden | keine | 0 | keine | Titel (im PNG) |
| AKT 1 früh (A1.1–A1.4) | 11,7 % | 3,0–4,2 s | **ruhig, Richtung je Clip wechselnd**, jedes 3. Bild ganz ohne | warm anlaufend | keine | Poppins Bold, schräg, unten rechts, klein |
| AKT 1 Mitte (A1.5–A1.8) | 19,7 % | 2,8–3,6 s | leichtes Ziehen, Pan L→R / R→L im Wechsel, gelegentlich **raus**zoomen | steigend | **genau 1 Akzent (1390)** | Poppins, randständig |
| AKT 1 spät (A1.9–A1.12) | 10,4 % | 2,2–3,6 s, Video 6,5 s | knapper, Hochkant nur minimal (Motiv nie wegzoomen) | Verdichtung zum Cut | keine | 3-Zeiler auf 1406 |
| AKT 2 Aufbau (B0–B3) | 11,0 % | **1,4–2,6 s** Beat-Cuts | fast keine; wenn, dann kurzer Push | Drop, sofort oben | Neon-FX, Akzent | Bangers, groß, schräg, Rand |
| AKT 2 Rooftop (B4–B7) | 13,4 % | 1,0–2,6 s, atmet auf Sonnenuntergang kurz durch | sehr knapp, Richtung wechselnd | golden → blau, Plateau | Werbe-Look 1544, Kronen 1707/1706 | Gag-Texte, unten li/re |
| AKT 2 Karaoke (B8–B10) | 16,5 % | **0,8–2,2 s** + lange Video-Blöcke | keine (Video trägt) | **Höhepunkt**, Cast-Intro als Zäsur | Cast-SFX + `color_pop` ×9, Speedlines | Namen unten li/re, schräg |
| AKT 2 Abgang (B11–B13) | 5,5 % | 1,4–3,3 s, wird schwerer | leichtes langsames Rein | abfallend, skurril | dezent | Gurken-Texte |
| Aftermath | 10,5 % | **4,6–6,0 s**, nahezu statisch | ganz ohne oder minimalst | Absturz, leer | nur „Where is my mind?" | 1 Zeile |
| Schluss | 1,4 % | Cross-Fade → Standbild → Schwarz | keine | Stille | keine | 6 Danke-Zeilen, gestaffelt |

Legende: `[M]` = must · `[N]` = nice · `[O]` = ok/Füller. Dauern sind Richtwerte für den
`timeline-builder`; die **Kapitelsummen sind bindend**, weil sie an den Musik-Ankern hängen.
`fit: blur` = Hochkant → Blur-Extend (§0.5), Motiv in voller Höhe, **nicht** überskalieren.

---

## INTRO — 0:00,0–0:05,5 (5,5 s)

| TC | Inhalt | Dauer |
|---|---|---|
| 0:00,0 | **Schwarz** (`transition_in: black`), CL Theme setzt leise ein (`fade_in_s: 2`) | 0,8 |
| 0:00,8 | weiche, **gestreckte** Blende in `design/assets/img/JGA_INTRO.png` — Titel „Micha im Delirium" / „JGA · Brüssel 2026" sind im PNG enthalten, kein Zusatztext | 3,5 |
| 0:04,3 | **kurze** Schwarzblende raus (Runde-1-Kritik: war zu lang) | 1,2 |

Kein Cold Open. Danach direkt Akt 1. Ken Burns: **keins** auf dem Standbild.

---

# AKT 1 — „Gediegen" · 0:05,5–3:01,45 (175,95 s Bild, Musik 0,00–181,45)

Champions League Theme trägt. Warm, langsam. **Ken Burns pro Clip variieren** (§0.4):
Richtung durchwechseln, mindestens jedes dritte Bild **ganz ohne** Bewegung stehen lassen.
Text: Poppins SemiBold/Bold, **schräg**, Schatten, **am Rand** (bevorzugt unten rechts),
Buchstaben einzeln rein, **weg bevor der Fade beginnt**.
**FX: genau ein einziger Akzent im ganzen Akt — Sticker am Pappbären (1390).**
(Runde 1 hatte die Sprechblase auf 1381; 1381 ist in Runde 2 gestrichen, der Akzent wandert.)

> **Dichte:** 55 Muss-Assets in 175,95 s → Basis-Standzeit **3,0–3,2 s**, Hero-Shots 4,0 s.
> Fenster aus `brief.yaml` (3,5–6 s) wird unterschritten — siehe „Offene Konflikte" #1.

## A1.1 Anreise & Ankunft — 0:05,5–0:19,1 (13,6 s)

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 1 | **IMG_4734** `[M]` | 4,0 | allererster Shot, Abholung zu Hause. `Text: „Let's go"` — unten rechts, groß, bold, schräg, Schatten; „Let's" und „go" **nacheinander** rein, vor dem Fade weg. Ken Burns: langsam **raus**. |
| 2 | **`1646D950-…777E.jpg`** `[M]` | 3,2 | Grimassen im Auto. **Zwang: direkt nach 4734.** Ken Burns: Pan L→R. |
| 3 | **IMG_1252** `[M]` | 3,0 | Wohnzimmer/Couch der Ferienwohnung — **vorgezogen** (round2 §1: „erst das Bild danach"). Ken Burns: **keins**. |
| 4 | **IMG_1699** `[M]` | 3,4 | Hagi, helle Küche, „Daumen hoch" — **nach hinten geschoben** (war ~0:14). Ken Burns: leicht rein. |

## A1.2 Unterkunft Freitag — 0:19,1–0:31,9 (12,8 s)

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 5 | **IMG_1253** `[M]` | 3,0 | Mann im rosa Hoodie in der Küche. KB: Pan R→L. |
| 6 | **IMG_1256** `[M]` | 3,2 | Schlafzimmer — **nur dieses**. (IMG_1257 „nur das Bett" ist raus, round2 §1.) KB: keins. |
| 7 | **IMG_1262** `[M]` | 3,2 | Treppenhaus von oben — bleibt (ausdrücklich gelobt). KB: langsam oben→unten. |
| 8 | **IMG_1281** `[M]` | 3,4 | sechs Männer im Kreis von oben. **`fit: blur`** — im alten Preview überskaliert, halbe Gesichter weg (round2 §1, ~0:33). KB: minimal. |

**Nur EIN Haus-Innenbild-Paar** (round2: „das zweite Haus-Bild ist zu viel"): IMG_1265
(Wohn-Essbereich) ist gestrichen, 1252 trägt den Raum.

## A1.3 Pizza-Abend — 0:31,9–0:45,5 (13,6 s)

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 9 | **IMG_1309** `[M]` | 4,0 | Uber-Eats-Fahrer, unscharfe Nacht. **`fit: blur`** (Hochkant, halber Kopf weg). `Text: „Der Mann des Abends: Süleman Pizza-Star"` — zweizeilig umgebrochen („Der Mann des Abends:" / „Süleman Pizza-Star"), unten links, animiert. Schreibweise **„Süleman"**. KB: keins (Text braucht Ruhe). |
| 10 | **IMG_1310** `[M]` | 3,0 | Pizzakartons-Stapel. **`fit: blur`**. KB: leicht rein. |
| 11 | **IMG_1312** `[M]` | 3,2 | Pizza-Nahaufnahme. **`fit: blur`**, Start-Box etwas **weiter** (rauszoomen), Motiv sitzt sonst zu nah. |
| 12 | **IMG_1264** `[M]` | 3,4 | Nachtaufnahme Fensterfront — schließt den Abend. Weicher Fade auf das Frühstück. KB: sehr langsam rein. |

## A1.4 Samstag — Frühstück & Aufbruch — 0:45,5–0:55,7 (10,2 s)

**Reihenfolge getauscht** (round2 §1: „0:56 zuerst, dann 0:53").

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 13 | **IMG_1321** `[M]` | 3,4 | Frühstück am Esstisch. KB: Pan L→R. |
| 14 | **IMG_1325** `[M]` | 3,4 | Gruppe auf dem Bürgersteig — **vorgezogen** (Frühstücksstart/Aufbruch). KB: keins. |
| 15 | **IMG_1323** `[M]` | 3,4 | pinke Café-Front „Marie" — **danach**. KB: leicht rein. |

## A1.5 Stadtbummel / Mont des Arts — 0:55,7–1:18,1 (22,4 s)

Erste Verdichtung; Reit-/Pferde- und Architekturbilder bleiben (ausdrücklich gelobt).

**1328** `[M]` 3,2 Straßenbahn + Fassaden (KB Pan R→L) → **1331** `[M]` 3,0 bärtiges Selfie
(KB keins) → **4763** `[M]` **4,0 Hero** fünf Männer Arm in Arm am Mont des Arts (KB langsam
raus) → **1340** `[M]` 3,2 formaler Garten Kunstberg (KB unten→oben) → **1338** `[M]` 3,2
SW-Wandbild Fabelfigur (KB langsam rein) → **1341** `[M]` 3,0 Parkpromenade Platanen
(KB keins) → **4773** `[M]` 2,8 Parkweg mit Schattenlicht (KB Pan L→R).

## A1.6 Einkaufsstraße & Galeries — 1:18,1–1:30,5 (12,4 s)

**1343** `[M]` 3,2 Gruppe mit Rucksäcken (KB keins) → **1344** `[M]` 3,0 Waffelgeschäft
„Gaufre de Bruxelles" (KB rein) → **1347** `[M]` 3,2 Galeries Royales innen (KB oben→unten)
→ **4814** `[M]` 3,0 Gruppe bei blauem Himmel Richtung Innenstadt (KB keins).
**1385 (2. Galeries-Perspektive) steht bewusst erst in A1.7.**

## A1.7 Grand Place / Belgian Beer Weekend — 1:30,5–1:55,7 (25,2 s)

Zwischenhöhepunkt von Akt 1.

**1356** `[M]` 3,2 gotischer Rathausturm (KB unten→oben) → **1359** `[M]` 2,8 Hopfendolden
(KB keins) → **1360** `[M]` 3,2 Zunfthäuser (KB Pan L→R) → **1362** `[M]` 3,0 Lederhelme /
Fliegerbrillen am Stand (KB keins) → **1379** `[M]` 3,6 Banner „Belgian Beer Weekend".
`Text: „~250 Biere"` — bekritzelt/handgemalt-dynamisch, **unten rechts**, animiert, vor dem
Fade weg → **1376** `[M]` 2,8 barockes Zunfthaus-Detail (KB rein) → **1358** `[M]` 3,2 Blick
über die Grand Place (KB Pan R→L) → **1385** `[M]` 3,4 Galeries innen, 2. Perspektive
(KB raus).

**Gestrichen hier (round2 §1):** **1381** (Bier-Logo belgische Fahne) — damit entfällt auch
die Sprechblase „Design Award 2026"; der einzige Akt-1-FX-Akzent wandert auf **1390**.
**1352** (Kranbild / „Architektur von oben, zweite Version", ~1:50/~1:56) — raus.
**Nicht doppeln:** 1356 und 1358 stehen 6 Bilder auseinander — Reihenfolge nicht umstellen.

## A1.8 Waffeln & Schokolade — 1:55,7–2:20,5 (24,8 s)

Waffel-Bilder **von oben** bevorzugt (round2 §1), Schoko-Block ausgedünnt.

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 35 | **IMG_1387** `[M]` | 3,2 | Waffel-Gruppentisch **von oben**. KB: langsam raus. |
| 36 | **IMG_8320** `[M]` | 3,4 | Aufsicht Tisch voller Waffeln, „alle mit Handy". KB: Pan L→R. |
| 37 | **IMG_1389** `[M]` | 3,0 | Gruppen-Selfie, leere Teller. KB: keins. |
| 38 | **IMG_1390** `[M]` | 3,2 | großer Pappbär-Aufsteller. **`fit: blur`** (Hochkant, halber Kopf). **`FX:` kleiner Sticker — der EINE erlaubte Akt-1-Akzent.** KB: minimal. |
| 39 | **IMG_1392** `[M]` | 3,0 | zwei Männer beugen sich in die Pralinen-Boutique. KB: rein. |
| 40 | **IMG_4790** `[M]` | 3,0 | Schokolade kaufen. KB: keins. |
| 41 | **IMG_4793** `[M]` | 2,8 | Becher Schokomousse mit Erdbeeren. **`fit: blur`**. KB: minimal rein. |
| 42 | **IMG_1397** `[M]` | 3,2 | reich garnierte Waffelauslage. KB: Pan R→L. |

**Gestrichen (Schoko ausdünnen, round2 §1):** **1391** (Pralinen-Vitrine), **1393**
(Marcolini-Schachtel, = „~2:20 raus"), **1395** (MOV Praliniere — round2: „Schoko-Video muss
nicht zwingend rein"; damit entfällt auch das Runde-1-Duck-Fenster ersatzlos).
**1386** (Waffel-Nahaufnahme **von vorn**) raus — round2 bevorzugt die Aufsicht (1387/8320).

## A1.9 Duck Store / Manneken Pis / Genuss — 2:20,5–2:40,0 (19,5 s)

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 43 | **IMG_1399** `[M]` | 3,0 | „Brussels Duck Store"-Schild. **`fit: blur`** (Hochkant). KB: keins. |
| 44 | **IMG_1401** `[M]` | 3,2 | weiße Manneken-Pis-Nachbildung im Schaufenster. **`fit: blur`**. KB: langsam rein, Figur **nicht** wegzoomen. |
| 45 | **IMG_1403** `[M]` | 3,2 | Hand hält Schoko-Waffel am Stiel. `Text: „Präsente für den Junggesellen"` — unten links, animiert, schräg. KB: keins. |
| 46 | **IMG_1404** `[M]` (MOV) | 6,5 | **Cut ~26,5–33,0 s** — rein kurz vor dem Biss, Biss bei ~30, raus bei ~33. (Runde 1 hatte 10 s; für die neue Länge gekürzt.) |
| 47 | **IMG_1406** `[M]` | 3,6 | Still: genüsslich reinbeißen. `Text:` **dreizeilig** „Ein bisschen / genießt er es / ja schon", **links oben**, coole Schrift, Buchstaben einzeln rein, komplett weg vor dem Fade. KB: keins. |

**Manneken-Pis-Serie aufgelöst:** 1409/1410/1411 sind **nicht** eingeplant (Zeit; 1409/1411
`nice`, 1410 `nice`). Damit gibt es keine Wiederholung derselben Figur. Nachrück-Priorität
bei freier Zeit: **1409** (mit `fit: blur`), frühestens 3 Bilder nach 1401.

## A1.10 Architektur & Spiegelungen — 2:40,0–2:50,0 (10,0 s)

**1416** `[M]` 3,0 steiler Blick in die Straßenschlucht („V wie Berge", KB unten→oben) →
**1420** `[M]` 3,0 Eckgebäude mit Kuppelturm (KB keins) → **1423** `[M]` **4,0 Hero** —
Thomas in Grau mit Kapuze über Kopfsteinpflaster, „ultimatives Muss-Bild". `Text:` etwas
Lustiges zur „Kunstfigur" (party-fx formuliert) — klein, **unten rechts**, animiert.
KB: sehr langsam raus.

## A1.11 MOK Coffee — 2:50,0–2:59,2 (9,2 s)

Letztes Durchatmen. Auswahl ausdrücklich gelobt, unverändert.

**4813** `[M]` 3,0 Kaffee-Verkostung auf der Terrasse (KB Pan L→R) → **1430** `[M]` 3,0
Männerrunde am runden Außentisch (KB keins) → **1435** `[M]` 3,2 Schaufenster „100 Best
Coffee Shops" — **muss** (round2 §1). KB: langsam rein.

**IMG_1440** (Gruppe an den Bars entlang) ist im Index `ok` → für die neue Länge gestrichen.

## A1.12 Pommes → MUSIKWECHSEL — 2:59,2–3:03,5 (4,33 s)

Hier endet das CL Theme **hart bei 181,45 s** — mitten im Pommes-Schwenk, ohne Ausblendung.

| TC | Asset | Dauer | Regie |
|---|---|---|---|
| 2:59,2 | **IMG_1444** `[M]` | 2,2 | kopfüber gedrehter Blick auf die Frietland-Terrasse. **Zwang: vor 1443.** KB: keins. |
| 3:01,4 | **IMG_1443** `[M]` | 2,13 | zwei Pommes-Tüten mit Saucen — **der Pommes-Schwenk**. Läuft über den Musikschnitt (181,45) hinweg bis **183,53**, wo der Bild-Cut auf den Miserlou-Downbeat sitzt. KB: langsamer Pan, über den Musikwechsel **durchlaufen** lassen. |

---

# MUSIKWECHSEL — 181,45 s (HART) · Bild-Sync 183,53 s

CL Theme endet ohne Ausblendung. **Kein Crossfade.** Miserlou (loop-196) `src_in 0`,
`tl_in 181,45`. Der erste Downbeat nach dem Einsatz (`src ≈ 2,078 s`) liegt auf
**183,53 s** — dort der Bild-Cut auf das Zusteiger-Foto. Ab hier alle Cuts aufs Beat-Grid.

---

# AKT 2 — „Eskalation" · 3:03,5–6:17,4 (193,85 s Bild, Musik 181,45–377,38)

Beat-Cuts **0,8–2,6 s** (round2 §0.8: deutlich schneller als das alte Preview, aber nicht
1-Frame-hektisch). Ken Burns: fast keins — wenn, dann ein knapper Push, Richtung wechselnd.
Text: **Bangers**, groß, bold, **schräg**, Schatten, Buchstaben einzeln rein, **unten links
oder unten rechts**, nie über Gesichtern, **weg vor dem Fade**. Comic-FX aktiv, als Akzent.
**Speed-Ramps** (§0.7) an genau drei Clips: **1621**, **1635**, **1637**.
**Nie Video an Video** — immer Fotos dazwischen. **Kein Ducking, nirgends.**

## B0 Crew-Update (Zusteiger) — 3:03,5–3:08,0 (4,47 s)

| TC | Asset | Dauer | Regie |
|---|---|---|---|
| 3:03,5 | **`F9615661-…1429.jpg`** `[M]` | 2,2 | drei Männer, Selfie in der sonnigen Fußgängerzone — **der Cut hier sitzt exakt auf dem Miserlou-Downbeat (183,53)**. `Text:` „Crew-Update" / „Die verlorenen Söhne stoßen dazu" — unten links, animiert (party-fx finalisiert). Hochkant prüfen → ggf. **`fit: blur`**. |
| 3:05,7 | **IMG_4817** `[M]` | 2,27 | enge Zugangsgasse zur Bécasse — **jetzt der Einstieg in die Kneipe**, weil das Eingangsbild gestrichen ist. **`fit: blur`** (Hochkant). |

**Gestrichen:** **IMG_1445** (Eingang à la Bécasse) — round2 §3: „kein schönes Bild, raus,
stattdessen gleich das Bild danach". Das ist ein `must`; siehe „Offene Konflikte" #2.
Damit entfällt auch der Runde-1-Zwang „1445 → 4817"; 4817 trägt den Einstieg allein.
Der Block ist gegenüber Runde 1 **ausgedünnt** (round2 §2: „danach zu viele Bilder").

## B1 Erste Kneipe (à la Bécasse) — 3:08,0–3:22,4 (14,4 s)

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 1 | **IMG_1448** `[M]` | 2,0 | Innenraum traditionelles Bierkafé — die ruhige Kneipe. |
| 2 | **IMG_1449** `[O]` | 1,6 | belgische Bierkarte (blond/braun/Trappist) — der einzige `ok`-Shot im Film, trägt den Rhythmus in die Tränke-Reihe. |
| 3 | **IMG_1451** `[M]` | 1,6 | Kwak-Bier im Holzständer — Cut auf den Beat. |
| 4 | **IMG_1452** `[M]` | 1,4 | Mann hält Steinzeugkrug. |
| 5 | **IMG_1453** `[M]` | 1,4 | Mann schenkt aus dem Krug ein. |
| 6 | **IMG_1454** `[M]` | 1,6 | Krug + Gläser, „vollgeschüttet". |
| 7 | **IMG_8337** `[M]` | 1,4 | Nah-Selfie, Zunge raus. **Muss bleiben, aber um 90° gedreht** (round2 §3, ~3:47: „90° falsch gedreht"). Danach ggf. **`fit: blur`** prüfen. |
| 8 | **IMG_8648** `[M]` | 2,0 | Gruppen-Selfie um den langen Holztisch — „wo das Ganze losgeht". |
| 9 | **IMG_1455** `[M]` | 1,4 | Emailleschild „Timmermans" (Lambic). Round2 stuft auf `kann` → bleibt **kurz** drin, **ohne** den Runde-1-„Witte/Nebengewerbe"-Wortwitz (Text kostet Standzeit, die es hier nicht gibt). **Zwang: nach dem Laden.** |

## B2 Delirium / Bierverkostung — 3:22,4–3:40,4 (18,0 s)

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 1 | **IMG_1460** `[M]` (MOV) | 3,4 | Michas „wahnsinniges Lachen". **Anfang 1–2 s wegschneiden, direkt aufs Lächeln rein** (round2 §3). **O-Ton-Clip `gain_db: -12` unter ungedämpfter Musik, kein Ducking**, 0,3 s Ein-/Ausblende am O-Ton-Clip. |
| 2 | **IMG_1461** `[M]` | 1,6 | Bierverkostung, Reihe kleiner Gläser („Trinken/Cocktail gut"). |
| 3 | **IMG_1463** `[M]` | 1,6 | Verkostungsbrett mit 9 Gläsern. |
| 4 | **IMG_4824** `[M]` | 1,8 | Delirium-Bar innen mit großer Kreidetafel. |
| 5 | **IMG_2636** `[M]` | 1,4 | handgeschriebene Kreidetafel Craft-Bier-Liste. |
| 6 | **IMG_1464** `[M]` | 2,2 | pinkes Delirium-Neon mit Elefant. **`FX:` „Delirium" als zittrig nachgemalte Leuchtschrift** (round2 §5). |
| 7 | **IMG_1465** `[M]` | 1,4 | grinsender Mann, blauer Haarreif, Daumen hoch. |
| 8 | **IMG_1466** `[M]` | 1,4 | zwei Männer, Tisch voller leerer Gläser. |
| 9 | **IMG_1473** `[M]` | 1,4 | Mann mit fast leerem Glas. |
| 10 | **IMG_1475** `[M]` | 1,8 | extreme Nahaufnahme Delirium-Glas. **`fit: blur`** — „muss zur Höhe / voll zu sehen sein" (round2 §3). |

**Gestrichen:** **1459** `[N]` (Leucht-Haarreif-Selfie, = „~3:51 raus") · **1474** `[O]`
(Kriek-Nahaufnahme, = „~4:11 raus"). Das Runde-1-Duck-Fenster an dieser Stelle entfällt.
**Nicht doppeln:** 2636 hier, 2644 erst im Aftermath — 2642 ist gar nicht eingeplant.

## B3 Kreisbild / Weg zur Rooftop-Bar — 3:40,4–3:45,2 (4,8 s)

**1497** `[M]` 2,4 Froschperspektive aus der Kreismitte, ganze Gruppe beugt sich runter →
**1476** `[M]` 2,4 Delirium-Gasse voller Bar-Schilder.
**Gestrichen:** 1499 `[N]`, 1478 `[O]` (passen nicht zum fetzigen Schnitt).

## B4 Rooftop Bar 58 — Aufstieg & goldene Stunde — 3:45,2–3:59,2 (14,0 s)

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 1 | **IMG_1500** `[M]` | 2,6 | Aufzug-Selfie vier Männer. `Text:` **„Rooftop Bar 58 — wir kommen"**, **links oben** (round2 §3), geile Schrift, cooler Auftritt, Farben, **nicht** über die Gesichter. |
| 2 | **IMG_4829** `[M]` | 1,8 | beleuchtete Glühbirnen-Ziffern „58" — direkt nach dem Hochfahren. |
| 3 | **IMG_1501** `[M]` | 1,6 | Dachterrassen-Bar mit Holzdeck. |
| 4 | **IMG_1502** `[M]` | 1,6 | Dachpanorama Abendlicht. |
| 5 | **IMG_1509** `[M]` | 1,8 | Kirchturm im warmen Licht. **Zwang: früh in der Sequenz.** |
| 6 | **IMG_1503** `[M]` | 1,8 | Gruppe auf der Terrasse mit Palme/Lichterketten. |
| 7 | **IMG_1505** `[M]` | 1,6 | Blick über die Dächer mit Kirchturm. |
| 8 | **IMG_1511** `[M]` | 1,2 | Selfie drei Männer auf der Dachterrasse. |

**Sonnenuntergänge stark ausgedünnt** (round2 §3): 1506 `[N]`, 2642 `[O]`, 1519 `[O]`,
8649/8652 `[N]`, 1549 `[N]`, 1548 `[N]`, 8654 `[N]`, 1540/1541 `[O]`, 4839/4840 `[N]` sind
**nicht** eingeplant.

## B5 Rooftop — Sonnenuntergang & Corona — 3:59,2–4:13,6 (14,4 s)

Der feurige Sonnenuntergang sitzt jetzt **in der Mitte** der Rooftop-Sequenz (round2 §3
überschreibt den Runde-1-Zwang „1508 spät").

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 1 | **IMG_1508** `[M]` | 2,6 | feuriger Sonnenuntergang — **Mitte der Rooftop-Sequenz**, nicht ans Ende, nicht neben Karaoke. |
| 2 | **IMG_1524** `[M]` | 2,4 | Untersicht in den Kreis, alle stoßen mit Corona an — **muss**, Cut auf einen kräftigen Miserlou-Akzent. |
| 3 | **IMG_1531** `[N]` | 1,2 | zweites Corona-Bild, Christoph wieder da — `kann`, kurzer Blitz. |
| 4 | **IMG_1543** `[M]` | 2,2 | Zunge raus neben Corona. `Text:` **„Stay hydrated"** oben rechts, **zwei Elemente** („stay" + „hydrated") gegeneinander laufend, halb übereinander, dann langsam ausfaden — Werbecharakter. |
| 5 | **IMG_1514** `[M]` | 2,4 | ganze Gruppe als Breitbild-Reihe. `Text:` **„Wo ist Christoph???"** — **unten rechts**, kleiner, nette Schrift, **drei** Fragezeichen, **nicht mittig**. |
| 6 | **IMG_1515** `[N]` | 1,6 | Hochkant-Gruppenfoto (alle drauf). **`fit: blur`** — nicht mehr überskalieren. |
| 7 | **IMG_1544** `[N]` | 2,0 | Hand hält Corona Extra gegen den Sonnenuntergang. **`FX:` Werbe-Look**, Flüssigkeitslinie = Horizont. |

## B6 Rooftop — blaue Stunde & Abgang — 4:13,6–4:28,4 (14,8 s)

Farbwechsel golden → blau. **Ab hier keine Rücksprünge in die goldene Stunde**, und
**keine Karaoke-Bilder** (round2 §3: Rooftop ↔ Karaoke hart trennen).

**1551** `[N]` 1,4 Gruppe dicht gedrängt, blaue Stunde → **1554** `[M]` 1,8 Gruppe an der
Brüstung → **1555** `[M]` 1,8 blaue Stunde → **1557** `[M]` 1,8 Froschperspektive drei Männer
im Kreis → **1707** `[M]` 2,0 Hagi-Selfie zwei Männer, Dachterrasse (`FX:` Herzchen + goldene
Kronen) → **1588** `[N]` 1,4 Untersicht mit blau beleuchteter Gebäudekante („geiler Style") →
**1518** `[M]` 2,2 feurig-oranger Sonnenuntergang mit Silhouette → **1556** `[M]` 2,4
nächtliche Dachterrasse, blau angestrahlte Fassade.
**Zwang: 1518 direkt vor 1556.** 1556 schließt die Rooftop-Sequenz.
**Gestrichen:** das „~5:25"-Bild (zu dunkel) und der „~4:48"-Videoschnipsel — kein `muss`.

## B7 Abgang & Burger-Stop — 4:28,4–4:42,8 (14,4 s)

Der Burger-Stop steht jetzt **vor** der Karaoke-Bar (round2 §3) — er bringt die Zeit rüber.

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 1 | **IMG_1706** `[M]` | 2,4 | „vor der Tür", nachdem sie runtergegangen sind. **Umgezogen aus dem Aftermath** (round2 §4: „super wichtiges Bild, aber nicht in den Abspann — gehört zur Rooftop-Sequenz"). `FX:` Herzchen + goldene Kronen. |
| 2 | **IMG_1589** `[M]` | 2,0 | Prunkfassade „More than a beer museum" bei Nacht. |
| 3 | **IMG_1592** `[N]` | 1,0 | Neonschild „Down Town", Spiegelung — schneller Blitz. |
| 4 | **IMG_1594** `[M]` | 1,6 | Burger im Körbchen + Bier. |
| 5 | **IMG_1596** `[M]` | 1,6 | Burger-Nahaufnahme. |
| 6 | **IMG_1597** `[M]` | 2,0 | Gruppe am Stehtisch, Backsteinwand — „unser Burger-Stop". |
| 7 | **IMG_1598** `[M]` | 2,4 | Nacht-Selfie vor dem Juwelier-Schaufenster. `Text:` **„wolle Token kaufen ???"** — „wolle" klein, **„Token" groß**, „kaufen" klein, drei Fragezeichen, animiert, **unten links** (nicht über die Köpfe). **Skalierung prüfen** (wirkte im Preview komisch) → ggf. `fit: blur`. |
| 8 | **IMG_1591** `[N]` | 1,4 | O'Reilly's Irish Pub bei Nacht — Weg zur Karaoke-Bar. |

> **Loop-Naht 1 (Timeline ~284,7 s)** fällt in den Anfang von B8 und wird vom regulären
> Beat-Cut bei **284,60** (1611 → 1619) restlos überdeckt. Keine Stille, kein Hard-Break.

## B8 Red Karaoke-Bar I — Ankunft & Aufheizen — 4:42,8–5:06,8 (24,0 s)

| # | Asset | Dauer | Regie |
|---|---|---|---|
| 1 | **IMG_1611** `[M]` | 1,8 | rotes Neon „KARAOKE" — **Einleitungsbild** der Karaoke-Sektion (round2 §3). |
| 2 | **IMG_1619** `[M]` | 1,6 | rote Leuchtschrift „La Pod". *(Cut bei 284,60 deckt die Loop-Naht.)* |
| 3 | **IMG_1608** `[M]` | 1,8 | grinsender Mann stößt an, „der Tequila ist da". **Kein Ducking.** |
| 4 | **IMG_1610** `[N]` (MOV) | 2,6 | ab **~28 s** („Was machst du, was machst du"), Rest weg. Nur Musik. |
| 5 | **IMG_1613** `[M]` (MOV) | **9,0** | ab **~10 s**, **ganze Szene zusammenhalten, nicht zerschneiden**; das **„Füßchen" bei ~21 s muss drin sein** → Fenster ~10,0–19,0 s so legen, dass ~21 s enthalten ist; falls das nicht aufgeht, Fenster nach hinten schieben (Priorität: Füßchen). **O-Ton-Clip `gain_db: -14`, kein Ducking.** („~6:00 Video mit Knutscher: perfekt, nur etwas kürzen" — von 14 auf 9 s.) |
| 6 | **IMG_1617** `[M]` | 1,6 | lachender Mann auf dem Barhocker. |
| 7 | **IMG_1620** `[M]` | 1,6 | Porträt bärtiger Mann mit LED-Haarreif. |
| 8 | **IMG_1622** `[M]` | 1,6 | Männergruppe an der Bartheke, blaues Licht. |
| 9 | **IMG_1614** `[N]` | 1,4 | vier Männer Porträt — Christians Wunschbild („ich bin selten drauf"). |
| 10 | **IMG_8656.HEIC** `[N]` | 1,0 | Karaoke-Screen „I Want It That Way" — schneller Blitz vor dem Cast-Intro. |

**Gestrichen (round2 §3):** „~6:11 I wandered that way" **raus**, „~6:12 Mini-Video"
(**8656.MP4**) **raus**. 1607/1615/1616 `[O]` nicht eingeplant.

## B9 CAST-INTRO — 5:06,8–5:15,5 (8,7 s) ⭐ eigener Beat

Mitten in der Red-Bar-Sequenz. Neun Sonnenbrillen-**Standbilder**, Cuts hart auf das
Miserlou-Beat-Grid. **Name unten links / unten rechts** (alternierend), **schräg**, Bangers,
**einzelne Buchstaben nacheinander rein**, und **komplett ausgeblendet, bevor der Fade zum
nächsten Foto beginnt** — nicht mehr Mitte-Mitte über den Gesichtern wie im alten Preview.
**`color_pop` auf ALLEN 9 Cuts** + je 1 Whoosh (−6 dB, Cut −0,18 s) und 1 Stamp (0 dB, exakt
auf dem Cut) aus `music/sfx/`.

| # | Person | Foto | Dauer | Position |
|---|---|---|---|---|
| 1 | Witte | IMG_1624 | 0,9 | unten links |
| 2 | Christoph | IMG_1625 | 0,9 | unten rechts |
| 3 | Matti | IMG_1627 | 0,9 | unten links |
| 4 | Bartosz | IMG_1628 | 0,9 | unten rechts |
| 5 | Hagi | IMG_1629 | 0,9 | unten links |
| 6 | Bernhard | IMG_1630 | 0,9 | unten rechts |
| 7 | André | IMG_1631 | 0,9 | unten links — Schreibweise **einmal final** festlegen (§0.9), kein Mischen |
| 8 | Skuub | IMG_1632 | 0,9 | unten rechts |
| 9 | **Micha** | IMG_1626 | **1,5** | unten links, Stempel „Micha im Delirium", Sonderblau `#4fd8ff`, `sfx-cast-stamp-micha.wav` (−1 dB) |

## B10 Red Bar II — HÖHEPUNKT (Tanz / Gesang / Tequila) — 5:15,5–5:53,7 (38,2 s)

Das energetische Zentrum. Videolastig, dazwischen konsequent Fotos. **Drei Speed-Ramps.**

| # | Asset | Fenster / Dauer | Regie |
|---|---|---|---|
| 1 | **IMG_1621** `[M]` Teil A | ~1–4,4 s → **3,4** | „Die Lichter gehen an", Grimassen. **Speed-Ramp**: ein paar Frames schnell auf die Grimasse zu, dort normal weiter. `FX:` Speedlines. |
| 2 | **IMG_1636** `[M]` | 1,2 | Gruppenfoto der Runde, blau-violett. |
| 3 | **IMG_1621** Teil B | ~20–22,2 s → **2,2** | Arme hoch. |
| 4 | **IMG_1634** `[M]` | 1,8 | Gruppe dicht in blau-rotem Neon. `Text:` **„Gehen hier etwa schon die Lampen aus?"** — **unten rechts**, mit Abstand zum Rand, **nicht über Gesichter**. |
| 5 | **IMG_1621** Teil C | ~29 s–Ende → **2,0** | „Micha im Delirium"-Lampen-Szene — bleibt wie sie ist (ausdrücklich gelobt). |
| 6 | **IMG_1623** `[M]` (MOV) | ~0–3,0 s → **3,0** | „der mit dem Video reinkommt". `Text:` **unten rechts** „Natürlich … (noch nicht)" — „noch nicht" in Klammern. |
| 7 | **IMG_1639** `[M]` | 1,2 | Dart, „Arm hoch" — kurz. |
| 8 | **IMG_1635** `[M]` Teil A | ~0–2,6 s → **2,6** | Dance-Move. **Speed-Ramp** + `FX:` Farb-Pop / Speedlines auf den Beat. |
| 9 | **IMG_8655** `[N]` | 1,0 | Bar-Bild, Blitz zwischen die Videos. |
| 10 | **IMG_1635** Teil B | ~8–10,2 s → **2,2** | runtergehen. |
| 11 | **IMG_1640** `[M]` | 1,4 | rote japanische Leuchtschrift — unscharf, aber „Lichter an", absolutes Muss. |
| 12 | **IMG_1637** `[M]` (MOV) | **Hauptstelle 2:22–2:29** → **7,0** | Karaoke-Gesang, „dreht sich um, laut" — die wichtigste Sekunde des Clips. **Speed-Ramp** in die Drehung hinein. **O-Ton-Clip `gain_db: -12`, kein Ducking.** Das Umdrehen auf einen Miserlou-Beat legen. *(Cut bei 344,50 deckt **Loop-Naht 2** ~344,7 s.)* |
| 13 | **IMG_1638** `[M]` (MOV) | ~0–2,2 s → **2,2** | oder ~8–9 s (Bräutigam drückt jemanden, Daumen hoch). |
| 14 | **IMG_1641** `[M]` (MOV) | ~0:24–0:26,6 → **2,6** | Bräutigam singt — gekürzt. Nur Musik (Runde-1-Duck-Fenster entfällt). |
| 15 | **IMG_4835** `[M]` (MOV) | ab **~8 s** → **4,4** | Tequila-Shot wird genommen und hochgehalten. **O-Ton-Clip `gain_db: -13`, kein Ducking.** `FX:` Farb-Pop. |

Puffer: keiner. Fällt ein Videofenster kürzer aus, zieht der `timeline-builder` die
Standzeit von **1636 / 8655 / 1639** hoch (in dieser Reihenfolge), nicht von den Musts.

## B11 Weiterziehen (Delirium Village / Dubliner) — 5:53,7–6:00,7 (7,0 s)

**1646** `[M]` 1,6 nächtlicher Kopfsteinpflaster-Platz → **1648** `[M]` 2,0 Neon „Delirium
Village" mit Elefant + Pfeil (**`fit: blur`**, Hochkant, mit Ecken/Seiten) → **1649** `[M]`
1,8 „The Dubliner" → **1650** `[M]` 1,6 zwei Männer posieren nachts. `Text:` dezent, party-fx
formuliert („Noch ahnen sie nicht, wie toll der Abend wird" o.ä.) — **unten rechts**, kurz.

## B12 Taxi — 6:00,7–6:05,5 (4,8 s)

- **IMG_1652** `[M]` 1,4 — Blick von der Rückbank über zwei Insassen zur Frontscheibe.
- **IMG_1653** `[M]` (MOV) 3,4 — Taxi-POV, **ab ~10 s** (Kamera dreht, Hände hoch).
  **Kein O-Ton-Clip, nur Musik** (Christian explizit; unter Runde 2 gilt das ohnehin überall).

## B13 Gurken & abgeschossen — Ende Akt 2 — 6:05,5–6:17,4 (11,88 s)

**Komplett neu geordnet** (round2 §3 „Taxi / abgeschossen / Gurken", Punkte 1–5). Miserlou
läuft bis **377,38** und bricht dann ab; der Block liegt in den letzten Sekunden des Tracks,
der Schwarz-Fade beginnt exakt auf dem Musikabbruch.

| TC | Asset | Dauer | Regie |
|---|---|---|---|
| 6:05,5 | **IMG_1660** `[M]` | 2,4 | Mann grinst mit Gurken vor dem offenen Kühlschrank. `Text:` **nur „WTF?"** — unten rechts, groß, animiert. |
| 6:07,9 | **IMG_1656** `[N]` | 1,8 | drei/vier Männer lümmeln lachend auf den Betten (Nachthaus 1). |
| 6:09,7 | **IMG_1658** `[M]` | 2,2 | Gruppen-Selfie von oben, schwarze Crew-Shirts (Nachthaus 2). |
| 6:11,9 | **IMG_1659** `[N]` | 2,2 | Männer in Crew-Shirts, Arme aus. `Text:` **„Ich war es nicht."** — unten rechts, Christoph-Gag. |
| 6:14,1 | **IMG_1661** `[M]` | 3,28 | zwei Männer albern am Kühlschrank, drei Gurken in der Hand. `Text:` **„Der Michael mag Gurken. / Gib mir Gurken. / Der Michael braucht Gurken."** — dreizeilig, skurril, unten links, **muss ausgeblendet sein, bevor die Schwarzblende beginnt**. Letztes Bild von Akt 2; auf **377,38** bricht Miserlou ab und die Blende startet. |

---

# AFTERMATH / OUTRO — 6:17,4–7:02,4 (45,0 s)

**377,38 — abrupter Cut in die Stille**, Schwarzblende. **Aus der Mitte der Blende** setzt
Where Is My Mind ein (`src_in 17,0`). Sehr langsam, nahezu statisch, Ken Burns nur minimal
oder gar nicht. Kein FX außer dem einen Text. Übergänge weich.

**Feste Bild-Reihenfolge (Christian diktiert, round2 §4):**

| # | Asset | TC | Dauer | Regie |
|---|---|---|---|---|
| 1 | **IMG_2644** `[M]` | 6:17,4 | 6,0 | Christoph liegt da, einer macht Daumen hoch — **in dieses Bild blenden wir rein**. `Text:` **„Where is my mind?"** — unten links, animiert, weg vor dem nächsten Fade. |
| 2 | **IMG_1665** `[M]` | 6:23,4 | 4,8 | Michael (hell, Airbnb). |
| 3 | **IMG_1666** `[M]` | 6:28,2 | 5,2 | Michael „total zerstört, total kaputt". |
| 4 | **IMG_1663** `[M]` | 6:33,4 | 5,0 | die Gruppe auf den Sofas, der neue Tag. |
| 5 | **IMG_1697** `[N]` | 6:38,4 | 4,6 | Hagi — mit Koffer/Taschen am Bordstein (Michael/Christoph, morgens). |
| 6 | **IMG_1667** `[M]` | 6:43,0 | 4,8 | jemand übergibt sich / „mir geht's gut", drückt den Bauch — **dezent**. |
| 7 | **IMG_1668** `[M]` | 6:47,8 | 4,6 | mehrere warten mit Rucksäcken auf dem Bürgersteig. |
| 8 | **`93638dac-…5F53.jpg`** `[M]` | 6:52,4 | 5,0 | Auto-Schlaf, angeschnallt. **Zwang: zuerst von beiden.** |
| 9 | **`c12b0d91-…EA4B.jpg`** `[M]` | 6:57,4 | 5,0 | Auto-Schlaf mit Nackenkissen. **Zwang: danach.** Letztes der „letzten beiden Bilder". |

**Musik-Fade-out 6:58,4–7:02,4** (`fade_out_s: 4`) liegt komplett auf EA4B. Bei 422,38 ist
es still. **Kein harter Schnitt** ans Ende — die Musik läuft aus, dann die Blende.

**Aus dem Aftermath entfernt (round2 §4):** **1664** („~8:07, zwei fast gleiche Bilder — eins
raus") · **1703** („~8:16, Bild aus der Bar, letzte Nacht — passt zeitlich nicht") ·
**1705** („~8:19/~8:20 raus") · **1706** → **umgezogen nach B7** („vor der Tür", gehört zur
Rooftop-Sequenz). 1700/1702/1704 `[N]` (Hagi) bleiben ungenutzt.

---

## SCHLUSS — 7:02,4–7:08,4 (6,02 s) · Stille

| TC | Inhalt | Dauer |
|---|---|---|
| 7:02,4 | **sauberer Cross-Fade** (1,0 s) aus EA4B in `design/assets/img/JGA_OUTRO.png` — ersetzt den im Preview als „extrem KI-wirkend" gerügten Schwarzblenden-Übergang. Kein Zwischenschwarz. | 1,0 |
| 7:03,4 | `JGA_OUTRO.png` steht **in Stille**. Textzeilen gestaffelt, animiert, **nicht über Gesichter**, jede vor der nächsten weg: „Drink responsibly" · „Danke, Jungs" · „Super Crew, tolle Erinnerung" · „Genug Käse" · „Ein unvergesslicher Abend" · **„Micha im Delirium"**. Trägt die Karte kein „Danke", danach 1,5 s schlichte credits-Karte (bestehendes SVG-Template) — dann aus dieser Standzeit abzweigen. | 3,5 |
| 7:06,9 | Blende ins **Schwarz** (`transition_out: black`). Ende bei **7:08,4 (428,4 s)**. | 1,5 |

---

# Zwangsfolgen (Stand Runde 2)

1. **4734 → …777E** ganz am Anfang — *A1.1* ✔
2. **1252 vor 1699** („Daumen hoch" nach hinten, round2 §1) — *A1.1* ✔
3. **1444 vor 1443** (Pommes), 1443 trägt den Musikschnitt — *A1.12* ✔
4. **F9615661…1429 auf dem Miserlou-Downbeat (183,53)** — *B0* ✔ *(Runde-1-Zwang „direkt vor 1445" entfällt, 1445 ist gestrichen.)*
5. **4817 als Kneipen-Einstieg** (statt 1445) — *B0* ✔
6. **1455 nach dem Laden** — *B1, letztes Bild* ✔
7. **1509 früh** (B4) / **1508 in der MITTE** der Rooftop-Sequenz (B5) — round2 §3 überschreibt „1508 spät" ✔
8. **1518 direkt vor 1556** — *B6, Sequenzende* ✔
9. **Rooftop-Block (B4–B6) und Karaoke-Block (B8–B10) hart getrennt**, dazwischen nur der Abgang + Burger-Stop (B7) — keine Rücksprünge ✔
10. **Burger-Stop vor der Karaoke-Bar** — *B7 vor B8* ✔
11. **1706 („vor der Tür") in den Rooftop-Abgang**, nicht in den Aftermath — *B7* ✔
12. **Cast-Intro in der Red-Bar, Micha zuletzt** — *B9, zwischen B8 und B10* ✔
13. **Gurken-Schluss: 1660 → 1656 → 1658 → 1659 → 1661 → Schwarz** — *B13* ✔
14. **Aftermath: 2644 → 1665 → 1666 → 1663 → 1697 → 1667 → 1668 → 5F53 → EA4B** ✔
15. **Schluss: EA4B → (Cross-Fade) → JGA_OUTRO → Schwarz** ✔

# Nicht doppeln (eingehalten)

- **1356 / 1358** (Grand Place): 6 Bilder Abstand in A1.7 — nicht umsortieren.
- **1409 / 1410 / 1411** (Manneken Pis): **keines** eingeplant → Serie aufgelöst. Nachrücken
  nur einzeln (Priorität 1409, `fit: blur`).
- **2636 / 2642 / 2644**: 2636 in B2, 2644 als Aftermath-Eröffner, **2642 gar nicht** — nie als Serie.
- **Rooftop-Sonnenuntergänge**: von 1502/1505/1506/1508/1509/1518/2642 sind nur **1502, 1505,
  1509** (B4, golden), **1508** (B5, Mitte) und **1518** (B6, Abgang) drin — 1506 und 2642 raus.
- **Haus-/Unterkunft-Innenräume**: nur 1252 + 1253 + 1256 + 1262 + 1281 (1257 und 1265 raus).
- **Waffeln**: nur die beiden Aufsichten (1387, 8320) + Auslage (1397); 1386 „von vorn" raus.
- **Schokolade**: nur 1392 + 4790 + 4793; 1391, 1393, 1395 raus.
- **Burger**: 1594 + 1596 direkt hintereinander bleiben (unterschiedliche Einstellungsgröße,
  ausdrücklich als „zwei Burger-Bilder gut" freigegeben).
- **8646.HEIC/.MP4** nicht eingeplant — Duplikat-Gefahr zu 5F53/EA4B.

# O-Ton — vier Clips, **kein Ducking**

Alle vier laufen als `type: "oton"` mit negativem `gain_db` **unter ungedämpfter Musik**.
**Keine `duck_music_db` / `duck_fade_s` irgendwo im ganzen Film.** Wenn ein O-Ton hörbar
rein-/rauskommen soll: 0,2–0,4 s `fade_in_s`/`fade_out_s` **am O-Ton-Clip selbst**.

| # | Clip | Kapitel | Fenster | `gain_db` | Zweck |
|---|---|---|---|---:|---|
| 1 | **IMG_1460** | B2 | ganzer genutzter Ausschnitt (3,4 s) | **−12** | Michas „wahnsinniges Lachen" |
| 2 | **IMG_1613** | B8 | ab ~10 s, ganze Szene (9,0 s) — „Füßchen" ~21 s **muss hörbar bleiben** | **−14** | Karaoke-Reden |
| 3 | **IMG_1637** | B10 | Hauptstelle „dreht sich um" (7,0 s) | **−12** | wichtigste O-Ton-Sekunde, auf einen Miserlou-Beat legen |
| 4 | **IMG_4835** | B10 | ab ~8 s, Tequila-Shot (4,4 s) | **−13** | Anstoß/Ruf |

- **IMG_1395** („da-da-da") ist **ganz raus** — das Bild/Video ist gestrichen, das Runde-1-
  Duck-Fenster entfällt ersatzlos.
- **IMG_1653, IMG_1621, IMG_1635, IMG_1641, IMG_1610, IMG_1623, IMG_1638** und alle übrigen
  Akt-2-Videos: **nur Musik**, O-Ton still oder sehr leise, **kein Anheben**.

# Verbotene Shots

Die **67 Dateien** aus `brief.yaml:forbidden_shots` sind **nirgends** eingeplant und dürfen
vom `timeline-builder` auch **nicht als Ersatz nachgezogen** werden, wenn ein Fenster kürzer
ausfällt. Die zwei hart gesperrten Assets (IMG_4745, IMG_8338) stehen ohnehin nicht im Pool.

---

# Report

## Kapitel-Liste

| Kapitel | TC | Dauer | must | nice | ok |
|---|---|---|---:|---:|---:|
| Intro | 0:00,0–0:05,5 | 5,50 | (Standbild) | — | — |
| A1.1 Anreise & Ankunft | 0:05,5–0:19,1 | 13,60 | 4 | 0 | 0 |
| A1.2 Unterkunft Freitag | 0:19,1–0:31,9 | 12,80 | 4 | 0 | 0 |
| A1.3 Pizza-Abend | 0:31,9–0:45,5 | 13,60 | 4 | 0 | 0 |
| A1.4 Frühstück & Aufbruch | 0:45,5–0:55,7 | 10,20 | 3 | 0 | 0 |
| A1.5 Stadtbummel / Mont des Arts | 0:55,7–1:18,1 | 22,40 | 7 | 0 | 0 |
| A1.6 Einkaufsstraße & Galeries | 1:18,1–1:30,5 | 12,40 | 4 | 0 | 0 |
| A1.7 Grand Place / Beer Weekend | 1:30,5–1:55,7 | 25,20 | 8 | 0 | 0 |
| A1.8 Waffeln & Schokolade | 1:55,7–2:20,5 | 24,80 | 8 | 0 | 0 |
| A1.9 Duck Store / Manneken / Genuss | 2:20,5–2:40,0 | 19,50 | 5 | 0 | 0 |
| A1.10 Architektur & Spiegelungen | 2:40,0–2:50,0 | 10,00 | 3 | 0 | 0 |
| A1.11 MOK Coffee | 2:50,0–2:59,2 | 9,20 | 3 | 0 | 0 |
| A1.12 Pommes → Musikwechsel | 2:59,2–3:03,5 | 4,33 | 2 | 0 | 0 |
| **Σ Intro + AKT 1 (Bild)** | **0:00,0–3:03,5** | **183,53** | **55** | **0** | **0** |
| *davon unter CL Theme* | *0:00,0–3:01,45* | *181,45* | | | |
| B0 Crew-Update (Zusteiger) | 3:03,5–3:08,0 | 4,47 | 2 | 0 | 0 |
| B1 Erste Kneipe (à la Bécasse) | 3:08,0–3:22,4 | 14,40 | 8 | 0 | 1 |
| B2 Delirium / Bierverkostung | 3:22,4–3:40,4 | 18,00 | 10 | 0 | 0 |
| B3 Kreisbild / Weg | 3:40,4–3:45,2 | 4,80 | 2 | 0 | 0 |
| B4 Rooftop — Aufstieg & golden | 3:45,2–3:59,2 | 14,00 | 8 | 0 | 0 |
| B5 Rooftop — Sonnenuntergang & Corona | 3:59,2–4:13,6 | 14,40 | 4 | 3 | 0 |
| B6 Rooftop — blaue Stunde & Abgang | 4:13,6–4:28,4 | 14,80 | 6 | 2 | 0 |
| B7 Abgang & Burger-Stop | 4:28,4–4:42,8 | 14,40 | 6 | 2 | 0 |
| B8 Red Karaoke-Bar I | 4:42,8–5:06,8 | 24,00 | 7 | 3 | 0 |
| **B9 CAST-INTRO** | 5:06,8–5:15,5 | 8,70 | 9 | 0 | 0 |
| **B10 HÖHEPUNKT (Tanz/Gesang/Tequila)** | 5:15,5–5:53,7 | 38,20 | 11 | 1 | 0 |
| B11 Weiterziehen | 5:53,7–6:00,7 | 7,00 | 4 | 0 | 0 |
| B12 Taxi | 6:00,7–6:05,5 | 4,80 | 2 | 0 | 0 |
| B13 Gurken & abgeschossen | 6:05,5–6:17,4 | 11,88 | 3 | 2 | 0 |
| **Σ AKT 2 (Bild)** | **3:03,5–6:17,4** | **193,85** | **82** | **13** | **1** |
| *Musikfenster Miserlou* | *3:01,45–6:17,4* | *195,93* | | | |
| Aftermath / Outro | 6:17,4–7:02,4 | 45,00 | 8 | 1 | 0 |
| Schluss (Danke → Schwarz, Stille) | 7:02,4–7:08,4 | 6,02 | (Standbild) | — | — |
| **GESAMT** | **0:00,0–7:08,4** | **428,40 s = 7:08,4** | **145** | **14** | **1** |

Anker-Abgleich: Intro+Akt 1 unter CL Theme **181,45 ✔** · Miserlou 181,45→377,38 = **195,93 ✔**
· WIMM 377,38→422,38 = **45,00 ✔** · Stille 422,38→428,40 = **6,02 ✔** · Gesamt **428,40 ✔**

## Bilanz

- **must: 145 / 156 untergebracht** (Akt 1: 55, Akt 2: 82 inkl. des umgezogenen 1706,
  Aftermath: 8). **11 `must` gestrichen** — jede einzelne Streichung geht auf eine
  ausdrückliche „raus"-Anweisung aus `editorial-notes-round2.md` zurück, nicht auf
  Zeitdruck allein (Liste unten).
- **nice: 14 / 50 untergebracht** (Akt 2: 13, Aftermath: 1). Akt 1 kommt in Runde 2 **ohne
  ein einziges `nice`** aus — dort ist der Takt am dünnsten.
- **ok: 1 eingeplant** (IMG_1449, Bierkarte — hält die Tränke-Reihe zusammen). Alle anderen
  `ok`-Bilder sind gestrichen, wie in §0.1 gefordert („`ok`-Bilder fallen zuerst").
- **Verbotene Shots: 0 eingeplant.**
- **Ducking: 0 Stellen.** 4 O-Ton-Clips mit negativem `gain_db`, sonst nur Musik.
- **Kürzung gegenüber Runde 1: 533,9 → 428,4 s = −105,5 s (−1:45,5).** Woher:
  Akt 1 −24,0 s (205,5 → 181,45 inkl. Intro), Akt 2 −77,6 s (271,4 → 193,85 Bild),
  Aftermath ±0 (45,0), Schluss ±0 (6,0).

### Gestrichene `must` (11) — jeweils mit Quelle

| Asset | Kapitel Runde 1 | Grund (Runde 2) |
|---|---|---|
| IMG_1257 | A1.2 | §1 „~0:28 (nur das Bett): **raus**" |
| IMG_1265 | A1.2 | §1 „Haus zeigen: das zweite Haus-Bild ist zu viel → eins reicht" |
| IMG_1352 | *(war schon in Runde 1 nicht eingeplant)* | §1 „~1:50 Kranbild: eher raus" / „~1:56 Doppelung → Kranbild raus" |
| IMG_1386 | A1.7 | §1 „Waffeln von vorn: nur noch nice/ok — das Bild von oben danach ist schöner" |
| IMG_1391 | A1.8 | §1 „Schokoladen-Bilder sind zu viele → ausdünnen" |
| IMG_1393 | A1.8 | §1 „~2:20: **raus** (nicht schön)" |
| IMG_1395 (MOV) | A1.8 | §1 „Schoko-Video (Praliniere) muss nicht zwingend rein" + §0.3 (Duck-Fenster entfällt) |
| IMG_1445 | B1 | §3 „~3:31 Eingangsbild à la Bécasse: **raus** — stattdessen gleich das Bild danach" |
| IMG_1664 | Aftermath | §4 „~8:07 zwei fast gleiche Bilder: eins **raus** (das erste)" |
| IMG_1703 | Aftermath | §4 „~8:16 Bild aus der Bar, letzte Nacht: **raus** (passt zeitlich nicht)" |
| IMG_1705 | Aftermath | §4 „~8:19 / ~8:20: **raus**" |

### Gestrichene `nice` / `ok` (Auswahl, Zeitgründe + Runde-2-Anweisung)

- **Akt 1 (`nice`, komplett):** 1322, 1348, 1353, 1381 *(§1 ausdrücklich raus)*, 1409, 1410,
  1411, 1412, 1419, 1425, 1427, 1439, 4754, 4781, 4782, 4783, 4804, 8306, 8310, 8321.
- **Akt 1 (`ok`):** 1254, 1255, 1259, 1263, 1306, 1326, 1327, 1330, 1333–1335, 1337, 1366,
  1369–1371, 1374, 1378, 1382–1384, 1396, 1398, 1400, 1402, 1407, 1413, 1415, 1421, 1436,
  1440, 4758, 4760, 4775, 8334.
- **Akt 2 (`nice`):** 1459 *(§3 „~3:51 raus")*, 1499, 1506, 1548, 1549, 1551 *(drin)*, 4839,
  4840, 8646, 8649, 8652, 8654, 8656.MP4 *(§3 „~6:12 raus")*, 1700, 1702, 1704.
- **Akt 2 (`ok`):** 1474 *(§3 „~4:11 raus")*, 1478, 1519, 1540, 1541, 1607, 1615, 1616,
  1642, 1647, 2642, 4820, 8334.

### Nachrück-Reihenfolge, falls ein Videofenster kürzer ausfällt

1. Standzeit von **IMG_1636 / IMG_8655 / IMG_1639** (B10) hochziehen — keine neuen Assets.
2. **IMG_1409** `[N]` mit `fit: blur` in A1.9 (frühestens 3 Bilder nach 1401).
3. **IMG_1439** `[N]` (nasses Kopfsteinpflaster, „schön, sehr gut") in A1.10.
4. **IMG_8654** `[N]` in B6.
Niemals ein `forbidden_shot` nachziehen.

## Offene Konflikte

1. **Akt-1-Pacing unterschreitet das Brief-Fenster.** `brief.yaml:pacing` nennt für Akt 1
   3,5–6 s je Foto. 55 Musts in 175,95 s ergeben **3,0–3,2 s Basis** (Hero 4,0 s). Das liegt
   innerhalb `min_s: 0.4 / max_s: 6`, aber unter dem Kommentar-Fenster. Vorschlag: Kommentar
   in `brief.yaml` auf **2,8–4,2 s** korrigieren. Alternative wäre, weitere ~8 Akt-1-Musts zu
   streichen — dafür gibt es in Runde 2 **keine** Anweisung, also habe ich es gelassen.
2. **IMG_1445 ist `must`, aber Runde 2 sagt „raus".** Ich folge Runde 2 (sie überschreibt
   punktuell). Der Einstieg in die Kneipe läuft jetzt über 4817. Dasselbe Muster gilt für
   1257/1265/1386/1391/1393/1395/1664/1703/1705. Wenn Christian will, dass `must` absolut
   Vorrang hat, müssten dafür ~28 s aus Akt 1/Aftermath anderswo raus — das ginge nur zu
   Lasten der Videofenster in B10.
3. **Zwei Runde-1-Zwänge sind durch Runde 2 aufgehoben:** „1508 spät, kurz vor Verlassen der
   Rooftop-Bar" → Runde 2 §3 will den Sonnenuntergang **in der Mitte** (B5). Und „F9615661
   direkt vor 1445" → 1445 existiert nicht mehr. Beides bewusst, nicht versehentlich.
4. **Zuordnung der Runde-2-Zeitstempel zu Asset-IDs ist teilweise abgeleitet**, nicht
   verifiziert: Runde 2 nennt nur `M:SS` aus dem alten Preview. Ich habe sie über die
   TC-Tabelle des Runde-1-Beat-Sheets rückgerechnet. **Unsicher bleiben:**
   `~1:50/~1:56 Kranbild` → ich lese **IMG_1352** (das einzige `must`, das Runde 1 nie
   einplante); `~0:28 nur das Bett` → **IMG_1257**; `zweites Haus-Bild` → **IMG_1265**;
   `Waffeln von vorn` → **IMG_1386**; `~8:11 Michael` → **IMG_1697**;
   `~8:30 vor der Tür` → **IMG_1706**. Der `timeline-builder` sollte diese sechs beim
   Zusammenbau gegen die Keyframes prüfen und im QC-Report melden, wenn eine Zuordnung
   offensichtlich falsch ist.
5. **Videofenster sind Schätzungen aus den Notes**, nicht am Material gemessen (kein Bash).
   Kritisch: **IMG_1637** (Hauptstelle 2:22 setzt Clipdauer > 2:29 voraus), **IMG_1621**
   Teil C („~29 s–Ende" — Restlänge unbekannt, ich rechne mit 2,0 s), **IMG_4835** („ab ~8 s"
   — ich rechne mit 4,4 s Rest), **IMG_1613** (Fenster 10–19 s muss die 21-s-Stelle
   enthalten — falls nicht, Fenster **nach hinten** schieben, das „Füßchen" hat Vorrang vor
   dem Startpunkt). Alle vier gegen die echten Clipdauern prüfen.
6. **Speed-Ramps verkürzen die tatsächliche Laufzeit** der drei Clips gegenüber ihrer
   Quelldauer. Die im Beat-Sheet stehenden Dauern sind **Timeline-Dauern nach Ramp** — der
   `timeline-builder` muss `src_out` entsprechend weiter fassen.
7. **`target_duration_s: 534` in `brief.yaml` ist veraltet.** In T7 auf die real gebaute
   Länge (**~428,4**) nachziehen, sonst bricht die QC-Längenprüfung (±2 s) ab — HANDOVER.
8. **B13 liegt teils sehr nah am Musikende.** Wenn beim QC-Hördurchgang das harte Miserlou-
   Ende auf 377,38 unschön knackt, `dur` auf ~377,0 ziehen und IMG_1661 um 0,4 s verlängern
   — der Bild-Cut auf die Schwarzblende bleibt bei 377,38.
