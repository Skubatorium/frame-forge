# Beat-Sheet — `norwegen-2026` / `vlog-edit`

**Revision 2 (2026-08-08).** Die Vollversion des Roadtrips: alle Kameras (Drohne, Chris-iPhone,
Christina-iPhone, Fotos), durchgehende Karte unten rechts, drei Musikteile, Cold Open mit
Karten-Overview und Titel/Infokarte.

**Preset:** `nordic-cinematic` · **Länge:** **18:24 (1103,887 s)** · **Sprache:** de
**Auswahl:** `prefer_source: [drone, phone]`, `rating >= 3`, `exclude != true`, `avoid_redundant_angles`
**Chronologie:** `chronological: true` (genau **eine** dokumentierte Ausnahme, siehe K1)
**Karte:** `map_usage: leitmotif`, unten rechts, Ort + kumulierte Strecke, **keine Höhenmeter**
**Text:** `moderate` — Titel, Infokarte, sonst nichts · **Farbe:** `color_match: soft`, kühle
Lichter / warme Spitzen, mittlerer Kontrast · **O-Ton:** `ambience_only`, keine Sprachfenster

> **Was sich gegenüber Revision 1 geändert hat (beides Nutzerentscheidung vom 2026-08-08):**
>
> 1. **Der Film endet nicht mehr auf dem letzten Norwegen-Bild**, sondern auf der nächtlichen
>    **Ankunft zuhause in Grevenbroich** (K15, letzter Beat).
> 2. **Die Musik bestimmt jetzt die Filmlänge, nicht umgekehrt.** Der `audio-designer` hat die
>    drei Pflicht-Tracks real vermessen (`audio-plan.md`): *Aguila de Oro (Ecstatic Mix)* ist mit
>    **374,63 s** gemessen deutlich kürzer als die für Abschnitt C angenommenen 480 s. Keine
>    KI-Verlängerung, keine Extended-Version, kein Loop — stattdessen endet der Film dort, wo
>    die Musik endet: **1103,887 s = 18:23,9**. Gekürzt wurde ausschließlich der Ausklang
>    (K12–K15, zusammen **190 s → 93,887 s**). Alles bis einschließlich K11 bleibt
>    dramaturgisch unverändert.
>
> Ebenfalls aus `audio-plan.md` übernommen (§1, gemessener Puls-Einsatz statt geschätzter
> 30 s): **Cold Open 40 s statt 30 s, K2 70 s statt 80 s.** Die Blocklänge K0–K2 bleibt bei
> 132 s, K3 und alles danach beginnt unverändert. Das ist keine neue Entscheidung, sondern die
> in Revision 1 bereits formulierte Regel „bei abweichendem Messwert gewinnt die Musik,
> Ausgleich vollständig in K2".

Der Bogen des Presets ist das Gerüst: *ruhiger Auftakt → behutsamer Aufbau über die Etappen →
ein emotionaler Höhepunkt → stiller Ausklang.* `music_energy_curve: gradual_build`. Der
Schnittrhythmus **entwickelt sich über den Film** und ist nicht konstant:

| Filmdrittel | Kapitel | Beat-Länge | Energie |
|---|---|---|---|
| Auftakt | K0–K5 | 7–8 s (oberes Ende von `pacing`) | sehr niedrig → niedrig |
| Aufbau | K6–K10 | 7 s → 5,7 s | steigend |
| Höhepunkt | K11 | 6 s → **4,75 s** → ein 14-s-Klimaxbild | Maximum |
| Ausklang | K12–K15 | 7 s → 8 s → 6 s → 7,3 s, Schlussbild 5 s | fallend, still |

`pacing.min_s = 4` wird nirgends unterschritten, `pacing.max_s = 8` nur an drei erklärten
Stellen überschritten (Cold Open K0, Titelbild K1, Klimaxbild K11). Der Ausklang bleibt nach der
Kürzung **vollständig innerhalb** von `pacing` — er wurde über die **Anzahl** der Beats gekürzt,
nicht über deren Länge. Das ist die entscheidende Regel dieser Revision: **kürzer heißt weniger
Bilder, nicht hektischere Bilder.**

**Abgrenzung zum bestehenden `drone-edit` (568 s):** dort trägt reines Drohnenmaterial ohne
Karte und ohne Menschen bis zum Schluss. Hier ist es umgekehrt — die Menschen sind der Grund,
warum der Film 18 Minuten dauern darf. Drohnenmaterial ist der **Atem** zwischen den Szenen,
nicht das Rückgrat. Faustregel je Kapitel: **1 Drohnen-Establisher am Anfang, 1 am Ende, dazwischen
Menschen/Details.** Beats, die im `drone-edit` wörtlich vorkommen, dürfen hier wiederverwendet
werden, aber **nicht in derselben Reihenfolge und nie als ganze Sequenz** — sonst fühlt sich
`vlog-edit` wie ein gestreckter `drone-edit` an.

---

## 1. Materiallage

Gesamtfundus **975 indizierte Assets** (Stand `PROGRESS.md`, 2026-08-07), alle inhaltlich
gesichtet:

- **Chris-iPhone:** 689 Assets (539 HEIC-Fotos + 150 MOV, 4K60), Tag für Tag beschrieben,
  `captured_at` bei 100 %.
- **Christina-iPhone:** 157 Fotos + 47 Videos.
- **Drohne + übriges:** der ursprüngliche 286er-Bestand (Drohnenvideo/-fotos, tagesbenannte
  Ordner `2026-07-2x_…/Vorauswahl/`).

Verteilung der Chris-iPhone-Assets über die Reisetage — sie bestimmt, welches Kapitel Material
im Überfluss hat und welches knapp ist:

| Tag | Assets | Kapitel | Lage |
|---|---:|---|---|
| 17.07. Verladen | 6 | K2 | knapp — nur 1–2 Beats |
| 18.07. NRW → Flensburg | 42 | K2 | reichlich |
| 19.07. Fähre → Skien | 33 | K3 | ausreichend |
| 20.07. Hütte am Waldsee | 45 | K4 | reichlich, dazu Drohne |
| 21.07. Küste Langesund | 15 | K5 | knapp |
| 22.07. Ruhetag/Grillen | 19 | K5 | ausreichend, dazu Drohne (Golden Hour) |
| 23.07. Heddal → Geilo | 39 | K6 | reichlich, dazu Drohne |
| 24.07. Aurlandsfjellet/Flåmsbana | 70 | K7 | sehr reichlich, viel Drohne |
| 25.07. Nærøyfjord/Gudvangen | 106 | K8 | **größter Tag** — **keine Drohne (Regen)** |
| 26.07. Pässe → Geiranger | 58 | K9 | reichlich, dazu Drohne |
| 27.07. Geburtstag/RIB | 61 | K10 | reichlich, **keine Drohne** |
| 28.07. Trollstigen + Lom | 78 | K11/K12 | reichlich, viel Drohne |
| 29.07. Lom abends/Valdresflye | 15 | K12/K13 | knapp, Drohne trägt |
| 30.07. Uvdal | 10 | K14 | **sehr knapp** |
| 31.07. Uvdal Aktivtag | 15 | K14 | knapp |
| 01.08. Uvdal → Skien | 6 | — | **entfällt nach der Kürzung** (siehe K15) |
| 02.08. Ruhetag | 10 | — | **entfällt nach der Kürzung** (siehe K15) |
| 03.08. Angeln Schärenküste | 20 | K15 | stark, dazu bestes Drohnenmaterial |
| 04.08. Rückreise | 18 | K15 | ausreichend |

Die Christina-iPhone-Assets liegen zusätzlich oben drauf und sind in der Tabelle **nicht**
enthalten — sie sind der Reservepuffer für die knappen Tage (30.07., 31.07.).

**Muss-Shots / verbotene Shots im Brief:** beide leer. Aus dem `drone-edit`-Feedback des Nutzers
gelten projektweit trotzdem zwei benannte Fälle, die hier übernommen werden:

- **Gesperrt:** `20260730-drone-4abe2d` (rote Fußgängerbrücke, angelnde Jungen, Uvdal;
  `stability 0.0`, Schwenk mitten im Take). Wie ein `forbidden_shot` behandeln.
