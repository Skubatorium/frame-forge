# KI-Prompts — `michael-jga-2026`

Prompts nach `templates/prompts/music.md`-Konvention. Entwurf (Plan 0004 §6/§18) — noch nicht
gegen echte Schnittlänge geprüft, da Ingest/Index/Timeline erst nach echtem Material laufen.

## Musik

### Outro-Track (dritter Musiktrack, Christians Entscheidung aus Plan §6)

**Kontext:** Akt 1 läuft auf Vivaldis „L'inverno" (~3:31), Akt 2 auf einem Pulp-Fiction-
Soundtrack-Stück (~2:14, Titel noch offen). Für den ruhigen Ausklang danach hat sich Christian
für einen dritten, eigenständigen, ruhigen Track entschieden statt einer dritten Wiederverwendung
vorhandener Musik. Laut Preset-`arc` (`presets/jga-zweiteiler.yaml`) macht das Outro ca. 10 % der
Gesamtlaufzeit aus — bei einer offenen Zielrichtung von 6–7 Minuten also grob 35–45 Sekunden.
**Reine Schätzung**, die erst nach dem echten Schnitt feststeht — eher zu lang als zu kurz
generieren, überschüssige Länge lässt sich beim Build kappen, eine zu kurze nicht verlängern.

**Ziel:** ruhiger, schläfrig-getragener Ausklang nach der Partynacht — trägt die „alle sind
erledigt"-Bilder plus die zwei Auto-Schlaf-Fotos. Kein erneuter Spannungsaufbau, kein Beat mehr.

**Ausgabe:** WAV (oder hochbitratiges MP3), Stereo. Ziel-Länge = **45 Sekunden** (Reserve schon
eingerechnet, siehe oben — bei Bedarf anpassen, sobald die echte Outro-Dauer feststeht).
**Instrumental, keine Vocals.**
**Energiekurve:** durchgehend niedrig und fallend — kein `gradual_build`/`escalate_to_drop` wie
in den beiden Hauptakten, sondern das genaue Gegenteil: aus der Stille kommend, bis zum Schluss
leiser werdend.

```
Instrumentaler, ruhiger Ambient-/Lo-Fi-Track als schläfriger Ausklang nach einer durchzechten
Partynacht, Stimmung: warm, erschöpft-zufrieden, sacht, ein bisschen wehmütig-komisch (wie ein
"alle sind fertig, aber es war gut"-Gefühl).
Tempo: sehr langsam, ca. 60-70 BPM oder ohne festen Beat.
Energieverlauf: durchgehend niedrig, leicht abfallend zum Ende hin, keine Steigerung.
Instrumentierung: warme Klavier- oder Wurlitzer-Akkorde, weiche Pads, ganz dezente,
unaufdringliche Percussion oder gar keine, evtl. leises Vinyl-Rauschen für Wärme.
Länge: 45 Sekunden. Ohne Gesang. Sauberer, leiser Ausklang, kein Loop-Punkt nötig.
Referenz (optional): ruhige Lo-Fi-/Ambient-Outros, wie man sie am Ende eines
Reise-/Partyvideos hört — Richtung "Nachglühen", nicht "Chillout-Beat".
```

**Nach Erzeugung:** als `.wav`/`.mp3` unter `projects/michael-jga-2026/music/` ablegen (z. B.
`music/outro-<Dienst>.wav`), danach `build` — Analyse (BPM/Beats/Energie) läuft automatisch.
Lizenz/Quelle des KI-Dienstes hier vermerken (Plan §11: Musik-Lizenz ist ein offener Punkt, für
diesen KI-generierten Track aber unkritischer als beim Pulp-Fiction-Stück).

### Vivaldi „L'inverno" und Pulp-Fiction-Stück

Keine KI-Prompts nötig — beides sind bereits existierende, konkrete Aufnahmen, die Christian
selbst besorgt (Vivaldi: freie Wahl der Interpretation/Aufnahme, gemeinfrei; Pulp-Fiction-Stück:
genauer Titel laut Plan §11 noch offen, kommerzielle Aufnahme, Lizenzhinweis siehe dort).
