# Detail-Regie Export "JGA" — RUNDE 5 (4. Preview-Feedback)

Quelle: Christians Sichtung des **vierten** Previews `preview/JGA_preview.mp4`
(6:59,5 / 419,53 s, aus R4-T6), Voice-Transkript 2026-09-11. Christian sichtet live, gibt
Zeitmarken auf Sekundenbasis an.

**Ergänzt und überschreibt punktuell `editorial-notes-round4.md` … `.md`.** Wo Runde 5
widerspricht, gilt Runde 5. Alle Agenten lesen **alle fünf** Dateien.

Zeitangaben `M:SS` = Position im **6:59,5-Preview** (= `timeline.json` Stand `a31095a`,
Dauer 419,5 s). Clip-IDs beziehen sich auf dieselbe Datei (171 Video / 34 Overlay / 25 Audio).
Zeit→Clip-Tabelle: `scratchpad/clipmap.txt` bzw. `round5-timeline.py` baut sie neu.

Christians Gesamturteil: **"schon wirklich großartig … hier geht es mehr um Präzision."**
Feinschliff. Danach FHD- + 4K-Download-Version — **erst nach Freigabe dieses Previews**.

---

## 0. Globale Regeln Runde 5

### 0.1 Text-Look — 3 Ebenen bleibt, aber Front IMMER WEISS
Der 3-Ebenen-Look aus Runde 4 (Weiß-Front / Schwarz −6/−6 / Pink +10/+10, Bangers) bleibt.
Christian rügt **zwei Verstöße**, wo die Frontface nicht weiß ist:
- **`ov-geniesst` (~2:36):** Frontface ist **gelb** → muss **weiß**. ("Fontfehler … da ist
  eine gelbe Schrift … der muss weiß sein, dass wir da eine konsistente Nutzung haben.")
- **`ov-wtf` (~5:59):** Frontface ist **pink** → muss **weiß**. ("bei dem WTF ist alles pink …
  die Frontface ist auch pink, die müsste aber weiß sein.")

→ **Die Gold/Orange-Ausnahme aus Runde 4 entfällt komplett.** `front=WHITE` für **alle**
Text-Overlays, ohne Ausnahme. `GOLD_HI` nicht mehr als Front verwenden.

### 0.2 Text-Neigung
Runde-4-Regel bleibt: **gerade** oder **steigend links-unten → rechts-oben**, **nie fallend**.
Runde 5 bestätigt das ("Texte stürzen ab" kommt nicht mehr vor). Einzel-Deltas:
- `ov-praesente`: Winkel **ist jetzt gut** — **nicht weiter drehen**.
- `ov-wtf`: **etwas schräger** stellen (mehr Steigung) + **kursiv**-Anmutung.
- `ov-sulemann-a`, `ov-christoph`, alle `ov-cast-*`: weiterhin **ganz gerade**.

### 0.3 Text-Größe (Deltas ggü. Preview `a31095a`)
Grundlinie Runde 4 (regulär ×2) bleibt. Runde-5-Änderungen:
| Overlay | Runde-5-Größe |
|---|---|
| `ov-crewupdate` | **+10 %** ("nochmal 10 % größer") |
| `ov-geniesst` | **+10 %** ("minimal größer, 10 %") + tiefer setzen (s. §1) |
| `ov-praesente` | **etwas größer** ("könnte noch ein bisschen größer sein") |
| `ov-mok-detektor` | **deutlich größer**, 2-zeilig (s. §1) |
| `ov-hydrated` | **×2 ggü. jetzt** ("mindestens doppelt so groß" — die −15 % aus R4 werden zurückgenommen) |
| `ov-lampen` | **ein ganzes Stück größer** |
| `ov-wtf` | **+20 %** |
| `ov-gurken` | **größer, besser lesbar** (viel Text) |
| `ov-raetkeinkaese` | **größer, besser lesbar** |
| `ov-sulemann-a`/`-b` | Größe ok, **+1 s Standzeit** (viel zu lesen) |
| `ov-ichwaresnicht` | Größe ok |
| Rest | Runde-4-Stand |

### 0.4 Ken Burns — noch eine Stufe ruhiger + echte Varianz
Christian: "Die Ken-Burns-Sachen sind viel, viel besser, bei allen Bildern." Aber:
- **Manche Bilder super-super-minimal** oder **wirklich statisch** (Mini-Zoom reicht). Grund:
  wenn zwei aufeinander folgende Bilder beide **rauszoomen**, "hat man das Gefühl, man zoomt
  nur aus dem Bild raus, das wirkt komisch."
  → **Nie zwei aufeinander folgende Foto-Clips beide `zoom-out`.** In/Out strikt abwechseln,
  bei erzwungenen Out-Clips (v021/v036/v037) die Nachbarn auf In zwingen.
- **Mehr seitliche Bewegung** (links/rechts), nicht nur rein/raus. Aber: **langsam, nicht
  stark, kleine Varianz.**
- **Richtung innerhalb eines Clips NICHT wechseln** — bei Bildern, die "nach rechts gehen"
  bzw. "nach links", die Richtung über den Clip konstant halten (statisch = eine Richtung).
- **Erste Bilder (v003–v015): fast nichts ändern** ("bei den ersten Bildern würde ich fast
  gar nichts ändern"). Nur Amplitude minimal runter, sonst Runde-4-Stand lassen.
- **`v040` (2:05) bleibt unangetastet** (Christian-Referenz, "ich mag es, würde ich drin
  lassen").
- **Near-static-Set** (nur Mini-Zoom `Z_LO → Z_LO+0.020`, **kein Pan**): eine über den Film
  verteilte Auswahl bekommt echten Quasi-Stillstand. Vorschlag: `v006, v013, v020, v034,
  v049, v135, v150, v167` (an Preview justierbar).
- **Namentlich zu unruhig** (Runde 5): Bilder bei **1:27 / 1:28 / 1:29 = `v028`, `v029`** —
  "zu viel Bewegung … immer zu rein, raus, links, rechts … muss ruhiger sein oder weniger
  bewegen." → beide ins Near-static-Set (Mini-Zoom, kein Pan).
- **`v039` (2:02, Äxte-Vitrine von oben):** eher **rauszoomen**.
- Global für alle KB-Clips prüfen.

### 0.5 Musik / Audio-Timing
1. **Intro:** erstes Bild (`v003`) **doppelt so lang** (§1). Musikeinsatz so, dass der
   erste hörbare Ausschlag mit dem **Einblenden von `v003`** zusammenfällt.
2. **Akt-1-Ende / Übergang 3:03:** `music-01` (CL-Theme) muss **bis knapp an den 3:03-Cut**
   laufen — **≤1 s echte Stille**, dann Fade-out. Aktuell entsteht eine "2–3–4-Sekunden-
   Lücke" vor Akt 2. Die letzten Bilder vor Akt 2 (`v056` 2:59 + `v057` 3:01, "Frittenbilder")
   **bleiben** — den Akt-1-Rest ggf. minimal komprimieren, damit `v069` + `music-02`
   **exakt bei 3:03** sitzen (Toleranz 3:02–3:05). Der 3:03-Schnitt (`v069`-Video + O-Ton +
   Miserlou-Einsatz) ist **"super geschnitten, muss so bleiben"**.
3. **Akt-2-Musik (Miserlou) STOPPT bei ~6:03** — **nicht** bis 6:15 weiterlaufen. Vor
   `v160` (Schwarzblende ~6:03,7) läuft die Musik aus, **volle Stille** über die
   Schwarzblende. Christian: "bei 6.04 muss die Blende raus, das Audio muss raus, wir haben
   Stille … hier läuft immer noch das Audio, da sind wir schon beim zweiten Bild."
4. **WIMM (Pixies) startet IM SCHWARZ:** ~2 s Schwarzpause (`v160`), dann setzt `music-03`
   1–2 s **vor** dem Einblenden von `v161` (~6:05) ein — "das muss im Schwarz anfangen".
   `music-03` `tl_in` ≈ 364,0, `fade_in_s` ~1,5.
5. **Outro:** `jga-outro-card` ("JGA Crew" / "Danke Jungs") **+1,5 s** länger stehen.
   Danach kurze Schwarzblende, **dann neue Text-Karte `ov-thanks`, die stehen bleibt** —
   der Film endet **nicht auf Schwarz**, sondern auf diesem Text. Musik läuft vorher aus.
6. Ducking bleibt draußen.

### 0.6 FX
- **Speedlines bei 5:15 (`ov-fx-speedlines-v144`): RAUS.** "Das muss an der Stelle komplett
  raus. Das macht da keinen Sinn."
- **Speedlines bei 5:21 (`ov-fx-speedlines-v139`): RAUS** (schon Runde 4, bleibt).
- **Speedlines NEU auf Bild `v143` (5:29):** "Vielleicht können wir diese Lines auf die 529
  auf das Bild setzen." → einen Speedlines-Blitz dort platzieren (`dur` ~1,2 s).
- **Speedlines `v131` (5:01, Cast-Auftakt): bleibt.**
- **Cast-Linien-/Outline-Effekt (~5:05–5:15):** die Striche liegen "über Linie den Gesicht"
  (auf Nase/Stirn). → **freien Kernbereich der Linien ~30 % vergrößern** (Linien weiter nach
  außen skalieren), sodass mehr Gesicht durchkommt — **oder** den Effekt **kürzer** zeigen.
  Umsetzung in `party-fx-recipe.py` (`render_speedlines`/Cast-FX).
- **Herzchen (`ov-fx-herzen` / `ov-fx-herz-1706`):** Runde-4-Stand ist gut ("super mit den
  Herzchen"). **Keine Änderung.**

---

## 1. Intro & Akt 1

- **`v003` (erstes Bild, 0:05,5, aktuell 4,0 s): auf 8,0 s** ("doppelt so lang auf jeden
  Fall"). Schwarzblende davor (`v002`) bleibt. Danach `v003`.
- **`ov-letsgo` (~0:08):** "super toll reingeblendet, sieht cool aus." **Keine Änderung.**
- **30-Sekunden-Anker:** "Das Bild auf 30 Sekunden genau … nach 30 Sekunden muss genau
  dieses Bild da sein. Ist ein fester Anker, sollte so bleiben." Anker-Clip ≈ **`v011`**
  (aktuell 0:31,9). Nach `v003` +4,0 s / `v008` −3,2 s die frühen Clips (`v004`–`v007`) um
  in Summe ~0,8 s trimmen, sodass **`v011` `tl_in` ≈ 30,0** landet. An Preview feinjustieren.
- **`v008` (0:21): STREICHEN.** ("Das ist ein Kannbild … nimm das raus.") — **einziger**
  gestrichener Clip in Runde 5.
- **`ov-sulemann-a` / `-b` (~0:32):** Texte bleiben ("Der Mann / des Abends" o.l. gerade;
  "Pizzamann Sülemann Bestermann" u.r. groß). **+1 s Standzeit** je Element (3,0 → 4,0 s):
  "könnte minimal eine Sekunde länger stehen. Man muss schon relativ viel lesen."
- **`v022` (1:10):** Kannbild "zum Notrausnehmen" — **bleibt** (nur `v008` raus). Als Reserve
  notiert, falls Länge später klemmt.
- **`v027` (1:26):** Christian erwog "könnte eher weg" — Endentscheid: **bleibt** (nur `v008`).
- **`v028`, `v029` (1:27–1:29):** KB beruhigen → Near-static (§0.4).
- **`v037` (1:53–1:54):** **bleibt** ("wir lassen das bei 1,53 drin"). Doppelung akzeptiert.
- **`ov-biere` (~1:43):** "mega gut." **Keine Änderung** (Größe Runde 4 passt).
- **`v039` (2:00–2:02, von oben, Äxte-Vitrine):** eher **rauszoomen** (§0.4).
- **`v040` (2:07):** "ich mag es, würde ich drin lassen." **Unangetastet.**
- **Schoko-Block — Reihenfolge NEU (überschreibt R4-Swaps):**
  Aktuelle Reihenfolge: `v041` (2:08,5) · `v043` (2:11,5) · `v041b` (2:14,3) · `v045`
  (2:17,1) · `v044` (2:20,1) · `v046` (2:23,3).
  - Christian: "Das Bild bei 2:15 [`v041b`] … davor gesetzt werden … das Bild, was jetzt auf
    2:10 ist [`v041`], soll dahinter kommen und dann das Bild von 2:12/2:13 [`v043`]."
    → Triplet neu: **`v041b` → `v041` → `v043`**.
  - Christian: "Das Bild von 2:21 [`v044`] muss vor dem Bild von 2:18 [`v045`] kommen, weil
    2:18 [`v045`] gehört mit 2:24/2:25 [`v046`] zusammen."
    → Gruppe neu: **`v044` → `v045` → `v046`** (macht den R4-Swap `v044↔v045` rückgängig).
  - Resultierende Reihenfolge um den Schoko-Block:
    `v040` → **`v041b` → `v041` → `v043` → `v044` → `v045` → `v046`** → `v047` …
  - "Unpacking" (IMG_4790) bleibt draußen (bestätigt).
- **`ov-praesente` (~2:27):** Text bleibt **"Süßes Geschenk / für den / jungen Gesellen"**
  (Christians Formulierung Runde 5, Singular). **Etwas größer.** Winkel **ist gut** — nicht
  weiter drehen. Oben links.
- **`ov-geniesst` (~2:36):** Text bleibt ("Ein bisschen / genießt er es / ja schon").
  **Frontface WEISS** (war gelb). **+10 % Größe.** **Tiefer setzen** — Text ragt oben aus dem
  Bild → gesamten Block ~10 % der Bildhöhe nach unten. (Platzierung `top-left` → eigener
  Wert mit y ~22–24 %.)
- **`v051` (2:42):** Kannbild — **bleibt** (nur `v008` raus).
- **`ov-mok-detektor` (~2:48, auf `v052`):** Text **2-zeilig**: **"MOK"** (Versalien, sehr
  groß) / **"Detektor"** (kleiner, darunter). Oben links (Position ok). **Deutlich größer**
  als jetzt. 3-Ebenen, gerade.
- **`v054`/`v055` (MOK-Café / "Best Coffee", ~2:55):** leicht reinzoomen (Runde-3-Stand ok).
- **`v056` (2:59) + `v057` (3:01):** die "Frittenbilder" — **bleiben als letzte Akt-1-Bilder**
  vor dem 3:03-Cut. Akt-1-Musik läuft hier aus (§0.5.2).

---

## 2. Akt-1 → Akt-2 (3:03)

- **`v069`-Video + O-Ton + `music-02` (Miserlou) exakt bei 3:03** — "super geschnitten, muss
  so bleiben." Unverändert.
- **`ov-crewupdate` (~3:05):** Text bleibt ("Crew Update / die verlorenen Söhne / stoßen
  dazu"), rechte Seite. **+10 % Größe.** **+1 bis 1,5 s Standzeit** (2,2 → 3,5 s) — "das ist
  ein richtiger Punkt."
- Delirium/Fields/Kristoff: "fantastisch." **Keine Änderung.**

---

## 3. Akt 2 (Miserlou)

- **KB Akt 2 (`v058`–`v065` u. ä., kurze Clips):** "hier auch ein bisschen zu viel rein und
  raus zoomen, das muss ruhiger werden." → Amplitude runter, In/Out-Wechsel strikt (§0.4).
- **`ov-hydrated` (~3:59, "stay hydrated"):**
  - **Mittig** setzen (aktuell rechtsbündig — "können wir das mittig machen? … das Stay ein
    bisschen nach links"). Platzierung → **`bottom`/zentriert** (unterer Drittelbereich ok).
  - **×2 Größe** ggü. jetzt ("mindestens doppelt so groß"). Die −15 % aus Runde 4 werden
    zurückgenommen.
  - **Jitter/Wackel ab Frame 1** bleibt ("es wackelt super").
- **`ov-christoph` (~4:01):** Text NEU → **"Wo ist eigentlich / Christoph?"** ("wo ist
  eigentlich Christoph, würde ich sagen"). Gerade, unten links. 3-Ebenen.
- **`v097` ↔ `v100` tauschen** (4:02 ↔ 4:05): "Kannst du das Bild auf 4:05 mit dem Bild von
  4:02 tauschen, weil das ist dann noch ein bisschen mehr der Abschluss."
- **Rooftop-/Wings-Bild raus:** Christian will "das letzte Bild hier oben an den Wings,
  Rooftop-Bar wieder raus." Kandidat nicht eindeutig identifizierbar (`v098` 4:06 oder
  `v101` 4:10). **`v101` ist zugleich als Kannbild markiert, das er "drin lassen" will** →
  **kein Clip gestrichen**, an Preview mit Christian klären. (VERIFY.)
- **`v101` (4:10):** "ich finde das sehr schön … eher ein Kannbild, aber ich finde es gut."
  → **bleibt.**
- **`ov-fx-herzen` (~4:19):** "super mit den Herzchen." **Keine Änderung.**
- **`ov-token` (~4:39, "wolle Token kaufen"):** Text/Größe gut. Winkel bleibt (Runde 4,
  links-unten → rechts-oben). **Rechtsbündig / rechte Seite** legen (Platzierung
  `bottom-left` → `bottom-right`). **+~0,5–1,4 s Standzeit** (2,0 → 3,0 s).
- **`v117` (4:44):** "nur kurz da … muss ein bisschen später kommen, 2–3 Bilder nach hinten.
  Muss aber VOR den Cast kommen." → `v117` direkt **vor `v122`** (Cast-Auftakt) einsortieren:
  `v118` → `v119` → `v120` → **`v117`** → `v122` …

### Cast-Intro `ov-cast-01..09` (~4:48–5:00)
- Namen: Runde-4-Stand bleibt (gerade, groß, 3-Ebenen, `#09` nur "Micha").
- **Linien-/Outline-Effekt:** freien Kernbereich ~30 % vergrößern **oder** kürzer zeigen
  (§0.6) — Striche liegen aktuell im Gesicht (Nase/Stirn).
- Wechsel-/Durchratter-Effekt: bleibt ("alles gut").

### Lampen & Antwortvideo (~5:05–5:40)
- **`ov-lampen` ("Gehen hier etwa schon die Lampen aus?"):** **deutlich größer** ("ein
  ganzes Stück größer") + **+1 s Standzeit** (1,6 → 2,6 s).
- **Antwortvideo / Grinsen (~5:34–5:40):** "mit dem Video und den Grinsen, super auf jeden
  Fall." **Runde-4-Anordnung bleibt.**
- **`ov-natuerlich` ("natürlich / (noch) nicht"):** Text bleibt. **+1 s Standzeit**
  (2,2 → 3,2 s) — "könnte noch ein bisschen länger gezeigt werden."
- **Speedlines 5:15 raus; 5:21 raus; NEU auf `v143` (5:29)** (§0.6).

### Gurken-Ende Akt 2 (~5:47–6:03)
- **`ov-weiterziehen` ("Noch ahnten sie nicht wie toll die Nacht wird"):** gehört auf das
  Bild bei **5:47 = `v153`** (nicht 5:49). "Bei 5,47 muss der Text hin, der bei 5,51 gezeigt
  wird." → `ov-weiterziehen` an `v153` ankern. Unten / Mitte, gerade oder leicht steigend.
  **Deutlich größer.**
- **`v157` (5:56) ↔ `v156` (5:57) tauschen:** "bei 5:56 im Bild … muss mit dem Bild von 57
  getauscht werden."
- **`v158` (6:00) ↔ `v159` (6:02) tauschen:** "das Bild mit diesem Ich-war-es-nicht [`v158`]
  muss mit dem Gurkenbild [`v159`] getauscht werden … das Bild von 6:00 … muss unter das
  Bild von 6:02 dahinter kommen." → Reihenfolge neu: **`v159` (Gurkenbild) → `v158`**.
  Macht die R4-Notiz "`v158`/`v159` NICHT tauschen" rückgängig. Overlays folgen ihren Bildern.
- **`ov-wtf` (~5:59):** **Frontface WEISS** (war pink) (§0.1). **+20 % Größe.** ~10 % der
  Bildhöhe **tiefer**. **Schräger** (mehr Steigung) + kursiv-Anmutung. Bild dahinter
  (`v155`) `fit:"blur"` ✓.
- **`ov-ichwaresnicht` (~6:00):** Text bleibt ("Ich war es nicht!", "!" mit Schatten-Punkt).
  Größe ok. Etwas weiter links, unten rechts (Runde-4-Stand).
- **`ov-gurken` (Gurkenbild `v159`):** Text NEU, **dreizeilig**:
  **"Der Micha mag Gurken."** / **"Gib mir die Gurken."** / **"Er braucht sie dringend."**
  ("nur Micha … ohne el"). **Viel größer, gut lesbar.** **+1 s Standzeit** (2,6 → 3,6 s).
  Blendet **zuerst** ein (vor `ov-raetkeinkaese`). Unten links.
- **`ov-raetkeinkaese`:** Text-Korrektur → **"Red kein Käse!"** (R-E-D, Slang-Kurzform;
  war "Rede kein Käse!"). Oben rechts. **Größer / besser lesbar.** ~10 % **tiefer** setzen.
  Blendet **nach** `ov-gurken` ein (Versatz ~+1,0 s). Einblend-Tempo ist gut.
- **`v160` (Schwarzblende ~6:03,7):** Musik läuft davor aus, **volle Stille** (§0.5.3).

---

## 4. Aftermath / Outro (WIMM, ~6:05–7:02)

- **WIMM startet im Schwarz** (§0.5.4): ~2 s Schwarzpause (`v160`), `music-03` setzt 1–2 s
  vor `v161` ein, dann Bild `v161` einblenden.
- **`ov-wimm` ("Where is my mind?") auf `v162` (~6:12):** "super … muss aber deutlich
  tiefer, nochmal locker 20 % tiefer." → gesamten Block **~20 % der Bildhöhe nach unten**.
  **Länger stehen lassen** — über `v162` hinaus bis in `v163`, blendet **mit `v163`
  zusammen aus** (`dur` 4,5 → ~7,0 s). Zeilen enger (Runde 4), "mind?" groß (Runde 4),
  steigend / leicht nach links rotiert.
- **Aftermath-Reihenfolge (`v163`–`v169`): Runde-4-Stand bleibt.** "Dann ist die
  Bilderreihenfolge ganz gut."
- **`jga-outro-card` ("JGA Crew" / "Danke Jungs von der Crew"):** **+1,5 s** länger stehen
  (`src_out` +1,5). Blendet ins Schwarz aus.
- **NEU `ov-thanks` — Schluss-Karte, bleibt stehen:**
  - Nach der Outro-Karte kurze Schwarzblende (`v171`, ~2 s), **dann** eine neue schwarze
    Karte (~3,5 s) mit Text-Overlay `ov-thanks`, **in Bangers + 3-Ebenen-Look**, zentriert:
    - Zeile 1 (groß): **THANKS FOR WATCHING**
    - Zeile 2 (klein, darunter): **No animals were harmed in the making of this movie.**
  - Musik (`music-03`) läuft **vor** dieser Karte aus. Der Film **endet auf diesem Text**,
    nicht auf Schwarz. Keine weitere Schwarzblende danach.

---

## 5. Overlay-Liste Runde 5 (Delta zu round4 §5)

| Overlay | Änderung Runde 5 |
|---|---|
| **alle** | Front **immer WEISS** (Gold/Orange-Ausnahme entfällt). 3-Ebenen + Bangers bleiben. |
| `ov-letsgo` | keine Änderung |
| `ov-sulemann-a` / `-b` | Text bleibt; **+1 s Standzeit** (→ 4,0 s) |
| `ov-biere` | keine Änderung |
| `ov-praesente` | Text **"Süßes Geschenk / für den / jungen Gesellen"**; **etwas größer**; Winkel **nicht** weiter drehen |
| `ov-geniesst` | Front **WEISS** (war gelb); **+10 %**; Block **~10 % tiefer** |
| `ov-mok-detektor` | **2-zeilig** "MOK" (riesig) / "Detektor" (klein); **deutlich größer**; o.l. |
| `ov-crewupdate` | **+10 %**; **+1–1,5 s Standzeit** (→ 3,5 s) |
| `ov-rooftop` | keine Änderung (Runde-4-Stand ok) |
| `ov-hydrated` | **mittig** (war rechts); **×2 Größe** (R4-−15 % zurückgenommen); Jitter ab Frame 1 bleibt |
| `ov-christoph` | Text **"Wo ist eigentlich / Christoph?"**; gerade; unten links |
| `ov-token` | **rechtsbündig / rechte Seite**; **+0,5–1,4 s Standzeit** (→ 3,0 s) |
| `ov-lampen` | **deutlich größer**; **+1 s Standzeit** (→ 2,6 s) |
| `ov-natuerlich` | **+1 s Standzeit** (→ 3,2 s) |
| `ov-weiterziehen` | auf Bild **`v153` (5:47)**; **deutlich größer**; unten/Mitte, gerade/leicht steigend |
| `ov-wtf` | Front **WEISS** (war pink); **+20 %**; **~10 % tiefer**; **schräger** + kursiv |
| `ov-ichwaresnicht` | keine Änderung (folgt seinem Bild `v158` nach dem Swap) |
| `ov-gurken` | Text **"Der Micha mag Gurken." / "Gib mir die Gurken." / "Er braucht sie dringend."**; **viel größer**; **+1 s Standzeit** (→ 3,6 s); blendet vor `ov-raetkeinkaese` ein |
| `ov-raetkeinkaese` | Text **"Red kein Käse!"** (war "Rede kein Käse!"); **größer**; **~10 % tiefer**; blendet ~1 s nach `ov-gurken` ein |
| `ov-wimm` | auf `v162`; **Block ~20 % tiefer**; **`dur` → ~7,0 s** (bis in `v163`, gemeinsamer Ausblend) |
| `ov-cast-01..09` | Namen: Runde-4-Stand; Linien-FX: Kern ~30 % größer **oder** kürzer |
| **`ov-thanks`** (neu) | Schluss-Karte, zentriert: "THANKS FOR WATCHING" / "No animals were harmed in the making of this movie."; bleibt am Ende stehen |
| `ov-fx-speedlines-v144` (5:15) | **LÖSCHEN** |
| `ov-fx-speedlines-v139` (5:21) | **LÖSCHEN** (schon Runde 4) |
| Speedlines auf `v143` (5:29) | **NEU** |
| `ov-fx-herzen` / `ov-fx-herz-1706` | keine Änderung |

---

## 6. Code-/Timeline-Aufgaben Runde 5

- **`party-fx-recipe.py` → Runde 5:**
  - `front=WHITE` für **alle** `TEXTS` (Gold/Orange-Front raus). `ov-geniesst` `GOLD_HI` → `WHITE`,
    `ov-wtf` `PINK` → `WHITE`.
  - Texte: `ov-praesente`, `ov-christoph`, `ov-gurken`, `ov-raetkeinkaese`, `ov-mok-detektor`
    (2-zeilig) laut §5.
  - Größen: `ov-geniesst` +10 %, `ov-crewupdate` +10 %, `ov-praesente` größer, `ov-mok-detektor`
    groß, `ov-hydrated` ×2, `ov-lampen` größer, `ov-wtf` +20 %, `ov-gurken`/`ov-raetkeinkaese`
    größer.
  - Platzierungen: `ov-geniesst` tiefer, `ov-hydrated` mittig, `ov-token` rechts, `ov-wtf`
    tiefer + schräger/kursiv, `ov-raetkeinkaese` tiefer.
  - `ov-thanks.png` neu rendern (2 Zeilen, zentriert, 3-Ebenen).
  - Cast-Linien-FX: freien Kern ~30 % vergrößern (bzw. Clip-`dur` im Timeline-Skript kürzen).
  - `ov-fx-herzen`/`-herz-1706` unverändert.
- **`round5-timeline.py` (aus `round4-timeline.py` abgeleitet, schreibt `timeline.json`):**
  - `v003` `src_out` so, dass `dur` = 8,0 s. `v008` streichen. `v004`–`v007` um Σ ~0,8 s
    trimmen, `v011` `tl_in` ≈ 30,0 (an Preview justieren).
  - Reihenfolge: Schoko-Block `v041b→v041→v043→v044→v045→v046`; `v097↔v100`; `v157↔v156`;
    `v159→v158`; `v117` vor `v122`.
  - KB: `v028`/`v029`/`v006`/`v013`/`v020`/`v034`/`v049`/`v135`/`v150`/`v167` → Mini-Zoom,
    kein Pan. `v039` → Out. Nie zwei aufeinander folgende Fotos beide Out. `v040` `SKIP`.
    `v003`–`v015` Amplitude nur minimal runter.
  - Overlay-Retimes/-Placements/-`dur` laut §5. `ov-weiterziehen`→`v153`, `ov-wimm`→`v162`
    (`dur` ~7,0, tiefer), `ov-crewupdate`/`ov-sulemann-*`/`ov-lampen`/`ov-natuerlich`/
    `ov-token`/`ov-gurken` `dur` +.
  - Speedlines: `-v144` + `-v139` raus, neu auf `v143`.
  - Outro: `jga-outro-card` `src_out` +1,5; nach `v171` neue schwarze Karte (~3,5 s) +
    `ov-thanks`-Overlay; Timeline endet dort.
  - Audio: `music-01` bis ~1 s vor `v069`, `fade_out` ~1,5; `music-02` `tl_in` = `v069.tl_in`,
    **`dur` so, dass Ende ≈ `v160`-Start (~6:03)**, `fade_out` ~1,5; `music-03` `tl_in`
    ≈ 364,0, `fade_in` ~1,5, `dur` bis vor `ov-thanks`, `fade_out` so, dass vor der
    Schluss-Karte still.
  - `brief.yaml` `target_duration_s` nachziehen.
- **`render.py`:** vermutlich keine Änderung (KB-Regie = Timeline). Prüfen, ob eine
  End-Karte, die "stehen bleibt" (Overlay auf letztem Clip, Timeline endet mit Overlay) sauber
  durch `qc.validate` / `validate_semantics` geht.
- **Abnahme:** `validate_semantics` + `qc.validate` leer; `pytest` / `ruff` / `doctor` grün;
  `proto` + `test-timelapse-journey` unverändert lauffähig; neues Preview gesichtet auf:
  erstes Bild ~8 s, 30-s-Anker, 3:03-Cut + ≤1 s Stille, Miserlou-Stopp ~6:03, WIMM im
  Schwarz, Front überall weiß (kein Gelb/Pink), Schoko-Reihenfolge, Schluss-Karte bleibt
  stehen.

---

## 7. Nach dem Preview — FHD + 4K (blockiert, braucht Christians Freigabe)

Christian: **"ich brauche danach eine Full-HD-Version und eine 4K-Download-Version — erst
nach Freigabe des Previews."**

Unverändert zu round4 §7 / PROGRESS R4-T7: nach `frameforge approve` →
**4K-Final in Chunks** (`render --resolution 3840x2160 --crf 18 --preset medium
--chunk-s ~90`, Muster `web/sites/norwegen-2026/deploy/render-web-versions.sh`) +
**1080p-Streaming-/Download-Fassung** (`JGA_1080p.mp4` + `JGA_4k.mp4`). Dann Website
`web/sites/michael-jga-2026/public/` (Video-Block + Download-Link). Videos getrennt unter
`/videos/` auf dem Server, `rsync -avP`. **Offen: exakter SSH-Host + Server-Pfad** für
`micha-jga.skubus.de/videos/`, Traefik-Basic-Auth serverseitig. Norwegen- und JGA-Videosätze
strikt getrennt.
