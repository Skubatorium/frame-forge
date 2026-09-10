# Detail-Regie Export "JGA" — RUNDE 3 (Preview-Feedback)

Quelle: Christians Sichtung des **zweiten** Previews `preview/JGA_preview.mp4` (7:08, aus T9 /
Commit `ddd9a4d`), Voice-Transkript 2026-09-10 (Christian sichtet live, gibt Zeitmarken an).

**Ergänzt und überschreibt punktuell `editorial-notes-round2.md` und `editorial-notes.md`.**
Wo Runde 3 widerspricht, gilt Runde 3.

`story-architect`, `timeline-builder`, `audio-designer` und `party-fx` lesen **alle drei** Dateien.

Zeitangaben `M:SS` = Position im **7:08-Preview aus T9**. Clip-IDs (`v003`, `ov-letsgo`, …)
beziehen sich auf `timeline.json` Stand `ddd9a4d`. Vollständige Zeit→Clip→Asset→Beschreibung-
Tabelle: `scratchpad/clipmap.txt` (aus der Session erzeugt, im Repo nicht versioniert — bei
Bedarf neu bauen: sortiere `tracks.video` nach `tl_in`, join auf `index/assets.json`).

Christians Gesamturteil: **"deutlich besseres Ergebnis als vorher, mega gut."** Es geht um
Feinschliff, nicht um Neubau. Struktur (Intro + Akt 1 unter Champions League, Akt 2 unter
Miserlou, Aftermath unter Where Is My Mind) bleibt.

---

## 0. Globale Regeln Runde 3

### 0.1 Ken Burns — Kernkritik, jetzt richtig
Runde 2 hat variiert, aber:
- **Viele "Bewegungen" bewegen sich real nicht.** Ursache (in dieser Session gefunden):
  11 Clips tragen `kenburns` mit `from/to`-Zoom `1.04` **und einem reinen Pan** (`dx`/`dy` 0.03–0.06,
  `dz=0`). `zoompan` hat bei Zoom ~1.0 **kein Crop-Fenster zum Schwenken** → das Bild steht,
  ruckt am Ende minimal. Genau Christians "das Bild steht oder wird ein bisschen in irgendeine
  Richtung verschoben, nicht weich".
- **Fix im Code (R3-T2, `render.py`):** Pan erzwingt jetzt Mindest-Zoom (~1.08), damit
  `zoompan` Schwenkraum hat. Zusätzlich neue Easing-Kurve `ease: "in"` (beschleunigend,
  `pow(n,1.7)`) — "langsam anlaufen, dann schneller", Bewegung läuft bis zum Schnitt durch,
  kein toter Stillstand am Ende wie bei `smooth`.
