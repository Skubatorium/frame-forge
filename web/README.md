# web/ — Reise-Mini-Sites

Gekapselter Zusatzbereich neben der FrameForge-Pipeline: **eine kleine, passwortgeschützte
Website pro Reise**, auf der die fertigen Filme angeschaut werden können.

Kein Teil der Video-Pipeline. Kein Python, kein Build-Schritt, keine State-Machine — nur
statische Dateien, die auf einen VPS kopiert werden.

**Bauplan je Site (bewusst klein):** Landing · eine Seite pro Film · Zahlen & Fakten ·
Impressum. Jede Reise bekommt ein eigenes, thematisch passendes Theme; System-Tokens und
Komponenten bleiben gleich.

## Struktur

```
web/
  shared/                       spätere gemeinsame Bausteine (Tokens, Komponenten)
  sites/
    norwegen-2026/
      design/                   Design-System: Prompt rein, Export raus
        PROMPT-designsystem.md  <- der Prompt für das Claude-Design-System-Projekt
        (hier landet der Export: tokens.css, components.css, Doku, …)
      content/                  Inhaltsdaten und Quellbilder (nicht deploybar)
        facts.md                alle Fakten der Reise, Quelle für die Texte
        media/                  Rohbilder, Kartenscreenshot, Stills (gitignored)
      public/                   >>> genau das kommt auf den Server <<<
        index.html
        drone.html
        assets/{css,js,img,fonts}/
        video/                  MP4s (gitignored, werden separat hochgeladen)
      deploy/                   nginx-Konfiguration, Basic-Auth-Anleitung
```

**Regel:** Alles unter `public/` wird 1:1 auf den Server kopiert. Alles außerhalb von
`public/` ist Arbeitsmaterial und bleibt lokal.

## Neue Reise anlegen

1. `web/sites/<reise>/` nach obigem Muster anlegen.
2. `design/PROMPT-designsystem.md` aus Norwegen kopieren, Fakten austauschen.
3. Nur `theme-<reise>.css` und die Bilder tauschen — Komponenten und System-Tokens bleiben.

## Videos

Die 4K-Finals liegen in `projects/<projekt>/exports/<export>/final/` und sind mehrere GB
groß. Sie gehören **nicht** ins Repo und **nicht** unverändert auf den Server:

- Browser brauchen das `faststart`-Flag (moov-Atom vorn), sonst startet die Wiedergabe nicht,
  bevor die Datei komplett geladen ist.
- 4K-Originale liegen bei ~50–76 Mbit/s. Für flüssiges Streaming über normale Anschlüsse ist
  eine 1080p-Webfassung (~10 Mbit/s) nötig; das 4K-Original kann zusätzlich als Download
  angeboten werden.

Erzeugt werden die Webfassungen über die Pipeline (`frameforge render`), nicht mit nackten
ffmpeg-Aufrufen — der Gate-Hook blockiert die ohnehin.
