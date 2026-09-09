# Audio-Plan — `michael-jga-2026` / `JGA` — **RUNDE 2**

Löst die Runde-1-Fassung ab (Vivaldi + Galvanize + Ducking). Grundlage:
`editorial-notes-round2.md` §0. Alle Track-Werte **gemessen** über
`frameforge.audio.analyze_and_cache` (librosa, Cache-Schlüssel = `sha256(Datei)`),
frisch gerechnet 2026-09-09.

| Track | Datei (`music/`) | Analyse-Cache (`music/analysis/`) | gemessen |
|---|---|---|---|
| **Champions League Theme** | `01 Champions League Theme (Champions League Theme).m4a` | `38963d3e…d3e.json` | **181,45 s**, 126,0 BPM, 351 Beats, Beat 1 bei 1,997 s |
| **Miserlou (loop-196)** | `01 Miserlou (loop-196).m4a` | `4e49b0fe…d44.json` | **195,93 s**, 117,5 BPM, 378 Beats, Beat 1 bei 0,104 s |
| **Where Is My Mind (2007 Remaster)** | `07 Where Is My Mind_ (2007 Remaster).m4a` | `beb194c5…011.json` | **234,97 s**, 161,5 BPM (unverändert) |

Miserlou-Loop: 136,1 s → 195,93 s, Phrasenblock 43,2→103,2 s dupliziert, Nahtstellen bei
**~103,2 s** und **~163,2 s** (Track-Zeit). Details: `audio-prep.py` / PROGRESS T4.

---

## 1. Musik-Gesamtbild (hart)

```
0,00              181,45                       377,38            422,38   ~428,4
  |  CL Theme       |        Miserlou (loop)      |   Where Is My Mind |  Stille |
  | (fade_in 2,0)   |   (harter Cut beidseitig)   | src_in 17,0 · 45 s |         |
                                                     (fade_out 4,0)
```

- **Filmlänge ~428 s ≈ 7:08.** `target_duration_s` in `brief.yaml` von `timeline-builder`
  in T7 auf die real gebaute Länge nachziehen.
- **Kein Ducking, nirgends** (§0.3 der Regie). Keine Duck-`AudioClip`s. Die vier O-Ton-Clips
  laufen als leise `type: "oton"`-Clips **unter ungedämpfter Musik**.

### Die drei Anker
| Anker | Timeline-Zeit | Regel |
|---|---:|---|
| **A — CL Theme kommt hoch** | 0,00 | `fade_in_s: 2.0` unter `JGA_INTRO.png`. Track hat ~2 s leisen Vorlauf, Beat 1 bei 1,997 s — die Rampe ist vorher durch. |
| **B — HARTER Cut CL Theme → Miserlou** | **181,45** | CL Theme endet ohne Ausblendung auf dem Pommes-Schwenk. Miserlou `src_in 0.0`, `tl_in 181.45`. **Kein Crossfade.** Der Bild-Cut auf „3 Personen Daumen hoch" liegt auf Miserlous erstem Downbeat nach dem Einsatz (Beat-Grid `0.104, 0.511, 1.033, 1.544, 2.078, …` → Downbeat-Kandidat **src ≈ 2,078 s** → Timeline **≈ 183,53 s**). Der Pommes-Schwenk füllt 181,45–183,53 s. |
| **C — HARTER Cut Miserlou → Where Is My Mind** | **377,38** | Miserlou endet hart (`= 181,45 + 195,93`). Where Is My Mind `src_in 17.0`, `tl_in 377.38`, **kein `fade_in`**. Der Gurken-Schluss von Akt 2 sitzt in den letzten ~4 s von Miserlou; danach abrupt Stille → Schwarzblende, aus der Mitte der Blende setzt WIMM ein. |

---

## 2. AudioClip-Definitionen für `tracks.audio`

Feldnamen nach `frameforge.timeline.AudioClip`. Pfade relativ zum Projekt-Root.

### 2.1 Track A — Champions League Theme (Intro + AKT 1)
```json
{
  "id": "music-01-cltheme",
  "src": "music/01 Champions League Theme (Champions League Theme).m4a",
  "type": "music",
  "tl_in": 0.0,
  "src_in": 0.0,
  "dur": 181.45,
  "gain_db": 0.0,
  "fade_in_s": 2.0,
  "fade_out_s": 0.0
}
```
- `fade_out_s: 0.0` — endet abrupt auf 181,45 s → harter Schnitt. **QC-Preview:** letzte
  ~0,3 s auf einen Hallschwanz abhören; falls hörbar, `dur` auf ~181,1 ziehen und das letzte
  Akt-1-Bild entsprechend länger halten, Cut bleibt bei 181,45 s.

