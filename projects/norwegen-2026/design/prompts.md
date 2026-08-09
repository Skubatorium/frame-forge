# KI-Prompts — `norwegen-2026`

Prompts nach `templates/prompts/music.md`-Konvention. Nur anwenden, wenn die dort beschriebenen
Bedingungen tatsächlich eintreten — siehe Kontext bei jedem Eintrag.

## Musik

### Export `vlog-edit` — Option "KI-Verlängerung Track C" (bedingt, nicht sofort auslösen)

**Kontext:** siehe `exports/vlog-edit/audio-plan.md` Abschnitt 3. Der Pflicht-Track "Aguila de
Oro (Ecstatic Mix)" ist mit gemessenen 374,63 s zu kurz für den ihm zugeteilten Abschnitt C
(480 s, 720–1200 s) — Fehlbetrag 105,37 s. Das ist **eine von drei Optionen** (siehe audio-plan.md
Abschnitt 3), keine getroffene Entscheidung. Diesen Prompt nur verwenden, wenn Nutzer/Orchestrator
sich für die KI-Verlängerung statt einer längeren Original-Version oder einem D-Abschnitt
entscheiden.

**Ziel:** kein Versuch, den lizenzierten Originaltrack zu imitieren oder nahtlos zu verlängern
(rechtlich unsauber und klanglich riskant), sondern ein **eigenständiger, sauber lizenzierbarer
Ausklang-Track**, der den Bruch zwischen Track C und Filmende überbrückt — Charakter und Tempo an
Aguila de Oro angelehnt, aber ein neues Stück.

**Ausgabe:** WAV, Stereo. Ziel-Länge = 110 s + 5 s Reserve = **115 s**.
**Instrumental, keine Vocals.**
**Energiekurve:** passend zum Ende von `music_energy_curve: gradual_build` — der Film ist zu
diesem Zeitpunkt bereits im Ausklang (K13–K15: "niedrig, weit", "niedrig, warm", "Ausklang"), der
Track sollte also **nicht** erneut eskalieren, sondern das Ecstatic-Niveau von Track C sanft
auslaufen lassen.

```
Instrumentaler Ecstatic-/World-Fusion-Track als ruhiger Ausklang nach einem energetischen
Höhepunkt, Stimmung: warm, weit, zufrieden, sacht nachklingend statt eskalierend.
Tempo: ca. 82 BPM, im Verlauf leicht verlangsamend.
Energieverlauf: beginnt auf mittlerem Energieniveau (Nachklang eines Ecstatic-Höhepunkts),
nimmt über die volle Länge stetig ab, endet nahezu still.
Instrumentierung: warme Pads, dezente Percussion, akustische/organische Texturen (Flöte,
Streicher oder Kalimba), kein treibender Beat mehr im letzten Drittel.
Länge: 115 Sekunden. Ohne Gesang. Kein Loop-Punkt nötig (linearer Ausklang, kein Repeat).
Referenz (optional): Little Whale, Sariel Orenda — Richtung "Ecstatic/World", aber ruhiger,
ausklingender Charakter statt Aufbau.
```

**Nach Erzeugung:** als `.wav` unter `projects/norwegen-2026/music/` ablegen (z. B.
`music/KI Generated/Aguila-Ausklang-<Dienst>.wav`), danach `build` erneut — Analyse läuft
automatisch. Lizenz/Quelle des KI-Dienstes hier oder in `audio-plan.md` vermerken.

**Lizenz-Hinweis:** wie bei den drei Original-Pflicht-Tracks (siehe `audio-plan.md` Abschnitt 3)
gilt auch hier — Nutzungsbedingungen des jeweiligen KI-Dienstes für den Anwendungsfall
(Veröffentlichung des fertigen Films) vor Verwendung prüfen und dokumentieren.