- **Regie (`timeline-builder`, R3-T7):**
  - Ken Burns ist **die Regel, nicht die Ausnahme** — grob **2/3 aller Fotos** bekommen eine
    Bewegung, **~1/3 dürfen bewusst stehen** (Christian: "manche Bilder können auch stehen,
    das ist völlig in Ordnung").
  - **Jede Bewegung koppelt Zoom + leichte Translation.** Reiner Pan ohne Zoom ist verboten.
    Varianten: leicht rein (`z 1.0→1.10`), leicht **raus** (`z 1.10→1.0`), rein + diagonal
    driften, raus + driften. Amplitude spürbar aber ruhig; Zoom-Delta 0.06–0.12, Pan-Delta
    0.04–0.09.
  - **Richtung wechseln.** Nie über mehrere Clips dieselbe. Zwei gleiche hintereinander ok,
    nicht drei. Diagonale/schräge Bewegung bevorzugen, keine starren 90°-Achsen-Schwenks.
  - **`ease` mischen:** überwiegend `"in"` (beschleunigend), einige `"smooth"`.
  - **Zoom-Richtung motivisch:** Gruppen-/Establisher tendenziell **raus** (öffnet), Details
    **rein**. Christian nennt namentlich: **1:08 (`v021`) nicht nach oben zoomen, sondern
    RAUS**; **1:54 (`v036`/`v037`) Rauszoom ist gut** (bleibt); **2:07 (`v040`, Pappbär,
    `fit:blur` + KB) = Referenz-Look, so soll es überall aussehen**.
  - Namentlich "zu starr / kein KB, bitte Bewegung rein": `v007` (0:21), `v023` (1:14),
    `v024` (1:16), `v025` (1:19), `v029` (1:30 zu starr), `v030` (1:33 Schwenk hoch — ok, aber
    mit Zoom + Easing), `v039` (2:05 "gar nichts"), `v091`/Umfeld (4:05), `v142`/`v143` (5:36
    scharfes Bild, "überhaupt keine Bewegung" → unbedingt Bewegung rein).

### 0.2 Hochkant + Video: Blur-Extend überall
- **Regel wie Runde 2 §0.5**, aber Christian rügt weiter viele überskalierte Hochkantbilder
  (halbe Köpfe/Motive weg). `fit: "blur"` auf **allen** Hochkant-Motiven — auch da, wo EXIF
  "landscape" sagt, das Bild aber um 90° gedreht ist (die `assets.json`-Summaries vermerken
  "Bild um 90 Grad gedreht"). Kandidaten namentlich unten in §1/§2.
- **NEU: Blur-Extend auch für Videos.** Die Akt-2-Videos (Hochkant / nicht-16:9) laufen mit
  schwarzen Balken — Christian: "können wir das bei Videos auch machen, dieser Effekt, dass
  der Inhalt visuell nach links und rechts erweitert wird". `render.py` `fit:"blur"` greift
  bereits generisch (`split`+`overlay`, funktioniert auf Video-Streams) — `timeline-builder`
  setzt `fit:"blur"` auf allen Hochkant-/Schmal-Videoclips (`v069` IMG_1460 Hochkant-Selfie,
  `v148` IMG_4835 Karaoke Hochkant, ggf. weitere). R3-T2 verifiziert Blur-Fit auf Video mit
  Mini-Render.

### 0.3 Text-Overlays — kompletter Neuaufbau des Looks (party-fx, R3-T3)
Christian sehr ausführlich. Neue verbindliche Regeln:

1. **Eine Schrift überall, eine Variante: Bangers (Display/Comic).** Auch Akt 1, auch "Let's
   go", auch "Where is my mind". Kein Poppins mehr für Overlays. ("Wichtig, überall möchte
   ich dieselbe Schriftart in derselben Variante.")
2. **Doppelebene für harten Schatten.** Jeder Text ist **zwei Grafik-Ebenen**:
   - **Vorne:** goldgelbe Frontface (`#d9a441` / `#ffcf5c`). Alternativ pink `#ff2e8a` —
     Christian findet Pink "nochmal ein bisschen schicker", ausdrücklich erlaubt für WTF.
   - **Dahinter (Z tiefer):** identischer Text in **Pink** (`#ff2e8a`), versetzt
     **+10 px rechts / +10 px runter** (bei 4K; ~5 px bei kleineren Overlays / Christian nennt
     mal 10, mal 5 — nimm 10 px @ 4K, skaliert). Kein Weichzeichner — **harte** Deckfläche,
     Sticker-Optik. ("die goldene gelbe Schrift oben, die darunter liegende Ebene schwarz bzw.
     pink, 10 Pixel nach rechts, 10 nach unten, schöner Schatteneffekt, Lesbarkeit deutlich
     erhöht.") Umsetzung: dupliziertes `<text>` hinter dem Haupttext, Pink-Fill, `translate`.
3. **Deutlich größer.** Mindestens **2×** der Runde-2-Größen für alle regulären Overlays.
   Einzelne noch größer (s. §4: "Where is my mind" Titel ~4–5×, "mind" nochmal 4× im Titel).
4. **Leicht schräg.** Rechts platzierter Text kippt **nach links** (negativer Winkel), links
   platzierter Text nach rechts — Christian: "wenn die Schrift rechts ist, muss sie mehr nach
   links gekippt sein" / bei Cast `Christoph` (rechts) "muss nach links kippen, ist aber nach
   rechts gekippt". → **PLACEMENT-abhängiges Vorzeichen des `slant`** in `party-fx-recipe.py`
   fest verdrahten: `*-right` → slant negativ, `*-left` → slant positiv.
5. **Animierter Auftritt bleibt über `anim` im Render** (Slide + Fade). "Buchstaben einzeln"
   ist nice-to-have, kein Blocker — Slide/Fade ist Christian ausdrücklich ok ("wird
   herangefadet, wieder herausgefadet, finde ich nicht schlecht").
6. **Weg, bevor der Fade zum nächsten Bild beginnt** (Runde-2-Regel gilt weiter).
7. **Zitter-/Wackel-Effekt** für ausgewählte Stellen ("Stay hydrated", "Delirium"): wenn Text
   aus zwei Grafiken (Gold vorn / Pink hinten) besteht und wackelt, müssen **beide im selben
   Rhythmus** wackeln (nicht gegeneinander). Umsetzung über `anim.jitter` im Render bzw. als
   fertig gewackelte Sequenz — pragmatisch: leichter, gleichmäßiger Positions-Jitter auf dem
   ganzen Overlay-PNG.

### 0.4 Comic-FX vielfältiger (party-fx)
Christian: "das sind so kleine einzelne Icons im Bild, müssten vielfältiger sein, ein paar
mehr Icons zusammen."
- **Herzchen-Cluster (Knutsch-Szene, s. §3):** viele rosa Herzen **verschiedener Größe**,
  über das Bild verteilt, tauchen auf / poppen weg / sprudeln aus der Bildmitte, schnell,
  viele. Nicht ein einzelnes Herz. → neuer FX `hearts` (R3-T2) ODER Cluster-PNG mit
  Puls-Anim.
- **Sterne:** zwei/drei drehende Sterne im Gold-Pink-Stil an lebendigen Stellen einstreuen
  (comichafter, lebendiger Bildteil). → FX `sparkles` / Cluster-PNG.
- **Glows / Speedlines:** kamen im Preview nicht sichtbar an ("die Glows gibt es gar nicht,
  Speedlines habe ich überhaupt nicht gesehen"). `party-fx` R3-T8: Speedlines/Color-Pop an
  1621/1635/1637 kräftiger und sichtbar setzen, gegen das Nachtmaterial prüfen.

### 0.5 André / Sülemann-Schreibweise
- **André** bleibt mit Akzent (Runde-2-Entscheidung, Bangers rendert É sauber).
- **Süleman → "Süleman"** mit **ü**, und **Doppel-N: "Sülemann"**. Christian: "Sülemann ist
  mit Ü und Doppel-N." Text: **"Der Mann des Abends / Pizzamann Sülemann"** (Christian:
  "Pizzamann, Sülemann"). "Der Mann des Abends" darf in der Zeile bleiben, darunter groß im
  Comic-Stil (Gold vorn / Pink versetzt) "Pizzamann Sülemann".

### 0.6 Musik — Lücken schließen, weiche Übergänge (audio-designer, R3-T5)
- **~2:56–3:01 tote Stille.** Champions League endet, Miserlou-Cut sitzt erst bei 3:01.4.
  Der CL-Theme-m4a hat einen leisen Ausklang → `music-01` `src_out` früher trimmen
  (~176 s), `music-02` (Miserlou) **~2:57** starten mit ~1 s Equal-Power-Crossfade. Ein
  **1–2 s** Mini-Atem ist ok ("dann vielleicht noch ein, zwei Sekunden warten, dann müsste
  der Auftakt kommen"), 5 s Loch nicht.
- **~6:05–6:19 Stille vor Where Is My Mind.** Miserlou-Loop endet ~6:17 hart, WIMM startet
  6:17.4 **hart** (`fade_in_s: 0`). Christian: "die Stille viel zu lange … Where is my mind
  muss eingeblendet werden, richtig weich, könnte schon vorher passieren." Neu:
  - Miserlou (`music-02`) ab **~6:05** sanft ausblenden, Ende ~6:13.
  - WIMM (`music-03`) **~6:13** einsetzen, `fade_in_s` ~3–4 s (weich), so dass der Gurken-
    Schluss-Block (`ich war es nicht`, 6:12–6:14) schon vom WIMM-Auftakt getragen wird.
  - Dead-Air zwischen den Tracks vermeiden — Crossfade, keine Lücke.
- **Miserlou-Loop-Naht** (~4:44 / bei ~284 s) noch hörbar ("den Loop hört man schon"). Naht
  wenn möglich weiter entschärfen (längerer Crossfade an der Loopstelle in
  `01 Miserlou (loop-196).m4a`) oder Naht unter einen harten Bild-Cut legen. Kein Blocker,
  aber prüfen.
- **Schluss:** Outro-Karte "Danke Jungs" **2–3 s länger stehen lassen** (Christian:
  "das kann ein bisschen stehen bleiben, ist zu kurz … das Lied kann an der Stelle ein
  bisschen länger gehen, so zwei, drei Sekunden erweitern"). Danach Musik ganz aus. Ende:
  **kein Zwang zur Schwarzblende** — "wir lassen es in schwarz enden, das ist okay, lassen
  wir so" → aktuelles Ende (Fade auf Schwarz) bleibt, nur eben etwas später.
- **Ducking** bleibt komplett draußen (Runde 2 §0.3).

### 0.7 Diverses aus der Sichten-Prüfliste
- "IMGB ist ein Preview seitlich, kann man rausnehmen" → falls ein seitlich stehender
  IMG-Clip im Preview auftaucht (`v066` IMG_8337 steht bekannt seitlich, `note` im Clip):
  **raus** oder vorgedreht ersetzen. Kein Rotate-Feature bauen.
- Cast-Name ragt 0,3 s ins Folgefoto: die Cast-Fenster sind mit 0,9–1,2 s zu kurz für die
  QC-Lesbarkeitsgrenze. `timeline-builder`: Cast-Standbilder auf **~1,3–1,6 s** verlängern
  (Christian: "die müssen länger zu sehen sein, die sind wichtig"), Beat-Grid der Cast-SFX
  entsprechend nachziehen. Der Karaoke-Block bekommt dadurch etwas mehr Zeit — an anderer
  Stelle (Streichbilder unten) wieder reinholen.
- "Windblende 10 Sekunden" / "Ausstattratter" / "Stille ab :24" — vermutlich die zweite
  Intro-Schwarzblende (`v002`, 3,9–5,5 s) bzw. Loop-Artefakt. Zweite Intro-Blende weiter
  kürzen (Runde 2 §1 wollte das schon), Intro-Standbild-Ausblendung knapper.

---

## 1. Intro & Akt 1 (Champions League) — per Clip

- **Intro-Standbild `v001`:** "Schwarzblende auf das Bild JGA, sieht super aus, richtig gut."
  → bleibt. Erste (gestreckte) Blende bleibt. **Zweite Blende `v002` kürzen** (§0.7).
- **`ov-letsgo` (0:08):** Comic-Schrift (Bangers), **deutlich größer**, **oben rechts**
  (nicht bottom-right), rein-/rausgefadet ok. "Let's go" — Gold vorn / Pink versetzt.
- **`v007` (0:21):** zu starr, "nach links gefahren, sehr starr, kein Easing". → KB mit
  Zoom + Easing `"in"` (§0.1).
- **`ov-sulemann` (~0:32):** Text **"Der Mann des Abends" / "Pizzamann Sülemann"** (ü + nn,
  §0.5). Comic-Doppelebene, groß. Bild `v019`? — der Sülemann-Shot ist Hochkant/halber Kopf →
  `fit:"blur"`.
- **`v016` (0:50):** Christian denkt Hochkant; Kopf der linken Person oben angeschnitten.
  "kann man es so drehen lassen, passt schon" → **niedrige Priorität**, wenn `fit:"blur"`
  ohne Aufwand geht: machen, sonst lassen.
- **`v021` (1:08):** **kein Zoom nach oben** — Rauszoom-Effekt nutzen (§0.1).
- **`v022` (1:10):** Hochkant-Graffiti ("surreales SW-Wandbild"), aktuell viel abgeschnitten →
  `fit:"blur"`, volle Bildhöhe, seitlich farblich weitergeführt.
- **`v023` (1:14):** kein KB → leichte Bewegung rein.
- **`v024` (1:16):** sehr starr → KB Zoom+Pan diagonal, Easing.
- **`v025` (1:19):** steht starr → leichte Bewegung.
- **`v026`/`v028` (1:22–1:23, "Dreieck"):** Christian lobt ("sehr schön") → so lassen.
- **`v029` (1:30):** zu starr → Bewegung.
- **`v030` (1:33):** Schwenk nach oben ist gut, aber **mit Zoom + Easing** ausführen.
- **1:33 Hopfen `v030`, "ist schön"** — bleibt.
- **Bierliste-Banner `v033` (IMG_1379, "Belgian Beer Weekend mit langer Bierliste", ~1:43):**
  Das ist das **"250 Biere"-Bild**. **R3-T4 recherchiert:** Belgian Beer Weekend (Grand Place,
  4.–6.9.2026) = **über 500 belgische Biere von 50+ Brauereien** (offizielle Festivalangabe,
  Datum passt exakt zu den Assets). → `ov-biere` Text **"500+ Biere"**. Schrift **mindestens
  2× so groß**, Gold vorn / Pink versetzt. Bild ok ("schönes Bild") — bleibt.
- **`v036`/`v037` (1:54, Rauszoom):** gut so, bleibt.
- **`v039` (2:05):** "gar nichts" → KB rein.
- **`v040` (2:07, Pappbär, `fit:blur`+KB):** **Referenz-Look.** Nicht anfassen. `ov-fx-sticker-baer`
  bleibt der eine Akt-1-Akzent.
- **Schoko-Vitrine:** Christian will das **Vitrinen-/Mousse-Bild** (`v041` Pralinen-Boutique
  Vitrine) behalten und **eher mehr davon** — ggf. ein zweites Vitrinen-Foto aus dem Fundus
  ergänzen (Suche: tags `schokolade`/`vitrine`/`praline`, Tag 2026-09-05).
- **`v042` (2:13, IMG_4790 "einer zeigt geöffnete Schokoladenpackung"):** **RAUS** ("kein
  gutes Bild, muss entfernt werden").
- **`v043` (2:15, Schokomousse-Becher, `fit:blur`):** gut, bleibt.
- **`v044` (2:19):** "Stadtsdorf nicht gut" aber "schönes Foto" — behalten, KB dezent.
- **`v049` (2:36, Zigounette-Lolli):** bleibt.
- **`v050` (2:41):** Kann-Bild (Straßenschlucht nach oben).
- **`v051` (2:44, IMG_1420 Eckgebäude/Kuppelturm):** "sieht scheiße aus, weil das Bild
  eigentlich richtig gut ist — zu krass reingezoomt, zu viel geht verloren." → **`fit:"pad"`
  oder minimaler Zoom**, ganzes Gebäude zeigen. Wenn es sich als Hochkant erweist:
  `fit:"blur"`.
- **`ov-praesente` (~2:27, "Präsente für den Junggesellen"):** **oben links**, **richtig
  groß**, Comic-Doppelebene. Bild `v047` bleibt. Nett umgebrochen/versetzt.
- **`ov-geniesst` (~2:37, "Ein bisschen / genießt er es / ja schon"):** dreizeilig, oben
  links, **größer, orange (Gold)**, "von Weitem lesbar". Bild bleibt.
- **`ov-kunstfigur` (~2:46, "Die wandelnde Kunstfigur"):** **KOMPLETT RAUS.** "Wir machen da
  gar keinen Text hin." Overlay aus `party-fx-recipe.py` **und** aus `timeline.json` löschen.
  Das Bild dahinter ("More Coffee" / Kunstfigur, Hochkant) bleibt, `fit:"blur"`, cool.
- **MOK Coffee `v053` + `v055` ("100 Best Coffee Shops", 2:56):** super, bleibt. `v055`
  leicht reinzoomen ("richtig toll").
- **`v048` (2:29, Schoko-Waffel-Video):** Christian: **weniger Standbilder, mehr die Wurzeln/
    Videos nutzen** — Video bleibt drin.

---

## 2. Akt-1 → Akt-2 Übergang, Fritten, Crew-Update (~2:56–3:10)

- Champions League endet ~2:57, Miserlou setzt mit Crossfade ein (§0.6). Kein Loch.
- **Fritten/Pommes müssen an den Umbruch.** Reihenfolge um 3:00:
  1. `v055` "100 Best Coffee Shops" (2:56) — hier "könnte man aufhören" mit Akt 1.
  2. **`v056` Frietland-Terrasse** und **`v057` Pommes-Nahaufnahme** direkt davor/dazwischen
     schneiden, so dass Friet + Pommes noch klar zu Akt 1 gehören ("Fritten sollte mit
     reinkommen, davor geschnitten werden").
  3. **`ov-crewupdate`** sitzt bei **~3:04** auf dem ersten Akt-2-Bild ("die verlorenen
     Söhne stoßen dazu"). Christian: Position über dem linken/oberen Bildteil ist cool,
     bleibt; **größer**, Comic-Doppelebene. Text: **"Crew-Update" / "Die verlorenen Söhne
     stoßen dazu"** (zweizeilig).
  4. Miserlou läuft, wenn "die Jungs" kommen (Runde 2 §2) — der Beat sitzt auf dem
     Crew-Update-Cut.
- **`v058` (3:03, Jupiler-Selfie):** Christian: "das ist ein bisschen zu viel, es muss
  zeitgleich in 3:04 mit dem Crew-Update stehen" → `v058` verkürzen bzw. so legen, dass das
  Crew-Update-Overlay auf `v058`/erstem Akt-2-Bild sitzt.
- Danach zu viele Bilder im Block → ausdünnen (Runde 2 §2 gilt weiter).

---

## 3. Akt 2 (Miserlou) — per Clip

### La Bécasse / erste Kneipe (~3:05–3:22)
- **`v059` (3:05, La-Bécasse-Gasse, Hochkant):** `fit:"blur"`. Einstieg (Runde 2: Eingangs-
  bild raus, dieses ist der Einstieg).
- **`v062` (3:11, Kwak Hochkant):** `fit:"blur"`.
- **`v063` (3:13, IMG_1452):** Christian: "das ist ein Hochkantbild, ist aber nicht so
  verwendet worden" → `fit:"blur"`.
- **`v064` (3:14, IMG_1453):** "sehr unscharf … man könnte es rausnehmen, aber ich finde
  beide gut" → behalten, aber wenn Hälfte der Person abgeschnitten: `fit:"blur"`, sonst
  ganz raus. Nicht die halbe Person zeigen.
- **`v066` (3:18, IMG_8337, steht seitlich):** **LÖSCHEN.** "Das Bild muss raus, das ist
  nicht gedreht, ich muss hier keine gedrehte Sache haben."
- **`v067` (3:19, großes Gruppen-Selfie Bierstube):** super, bleibt. Hochkant → `fit:"blur"`.
- **`v068` (3:21, Timmermans-Emailleschild):** Christian: **rausnehmen** ("das Bild mit
  Timmermans Witte / Blanche würde ich rausnehmen").
- **`v069` (3:22–3:25, IMG_1460.MOV, Hochkant-Selfie-Video):** dran schneiden. "Beginnt bei
  3:22/3:23, entscheidende Szene eher 3:23 Anfang bis 3:25" → `src_in` ~1 s später, ggf.
  Fenster nach rechts. **`fit:"blur"` für das Hochkant-Video** (§0.2). `oton-01-img1460`
  entsprechend nachziehen.

### Delirium (~3:29–3:42)
- **`v072` (3:29, Delirium-Bar-Innen, Hochkant):** `fit:"blur"`.
- **`v074` (3:32, Delirium-Neon-Logo) + `ov-fx-delirium`:** Christian: **`ov-fx-delirium`
  (Text "Delirium") raus** — "Delirium steht im Foto selbst schon drin." Stattdessen: **das
  ganze Bild leicht wackeln lassen** ("dieser Wackel-Effekt kann übernommen werden, aber
  wichtig: das ganze Bild muss zu sehen sein"). → Overlay `ov-fx-delirium` entfernen;
  `timeline-builder` gibt `v074` einen dezenten Wackel (`anim`/kleiner Positions-Jitter auf
  dem Clip) statt KB, **volles Bild** (`fit:"pad"` falls nicht 16:9).
- **`v075` (3:33, IMG_1465, "leuchtender blauer Haarreif"):** Christian: "3:33 Elefant … zu
  weit reingezoomt, zu viel vom Bild weg" — Zoom-Faktor runter / `fit:"pad"`.
- **`v076` (3:35, IMG_1466):** "zu weit reingezoomt, nur noch ein Teil des Bildes" →
  Zoom raus / `fit:"pad"`.
- **`v077` (3:37–3:38, IMG_1473):** **ENTFERNEN** ("das Foto entfernen, das brauchen wir
  nicht").
- **`v078` (3:38, Delirium-Glas Extrem-Nah, `fit:blur`):** bleibt.
- **`v079` (3:40, "Grote", Froschperspektive Kreis):** "ist super" — bleibt.
- **`v081` (3:45, Aufzug-Selfie):** "3:49 finde ich gut" — bleibt.

### Rooftop Bar 58 (~3:45–4:03) — NEU ORDNEN
- **`ov-rooftop` (~3:45, "Rooftop Bar 58 — wir kommen"):** Christian mag Pink + Position
  ("finde ich gut mit dem Pink, Positionierung cool") → **oben links bleibt**, Pink-Frontface
  erlaubt, Comic-Doppelebene, größer.
- Reihenfolge um die Bar (Christian diktiert): "bei 3:48 kommt die 58 (`v082`), danach zeigen
  wir die Bar bei 3:50 (`v083`), dann das Bild einfügen (`v086` Gruppe auf der Terrasse /
  IMG_1503, ~3:55), dann nochmal die zwei Aussichtsbilder (`v084`/`v087`/`v089`)."
  → Sequenz: `v082` (58) → `v083` (Bar-Deck) → `v086` (Gruppe Rooftop, vorziehen) →
  `v084` (Panorama) → `v087`/`v089` (Sonnenuntergang).
- Zu viele Sonnenuntergänge → ausdünnen (Runde 2 §Rooftop). `v085` kann raus.
- **`v089`/`v102` (IMG_1508/IMG_1518, Sonnenuntergang-Silhouette):** einer davon **in die
  Mitte** der Rooftop-Sequenz (Runde 2), nicht neben Karaoke.

### Corona / Stay hydrated / Christoph (~4:01–4:20)
- **`v090` (4:01, Corona-Anstoßen von unten, Hochkant):** "muss", `fit:"blur"`.
- **`v091` (4:04, IMG_1531):** Umfeld — Bewegung rein (§0.1).
- **`v092` (4:05, IMG_1543, Zunge + Corona, Hochkant):** "zu viel vom Bild abgeschnitten,
  muss kleiner / anders gezoomt / Hochkant." → `fit:"blur"`, Motiv ganz zeigen.
- **`ov-hydrated` (~4:05, "stay hydrated"):** **mittiger** ("das Stay ist zu weit rechts"),
  oben rechts bleiben, **mindestens 2× so groß**, "stay" + "hydrated" als zwei Elemente,
  **Zitter-Effekt** — Gold-Front und Pink-Schatten wackeln **im gleichen Rhythmus** (§0.3.7).
- **`v093` (4:07, ganze Gruppe Reihe):** bleibt.
- **`v094` (4:10, IMG_1515, `fit:blur`):** Runde 2 `nice`.
- **`ov-christoph` (~4:07, "Wo ist Christoph???"):** Christian: **nach ganz links / unten
  links** ("könnte man nach ganz links packen, unten links reinpacken, das ist super"),
  gelbe/Gold-Schrift, drei Fragezeichen, **nicht mittig**. `party-fx`: placement
  `bottom-left`, slant dann **positiv** (kippt nach rechts) — Christian hat bei Cast
  `Christoph` rechts die Links-Kippung verlangt; bei bottom-left ist Rechts-Kippung korrekt.
- **`v095` (4:11, IMG_1544 Corona gegen Sonne, `color_pop`):** `nice`, Werbe-Look (Runde 2).
- **`v096`/`v097` (4:13–4:16, blaue Stunde Gruppe):** eins reicht (Doppelung), das mit
  weniger Skalierungsbedarf behalten.
- **`v100` (4:20, IMG_1707, Rooftop-Selfie blaue Stunde) + `ov-fx-krone-1707`:** Christian:
  **Krone raus.** Das ist ein Hochkantbild → `fit:"blur"`. **Muss VOR das Bild bei 4:17
  (`v098`)** — sonst "hüpfen wir zurück in die Rooftop-Bar". → `v100` vor `v098` einsortieren,
  `ov-fx-krone-1707` **löschen** (Overlay + `party-fx-recipe.py`).
- **`v101` (4:22, IMG_1588, blau beleuchtete Fassade):** Christian will das **Hochkantbild
  (`v099` IMG_1557 Röhre/Neonringe)** und ein Querbild — `v099` Hochkant `fit:"blur"`. Das
  Corona-Doppelbild (`v091`/`v095`-Klasse, zweites Corona) eher **raus** (Runde 2 `v095` =
  `nice`).
- **`v104` (4:28, IMG_1706, Zunge-raus-Selfie Nacht) + `ov-fx-herz-1706`:** Christian ordnet
  das "vor der Tür"-Bild ausdrücklich in die **Rooftop-Sequenz** ein (Runde 2 §4 auch). Herz-
  Sticker `ov-fx-herz-1706` hier ist ok (klein). `v104` "muss gegen Ende der Rooftop/Park-
  Sequenz, ~4:15 davor oder dahinter" → früher einsortieren.
- **`v102` (4:25, IMG_1518 Sonnenuntergang):** "muss gegen Ende von dem Park kommen, ~4:15"
  → vorziehen in die Rooftop-Mitte.

### Downtown / Burger-Stop (~4:30–4:41)
- **`v105`/`v106` (Downtown):** Kann-Bilder (Runde 2).
- **Burger `v107`–`v109`:** gut, bleibt.
- **`ov-token` (~4:39, "wolle Token kaufen ???"):** Bild `v110` (Claude-Schild "Frische
  Token", Hochkant) → `fit:"blur"`. Text größer, Comic-Doppelebene, drei Fragezeichen,
  "wolle" klein / "Token" groß / "kaufen" klein.

### Red Karaoke + Cast-Intro (~4:42–5:26)
- **`v112` (4:43, KARAOKE-Neon) = Einstieg Karaoke** (Christian: "guter Einstieg").
- **`v113` (4:45, "La Pod"/"La Red" rote Leuchtschrift):** Christian: **dieses "La Red"-Bild
  ans ENDE der Karaoke-Sektion** — letztes Bild, bevor die nächste (Außen-)Szene kommt.
  → `v113` aus Position 4:45 herausnehmen und **hinter `v148`** (Ende Karaoke) einsortieren.
- **`v114` (4:46, IMG_1608 Anstoßen) = neuer Karaoke-Einstieg nach `v112`** ("4:45 das Red
  Soilbag" ~ Christians Ausdruck; er meint das Anstoß-Bild als Einstieg).
- **`v115` (4:48, IMG_1610.MOV) bzw. das Foto bei 4:48:** "funktioniert nicht, komplett
  abgeschnitten, muss Hochkant sein, da darf nicht die Hälfte fehlen." → `fit:"blur"`.
- **`v116` (4:50, IMG_1613.MOV Anstoßen Kurze):** Video, bleibt.
- **Knutsch-Szene ~4:57 (`v116` Ende / Umfeld):** Christian: "bei 4:57 wird sich geknutscht"
  → **Herzchen-Cluster-FX** (§0.4): viele rosa Herzen verschiedener Größe, sprudeln aus der
  Bildmitte, poppen, schnell, viele. `party-fx` R3-T8 + FX aus R3-T2.
- **`v117` (5:01) ↔ `v118` (5:02):** **tauschen** ("das Bild bei 5:00/5:01 muss getauscht
  werden mit dem dahinterliegenden Bild"). Das dahinterliegende (`v118`) sollte Hochkant sein
  → sonst `fit:"blur"` (Kopf oben angeschnitten). `v117` "war zu viel die eine Person".
- **`v121` (5:05, IMG_8656, lila Karaoke-Screen mit Songtitel):** **KOMPLETT RAUS.** "Da wird
  ein Musiktitel angezeigt mit so einem Liederbild, das kann komplett raus, definitiv, das
  brauchen wir nicht."
- **Cast-Intro `ov-cast-01..09` (~5:06–5:15):** Die dahinterliegenden Bilder sind
  **Hochkantbilder → als Hochkant reinnehmen** (`fit:"blur"`), **länger stehen** (§0.7,
  ~1,3–1,6 s je Person). Schrift **unten links**, **2× so groß**, Gold vorn / Pink-Shadow,
  Slant PLACEMENT-abhängig: Namen rechts kippen nach links, Namen links kippen nach rechts
  (§0.3.4). "Der wird durchgerattert, künstlerisch, mit Überblenden — sieht super aus"
  (bleibt), aber Namen länger + größer. Reihenfolge unverändert (Witte · Christoph · Matti ·
  Bartosz · Hagi · Bernhard · André · Skuub · Micha im Delirium).
- **`v131`/`v132`/`v134`/`v136` (IMG_1621.MOV Partybus, Speed-Ramp):** bleibt.
- **`v133` (5:19, Gruppe Daumen hoch):** bleibt.
- **`ov-lampen` (~5:22, "Gehen hier etwa schon die Lampen aus?"):** Christian: **zweizeilig**
  — "Gehen hier etwa schon" / (neue Zeile, ~3 Tabs eingerückt) "die Lampen aus". Etwas
  größer, Comic-Doppelebene, Slant passt.
- **`v137` (5:26, IMG_1623.MOV "Micha im Delirium" Lampen-Szene):** "einfach super, bleibt
  wie es ist."
- **Antwort-Video auf "Lampen aus?": das Video bei ~5:48 (`v144`/`v145` IMG_1637.MOV
  Karaoke-Gesang) soll DIREKT NACH der Lampen-Szene kommen** — Christian: "können wir dieses
  Video bei 5:48 als Antwortvideo auf die Frage 'gehen hier etwa schon die Lampen aus' … nach
  dem Video soll direkt das Video, was ich gerade gemeint habe." Danach `ov-natuerlich`
  ("Natürlich … (noch nicht)" — Text: **"natürlich" / "(noch) nicht"**, Klammern um "noch").
  → `timeline-builder`: `v144`/`v145` (+ `oton-03-img1637`) aus Position 5:37–5:44 an Position
  direkt nach `v137` ziehen; `ov-natuerlich` dahinter. Danach läuft die Reihenfolge ab
  `v138` normal weiter ("die Reihenfolge wird erhalten, das sieht alles super aus").
- **`v135` (5:22, IMG_1634):** "natürlich" gehört hier weg / später — s.o., `ov-natuerlich`
  wandert mit dem 5:48-Video.
- **`v139`/`v140`/`v142` (IMG_1635.MOV Dance, Speed-Ramp, `color_pop`/`speedlines`):** bleibt,
  FX kräftiger.
- **`v143` (5:36, IMG_1640, scharfes Bar-Bild):** "sehr cool, aber überhaupt keine Bewegung
  — da muss Bewegung rein." → KB Zoom + leichte Drift, Easing.
- **`v144`/`v145` (IMG_1637.MOV, Hauptstelle Gesang):** vorgezogen (s.o.), O-Ton leise unter
  Musik (`oton-03`, kein Ducking).
- **`v146`/`v147` (5:44–5:49, Karaoke-Menge/Tanz-Videos):** bleiben.
- **`v148` (5:49, IMG_4835.MOV Karaoke Hochkant, `color_pop`):** `fit:"blur"` (§0.2). Danach
  **`v113` ("La Red"-Bild)** als letztes Karaoke-Bild (s.o.), dann raus in die Nacht.

### Weiterziehen / Taxi (~5:53–6:05)
- **`v149`–`v152` (nächtliche Gassen, Delirium Village, Dubliner, Pizzeria-Gasse):** bleiben.
- **`v150` (Delirium Village Neon, `fit:blur`):** bleibt.
- **`ov-weiterziehen` (~5:59):** Text **"Noch ahnten sie nicht" / "wie toll die Nacht wird"**
  (Christian: "Noch ahnten sie nicht, wie toll die **Nacht** wird" — nicht "Abend"; neue
  Zeile vor "wie toll die Nacht wird"). **Linke Seite / Mitte, richtig groß, unterer
  Bereich.** Comic-Doppelebene.
- **`v153` (6:00, Auto-Rückbank Nacht):** bleibt ("gucken aus dem Fenster, ist gut").
- **`v154` (6:02, IMG_1653.MOV Taxifenster):** bleibt.

### Gurken-Ende Akt 2 (~6:05–6:16) — NEU ORDNEN
Christian diktiert die Reihenfolge und die Texte. Ist-Zustand: `v155` (Gurke Kühlschrank +
`ov-wtf`), `v156` (IMG_1656 Betten), `v157` (IMG_1658 Crew-Selfie oben), `v158` (IMG_1659
Crew Arme breit + `ov-ichwaresnicht`), `v159` (IMG_1661 Gurke Kühlschrank + `ov-gurken`).

Christian:
- Das **zweite Gurkenbild wurde fälschlich entfernt** und muss zurück — es gibt zwei
  Gurken-Kühlschrank-Bilder (`v155` IMG_1660, `v159` IMG_1661). Beide behalten.
- **`v155` (Gurke, "WTF"):** Bild **komplett zeigen** ("hier fehlt die Hälfte vom Kopf") →
  `fit:"blur"` bzw. `fit:"pad"`. **`ov-wtf` nach OBEN LINKS** (Christian: "das WTF muss auf
  der linken Seite sein, links unten, oder links oben vielleicht sogar — oben links, ziemlich
  gut"), **doppelt so groß**, Gold-Front / Pink-Shadow. Christian erwägt für WTF sogar
  Pink-Front — `party-fx` darf Pink nehmen.
- Reihenfolge (Christian): Gurke-WTF (`v155`) → dann die **zwei Nachthaus-Bilder** `v156`
  (IMG_1656) und die im Bett → dann **"Ich war es nicht"** groß **unten rechts** auf
  Christophs Bild (`v158` bzw. das Bild bei 6:12) → dann **zweites Gurkenbild `v159`** mit
  Text **"Der Michael mag Gurken. / Gib mir Gurken. / Der Michael braucht Gurken."** (größer,
  besser lesbar, Comic) → dazu **oben rechts eine kleine Antwort: "Rät kein Käse"** (neues
  Overlay `ov-raetkeinkaese`).
- **`v156` (6:09) ↔ das Bild bei 6:11 (`v157`): tauschen** — Christian: "das erste Bild, das
  dann zu sehen ist, ist das Bild von 6:11, und das zweite von 6:09. Die beiden tauschen in
  der Reihenfolge."
- **`ov-ichwaresnicht`** bei **~6:12**, groß, unten rechts.
- **`v158`/`v159` "ich war es nicht"-Bild (Christoph, bei ~6:13) ist das LETZTE Bild von Akt
  2**, und **hier läuft die Musik langsam aus** (§0.6): Miserlou fade-out endet hier, WIMM
  fade-in beginnt ~6:13.
- Kleiner Sound-Check-Moment danach ("dann checken sie kurz den Sound") — die kurze
  Schwarzblende `v160` bleibt.

---

## 4. Aftermath / Outro (Where Is My Mind) — ~6:16–7:08

- **WIMM-Anfang weich einblenden** (§0.6). Der Where-Is-My-Mind-Titel: **Comic-Schrift ~5×
  so groß** ("hier haben wir sehr viel Platz"). Das erste Aftermath-Bild (`v161`, IMG_2644
  Sofa) ist **zu stark gezoomt** → Zoom-Faktor / Ausschnitt korrigieren.
- **`v161` (6:18, Sofa):** Christian: "beim ersten Bild in 6:22 schreibt Konkretext rein,
  Bild muss richtig gezoomt und der Ausschnitt passen." → `fit:"pad"` / Zoom moderat, KB
  dezent. (`ov-wimm` verschieben, s.u.)
- **`ov-wimm` (~6:19, "Where is my mind?"):** Christian: bei **~6:24 oben links**, und
  **"mind" nochmal 4× so groß** mit Fragezeichen. → `party-fx`: eigenes großes Titel-Overlay,
  "Where is my" normal groß + "mind?" massiv (eigener `<tspan>` mit ~4× `font-size`),
  placement `top-left`, Bangers, Gold-Front / Pink-Shadow.
- Aftermath-Bild-Reihenfolge: Runde 2 §"Aftermath — feste Bild-Reihenfolge" bleibt die
  Grundlage. Runde 3 ergänzt nur:
  - **`v162` (6:22, IMG_1665, Kopf 2/3 angeschnitten):** Ausschnitt/Zoom korrigieren
    ("die Person vom Kopf, zwei Drittel oben vorm Kopf").
  - **`v163` (6:27, IMG_1666 Daumen auf sich):** "danke Jungs"-Klasse, ok.
  - **Kotzbild `v166` (6:42, IMG_1667):** **etwas kürzer** ("ein bisschen zu lange").
  - **`v167` (6:47, IMG_1668):** Zoom-Faktor stimmt nicht → anpassen.
  - **`v168` (6:51, IMG_..., Kopf angeschnitten):** Ausschnitt/Zoom anpassen.
  - **`v169` (6:56):** letztes Foto — zoom-technisch checken.
- **Crew-im-Wohnzimmer-Bild** (`v164` IMG_1663) bleibt ("noch mal die Crew zusammen im
  Wohnzimmer").
- **Outro `v170` ("Danke Jungs"):** **2–3 s länger stehen**, Musik entsprechend länger
  (§0.6). Danach Musik aus, Fade auf Schwarz (`v171`), Ende. Kein sauberer harter Cut nötig,
  "lassen wir so".
- Aftermath-Textinhalte bleiben (Runde 2 §Schluss: "Drink responsibly" · "Danke, Jungs" ·
  "Super Crew, tolle Erinnerung" · "Genug Käse" · "Ein unvergesslicher Abend" · "Micha im
  Delirium") — alle im neuen Comic-Doppelebene-Look, nicht über Gesichtern.

---

## 5. Overlay-Liste Runde 3 (party-fx `party-fx-recipe.py`, R3-T3)

| Overlay | Änderung |
|---|---|
| **alle** | Bangers-Font; Gold-Front + **harter Pink-Schatten +10/+10 px @ 4K**; **≥ 2× Größe**; Slant-Vorzeichen abhängig vom Placement (right → neg, left → pos) |
| `ov-letsgo` | placement **top-right**, groß |
| `ov-sulemann` | Text **"Der Mann des Abends" / "Pizzamann Sülemann"** (ü + nn) |
| `ov-biere` | Text **"500+ Biere"** (R3-T4: Belgian Beer Weekend = 500+ Biere / 50+ Brauereien); sehr groß |
| `ov-praesente` | placement **top-left**, sehr groß |
| `ov-geniesst` | größer, Gold |
| `ov-kunstfigur` | **LÖSCHEN** (Overlay-PNG + Clip in `timeline.json`) |
| `ov-crewupdate` | Text zweizeilig **"Crew-Update" / "Die verlorenen Söhne stoßen dazu"**, größer |
| `ov-rooftop` | Pink-Front erlaubt, top-left bleibt, größer |
| `ov-hydrated` | mittiger ("stay" weniger weit rechts), 2×, **Jitter** (Gold+Pink synchron) |
| `ov-christoph` | placement **bottom-left**, Gold, drei "?" |
| `ov-fx-krone-1707` | **LÖSCHEN** |
| `ov-fx-herz-1706` | bleibt (kleiner Sticker) |
| `ov-fx-delirium` | **LÖSCHEN** (Text steckt im Foto; Bild wackelt stattdessen) |
| `ov-token` | größer, "wolle"/"Token"/"kaufen" Größenstaffel, drei "?" |
| `ov-lampen` | zweizeilig, 2. Zeile eingerückt |
| `ov-natuerlich` | Text **"natürlich" / "(noch) nicht"**; wandert ans 5:48-Video |
| `ov-weiterziehen` | Text **"Noch ahnten sie nicht" / "wie toll die Nacht wird"**; links/Mitte, sehr groß, unterer Bereich |
| `ov-wtf` | placement **top-left**, 2×, Pink-Front erlaubt |
| `ov-ichwaresnicht` | placement **bottom-right**, sehr groß |
| `ov-gurken` | größer/lesbarer |
| **`ov-raetkeinkaese`** (neu) | "Rät kein Käse", placement **top-right**, klein-mittel, auf `v159` |
| `ov-wimm` | **NEU als Titel:** "Where is my my" + **"mind?" ~4× Größe**, placement **top-left**, ~5× Gesamtgröße |
| `ov-cast-01..09` | 2× Größe, unten links/rechts, Slant-Vorzeichen nach Placement, längere Standzeit im Clip |
| **FX** | `hearts`-Cluster (Knutsch-Szene ~4:57), `sparkles` (2–3 drehende Sterne, verteilt an lebendigen Akt-2-Stellen) |

---

## 6. Code-Aufgaben (R3-T2, `frameforge/render.py`)

1. **Pan erzwingt Mindest-Zoom.** In `_kenburns_expr`: wenn `|dx|>0` oder `|dy|>0` und
   `max(z_from,z_to) < 1.08` → beide Zoomwerte auf ≥ 1.08 anheben (Schwenkraum). Dokumentiert
   mit dem Befund aus dieser Session.
2. **`ease: "in"`** = beschleunigende Kurve `p = pow(n, 1.7)` (Bewegung läuft bis zum Cut
   durch, kein Ease-out-Stillstand). `"smooth"`/`"linear"` unverändert.
3. **`fit:"blur"` auf Video verifizieren** — Mini-Render (2–3 Hochkant-Videoclips) durch
   `build_filtergraph` + `_run_ffmpeg`, Frame sichten (kein schwarzer Balken).
4. **`hearts`-Effekt** (`Effect(type="hearts")`): über `enable`-Fenster viele Herz-Glyphen
   (drawtext ♥ oder overlay eines Cluster-PNG) verschiedener Größe, aus der Bildmitte nach
   außen driftend + Alpha-Puls. Parameter `at`, `dur`, `count`, `color`. Analog `_color_pop_expr`.
5. **`sparkles`-Effekt** (`Effect(type="sparkles")`): 2–3 rotierende Stern-Glyphen, Gold/Pink,
   Alpha-Puls, an `at`/`dur`. (Kann dieselbe Mechanik wie `hearts` teilen.)
6. Tests + `ruff` + `doctor` grün. Bestehende Timelines (`proto`, `test-timelapse-journey`)
   unverändert lauffähig.

---

## 7. Nach dem Preview (R3-T10, blockiert — braucht Christian)

- Christian sichtet neues Preview → `frameforge approve` → **4K-Final-Render in Chunks**
  (HANDOVER: 172 Inputs, nicht in einem Pass; `render_final` bzw. Chunk-Weg).
- **Website `web/sites/michael-jga-2026/`**: Video einbetten + Download-Link. Vorbild: wie
  bei den Norwegen-Videos gelöst (`web/` prüfen).
- **Upload SSH-Server:** Christian braucht Ziel-Pfad + Datei-Benennung. **Zwei Videos
  getrennt halten**, nicht vermischen. → **offene Frage an Christian**, wenn er wach ist.
- Christian will "morgen früh ein fertiges neues Preview-Video". Final-Render + Website erst
  nach seiner Freigabe.
