---
description: Export-Briefing-Wizard - Stil, Ziellänge, Muss-/verbotene Shots
argument-hint: <projekt-name> <export-name>
---

Neuen Export briefen. Argumente: `$ARGUMENTS` — `<projekt-name> <export-name>`. Erfordert
Projekt-Phase `>= DESIGNED` (`gate_brief`).

Schritte:
1. `frameforge status <projekt-name>` prüfen — Projekt muss `DESIGNED` sein (impliziert
   `INDEXED`). Fehlt das, zuerst `/ff-design` bzw. `/ff-index` vorschlagen statt zu erzwingen.
2. Wizard-Dialog mit dem Nutzer:
   - Stil-Preset aus `docs/styles/style-catalog.md` wählen (oder Overrides beschreiben)
   - Ziellänge
   - Muss-Shots (Asset-IDs oder Beschreibung, über `frameforge query` auflösen)
   - Verbotene Shots
   - Sprache für Text/Overlays (Default aus `project.yaml`, pro Export überschreibbar)
3. Ergebnis als `exports/<export-name>/brief.yaml` schreiben (Preset + Overrides +
   Muss-/verbotene Shots — Schema orientiert an Plan §6).
4. Export-Phase auf `BRIEFED` setzen (`ProjectState.advance_export`), dann
   `frameforge status <projekt-name>` zur Bestätigung.

Ändert sich ein bereits bestehendes `brief.yaml`, fällt der Export laut Plan §2 auf
`BRIEFED` zurück — das ist beabsichtigt, kein Fehler.
