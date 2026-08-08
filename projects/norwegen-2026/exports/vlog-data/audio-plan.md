# Audio-Plan — `norwegen-2026` / `vlog-data`

Ergänzung zu `beatsheet.md` Abschnitt 2 ("Musikplan"). Alle Werte hier sind **gemessen**, nicht
geraten — Quelle: `frameforge.audio.analyze_track` (librosa BPM/Beat-Grid/RMS-Energiekurve),
Cache unter `music/analysis/*.json`. Für alle drei Pflicht-Tracks lag die Analyse bereits
gecacht vor (Hash = `sha256(Datei)`, siehe `frameforge.ingest.hash_file`); es musste nichts neu
berechnet werden:

| Track | Datei | Analyse-Cache |
|---|---|---|
| Cuatro Vientos | `music/Originals/Danit/Cuatro Vientos - Single/01 Cuatro Vientos.m4a` | `music/analysis/5f3405c41e0bec66e5a0a18f4175c98880b389eddc1a23d7bbe3f7edaa4d6810.json` |
| Naturaleza (Mose Edit) | `music/Originals/Mose & Danit/Naturaleza (Mose Edit) - Single/01 Naturaleza (Mose Edit).m4a` | `music/analysis/b57873d01a9e90600cd9ddc44f84e06d98a35f6a2ce6f9e49ccc6486353ec40a.json` |
| Aguila de Oro (Ecstatic Mix) | `music/Originals/Little Whale, Sariel Orenda & UAK/Aguila de Oro (Ecstatic Mix) - Single/01 Aguila de Oro (Ecstatic Mix).m4a` | `music/analysis/081be7f3fd22ce9a0a35dbd638698691ff13047acb719a4b4284f8574a6f83b3.json` |

Gemessene Werte:

| Track | BPM (gemessen) | Dauer (gemessen) | 1. stabiler Beat |
|---|---:|---:|---:|
| Cuatro Vientos | 147,66 (Beat-Sheet nannte 147,7 — bestätigt) | 446,86 s | **43,572 s** (davor kein stabiles Beat-Grid, siehe unten) |
| Naturaleza (Mose Edit) | 68,91 (Beat-Sheet nannte 68,9 — bestätigt) | 445,22 s | 36,537 s |
| Aguila de Oro (Ecstatic Mix) | **82,03** (Beat-Sheet: bewusst nicht geraten) | **374,63 s** | 0,743 s |

---

## 1. Puls-Einsatz Cuatro Vientos → Cold-Open-Länge (K0)

`librosa.beat.beat_track` findet **kein stabiles Beat-Grid vor 43,572 s** — die RMS-Energiekurve
bestätigt das: bis ~24 s durchgehend niedrig (< 0,02), ab ~24,5 s ein erster Anstieg (Crescendo,
0,03–0,05), aber erst **ab ~36 s** ein deutlicher Sprung (0,11 bei t=36,0) und ab **43–45 s**
dauerhaft hohes, rhythmisch trägendes Energieniveau — genau der Punkt, an dem der Beat-Tracker
erstmals eine stabile Taktfolge verankert. Das ist der gemessene "Puls-Einsatz".

**Gemessener Punkt: 43,572 s → liegt außerhalb der erlaubten Klemmung 25–40 s.**

Nach Beat-Sheet-Regel (Abschnitt 2, "gewinnt die Musik"): Cold-Open-Länge = gemessener Punkt,
**geklemmt auf das obere Ende, 40,0 s**. Differenz zur ursprünglichen Planung (30 s): **+10,0 s**,
vollständig in K2 auszugleichen, alle späteren Zeiten unverändert.

**Resultierende Verschiebung K0–K2** (nur diese drei Kapitel betroffen, K3 startet weiterhin
exakt bei 132 s / 02:12):

| Kapitel | Alt | Neu | Δ |
|---|---|---|---|
| K0 Cold Open | 00:00–00:30 (30 s) | **00:00–00:40 (40 s)** | +10 s |
| K0→K1 Übergang (`slow_dissolve` 2,0 s) | 00:28–00:30 | **00:38–00:40** | verschoben, Dauer gleich |
| K1 Titel & Infokarte | 00:30–00:52 (22 s) | **00:40–01:02 (22 s)** | verschoben, Dauer gleich |
| HUD-Einblendung | 00:52 | **01:02** | verschoben |
| K2 Aufbruch → Flensburg | 00:52–02:12 (80 s) | **01:02–02:12 (70 s)** | −10 s (Puffer wie im Beat-Sheet vorgesehen) |
| K3 Die Überfahrt | 02:12–03:37 | **unverändert** | 0 |

