# Detail-Regie Export "JGA" — RUNDE 4 (3. Preview-Feedback)

Quelle: Christians Sichtung des **dritten** Previews `preview/JGA_preview.mp4` (7:02 / 422,23 s,
aus R3-T9 / Commit `49cfced`), Voice-Transkript 2026-09-10 (Christian sichtet live, gibt
Zeitmarken auf Sekundenbasis an).

**Ergänzt und überschreibt punktuell `editorial-notes-round3.md`, `-round2.md`, `.md`.**
Wo Runde 4 widerspricht, gilt Runde 4. `story-architect`, `timeline-builder`, `audio-designer`
und `party-fx` lesen **alle vier** Dateien.

Zeitangaben `M:SS` = Position im **7:02-Preview**. Clip-IDs (`v003`, `ov-letsgo`, …) beziehen
sich auf `timeline.json` Stand `49cfced` (165 Video / 33 Overlay / 25 Audio). Zeit→Clip→Asset-
Tabelle bei Bedarf neu bauen: `tracks.video` nach `tl_in` sortieren, auf `index/assets.json`
joinen (`scratchpad/clipmap.txt`).

Christians Gesamturteil: **"deutlich, deutlich besser, gefällt mir sehr gut."** Feinschliff.
Struktur bleibt (Intro + Akt 1 / Akt 2 / Aftermath). Danach **Final-Render** (4K), evtl. noch
eine kleine Feintuning-Runde, dann durch.

---

## 0. Globale Regeln Runde 4 (jede überschreibt Runde 3, wo abweichend)

### 0.1 Text-Look — NEUE Spezifikation, 3 Ebenen (überschreibt round3 §0.3.2)
Christian sehr ausführlich und explizit. **Gilt für ALLE durchgängig vorkommenden Texte**,
muss überall geprüft werden. Jeder Text besteht aus **drei deckungsgleichen Ebenen**:

1. **Oberste Ebene (Front):** Hauptschrift **WEISS** (`#ffffff`).
2. **Mittlere Ebene:** identischer Text in **SCHWARZ** (`#000000`), versetzt **3 px nach oben +
   3 px nach links** (@ 1080p; @ 4K entsprechend ~6 px) → ergibt eine harte schwarze Outline
   oben-links.
3. **Unterste Ebene:** identischer Text in **PINK** (`#ff2e8a`), versetzt **nach unten-rechts**,
   ~5–10 px. Der aktuelle Pink-Versatz aus Runde 3 (+10/+10) **passt** — so lassen.

Ergebnis: schwarze Kante oben-links, weißes Font-Face, pinker Schlagschatten unten-rechts.
Keine Weichzeichnung — harte Deckflächen (Sticker-Optik). Umsetzung in `party-fx-recipe.py`:
drei `<text>`-Kopien, `translate(-3,-3)` schwarz hinter, `translate(+10,+10)` pink ganz hinten,
weiß vorn.

- **Font bleibt Bangers.** Christian rügt an mehreren Overlays "Fontface ist falsch" (z. B.
  Cast `Witte`) — dort ist noch nicht Bangers / nicht der neue Look. Alle Overlays auf Bangers
  + 3-Ebenen-Look vereinheitlichen.
- **Gold-Front aus Runde 3 entfällt** — Front ist jetzt Weiß. (Ausnahmen, wo Christina Gold/
  Orange nennt: `ov-geniesst` "orange". Im Zweifel 3-Ebenen-Weiß, es sei denn unten anders
  vermerkt.)

### 0.2 Text-Neigung (überschreibt round3 §0.3.4)
Christian rügt durchgängig: **Texte "stürzen ab"** — sie kippen nach rechts-unten, das sieht
schlecht aus. Neue Regel:

- **Default: gerade** oder **leicht steigend von links-unten nach rechts-oben** (positiver
  Winkel im mathematischen Sinn, "L" tiefer als das letzte Zeichen).
- **Nie nach rechts-unten fallend.**
- Mehrere Overlays ausdrücklich **ganz gerade**: `ov-sulemann` (Element "Der Mann des Abends"),
  `ov-christoph`, alle `ov-cast-*`.
- Wo Christian "mehr nach links kippen" sagt (`ov-crewupdate`, `ov-rooftop`, `ov-praesente`):
  gemeint ist **die steigende Richtung** (links-unten → rechts-oben), NICHT nach links-unten
  fallend. `ov-praesente`: ~30° gegenüber jetziger Position zurückdrehen.
