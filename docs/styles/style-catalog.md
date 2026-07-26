# Stil-Katalog

Presets für `/ff-brief`. Jedes Preset ist ein YAML-Fragment mit Pacing-, Schnitt-, Farb- und
Typo-Parametern, das der Nutzer im Brief überschreiben kann — **Preset ≠ Zwangsjacke**.
`brief.yaml` = Preset + Overrides + Muss-Shots + verbotene Shots.

Jedes Preset legt fest: `pacing`, `transition_vocabulary`, `color_grade`, `text_density`,
`music_energy_curve`, `map_usage`, `photo_treatment` (Ken-Burns-Intensität),
`original_audio_policy`.

## Übersicht

| Preset | Schnittrhythmus | Charakter | Passt zu |
|---|---|---|---|
| Nordic Cinematic | 4–8 s, langsam | Weite Establisher, Slow-Push, kalte Highlights/warme Lichter, viel Ambiente, sparsamer Text | 15-Minuten-Reisefilm |
| Punch Teaser | 0,4–1,5 s, beat-getrieben | Harte Cuts auf den Beat, Whip-Pans, große Typo, Escalation zum Drop | 60–90 s Trailer |
| Chronikel | 3–6 s | Strikt chronologisch, Tages-Kapitelkarten, Karte zwischen den Etappen, ruhig erzählt | "Was haben wir gemacht"-Familienfilm |
| Thematisch/Assoziativ | 2–5 s | Nicht chronologisch, gruppiert nach Motiv (Wasser, Straßen, Essen, Abende), Match-Cuts | Zweitfassung mit anderem Blick |
| Diary / Handheld | 1,5–4 s | Roher Look, O-Ton dominant, Musik nur Bett, handschriftliche Typo | Persönlicher, intimer Schnitt |
| Timelapse Journey | variabel | Bewegungslastig, Karte als Leitmotiv, Zeitraffer-Blöcke, minimaler Text | Roadtrip-Fokus |

## Nordic Cinematic

```yaml
pacing: { min_s: 4, max_s: 8, rhythm: slow }
transition_vocabulary: [fade, slow_dissolve]
color_grade: { mood: cool_highlights_warm_lights, contrast: medium }
text_density: sparse
music_energy_curve: gradual_build
map_usage: between_chapters
photo_treatment: { ken_burns: subtle }
original_audio_policy: ambience_only
```

## Punch Teaser

```yaml
pacing: { min_s: 0.4, max_s: 1.5, rhythm: beat_driven }
transition_vocabulary: [hard_cut, whip_pan]
color_grade: { mood: punchy, contrast: high }
text_density: bold_large
music_energy_curve: escalate_to_drop
map_usage: none_or_flash
photo_treatment: { ken_burns: aggressive }
original_audio_policy: none
```

## Chronikel

```yaml
pacing: { min_s: 3, max_s: 6, rhythm: steady }
transition_vocabulary: [cut, fade]
color_grade: { mood: natural, contrast: medium }
text_density: chapter_cards
music_energy_curve: flat_calm
map_usage: between_legs
photo_treatment: { ken_burns: moderate }
original_audio_policy: selective_keep
```

## Thematisch/Assoziativ

```yaml
pacing: { min_s: 2, max_s: 5, rhythm: associative }
transition_vocabulary: [match_cut, dissolve]
color_grade: { mood: consistent_across_theme, contrast: medium }
text_density: minimal
music_energy_curve: per_theme_block
map_usage: none
photo_treatment: { ken_burns: moderate }
original_audio_policy: selective_keep
```

## Diary / Handheld

```yaml
pacing: { min_s: 1.5, max_s: 4, rhythm: loose }
transition_vocabulary: [cut, whip_pan]
color_grade: { mood: raw, contrast: low }
text_density: handwritten_sparse
music_energy_curve: bed_only
map_usage: none
photo_treatment: { ken_burns: minimal }
original_audio_policy: dominant
```

## Timelapse Journey

```yaml
pacing: { min_s: 1, max_s: 8, rhythm: variable }
transition_vocabulary: [cut, speed_ramp]
color_grade: { mood: vivid, contrast: medium_high }
text_density: minimal
music_energy_curve: sustained_motion
map_usage: leitmotif
photo_treatment: { ken_burns: moderate }
original_audio_policy: ambience_only
```