→ **An `timeline-builder`/`story-architect`:** K2 muss auf 70 s statt 80 s gebaut werden (9 statt
10 Beats bei ~7,8 s Rhythmus, oder 10 Beats etwas kürzer — Materiallage in K2 ist "reichlich",
verträgt das). Alle Kapitelgrenzen ab K3 bleiben exakt wie im Beat-Sheet.

Die Musik-Clip-Definition von Track A selbst ist davon **nicht** betroffen — Cuatro Vientos läuft
durchgehend ab `src_in 0.0`, das Video-Tempo (K0/K1 Schnittfrequenz) folgt der Energiekurve, nicht
umgekehrt.

---

## 2. AudioClip-Definitionen für `tracks.audio`

Feldnamen nach `frameforge.timeline.AudioClip` (`id`, `src`, `tl_in`, `src_in`, `dur`, `gain_db`,
`fade_in_s`, `fade_out_s`, `duck_music_db`).

### 2.1 Track A — Cuatro Vientos

```json
{
  "id": "music-01",
  "src": "music/Originals/Danit/Cuatro Vientos - Single/01 Cuatro Vientos.m4a",
  "tl_in": 0.0,
  "src_in": 0.0,
  "dur": 395.0,
  "gain_db": 0.0,
  "fade_in_s": 3.0,
  "fade_out_s": 10.0
}
```

- `fade_in_s: 3.0` deckungsgleich mit `transition_in: black` / Bild-`fade_in_s: 3` — Musik und
  Bild blenden gemeinsam aus Schwarz.
- `fade_out_s: 10.0` = Crossfade A→B, 385,0–395,0 s. Kapitelgrenze **395 s liegt fest** (Fixpunkt)
  und liegt bereits sehr nah an einem echten Beat des Tracks (394,797 s / 395,204 s,
  < 0,21 s Abweichung) — keine Korrektur nötig, die im Beat-Sheet vorgegebene Sekunde ist
  musikalisch bereits sauber.
- Von den 446,86 s verfügbarer Spielzeit werden 395 s genutzt (51,86 s Überschuss, nicht
  gebraucht, kein Problem).

### 2.2 Track B — Naturaleza (Mose Edit)

```json
{
  "id": "music-02",
  "src": "music/Originals/Mose & Danit/Naturaleza (Mose Edit) - Single/01 Naturaleza (Mose Edit).m4a",
  "tl_in": 385.0,
  "src_in": 0.0,
  "dur": 345.0,
  "gain_db": 0.0,
  "fade_in_s": 10.0,
  "fade_out_s": 10.0
}
```

- `fade_in_s: 10.0` = Crossfade A→B (385–395 s), spiegelt Track A's `fade_out_s`.
- `dur: 345.0` → Track spielt von `src 0` bis `src 345`. Nächster echter Beat dort: **345,234 s**
  (0,234 s Abweichung von der geplanten Kapitelgrenze 730 s) — ebenfalls sauber, keine Korrektur
  nötig.
- `fade_out_s: 10.0` = 720–730 s, der **kritische zweite Wechsel** (siehe 2.3). Von den 445,22 s
  verfügbarer Spielzeit werden 345 s genutzt (100,22 s Überschuss, nicht gebraucht).
- Bei `src`-Position 335–345 s (= Zeitfenster 720–730 s auf der Timeline) ist Naturaleza laut
  Energiekurve noch **voll in Fahrt** (RMS 0,4–0,5, keine natürliche Beruhigung) — der
  "Rückzug hinter das Bild" aus dem Beat-Sheet ist **kein Effekt des Materials**, sondern muss
  über den Gain-Fade selbst erzeugt werden. `fade_out_s: 10.0` mit linearer Rampe (so wie
  `render.build_filtergraph` `afade` aktuell umsetzt) leistet das ausreichend; ein zweistufiger
  Rückzug (schneller runter bis 727 s, dann fast stumm bis 730 s) wäre musikalisch etwas
  präziser, ist mit dem aktuellen Render-Filtergraph (ein `afade`, keine Mehrpunkt-Kurve) aber
  nicht ohne Weiteres abbildbar — für diesen Export reicht die lineare 10-s-Rampe.