- Das placement-abhängige Slant-Vorzeichen aus Runde 3 wird durch diese Regel ersetzt.

### 0.3 Text-Größe
- **Alle Texte deutlich größer** als im 7:02-Preview. Christian mehrfach: "mindestens doppelt
  so groß", teils "dreimal". Als Faustregel: **regulär ×2 gegenüber Preview `49cfced`**,
  einzelne mehr (s. §-Einträge). Ausnahme: `ov-hydrated` **−15 %** (war zu groß).

### 0.4 Ken Burns — noch ruhiger, keine Dreiecks-Bewegung (verschärft round3 §0.1)
Christian: die Bewegung "tiltet nur rum", geht "oben-links, dann unten, dann rechts" — über
**Dreieckspositionen**. "Das ist Quatsch, viel zu hart."

- **Pro Clip nur EINE Aktion:** entweder rein- **oder** rauszoomen.
- **Höchstens ZWEI Richtungen, eher nur EINE** Translationsrichtung. Keine Kurswechsel
  innerhalb eines Clips, kein Zick-Zack.
- **Bewegung beginnt sofort** mit dem Einblenden des Bildes und läuft **konstant** in eine
  Richtung — **keine Beschleunigungen** —, ODER ganz leicht mit `ease:"in"` anlaufend und
  gegen Ende sanfter. Kein toter Stillstand, kein hartes Ruckeln.
- **Deutlich smoother.** Amplitude klein.
- **Jedes "statische" Bild bekommt trotzdem einen minimalen Zoom** (rein oder raus), ganz
  leicht. "Ein bisschen Bewegung ist nicht verkehrt." → Der ~1/3-statisch-Anteil aus Runde 3
  entfällt praktisch; statt echtem Stillstand ein kaum sichtbarer Zoom.
- Gilt **global für alle Ken-Burns-Effekte** — jeder Clip einzeln prüfen.
- Namentlich zu wackelig / zu schnell: Bild bei **0:11**, Bild bei **0:08**-Umfeld.

### 0.5 Hochkant / Blur-Extension — global prüfen (verschärft round3 §0.2)
- **Alle Hochkantbilder als Hochkant darstellen** — nicht ins Querformat skaliert, **nicht
  stark reingezoomt** (halbe Köpfe/Motive weg). Bei Ken Burns nur minimaler Zoom.
- **Alle** bekommen die Blur-Bild-Extension (`fit:"blur"`), damit keine schwarzen Balken
  entstehen. Christian: "später kommen welche, die haben das nicht."
- **Abschluss-Prüfung nach dem Rebuild:** Preview stichprobenartig auf **dicke schwarze
  Balken** absuchen, die nicht da sein dürfen (Frames bei den unten genannten Zeitmarken).
- Auch **Querbilder mit fehlender Extension** rügt Christian (schwarz links/rechts) — s.
  2:44, 6:13.

### 0.6 Musik — Übergänge (überschreibt round3 §0.6 punktuell)
1. **Intro-Sync:** Film startet schwarz, Bild blendet ein, Musik setzt aktuell erst bei
   ~0:02–0:03 ein. **Der erste Audio-Ausschlag muss mit dem Einblenden des Bildes
   zusammenfallen** — Musikeinsatz auf den Bild-Fade-in-Zeitpunkt vorziehen (`music-01`
   `tl_in` / `src_in` so, dass der erste hörbare Schlag auf dem Bild-Einblenden sitzt).
2. **Akt 1 → Akt 2 Titelwechsel:** Aktuell startet der neue Titel bei ~2:55, das Bild dazu
   passt aber erst bei **3:03**. Christian will den **neuen Soundtrack exakt bei 3:03**
   (Toleranz 3:02–3:05). Weg dahin: Akt-1-Musik (`music-01`) bei "Friedland" (`v056`)
   ausklingen lassen, ggf. den CL-Ausklang **länger ziehen / dehnen / strecken** um die paar
   Sekunden. Bei ~3:02 **höchstens 1–2 s Stille**, dann bei **3:03** harter/weicher Einsatz
   `music-02` (Miserlou) + neuer Soundtrack. (Runde 3 wollte ~2:57 mit Crossfade — Runde 4
   korrigiert auf exakt 3:03.)
