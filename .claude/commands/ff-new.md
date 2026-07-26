---
description: Neues FrameForge-Projekt anlegen
argument-hint: <projekt-name> <media-root> [timezone] [language]
---

Lege ein neues Projekt an.

Argumente: `$ARGUMENTS` — erwartet mindestens `<projekt-name> <media-root>`, optional
`<timezone>` (Default `UTC`) und `<language>` (Default `de`).

Schritte:
1. Prüfe, ob `projects/<projekt-name>/` bereits existiert (`frameforge list`). Falls ja,
   abbrechen und nachfragen statt zu überschreiben.
2. `frameforge new <projekt-name> --media-root <media-root> [--timezone <tz>] [--language <lang>]`
   ausführen.
3. Ergebnis prüfen: `frameforge status <projekt-name>` sollte Phase `INIT` zeigen.
4. Kurz zusammenfassen: angelegte Struktur, Hinweis falls `media-root` noch nicht existiert
   (externer Pfad, wird erst bei `frameforge ingest` gebraucht).

Nicht spekulieren, welche Werte der Nutzer will — fehlt `media-root`, nachfragen statt
Platzhalter einzusetzen.
