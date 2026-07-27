# Musik-Prompt-Vorlage

Vorlage für die Prompts, die der `audio-designer`-Agent nach `projects/<projekt>/design/prompts.md`
(Abschnitt Musik) schreibt, wenn für einen Export kein passender Track in
`projects/<projekt>/music/` liegt. Du kopierst den Prompt in einen KI-Musik-Dienst (Suno, Udio …),
lädst den Track herunter und legst ihn als `.wav` unter `projects/<projekt>/music/` ab. Danach
`build` erneut — die Analyse (BPM/Beats/Energie) läuft automatisch.

## Konventionen

- **Ausgabe:** WAV (oder hochbitratiges MP3), Stereo. Ziel-Länge = Export-Länge + ~5 s Reserve.
- **Instrumental, keine Vocals** (außer der Export will ausdrücklich Gesang) — Sprache/O-Ton
  soll frei bleiben.
- **Energiekurve zum Stil-Preset:** `music_energy_curve` aus dem Preset (siehe
  `docs/styles/style-catalog.md`) — z. B. `gradual_build` (Nordic Cinematic) oder
  `escalate_to_drop` (Punch Teaser).
- **Lizenz notieren:** Quelle/Lizenz des Tracks festhalten, falls der Film veröffentlicht wird.

## Prompt-Skelett (ausfüllen)

```
Instrumentaler <Genre/Charakter> Track für <Projekt/Export>, Stimmung: <Adjektive>.
Tempo: <BPM oder "langsam/treibend">.  Energieverlauf: <z. B. ruhiger Aufbau zum Höhepunkt>.
Instrumentierung: <z. B. Streicher, Pad, dezente Percussion>.
Länge: <Sekunden>.  Ohne Gesang.  Sauberer Loop-Punkt, falls wiederholt.
Referenz (optional): <Künstler/Track als Richtung>.
```

## Hinweise

- **O-Ton bleibt erhalten:** Der `audio-designer` legt fest, wo Original-Ton (z. B.
  Wasserfall, Motor) durchkommt; die Musik wird an diesen Stellen automatisch abgesenkt
  (Ducking, `duck_music_db`). Der Musik-Track muss das nicht selbst berücksichtigen.
- **Ein Track pro Stimmung reicht oft:** Verschiedene Exporte (Teaser vs. Hauptfilm) brauchen
  meist unterschiedliche Energie — dafür je einen eigenen Prompt/Track, alle liegen im selben
  `music/`-Ordner und werden pro Export im Brief ausgewählt.