### 2.2 Track B — Miserlou (loop-196) (AKT 2)
```json
{
  "id": "music-02-miserlou",
  "src": "music/01 Miserlou (loop-196).m4a",
  "type": "music",
  "tl_in": 181.45,
  "src_in": 0.0,
  "dur": 195.93,
  "gain_db": 0.0,
  "fade_in_s": 0.0,
  "fade_out_s": 0.0
}
```
- **Harter Cut an beiden Enden** (Christian). Loop-Naht liegt bei `src` ~103,2 s / ~163,2 s
  = Timeline **~284,7 s / ~344,7 s** — dort **keinen** auffälligen Bild-Hard-Cut mit Stille
  setzen, ein normaler Beat-Cut überdeckt die Naht restlos.
- Endet Timeline 377,38 s.

### 2.3 Track C — Where Is My Mind (Aftermath / Outro)
```json
{
  "id": "music-03-wimm",
  "src": "music/07 Where Is My Mind_ (2007 Remaster).m4a",
  "type": "music",
  "tl_in": 377.38,
  "src_in": 17.0,
  "dur": 45.0,
  "gain_db": 0.0,
  "fade_in_s": 0.0,
  "fade_out_s": 4.0
}
```
- Unverändert zu Runde 1: steigt mitten in die getragene Strophe ein (Beat bei src 17,009 s).
- `fade_out_s: 4.0` → Rampe **418,38–422,38 s**. Musik komplett aus **bevor** `JGA_OUTRO.png`
  steht; Danke-Karte + Schlusschwarz in **Stille**.

---

## 3. O-Ton-Fenster — OHNE Ducking

Vier O-Ton-Clips, als `type: "oton"` mit **negativem `gain_db`** (leise unter der Musik),
**kein `duck_music_db`**, **kein `duck_fade_s`**. Die Musik bleibt an jeder Stelle voll.
Wenn ein O-Ton am Anfang/Ende hörbar rein-/rauskommen soll: kurzer `fade_in_s`/`fade_out_s`
am O-Ton-Clip selbst (0,2–0,4 s), nicht an der Musik.

| # | Clip (`asset`) | Kapitel | Fenster (Timeline, in T7 feinjustieren) | `gain_db` | Zweck |
|---|---|---|---|---:|---|
| 1 | `IMG_1460` | Delirium | ganzer genutzter Ausschnitt | **−12** | Michas „wahnsinniges Lachen" — punchy, kurz oben lassen |
| 2 | `IMG_1613` | Karaoke | ab ~10 s in den Clip, ganze Szene | **−14** | Karaoke-Reden/Gesang; das „Füßchen" bei ~21 s muss hörbar bleiben |
| 3 | `IMG_1637` | Weiterziehen | Hauptstelle „dreht sich um" (2:22–2:37 im Clip) | **−12** | wichtigste O-Ton-Sekunde; auf einen Miserlou-Beat legen |
| 4 | `IMG_4835` | Karaoke | ab ~8 s, Tequila-Shot bis Ende | **−13** | Anstoß/Ruf |

- **IMG_1395** (Schoko-Praliniere): Runde 1 wollte hier ein Duck-Fenster für den
  „da-da-da"-String. **Entfällt** — kein Ducking. Wenn der String hörbar sein soll, O-Ton-Clip
  mit `gain_db: -16` über die ersten ~2 s, sonst Clip ganz ohne O-Ton.
- **IMG_1653** (Taxi-POV), **IMG_1621**, **IMG_1635**: kein O-Ton-Clip, nur Musik (wie
  Runde 1, aber jetzt gilt das ohnehin für ganz Akt 2).

---

## 4. Cast-Intro-SFX (B-Sektion Red-Bar) — 9 Personen

**SFX-Dateien liegen bereit** (`music/sfx/`, siehe `editorial-notes-round2.md` §3):
`sfx-cast-whoosh.wav` (0,42 s), `sfx-cast-stamp.wav` (0,40 s), `sfx-cast-stamp-micha.wav`
(0,55 s). Alle 48 kHz Stereo.

