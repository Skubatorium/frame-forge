---
description: Visuelle Pipeline-Übersicht + nächster erlaubter Schritt
argument-hint: [projekt-name]
---

Arbeitsstand anzeigen.

- Ohne Argument: `frameforge list` — alle Projekte auflisten.
- Mit `$ARGUMENTS` (Projektname): `frameforge status $ARGUMENTS` — die **visuelle
  Pipeline-Karte** ausgeben. Sie zeigt pro Schritt:
  - `✓` erledigt · `→` jetzt dran · ` ` (leer) offen,
  - die Projekt-Ebene (ingest → index → design) und jede Export-Spur einzeln
    (brief → build → preview → approve → render),
  - unten den **nächsten fälligen Befehl**.

Gib die Ausgabe von `frameforge status` unverändert wieder und ergänze bei Bedarf einen Satz,
was der nächste Schritt inhaltlich bedeutet. Wenn der Nutzer geführt weitermachen will, biete
`/ff-wizard $ARGUMENTS` an — der übernimmt die Führung durch den nächsten Schritt.

Die Reihenfolge ist erzwungen (Gates); `frameforge status` sagt zuverlässig, wo das Projekt
steht und was als Nächstes möglich ist — nicht raten.
