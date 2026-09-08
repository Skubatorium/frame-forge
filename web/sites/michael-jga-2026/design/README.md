# Design-System — JGA 2026 (Micha im Delirium)

## Ablauf

1. `PROMPT-designsystem.md` vollständig in ein neues Claude-Design-System-Projekt geben.
2. Den Export **hier in diesen Ordner** legen, unverändert:

```
design/
  PROMPT-designsystem.md      der Prompt (Eingang)
  DESIGN-SYSTEM.md            die Design-Dokumentation aus dem Export
  tokens.css
  theme-jga-2026.css
  base.css
  components.css
  fonts/                      Bangers + Poppins als woff2
```

3. Danach wird daraus die auslieferbare Seite unter `../public/` gebaut. `design/` bleibt
   Referenz, `public/` ist das Ergebnis.

Siehe zum Vergleich `web/sites/norwegen-2026/design/README.md` — identisches Verfahren,
anderes Thema.
