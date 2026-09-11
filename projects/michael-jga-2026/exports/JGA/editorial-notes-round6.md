# Detail-Regie Export "JGA" — RUNDE 6 (5. Preview-Feedback)

Quelle: Christians Sichtung des **fünften** Previews `preview/JGA_preview.mp4`
(7:03,3 / 423,33 s, aus R5-T6), Voice-Transkript 2026-09-11.

**Ergänzt und überschreibt punktuell Runde 1–5.** Zeitangaben `M:SS` = Position im
**7:03,3-Preview** (= `timeline.json` Stand `c7669ec`, 160 Video / 34 Overlay / 25 Audio).

Christians Gesamturteil: **"schon wirklich großartig … Feinschliff."** „Reihenfolge und Texte
sind eigentlich alles ganz gut." Danach FHD + 4K — **erst nach Freigabe**.

---

## 0. Zwei übergreifende Themen

### 0.1 Akt-1 → Akt-2: die Stille MUSS weg (Hauptproblem, bisher ungelöst)
Zwischen ~2:57 und dem Akt-2-Start ist **Stille** (zwei Fotos ohne Musik). Das darf nicht
sein. Lösung:
- **`music-01` (CL) und `music-02` (Miserlou) aneinanderschieben** — kein stiller Spalt.
  `music-01` läuft bis ~1 s in Akt 2 hinein (fade_out 2,5), `music-02` setzt **0,5 s vor
  dem `v069`-Cut** ein (fade_in 1,5) → ~1,5 s Überlappung, **kein Loch**.