3. **Video-Vorzug an den Titelwechsel:** Das Akt-2-Video bei **~3:19–3:20** (erstes/frühes
   Akt-2-Video) **nach vorne ziehen**, direkt hinter Friedland / an den 3:03-Titelstart —
   "dann können wir diesen Sound besser verarbeiten". Danach läuft die Reihenfolge **normal
   weiter** wie bisher. (Separates Video vom 5:37-Antwortvideo, s. §3.)
4. **Miserlou → WIMM:** bleibt wie round3 §0.6 (Miserlou ab ~6:05 sanft aus, WIMM ~6:13 weich
   rein, Crossfade, kein Loch).
5. **Outro "Danke Jungs" 2–3 s länger** stehen lassen, Musik entsprechend länger, dann aus,
   Fade auf Schwarz. (Wie round3 §0.6 — Christian bestätigt "sehr gutes Ende".)
6. Ducking bleibt komplett draußen.

### 0.7 FX
- **Sterne (`sparkles` / `ov-fx-sterne`): KOMPLETT RAUS.** Christian: gelbe + pinke Sterne
  "bewegen sich nicht, liegen einfach nur starr drüber". FX aus `render.py`-Nutzung +
  `party-fx-recipe.py` + `timeline.json` entfernen.
- **Herzchen (`hearts` / `ov-fx-herzen`, ~4:19): mehr davon, verschiedene Größen.** Aktuell
  zu wenige. Christian: "noch 2 die 50 % kleiner sind und ein größeres" rechts dazu, **auch
  links** ein paar. Über beide Bildseiten verteilt. Das spätere Herz-Bild (~4:35-Umfeld) ist
  "super mit den Herzchen" — als Referenz.
- **Stripes-/Streifen-Effekt (Cast-Ende, ~5:05):** brauchen mehr freie Bildfläche → Streifen
  **später anfangen, weiter außen — ~50 %** (statt vom Rand).
- **Stripes bei ~5:21: RAUS** — "passt da nicht hin".
- Speedlines / Color-Pop: kein neuer Kommentar → Runde-3-Stand bleibt.

---

## 1. Intro & Akt 1 (bis ~2:56)

- **0:00 Intro:** Schwarzblende → Bild "JGA" blendet ein — "sieht super aus". Bleibt. Nur
  Musik-Sync (§0.6.1).
- **`ov-letsgo` (~0:08):**
  - **Deutlich größer** (nochmal ein gutes Stück).
  - 3-Ebenen-Look (§0.1).
  - **Position: unten rechts, aber weit nach links gezogen** — das "L" von "Let's Go" beginnt
    bei **~60 % der Bildbreite** (von links), der Text liegt zur Hälfte über dem Bild, zur
    Hälfte über der Blur-Extension. (Runde 3 sagte "oben rechts" — Runde 4 korrigiert auf
    unten rechts / weit links reingezogen.)
- **~0:08–0:11 Ken Burns:** zu wackelig/schnell → §0.4.
- **Bild ~0:32 ("Pizzamann"-Umfeld) + `ov-sulemann`:** Christian will einen **Dreizeiler,
  aufgeteilt auf zwei Elemente:**
  - **Element 1, oben links in die Ecke, GERADE:** "Der Mann" (Zeile 1) / "des Abends" (Zeile 2).
  - **Element 2, unten rechts, über die halbe Bildbreite, SEHR GROSS:** "Pizzamann Sülemann
    Bestermann" (ü + Doppel-N; "Bestermann" neu ergänzt).
  - Text muss **höher** als aktuell.
- **~0:40 Frühstücksbild** — Orientierung.
- **Bild ~0:45 (Pizzakartons, statisch):** leichten Zoom rein.
- **Bild ~0:49–0:52 ("am nächsten Tag, wo wir los sind"):** **Hochkant-Bild** → als Hochkant
  + `fit:"blur"`, nicht reingezoomt.
- **Bilder ~1:12–1:15 (Bäume / draußen):** ganz ruhige, ganz leichte Zoom-/Bewegungseffekte,
  auch mal rauszoomen.
- **Bild ~1:24:** vermutlich Hochkant → prüfen, ggf. `fit:"blur"`.
- **`ov-biere` (~1:43, "500+ Biere"):** Text bleibt "500+ Biere" (über 500 bestätigt).
  **Mindestens doppelt so groß.** "mega gut."
