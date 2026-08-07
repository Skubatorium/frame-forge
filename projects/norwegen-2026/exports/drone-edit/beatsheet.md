# Beat-Sheet — `norwegen-2026` / `drone-edit`

**Revision 2** (nach Preview-Feedback des Nutzers). Revision 1 lag bei 12:00 / 720 s mit drei
Musikabschnitten, Foto-Ken-Burns in K4 und Hyperlapse-Ramps. Alles drei ist raus. Die tragenden
Entscheidungen aus Revision 1 bleiben: **chronologisch**, **Establisher-Bildsprache**,
**K5 Trollstigen als Höhepunkt**, **K9 Menschen am Wasser als Ausklang**, Golden-Hour-Titelshot.

**Preset:** `nordic-cinematic` · **Ziellänge:** **9:28 (568 s)** · **Sprache:** de
**Auswahl:** ausschließlich `source: drone` **und `kind: video`**, `rating >= 3`, `exclude != true` · **chronologisch**
**Karte:** keine · **Text:** nur Intro-Titel · **Farbe:** `color_match: soft`, kühle Lichter / warme Spitzen, mittlerer Kontrast

Der Bogen des Presets bleibt die Vorlage: *ruhiger Auftakt → behutsamer Aufbau über die Etappen →
ein emotionaler Höhepunkt → stiller Ausklang.* `music_energy_curve: gradual_build`, der
Schnittrhythmus entwickelt sich also über den Film: K1–K2 am oberen Ende des Pacing-Fensters
(≈7 s), das Mittelstück auf 6,5 s, der Höhepunkt auf 4,9 s (nie darunter — `pacing.min_s = 4`),
der Ausklang wieder auf 6,5–13 s.

---

## 0. Was sich gegenüber Revision 1 ändert (Änderungsliste für den `timeline-builder`)

| # | Änderung | Konsequenz |
|---|---|---|
| 1 | **Keine Fotos, kein Ken-Burns.** Der Reel ist reines Drohnen-**Video**. | K4: `20260726-drone-dd243f` und `20260726-drone-8a347b` (Drohnen-JPGs, im alten `timeline.json` `c064`/`c065` mit `kenburns`-Effekt) **ersatzlos raus**. Ersatz nur aus 26.07.-Videomaterial, auch wenn der Ersatz kürzer/schwächer ist. Läuft das Material aus, werden die Nachbar-Beats in K4 länger — **nie** ein Foto einsetzen. Global: `kind: photo` ist aus der Auswahl ausgeschlossen. |
| 2 | **Musik nur noch 2 Abschnitte.** Der dritte Abschnitt (Naturaleza-Reprise ab 550 s, `music-a2`) entfällt komplett. | Neue Gesamtlänge **568 s**. Der 30-s-Crossfade B→A′ und damit der hallige/„schallende" Übergang im Bereich Lom entfällt mitsamt Ursache. Der **gelobte Übergang A→B bei 230–260 s („Wind in den Bergen" → Bergfelsen) bleibt unverändert stehen** — Zeitlage, Länge und Kapitelgrenze K2/K3 dürfen dort nicht angefasst werden. |
| 3a | **Instabile Clips raus.** `20260730-drone-4abe2d` (rote Fußgängerbrücke, zwei angelnde Jungen, Uvdal — `stability 0.0`, Schwenk mitten im Take) ist **gesperrt**, wie ein `forbidden_shot` zu behandeln. | K7 verliert seinen bisherigen Schlussbeat (`c094`). Generell: Clips mit Schwenk/Unruhe **mitten** im Take meiden, auch wenn Anfang und Ende ruhig wirken. Bei `stability < 0.35` nur verwenden, wenn ein nachweislich ruhiges Fenster von voller Beat-Länge existiert. |
| 3b | **Keine Timelapse-/Hyperlapse-Beats.** `speed > 1.0` ist im ganzen Film verboten. | Betroffen: `c073` (Trollstigen-Mittelteil, `speed 11.43`) → **raus**; `c056`/`c058` (`20260726-drone-7206fd`, `20260726-drone-73d4f8`, `speed 1.5`) und `c068` (`20260728-drone-eab4d9`, `speed 1.3`) → auf `speed 1.0` mit **kürzerem Ausschnitt**. Slow-Mo (`speed < 1.0`) bleibt erlaubt und erwünscht. |
| 3c | **Regeländerung gegenüber Revision 1:** lange Clips werden jetzt **beschnitten statt gerampt**. | Die alte Vorgabe „152-s-Clips nicht kürzen, sondern filmisch verdichten (Ramp rein, beschleunigter Mittelteil, Ramp raus)" ist durch das Nutzer-Feedback **aufgehoben**. Neu: aus einem langen Clip das ruhigste, stärkste Fenster von Beat-Länge herausschneiden, Rest verwerfen. |
| 4 | **Mehr Top-Down / Vogelperspektive.** | Pro Kapitel **ein** senkrechter Draufsicht-Shot als Akzent (Slots siehe Abschnitt 3). Der Nutzer hat einen Fluss von senkrecht oben ausdrücklich gelobt. |
| 5 | **Neuer Beat: Möwe.** `20260803-drone-574c7c` (seg16, Angelplatz bei Langesund, 75 s, Rating 5). | Eigener Beat in K9, grob `src_in ≈ 26–28 s` bis `≈ 32–34 s`. Die Möwe steht **nicht** in der Index-Beschreibung — sie wurde zwischen den Analyse-Keyframes verpasst. Der `timeline-builder` verfeinert die Grenzen am tatsächlichen Material. |
| 6 | **Weniger zufällige Wiederholung, mehr bewusste Mini-Sequenzen.** | Die Kreuzfahrtschiff-Sequenz in K3 (weit → näher → Bogen ums Schiff) wurde gelobt und bleibt als **zusammenhängender Dreier**. Nach diesem Muster sind zwei weitere Mini-Sequenzen gesetzt (K5 Serpentinen, K9 Felseninsel). Umgekehrt: dasselbe Motiv nicht verstreut über mehrere Kapitel wiederholen. |
| 7 | **Bevorzugter Bewegungsstil: Aufblenden von unten nach oben** (Kamera steigt/tiltet aus einer tiefen Lage episch nach oben). | Vier reservierte Slots: K0, K3, K5-Klimax, K9-Schlussbild. |
| 8 | **Crossfades kürzer.** Die Standard-`slow_dissolve` von 1,2–2,0 s erzeugte einen „Schlier". | Neue Defaults und Empfehlung pro Übergang in Abschnitt 4. |