Pro Person **zwei** `AudioClip`s, `type: "sfx"`, überlappend:
- Whoosh: `tl_in` = Cast-Cut − 0,18 s, `gain_db: -6`
- Stamp: `tl_in` = Cast-Cut (exakt auf dem Bild-Cut / Miserlou-Beat), `gain_db: 0`
- Person 9 (**Micha**): Stamp = `sfx-cast-stamp-micha.wav`, `gain_db: -1`

`timeline-builder` bindet die 9 Cut-Zeiten an die **realen** Cast-Intro-Bild-Cuts aus
`timeline.json` (auf dem Miserlou-Beat-Grid, Track-Zeit = Timeline-Zeit − 181,45). Reihenfolge
Witte · Christoph · Matti · Bartosz · Hagi · Bernhard · André · Skuub · **Micha**.

Beispiel:
```json
{ "id": "sfx-cast-07-andre-whoosh", "src": "music/sfx/sfx-cast-whoosh.wav",
  "type": "sfx", "tl_in": 0.0, "src_in": 0.0, "dur": 0.42, "gain_db": -6.0 }
{ "id": "sfx-cast-07-andre-stamp",  "src": "music/sfx/sfx-cast-stamp.wav",
  "type": "sfx", "tl_in": 0.0, "src_in": 0.0, "dur": 0.40, "gain_db":  0.0 }
```

---

## 5. Loudness / EBU R128

- **Integrated Loudness Ziel: −16 LUFS** (Web-/Social-Delivery).
- **True Peak ≤ −1,0 dBTP** (Limiter am Master). Die Miserlou-Loop-Datei hat Roh-Peak
  ~−0,04 dBFS → im Render ~−3…−4 dB Vorabsenkung, damit der Limiter Luft hat.
- **LRA ~6–9 LU** — CL-Theme/Aftermath dürfen leiser sitzen als der Miserlou-Block (gewollt,
  `build_drop_calm`).
- Musikbett Short-Term: Akt 1 ~ −19…−17 LUFS-S, Akt 2 ~ −15…−13 LUFS-S, Aftermath ~ −20 LUFS-S.
- Messung/Korrektur beim QC-Preview-Hördurchgang, nicht vorab geraten.

---

## 6. Zusammenfassung für `timeline-builder`

1. **Drei Musik-`AudioClip`s** aus §2 direkt übernehmen. Anker: CL-Theme-Ende **181,45 s**,
   Miserlou-Ende **377,38 s**, Musik-Ende (nach 4 s Fade) **422,38 s**, Filmende **~428 s**.
2. **Bild-Cut auf „3 Personen Daumen hoch"** auf Miserlou-Downbeat ~`src 2,078 s` = Timeline
   **~183,53 s**. Pommes-Schwenk füllt 181,45–183,53 s. Ab da Cuts aufs Miserlou-Beat-Grid
   (Track-Zeit = Timeline-Zeit − 181,45).
3. **Loop-Nähte** bei Timeline ~284,7 s / ~344,7 s — dort normale Beat-Cuts drüberlegen, keine
   Stille/Hard-Break.
4. **Vier O-Ton-`oton`-Clips** aus §3, **negatives `gain_db`, kein Ducking-Feld**.
5. **18 SFX-`AudioClip`s** (9× Whoosh + 9× Stamp) aus §4, an die realen Cast-Cuts gebunden.
6. **Loudness-Ziel −16 LUFS / −1 dBTP** an `render-engineer` weiterreichen.

---

## 7. Musik-Lizenz — weiterhin OFFEN, aber unkritisch (Christian)

Christian 2026-09-09: „Musiklizenz aller drei Tracks ungeklärt. Ist völlig egal, ist ein
internes Projekt. Wir brauchen was auf dem Impressum, auf der Website nicht erklären."

| Track | Rechte-Lage |
|---|---|
| Champions League Theme (Tony Britten, UEFA) | geschützte Komposition + Aufnahme, keine Videolizenz. |
| Miserlou (Dick Dale 1962 / „Pulp Fiction") | geschützte Aufnahme, keine Videolizenz. |
| Where Is My Mind (Pixies, 2007 Remaster) | Label-/Verlagsrechte, keine Videolizenz. |

**Entscheidung Christian:** interne JGA-Vorführung, kein öffentlicher Upload. Auf der Website
kein Musikhinweis. Ein knapper Impressum-Vermerk genügt. Diese Einstufung liegt beim Nutzer,
nicht bei diesem Agenten — vor einem etwaigen öffentlichen Upload neu bewerten.
