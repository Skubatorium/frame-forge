---
description: Story -> Timeline bauen (Beat-Sheet + timeline.json)
argument-hint: <projekt-name> <export-name>
---

Timeline für den Export bauen. Argumente: `$ARGUMENTS` — `<projekt-name> <export-name>`.
Erfordert Export-Phase `>= BRIEFED` (`gate_build`).

Schritte:
1. `frameforge status <projekt-name>` prüfen — der Export muss `BRIEFED` sein.
2. Delegiere an `story-architect`: Beat-Sheet aus `brief.yaml` + Index bauen
   (`exports/<export-name>/beatsheet.md`).
3. Bei Musik-/O-Ton-Bedarf: `audio-designer` einbeziehen (Track-Wahl, Ducking-Fenster),
   bei Karten-Segmenten `map-animator` (Route-Reveal-Clips).
4. Delegiere an `timeline-builder`: Beat-Sheet + Zulieferungen → `timeline.json`
   (`exports/<export-name>/timeline.json`), inklusive `Timeline.validate_semantics()`.
5. `frameforge build <projekt-name> <export-name>` ausführen — prüft das Gate, setzt bei
   Erfolg die Export-Phase weiter.
6. `frameforge status <projekt-name>` zur Bestätigung.

Kein Rendering in diesem Schritt — das ist `/ff-preview`.