**Nicht in diesem Beat-Sheet geregelt** (separat behandelt): die Bewegungsanimation der
Intro-Titelgrafik — das ist ein Render-Feature. K0 bleibt hier wie gehabt beschrieben.

---

## 1. Materiallage

Drohnenmaterial in tagesbenannten Ordnern (`2026-07-2x_…/Vorauswahl/DJI_*.MP4`, 4K, 59,94 fps,
HEVC). Die `DJI_*.JPG` im selben Ordner sind **ab dieser Revision nicht mehr Teil der Auswahl**.

| Tag | Etappe | Drohnen-**Video** | Rolle |
|---|---|---|---|
| 17.–19.07. | Anreise, Fähre | keins | entfällt |
| 20.07. | Skien / Hütte am Waldsee | ja | Auftakt |
| 21.07. | Küste Langesund | keins | entfällt |
| 22.07. | Skien, goldene Stunde (`20260722-drone-e0e4c2`, Rating 4) | ja | **Titelshot** |
| 23.07. | Geilo / Hakkesetstølen (Rating 4) | ja | Aufbruch ins Fjell |
| 24.07. | Geilo → Aurland, inkl. **Kreuzfahrtschiff im Fjord** | viel | erster großer Block |
| 25.07. | Aurland | keins (Regen) | Lücke, unproblematisch |
| 26.07. | Aurland → Geiranger, Roadshots | ja (Video); **JPGs ab jetzt gesperrt** | Anstieg |
| 27.07. | Geiranger | keins | über 26./28.07. erzählt |
| 28.07. | Geiranger → Lom, inkl. 152-s-Clip `20260728-drone-3feda7`, dazu Abendflug Lom | viel | **Höhepunkt + Nachhall** |
| 29.07. | Lom → Uvdal, Valdresflye (Rating 4) | ja | Abstieg |
| 30./31.07. | Uvdal, Hütte am Fluss | ja — aber `4abe2d` gesperrt, `31.07.`-Clip `exclude: true` | dünn |
| 01.08. | Uvdal → Skien, Passstraße | **im Preview nicht verwendet** — siehe K8 | bedingt |
| 03.08. | Angelplatz Langesund (`991503`, `5601da`, `d1eb17`, **`574c7c` Möwe**, Rating 5) | ja, stärkstes Material der Rückreise | Ausklang |
| 04.08. | Rückreise | keins | entfällt |

