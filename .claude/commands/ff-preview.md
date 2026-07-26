---
description: 1080p-Proxy-Render eines Exports
argument-hint: <projekt-name> <export-name>
---

Proxy-Preview rendern. Argumente: `$ARGUMENTS` — `<projekt-name> <export-name>`. Erfordert
`timeline.json` und Export-Phase `>= TIMELINE` (`gate_preview`), plus einen sauberen
`qc.validate()`-Durchlauf.

Schritte:
1. Optional: `qc-reviewer` vor dem Render einbeziehen, wenn seit dem letzten Preview
   inhaltliche Änderungen an der Timeline gemacht wurden (nicht bei jedem Preview nötig).
2. `frameforge preview <projekt-name> <export-name>` ausführen — prüft Gate und QC selbst,
   delegiert an `render-engineer`/`frameforge.render.render_proxy`.
3. Schlägt der Render fehl: Fehlerausgabe an `render-engineer` zur Diagnose, nicht selbst
   an der Timeline herumraten.
4. Bei Erfolg: Pfad des Proxy-Renders unter `exports/<export-name>/preview/` nennen und den
   Nutzer bitten, ihn anzusehen, bevor `/ff-render` bzw. eine Freigabe folgt.

Preview läuft immer auf Proxy-Assets, nie auf Originalen.
