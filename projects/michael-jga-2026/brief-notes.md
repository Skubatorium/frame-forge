# Brief-Notizen: Micha im Delirium 2026 (JGA Brüssel)

> Entwurf (Plan 0004 §3/§7), noch nicht gegen echtes indiziertes Material geprüft — das geht
> erst nach `frameforge ingest`/`index`. Dient als fertig vorformulierte Grundlage für den
> `/ff-brief`-Wizard bzw. direkt für den `story-architect`, sobald ein Export angelegt ist
> (`frameforge new-export michael-jga-2026 <export-name>` o.ä.). Nicht selbst editierbar durch
> `frameforge` — reine Vorbereitung, die den Preset-Zufall ersetzt (Plan §3: "als Muss-Shot-
> Liste + Kapitelgerüst direkt ins Briefing geben").

**Preset:** `jga-zweiteiler` (siehe `presets/jga-zweiteiler.yaml`)
**Ziellänge:** offener Richtwert, circa 6–7 Minuten (kein starrer Wert, siehe Plan §10)

## Akt 1 — „Gediegen" (Freitag + Samstag bis zur ersten Kneipe)

Musik: Antonio Vivaldi, „L'inverno" (RV 297, ~3:31). Schnitt langsam, warm, leiser
Humor-Unterton („eigentlich sind wir schon ziemlich alt"). **Keine Comic-FX** — das ist
bewusst der Kontrast zu Akt 2.

Reihenfolge/Beats:
1. Ankunft/Anfahrt (Auto)
2. Haus/Unterkunft in Brüssel
3. Pizza + Bier + Schnaps, ruhig ins Bett
4. Frühstück am nächsten Morgen
5. Stadtbummel, Läden
6. Waffeln + Schokolade (Meme-Potenzial — hier darf's ein bisschen komisch werden, aber noch
   ohne FX-Werkzeug, rein durch Timing/Schnitt)
7. Pommes

## Akt 2 — „Eskalation" (ab der ersten Kneipe)

Musik: Pulp-Fiction-Soundtrack-Stück (~2:14, genauer Titel noch offen — siehe „Was noch
fehlt" unten). Schnitt schnell, laut. **Comic-FX aktiv** (Denkblasen, Sticker, Speedlines,
Farb-Pop, Cartoon-Outline — sparsam, als Akzent, siehe `.claude/agents/party-fx.md`).

Reihenfolge/Beats:
1. Die anderen 5 stoßen dazu (erste Kneipe)
2. Kneipe zu Kneipe
3. **Cast-Intro** (mittendrin, konkret in der Karaoke-Bar „Red"): für jede der zehn Personen
   ein kurzes Foto mit Sonnenbrille, Namensstempel eingeblendet, kurzer SFX-Einschuss —
   danach geht die Eskalation weiter. Details: `.claude/agents/party-fx.md` Schritt 5.
4. Karaoke
5. Burger/Pizza/Bier/Tequila-Shots
6. Junggeselle „abgeschossen" im Bett

## Outro — eigener dritter, ruhiger Track

Kurzes, getragen-schläfriges Stück (noch zu besorgen/generieren, siehe `design/prompts.md`
sobald angelegt). Bilder: „alle sind erledigt"-Stimmung plus die zwei Auto-Schlaf-Fotos.
Schnitt ruhig, kaum Bewegung, abrupter Wechsel von Akt 2 in diese Ruhe.

## Danke-Karte (ganz am Ende)

Kurze, schlichte Textkarte („Danke") nach dem Outro — kein neues Element nötig, bestehende
`title-card.svg`/`credits.svg`-Mechanik reicht.

## Muss-Shots (harte Anker, `content.priority: must`)

Aus der Beat-Liste oben leiten sich die festen Ankerpunkte ab, die unbedingt im fertigen
Schnitt vorkommen sollen (nicht dem Zufall der Auswahl-Logik überlassen). Sobald echtes
Material indiziert ist: die passenden Dateien mit
`frameforge set-priority michael-jga-2026 --filename "<Teil des Dateinamens>" --priority must`
markieren (oder gesammelt über `--from-file`, siehe Plan §5/§18):

- Ankunft/Anfahrt
- Haus-/Unterkunftsbild
- Anstoßen (Pizza/Bier/Schnaps)
- Frühstück
- Waffeln + Schokolade
- Pommes
- Zusammentreffen mit den restlichen 5 (erste Kneipe)
- Die zehn Sonnenbrillen-Fotos aus der Karaoke-Bar „Red" (Cast-Intro — je eins pro Person)
- Karaoke-Moment (mindestens ein weiterer, über die Cast-Intro-Fotos hinaus)
- Tequila-Shots
- „Abgeschossen im Bett"
- Die zwei Auto-Schlaf-Fotos (Outro)

Alles andere aus der Vorauswahl bleibt `ok` (Default) — bei besonders schönen/lustigen
Treffern beim Sichten optional `nice` vergeben (siehe Plan §5).

## Was noch fehlt, bevor daraus ein echter Brief wird

- Exakter Titel + Timecode des Pulp-Fiction-Stücks
- Zehn Namen zu den zehn Cast-Intro-Fotos
- Bestätigtes Datum des Wochenendes (auch für die Website-Kicker-Zeile)
- Der dritte Outro-Track (fertig oder als KI-Musik-Prompt)
