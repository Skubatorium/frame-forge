# Design-System — Norwegen 2026

## Ablauf

1. `PROMPT-designsystem.md` vollständig in ein neues Claude-Design-System-Projekt geben.
2. Den Export **hier in diesen Ordner** legen, unverändert:

```
design/
  PROMPT-designsystem.md      der Prompt (Eingang)
  DESIGN-SYSTEM.md            die Design-Dokumentation aus dem Export
  tokens.css                  System-Tokens (reiseübergreifend)
  theme-norwegen-2026.css     Reise-Tokens (Akzentfarbe, Hero-Motive)
  base.css
  components.css
  index.html                  Entwurf, falls mitgeliefert
  drone.html                  Entwurf, falls mitgeliefert
  fonts/                      Schriftdateien (woff2), falls schon beschafft
```

Namen dürfen abweichen, wenn der Export andere wählt — dann bitte hier notieren.

3. Danach baue ich daraus die auslieferbare Seite unter `../public/`. Der Design-Ordner
   bleibt als Referenz erhalten; `public/` ist das Ergebnis, nicht die Quelle.

## Warum getrennt

`design/` ist der Stand des Systems, `public/` ist die konkrete Seite. Bei der nächsten Reise
wird `tokens.css`/`components.css` wiederverwendet und nur das `theme-*.css` neu gebaut.
