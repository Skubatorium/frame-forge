---
description: Final-Render (4K) eines freigegebenen Exports
argument-hint: <projekt-name> <export-name>
---

Final-Render. Argumente: `$ARGUMENTS` — `<projekt-name> <export-name>`. Erfordert
Export-Phase exakt `APPROVED` (`gate_render_final` — auch ein bereits `RENDERED`-Export
braucht für einen erneuten Final-Render wieder eine explizite Freigabe, siehe
`docs/plans/PROGRESS.md`, Task 2).

Schritte:
1. `frameforge status <projekt-name>` prüfen. Ist der Export noch nicht `APPROVED`: darauf
   hinweisen, dass zuerst `/ff-preview` und danach eine explizite Freigabe
   (`frameforge approve <projekt-name> <export-name>`) nötig sind. **Nicht** selbstständig
   freigeben — das ist eine bewusste Nutzer-Entscheidung nach dem Ansehen des Previews.
2. Ist `APPROVED` erreicht: `frameforge render <projekt-name> <export-name>` ausführen —
   delegiert an `render-engineer`/`frameforge.render.render_final`, mappt automatisch auf
   die 4K-Originale.
3. Bei Erfolg: Pfad unter `exports/<export-name>/final/` nennen.
4. Scheitert der Render: an `render-engineer` zur Diagnose übergeben.

Nackte `ffmpeg`-Aufrufe sind in dieser gesamten Pipeline verboten und werden vom Gate-Hook
blockiert — auch als "schneller Test" nicht versuchen.
