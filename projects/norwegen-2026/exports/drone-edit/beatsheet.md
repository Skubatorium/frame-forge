# Beat-Sheet — `norwegen-2026` / `drone-edit`

**Preset:** `nordic-cinematic` · **Ziellänge:** 12:00 (720 s, hart) · **Sprache:** de
**Auswahl:** ausschließlich `source: drone`, `rating >= 3`, `exclude != true` · **chronologisch**
**Karte:** keine · **Text:** nur Intro-Titel · **Farbe:** `color_match: soft`, kühle Lichter / warme Spitzen, mittlerer Kontrast

Der Bogen des Presets ist die Vorlage: *ruhiger Auftakt (Landschaft) → behutsamer Aufbau über die
Etappen → ein emotionaler Höhepunkt → stiller Ausklang.* Die `music_energy_curve` ist
`gradual_build`, also **entwickelt sich der Schnittrhythmus über den Film** statt konstant zu
bleiben: Kapitel 1–2 liegen am oberen Ende des Pacing-Fensters (7–8 s), das Zentrum wandert auf
6–6,5 s, der Höhepunkt auf 5–5,5 s (nie darunter — `pacing.min_s = 4`), der Ausklang geht wieder
auf 8 s und länger.

---

## 0. Materiallage (aus dem Index, vor der Dramaturgie)

Das Drohnenmaterial liegt in tagesbenannten Ordnern (`2026-07-2x_…/Vorauswahl/DJI_*.MP4`,
4K, 59,94 fps, HEVC) plus einige `DJI_*.JPG` (Luftfotos). Verteilung entlang der Reise:

| Tag | Etappe | Drohnenmaterial | Rolle im Film |
|---|---|---|---|
| 17.–19.07. | Anreise, Fähre | **keins** | entfällt (reiner Drohnen-Reel) |
| 20.07. | Skien / Hütte am Waldsee | ja (`DJI_20260720…`) | Auftakt |
| 21.07. | Küste bei Langesund | keins gefunden | entfällt |
| 22.07. | Skien, Ruhetag | ja, **Sonnenuntergang/goldene Stunde** (`DJI_20260722215000`, Rating 4) | Auftakt-Schluss |
| 23.07. | Geilo, Hakkesetstølen | ja (`DJI_20260723140707`, See zwischen Bergen, Rating 4) | Aufbruch ins Fjell |
| 24.07. | Geilo → Aurland | viel: Passstraße am See (Rating 4), Hüttensiedlung von oben (Rating 4), Abendflug `DJI_20260724195421` | erster großer Block |
| 25.07. | Aurland, Erlebnistag | **keins — Regen** (in `stages.csv` ausdrücklich vermerkt) | Lücke, chronologisch unproblematisch |
| 26.07. | Aurland → Geiranger | ja: Roadshots über die Pässe + Luftfotos an der Unterkunft Geiranger | Anstieg |
| 27.07. | Geiranger, Geburtstag | **keins im Index** (der Tag ist rein iPhone-dokumentiert) | Geiranger wird über 26./28.07. erzählt |
| 28.07. | Geiranger → Lom | viel, darunter ein 152-s-Clip (`DJI_20260728145455_0032…seg8`) und der Abendflug in Lom (`DJI_20260728214940`, 21:49) | **Höhepunkt + Nachhall** |
| 29.07. | Lom → Uvdal, Valdresflye | ja (`DJI_20260729154156`, Rating 4) | Abstieg |
| 30./31.07. | Uvdal, Hütte am Fluss | ja (`DJI_20260730114813`, rote Fußgängerbrücke, Rating 3) | ruhiger Nachsatz |
| 01.08. | Uvdal → Skien | ja (`DJI_20260801125246`, Passstraße/Rennradfahrer) | letzte Bewegung |
| 03.08. | Angelplatz bei Langesund | ja, **stärkstes Material der Rückreise** (`DJI_20260803155043`, Schärenküste türkis, Rating 5) | Ausklang |
| 04.08. | Rückreise/Fähre | keins | entfällt |

**Muss-Shots / verbotene Shots:** im Brief beide leer — keine Einschränkung, keine Lücke zu melden.