**Muss-Shots / verbotene Shots im Brief:** beide leer. Der Nutzer hat nachträglich **einen**
verbotenen Shot benannt (`20260730-drone-4abe2d`) und **einen** Muss-Shot (`20260803-drone-574c7c`,
Möwenfenster). Beide sind oben verbindlich eingearbeitet.

**Offene Materialfrage (ehrlich vermerkt, nicht überspielt):**

- **01.08., Passstraße/Rennradfahrer.** Revision 1 hatte dafür ein eigenes Kapitel K8 vorgesehen,
  im gerenderten `timeline.json` taucht **kein einziges 01.08.-Asset** auf (die Videospur springt
  von `20260730-…` direkt auf `20260803-…`). Vermutlich fällt das Material durch den
  `min_rating: 3`-Filter oder ist `exclude: true`. K8 bleibt deshalb als **bedingtes** Kapitel
  stehen, mit definiertem Fallback (siehe K8).
- **Top-Down-Shots.** Ich habe die konkreten Asset-IDs bewusst **nicht** geraten. Der
  `timeline-builder` löst die Slots in Abschnitt 3 per Index-Abfrage auf:
  `query … --source drone --min-rating 3` und dann Filter auf Summary/Tags mit
  *von oben, senkrecht, Vogelperspektive, Draufsicht, top-down, Luftbild, Flusslauf, Küstenlinie*.
  Findet sich für einen Slot nichts, bleibt der Slot **leer** und der Nachbar-Beat wird länger —
  kein Ersatz durch einen weiteren Frontalflug.

---

## 2. Musikplan

**Zwei Abschnitte statt drei.** Der ruhige Track eröffnet, der schnelle trägt Aufbau, Höhepunkt
und Ausklang. Form **A – B**.

