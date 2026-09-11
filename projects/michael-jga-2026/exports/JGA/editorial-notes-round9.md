# Detail-Regie Export "JGA" — RUNDE 9 (zwei Text-Korrekturen + eine Streichung)

Quelle: Christians Sichtung des **achten** Previews `preview/JGA_preview.mp4`
(7:05,8 / 425,8 s, aus R8-T3), Voice-Transkript 2026-09-11.

Christian: **"Es sind doch noch zwei kleine textliche Änderungen ... da es sich hier nur um
textliche Anpassungen handelt, kriegst du hiermit auch die Freigabe."** — Freigabe erteilt,
FHD + 4K sollen direkt danach gerendert werden.

---

## 1. `ov-sulemann-b` (~0:35) — "Bestermann"-Zeile raus

Aktuell "Pizzamann / Sülemann / Bestermann" (3 Zeilen). Dritte Zeile raus, bleibt
"Pizzamann / Sülemann" (2 Zeilen), `ov-sulemann-a` ("Der Mann des Abends") unverändert.

## 2. `ov-praesente` (~2:26) — Tippfehler/Wortwahl

War "Süßes Geschenk / für den / jungen Gesellen". **Korrigiert auf "Süßes Geschenk / für den /
Junggesellen"** (ein Wort — Junggesellenabschied). Christian hat in der Durchsage selbst
zwischen "die jungen Gesellen" (Plural) und "den Junggesellen" hin- und herkorrigiert; die
**explizite Nachkorrektur** stellt klar: **"für den Junggesellen"** ist richtig, nicht Plural.

## 3. "Frietland"-Bild (`v056`, ~2:55) raus

Terrassen-Aufnahme der Frittenbude "Frietland" — Christian: Bilder rücken dadurch vor,
Schwarzblende + kurze Stille am Akt-1/2-Übergang passen dann besser (Audio endet ohnehin vor
dem letzten Akt-1-Bild).

## 4. Rest bestätigt final gut — **Freigabe erteilt**

"Alles zu Ende geguckt, der Rest passt. Das sind wirklich nur die beiden Änderungen." Nach der
Umsetzung: FHD-Render (1080p) + 4K-Render, beide Dateien für den Upload.

---

## 5. Code-Aufgaben Runde 9

- **`party-fx-recipe.py` → Runde 9:** `ov-sulemann-b` 2-zeilig, `ov-praesente` „für den
  Junggesellen".
- **`round9-timeline.py`** (aus `round8-timeline.py`-Muster): `v056` streichen, Audio
  (Akt-Übergang + WIMM-Ende) auf neue Geometrie nachziehen, `brief.yaml`.
- **Abnahme:** `validate_semantics` + `qc.validate` leer, Tests grün, Preview gesichtet,
  danach FHD + 4K-Render.