**Zwei Hinweise, die der `timeline-builder` beachten muss:**

1. Assets mit `exclude: true` sind zu überspringen, auch wenn Rating und Quelle passen
   (im Fundus z. B. ein 31.07.-Clip mit `exclude_reason: "Drohne in Ast, ruckartige Fehlbewegung"`).
2. Mehrere Drohnenclips sind **sehr lang** (bis 152 s). Sie werden nicht gekürzt, sondern nach
   Nutzer-Vorgabe filmisch verdichtet: Speed-Ramp hinein, beschleunigter Mittelteil, Slow-Mo auf
   dem Motiv-Höhepunkt. Aus einem solchen Clip darf **ein** Beat entstehen, nicht drei —
   sonst kippt der Reel in Wiederholung.

---

## 1. Musikplan (Grundgerüst des Bogens)

Zwei Pflicht-Tracks, keiner läuft komplett durch, fließender Crossfade statt Schnitt.
Form **A – B – A′**: der ruhige Track rahmt, der schnelle trägt den Aufbau und den Höhepunkt.

| Abschnitt | Zeit | Track | BPM | Funktion |
|---|---|---|---|---|
| A | 00:00 – 04:10 | *Naturaleza (Mose Edit)* | 68,9 | Auftakt, weit, atmend. Fade-in 3 s aus Schwarz. |
| — | 03:50 – 04:20 | **Crossfade A→B, 30 s** | — | überlappend, kein harter Wechsel |
| B | 04:10 – 09:25 | *Cuatro Vientos* | 147,7 | `gradual_build` bis zum Höhepunkt bei 08:40 |
| — | 09:10 – 09:40 | **Crossfade B→A′, 30 s** | — | Energie fällt, Bild wird wieder weit |
| A′ | 09:25 – 12:00 | *Naturaleza (Mose Edit)*, späterer, ruhigerer Abschnitt | 68,9 | Ausklang, Fade-out 3 s ins Schwarz |

**Schnittraster** (daraus leitet der `timeline-builder` die Beat-Sync-Punkte ab):

- 68,9 BPM → Beat 0,871 s, Takt 3,483 s. Verwendbare Clipdauern: **2 Takte ≈ 6,97 s**
  (im Pacing-Fenster), für den Ausklang **2,5–3 Takte ≈ 8,7–10,4 s** (bewusst über `max_s`,
  siehe Kapitel 9).
- 147,7 BPM → Beat 0,406 s, Takt 1,625 s. Verwendbare Dauern: **4 Takte = 6,50 s**,
  im Höhepunkt **3 Takte = 4,88 s**. 2 Takte (3,25 s) liegen unter `pacing.min_s` und sind
  verboten — dieser Reel darf nicht hacken.
- Übergänge liegen **auf** Phrasengrenzen (8 Takte), nicht auf einzelnen Beats. Der Höhepunkt
  bei 08:40 ist der einzige Punkt, an dem Bild- und Musikakzent hart zusammenfallen dürfen.

**Originalton:** `original_audio_policy: ambience_only` — bei Drohnenclips ist der Originalton
Rotorgeräusch, also **kein** O-Ton, keine O-Ton-Fenster im ganzen Film. Bewusste Abweichung vom
Preset-Default, begründet durch die Quelle. Die Musik trägt allein.

---

## 2. Kapitel

Summe der Beat-Dauern: **720,0 s = 12:00**, exakt auf Ziellänge.

### K0 — Schwarz, Titel · 00:00 – 00:22 (22 s)

Aus `transition_in: black`. Erste 3 s reines Schwarz, Musik blendet ein (`fade_in_s: 3`).
Ab 00:03 langsam aufblendendes Bild: **ein einziger** ruhiger Establisher, weit, kaum Bewegung —
Kandidat ist der Sonnenuntergangsflug vom 22.07. (`DJI_20260722215000`, goldene Stunde über
bewaldeten Hügeln) *oder* ein Waldsee-Shot vom 20.07. Ein Clip, 19 s Standzeit, sehr langsamer
Push — hier wird die Sehgewohnheit für den ganzen Film gesetzt.

