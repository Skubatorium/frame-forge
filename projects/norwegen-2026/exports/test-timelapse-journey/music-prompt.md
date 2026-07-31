# Musik-Prompt — Export `test-timelapse-journey`

3-Min-Überblickstrailer, Mischung Timelapse-Journey + Punch-Teaser. Beat-getrieben, harte
Cuts/Speed-Ramps auf den Beat, `escalate_to_drop` mit verteilten Action-Höhepunkten.

**Ablauf:** Prompt in einen KI-Musik-Dienst (Suno, Udio …) kopieren, Track als **WAV** nach
`projects/norwegen-2026/music/` legen (Dateiname z. B. `timelapse-journey-trailer.wav`), dann
`build` erneut — BPM/Beats/Energie werden automatisch analysiert und die Cuts darauf gesetzt.

## Prompt (zum Kopieren)

```
Instrumentaler cinematic-epic Trailer-Track (orchestral-elektronischer Hybrid) für einen
Norwegen-Drohnen-Reisetrailer. Stimmung: ehrfürchtig, weit, abenteuerlich, nordisch-kühl mit
warmem Kern, treibend.
Tempo: treibend, ~124 BPM, klare Downbeats zum Schneiden.
Energieverlauf (escalate_to_drop, 3 Minuten):
- 0:00–0:20 atmosphärischer Aufbau (luftige Pads, ferne Streicher, ein pulsierender Sub),
- 0:20–1:05 Puls setzt ein, Percussion/Plucks wachsen, erste Steigerung,
- ~1:05 erster Drop / Höhepunkt (Taiko/Kick, breite Streicher),
- 1:05–2:00 treibender Reise-Teil, konstante Beats zum harten Schneiden,
- 2:00–2:30 großer Build (Riser, Snare-Roll),
- 2:30–2:50 finaler, größter Drop (Climax),
- 2:50–3:00 Auflösung/Ausklang.
Instrumentierung: pulsierender Synth-Bass, cineastische Drums/Taiko-Akzente, Streicher-Swells,
helle Plucks, klarer Kick auf jedem Beat. Kräftige Akzent-Hits an den drei Höhepunkten.
Länge: ~185 Sekunden (180 s + Reserve). Ohne Gesang. Stereo.
Referenz (optional): Trailer-Musik à la "Really Slow Motion" / M83-artige Weite.
```

## Wichtig
- **Instrumental, keine Vocals** — O-Ton-Akzente (Wasserfall, Wind) sollen frei bleiben; die
  Musik wird an solchen Stellen automatisch abgesenkt (Ducking).
- **Länge = 180 s + ~5 s Reserve.**
- **Lizenz/Quelle notieren**, falls der Film veröffentlicht wird.