- Der Akt-2-**Beginn** (visuell) ist gut — bleibt der `v069`-Video-Cut. Durch die zwei
  Streichungen unten rutscht er von 3:02 auf **~2:58**; das ist ok (Christian: „wenn die
  Endzeit sich verändert, ist mir das egal, Hauptsache die Stille ist weg").
- **~5 s Bildzeit einsparen** (Christian): **`v007` (~0:23) streichen** + **`v022` (~1:11)
  streichen**. Damit kommt das Audio ohne Stille zusammen.
- Falls dadurch der Film unter ~7 min fällt: Outro-Audio darf länger, oder Akt-2-Texte-Hosts
  strecken (siehe 0.2). Ziel bleibt ~7:00.

### 0.2 Kein Text ragt ins nächste Bild
Durchgängige Regel: **Wenn ein Text länger lesbar stehen soll, muss das Footage darunter
mitwachsen.** Ein Text darf **nie** ins nächste Bild hineinragen. Mechanik: Host-Foto des
Overlays verlängern, dafür **textfreie** Nachbarfotos einen Tick kürzen („wo kein Text ist,
ein bisschen schneller").

**Einzige Ausnahme:** `ov-wimm` (~6:10) — darf über zwei Fotos laufen und dann enden. „Das
ist super."

Konkret betroffen (Host verlängert + Nachbarn gekürzt):
| Overlay | Zeit | Fix |
|---|---|---|
| `ov-crewupdate` | ~3:05 | Host `v058` 2,2 → 3,9 s; `v059`/`v060` gekürzt |
| `ov-token` „wolle Token kaufen" | ~4:22 | Host `v110` 2,4 → 3,5 s; `v111`/`v112` gekürzt; „volle Token" muss vor dem Schnitt ausgeblendet sein |
| `ov-natuerlich` „(noch) nicht" | ~5:18 | Host-Video `v145` +1,8 s (hinten); `v138`/`v144` gekürzt |
| `ov-weiterziehen` „Noch ahnten sie nicht …" | ~5:46 | Text gehört auf **`v153`** (Foto **vor** dem Taxi-Video), nicht aufs Taxi. `v153` 1,4 → 3,6 s; Taxi-Video `v154` vorne 1,6 s gekürzt; `v152` gekürzt |
| `ov-gurken` / `ov-raetkeinkaese` / `ov-ichwaresnicht` | ~5:58–6:01 | „alles zu schnell". `v159` 3,3 → 4,3 s, `v158` 2,2 → 3,0 s; `v156`/`v157` gekürzt. `ov-gurken` dur 4,0; `ov-raetkeinkaese` +1,4 s versetzt, dur 2,4; `ov-ichwaresnicht` dur 2,2 |

Nicht neu gerügt (bleiben) — `ov-letsgo`, `ov-sulemann`, `ov-biere`, `ov-praesente`,
`ov-geniesst`, `ov-christoph`, `ov-wtf`, `ov-lampen`, Cast-Namen: Runde-5-Stand.

---

## 1. Einzel-Fixes

- **Intro-Karte `v001` („JGA 2026"):** **+2,0 s** länger stehen (4,1 → 6,1 s), dann ausblenden,
  dann „Let's Go".
- **`v007` (~0:23) streichen** (Christian: „Bild auf 0:23 / Nummer 24 raus, ~2 s gespart").
- **`v022` (~1:11) streichen** (Christian: „bei Minute 11 das Bild auch rausnehmen").
- **`ov-mok-detektor` (~2:48):** „MOK" und „Detektor" kleben aneinander. → **3-zeilig**
  **„MOK" (riesig) / „DETEKTOR" / „AKTIV"**, großer Abstand nach „MOK". (Christian probierte
  „Running" → verworfen, weil Englisch → „aktiv".)
- **`ov-hydrated` „stay hydrated" (~3:55):** war „ein bisschen übertrieben" (mittig + sehr
  groß). Positionierung stacked bleibt, aber **−35 % Größe** und **oben rechts** setzen →
  „mehr Werbecharakter".
- **Schwarzblende `v160` (~6:03):** **+1,5 s** länger (2,2 → 3,7 s), *dann* fängt die
  WIMM-Musik an. (Christian: „ein, zwei Sekunden längere Schwarzblende bei 6:04, dann fängt
  die Musik an.") `music-03` `tl_in` = `v160`-Start + 1,0 s.
- **`ov-wimm` (~6:10):** unverändert — darf über zwei Fotos, „das ist super, das hört dann
  auch auf".
- **Ende (ab ~6:15):** „die Bildfolge ist super, der Ablauf ist super, das Ende ist super."
  Unverändert (Runde-5-Stand: Outro-Karte +1,5 s, Schluss-Karte `ov-thanks` bleibt stehen).

---

## 2. Code-/Timeline-Aufgaben Runde 6

- **`party-fx-recipe.py` → Runde 6:** nur zwei PNG-Deltas — `ov-mok-detektor` 3-zeilig
  (Abstand nach „MOK"), `ov-hydrated` −35 % + oben rechts. Rest Runde-5-Stand.
- **`round6-timeline.py`** (aus `round5-timeline.py`-Muster, transformiert R5→R6):
  - `v001` +2,0 s; `v007` + `v022` streichen.
  - Host-Verlängerungen + Nachbar-Kürzungen laut §0.2-Tabelle.
  - `ov-weiterziehen` an `v153` ankern; `ov-natuerlich`/`ov-gurken`/`ov-raetkeinkaese`/
    `ov-ichwaresnicht` Standzeit + Versatz.
  - Anti-Bleed-Sicherung: die sieben Lese-Texte werden zusätzlich geklemmt (nur kürzen, nie
    unter 1,6 s), falls nach der Host-Streckung noch Überhang bleibt.
  - `v160` +1,5 s.
  - Audio: `music-01` dur = `v069` + 1,0 (max 181,4), fo 2,5; `music-02` `tl_in` = `v069`
    − 0,5, fi 1,5, dur bis knapp vor `v160`; `music-03` `tl_in` = `v160` + 1,0, fi 1,5, fo 6,0.
  - `brief.yaml` `target_duration_s` nachziehen.
- **Abnahme:** `validate_semantics` + `qc.validate` leer, `pytest`/`ruff`/`doctor` grün,
  bestehende Timelines lauffähig, neues Preview gesichtet auf: **keine Stille** im Akt-1/2-
  Übergang, kein Text ragt ins Folgebild (außer `ov-wimm`), `ov-mok-detektor` entzerrt,
  `ov-hydrated` klein oben rechts, Schwarzblende ~6:03 länger.

---

## 3. Nach dem Preview (R6-T7, blockiert — braucht Christian)

Unverändert: nach `frameforge approve` → **FHD (1080p) + 4K-Download in Chunks** + Website +
SSH-Upload (`micha-jga.skubus.de/videos/`, exakter Host/Pfad weiterhin offen).
