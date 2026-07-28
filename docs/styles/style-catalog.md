# Stil-Katalog

Presets sind **Daten**, nicht Doku: sie liegen als YAML unter `presets/` (mitgeliefert) und
`~/.frameforge/presets/` (eigene). Single Source of Truth ist der Befehl

```
frameforge presets     # Slug, Name, Passt-zu, Beschreibung, Beispiel, Bogen
```

Jedes Preset ist ein YAML-Fragment, das der Brief überschreiben kann — **Preset ≠ Zwangsjacke**.
`brief.yaml` = `preset: <slug>` + Overrides + Muss-Shots + verbotene Shots. Jedes Preset legt
fest: `pacing`, `transition_vocabulary`, `color_grade`, `text_density`, `music_energy_curve`,
`map_usage`, `photo_treatment` (Ken-Burns-Intensität), `original_audio_policy` — plus
`example` (So-sieht-das-aus) und `arc` (dramaturgischer Bogen, den der story-architect nutzt).

## Mitgelieferte Presets

| Preset | Rhythmus | Charakter | Passt zu |
|---|---|---|---|
| Nordic Cinematic | 4–8 s, langsam | Weite Establisher, Slow-Push, kalte Highlights/warme Lichter | 15-Minuten-Reisefilm |
| Punch Teaser | 0,4–1,5 s, beat | Harte Cuts, Whip-Pans, große Typo, Escalation zum Drop | 60–90 s Trailer |
| Chronikel | 3–6 s | Strikt chronologisch, Tages-Kapitelkarten, Karte zwischen Etappen | Familienfilm, Tag für Tag |
| Thematisch/Assoziativ | 2–5 s | Nach Motiv gruppiert (Wasser, Straßen …), Match-Cuts | Zweitfassung, anderer Blick |
| Diary / Handheld | 1,5–4 s | Roher Look, O-Ton dominant, handschriftliche Typo | Persönlicher, intimer Schnitt |
| Timelapse Journey | variabel | Bewegungslastig, Karte als Leitmotiv, Zeitraffer | Roadtrip-Fokus |
| **Action / Adrenalin** | 0,3–1,2 s, beat | Sehr kurze Cuts, Whip-Pans, Speed-Ramps, kräftige Farben, aggressiv | Sport / Drohne / Adrenalin |
| **Epic Trailer** | 0,6–3 s, eskalierend | Kinoreif, große Musik, Slow-Mo-Höhepunkte + harte Beat-Cuts | 90–120 s Kino-Trailer |
| **Vlog Dynamic** | 1,5–4 s | O-Ton-Sprecher, Jump-Cuts, Pop-Captions, sauberer Look | Erzählter YouTube-Vlog |
| **Calm / Meditative** | 6–14 s, sehr langsam | Lange Einstellungen, weiche Überblendungen, Pastell, Ambient | Slow-TV, Achtsamkeit |
| **Retro / Super-8** | 2–5 s | Warmer Film-Look, weiche Blenden, handschriftliche Typo | Nostalgischer Erinnerungsfilm |
| **Beat Music Video** | 0,4–1,2 s, beat | Schnitt strikt auf den Beat, Match-Cuts, satte Farben | Reise als Musikvideo |

## Eigenes Preset

Zwei Wege, beide gleichwertig:

1. **Gerüst + bearbeiten** — `frameforge preset-new <slug>` legt eine kommentierte Vorlage unter
   `~/.frameforge/presets/<slug>.yaml` an. Ausfüllen, dann im Brief `preset: <slug>`.
2. **Frei im Brief** — Parameter (pacing, color_grade …) direkt in `brief.yaml` schreiben,
   ganz ohne `preset:`. Oder ein Preset wählen und einzelne Werte überschreiben.

Eigene Presets erscheinen in `frameforge presets` mit dem Marker `(eigen)` und überschreiben
gleichnamige mitgelieferte.

## Design-Themes (Look/Palette)

Analog für Farbe/Typo/Motion: `frameforge themes` listet 9 Startsets (Nordic Cold, Warm Sunset,
Mono Editorial, Vibrant Roadtrip, Midnight Neon, Earthy Film, Clean Broadcast, Pastel Dream,
Golden Hour). `frameforge apply-theme <projekt> <slug>` schreibt eines als Startpunkt nach
`design/tokens.yaml`. Eigenes Theme: `frameforge theme-new <slug>`.