Titel liegt darüber, langsam ein (2,5 s) / langsam aus (2,5 s), Standzeit ca. 8 s:
„Norwegen 2026", darunter kleiner „Drone Edit". Details siehe Abschnitt 4.

*Bemerkung zur Chronologie:* der 22.07.-Shot vor dem 20.07.-Material ist die **einzige**
zugelassene Abweichung von `chronological: true` — der Titelshot steht vor der Erzählung, nicht
in ihr. Nimmt der `timeline-builder` stattdessen den 20.07.-Waldsee, bleibt die Chronologie
lückenlos; beide Varianten sind vertretbar, die Entscheidung fällt am Keyframe.

### K1 — Sørlandet: Wald, Seen, weiches Licht · 00:22 – 02:15 (113 s)

**Material:** 20.07. (Hütte am Waldsee, Ruderboot, bewaldete Hügel), 22.07. (Skien, goldene Stunde).
**Rhythmus:** ~7,0 s je Beat (2 Takte Naturaleza) → **ca. 15 Clips**.
**Energie:** niedrig. Nur Establisher und langsame Vorwärtsflüge, keine schnellen Orbits.
**Übergänge:** überwiegend `slow_dissolve` (1,2 s), einzelne `fade`.
**Motiv:** Wasser + Wald. Weil das Motiv später wiederkehrt (Fjord, Fluss, Küste), hier bewusst
**ohne** Wasserfall und **ohne** Bergpanorama — der Film soll noch nichts von Norwegen zeigen,
was er später steigern will.
**Sync:** letzter Beat endet auf einer Phrasengrenze bei 02:15.

### K2 — Aufbruch ins Fjell · 02:15 – 03:50 (95 s)

**Material:** 23.07. (Geilo / Hakkesetstølen, 1041 m — See zwischen bewaldeten Bergen mit
Landzunge, `DJI_20260723140707`, Rating 4).
**Rhythmus:** ~6,9 s → **ca. 14 Clips**.
**Energie:** leicht steigend. Erstmals Höhe: Kamera darf steigen, Horizont wird weiter.
**Übergänge:** `slow_dissolve`, erster `speed_ramp` gegen Ende als Vorgriff auf K3.
**Sync:** 03:50 beginnt der 30-s-Crossfade in *Cuatro Vientos* — das Kapitelende ist der
akustische Wendepunkt des Films, dramaturgisch: „die Landschaft wird groß".

### K3 — Aurlandsfjellet & Aurlandsfjord · 03:50 – 05:55 (125 s)

**Material:** 24.07., der erste große Block: Passstraße am See durch karge Hochebene (Rating 4),
Hüttensiedlung mit rot-weißen Häusern von oben (Rating 4), Abendflug `DJI_20260724195421` über
dem Aurlandsfjord.
**Rhythmus:** 6,50 s (4 Takte Cuatro Vientos) → **ca. 19 Clips**.
**Energie:** mittel. Der Track ist schnell, der Schnitt bleibt langsam — der Kontrast ist
gewollt und trägt das ganze Mittelstück.
**Übergänge:** `speed_ramp` an Straßen- und Fahrtaufnahmen, `slow_dissolve` an Fjordblicken.
**Sync:** innerer Höhepunkt bei ca. 05:30 (Abendflug/Fjord im Gegenlicht) auf eine 8-Takt-Grenze.
**Achtung Wiederholung:** Straßenaufnahmen aus der Luft kommen auch in K4 und K8 vor — hier
maximal **drei**, sonst wird das Motiv verbraucht.

### K4 — Über die Pässe nach Geiranger · 05:55 – 07:40 (105 s)

**Material:** 26.07. (`2026-07-26_…_Geilo-Geiranger_Roadshots`, Gletscherseen, Wasserfälle,
Bergpässe) plus die Luftfotos an der Unterkunft Geiranger (`DJI_20260726165037…JPG` u. a.,
Ken-Burns `subtle`, je 6–7 s).
**Rhythmus:** 6,0 s → **ca. 17 Clips**.
**Energie:** deutlich steigend, die Musik trägt. Erste Slow-Mo-Passage auf einem Wasserfall.
**Übergänge:** `speed_ramp` (Pass hinauf), `slow_mo` (Wasser), gegen Ende kürzere `fade`s.
**Sync:** ab 07:20 zieht der Schnitt an (6,5 s → 5,5 s) und bereitet den Höhepunkt vor.
*Hinweis:* der 25.07. fehlt (Regen) und der 27.07. hat kein Drohnenmaterial — Geiranger wird
deshalb hier (Ankunft) und in K5 (Abfahrt) erzählt, nicht als eigener Ortsblock. Das fällt im
Reel nicht auf, weil er ohne Ortsnamen auskommt.