### 2.3 Der zweite Wechsel — Naturaleza → Aguila de Oro, 720–730 s

Bild- und Audioseite laufen hier **unterschiedlich**, wie im Beat-Sheet beschrieben:

- **Naturaleza fährt zurück:** `fade_out_s: 10.0` auf Clip `music-02`, 720,0–730,0 s.
- **Aguila de Oro setzt hart ein**, kein Crossfade, kein `fade_in_s` — der erste volle Downbeat
  (gemessen bei **0,743 s** im Track) soll exakt auf den Schnitt Tunnelausfahrt (730 s) fallen.
  Deshalb `src_in: 0.743` (die 0,743 s Vor-Silence/Anlauf werden abgeschnitten, nicht mitgespielt)
  statt `src_in: 0.0`.

Das ist **kein** 10-s-Doppel-Layer wie beim ersten Wechsel — genau der vom Nutzer geforderte
"kritische, saubere" Übergang: Musik A tritt zurück, Bild macht den Schnitt, Musik B setzt hart
und exakt auf dem Beat ein.

### 2.4 Track C — Aguila de Oro (Ecstatic Mix) — **siehe Warnung Abschnitt 3**

```json
{
  "id": "music-03",
  "src": "music/Originals/Little Whale, Sariel Orenda & UAK/Aguila de Oro (Ecstatic Mix) - Single/01 Aguila de Oro (Ecstatic Mix).m4a",
  "tl_in": 730.0,
  "src_in": 0.743,
  "dur": 373.887,
  "gain_db": 0.0,
  "fade_in_s": 0.0,
  "fade_out_s": 10.0
}
```

Mit diesen Werten **endet der hörbare Track bei 730,0 + 373,887 = 1103,887 s (18:23,9)** — siehe
Abschnitt 3, das ist der eigentliche Befund dieser Analyse und ein offener Punkt, kein
Implementierungsdetail.

`fade_out_s: 10.0` hier ist ein **Platzhalter für das natürliche Ende des Tracks**, nicht die vom
Beat-Sheet gewünschte 12–14-s-Ausklangrampe kurz vor 1200 s — die kann mit dem gemessenen Material
nicht gebaut werden (der Track ist an der Stelle längst zu Ende). Details und Optionen in
Abschnitt 3.

---

## 3. OFFENER PUNKT (blockierend) — Aguila de Oro ist zu kurz für Abschnitt C

**Befund:** Abschnitt C braucht laut Beat-Sheet 480 s Nettospielzeit (720–1200 s). Die
tatsächliche, gemessene Dauer von "Aguila de Oro (Ecstatic Mix)" ist **374,63 s** — ein
**Fehlbetrag von 105,37 s (≈ 22 % des Abschnitts)**. Zum Vergleich: Track A hatte 51,86 s
Überschuss, Track B 100,22 s Überschuss — nur Track C reicht nicht.

