# Audio-Plan — `michael-jga-2026` / `JGA`

Ergänzung zu `beatsheet.md` (Abschnitt „Musik-Layout") und `editorial-notes.md`
(„O-Ton-Fenster"). Alle Track-Werte hier sind **gemessen**, nicht geraten — Quelle:
`frameforge.audio.analyze_and_cache` (librosa BPM / Beat-Grid / RMS-Energiekurve).
Analyse für alle drei Pflicht-Tracks frisch gerechnet und gecacht (Schlüssel =
`sha256(Datei)`, siehe `frameforge.ingest.hash_file`):

| Track | Datei (`music/`) | Analyse-Cache (`music/analysis/`) |
|---|---|---|
| Vivaldi „Der Winter" I. Allegro non molto | `10 Violinkonzert No. 4 in F Minor, Op. 8, RV 297 - _Der Winter__ I. Allegro non molto.m4a` | `6b6a85a6da8c63a486d76ceee2e053f0c40359a3429e42e07eeb64b0267449cf.json` |
| Galvanize (feat. Q-Tip) [Edit] | `01 Galvanize (feat. Q-Tip) [Edit].m4a` | `8e97a8fcd204770c97bbfe52b31946140863b728e4eed6b75c98e5cfd23d7140.json` |
| Where Is My Mind (2007 Remaster) | `07 Where Is My Mind_ (2007 Remaster).m4a` | `beb194c5037419591732155139dfb8ec5d969b113fd9ab87221569db770e9011.json` |

**KI-Musik-Prompt:** nicht nötig — alle drei Tracks liegen vor und decken die
Energiekurve `build_drop_calm` des Presets ab.

---

## 1. Gemessene Tracklängen vs. Beat-Sheet-Annahme

| Track | Beat-Sheet nahm an | **gemessen** | Δ | BPM (gemessen) |
|---|---:|---:|---:|---:|
| Vivaldi | 211,5 s | **211,40 s** | −0,10 s | 147,66 |
| Galvanize [Edit] | 271,4 s | **271,39 s** | −0,01 s | 103,36 (Half-Time-Feel) |
| Where Is My Mind | ~235 s (≈40–45 s genutzt) | **234,97 s** | −0,03 s | 161,5 |

**Ergebnis: die Abweichungen sind vernachlässigbar (< 0,15 s).** Die Kapitel-Summen
des Beat-Sheets bleiben gültig. Nur die zwei **harten Musik-Anker** rutschen minimal:

| Anker | Beat-Sheet | **korrigiert (gemessen)** |
|---|---:|---:|
| Hard Cut 1 — Vivaldi-Ende → Galvanize | 3:31,5 (211,5 s) | **3:31,40 (211,40 s)** |
| Beat-Drop Galvanize (IMG_1451) | 3:40,5 (220,5 s) | **≈ 3:40,2 (220,24 s)** — s. §3.2 |
| Hard Cut 2 — Galvanize-Ende → Where Is My Mind | 8:02,9 (482,9 s) | **8:02,79 (482,79 s)** |
| Musik-Fade-out Start / Ende | 8:43,9 / 8:47,9 | **8:43,79 / 8:47,79 (523,79 / 527,79 s)** |
| Filmende (Schwarz) | 8:53,9 (533,9 s) | **8:53,79 (533,79 s)** |

→ **An `timeline-builder`:** die −0,10 s vor Hard Cut 1 im letzten Akt-1-Bild
(`F9615661-…1429`, 3,0 → 2,90 s) abfangen, die −0,11 s vor Hard Cut 2 im letzten
Akt-2-Bild (`IMG_1661`, 2,0 → 1,89 s). Alle übrigen Kapitelgrenzen unverändert aus
dem Beat-Sheet übernehmen.

---

## 2. AudioClip-Definitionen für `tracks.audio`

Feldnamen nach `frameforge.timeline.AudioClip` (`id`, `src`/`asset`, `type`, `tl_in`,
`src_in`, `dur`, `gain_db`, `duck_music_db`, `duck_fade_s`, `fade_in_s`, `fade_out_s`).
Pfade relativ zum Projekt-Root.

### 2.1 Track A — Vivaldi (Intro + AKT 1)

```json
{
  "id": "music-01-vivaldi",
  "src": "music/10 Violinkonzert No. 4 in F Minor, Op. 8, RV 297 - _Der Winter__ I. Allegro non molto.m4a",
  "tl_in": 0.0,
  "src_in": 0.0,
  "dur": 211.40,
  "gain_db": 0.0,
  "fade_in_s": 2.0,
  "fade_out_s": 0.0
}
```

- `fade_in_s: 2.0` — Vivaldi kommt langsam hoch, während das Intro-Standbild
  `JGA_INTRO.png` steht (deckungsgleich mit `audio.fade_in_s: 2` im Brief). Der erste
  stabile Beat liegt bei **4,853 s**; die 2-s-Rampe ist vorher abgeschlossen, der
  Puls trägt ab Sekunde 5 sauber.
- `fade_out_s: 0.0` — **kein Ausblenden.** Der Allegro läuft bis zum Schluss auf
  hohem Energieniveau (RMS 0,13 bei t≈200 s), endet abrupt → genau der im Beat-Sheet
  gewollte harte Schnitt.
- `dur: 211.40` = ganze Datei. **QC-Preview:** die letzten ~0,4 s auf einen
  Aufnahme-/Hallschwanz abhören; falls hörbar, `dur` auf ~210,9 ziehen und das letzte
  Akt-1-Standbild entsprechend länger halten — der Cut auf Galvanize bleibt bei
  211,40 s.

### 2.2 Track B — Galvanize [Edit] (AKT 2)

```json
{
  "id": "music-02-galvanize",
  "src": "music/01 Galvanize (feat. Q-Tip) [Edit].m4a",
  "tl_in": 211.40,
  "src_in": 0.0,
  "dur": 271.39,
  "gain_db": 0.0,
  "fade_in_s": 0.0,
  "fade_out_s": 0.0
}
```

- **HARTER Cut an beiden Enden**, kein Crossfade, keine Rampe (`fade_in_s` /
  `fade_out_s` beide 0). Galvanize startet bei `src_in 0.0`.
- Energiekurve: Galvanize [Edit] hat **kein wirklich stilles Intro** — ab
  `src ≈ 1,5 s` steht die Groove-/Bass-Figur (RMS ~0,17–0,20). Die im Beat-Sheet
  „ruhig geschnittenen" ersten ~9 s (Kneipe 1445 → 4817 → 1448 → 1449) liegen also
  auf laufendem Beat; „ruhig" meint hier nur den **Schnittrhythmus**, nicht die
  Musik. Ab dem Drop ziehen die Beat-Cuts an.
- `dur: 271.39` = ganze Datei; endet bei `tl 211,40 + 271,39 = 482,79 s` = Hard Cut 2.

### 2.3 Track C — Where Is My Mind (Aftermath / Outro)

```json
{
  "id": "music-03-wimm",
  "src": "music/07 Where Is My Mind_ (2007 Remaster).m4a",
  "tl_in": 482.79,
  "src_in": 17.0,
  "dur": 45.0,
  "gain_db": 0.0,
  "fade_in_s": 0.0,
  "fade_out_s": 4.0
}
```

- **ABRUPTER Cut** aus Galvanize in die Stille: Galvanize bricht bei 482,79 s hart ab,
  Where Is My Mind setzt **ohne** `fade_in` direkt ein.
- `src_in: 17.0` — steigt mitten in die getragene Strophe ein („man kennt das Lied").
  Bei `src 17,0 s` liegt ein Beat (17,009 s) und der Einsatz der Gesangslinie
  (RMS steigt von 0,04 auf 0,05–0,06) — sauberer, unauffälliger Einstiegspunkt.
- `dur: 45.0` → spielt `src 17,0 → 62,0 s`. Track ist 234,97 s lang, Reserve reichlich.
- `fade_out_s: 4.0` — lineare Rampe **523,79–527,79 s** (`src 58,0–62,0`). Musik ist
  bei **527,79 s vollständig aus**, die „Danke"-Karte (`JGA_OUTRO.png`, ab 527,79 s)
  und das Schlusschwarz stehen **in Stille**.

**Musik-Gesamtbild:** 0,0–211,40 Vivaldi · 211,40–482,79 Galvanize ·
482,79–527,79 Where Is My Mind (letzte 4 s Fade) · 527,79–533,79 **Stille**.

---

## 3. Die drei Musik-Übergänge — exakt

### 3.1 Übergang 1 — Vivaldi hoch, dann Hard Cut (0:00 / 3:31,40)

- **Einstieg:** `fade_in_s: 2.0` auf `music-01` unter dem Intro-Standbild. Nichts
  weiter zu synchronisieren — der Schnitt in Akt 1 folgt der Energiekurve, nicht
  umgekehrt.
- **Ausstieg:** kein Fade. Letztes Akt-1-Bild (`F9615661-…1429`) endet **exakt auf
  211,40 s**, im selben Frame beginnt Galvanize. `transition: cut`.

### 3.2 Übergang 2 — HARTER Cut Vivaldi → Galvanize + BEAT-DROP auf IMG_1451

Zwei getrennte Ereignisse:

**(a) Der Musik-Cut** liegt bei **211,40 s** (Vivaldi-Ende). Galvanize `src_in 0.0`.
Kein Crossfade.

**(b) Der Beat-Drop** soll auf dem Bild „Gläser werden vollgeschüttet" (`IMG_1451`)
sitzen. Vom Musik-Cut bis zum Drop liegen laut Beat-Sheet ~9 s ruhig geschnittene
Kneipenbilder (`IMG_1445` → `4817` → `IMG_1448` → `IMG_1449`).

Galvanize-Beat-Grid um `src 9 s` (Auszug):
`… 7,697 · 8,290 · 8,835 · 9,416 · 9,973 …`
Phrasen-/Downbeat-Raster (jeder 4. Beat): `… 7,697 · 8,835* · 9,973 …` bzw. um einen
Beat versetzt `… 6,513 · 8,835 · 11,157 …` — **`src 8,835 s` ist der belastbarste
Downbeat** nahe der Beat-Sheet-Vorgabe 3:40,5.

→ **Anweisung an `timeline-builder`:**
1. **Drop-Anker = Galvanize `src 8,835 s`** → Timeline **220,235 s (≈ 3:40,2)**.
2. Der **Bild-Cut auf `IMG_1451` muss exakt auf 220,235 s** liegen. Das heißt: die
   vier Vorlauf-Bilder `IMG_1445 + 4817 + IMG_1448 + IMG_1449` müssen zusammen
   **exakt 8,835 s** ergeben (Beat-Sheet-Richtwerte 2,5 + 2,0 + 2,0 + 2,5 = 9,0 s →
   0,165 s kürzen, am einfachsten `IMG_1449` 2,5 → 2,335 s, das „letzte Bild vor dem
   Drop").
3. Ab `IMG_1451` alle Cuts auf das Galvanize-Beat-Grid legen (Grid liegt im
   Analyse-Cache, Feld `beat_grid`, Werte sind Track-Zeit = Timeline-Zeit − 211,40).
4. **Alternative**, falls die 3:40,5 exakt gewünscht ist: Drop-Anker `src 9,416 s` →
   Timeline 220,816 s (≈ 3:40,8), Vorlauf-Block dann 9,416 s (`IMG_1449` 2,5 → 2,92 s).
   Musikalisch beide sauber; **empfohlen: 8,835 s** (tighter, klar auf dem Downbeat).

### 3.3 Übergang 3 — ABRUPTER Cut Galvanize → Where Is My Mind (8:02,79)

- Galvanize bricht **hart** bei **482,79 s** ab (kein `fade_out`).
- Where Is My Mind `src_in 17,0 s`, `tl_in 482,79 s`, **kein `fade_in`**.
- `fade_out_s: 4.0` am Schluss: Rampe **523,79–527,79 s**. Musik komplett aus
  **bevor** die „Danke"-Karte steht (Karte ab 527,79 s, in Stille).

---

## 4. O-Ton-Fenster + Ducking-Kurven

Umsetzung als eigene `AudioClip`-Einträge mit **`asset`** (nicht `src`), damit
`render.build_filtergraph` sie als Duck-Fenster für **alle** Musikspuren erkennt
(Duck-Logik greift nur bei `asset is not None and duck_music_db is not None`).
`duck_fade_s` = weiche Rampe am Anfang **und** Ende des Fensters (Attack = Release),
liegt außerhalb des O-Ton-Fensters — kein Knacken, kein Hartschalter.

**`duck_music_db` bewegt sich im Modell-Richtwert −10 bis −18 dB.** Gestaffelt nach
Wichtigkeit der O-Ton-Stelle; `original_audio_policy: accent` → die Musik bleibt
überall Leitspur, wird nur akzentweise zurückgenommen.

Die Timeline-Zeiten unten sind **aus den Beat-Sheet-Kapitel-TCs + Clip-Reihenfolge
abgeleitet (Näherung)**. `timeline-builder` muss jedes Fenster auf den **tatsächlich
platzierten Clip in `timeline.json` feinjustieren**, sobald dessen `tl_in` feststeht.

| # | Clip (`asset`) | Kapitel | Näherungs-Fenster (Timeline) | `gain_db` (O-Ton) | `duck_music_db` | `duck_fade_s` | Regel |
|---|---|---|---|---:|---:|---:|---|
| 1 | `IMG_1395` | A1.8 | **≈ 143,1–145,6 s** (nur die ersten ~2 s „da-da-da-da", + 0,4 s Release) | 0,0 | **−11** | 0,4 | nur der String am Anfang; danach Musik sofort wieder hoch, Rest des Clips leise mitlaufen |
| 2 | `IMG_1460` | B2 | **≈ 232,7–237,7 s** (ganzer 5-s-Ausschnitt) | 0,0 | **−14** | 0,3 | Michas Lachen — schneller Attack, Lachen ist punchy |
| 3 | `IMG_1613` | B8 | **≈ 350,1–364,1 s** (ganze 14 s) | 0,0 | **−13** | 0,5 | Szene zusammenhalten; das „Füßchen" bei ~11 s in den Clip (≈ 361,1 s) muss klar hörbar bleiben |
| 4 | `IMG_1637` | B10 | **≈ 421,7–436,7 s** (ganze 15 s) | +1,0 | **−17** | 0,6 | „wichtigste Sekunde des Films" — tiefstes Ducking; das Umdrehen liegt am Clip-Anfang, auf einen Galvanize-Beat legen |
| 5 | `IMG_1641` | B10 | **≈ 439,7–444,7 s** (5 s) | 0,0 | **−14** | 0,4 | Karaoke-Gesang |
| 6 | `IMG_4835` | B10 | **≈ 444,7–452,7 s** (8 s) | 0,0 | **−14** | 0,4 | Tequila-Shot; O-Ton = Anstoß/Ruf. `FX:` Farb-Pop (party-fx) |
| — | **`IMG_1653`** | B12 | ≈ 465,5–473,5 s | — | **KEIN Ducking** | — | **AUSNAHME (Christian explizit):** kein Duck-Clip anlegen, Galvanize läuft ungedämpft durch. Letzte laute Strecke vor dem Abbruch. |

**Kein Ducking / keine Duck-Clips** für `IMG_1621` und `IMG_1635` (B10) — die Musik
trägt, `original_audio_policy: accent`. Nur `FX:` Farb-Pop/Speedlines (party-fx).

Beispiel-Eintrag (Fenster 4, tiefstes Ducking):

```json
{
  "id": "oton-04-img1637",
  "asset": "<asset-id von IMG_1637, vom timeline-builder aufgelöst>",
  "type": "oton",
  "tl_in": 421.70,
  "dur": 15.0,
  "gain_db": 1.0,
  "duck_music_db": -17.0,
  "duck_fade_s": 0.6
}
```

**Fenster 1 (`IMG_1395`) ist ein Sonderfall:** der Clip ist 7 s lang, geduckt wird
nur der Anfang. Zwei saubere Wege:
- **empfohlen:** Duck-`AudioClip` mit `dur: 2.0` (nur der String), `duck_fade_s: 0.4`
  — Musik senkt sich für 2 s, kommt dann hoch, der Rest des Clips läuft mit voller
  Musik und leisem O-Ton darunter; oder
- den O-Ton als zwei `AudioClip`s splitten (0–2 s mit Duck, 2–7 s ohne
  `duck_music_db`, nur mit niedrigem `gain_db`).

---

## 5. Cast-Intro (B9) — SFX pro Namensstempel

**B9 ≈ 6:15,5–6:24,5 (375,5–384,5 s).** Neun Sonnenbrillen-Standbilder, je ein
Namensstempel (Bangers), Cut hart auf den Galvanize-Beat. Pro Stempel **ein kurzer
SFX-Einschuss** — kurzer Whoosh, der in einen Stempel-/Klick-Impact übergeht.

**Status: KEINE SFX-Dateien im Projekt** (`music/sfx/` existiert nicht). Der Build
läuft ohne SFX weiter — die neun `AudioClip`s sind **optional, nachreichbar**.

**Beschaffungs-Hinweis (an Orchestrator / Nutzer):**
- Ablage-Ordner anlegen: **`projects/michael-jga-2026/music/sfx/`**
- Zwei Dateien reichen (wiederverwendbar, für Micha ggf. eine dritte, größere):
  - `sfx-cast-whoosh.wav` — kurzer Transition-Whoosh (~0,3–0,5 s)
  - `sfx-cast-stamp.wav` — Stempel-/Rubber-Stamp-Thud oder Kamera-Shutter-Klick (~0,2 s)
  - optional `sfx-cast-stamp-micha.wav` — tiefer/größer für den Bräutigam
- Quellen mit sauberer, lizenzsicherer Nutzung: **Pixabay** (Content License, kein
  Attribution-Zwang) oder **Mixkit** (Mixkit Free License). Suchbegriffe:
  „whoosh transition", „stamp thud", „rubber stamp", „camera shutter click".
- Formatziel: WAV, 48 kHz, Stereo, normalisiert auf ca. −12 dBFS Peak.

**SFX-`AudioClip`s** (sobald Dateien da sind), `type: "sfx"`, je 9 Stück,
`tl_in` auf den jeweiligen Namens-Cut (~0,9 s Raster ab 375,5 s; Micha länger):

| # | Person | ~`tl_in` | SFX |
|---|---|---:|---|
| 1 | Witte | 375,5 | whoosh + stamp |
| 2 | Christoph | 376,4 | whoosh + stamp |
| 3 | Matti | 377,3 | whoosh + stamp |
| 4 | Bartosz | 378,2 | whoosh + stamp |
| 5 | Hagi | 379,1 | whoosh + stamp |
| 6 | Bernhard | 380,0 | whoosh + stamp |
| 7 | André | 380,9 | whoosh + stamp |
| 8 | Skuub | 381,8 | whoosh + stamp |
| 9 | **Micha** | 382,7 | whoosh + **stamp-micha** (größer), Stempel „Micha im Delirium" |

```json
{
  "id": "sfx-cast-01-witte",
  "src": "music/sfx/sfx-cast-whoosh.wav",
  "type": "sfx",
  "tl_in": 375.5,
  "src_in": 0.0,
  "dur": 0.5,
  "gain_db": -6.0
}
```

`timeline-builder`: die SFX-Zeiten an die **realen** Cast-Intro-Cuts aus
`timeline.json` binden (Galvanize-Beat-Grid), nicht an das 0,9-s-Näherungsraster.

---

## 6. Loudness / EBU R128

- **Zielwert Integrated Loudness: −16 LUFS** (EBU R128 / Web-/Social-Delivery — der
  Film wird geteilt/hochgeladen, nicht als Broadcast-Master mit −23 LUFS gemastert).
- **True Peak: ≤ −1,0 dBTP** (Limiter am Master).
- **LRA: ~6–9 LU** — Vivaldi/Aftermath dürfen deutlich leiser sitzen als der
  Akt-2-Block, das ist gewollt (`build_drop_calm`).
- Musikbett-Richtwert Short-Term: Akt 1 ~ −20…−18 LUFS-S, Akt 2 ~ −15…−13 LUFS-S,
  Aftermath ~ −20 LUFS-S. In den O-Ton-Fenstern soll der O-Ton-Peak nach dem Ducking
  **hörbar über** dem Musikbett liegen.
- Messung/Korrektur beim QC-Preview-Hördurchgang (nicht vorab geraten — die
  tatsächliche Lautheit hängt an den finalen Clips).

---

## 7. Zusammenfassung für `timeline-builder`

1. **Drei Musik-`AudioClip`s** aus §2.1–2.3 direkt übernehmen. Anker: Vivaldi-Ende /
   Hard Cut 1 = **211,40 s**, Galvanize-Ende / Hard Cut 2 = **482,79 s**,
   Musik-Ende (nach 4 s Fade) = **527,79 s**, Filmende = **533,79 s**. Die −0,10 s /
   −0,11 s im jeweils letzten Akt-Bild abfangen (§1).
2. **Beat-Drop:** Bild-Cut auf `IMG_1451` **exakt auf 220,235 s** = Galvanize
   `src 8,835 s` (Downbeat). Vorlauf-Block `1445+4817+1448+1449` auf **8,835 s**
   summieren. Ab da Cuts auf `beat_grid` aus dem Analyse-Cache (Track-Zeit =
   Timeline-Zeit − 211,40). Alternative `src 9,416 s` / 220,816 s in §3.2.
3. **Sechs O-Ton-Duck-`AudioClip`s** aus §4 (`asset` + `duck_music_db` +
   `duck_fade_s`), Zeitfenster auf die real platzierten Clips feinjustieren.
   `IMG_1637` bekommt das tiefste Ducking (−17 dB).
4. **`IMG_1653` (Taxi):** **kein** Duck-Clip — Musik läuft ungedämpft durch.
   `IMG_1621` / `IMG_1635`: ebenfalls kein Ducking.
5. **Neun Cast-Intro-SFX-`AudioClip`s** (`type: "sfx"`) sind **optional/nachreichbar**
   — Build läuft ohne. Dateien nach `music/sfx/` (§5). Zeiten an die realen
   Cast-Cuts binden.
6. **Loudness-Ziel −16 LUFS / −1 dBTP** (§6) an den `render-engineer` weiterreichen.

---

## 8. Offener Punkt — Musik-Lizenz-Nachweis (Plan §11)

**An den Orchestrator, explizit als offener Punkt markiert:**

Alle drei Tracks sind **kommerziell veröffentlichte, urheberrechtlich geschützte
Aufnahmen** ohne erkennbaren Freigabe-/Lizenzvermerk für Videoverwendung:

| Track | Rechte-Lage (soweit erkennbar) |
|---|---|
| „Der Winter" I. Allegro non molto | Komposition gemeinfrei (Vivaldi), **aber die Einspielung/Aufnahme ist leistungsschutzrechtlich geschützt** — Label-/Interpreten-Rechte ungeklärt. |
| Galvanize (feat. Q-Tip) [Edit] | The Chemical Brothers feat. Q-Tip — Label- & Verlagsrechte, **keine Videolizenz**. |
| Where Is My Mind (2007 Remaster) | Pixies — Label- & Verlagsrechte, **keine Videolizenz**. |

**Status: UNGEKLÄRT.** Für eine **private Vorführung** im JGA-Kreis unkritisch. Für
**jede Veröffentlichung / jeden Upload** (auch „privat" auf YouTube/Vimeo, WhatsApp-
Statusverteiler, Mini-Site `micha-jga.skubus.de`) muss die Lizenzfrage **vor dem
Final-Render / vor der Freigabe** geklärt werden — sonst drohen Sperre/Takedown.
Diese Entscheidung liegt beim Nutzer, nicht bei diesem Agenten.