### K5 — HÖHEPUNKT: Trollstigen · 07:40 – 09:25 (105 s)

**Material:** 28.07. tagsüber (`2026-07-28_…_Geiranger-Lom_Roadshots`): Serpentinen aus der
Vogelperspektive, Gudbrandsjuvet, Nebel über den Graten. Der 152-s-Clip
(`DJI_20260728145455_0032…seg8`) ist hier der Kern — als **ein** verdichteter Beat von ca. 18 s:
Slow-Mo-Anflug → Ramp auf beschleunigte Fahrt über die Serpentinen → Ramp zurück in Slow-Mo auf
der Plattform.
**Rhythmus:** 5,0–5,5 s (3 Takte = 4,88 s als schnellste zugelassene Dauer) → **ca. 19 Clips**,
darunter der eine lange Ramp-Beat.
**Energie:** Maximum des Films.
**Musik-Sync-Punkt:** **08:40** — der einzige harte Akzent: Musikspitze und der weiteste
Trollstigen-Blick fallen framegenau zusammen. Davor 8 Takte Anlauf mit kürzer werdenden Beats,
danach sofort wieder ausatmen.
**Übergänge:** `speed_ramp` dominiert, keine Fades im Anlauf; nach 08:40 der erste lange
`slow_dissolve` als Erlösung.

### K6 — Mitternachtslicht in Lom · 09:25 – 10:25 (60 s)

**Material:** 28.07. abends (`DJI_20260728214940`, Aufnahme 21:49, Lom — Stabkirche, türkisfarbener
Fluss, Brücken im späten Licht).
**Rhythmus:** 7,5 s → **ca. 8 Clips**.
**Energie:** fällt. Hier läuft der 30-s-Crossfade zurück in *Naturaleza* (09:10–09:40) — Bild und
Musik beruhigen sich gemeinsam.
**Übergänge:** ausschließlich `slow_dissolve` (1,5 s) und `fade`.
**Funktion:** der Nachhall des Höhepunkts. Ohne dieses Kapitel wirkt der Film hinten abgeschnitten.

### K7 — Valdresflye & Uvdal · 10:25 – 11:10 (45 s)

**Material:** 29.07. (`DJI_20260729154156`, Hochebene Valdresflye, Rating 4 — der höchste Punkt
der Reise) und 30./31.07. (Uvdal, rote Fußgängerbrücke über flachem Fluss, `DJI_20260730114813`).
**Rhythmus:** 6,5–7 s → **ca. 7 Clips**.
**Energie:** niedrig, aber noch nicht Schluss. Nach der Weite der Hochebene bewusst das kleine
Motiv: Fluss, Brücke, zwei Kinder von oben — der Film kommt vom Erhabenen zurück ins Menschliche.
**Auszuschließen:** der 31.07.-Clip mit `exclude: true`.

### K8 — Letzte Passstraße · 11:10 – 11:35 (25 s)

**Material:** 01.08. (`DJI_20260801125246`, Uvdal → Skien, Rennradfahrer auf der Passstraße).
**Rhythmus:** ~6,2 s → **ca. 4 Clips**.
**Energie:** ruhig, gleichmäßig. Eine kurze, letzte Bewegung nach vorn — das Straßenmotiv aus K3
kehrt wieder, jetzt leer und langsam statt aufbauend.
**Übergänge:** `slow_dissolve`.

### K9 — Schärenküste, Abschied · 11:35 – 12:00 (25 s)

