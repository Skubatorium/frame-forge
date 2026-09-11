# Detail-Regie Export "JGA" — RUNDE 8 (Korrektur eines Missverständnisses aus Runde 7)

Quelle: Christians Sichtung des **siebten** Previews `preview/JGA_preview.mp4`
(7:04,4 / 424,4 s, aus R7-T4), Voice-Transkript 2026-09-11.

Christians Urteil: **"Video ist quasi fertig ... eine ganz kleine Sache."** "Der Rest passt
alles, das sieht richtig cool aus, alles super gemacht, das kann alles so bleiben."

---

## 0. Der Fehler aus Runde 7

R7 hat `v092` (Asset `20260905-phone-a05520` / IMG_1543, Zunge raus neben Corona-Flasche)
gestrichen — in der Annahme, das sei das von Christian als "doppelt gemoppelt" gerügte 3:51-Bild.
**Das war falsch.** `v092` war laut eigener Notiz im Original-Timeline-Eintrag genau das Bild,
das mit `ov-hydrated` ("stay hydrated") zusammengehört (Zunge raus = Durst-Gag). Christian
wollte stattdessen `v091` (Asset `20260905-phone-8d1ede`, Dachterrasse-Anstoßen-Szene, jetzt an
Position ~3:52) draußen haben — die ist inhaltlich redundant zu `v090` (Untersicht-Anstoßen,
~3:50–3:52, **bleibt**).

**Korrektur:**
- `v091` (~3:52, Dachterrasse-Anstoßen) raus.
- `v092`/IMG_1543 (Zunge + Corona) wieder rein, an der Stelle, **mit `ov-hydrated` verknüpft**.
  Bild soll ein bisschen "wackeln" (aktive Ken-Burns-Bewegung, nicht statisch).
- `v090` (~3:50–3:51, bleibt unverändert).

## 1. `ov-christoph` „Wo ist eigentlich Christoph?" (~3:54) komplett raus

Kompletter Fall weg — kein Ersatztext, keine neue Platzierung.

## 2. `ov-raetkeinkaese` „Rät kein Käse" etwas länger stehen lassen

Rest der Gurken-Szene bestätigt gut (`ov-gurken` "Der Micha mag Gurken! Gib mir die Gurken."
bleibt unverändert).

## 3. `ov-ichwaresnicht` „Ich war es nicht" (~6:01) komplett raus

"Zu viel Text hintereinander" — nach `ov-raetkeinkaese` folgt direkt die Pause/Aftermath.

## 4. Alles andere bestätigt final gut, unverändert

Reihenfolge, restliche Texte, Schwarzblende, Aftermath, Dank-Karte — "that's it."

---

## 5. Code-/Timeline-Aufgaben Runde 8

- **`round8-timeline.py`** (aus `round7-timeline.py`-Muster, transformiert R7→R8):
  - `v091` streichen.
  - `v092` (IMG_1543/a05520) wieder einfügen, an `v090` anschließend, `ov-hydrated`
    darauf verankern.
  - `ov-christoph` aus der Overlay-Spur entfernen.
  - `ov-raetkeinkaese` Standzeit erhöhen (Host `v159` ggf. mitwachsen lassen).
  - `ov-ichwaresnicht` aus der Overlay-Spur entfernen; `v158` kann dafür etwas schrumpfen.
  - `brief.yaml` `target_duration_s` nachziehen.
- **Abnahme:** `validate_semantics` + `qc.validate` leer, Tests grün, neues Preview gesichtet
  auf: `ov-hydrated` sitzt auf dem Zunge-raus-Bild (IMG_1543), kein Christoph-Text mehr, kein
  Ich-war-es-nicht-Text mehr, `ov-raetkeinkaese` länger sichtbar.

---

## 6. Danach (blockiert — braucht Christian)

Nach `frameforge approve` → **FHD (1080p) + 4K-Download in Chunks** + Website + SSH-Upload
(`micha-jga.skubus.de/videos/`, exakter Host/Pfad weiterhin offen).