- **Bild ~2:00–2:01 (von oben, Äxte-Vitrine):** eher **rauszoomen**.
- **Schoko-Block ~2:11–2:18 — Reihenfolge:**
  - **Bild 2:14 und Bild 2:11 tauschen** — erst Vitrine, danach das Pralinen-/"Gesprächs"-
    Album.
  - Dann 2:15 Schokolade → 2:16 Schokolade im Becher → 2:17 Waffeln.
  - **Bild 2:18 mit Bild 2:17 tauschen.**
  - "Unpacking" (IMG_4790 / früheres `v042`) bleibt draußen — bestätigt.
- **`ov-praesente` (~2:27, Text NEU):** "Präsente" raus. Neuer Text, **dreizeilig:**
  "Süße Geschenke" / "für den" / "Junggesellen" ("Junggesellen" richtig groß). **Oben links.**
  Kippt aktuell nach rechts → **~30° zurück in die steigende Richtung** (links-unten →
  rechts-oben). 3-Ebenen-Look, größer.
- **`ov-geniesst` (~2:37, "Ein bisschen / genießt er es / ja schon"):** kippt nach rechts →
  **steigende Richtung**. **2–3× so groß.** Orange/Gold-Ton ok, sonst 3-Ebenen. Von Weitem
  lesbar.
- **Bild ~2:44 (Eckgebäude/Haus, `v051`-Klasse):** **Blur-Extension fehlt** — schwarz links
  und rechts → `fit:"blur"` (oder `fit:"pad"`, ganzes Gebäude zeigen, minimaler Zoom).
- **Bild ~2:48 (Hochkant, mit Thomas):** neues Overlay möglich — **`ov-mok-detektor`:**
  Text **"MOK Detektor"** — "MOK" groß in Versalien (M-O-K), "Detektor" klein daneben oder
  darunter. **Oben links.** 3-Ebenen-Look. ("MOK" = das Café MOK, M-O-C-K im Original, das
  danach kommt — Christian schreibt es bewusst "MOK".)
- **MOK-Café-Bilder ~2:56:** bleiben (Runde 3), leicht reinzoomen.

---

## 2. Akt-1 → Akt-2 Übergang (~2:55–3:20)

- **Titelwechsel exakt bei 3:03** — Musik §0.6.2. Bei "Friedland" Akt-1-Musik ausklingen,
  max. 1–2 s Stille, dann neuer Soundtrack.
- **Video ~3:19–3:20 nach vorne an den 3:03-Titelstart ziehen** — §0.6.3. Danach Reihenfolge
  normal weiter.
- **`ov-crewupdate` (~3:04, Text NEU dreizeilig):** "Crew Update" (sehr groß) / "die
  verlorenen Söhne" / "stoßen dazu". **Rechte Seite** (Runde 3 sagte top-left — Runde 4:
  rechts). Kippt aktuell nach rechts-unten ("stürzt ab") → **steigende Richtung**
  (links-unten → rechts-oben). "Crew Update" deutlich größer. 3-Ebenen-Look.
- Danach Delirium: "verschiedene Reihenfolge passt, sieht sehr gut aus" — bleibt.

---

## 3. Akt 2 (Miserlou)

- **Bild ~3:14:** garantiert Hochkant ("fehlt die Hälfte des Kopfes") → Hochkant + `fit:"blur"`.
- **`ov-rooftop` (~3:40–3:41, "Rooftop Bar 58 wir kommen"):** **Nach unten rechts setzen**,
  mit mehr Abstand nach rechts. Kippt aktuell nach rechts-unten → **nach links / steigende
  Richtung** kippen. 3-Ebenen-Look. (Runde 3 sagte top-left/Pink — Runde 4: unten rechts.)
- **Bild ~3:53 (Dach-Bild, gedoppelt): RAUS.**
- **Bild ~3:55 (Anstoßen):** super, bleibt.
- **Bild ~3:58:** Hochkant → als Hochkant + `fit:"blur"`.
- **`ov-hydrated` (~3:59, "stay hydrated"):**
  - **Nicht mittig — nach rechts.** "stay" ist zu weit rechts → ganzes Overlay **~20–25 %
    der Bildbreite weiter nach rechts**, so dass es den rechten Rand fast berührt.
  - **Text −15 %** (war zu groß).
  - **Jitter/Wackel von Anfang an** — der Effekt ist gut, muss aber ab dem ersten Frame
    konstant so wackeln (aktuell erst verzögert "hin und her"). Gold-/Weiß-Front und
    Pink-Ebene **im selben Rhythmus** (§0.1).
