---
description: Designsystem-Wizard - Tokens, Typo, Farbe, Motion, Asset-Prompts
argument-hint: <projekt-name>
---

Designsystem für Projekt `$ARGUMENTS` aufbauen bzw. verfeinern.

Schritte:
1. `frameforge status $ARGUMENTS` prüfen.
2. Delegiere an den `design-system`-Agenten. Er führt durch Plan §7
   (`docs/plans/0001-initial-structure.md`): Stimmung → Farbpalette/Typo → Farbrollen →
   Motion-Kurven → Asset-Inventur → `design/prompts.md` für Fehlendes.
3. Bei fehlenden Design-Assets (`design/assets/`): Prompts vorlegen, Nutzer entscheidet,
   ob er die Bilder selbst besorgt oder Platzhalter erlaubt sind.
4. `frameforge design $ARGUMENTS` ausführen, sobald Tokens stehen (setzt Projekt-Phase
   auf `DESIGNED`, sofern kein Fehler).
5. `frameforge status $ARGUMENTS` sollte danach `DESIGNED` zeigen.

Ein Projekt hat **ein** Designsystem für alle Exporte — nicht pro Export neu erfinden.