Das ist kein Rundungsfehler, sondern eine reale Lücke: **Ohne Eingriff fehlt Musik für die
komplette zweite Hälfte von K12 sowie für K13, K14 und ganz K15** — also für "Nachhall",
"Valdresflye", "Uvdal am Fluss" und den gesamten Ausklang inkl. Schlussbild "Ankunft zuhause".
Genau die Kapitel, die laut Beat-Sheet den *ruhigen, aber musikalisch getragenen* Abschluss des
Films bilden sollen (`music_energy_curve: gradual_build` endet nicht abrupt in der Stille,
sondern *fallend*). Die Warnung an den `render-engineer` im Beat-Sheet ("Track im Bereich
1150–1200 s prüfen, ob er von selbst zurücknimmt, sonst `fade_out_s` auf 12–14 s") geht von einem
Track aus, der bis dorthin überhaupt noch spielt — das ist mit den gemessenen 374,63 s **nicht
der Fall**, der Track ist ab ~1103,9 s vollständig zu Ende.

**Ausdrücklich nicht getan, wie im Auftrag verlangt:** kein Loop, kein Timestretch, keine
geratene Dauer.

**Zusatzbefund fürs Lizenz-Thema (Plan §11):** Die ID3/Metadaten aller drei Originaltracks tragen
nur `℗`-Copyright-Vermerke der jeweiligen Label (Danit / Mose Music / Resueño), **keinerlei
Lizenz- oder Freigabevermerk für Videoverwendung**. Für alle drei — nicht nur für Aguila de Oro —
ist der Lizenzstatus für die Verwendung in einem (ggf. veröffentlichten) Video **ungeklärt**. Das
ist ein eigener offener Punkt, unabhängig von der Längen-Frage, siehe auch Abschnitt 5.

**Drei Optionen, keine davon einseitig von mir entschieden:**

1. **Längere Version besorgen.** 374,63 s ist für einen "Ecstatic Mix" (Genre: Ecstatic
   Dance/Psy-World, typischerweise 6–9 Min.) auffällig kurz — die vorliegende Datei wirkt wie ein
   Radio-/Single-Edit. Lohnt sich zu prüfen, ob Little Whale/Sariel Orenda/UAK bzw. das Label
   Resueño eine Extended-/Full-Version veröffentlicht haben. Löst Längen- **und**
   Lizenzfrage in einem Schritt, wenn die Quelle geklärt ist.
2. **Zweiten Schlusstrack ergänzen (D-Abschnitt statt drei Pflicht-Tracks).** Bricht die im
   Beat-Sheet festgelegte Form "A–B–C" — nur mit Rücksprache Nutzer/`story-architect`, da das eine
   dramaturgische Entscheidung ist, keine audiotechnische.
3. **KI-generierte instrumentale Verlängerung.** Passender Prompt liegt vorbereitet in
   `design/prompts.md` (Abschnitt Musik) — Zielrichtung: Track im Charakter/Tempo von Aguila de
   Oro (BPM ≈ 82, ecstatic/aufsteigend, dann ausklingend), Länge ~110 s als eigenständiges
   Anschluss-/Ausklangstück (kein Versuch, den Originaltrack zu imitieren oder zu verlängern,
   sondern ein neuer, eigenständig lizenzierbarer Track für exakt diese Lücke).

**Bis zur Entscheidung** ist Abschnitt 2.4 die belastbare, ehrliche Fassung: Track C spielt genau
so lange, wie er wirklich ist (730,0–1103,887 s), danach **keine Musik** in der `timeline.json`,
klar als Lücke sichtbar statt stillschweigend überspielt. `timeline-builder` sollte diese Lücke
**nicht** eigenmächtig schließen (loopen/stretchen wäre gegen den expliziten Auftrag).

---

## 4. Originalton / Ambience-Fenster (K3, K7, K10, K14)

`original_audio_policy: ambience_only` — keine Sprache, keine Rotorengeräusche. Vier Fenster laut
Beat-Sheet Abschnitt 2, hier mit Ziel-Zeitfenstern (aus Kapitel-Rhythmus abgeleitet — **Näherung**,
der `timeline-builder` muss sie auf den tatsächlich gewählten Clip feinjustieren, sobald der Clip
feststeht):

| Kapitel | Atmo | Ziel-Zeitfenster (Timeline) | Beat-Position im Kapitel |
|---|---|---|---|
| K3 — Deck Color Line, Wind | Wind + Wasser | **≈ 170,6–178,4 s** (~7,7 s) | mittig, Beat 6/11 (Oskar-Beat) |
| K7 — Flåmsbana | Wasserrauschen | **≈ 579,1–586,3 s** (~7,2 s), Kandidatenfenster gesamt 564,7–600,6 s (Beats 10–14) | Mitte des Flåmsbana-Blocks |
| K10 — Storsæterfossen | Wasser + Schritte auf Metall | **≈ 864,0–881,0 s** (~17 s Block, Beats 7–9), Atmo real ~1 Beat davon | 3-Beat-Block "Weg hinter dem Wasserfall" |
| K14 — Kinder am Kiesufer | Wasser + entferntes Kinderlachen | **≈ 1053,0–1059,0 s** (~6,0 s, korrigiert Rev. 2: Beat-Sheet-Retiming auf 1103,887 s Gesamtlänge, altes Fenster lag hinter dem neuen Filmende) | Beat 2 |

Alle vier als eigene `AudioClip`-Einträge mit `asset` (nicht `src`) und `duck_music_db`, damit
`render.build_filtergraph` sie korrekt als Duck-Fenster für **alle** Musikspuren erkennt
(siehe `frameforge/render.py` — Duck-Logik greift nur bei `audio.asset is not None and
audio.duck_music_db is not None`):

```json
{
  "id": "atmo-k3-wind-deck",
  "asset": "<asset-id, vom timeline-builder aus dem K3-Kernbeat aufgelöst>",
  "tl_in": 170.6,
  "dur": 7.7,
  "gain_db": -18.0,
  "duck_music_db": -12.0
}
```

Analog für `atmo-k7-flaamsbana`, `atmo-k10-storsaeterfossen`, `atmo-k14-kiesufer` mit den
jeweiligen Zeiten aus der Tabelle.

- **`duck_music_db: -12.0`** für alle vier — Richtwert-Mitte des erlaubten Bereichs (−10 bis
  −18 dB). Kein Sprach-Ducking nötig (`original_audio_policy: ambience_only`, keine
  Sprachverständlichkeit gefordert), daher reicht ein moderater Wert: die Musik bleibt hörbar
  Leitspur, tritt aber für den Atmo-Teppich spürbar zurück.
- **`gain_db: -18.0`** am Atmo-Clip selbst ist eine Zielgröße für "leiser Teppich, ca. −24 LUFS"
  aus dem Beat-Sheet — grobe Setzung, keine gemessene Lautheit (dafür müsste der tatsächlich
  gewählte Clip vorliegen). Beim QC-Preview-Hördurchgang nachjustieren.
- **Kein Fade auf den Duck-Fenstern selbst** — `render.build_filtergraph` setzt aktuell ein
  hartes `enable='between(...)'`-Fenster ohne Rampe (die weichere `duck_curve()`-Funktion aus
  `frameforge/audio.py` ist laut Codekommentar noch nicht verdrahtet, siehe `PROGRESS.md` M2.1).
  Für vier kurze, unauffällige Ambience-Fenster ist das akzeptabel; bei hörbarem Sprung im
  QC-Preview auf kürzere `dur` mit größerem stillen Rand vor/nach dem eigentlichen Motiv
  ausweichen, nicht die Render-Logik ad hoc ändern.
- Überall sonst im Film: Musik allein, kein O-Ton.

---

## 5. Fade-in/Fade-out Filmanfang/-ende

- **Filmanfang:** `fade_in_s: 3.0` auf `music-01` (siehe 2.1), synchron mit Bild-`transition_in:
  black`.
- **Filmende (19:57–20:00, `transition_out: black`):** siehe Abschnitt 3 — mit dem gemessenen
  Material spielt an dieser Stelle **keine Musik mehr** (Track C endet bei ~18:23,9). Die im
  Beat-Sheet vorgesehene 12–14-s-Musik-Ausklangrampe kurz vor 1200 s kann nicht wie geplant gebaut
  werden, solange Abschnitt 3 offen ist. Bildseitig bleibt `fade` 3,0 s ins Schwarz unverändert
  gültig, unabhängig vom Musikstatus.

---

## 6. Zusammenfassung für `timeline-builder`

1. K0/K1/K2-Zeiten aus Abschnitt 1 übernehmen (Cold Open 40 s statt 30 s, K2 70 s statt 80 s), K3
   und alles danach bleibt exakt wie im Beat-Sheet.
2. `music-01` und `music-02` aus Abschnitt 2.1/2.2 direkt übernehmen — beide vollständig
   durchgemessen, beide Kapitelgrenzen (395 s, 730 s) bereits nah am echten Beat-Grid.
3. `music-03` aus Abschnitt 2.4 nur als **Übergangslösung** übernehmen — die Lücke 1103,887–1200 s
   ist ein offener Punkt (Abschnitt 3), keine für mich entscheidbare Frage. Bitte an Nutzer/
   Orchestrator zurückspiegeln, bevor der Export als musikalisch vollständig gilt.
4. Vier Atmo-`AudioClip`s aus Abschnitt 4 einbauen, sobald die jeweiligen Kernbeat-Clips (K3
   Oskar/Deck, K7 Flåmsbana, K10 Storsæterfossen, K14 Kiesufer) feststehen — Zeiten hier sind
   Zielfenster, keine exakten Clip-Grenzen.
5. Lizenzstatus aller drei Pflicht-Tracks ist ungeklärt (Abschnitt 3) — für eine Veröffentlichung
   vor Freigabe klären, unabhängig vom Längen-Problem.