- **`ov-christoph` (~4:01–4:02, "Wo ist Christoph???"):** diesmal **gerade schreiben** (kein
  Slant) — rutscht aktuell nach rechts-unten. **Unten links.** 3-Ebenen-Look, drei "?".
- **Bild direkt nach `ov-christoph`: RAUS** ("das zweite Bild, das danach kommt, entfernen").
- **`ov-fx-herzen` (~4:19):** mehr Herzchen, verschiedene Größen, links + rechts verteilt —
  §0.7.
- **Bild ~4:22 ("Downtown"):** **zum Prüfen markiert** — wahrscheinlich raus ("lass uns das
  mal ansehen"). timeline-builder: raus, außer es trägt sichtbar die Szene.
- **`ov-token` (~4:39, "wolle Token kaufen ???"):** Text ist gut. **Winkel ändern:
  links-unten → rechts-oben.** 3-Ebenen-Look ("Farbphase"). Größenstaffel wolle/Token/kaufen
  bleibt (Runde 3).
- **Bild ~4:35:** definitiv Hochkant → als Hochkant + `fit:"blur"`.

### Cast-Intro `ov-cast-01..09` (~5:05–5:15)
- **Alle Namen GERADE** (kein Slant) — fallen aktuell nach rechts-unten, zurückdrehen.
- **Text ~15–20 % größer.**
- **3-Ebenen-Look** — Fontface bei mehreren noch falsch (`Witte`), vereinheitlichen.
- **Bilder weniger stark reinzoomen / kleiner skalieren**, damit die **Köpfe komplett drauf**
  sind (aktuell fehlt oben ein großes Stück). Hochkant → `fit:"blur"`.
- Wechsel-/Durchratter-Effekt bleibt ("sieht super aus").
- **Cast #9: nur "Micha"** (nicht "Micha im Delirium") — gleicher Font-Style / gleiche Größe
  wie die anderen. Gilt auch für die Wiederholung bei ~5:05.
- **Stripes am Cast-Ende (~5:05):** später/weiter außen anfangen, ~50 % (§0.7).

### Lampen-Szene & Antwortvideo (~5:20–5:40)
- **Video nach Cast ("Super", dann Lampen gehen aus):** Winkel + Position schon gut. **Font
  anpassen (3-Ebenen), Größe mindestens ×2** für Lesbarkeit.
- **Stripes bei ~5:21: RAUS** (§0.7).
- **Antwortvideo auf "Gehen hier etwa schon die Lampen aus?":** das **Video bei ~5:37–5:38**
  ("der läuft zum Video") direkt hinter die Lampen-Szene setzen. Danach `ov-natuerlich`
  ("natürlich" / "(noch) nicht"). (Runde 3 zog v144/v145 nach vorn — Runde 4 präzisiert auf
  das 5:37–5:38-Video als Antwort. Falls identisch: Runde-3-Umsetzung reicht, sonst
  entsprechend nachziehen.)

### Gurken-Ende Akt 2 (~5:50–6:16)
- **`ov-weiterziehen` (~5:51, "Noch ahnten Sie nicht wie toll die Nacht wird"):** gehört auf
  das **Bild bei 5:52–5:53**. **Unten rechts oder Mitte, relativ gerade** (oder leicht
  steigend links-unten → rechts-oben). **Deutlich größer.** 3-Ebenen-Look.
- **`ov-wtf` (~5:59, "WTF"):** **deutlich größer.** **Links-unten → rechts-oben, etwas
  schräger** gestellt. Bild dahinter ist **Hochkant, definitiv** → `fit:"blur"`.
- **`ov-ichwaresnicht` (~6:05–6:12, "Ich war es nicht"):** **Ausrufezeichen mit
  Schatten-Punkt am Ende.** **Größer.** Etwas weiter nach links. Unten rechts.
- **Bild bei ~6:05 (unter "ich war es nicht") mit dem Gurkenbild tauschen.**
- **`ov-gurken` (Gurkenbild):** Text NEU, **dreizeilig, viel größer, gut lesbar:**
  "Der Michael mag Gurken." / "Gib mir Gurken." / **"Er braucht sie dringend."** (3. Zeile
  bewusst OHNE nochmal "Michael"). Darstellungsdauer so timen, dass alle drei Zeilen lesbar
  sind. 3-Ebenen-Look.
- **`ov-raetkeinkaese` → Text-Korrektur: "Rede kein Käse!"** (R-E-D-E, mit Ausrufezeichen;
  war "Rät kein Käse"). Oben rechts, klein-mittel, auf dem Gurkenbild. Einblend-Tempo ist gut.
- **Bild ~6:13 (super Foto):** **Blur-Extension fehlt** — schwarze Balken links/rechts →
  `fit:"blur"`.

---

## 4. Aftermath / Outro (Where Is My Mind, ~6:16–7:02)

- **`ov-wimm` ("Where is my mind?"):** gehört auf das **Bild bei ~6:17–6:19** (nicht früher).
  Abstand zwischen "Where is my" und "mind" ist zu groß ("mind" rutscht weit nach unten) →
  **Zeilen näher zusammen.** **Oben links.** **Steigende Richtung / leicht nach links
  rotiert** — nicht nach rechts-unten abstürzen. "mind?" bleibt der große Teil (Runde 3: ~4×).
  3-Ebenen-Look.
- Aftermath-Reihenfolge: Runde-3-Stand bleibt. Ende: draußen kotzen → Bild → Bild → **"Danke
  Jungs"** → Fade Schwarz. "Sehr gutes Ende."
- Outro-Karte 2–3 s länger (§0.6.5).

---

## 5. Overlay-Liste Runde 4 (Delta zu round3 §5)

| Overlay | Änderung Runde 4 |
|---|---|
| **alle** | **3-Ebenen-Look:** Weiß-Front / Schwarz −3/−3 px / Pink +10/+10 px (§0.1). Bangers. **Neigung: gerade oder links-unten→rechts-oben steigend, nie nach rechts-unten fallend** (§0.2). Regulär **×2** Größe ggü. Preview `49cfced` (§0.3). |
| `ov-letsgo` | **unten rechts, weit nach links gezogen** ("L" bei ~60 % Bildbreite, halb über Blur-Extension); deutlich größer |
| `ov-sulemann` | zwei Elemente: **"Der Mann" / "des Abends"** oben links, GERADE — **"Pizzamann Sülemann Bestermann"** unten rechts, sehr groß; höher als jetzt |
| `ov-biere` | mind. ×2 |
| `ov-praesente` | Text **"Süße Geschenke" / "für den" / "Junggesellen"**; oben links; ~30° in die steigende Richtung zurückdrehen; größer |
| `ov-geniesst` | 2–3× so groß; steigende Richtung; orange/Gold ok |
| **`ov-mok-detektor`** (neu) | Text **"MOK Detektor"** (MOK Versalien groß, Detektor klein drunter/daneben); oben links; auf Bild ~2:48 |
| `ov-crewupdate` | Text **"Crew Update" / "die verlorenen Söhne" / "stoßen dazu"**; **rechte Seite**; "Crew Update" deutlich größer; steigende Richtung |
| `ov-rooftop` | **unten rechts**, mehr Abstand rechts; nach links / steigend kippen |
| `ov-hydrated` | **−15 %**; **~20–25 % weiter nach rechts** (fast an den Rand); **Jitter ab Frame 1**, Front + Pink synchron |
| `ov-christoph` | **gerade** (kein Slant); unten links; drei "?" |
| `ov-token` | Winkel **links-unten → rechts-oben**; 3-Ebenen |
| `ov-weiterziehen` | auf Bild 5:52–5:53; unten rechts oder Mitte, gerade/leicht steigend; deutlich größer |
| `ov-wtf` | deutlich größer; links-unten → rechts-oben, schräger; Bild dahinter `fit:"blur"` |
| `ov-ichwaresnicht` | **"!"** mit Schatten-Punkt; größer; etwas weiter links; unten rechts |
| `ov-gurken` | Text **"Der Michael mag Gurken." / "Gib mir Gurken." / "Er braucht sie dringend."**; viel größer; Standzeit für 3 Zeilen |
| `ov-raetkeinkaese` | Text **"Rede kein Käse!"** (war "Rät kein Käse") |
| `ov-wimm` | auf Bild ~6:17–6:19; Zeilen näher zusammen; oben links; steigend / leicht nach links rotiert |
| `ov-cast-01..09` | **gerade** (kein Slant); +15–20 % Größe; 3-Ebenen (Fontface fixen); Cast #9 nur **"Micha"**; Bilder weniger reingezoomt (Köpfe komplett), Hochkant `fit:"blur"` |
| `ov-natuerlich` | hinter das 5:37–5:38-Antwortvideo |
| **`ov-fx-sterne`** | **LÖSCHEN** (Overlay + `sparkles`-Nutzung + Clip) |
| `ov-fx-herzen` | mehr Herzen, verschiedene Größen, links + rechts verteilt |
| Stripes-FX | Cast-Ende: ~50 % weiter außen anfangen · bei ~5:21: **raus** |

---

## 6. Code-/Timeline-Aufgaben Runde 4

- **`party-fx-recipe.py`:** 3-Ebenen-Text-Renderer (Weiß/Schwarz −3−3/Pink +10+10) statt
  Gold+Pink. Neigungslogik: gerade oder positiver Winkel, nie negativ-fallend. Größen ×2.
  Alle Text-Overlays neu bauen. `ov-mok-detektor` neu, `ov-fx-sterne` löschen, Texte
  korrigieren (siehe Tabelle). `ov-fx-herzen` Cluster erweitern.
- **`render.py` (falls nötig):** Ken-Burns-Regie ist Timeline-Sache — prüfen, ob `ease:"in"`
  + Einzelrichtung reicht oder ob eine "konstante lineare Drift ohne Ease"-Variante fehlt
  (`ease:"linear"` existiert). `sparkles`-Effekt aus dem Effektkatalog nehmen oder ungenutzt
  lassen. Kein neues Feature zwingend.
- **`timeline.json` (timeline-builder):**
  - KB pro Clip auf **eine Aktion + eine Richtung** reduzieren, Amplitude runter, alle
    "statischen" Fotos bekommen Mini-Zoom (§0.4).
  - `fit:"blur"` global nachziehen: 0:49–0:52, 1:24, 2:44, 2:48, 3:14, 3:58, 4:35, 5:59,
    6:13 + alle Cast-Bilder + Prüfliste (§0.5).
  - Streichungen: Bild 3:53, Bild nach `ov-christoph`, Bild 4:22 (Downtown, prüfen).
  - Swaps: 2:11↔2:14, 2:17↔2:18, 6:05-Bild↔Gurkenbild.
  - Video ~3:19–3:20 an den 3:03-Titelstart vorziehen.
  - Cast-Fenster: Namen sichtbar größer/länger — QC-Lesbarkeit beachten.
  - `brief.yaml` `target_duration_s` nach dem Umbau nachziehen.
- **Audio (audio-designer / direkt in timeline.json):** Intro-Musik-Sync auf Bild-Fade-in;
  Akt-1-Musik-Ausklang bis ~3:02 dehnen, neuer Titel bei 3:03 (max 1–2 s Stille davor);
  Miserlou→WIMM wie Runde 3; Outro +2–3 s.
- **Abnahme:** `validate_semantics` + `qc.validate` leer, `pytest`/`ruff`/`doctor` grün,
  bestehende Timelines (`proto`, `test-timelapse-journey`) unverändert lauffähig, neues
  Preview auf schwarze Balken + Text-Look + KB-Ruhe gesichtet.

---

## 7. Nach dem Preview (R4-T10, blockiert — braucht Christian)

Unverändert zu round3 §7 / PROGRESS R3-T10: nach `frameforge approve` → **4K-Final in Chunks**
(`render --resolution 3840x2160 --crf 18 --preset medium --chunk-s ~90`, Muster
`web/sites/norwegen-2026/deploy/render-web-versions.sh`) + 1080p-Streaming-Fassung. Dann
Website `web/sites/michael-jga-2026/public/` (Video-Block + Download-Link wie
`norwegen-2026/public/film-vlog.html`). Videos getrennt vom Website-Build unter `/videos/` auf
dem Server (`JGA_1080p.mp4` + `JGA_4k.mp4`), `rsync -avP`. **Offen: exakter SSH-Host +
Server-Pfad für `micha-jga.skubus.de/videos/`**, Traefik-Basic-Auth serverseitig. Norwegen-
und JGA-Videosätze strikt getrennt. Christian hat noch separate Website-Änderungen.
