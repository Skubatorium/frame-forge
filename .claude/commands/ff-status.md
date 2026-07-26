---
description: Zeigt State und den nächsten erlaubten Schritt
argument-hint: [projekt-name]
---

Arbeitsstand anzeigen.

- Ohne Argument: `frameforge list` — alle Projekte auflisten.
- Mit `$ARGUMENTS` (Projektname): `frameforge status $ARGUMENTS` — Projekt-Phase und alle
  Export-Phasen zeigen.

Danach den **nächsten erlaubten Schritt** ableiten und explizit benennen (nicht nur den
State roh wiedergeben):

| Aktuelle Phase | Nächster Befehl |
|---|---|
| `INIT` | `/ff-ingest` |
| `INGESTED` | `/ff-index` |
| `INDEXED` | `/ff-design` |
| `DESIGNED` | `/ff-brief` (pro Export) |
| Export `BRIEFED` | `/ff-build` |
| Export `TIMELINE`/`ASSETS_BUILT` | `/ff-preview` |
| Export `PREVIEWED` | Preview ansehen lassen, dann `frameforge approve` |
| Export `APPROVED` | `/ff-render` |
| Export `RENDERED` | fertig, oder erneute Freigabe für Re-Render |

Bei mehreren Exporten pro Projekt: pro Export den nächsten Schritt einzeln nennen, nicht
nur den am weitesten fortgeschrittenen.