| Abschnitt | Zeit | Track | BPM | Funktion |
|---|---|---|---|---|
| A | 00:00 – 04:20 (0–260 s) | *Naturaleza (Mose Edit)* | 68,9 | Auftakt, weit, atmend. `fade_in_s: 3` aus Schwarz. |
| — | **03:50 – 04:20 (230–260 s)** | **Crossfade A→B, 30 s** | — | **unverändert lassen.** Vom Nutzer gelobt („hat sich angehört, als wäre der Wind in den Bergen"). Bild wechselt hier von Fjell auf Bergfelsen. |
| B | 03:50 – 09:28 (230–568 s) | *Cuatro Vientos* (`src_in: 0`) | 147,7 | `gradual_build` bis zum Höhepunkt bei **07:31**, danach getragener Ausklang. |
| — | 09:25 – 09:28 | `fade_out_s: 3` ins Schwarz | — | siehe Warnung unten |

**Streichung:** `music-a2` (Naturaleza-Reprise, alt `tl_in: 550`, `src_in: 272.196`) entfällt.
Damit verschwindet der zweite 30-s-Crossfade — und mit ihm der „schallende"/hallige Klang im
letzten Drittel, der das eigentliche Problem war.

> **Warnung an den `render-engineer`:** Der Film endet jetzt auf dem schnellen Track. Ein harter
> 3-s-Fadeout aus voller Energie wirkt abgeschnitten. Prüfen, ob *Cuatro Vientos* zwischen
> Sekunde 320 und 338 (Filmzeit 550–568 s) von selbst zurücknimmt. Tut er das nicht,
> `fade_out_s` auf **10–12 s** verlängern (ab ca. 556 s) — der Bildfade ins Schwarz bleibt bei
> 3 s. Das ist eine bewusst zugelassene Abweichung von `audio.fade_out_s: 3` im Brief.

**Schnittraster:**

- 68,9 BPM → Beat 0,871 s, Takt 3,483 s, Phrase (8 Takte) 27,87 s. Beat-Länge in K1/K2:
  **2 Takte ≈ 6,97 s**.
- 147,7 BPM → Beat 0,406 s, Takt 1,625 s, **Phrase (8 Takte) = 13,00 s**. Beat-Längen:
  **4 Takte = 6,50 s** (Normalfall), **3 Takte = 4,875 s** (nur im Höhepunkt),
  **8 Takte = 13,00 s** (Klimaxbild und Schlussbild). 2 Takte (3,25 s) liegen unter
  `pacing.min_s` und sind verboten.
- **Alle Kapitelgrenzen ab K3 liegen exakt auf einer 13,0-s-Phrasengrenze.** Das ist beim
  Umlegen von Dauern zu erhalten: Kapitellängen ab K3 nur in Vielfachen von 13 s verschieben.

**Originalton:** `original_audio_policy: ambience_only`. Bei Drohnenclips ist der O-Ton
Rotorgeräusch → **kein O-Ton, keine O-Ton-Fenster im ganzen Film**. Musik trägt allein.

---

## 3. Kapitel

Summe der Beat-Dauern: **568,0 s = 9:28**.

### K0 — Schwarz, Titel · 00:00 – 00:22 (22 s)

Unverändert aus Revision 1 (funktionierte). `transition_in: black`, erste 3 s reines Schwarz,
Musik blendet ein. Ab 00:03 langsam aufblendend **ein einziger** Establisher: der
Sonnenuntergangsflug vom 22.07. (`20260722-drone-e0e4c2`, goldene Stunde) — der Golden-Hour-Einstieg
wurde ausdrücklich gelobt und bleibt. 19 s Standzeit, sehr langsamer Push, `speed ≈ 0.85`.

**Bewegungs-Slot „Aufblenden von unten nach oben" (1/4):** wenn der Clip ein Fenster hat, in dem
die Kamera aus tiefer Lage steigt, dieses Fenster nehmen — das ist der ideale erste Bildeindruck.

Titel darüber: 2,5 s ein / ca. 8 s Standzeit / 2,5 s aus. Grafik siehe Abschnitt 5.

*Chronologie-Ausnahme:* der 22.07.-Shot steht vor dem 20.07.-Material. Einzige zugelassene
Abweichung von `chronological: true` — der Titelshot steht vor der Erzählung, nicht in ihr.

### K1 — Sørlandet: Wald, Seen, weiches Licht · 00:22 – 02:15 (113 s)

**Material:** 20.07. (Hütte am Waldsee, Ruderboot, bewaldete Hügel), 22.07. (Skien).
**Rhythmus:** ~6,97 s (2 Takte Naturaleza) → **ca. 16 Beats**.
**Energie:** niedrig. Nur Establisher und langsame Vorwärtsflüge, keine Orbits.
**Top-Down-Slot (1/6):** **ein** senkrechter Blick auf die Seeoberfläche / das Ruderboot / den
Waldrand, am besten als Abschluss der ersten Dreiergruppe. Genau einer — der Effekt wird sonst
zur Masche, bevor der Film ihn im Höhepunkt braucht.
**Motiv-Disziplin:** kein Wasserfall, kein Bergpanorama. Der Film soll noch nichts zeigen, was er
später steigern will.
**Übergänge:** kurze `slow_dissolve` **0,6 s** (Revision 1: 1,2 s — zu lang). Siehe Abschnitt 4.

### K2 — Aufbruch ins Fjell · 02:15 – 03:50 (95 s)

**Material:** 23.07., Geilo / Hakkesetstølen, 1041 m — See zwischen bewaldeten Bergen mit
Landzunge (Rating 4).
**Rhythmus:** ~6,97 s → **ca. 14 Beats**.
**Energie:** leicht steigend. Erstmals Höhe, der Horizont wird weiter.
**Top-Down-Slot (2/6):** See mit Landzunge von senkrecht oben — die Landzunge als Grafik im Bild.
**Kein `speed_ramp` mehr am Kapitelende** (Revision 1 hatte hier einen Vorgriff auf K3; Ramps sind
raus). Stattdessen: der letzte Beat ist der weiteste, ruhigste Blick des Kapitels.
**Sync:** bei **230 s** beginnt der 30-s-Crossfade in *Cuatro Vientos*. Dieser Punkt ist gesetzt
und der akustische Wendepunkt des Films — **nicht verschieben**.

### K3 — Aurlandsfjellet & Aurlandsfjord · 03:50 – 05:21 (91 s = 7 Phrasen)

**Material:** 24.07.: Passstraße am See durch karge Hochebene (Rating 4), Hüttensiedlung von oben
(Rating 4), Abendflug `20260724195421` über dem Aurlandsfjord, **Kreuzfahrtschiff im Fjord**.
**Rhythmus:** 6,50 s (4 Takte) → **14 Beats**.
**Energie:** mittel. Der Track ist schnell, der Schnitt bleibt langsam — dieser Kontrast trägt das
Mittelstück.

**Mini-Sequenz A — Kreuzfahrtschiff (gelobt, bleibt zusammen):** drei aufeinanderfolgende Beats
aus demselben Motiv, in dieser Reihenfolge: (1) weit, Schiff klein im Fjord, (2) näher heran,
(3) Bogen um das Schiff. **Zwischen diesen drei Beats harte Schnitte** (kein Dissolve) — das hält
die Sequenz als eine Bewegung zusammen. Platzierung: Beats 9–11, also im hinteren Drittel des
Kapitels, als innerer Höhepunkt bei ca. **05:05**.

**Bewegungs-Slot „unten nach oben" (2/4):** der Fjord-Reveal im Abendlicht — Kamera steigt aus dem
Schatten über die Felskante, der Fjord öffnet sich. Direkt vor der Schiffsequenz.
**Top-Down-Slot (3/6):** die Passstraße von senkrecht oben (Straße als Linie durch die Hochebene)
oder die Hüttensiedlung.
**Achtung Wiederholung:** Straßen-aus-der-Luft kommt auch in K4 und K8 vor — hier **maximal drei**
Straßen-Beats.

### K4 — Über die Pässe nach Geiranger · 05:21 – 06:26 (65 s = 5 Phrasen)

**Material:** ausschließlich 26.07.-**Video** (`Geilo-Geiranger_Roadshots`: Gletscherseen,
Wasserfälle, Bergpässe). **Die beiden Luftfotos sind raus** (`20260726-drone-dd243f`,
`20260726-drone-8a347b`).
**Rhythmus:** 6,50 s → **10 Beats**.
**Energie:** deutlich steigend, die Musik trägt. Eine Slow-Mo-Passage auf einem Wasserfall
(`speed 0.55`, wie in Revision 1 — das funktionierte).
**Geschwindigkeit:** die bisherigen `speed 1.5`-Beats (`7206fd`, `73d4f8`) laufen jetzt auf
`speed 1.0` mit entsprechend kürzerem Ausschnitt. Der Beat wird dadurch nicht kürzer als 6,5 s —
notfalls ein anderes Fenster desselben Clips wählen.
**Top-Down-Slot (4/6):** Gletschersee oder Wasserfall von senkrecht oben.
**Fehlt Material** (durch die gestrichenen Fotos ist K4 der wackligste Punkt des Films):
Beats bis 9 s dehnen, notfalls K4 auf 52 s (4 Phrasen) kürzen und die 13 s an K5 geben. **Nicht**
mit Fotos, nicht mit 24.07.- oder 28.07.-Material auffüllen (bräche die Chronologie).
*Hinweis:* 25.07. fehlt (Regen), 27.07. hat kein Drohnenmaterial — Geiranger wird über Ankunft
(K4) und Abfahrt (K5) erzählt. Fällt im Reel nicht auf, weil er ohne Ortsnamen auskommt.

### K5 — HÖHEPUNKT: Trollstigen · 06:26 – 07:44 (78 s = 6 Phrasen)

**Material:** 28.07. tagsüber (`Geiranger-Lom_Roadshots`): Serpentinen aus der Vogelperspektive,
Gudbrandsjuvet, Nebel über den Graten. Kernclip weiterhin `20260728-drone-3feda7` (152 s).

**Aufbau (das ist die zentrale Korrektur dieser Revision):**

| Beats | Dauer | Inhalt |
|---|---|---|
| 1–4 | 4 × 6,50 s = 26 s | Anlauf: Grate, Nebel, Gudbrandsjuvet. Energie zieht an. |
| 5–12 | 8 × 4,875 s = 39 s | Verdichtung. Kürzeste zugelassene Beats des Films. **Mini-Sequenz B — Serpentinen:** Beats 8–10 aus demselben Serpentinen-Motiv, weit → seitlich mitfliegend → **senkrecht von oben** (Top-Down-Slot 5/6, der stärkste des Films: die Serpentinen als Grafik). |
| 13 | 13,00 s (8 Takte) | **KLIMAX bei 07:31 (451 s)** — weitester Trollstigen-Blick, **Bewegungs-Slot „unten nach oben" (3/4)**: Kamera steigt langsam auf, das Tal öffnet sich. Einziger Punkt im Film, an dem Bild- und Musikakzent framegenau zusammenfallen. |

**Der alte Dreier-Beat aus `3feda7` wird entzerrt:** `c072` (Slow-Mo-Anflug, `speed 0.67`) und
`c074` (Slow-Mo-Ausklang auf der Plattform, `speed 0.68`) waren gut und bleiben — aber **nicht
mehr direkt hintereinander**. Der beschleunigte Mittelteil `c073` (`speed 11.43`, 10→90 s) wird
**gestrichen**. An seine Stelle kommt der Top-Down-Serpentinen-Shot aus anderem Material; findet
sich keiner, ein ruhiges drittes Fenster desselben Clips bei `speed 1.0`. Zwischen den beiden
Slow-Mo-Teilen liegen mindestens zwei fremde Beats, damit die Herkunft aus einem Clip nicht auffällt.
**Übergänge:** im Anlauf und in der Verdichtung **harte Schnitte** auf den Taktdownbeat, keine
Dissolves. Erst **nach** 07:31 der erste lange `slow_dissolve` (1,5 s) als Erlösung.

### K6 — Mitternachtslicht in Lom · 07:44 – 08:23 (39 s = 3 Phrasen)

**Material:** 28.07. abends (`20260728214940`, 21:49, Lom — Stabkirche, türkisfarbener Fluss,
Brücken im späten Licht).
**Rhythmus:** 6,50 s → **6 Beats**.
**Energie:** fällt. Die Musik läuft weiter (kein Trackwechsel mehr an dieser Stelle — genau hier
lag der hallige Übergang), die Beruhigung passiert jetzt **rein über das Bild**: längere
Brennweiten-Wirkung, kaum Eigenbewegung, Wasser statt Fels.
**Top-Down-Slot (6/6) — der wichtigste für das Nutzerfeedback:** der **türkisfarbene Fluss von
senkrecht oben**. Das ist mit hoher Wahrscheinlichkeit der Shot, den der Nutzer gemeint hat
(„Fluss von senkrecht oben, sieht super aus"). Als Beat 3 oder 4 setzen, mit voller 6,5 s, davor
und danach ein Schrägblick — der Kontrast senkrecht/schräg ist die Wirkung.
**Funktion:** Nachhall des Höhepunkts. Ohne dieses Kapitel wirkt der Film hinten abgeschnitten.

### K7 — Valdresflye & Uvdal · 08:23 – 08:49 (26 s = 2 Phrasen)

**Material:** 29.07. (Valdresflye, Hochebene, Rating 4 — höchster Punkt der Reise) und 30.07.
(Uvdal, Fluss an der Hütte, `20260730-drone-e02ec6`).
**Rhythmus:** 6,50 s → **4 Beats**.
**Gestrichen:** `20260730-drone-4abe2d` (rote Fußgängerbrücke / angelnde Jungen) — gesperrt wegen
Instabilität. Damit verliert K7 seinen bisherigen Schlussbeat; ersetzt durch einen vierten
29.07.-Shot oder einen ruhigen zweiten Uvdal-Flussblick.
**Energie:** niedrig. Nach der Weite der Hochebene das kleinere Motiv: Fluss, Uferlinie.
**Auszuschließen** außerdem: der 31.07.-Clip mit `exclude: true` („Drohne in Ast").

### K8 — Letzte Passstraße · 08:49 – 09:02 (13 s = 1 Phrase) — **bedingt**

**Material:** 01.08. (`20260801125246`, Uvdal → Skien, Rennradfahrer auf der Passstraße).
**Rhythmus:** 6,50 s → **2 Beats**. Das Straßenmotiv aus K3 kehrt wieder, jetzt leer und langsam.

> **Fallback, wenn kein 01.08.-Drohnenclip die Filter passiert** (im Preview war keiner in der
> Timeline): K8 **entfällt ersatzlos**, und die 13 s gehen an **K9**, das damit auf 39 s
> (3 Phrasen) wächst. Die Gesamtlänge und das Phrasenraster bleiben in beiden Varianten exakt
> gleich. Der `timeline-builder` entscheidet das per Query, nicht per Vermutung.

### K9 — Schärenküste, Möwe, Abschied · 09:02 – 09:28 (26 s = 2 Phrasen; mit K8-Fallback 39 s)

**Material:** 03.08., Angelplatz bei Langesund — `20260803-drone-574c7c` (**neu**, 75 s, Rating 5),
`20260803-drone-991503`, `20260803-drone-5601da`, `20260803-drone-d1eb17`.

**Mini-Sequenz C — Felseninsel (nach dem Vorbild der Kreuzfahrtschiff-Sequenz):**

| Beat | Dauer | Inhalt |
|---|---:|---|
| 1 | 6,50 s | **MÖWEN-BEAT.** `20260803-drone-574c7c`, `src_in ≈ 26–28 s`, `src_out ≈ 32–34 s`. Die Möwe fliegt ruhig durchs Bild und lässt sich mitverfolgen. Steht nicht im Index — der `timeline-builder` sichtet das Fenster und setzt die Grenzen so, dass die Möwe **vollständig** im Beat liegt, notfalls 5,0–8,0 s statt 6,5 s (Beat-Grenze darf hier vom Raster abweichen, das Motiv hat Vorrang). Kein Slow-Mo. |
| 2 | 6,50 s | Anflug auf die Felseninsel mit der einzelnen Kiefer, Sonnenglitzern auf dem Wasser — späteres Fenster aus **demselben** Clip `574c7c` oder `991503`/`5601da`. Bewusste Motivwiederholung im Sinn der gelobten Schiffsequenz. |
| (3) | (13,00 s) | *nur im K8-Fallback:* Bogen/Umkreisung der Insel bzw. türkise Bucht von oben. |
| letzter | 13,00 s | **Schlussbild.** Weitester Blick über die Schärenküste. **Bewegungs-Slot „unten nach oben" (4/4):** sehr langsamer Aufwärts-/Rückwärtsflug. Kandidat: `20260803-drone-d1eb17`. Ab 09:25 `fade` ins Schwarz (`transition_out: black`), Musik parallel aus. |

**Bewusste Entscheidung (bleibt aus Revision 1):** dass im Schlussbild Menschen vorkommen, ist
gewollt. Der Reel ist neun Minuten lang menschenleer; die Familie am Wasser als Schlussakkord gibt
dem Ganzen rückwirkend einen Grund. Die Möwe davor ist das erste Lebewesen im Film — sie bereitet
diesen Wechsel vor, statt ihn abrupt zu setzen.

---

## 4. Übergänge — Empfehlung pro Kapitelgrenze

Das Preview-Feedback war eindeutig: mehrere Überblendungen waren zu lang und erzeugten einen
„Schlier" zwischen zwei Clips. Ursache war die pauschale `slow_dissolve` mit 1,2–2,0 s.

**Neue Faustregeln:**

1. **Dissolve-Default innerhalb eines Kapitels: 0,5–0,7 s** (statt 1,2 s).
2. **Nie zwei Clips überblenden, die beide eine deutliche Eigenbewegung haben** — das ist genau
   der Schlier. Bewegung auf Bewegung → **harter Schnitt** auf den Downbeat.
3. **Dissolve-Länge ≤ 25 % des kürzeren der beiden Clips.** Bei 4,875-s-Beats in K5 heißt das:
   praktisch nur harte Schnitte.
4. **Lange Blenden (≥ 1,5 s) sind ein Stilmittel und bleiben drei Stellen vorbehalten:**
   Intro-Aufblende, Erlösung nach dem Klimax, Schlussfade.

| Übergang | Zeit | Revision 1 | **Empfehlung Revision 2** | Warum |
|---|---:|---|---|---|
| Schwarz → K0 | 00:00 | `fade` 3,0 s | **`fade` 3,0 s — unverändert** | Aufblende aus Schwarz, gelobt |
| K0 → K1 | 00:22 | `slow_dissolve` 1,2 s | **`slow_dissolve` 1,2 s — unverändert** | Titel geht ins Bild über, hier ist weich richtig |
| K1 intern | | 1,2 s | **0,6 s** | Hauptquelle des Schliers |
| K1 → K2 | 02:15 | 1,2 s | **1,0 s** | Ortswechsel, minimal weicher als intern |
| K2 intern | | 1,2 s | **0,6 s** | |
| **K2 → K3** | **03:50** | 1,2 s + Musik-Crossfade | **1,2 s — NICHT anfassen** | der vom Nutzer gelobte Wind→Bergfelsen-Moment |
| K3 intern | | 1,2 s | **0,5 s**, Schiffsequenz **hart** | Bewegung auf Bewegung |
| K3 → K4 | 05:21 | 1,2 s | **harter Schnitt** | neuer Ort auf Phrasendownbeat, klarer als eine Blende |
| K4 intern | | 1,2 s | **0,5 s**; Einstieg in die Wasserfall-Slow-Mo **hart** | Slow-Mo wirkt nur, wenn sie schlagartig beginnt |
| K4 → K5 | 06:26 | 1,2 s | **harter Schnitt** | der Höhepunkt soll unvermittelt anfangen |
| K5 intern | | `speed_ramp`/1,2 s | **durchgehend harte Schnitte** | Beats sind 4,875 s, jede Blende frisst 25 % |
| K5 Klimax-Ausgang | 07:44 | — | **`slow_dissolve` 1,5 s** | einzige lange Blende im Mittelteil, „Erlösung" |
| K5 → K6 | 07:44 | 2,0 s | **1,5 s** | siehe oben, aber 2,0 s war zu viel |
| K6 intern | | 1,5 s | **0,8 s** | ruhiges Kapitel, darf etwas weicher sein |
| K6 → K7 | 08:23 | 1,5 s | **1,0 s** | |
| K7 intern | | 1,3 s | **0,6 s** | |
| K7 → K8 | 08:49 | 1,3 s | **harter Schnitt** | letzte Bewegung setzt neu an |
| K8 → K9 | 09:02 | 1,5 s | **1,2 s** | Ankunft am Meer, hier darf es atmen |
| K9 intern | | 1,5–2,0 s | **1,0 s** zwischen Möwe und Insel, **1,5 s** vor dem Schlussbild | am Ende ist Länge Stilmittel |
| K9 → Schwarz | 09:25 | `fade` 3,0 s | **`fade` 3,0 s — unverändert** | |

---

## 5. Prüfsumme

| Kapitel | Zeit | Dauer (s) | Phrasen (13 s) | Beats | Energie |
|---|---|---:|---:|---:|---|
| K0 Titel | 00:00–00:22 | 22 | — | 1 | — |
| K1 Sørlandet | 00:22–02:15 | 113 | — | 16 | niedrig |
| K2 Ins Fjell | 02:15–03:50 | 95 | — | 14 | steigend |
| K3 Aurlandsfjellet + Schiff | 03:50–05:21 | 91 | 7 | 14 | mittel |
| K4 Pässe nach Geiranger | 05:21–06:26 | 65 | 5 | 10 | steigend |
| K5 Trollstigen | 06:26–07:44 | 78 | 6 | 13 | **Maximum** |
| K6 Lom, Abendlicht | 07:44–08:23 | 39 | 3 | 6 | fallend |
| K7 Valdresflye/Uvdal | 08:23–08:49 | 26 | 2 | 4 | niedrig |
| K8 Passstraße *(bedingt)* | 08:49–09:02 | 13 | 1 | 2 | niedrig |
| K9 Küste, Möwe, Ausklang | 09:02–09:28 | 26 *(39 im Fallback)* | 2 *(3)* | 3 *(4)* | Ausklang |
| **Summe** | | **568** | **26** | **≈ 83** | |

**Regeln beim Nachjustieren:**

- Kapitel ab K3 nur in **13-s-Schritten** verändern, sonst reißt das Phrasenraster.
- Reicht das Material in einem Kapitel nicht, werden **dessen** Beats länger (bis 9 s), **nicht**
  aus dem Nachbarkapitel aufgefüllt — das bräche die Chronologie.
- Kommt ein Kapitel dadurch über 9 s je Beat, wird es um eine Phrase (13 s) gekürzt und die
  Differenz auf **K3 oder K5** gegeben, wo das meiste Material liegt.
- Die Grenzen **230 s** (Musik-Crossfade) und **451 s** (Klimax) sind fixiert.

---

## 6. Intro-Grafik — weiterhin offene Frage an den Nutzer

*(unverändert aus Revision 1 — die Bewegungsanimation der Titel ist ein Render-Thema und hier
bewusst nicht geregelt)*

Das Template `templates/svg/title-card.svg` kann:

- `{{title}}` groß, zentriert auf 46 % Höhe, `font_display`, `text_color` `#ffffff`
- `{{subtitle}}` kleiner, zentriert auf 58 % Höhe, in `accent_color` `#e0a458`
- `{{background_layer}}` — optionale, generierte Hintergrundgrafik

Damit sind „Norwegen 2026" groß + „Drone Edit" kleiner darunter abgedeckt, ebenso das langsame
Ein-/Ausblenden. **Nicht abgedeckt:** das „versetzt darunter" (das Template zentriert starr) und
`motif: norwegian_flag_optional` (kein Flaggen-Slot).

Vorschlag für den Grafik-Prompt, den der Nutzer freigeben oder ändern soll:

> Minimalistische, sehr dezente Titel-Hintergrundgrafik im Format 3840×2160, überwiegend
> transparent/dunkel (`#12222f`). Links unten, klein und zurückhaltend, das norwegische
> Flaggenkreuz als reduziertes Grafikelement (nicht als Rechteckflagge), in gedecktem Rot und
> gebrochenem Weiß, Deckkraft ca. 35 %, weiche Kanten. Kein Text, keine Rahmen, kein Verlauf über
> die Bildmitte — die Grafik liegt über einem Drohnen-Establisher und darf ihn nicht zudecken.

**Fallback:** Template unverändert, Flagge weglassen, Unterzeile zentriert. Der Export ist dadurch
nicht blockiert.