- **Gesperrt:** der 31.07.-Drohnenclip mit `exclude: true` („Drohne im Ast").
- **Empfohlen:** `20260803-drone-574c7c`, Möwenfenster bei `src_in ≈ 26–34 s` (Rating 5) — im
  `drone-edit` ausdrücklich gewünscht, hier als Beat in K15 vorgesehen und von der Kürzung
  **ausgenommen**. Steht **nicht** in der Index-Beschreibung, der `timeline-builder` sichtet das
  Fenster selbst.

**Ehrlich vermerkte Lücken — nicht überspielen, sondern erzählen:**

1. **25.07. hat kein Drohnenmaterial** (Regen). K8 ist deshalb das einzige Kapitel ohne
   Luftbild-Atem. Das ist kein Defizit, sondern Stilmittel: enger, nasser, näher an den
   Menschen — bewusst als Kontrast **vor** dem großen Aufatmen in K9 gesetzt. **Nicht** mit
   Drohnenmaterial vom 24. oder 26.07. „repariert" (bräche die Chronologie).
2. **27.07. hat kein Drohnenmaterial.** Geiranger wird über Ankunft (K9) und Abfahrt (K11)
   luftig eingefasst, K10 selbst bleibt am Boden — passt zum Geburtstag als Innenraum-/
   Menschen-Kapitel.
3. **30./31.07. sind materialarm** (10 / 15 Chris-Assets). Nach der Kürzung ist das **kein
   Problem mehr, sondern ein Vorteil:** K14 hat jetzt 4 Beats, dafür reicht das Material sicher.
   **Wichtig — Regel aus Revision 1 ist hiermit aufgehoben:** Beats werden **nicht** mehr bis
   8 s gedehnt, um dünnes Material zu strecken. Die Kapitelbudgets sind musikfest. Reicht das
   Material für einen geplanten Beat nicht, **entfällt der Beat** und die Zeit geht an den
   Nachbarbeat **desselben** Kapitels — nie an ein anderes Kapitel.
4. **01.08. und 02.08. kommen im Film nicht mehr vor.** Das ist bewusst und wird hier
   ausgeschrieben, damit es niemand später „repariert": im gekürzten Ausklang ist kein Platz für
   einen Beat, der weder Norwegen-Abschied noch Heimkehr erzählt. Der Film springt von Uvdal
   (31.07.) direkt zur Angel-Session an der Schärenküste (03.08.). Die Chronologie bleibt intakt,
   es ist eine Ellipse, keine Umstellung. Der Kartenstand im HUD läuft weiter — die Karte
   erzählt die ausgelassene Etappe, das Bild nicht.
5. **14 Christina-iPhone-Videos haben kein plausibles `captured_at`** (IMG_3587, 3590, 3304,
   3610, 3260, 3104, 3061, 3434, 3270, 3462, 2864, 2867, 2889_Cut-2, 2824). Für sie gilt die
   Fallback-Regel aus dem Brief: **Dateisystem-/Namensreihenfolge innerhalb des Ordners**
   `Christina-iPhone` ist die Erlebnisreihenfolge. Nicht raten, nicht auf EXIF bestehen. 10
   weitere Christina-Videos sind bereits manuell dem Cluster Aurlandsfjord/Flåmsbana zugeordnet
   → sie gehören nach **K7/K8**.
6. **`source_guess` liegt bei iPhone-Videos daneben** — die IDs lauten `2026xxxx-camera-…`,
   obwohl `source: phone` korrekt gesetzt ist. Beim Filtern also auf **`source`** gehen, nicht
   auf das ID-Präfix.

---

## 2. Musikplan

Drei Pflicht-Tracks in fester Reihenfolge. Form **A – B – C**, passend zu
`audio.structure_hint: three_parts` und `music_energy_curve: gradual_build`. **Alle Zeiten hier
sind gemessen** (`audio-plan.md`), keine Schätzungen mehr.

| Abschnitt | Filmzeit | Track | Funktion |
|---|---|---|---|
| A | 00:00 – 06:35 (0–395 s) | **Cuatro Vientos** (`src_in: 0`, 446,86 s verfügbar) | Cold Open, Aufbruch, Anreise, Ankommen in Sørlandet |
| — | **06:25 – 06:35 (385–395 s)** | **Crossfade A→B, 10 s** | Bild: letzte Abendbilder Skien → Aufbruch auf die Straße |
| B | 06:25 – 12:10 (385–730 s) | **Naturaleza (Mose Edit)** (445,22 s verfügbar) | Der Roadtrip beginnt: Heddal, Fjell, Aurland, Nærøyfjord. Weit, atmend, geduldig |
| — | **12:00 – 12:10 (720–730 s)** | **kein Crossfade:** B fährt zurück (`fade_out_s: 10`), C setzt bei **730,0 s hart** ein (`src_in: 0,743`) | Bild: **Dunkel des Lærdalstunnels → Ausfahrt ins Licht.** Siehe unten |
| C | 12:10 – 18:23,9 (730–1103,887 s) | **Aguila de Oro (Ecstatic Mix)** (374,63 s verfügbar, 373,887 s genutzt — **der Engpass, der die Filmlänge setzt**) | Aufstieg, **Höhepunkt Trollstigen**, Nachhall, Ausklang |
| — | 18:13,9 – 18:23,9 (1093,887–1103,887 s) | **natürlicher Fade-out des Tracks, 10 s** | Musik nimmt sich über dem letzten Norwegen-Bild zurück |
| — | 18:20,9 – 18:23,9 (1100,887–1103,887 s) | Bild-`fade` ins Schwarz, 3,0 s | über dem Schlussbild „Ankunft zuhause" |

`fade_in_s: 3` aus Schwarz, `transition_in: black`. **Nur der erste Wechsel ist ein Crossfade**
(10 s, damit nie mehr als ~15 s Doppelschicht entsteht — Brief-Vorgabe). Der zweite Wechsel ist
bewusst *kein* Crossfade, siehe unten.

### Der zweite Wechsel (Naturaleza → Aguila de Oro) — das Bild macht die Arbeit

Der Nutzer hat diesen Übergang ausdrücklich als den kritischen benannt. Statt ihn rein
akustisch zu lösen, liegt er auf dem **stärksten motivierten Bildwechsel des ganzen Films**:
Der 26.07. beginnt um 09:33 mit dem **Lærdalstunnel** — 24 km Dunkelheit mit blauen
Beleuchtungskavernen. Der Plan:

- **720–730 s:** letzter Naturaleza-Abschnitt, Einfahrt/Fahrt im Tunnel. Bild fast schwarz, blau
  gefleckt. Die Musik zieht sich hier über die 10-s-Gainrampe hinter das Bild zurück (der Track
  selbst beruhigt sich an dieser Stelle *nicht*, siehe `audio-plan.md` 2.2 — die Beruhigung ist
  gemacht, nicht gefunden).
- **730,0 s (12:10):** **Tunnelausfahrt ins Licht** — **harter Bildschnitt**, gleichzeitig
  harter Einsatz von Aguila de Oro auf dem ersten vollen Downbeat (`src_in: 0,743`). Ab hier
  trägt Track C allein.

Damit fällt der Trackwechsel mit einem Hell/Dunkel-Sprung zusammen, der ihn hörbar *begründet*.
**730,0 s ist gleichzeitig die Kapitelgrenze K8/K9** — der harte Schnitt liegt auf einer echten
Kapitel- und Beat-Grenze, nicht in einer laufenden Bewegung. Er ist **nicht verschiebbar**.
Findet sich kein brauchbarer Tunnelclip mit `rating >= 3`, ist der Ersatz die **Fähre
Mannheller–Fodnes (10:27)**: Auffahrt (dunkles Autodeck) → Ausfahrt aufs offene Wasser. Gleiche
Dramaturgie, gleiche Zeitlage.

### Schnittraster

- **Cuatro Vientos:** 147,66 BPM (gemessen, bestätigt die 147,7 aus Revision 1) → Beat 0,406 s,
  Takt 1,626 s, **Phrase (8 Takte) = 13,01 s**. Beat-Längen in A: **4 Takte = 6,50 s** oder
  **5 Takte = 8,13 s** — Letzteres nur in K2/K3, wo es am ruhigsten sein soll.
- **Naturaleza (Mose Edit):** 68,91 BPM (gemessen) → Beat 0,871 s, Takt 3,484 s, **Phrase
  (8 Takte) = 27,87 s**, halbe Phrase 13,94 s. Beat-Länge in B: **2 Takte ≈ 6,97 s**.
- **Aguila de Oro (Ecstatic Mix):** **82,03 BPM (jetzt gemessen** — in Revision 1 bewusst nicht
  geraten). Beat 0,731 s, **Takt 2,926 s**, **Phrase (8 Takte) = 23,41 s**. Brauchbare
  Beat-Längen innerhalb `pacing 4–8 s`: **1,5 Takte = 4,39 s · 2 Takte = 5,85 s · 2,5 Takte =
  7,31 s**. **3 Takte = 8,78 s liegen über `pacing.max_s` und sind gesperrt.**
- Die in Abschnitt 3 genannten Sekundenwerte sind **Sollwerte**, die um bis zu **±0,5 s** ans
  gemessene Raster gezogen werden dürfen. Ausdrückliche Ausnahme: die **8,0-s-Beats in K13**
  haben kein passendes Vielfaches (2,5 Takte = 7,31 s wäre 0,69 s daneben, 3 Takte sind
  gesperrt). Sie bleiben bei 8,0 s und werden **nicht** gesnappt — in einem Kapitel mit zwei
  langen, ruhigen Bildern ist die Rasterbindung unhörbar.
- **Kapitelgrenzen** dürfen um bis zu ±2 s wandern, **außer** an den Fixpunkten (Abschnitt 6).
  Die **Gesamtsumme bleibt exakt 1103,887 s**; Rundungsreste werden immer im **letzten Beat vor
  einer Kapitelgrenze** aufgefangen, nie durch Verschieben eines Fixpunkts.

### Der Punkt, der aus der Audiodatei kam — erledigt

**Puls-Einsatz in Cuatro Vientos.** Gemessen: kein stabiles Beat-Grid vor **43,572 s**
(`audio-plan.md` §1). Nach der Regel „gewinnt die Musik", geklemmt auf das erlaubte Maximum:
**Cold Open = 40,0 s** statt der 30 s aus `intro.cold_open_s`. Die Differenz von +10 s ist
vollständig in **K2** ausgeglichen (80 s → 70 s). Alle Kapitelgrenzen ab K3 sind unverändert.
Das ist die dokumentierte Abweichung von `intro.cold_open_s: 30`.

**Track-Längen — die Regel, die diese Revision auslöst.** Ist ein Track kürzer als sein
Abschnitt, wird **nicht geloopt, nicht zeitgedehnt, nicht ergänzt**: dann **bestimmt die
Musiklänge die Filmlänge**. Gemessen:

| Abschnitt | Bedarf Rev. 1 | Verfügbar | Ergebnis |
|---|---:|---:|---|
| A | 395 s | 446,86 s | 51,86 s Überschuss, unkritisch |
| B | 345 s | 445,22 s | 100,22 s Überschuss, unkritisch |
| C | 480 s | **374,63 s** | **Fehlbetrag 105,4 s → Film endet bei 1103,887 s** |

Die Kürzung wurde **nicht gleichmäßig verteilt**, sondern nach Funktion gewichtet (Abschnitt 3,
Vorspann zu K12).

> **Hinweis an den `render-engineer` (ersetzt die Warnung aus Revision 1):** Die alte Sorge —
> „harter 3-s-Fadeout aus voller Energie wirkt abgeschnitten, ggf. auf 12–14 s verlängern" — ist
> **gegenstandslos**. Der Track endet natürlich und blendet **selbst** über die letzten 10 s aus
> (1093,887–1103,887 s). `fade_out_s: 10.0` auf `music-03` ist damit kein Platzhalter mehr,
> sondern der reale Ausklang. Der **Bildfade** ins Schwarz bleibt bei 3,0 s
> (1100,887–1103,887 s). **Kein künstlich verlängertes Ausklangbild bauen** — die Musik macht
> die Arbeit.

### Originalton

`original_audio_policy: ambience_only` — **keine Sprache, keine O-Ton-Fenster, keine
Drohnen-Rotoren.** Erlaubt und erwünscht ist ein leiser Atmo-Teppich unter der Musik
(ca. −24 LUFS, Musik bleibt Leitspur) an **vier** Stellen, wo er die Szene trägt:

| Stelle | Kapitel | Atmo | Zeitfenster (neu) |
|---|---|---|---|
| Deck der Color-Line-Fähre, Wind | K3 | Wind + Wasser | ≈ 170,6–178,4 s (unverändert) |
| Flåmsbana / Wasserfälle | K7 | Wasserrauschen | ≈ 579,1–586,3 s (unverändert) |
| Storsæterfossen, Weg hinter dem Wasserfall | K10 | Wasser, Schritte auf Metall | ≈ 864–881 s (unverändert) |
| Kinder am Kiesufer, Steine ins Wasser | K14 | Wasser, entferntes Kinderlachen | **1053,0–1059,0 s** — **korrigiert** |

> **Korrektur an den `audio-designer`/`timeline-builder`:** Das K14-Atmo-Fenster stand in
> `audio-plan.md` §4 bei **1117,9–1124,3 s**. Das liegt nach der Kürzung **hinter dem Filmende**
> (1103,887 s) und wäre ins Leere gelaufen. Verbindlich ist jetzt **1053,0–1059,0 s** (K14,
> Beat 2). Die drei anderen Fenster liegen alle vor K12 und bleiben unverändert.

Überall sonst: Musik allein. Verständliche Sätze sind auch im Atmo-Teppich nicht zulässig —
notfalls ein anderes Fenster desselben Clips nehmen.

---

## 3. Kapitel

Summe der Beat-Dauern: **1103,887 s = 18:23,9**. Rund **159 Beats**.

### K0 — COLD OPEN: die Route wächst · 00:00 – 00:40 (40 s)

**Ein einziger Beat.** Kein Schnitt. `transition_in: black`, die ersten 3 s reines Schwarz,
Cuatro Vientos blendet mit dem Wind-/Ambientteil ein (`fade_in_s: 3`). Länge **40 s** statt
30 s — gemessener Puls-Einsatz, siehe Abschnitt 2.

**Bild:** die **Karten-Overview-Animation**, formatfüllend (nicht das HUD unten rechts) —
Europa-Ausschnitt, die Route wächst von **Grevenbroich → Hamburg → Flensburg → Hirtshals →
(Seeweg) → Larvik → Skien** und weiter nach Norden ins norwegische Fjell. Der Wachstumsvorgang
läuft über die vollen ~37 s und ist gegen Ende hin **langsamer**, damit er nicht vor der Musik
fertig ist.

> **Auftrag an den `map-animator`:** Dieser Beat ist ein eigener, gerenderter Clip
> (`kind: video`, Quelle: generierte Karte), kein Overlay. Erst danach beginnt das
> HUD-Kartenband unten rechts. Er ist der einzige Ort im Film, an dem die Karte das Bild ist.
> **Neue Länge: 37 s Wachstum + 3 s Blende.**

**Kein Schnitt-Tempo, keine Titel, kein Text in diesen 40 s.** Der Film soll erst atmen.

**Übergang nach K1:** `slow_dissolve` **2,0 s** — die im Brief geforderte
„leichte Blende ins erste echte Norwegen-Bild" (`cold_open_visual: light_dissolve_to_norway`).
Die Blende startet bei 00:38 und endet bei 00:40.

### K1 — TITEL & INFOKARTE · 00:40 – 01:02 (22 s)

**Ein Beat.** Ein einziger Drohnen-Establisher, goldene Stunde: `20260722-drone-e0e4c2`
(22.07., Skien, Rating 4) — derselbe Shot, der im `drone-edit` als Titelbild gelobt wurde. Sehr
langsamer Push, `speed ≈ 0.85`. Wenn der Clip ein Fenster hat, in dem die Kamera aus tiefer Lage
**nach oben steigt**, dieses Fenster nehmen.

**Text (`text_density: moderate`, das ist das gesamte Textbudget des Films):**

| Zeit | Element | Inhalt |
|---|---|---|
| 00:42 – 00:53 | Titel (`templates/svg/title-card.svg`) | **Norwegen 2026** / *Roadtrip* — 2,5 s ein, ~6 s Standzeit, 2,5 s aus |
| 00:54 – 01:02 | Infokarte | **17. Juli – 4. August 2026 · 19 Tage · rund 3.830 km** (davon ca. 325 km Fähre Hirtshals–Larvik und zurück) |

Die Kilometerangabe ist aus `route/stages.csv` aufsummiert (3.829 km inkl. beider Seewege),
nicht geschätzt. Titel und Infokarte **nacheinander**, nie gleichzeitig — zwei Textblöcke
übereinander sind bei `moderate` zu viel.

> **Chronologie-Ausnahme, die einzige im Film:** der 22.07.-Shot steht vor dem 17.07.-Material.
> Der Titelshot steht **vor** der Erzählung, nicht in ihr. Ab K2 ist die Reihenfolge lückenlos
> chronologisch.

**Karte:** Das HUD unten rechts blendet **ab 01:02** ein (1,5 s), auf Stand *Grevenbroich · 0 km*,
und läuft von da an bis **18:20,9** durch.

### K2 — Aufbruch: Verladen, Autobahn, Hamburger Hafen, Flensburg · 01:02 – 02:12 (70 s)

**Material:** 17.07. (6 Assets: Kombi mit Dachbox, blauer Himmel mit Schäfchenwolken) und 18.07.
(42 Assets: Aufbruch 07:00, Stau, Raststätte, **Hamburger Hafen 13:13**, Nord-Ostsee-Kanal,
Ankunft Flensburg 17:00, Möwe und Blumenkästen am Hafen, Restaurant „Gosch", Kartenhaus-Spiel,
Spaziergang am Hafensteg).

**Rhythmus:** 7,8 s → **9 Beats** (war 10 × 8,1 s; die 10 s aus dem längeren Cold Open werden
hier abgezogen). Das ist weiterhin der langsamste Schnitt des ganzen Films.
**Energie:** sehr niedrig, morgendlich, noch nicht angekommen.
**Bildsprache:** viel Foto (**ca. 60 % Fotos mit Ken Burns**), wenig Bewegung. Das Reisen ist
hier noch Warten.
**Aufteilung:** 2 Beats 17.07. (Verladen, Abendhimmel) · 4 Beats Fahrt/Hafen · 3 Beats Flensburger
Abend.
**Nicht zeigen:** Stau als Motiv mehr als **einmal**. Rating-2-Material (unruhige Handaufnahmen
aus dem Auto) fällt ohnehin durch `min_rating: 3`.
**Karte:** der Kilometerstand läuft in diesem Kapitel am stärksten hoch (0 → 578 km) — das ist
die einzige Stelle, an der die Karte selbst eine kleine Geschichte erzählt. Der `map-animator`
darf hier ruhig zügiger fortschreiben als sonst.
**Puffer — verbraucht.** Dieses Kapitel war der Ausgleichspuffer für den Cold Open; der Ausgleich
ist mit 70 s **bereits eingerechnet**. Kein weiterer Spielraum hier.

### K3 — Die Überfahrt · 02:12 – 03:37 (85 s)

**Material:** 19.07. (33 Assets): Abreise vom Hotel, Fährterminal Color Line Hirtshals,
Überfahrt (Deck, **Oskar im Wind auf dem Deck**, Bordrestaurant, Brettspiel, Familienselfies),
Ankunft Larvik, Fahrt nach Skien 18:15, Pizza bei Freunden.

**Rhythmus:** 7,7 s → **11 Beats**.
**Energie:** leicht steigend — Vorfreude, aber noch ruhig.
**Kernbeat:** *Oskar auf dem Deck im Wind*, mittig im Kapitel, mit dem **Atmo-Fenster Wind +
Wasser**. Das ist der erste Moment, in dem der Film ein Gesicht hat.
**Karte:** hier zeigt das HUD zum ersten Mal einen **Seeweg** — 162,5 km Luftlinie
Hirtshals–Larvik. Kennzeichnung als nicht selbst gefahrene Strecke ist Sache des `map-animator`,
kein Beat-Sheet-Thema.
**Motiv-Disziplin:** Fähre kommt im Film **dreimal** vor (19.07., 26.07. Mannheller, 04.08.
Rückreise). Hier ist die ausführliche Version, an den anderen beiden Stellen jeweils **maximal
2 Beats** (K9) bzw. **genau 1 Beat** (K15). Kein Wiederholen desselben Deck-Blicks.
**Schluss des Kapitels:** Ankunft, Pizza, warmes Licht — der erste Moment Ruhe. Übergang nach K4
mit `slow_dissolve` 1,0 s.

### K4 — Sørlandet: Waldsee, Ruderboot, Beeren · 03:37 – 05:17 (100 s)

**Material:** 20.07. (45 Assets + Drohnenvideo): Terrasse der dunklen Holzhütte,
Panorama-Porträts, Wanderung (Moltebeeren, Blaubeeren, Weidenröschen), **Ruderboot auf dem
Waldsee**, Beerenpflücken, Grillabend. Bestes Wetter der ersten Woche.

**Rhythmus:** 7,1 s → **14 Beats**.
**Energie:** niedrig, aber warm. Der erste Beat, der sich nach Urlaub anfühlt.
**Struktur:** Drohnen-Establisher (bewaldete Hügel, See) → Hütte/Terrasse → Wanderung/Beeren →
**Ruderboot als Mittelstück (3 Beats)** → Grillabend → Drohnen-Abschluss (See von oben).
**Ein einziger Top-Down-Beat:** Seeoberfläche oder Ruderboot von senkrecht oben, als Abschluss
der Ruderboot-Sequenz. **Genau einer** — der Effekt wird sonst zur Masche, bevor der Film ihn im
Höhepunkt braucht.
**Motiv-Disziplin:** **kein Wasserfall, kein Bergpanorama, keine Serpentine.** Der Film darf hier
noch nichts zeigen, was er später steigern will. Wasser ist in diesem Kapitel *flach und
still* — der Kontrast zu den stürzenden Wassern ab K7 ist gewollt.
**Fotoanteil:** ca. 40 %.

### K5 — Küste, Grillen, Routenplanung · 05:17 – 06:35 (78 s)

**Material:** 21.07. (15 Assets: Badebucht mit Felsklippen, Sandstrand, Kinderporträts,
Muscheln, Eis) und 22.07. (19 Assets: Videospiele, großes Grillessen, Kinder toben, Establisher
der dunklen Holzhütte) sowie die Notiz „Route besprochen" vom 22.07.

**Rhythmus:** 7,1 s → **11 Beats**.
**Energie:** ruhig-gesellig, das Ende der ersten Phase. Erstmals **viele Menschen im Bild**.
**Dramaturgische Funktion:** dies ist das Kapitel *vor* dem Aufbruch. Es endet mit dem
Kartentisch/der Routenbesprechung und dem Abendlicht über der Hütte — und genau darüber legt
sich der Musikwechsel.
**Musik-Sync:** **06:25–06:35 (385–395 s) Crossfade Cuatro Vientos → Naturaleza.** Er beginnt im
vorletzten Beat und ist mit dem ersten Beat von K6 abgeschlossen. Kapitelgrenze **395 s liegt
fest** (gemessen sauber: nächster echter Beat bei 394,797 s, < 0,21 s Abweichung).
**Nicht verwenden:** den Drohnen-Golden-Hour-Shot vom 22.07. (`e0e4c2`) — der ist als Titelbild
in K1 verbraucht. Ein zweiter Einsatz desselben Shots im selben Film ist ausgeschlossen.

---

### K6 — Der Roadtrip beginnt: Heddal → Fjell · 06:35 – 08:20 (105 s)

**Material:** 23.07. (39 Assets + Drohne): **Stabkirche Heddal 12:22** (Establisher, Museum,
Äxte-Vitrine, Rosemaling), Picknick auf der Wiese, Fahrt am Fjord entlang, Wanderung mit
Familienselfies, Ankunft **Hakkesetstølen Fjellstugu auf 1041 m** (Grasdach-Hütte,
Zimmerschilder), Drohnenshots: See zwischen bewaldeten Bergen mit Landzunge (Rating 4).

**Rhythmus:** 6,97 s (2 Takte Naturaleza) → **15 Beats**.
**Energie:** steigend. Erstmals Höhe, der Horizont wird weit.
**Struktur:** Aufbruch/Straße (2) → **Stabkirche Heddal (4 Beats, davon 1 Detail: Rosemaling
oder Äxte)** → Picknick/Fahrt am Fjord (4) → Ankunft Grasdach-Hütte (2) → **Drohnenabschluss:
See mit Landzunge, davon einer von senkrecht oben (3)**.
**Motiv-Disziplin:** Stabkirchen kommen zweimal im Film vor (Heddal hier, **Lom in K12**). Hier
die architektonische, dort die atmosphärische Variante (Abenddämmerung, Spiegelung). Kein
Wiederholen desselben Kamerawinkels.
**Fotoanteil:** ca. 35 %.
**Übergang nach K7:** harter Schnitt auf den Downbeat — der neue Tag setzt neu an.

### K7 — Aurlandsfjellet, Stegastein, Flåmsbana · 08:20 – 10:15 (115 s)

**Material:** 24.07. (70 Assets, der zweitgrößte Tag, dazu viel Drohnenmaterial): Passstraße
Fv243 durch karge Hochebene, **Stegastein 13:55**, Kreuzfahrtschiff im Hafen von Flåm,
**Flåmsbana 16:00–18:04** (Wasserfälle, Tunnel, Serpentinen), Marktplatz,
Ferienhaus-Siedlung am Fjord, Abenddämmerung mit auslaufendem Color-Line-Schiff.
Dazu die 10 Christina-iPhone-Videos, die dem Cluster Aurlandsfjord/Flåmsbana zugeordnet sind.

**Rhythmus:** 6,97 s → **16 Beats**.
**Energie:** mittel, der erste große Block des Films.
**Struktur:**

| Beats | Inhalt |
|---|---|
| 1–3 | Aurlandsfjellet: Passstraße durch die Hochebene, ein Blick von senkrecht oben |
| 4–6 | **Stegastein** — der Aussichtssteg über dem Fjord. Der Reveal (Kamera steigt aus dem Schatten über die Felskante, der Fjord öffnet sich) ist der stärkste Einzelmoment des Kapitels |
| 7–9 | **Mini-Sequenz „Kreuzfahrtschiff": weit → näher → Bogen ums Schiff.** Zwischen diesen drei Beats **harte Schnitte** — das hält die Sequenz als eine Bewegung zusammen. Genau drei Beats, nicht mehr |
| 10–14 | **Flåmsbana** — Zug, Wasserfälle, Tunnelblitze, Gesichter am Fenster. Hier liegt das **Atmo-Fenster Wasserrauschen** |
| 15–16 | Abenddämmerung, das Color-Line-Schiff läuft aus. Ruhiger Ausklang des Kapitels |

**Motiv-Disziplin — hier ist die Redundanzgefahr am größten:** Kreuzfahrtschiffe tauchen an
**vier** Reisetagen auf (24., 25., 26., 27.07.). Verbindlich: die Dreier-Sequenz hier ist die
**einzige** ausführliche Schiffspassage des Films. In K8 höchstens **ein** Schiffsbeat (die
*Artania* am Kai, aus der Bootsperspektive — anderer Blickwinkel), in K9/K10 **keiner**.
Ebenso: **maximal drei Straßen-aus-der-Luft-Beats** in diesem Kapitel; das Motiv kehrt in K9 und
K11 wieder und darf sich nicht abnutzen.
**Fotoanteil:** ca. 30 % — der Tag hat starkes Videomaterial.

### K8 — Nærøyfjord im Regen & Wikingerdorf · 10:15 – 12:10 (115 s)

**Material:** 25.07. (**106 Assets, der größte Tag der Reise — kein Drohnenmaterial, Regen**):
Camping-Hütte am Aurlandsfjord (Frühstück), Bootsausflug mit Wasserfällen,
**Elektro-Katamaran „Future of the Fjords" Flåm–Gudvangen ab 10:15**, Kreuzfahrtschiff *Artania*
am Kai, **Viking Valley Gudvangen 12:15–17:30** (Schwertkampf-Spiel, Bogenschießen,
Grassodenhäuser, Handwerksvorführungen, Drachenboot-Nachbauten), Familienselfies auf dem
Außendeck. Dazu Christina-iPhone-Material desselben Clusters.

**Rhythmus:** 6,4 s → **18 Beats**. Erstmals unter 7 s — der Puls zieht spürbar an.
**Energie:** steigend, aber **anders**: eng, nass, nah an den Menschen. Kein einziges Luftbild.
**Das ist bewusst gesetzt** — der Film verengt sich hier, damit die Weite in K9 wieder etwas
bedeutet. Kein Ausgleichsversuch mit Drohnenmaterial aus Nachbartagen.
**Struktur:** Frühstück in der Hütte (2) → **Bootsfahrt Nærøyfjord: Wasserfälle direkt an der
Bordwand, Regen auf dem Wasser, Gesichter am Außendeck (7)** → Landung Gudvangen (1) →
**Viking Valley: Bogenschießen, Schwertkampf, Handwerk, Drachenboot (7)** → Rückkehr, Abend (1).
**Kinder-Beats:** hier liegt der emotionale Vorlauf des Films. Mindestens **drei** Beats mit
Kindern in Aktion (Bogenschießen, Schwertkampf) — sie zahlen später auf K10 und K14 ein.
**Schluss:** der **letzte Beat ist der Tunnel-Beat** (Einfahrt/Fahrt im Lærdalstunnel, Bild fast
schwarz). Er endet exakt auf **730,0 s**.
**Musik-Sync:** **720–730 s Rückzug von Naturaleza, bei 730,0 s harter Bildschnitt +
harter Einsatz von Aguila de Oro** (siehe Abschnitt 2). Kapitelgrenze **730,0 s liegt fest** und
ist **nicht verschiebbar** — sie ist zugleich Kapitel-, Beat- und Musikgrenze.

---

### K9 — Über die Pässe nach Geiranger · 12:10 – 13:50 (100 s)

**Material:** 26.07. (58 Assets + Drohne): **Lærdalstunnel 09:33**, **Fähre Mannheller–Fodnes
10:27**, Wanderung an einem Gletscherfluss, **Laukifossen 13:22**, **Loen Skylift 14:01**,
Bergpass mit vielen Wasserfällen im Nebel, türkisfarbene Gletscherseen, **Ankunft Geiranger
16:16**, Balkonporträts an der Hütte (Kaffee, Küsse, Grimassen), Fossen Camping mit
Grasdach-Rezeption, kurze Wanderung zu einem alten Bergbauernhof mit Ziegen.

**Rhythmus:** 5,9 s → **17 Beats** (nahe am gemessenen Raster: 2 Takte = 5,85 s).
**Energie:** deutlich steigend. Das Kapitel beginnt mit dem Lichtsprung aus dem Tunnel und wird
von da an weiter, heller, höher.
**Struktur:** Tunnelausfahrt (1, der Sync-Beat, beginnt exakt bei 730,0 s) → Fähre Mannheller,
**maximal 2 Beats** → Gletscherfluss/Wanderung (3) → **Wasserfälle im Nebel, eine Slow-Mo-Passage
`speed 0.55` auf einem Wasserfall (3)** → türkise Gletscherseen, davon **einer von senkrecht
oben** (3) → Ankunft Geiranger, Hütte, Balkonporträts (4) → Ziegen/Bergbauernhof als leiser
Schlussbeat (1).
**Slow-Mo:** erlaubt und erwünscht (`speed < 1.0`). **`speed > 1.0` ist im ganzen Film
verboten** — keine Timelapse-/Hyperlapse-Beats, das hat sich im `drone-edit`-Preview nicht
bewährt. Lange Clips werden **beschnitten, nicht gerampt**: das ruhigste, stärkste Fenster von
Beat-Länge herausschneiden, Rest verwerfen.
**Motiv-Disziplin:** Wasserfälle kommen in K7, K9, K10 vor. Hier die **nebligen, vielen kleinen**
(Bergpass), in K10 der **eine große, begehbare** (Storsæterfossen). Nicht mischen.
**Fotoanteil:** ca. 35 %.

### K10 — Geburtstag in Geiranger · 13:50 – 15:15 (85 s)

**Material:** 27.07. (61 Assets, **kein Drohnenmaterial**): festlich gedeckter Frühstückstisch
mit Wimpelgirlande, Geschenke (Brettspiel „Brass: Birmingham"), Pop-up-Karte, Kerzenkuchen →
Wanderung zum **Storsæterfossen** (Metalltreppen am Wildbach, Weg hinter dem Wasserfall) → Ort
Geiranger (Marktplatz, Hafen, Katze) → **RIB-Safari 15:00** mit Ausrüstungsverleih,
Gruppenselfies auf dem Boot, Sieben-Schwestern-artige Wasserfälle direkt an der Felswand.

**Rhythmus:** 5,7 s → **15 Beats**.
**Energie:** hoch und **warm** — das ist der menschliche Gipfel des Films, dem 90 Sekunden
später der landschaftliche folgt. Diese Reihenfolge ist Absicht: erst der Grund, dann das Bild.
**Struktur:** Geburtstagsfrühstück (4, davon 1 Detail Kerzenkuchen) → Aufbruch/Treppenweg (2) →
**Storsæterfossen, Weg hinter dem Wasserfall (3)** — hier das **Atmo-Fenster Wasser + Schritte
auf Metall** → Ort Geiranger (2) → **RIB-Safari (4)**: Ausrüstung anlegen, Fahrt, Gesichter in
der Gischt, Wasserfall an der Felswand.
**Kein Luftbild.** Wenn das Kapitel „am Boden" zu eng wirkt, wird der letzte RIB-Beat länger
(bis 8 s) — **nicht** mit Drohnenmaterial vom 26. oder 28.07. aufgefüllt.
**Übergang nach K11:** **harter Schnitt.** Der Höhepunkt soll unvermittelt anfangen.

### K11 — HÖHEPUNKT: Gudbrandsjuvet & Trollstigen · 15:15 – 16:50 (95 s)

**Material:** 28.07. tagsüber (aus 78 Assets des Tages + reichlich Drohnenmaterial, u. a. der
152-s-Clip `20260728-drone-3feda7`): Abschied vom Geirangerfjord, **Schlucht Gudbrandsjuvet
11:44** (Wasser-Steg-Park, Café mit Zimtschnecken, Erdbeeren), Berghütte im Nebel,
**Trollstigen 12:29 auf 702 m** — Aussichtsplattform, Serpentinenstraße aus der
Vogelperspektive, Steinmännchen, „No Trolls beyond this point"-Schild.

**Aufbau — die dramaturgische Mitte des ganzen Films:**

| Beats | Zeit | Dauer | Inhalt |
|---|---|---:|---|
| 1–4 | 915–939 s | 4 × 6,0 s = 24 s | **Anlauf.** Abschied vom Geirangerfjord (1), Gudbrandsjuvet: Schlucht, Steg über dem Wasser, Erdbeeren als warmes Detail (3). Energie zieht an, der Schnitt ist noch atmend |
| 5–16 | 939–996 s | 12 × 4,75 s = 57 s | **Verdichtung.** Kürzeste Beats des Films. Nebel über den Graten, Anfahrt, Plattform, Gesichter, Steinmännchen, das Schild. **Mini-Sequenz „Serpentinen" (Beats 11–13):** weit → seitlich mitfliegend → **senkrecht von oben** (die Serpentinen als Grafik). Zwischen allen Beats dieser Passage **harte Schnitte auf den Downbeat** — jede Blende würde bei 4,75 s ein Viertel des Beats fressen |
| 17 | **996–1010 s** | 14,0 s | **KLIMAX.** Der weiteste Trollstigen-Blick, Kamera steigt langsam aus tiefer Lage auf, das Tal öffnet sich. Einziger Punkt im Film, an dem Bild- und Musikakzent framegenau zusammenfallen. Danach der erste lange `slow_dissolve` (1,5 s) als Erlösung |

> **Korrektur gegenüber Revision 1:** Dort war der Klimax mit „16:20 (980 s)" beziffert. Das
> passte **nicht** zur eigenen Kapitelaufteilung: 915 + 24 + 57 = **996 s (16:36)**. Die 980 s
> waren ein aus einem früheren Entwurf mitgeschleppter Wert. Verbindlich ist die Aufteilung:
> **Klimaxbeat 996,0–1010,0 s, Toleranz ± 2 s.** Die Kapitellänge (95 s) und alle Grenzen
> bleiben davon unberührt — es ändert sich nur die Beschriftung des Fixpunkts.

**Aus `3feda7` (152 s) höchstens zwei Fenster**, und **nicht direkt hintereinander** —
mindestens zwei fremde Beats dazwischen, damit die gemeinsame Herkunft nicht auffällt. Der
beschleunigte Mittelteil dieses Clips ist gesperrt (`speed > 1.0`).
**Menschen im Höhepunkt:** mindestens **zwei** der Verdichtungsbeats zeigen Gesichter auf der
Plattform. Der `drone-edit` durfte hier menschenleer sein — `vlog-edit` darf es nicht, sonst
kippt der Film in seiner stärksten Passage in eine andere Erzählung.
**Fotoanteil:** höchstens 20 %, und **nie zwei Fotos hintereinander** in der Verdichtung.

---

> ## Der Ausklang K12–K15 — wie gekürzt wurde und warum
>
> **Budget: 1010,0 – 1103,887 s = 93,887 s** statt der 190 s aus Revision 1 (−96,113 s, −50,6 %).
> Der Höhepunkt endet bei 1010 s; danach bleiben knapp 94 Sekunden. Das ist ein **kurzer, aber
> vollständiger Abgesang** — nicht mehr das vierteilige Nachspiel von Revision 1.
>
> **Nicht gleichmäßig gekürzt.** Die Gewichtung folgt drei Regeln:
>
> 1. **Der Schluss ist unantastbar.** K15 behält den **Möwen-Beat** (Nutzerwunsch aus dem
>    `drone-edit`) in voller Länge und das **Schlussbild „Ankunft zuhause"** (Nutzerentscheidung
>    2026-08-08). K15 wird deshalb am **wenigsten** gekürzt (50 → 32,887 s, −34 %) und ist jetzt
>    das **längste** der vier Ausklangkapitel.
> 2. **Nachhall verträgt Kompression, Stille nicht.** K12 („Nachhall Lom") hat die
>    reichste Materiallage der vier und die am leichtesten verzichtbare Funktion — es ist ein
>    Atemzug, kein Argument. Es trägt die größte Kürzung (55 → 21 s, −62 %). K13 ist ein
>    Interpunktionskapitel und schrumpft auf zwei Bilder (40 → 16 s), behält aber seine
>    **8-s-Beats**: es darf kurz sein, aber nicht hastig.
> 3. **Weniger Bilder, nicht schnellere Bilder.** Alle Kapitelbudgets wurden über die
>    **Beat-Anzahl** erreicht (27 Beats → 14). Kein Beat unterschreitet 5,85 s. Der Ausklang
>    bleibt langsamer als der Höhepunkt — sonst hätte die Kürzung den Bogen umgekehrt.
>
> **Was das inhaltlich kostet — offen benannt:** 01.08. und 02.08. entfallen ganz (siehe
> Abschnitt 1, Punkt 4); in K12 entfallen Bäckerei, Spielplatz, Katze/Mustang und der **Angler
> mit Fisch** (Letzterer bewusst, weil Oskars Fischfang in K15 dieselbe Beobachtung persönlicher
> erzählt — von zwei Fischbeats überlebt der mit dem Gesicht); in K13 entfallen Aufbruch aus Lom
> und der Sonnenuntergang am Fluss (der Sonnenuntergang wird in K14 als Brücken-Silhouette
> erzählt, das ist die stärkere Fassung); in K14 entfallen Kanufahrt, Bogenschießen/Tischtennis
> und die Weidenröschen-Nahaufnahme.

### K12 — Nachhall: Mitternachtslicht in Lom · 16:50 – 17:11 (21 s)

**Material:** 28.07. abends (**Ankunft Lom 18:19**, Drohnenflug 21:49): Stabkirche Lom mit
Friedhof, **türkisfarbener Fluss mit Brücken**, Bakeriet i Lom, Camping-Spielplatz (Trampolin,
Schaukel), Pizza-Abendessen. Dazu 29.07. abends (15 Assets): Angler am türkisfarbenen Fluss,
Stabkirche Lom in der Abenddämmerung gespiegelt, streunende Katze, grüner Ford-Mustang-Oldtimer.

**Rhythmus:** 7,0 s (≈ 2,5 Takte = 7,31 s) → **3 Beats**. Der Puls fällt.
**Energie:** fallend. Die Musik läuft weiter — die Beruhigung passiert **rein über das Bild**:
kaum Eigenbewegung, längere Brennweitenwirkung, Wasser statt Fels.

| Beat | Zeit | Inhalt |
|---|---|---|
| 1 | 1010,0–1017,0 | **Stabkirche Lom in der Abenddämmerung, im Wasser gespiegelt** (29.07. abends). Bodennah, ruhig, kaum Bewegung — der Gegensatz zur Luftperspektive des Höhepunkts. Beginnt direkt nach dem 1,5-s-`slow_dissolve` aus dem Klimax |
| 2 | 1017,0–1024,0 | **Der türkisfarbene Fluss von senkrecht oben** (Drohne, 28.07. abends). Der vom Nutzer im `drone-edit` ausdrücklich gelobte Shot. **Bleibt drin, volle Länge** — er ist der Grund, warum es dieses Kapitel gibt |
| 3 | 1024,0–1031,0 | **Brücken über dem türkisfarbenen Fluss, schräge Drohnenperspektive**, Abendlicht. Der Schrägblick nach dem Senkrechtblick — der Kontrast senkrecht/schräg ist die Wirkung des Kapitels |

**Anmerkung zum Kontrastpaar:** In Revision 1 war der Top-Down-Beat von *beiden* Seiten mit
Schrägblicken eingefasst. Bei drei Beats trägt jetzt nur noch die Seite danach den Kontrast;
davor steht ein Bodenbild. Das ist bewusst so gewählt — die Abfolge *Boden → senkrecht → schräg*
öffnet den Blick, statt ihn zu spiegeln, und passt besser zu einem Kapitel, das nur noch 21 s hat.
**Funktion:** ohne dieses Kapitel wirkt der Film hinter dem Höhepunkt abgeschnitten. Es ist kein
Füllmaterial — auch nicht in der kurzen Fassung.
**Chronologie-Hinweis:** 28.07. abends und 29.07. abends werden hier zu **einem** Abendkapitel
verbunden. Zulässig, weil beide Abende am selben Ort (Lom) liegen. Die Reihenfolge innerhalb
weicht in der Kurzfassung ab (Beat 1 ist vom 29., Beat 2/3 vom 28.) — das ist **innerhalb eines
Ortes und einer Tageszeit** und damit keine Chronologie-Ausnahme im Sinne des Briefs, sondern
eine Bildfolge. Wer es streng will: Beat 1 und Beat 3 tauschen; dann steht 28. vor 29., der
Senkrecht/Schräg-Kontrast liegt aber ungünstiger. **Vorzug: so lassen wie oben.**

> **Achtung `timeline-builder`/`map-animator`:** In K12 muss der Kartenstand auf **Lom** stehen
> bleiben. Der Sprung Lom → Valdresflye → Uvdal passiert erst in K13. Falls die HUD-Stufen streng
> nach `captured_at` laufen, hier eine manuelle Stufengrenze bei **1031,0 s** setzen
> (war in Revision 1: 1065 s — durch die Kürzung verschoben).

### K13 — Valdresflye: der höchste Punkt · 17:11 – 17:27 (16 s)

**Material:** 29.07. tagsüber (Drohne trägt dieses Kapitel): Stabkirche Lom am Morgen,
**Valdresflye Fv51, 1183 m — der höchste gemessene Punkt der Reise (echte GPS-Messung)**,
Hochebene, Numedal, **Ankunft Camp Uvdal 16:44**, Reihe von Camping-Hütten am spiegelglatten
Wasser, Sonnenuntergang am Fluss.

**Rhythmus:** 8,0 s → **2 Beats**. Die längsten Beats seit K2 — der Film wird still.
**Energie:** niedrig, weit, klar. Nach dem Trubel von K11/K12 ein Kapitel, das nur schaut.

| Beat | Zeit | Inhalt |
|---|---|---|
| 1 | 1031,0–1039,0 | **Valdresflye, Hochebene, weitester Blick.** Der höchste Punkt der Reise bekommt genau **ein** Bild. Das ist Absicht: ein Rekord braucht keine Sequenz, er braucht Zeit |
| 2 | 1039,0–1047,0 | **Ankunft Camp Uvdal:** Hüttenreihe am spiegelglatten Wasser. Ruhe, Spiegelung, Ankommen |

**Raster-Ausnahme:** 8,0 s ist kein Vielfaches des Aguila-Taktes (2,5 Takte = 7,31 s, 3 Takte =
8,78 s > `pacing.max_s`). Hier wird **nicht gesnappt** — begründet in Abschnitt 2. Der
`timeline-builder` darf 8,0 s stehen lassen.
**Karte:** dies ist der Höhenrekord der Reise — im HUD **nicht** sichtbar, weil
`show_elevation: false`. Bewusst so: die Höhe steht im Bild, nicht in der Grafik. Das HUD muss in
diesen 16 s allerdings **zwei** Etappenstufen durchlaufen (Lom → Valdresflye → Uvdal); der
`map-animator` fasst das zu **einer** durchgehenden Bewegung zusammen, nicht zu zwei Sprüngen.
**Fotoanteil:** ca. 40 %, Ken Burns sehr langsam.

### K14 — Uvdal: Tage am Fluss · 17:27 – 17:51 (24 s)

**Material:** 30.07. (10 Assets) und 31.07. (15 Assets) — **das materialärmste Kapitel**: Jungen
laufen über die Wiese Richtung Wald, Kind watet/angelt im Fluss unter der Holzbrücke, Kinder
plantschen auf der Kiesbank, Establisher der Holzbrücke, Familien-Pizzaessen am Flussufer bei
Abendlicht, dramatischer Sonnenuntergang mit Brücken-Silhouette; Kanufahrt von Mutter und Kind,
Tischtennis, Bogenschießen, Kinder werfen Steine ins Wasser, Weidenröschen-Nahaufnahme.
Ergänzend: Christina-iPhone-Material (Fallback-Sortierung nach Dateinamen, siehe Abschnitt 1).

**Rhythmus:** 6,0 s (= 2 Takte, 5,85 s, sauber auf dem Raster) → **4 Beats**.
**Energie:** niedrig, warm, menschlich. Das emotionale Nachbild des Films — hier passiert nichts
Spektakuläres, und genau das ist der Punkt.

| Beat | Zeit | Inhalt |
|---|---|---|
| 1 | 1047,0–1053,0 | **Kind watet/angelt im Fluss unter der Holzbrücke.** Establisher und Motiv in einem Bild — der separate Brücken-Establisher aus Revision 1 entfällt (Brücken-Beat 1 von 2) |
| 2 | 1053,0–1059,0 | **Kinder werfen Steine ins Wasser.** Hier liegt das **Atmo-Fenster Wasser + entferntes Kinderlachen, 1053,0–1059,0 s** (korrigierte Zeit, siehe Abschnitt 2) |
| 3 | 1059,0–1065,0 | **Familien-Pizzaessen am Flussufer** im Abendlicht. Der letzte Beat des Films mit der ganzen Familie im Bild |
| 4 | 1065,0–1071,0 | **Sonnenuntergang mit Brücken-Silhouette** (Brücken-Beat 2 von 2). Ende des Norwegen-Alltags |

**Tagesbalance:** Beats 1–2 kommen vom 30.07., Beats 3–4 dürfen von **beiden** Tagen stammen.
Der `timeline-builder` wählt so, dass **jeder der beiden Tage mindestens einmal** vorkommt —
sonst verschwindet der 31.07. (Aktivtag) vollständig aus dem Film.
**Gesperrt:** `20260730-drone-4abe2d` (rote Fußgängerbrücke, angelnde Jungen) — instabil, Schwenk
mitten im Take. Und der 31.07.-Drohnenclip mit `exclude: true`. Für das Brückenmotiv wird das
iPhone-Material genommen, nicht die Drohne.
**Wenn das Material nicht reicht:** Beat streichen, Zeit an den Nachbarbeat **innerhalb K14** —
**nicht** dehnen, **nicht** aus K13 oder K15 borgen, **nicht** mit 01.08.-Material vorgreifen.
**Motiv-Disziplin Brücken:** **maximal zwei Brücken-Beats** (Beat 1 und Beat 4), und die sind
durch zwei andere Bilder getrennt. Die vom Nutzer beanstandete Brücken-Häufung ist damit
strukturell ausgeschlossen.

### K15 — Heimweg: Schärenküste, Fähre, Ankunft zuhause · 17:51 – 18:23,9 (32,887 s)

**Material:** **03.08.** (20 Assets + das stärkste Drohnenmaterial der Rückreise: Angel-Session
an Küstenfelsen, **Oskar fängt einen kleinen Fisch**, türkisfarbene Meeresbucht,
`20260803-drone-574c7c` mit **Möwenfenster**, `991503`, `5601da`, `d1eb17` — alle Rating 5),
**04.08.** (18 Assets: Fährterminal Larvik im frühen Morgenlicht **07:00**, Überfahrt,
Routenkarte an Bord, nächtliche Ankunft zuhause mit beladenem Auto).
01.08. und 02.08. kommen nicht mehr vor (siehe Abschnitt 1, Punkt 4).

**Rhythmus:** **5 Beats**, das längste der vier Ausklangkapitel.

| Beat | Zeit | Dauer | Inhalt |
|---|---|---:|---|
| 1 | 1071,0–1078,0 | 7,0 s | **MÖWEN-BEAT — unangetastet.** `20260803-drone-574c7c`, `src_in ≈ 26–28 s` bis `≈ 32–34 s`. Die Möwe fliegt ruhig durchs Bild und lässt sich mitverfolgen. Steht **nicht** in der Index-Beschreibung — der `timeline-builder` sichtet das Fenster und legt die Grenzen so, dass die Möwe **vollständig** im Beat liegt; die Beat-Grenze darf hier vom Raster abweichen (5–8 s), das Motiv hat Vorrang. Kein Slow-Mo. Wird die Beat-Länge dadurch verändert, gleicht **Beat 4** die Differenz aus |
| 2 | 1078,0–1084,0 | 6,0 s | **Oskar fängt einen Fisch** — Jubel an den Küstenfelsen. Der letzte laute Moment des Films und der einzige Beat in K15 mit Bewegung im Bild. Slow-Mo optional (`speed 0.7`) |
| 3 | 1084,0–1091,0 | 7,0 s | **04.08., Fähre Larvik 07:00 im Gegenlicht.** Deck, Routenkarte an Bord — die Karte im Bild spiegelt die Karte im HUD. **Genau dieser eine** Fährbeat (Motiv-Disziplin K3) |
| 4 | 1091,0–1098,887 | 7,887 s | **Letztes Norwegen-Bild:** weitester Blick über die Schärenküste, sehr langsamer Aufwärts-/Rückwärtsflug. Kandidat: `20260803-drone-d1eb17`. **Ab 1093,887 s beginnt der natürliche 10-s-Fade-out der Musik** — die Musik nimmt sich also über diesem Bild zurück, nicht erst über dem Schlussbild. Das ist der eigentliche Abschied. Danach `slow_dissolve` **1,5 s** |
| 5 | 1098,887–1103,887 | 5,0 s | **SCHLUSSBILD: Ankunft zuhause.** Nächtliche Ankunft in Grevenbroich, beladenes Auto — schließt den Reisebogen buchstäblich. Ab **1100,887 s** `fade` ins Schwarz (`transition_out: black`, 3,0 s), die Musik ist zu diesem Zeitpunkt bereits fast ausgeblendet |

**Zwei Entscheidungen, die hier zusammenlaufen (beide 2026-08-08, beide vom Nutzer bestätigt):**

1. **Heimkehr statt Norwegen-Schluss.** Ursprünglich hatte der `story-architect` empfohlen, auf
   dem letzten norwegischen Bild zu enden, weil ein dunkler Parkplatz den Bogen eher abschließt
   als schließt. Der Nutzer wollte ausdrücklich die Heimkehr. Sie steht.
2. **Musiklänge bestimmt Filmlänge.** Aus den 7 Beats von Revision 1 sind 5 geworden. Entfallen
   sind der **Rennradfahrer auf der Passstraße** (01./02.08. — damit entfallen diese beiden Tage
   ganz) und die **türkisfarbene Meeresbucht von oben**. Letztere war die schwächere Dublette zu
   Beat 4: beide menschenleer, weit, still, beide aus dem 03.08.-Drohnenmaterial. Von zwei
   gleichartigen Abschiedsbildern überlebt das weitere.

**Nebenwirkung, bewusst in Kauf genommen:** ohne den Rennradfahrer hat K15 kein
Straßen-von-oben-Motiv mehr. Das Straßenmotiv aus K7/K9/K11 wird im Film also **nicht mehr
aufgelöst**. In 33 Sekunden Ausklang ist dafür kein Platz — und die Fähre (Beat 3) erzählt den
Heimweg ohnehin konkreter als eine leere Straße.

**Karte:** Der Kilometerstand erreicht in Beat 3/4 den Endwert **rund 3.830 km**. Das HUD blendet
mit dem Bild aus (ab **1100,887 s**). Ein finaler Zahlenstand ist erlaubt, aber **kein
zusätzlicher Abspanntext** — `text_density: moderate` ist mit Titel und Infokarte bereits
ausgeschöpft.

---

## 4. Übergänge

`transition_vocabulary: [fade, slow_dissolve, cut]`. Aus dem `drone-edit`-Preview ist belegt:
**pauschal lange Blenden erzeugen einen „Schlier".** Diese Faustregeln gelten hier von Anfang an:

1. **Dissolve-Default innerhalb eines Kapitels: 0,5–0,8 s.**
2. **Nie zwei Clips überblenden, die beide deutliche Eigenbewegung haben** — Bewegung auf
   Bewegung heißt **harter Schnitt** auf den Downbeat.
3. **Dissolve-Länge ≤ 25 % des kürzeren der beiden Clips.** In der K11-Verdichtung (4,75 s)
   heißt das praktisch: nur harte Schnitte.
4. **Lange Blenden (≥ 1,5 s) sind ein Stilmittel** und bleiben vier Stellen vorbehalten:
   Cold-Open-Ausgang, Titelübergang, Erlösung nach dem Klimax, Schlussfade.

| Übergang | Zeit | Empfehlung | Warum |
|---|---:|---|---|
| Schwarz → K0 | 00:00 | `fade` 3,0 s | `transition_in: black`, mit `fade_in_s: 3` synchron |
| K0 → K1 | 00:38–00:40 | **`slow_dissolve` 2,0 s** | die im Brief geforderte „leichte Blende" Karte → Norwegen |
| K1 → K2 | 01:02 | `slow_dissolve` 1,2 s | Titel geht ins Bild über, hier ist weich richtig |
| K2/K3/K4/K5 intern | | **0,8 s** | Auftakt darf weicher sein als der Rest |
| K2 → K3 / K3 → K4 | | 1,0 s | Ortswechsel |
| K4 → K5 | 05:17 | 1,0 s | |
| **K5 → K6** | **06:35 (395 s)** | **1,2 s**, parallel Musik-Crossfade | der erste Trackwechsel, weich |
| K6/K7/K8 intern | | **0,6 s**; Schiffsequenz in K7 **hart** | Bewegung auf Bewegung |
| K6 → K7 | 08:20 | **harter Schnitt** | neuer Tag setzt neu an |
| K7 → K8 | 10:15 | 0,8 s | |
| **K8 → K9** | **12:10 (730,0 s)** | **harter Schnitt, Länge 0,0 s — Fixpunkt** | Tunnelausfahrt; der zweite Trackwechsel lebt vom Lichtsprung, nicht von der Blende. Kein Dissolve, kein Crossfade, keine Verschiebung |
| K9 intern | | **0,5 s**; Einstieg in die Wasserfall-Slow-Mo **hart** | Slow-Mo wirkt nur, wenn sie schlagartig beginnt |
| K9 → K10 | 13:50 | 0,8 s | |
| K10 intern | | 0,5 s | |
| K10 → K11 | 15:15 | **harter Schnitt** | der Höhepunkt soll unvermittelt anfangen |
| K11 intern | | **durchgehend harte Schnitte** | Beats sind 4,75 s |
| K11 Klimax-Ausgang → K12 | **16:50 (1010 s)** | **`slow_dissolve` 1,5 s** | einzige lange Blende im Mittelteil, „Erlösung" |
| K12 intern | | 0,8 s | ruhiges Kapitel, darf weicher sein |
| K12 → K13 | **17:11 (1031 s)** | 1,2 s | Ortswechsel Lom → Hochebene |
| K13 intern | | 1,0 s | längste Beats, längste Blenden |
| K13 → K14 | **17:27 (1047 s)** | 1,0 s | |
| K14 intern | | 0,7 s | |
| K14 → K15 | **17:51 (1071 s)** | 1,2 s | Ankunft am Meer, hier darf es atmen |
| K15 intern (Beats 1–3) | | 1,0 s | |
| K15 Beat 4 → Beat 5 | **≈ 18:18,9 (1098,887 s)** | **`slow_dissolve` 1,5 s** | Norwegen → zuhause; am Ende ist Länge Stilmittel |
| K15 → Schwarz | **18:20,9 (1100,887 s)** | `fade` 3,0 s | `transition_out: black`; Musik ist parallel schon fast aus |

---

## 5. Karte, Fotos, Auswahl — Hinweise an den `timeline-builder`

**Karte (`map_usage: leitmotif`).** Ein durchgehender Render-Layer unten rechts, gebaut vom
`map-animator` über `render_inset_frames` mit **`heights=None`** (`show_elevation: false`). Er
zeigt nur `stage_label` (Ort/Etappe) und `cumulative_km`. **Kein Beat-Sheet-Eintrag pro
Kartenupdate** — die Karte läuft in jedem Kapitel mit. Nur vier Stellen sind besonders:

- **K0:** die Karte **ist** das Bild, formatfüllend, als eigener Clip (40 s). Kein HUD.
- **01:02 (62 s):** HUD blendet ein (1,5 s), Stand *Grevenbroich · 0 km*.
- **K12/K13:** Stufengrenze manuell auf **1031,0 s** setzen, damit der Stand nicht vorzeitig auf
  Uvdal springt (siehe K12). In K13 laufen dann **zwei** Etappenstufen in einer Bewegung durch.
- **18:20,9 (1100,887 s):** HUD blendet mit dem Bild aus.

**Ken Burns (`photo_treatment: { ken_burns: subtle }`).** Die HEIC-Fotos liegen bei 5712×4284
(4:3) vor — das Zielformat ist 16:9. **Nie schwarzen Hintergrund zeigen, kein Letterboxing:**
Crop/Scale so wählen, dass das Bild die Fläche über die **gesamte** Ken-Burns-Bewegung
vollständig füllt, also mit Reserve am Rand. Das ist der häufigste Fehlerfall bei zu kleinem
Ausschnitt. HEIC rendert immer über den JPEG-Proxy (dokumentierte Ausnahme, siehe
`PROGRESS.md` HEIC-4); fehlt der Proxy, ist das ein Fehler, keine Notlösung.
Weiter: **nie mehr als zwei Fotos hintereinander**, und in K11 (Verdichtung) **nie zwei**.

**Auswahl-Queries.** Asset-IDs sind hier bewusst **nicht** geraten — außer den namentlich
benannten. Der `timeline-builder` löst jedes Kapitel über den Index auf, nicht über Vermutung:

```
python -m frameforge query norwegen-2026 --date 2026-07-24 --min-rating 3
python -m frameforge query norwegen-2026 --date 2026-07-28 --source drone --min-rating 3
```

und filtert dann auf Summary/Tags. Für die Top-Down-Slots (K4, K6, K7, K9, K11, K12) sind die
Suchbegriffe: *von oben, senkrecht, Vogelperspektive, Draufsicht, top-down, Luftbild, Flusslauf,
Serpentinen, Küstenlinie*. **Findet sich für einen Slot nichts, bleibt er leer** und der
Nachbar-Beat **desselben Kapitels** wird länger — kein Ersatz durch einen weiteren Frontalflug,
und keine Anleihe beim Nachbarkapitel.

**Geschwindigkeit.** `speed > 1.0` ist im ganzen Film **verboten** (Nutzer-Feedback aus dem
`drone-edit`-Preview: Timelapse-/Hyperlapse-Ramps haben sich nicht bewährt). Slow-Mo
(`speed < 1.0`) bleibt erlaubt und ist an drei Stellen vorgesehen: Wasserfall in K9, ein
Verdichtungsbeat in K11, optional der Fischfang in K15. Lange Clips werden **beschnitten**, nicht
gerampt.

**Stabilität.** Clips mit Schwenk/Unruhe **mitten** im Take meiden, auch wenn Anfang und Ende
ruhig wirken. Bei `stability < 0.35` nur verwenden, wenn ein nachweislich ruhiges Fenster von
voller Beat-Länge existiert.

**Redundanz-Deckel (verbindlich, aus dem Brief).** Dieselbe Szene nicht aus mehreren
Perspektiven als Serie:

| Motiv | Erlaubt | Regel |
|---|---|---|
| Kreuzfahrtschiff | K7 (3 Beats als Sequenz), K8 (1 Beat) | sonst **nirgends**. Die Dreier-Sequenz in K7 ist die einzige ausführliche |
| Fähre | K3 (ausführlich), K9 (max. 2), K15 (genau 1) | nie derselbe Deckblick zweimal |
| Stabkirche | K6 Heddal, K12 Lom | zwei verschiedene Charaktere, nicht derselbe Winkel |
| Wasserfall | K7 (Flåmsbana), K9 (viele kleine im Nebel), K10 (Storsæterfossen) | drei verschiedene Erzählweisen, keine Wiederholung |
| Straße von oben | K7 (max. 3), K9, K11 (Serpentinen-Sequenz) | **in K15 entfallen** (Kürzung) — das Motiv wird nicht mehr aufgelöst |
| Brücke | K12 (1, schräg über dem Fluss), K14 (max. 2, getrennt) | **nie** drei Brückenwinkel hintereinander — das war die vom Nutzer beanstandete Häufung |
| Fischfang | K15 (Oskar) | der Angler in K12 ist **gestrichen**; es gibt genau **einen** Fischbeat im Film |
| Familienselfie | max. **1 pro Kapitel** | kommt an fast jedem Reisetag vor, wird sonst zur Masche |

---

## 6. Prüfsumme

| Kapitel | Zeit | Dauer (s) | Beats | Ø Beat | Musik | Energie |
|---|---|---:|---:|---:|---|---|
| K0 Cold Open / Karte | 00:00–00:40 | 40 | 1 | 40,0 | A (Wind) | — |
| K1 Titel & Infokarte | 00:40–01:02 | 22 | 1 | 22,0 | A | — |
| K2 Aufbruch → Flensburg | 01:02–02:12 | 70 | 9 | 7,8 | A | sehr niedrig |
| K3 Die Überfahrt | 02:12–03:37 | 85 | 11 | 7,7 | A | niedrig |
| K4 Sørlandet, Waldsee | 03:37–05:17 | 100 | 14 | 7,1 | A | niedrig, warm |
| K5 Küste, Routenplanung | 05:17–06:35 | 78 | 11 | 7,1 | A → **CF** | ruhig-gesellig |
| K6 Heddal → Fjell | 06:35–08:20 | 105 | 15 | 7,0 | B | steigend |
| K7 Stegastein, Flåmsbana | 08:20–10:15 | 115 | 16 | 7,0 | B | mittel |
| K8 Nærøyfjord, Wikinger | 10:15–12:10 | 115 | 18 | 6,4 | B → **harter Wechsel** | steigend, eng |
| K9 Pässe → Geiranger | 12:10–13:50 | 100 | 17 | 5,9 | C | deutlich steigend |
| K10 Geburtstag Geiranger | 13:50–15:15 | 85 | 15 | 5,7 | C | hoch, warm |
| **K11 Trollstigen** | **15:15–16:50** | **95** | **17** | **5,6** | C | **Maximum (Klimax 996 s)** |
| K12 Lom, Abendlicht | 16:50–17:11 | **21** | 3 | 7,0 | C | fallend |
| K13 Valdresflye | 17:11–17:27 | **16** | 2 | 8,0 | C | niedrig, weit |
| K14 Uvdal am Fluss | 17:27–17:51 | **24** | 4 | 6,0 | C | niedrig, warm |
| K15 Küste, Fähre, Ankunft zuhause | 17:51–18:23,9 | **32,887** | 5 | 6,6 | C (Fade ab 1093,887) | Ausklang |
| **Summe** | | **1103,887** | **≈ 159** | | | |

Kontrollrechnung Ausklang: 21 + 16 + 24 + 32,887 = **93,887 s** = 1103,887 − 1010,0. ✔

**Fixpunkte — nicht verschieben:**

| Zeit | Was |
|---:|---|
| 40,0 s | Ende Cold Open — **gemessener** Puls-Einsatz (43,572 s), geklemmt auf 40 s. Ausgleich ist in K2 bereits verrechnet, **keine weitere Wanderung** |
| 395,0 s | Crossfade Cuatro Vientos → Naturaleza, Kapitelgrenze K5/K6 |
| **730,0 s** | **Harter Bildschnitt Tunnelausfahrt + harter Einsatz Aguila de Oro** (`src_in 0,743`). Zugleich Kapitelgrenze **K8/K9** und Beat-Grenze. Kein Dissolve, keine Toleranz |
| 996,0 s | **Klimax Trollstigen**, Beat 17 von K11 (± 2 s) — korrigiert von den fehlerhaften 980 s aus Revision 1 |
| 1010,0 s | Kapitelgrenze K11/K12 — Beginn des gekürzten Ausklangs, Budget ab hier: 93,887 s |
| 1093,887 s | Beginn des **natürlichen** 10-s-Fade-outs von Aguila de Oro (in K15 Beat 4) |
| 1100,887 s | Beginn Bild-`fade` ins Schwarz (3,0 s), HUD blendet aus |
| **1103,887 s** | **Gesamtlänge — harte Grenze, von der Musik gesetzt.** Kein Richtwert, kein Aufrunden auf 1104 s |

**Regeln beim Nachjustieren:**

- **Die Summe bleibt exakt 1103,887 s.** Wird ein Kapitel länger, wird ein anderes **im selben
  Musikabschnitt** kürzer. Rundungsreste landen im letzten Beat vor einer Kapitelgrenze.
- Reicht das Material in einem Kapitel nicht, **entfällt ein Beat** und die Zeit geht an einen
  Nachbarbeat **desselben** Kapitels. Beats werden **nicht mehr gedehnt**, um Material zu
  strecken (Änderung gegenüber Revision 1), und **nie** aus dem Nachbarkapitel aufgefüllt — das
  bräche die Chronologie.
- Ist ein Kapitel dennoch zu lang, wird es gekürzt und die Differenz auf **K7, K8 oder K9**
  gegeben (dort liegt mit 70/106/58 Assets das meiste Material). **Nicht** auf K12–K15 — die
  sind bereits auf das musikalische Minimum gekürzt.
- Beat-Längen dürfen ± 0,5 s ans gemessene Musikraster gezogen werden (Takt A 1,626 s /
  B 3,484 s / **C 2,926 s**), Kapitelgrenzen ± 2 s — außer an den Fixpunkten oben.
- **Was ausdrücklich nicht getan wird:** loopen, timestretchen, einen vierten Track ergänzen oder
  Musik generieren, um wieder auf 20 Minuten zu kommen. Die Länge ist entschieden.