**Material:** 03.08. (`DJI_20260803155043`, Angelplatz bei Langesund — türkise Bucht, Felsen,
Sandbucht; ein Clip Rating 5 mit Personen, `usable_as: hero`).
**Rhythmus:** **2 Clips**, ca. 9 s und 13 s — bewusst über `pacing.max_s`. Am Filmende ist die
Länge das Stilmittel; der Beat-Takt hat hier nichts mehr zu suchen.
**Ablauf:** letzter Beat ist der weiteste Blick über die Schärenküste, sehr langsamer Rückwärts-
oder Aufwärtsflug. Ab 11:57 `fade` ins Schwarz (`transition_out: black`), Musik `fade_out_s: 3`
parallel — Bild und Ton enden gemeinsam, kein hartes Abschneiden.
**Bewusste Entscheidung:** dass im letzten Bild Menschen vorkommen, ist gewollt. Der Reel ist
zwölf Minuten lang menschenleer; die Familie am Wasser als Schlussakkord gibt dem Ganzen
rückwirkend einen Grund.

---

## 3. Prüfsumme

| Kapitel | Dauer (s) | Clips (Richtwert) | Energie |
|---|---:|---:|---|
| K0 Titel | 22 | 1 | — |
| K1 Sørlandet | 113 | 15 | niedrig |
| K2 Ins Fjell | 95 | 14 | steigend |
| K3 Aurlandsfjellet | 125 | 19 | mittel |
| K4 Pässe nach Geiranger | 105 | 17 | steigend |
| K5 Trollstigen | 105 | 19 | **Maximum** |
| K6 Lom, Abendlicht | 60 | 8 | fallend |
| K7 Valdresflye/Uvdal | 45 | 7 | niedrig |
| K8 Passstraße | 25 | 4 | niedrig |
| K9 Küste, Ausklang | 25 | 2 | Ausklang |
| **Summe** | **720** | **≈ 106** | |

Reicht das Material in einem Kapitel nicht für die geplante Clipzahl, wird **nicht** aus einem
Nachbarkapitel aufgefüllt (das bräche die Chronologie), sondern die Beats dieses Kapitels werden
länger — bis 9 s ist das im Stil gedeckt. Erst wenn ein Kapitel dadurch über 9 s je Beat käme,
wird es gekürzt und die Differenz auf K3/K4/K5 verteilt, wo das meiste Material liegt.

---

## 4. Intro-Grafik — offene Frage an den Nutzer

Das bestehende Template `templates/svg/title-card.svg` kann:

- `{{title}}` groß, zentriert auf 46 % Höhe, `font_display`, `text_color` `#ffffff`
- `{{subtitle}}` kleiner, zentriert auf 58 % Höhe, in `accent_color` `#e0a458`
- `{{background_layer}}` — optionale, generierte Hintergrundgrafik

Damit sind **„Norwegen 2026" groß + „Drone Edit" kleiner darunter" abgedeckt**, ebenso das
langsame Ein-/Ausblenden (über die Overlay-Dauern, nicht über das Template).

**Nicht abgedeckt sind zwei Punkte aus dem Brief:**

1. *„versetzt darunter"* — das Template zentriert die Unterzeile starr; eine seitliche
   Versetzung gibt es nicht.
2. *`motif: norwegian_flag_optional`* — es gibt keinen Flaggen-Slot, nur `background_layer`.

Laut Brief wird hier **nicht improvisiert**. Vorschlag für den Grafik-Prompt, den der Nutzer
freigeben oder ändern soll:

> Minimalistische, sehr dezente Titel-Hintergrundgrafik im Format 3840×2160, überwiegend
> transparent/dunkel (`#12222f`). Links unten, klein und zurückhaltend, das norwegische
> Flaggenkreuz als reduziertes Grafikelement (nicht als Rechteckflagge), in gedecktem Rot und
> gebrochenem Weiß, Deckkraft ca. 35 %, weiche Kanten. Kein Text, keine Rahmen, kein Verlauf über
> die Bildmitte — die Grafik liegt über einem Drohnen-Establisher und darf ihn nicht zudecken.

**Fallback, falls der Nutzer keine Grafik will:** Template unverändert nutzen, Flagge weglassen,
Unterzeile zentriert. Der Export ist dadurch nicht blockiert — Kapitel K0 funktioniert in beiden
Varianten identisch.
