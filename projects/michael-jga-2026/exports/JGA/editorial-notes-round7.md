# Detail-Regie Export "JGA" — RUNDE 7 (finales Feintuning)

Quelle: Christians Sichtung des **sechsten** Previews `preview/JGA_preview.mp4`
(7:05 / 425,1 s, aus R6-T4), Voice-Transkript 2026-09-11.

**Ergänzt und überschreibt punktuell Runde 1–6.** Zeitangaben `M:SS` = Position im
**7:05-Preview** (= `timeline.json` Stand R6, 160 Video / 34 Overlay / 25 Audio).

Christians Gesamturteil: **"schon viel besser, sieht richtig gut aus."** "Bildreihenfolge,
Schnitt alles super, die Längen sind gut." Explizit als **finale Runde** angekündigt — danach
Freigabe erwartet.

---

## 1. Intro-Schwarzblende

`v000` (Schwarz vor der Titelkarte `v001`): **+1,0 s** länger halten, bevor das Bild
(Titelkarte) erscheint.

## 2. Ken Burns — mehr Varianz

Durchgängige Kritik (Akt 1 **und** Akt 2): zu viel stures Rein-Zoom/Raus-Zoom im Wechsel.
Gewünscht:
- Öfter mal **reiner Pan ohne Zoom** (Bild bewegt sich nur leicht, Zoom bleibt ~konstant).
- Bewegungsachse nicht stur im 90°-Winkel (nur horizontal oder nur vertikal) — **leicht
  schräg/diagonal**, damit Varianz reinkommt.
- Kein hartes Redesign nötig, Gesamteindruck bleibt gut — **nur auflockern**, bei manchen
  Bildern den Zoom rausnehmen oder entschärfen, dafür einen kleinen Slide.

## 3. `ov-mok-detektor` (~2:44)

„MOK" bleibt oben stehen. Text NICHT mehr „DETEKTOR"/„AKTIV", sondern **„MODE: ON"** (2-zeilig:
„MOK" riesig / „MODE: ON" darunter).

## 4. Akt-1 → Akt-2-Übergang — Trennung schärfer (Kurskorrektur ggü. Runde 6)

Runde 6 hat den Übergang bewusst als nahtlosen 3-s-Crossfade gebaut (keine Stille). Christian
korrigiert das jetzt: **keine durchgängige Stille mehr nötig — aber die zwei Akte sollen
sauberer getrennt sein**, nicht ineinander verschmiert:
- Letztes Akt-1-Bild (~2:56, `v057`) bekommt danach eine **kurze Schwarzblende** (~1,5 s).
- `music-01` (CL-Theme) endet **an** dieser Schwarzblende (Fade-out), **nicht** mehr mit
  3,5-s-Vorlauf-Überlappung in Akt 2 hinein.
- Zwischen Ende `music-01` und Start `music-02` (Miserlou) liegen **1 bis 1,5 s echte
  Stille** — bewusste, kurze Pause statt nahtlosem Übergang.
- Der Akt-2-**Bildschnitt** (`v069`) bleibt visuell an derselben Stelle (~2:58–2:59) — die
  Schwarzblende schiebt ihn nur um ihre eigene Länge nach hinten. Miserlou setzt **exakt mit
  dem Bild** ein, nicht mehr vorher.
- (Bei R6 lag `music-02`-Start bei 2:54,5 mit 3,5-s-Crossfade-Vorlauf — Christian hört das als
  „beginnt schon bei 2:57" und will es später, **mit dem Bild zusammen**.)

Akt-2-Ken-Burns: dieselbe Varianz-Regel wie §2, nicht separat behandeln.

## 5. Bild bei 3:51 raus

`v092` (Nahaufnahme Mann mit rausgestreckter Zunge + Corona-Flasche, Schärfe 0.018, Rating
3/5) — wirkt neben `v090`/`v091` (Anstoßen/Gruppe) redundant („doppelt gemoppelt"). Streichen.
`ov-hydrated` (danach) bleibt unverändert, ist gut.

## 6. `ov-weiterziehen` „Noch ahnten sie nicht …" (~5:45)

Text muss auf das Bild **vor** dem aktuellen Host (`v153`, zwei Personen schwarze Kleidung
vorne links) gemünzt werden, also auf **`v152`**. Länger stehen lassen. Das Taxi-Video
danach (`v154`) **deutlich kürzer** zeigen.

## 7. Gurken-Szene (~5:57)

Zu viel Text, muss nur kurz zu sehen sein. `ov-gurken` kürzen auf **„Der Micha mag Gurken!" /
„Gib mir die Gurken."** (2 Zeilen, Ausrufezeichen nach „Gurken", dritte Zeile „Er braucht sie
dringend" raus). Kürzere Standzeit. `ov-raetkeinkaese` („Rät kein Käse", oben rechts) bleibt
unverändert, ist gut.

## 8. Schluss-Karte `ov-thanks`

„No animals were harmed in the making of this movie." — **Punkt am Ende raus.**

## 9. Alles andere

Bildreihenfolge, Schnitt, Längen, Musik-Übergang Miserlou→WIMM, Schwarzblende vor WIMM,
`ov-wimm`, Outro — alles bestätigt gut, **unverändert**.

---

## 10. Code-/Timeline-Aufgaben Runde 7

- **`party-fx-recipe.py` → Runde 7:** `ov-mok-detektor` 2-zeilig „MOK"/„MODE: ON", `ov-gurken`
  Text kürzen, `ov-thanks` Punkt raus.
- **`round7-timeline.py`** (aus `round6-timeline.py`-Muster, transformiert R6→R7):
  - `v000` +1,0 s.
  - KB-Diversifizierungs-Pass: Teilmenge der `kenburns`-Effekte auf reinen Pan (Zoom konst.)
    oder diagonale Achse umstellen, um den Rein/Raus-Wechsel aufzubrechen.
  - `v092` streichen.
  - Neue Schwarzblende zwischen `v057` und `v069` (~1,5 s), `music-01` endet dort (fo),
    `music-02` startet **mit** `v069` (kein Vorlauf mehr), Ziel-Lücke 1,0–1,5 s Stille.
  - `ov-weiterziehen` von `v153` auf `v152` umhängen, Standzeit hoch; `v154` (Taxi) kürzen.
  - `ov-gurken` Standzeit runter (kürzerer Text); `v159` ggf. leicht zurücknehmen.
  - `brief.yaml` `target_duration_s` nachziehen.
- **Abnahme:** `validate_semantics` + `qc.validate` leer, Tests grün, neues Preview gesichtet
  auf: Intro-Schwarz länger, KB-Varianz spürbar, MOK/MODE ON, Akt-Übergang mit kurzer
  Schwarzblende + 1–1,5 s Stille statt Crossfade, 3:51-Bild weg, „Noch ahnten..." auf `v152`
  + Taxi kürzer, Gurken-Text kurz, kein Punkt hinter „movie".

---

## 11. Danach (blockiert — braucht Christian)

Nach `frameforge approve` → **FHD (1080p) + 4K-Download in Chunks** + Website + SSH-Upload
(`micha-jga.skubus.de/videos/`, exakter Host/Pfad weiterhin offen).
