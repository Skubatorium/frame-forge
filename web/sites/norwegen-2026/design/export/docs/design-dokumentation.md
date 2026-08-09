# Design-Dokumentation

## Prinzipien

1. **Das Bild führt, das Interface folgt.** Alles Gestaltete ist dunkel, ruhig und
   zurückgenommen; Farbe kommt aus dem Filmmaterial. Wer die Seite öffnet, soll kurz „oh,
   schön" denken und dann auf Play drücken.
2. **Wenige Dinge, richtig gemacht.** Fünf Seiten, zwölf Komponenten, eine Akzentfarbe.
   Jede zusätzliche Idee muss eine bestehende ersetzen.
3. **Norwegen als Farbe, nicht als Kostüm.** Fjord, Gletscher, Granit, Moos,
   Mitternachtssonne. Keine Trolle, keine Runen, keine Wikinger.
4. **Statisch und selbstgenügsam.** Kein Build, kein Framework, keine externen Requests.
   Die Seite muss auch in zehn Jahren noch aufgehen.
5. **Wiederverwendbar trennen.** System bleibt, Thema wechselt, Inhalt steht im HTML.

## Farbrollen

Komponenten benutzen **ausschließlich Rollen**, nie Palettenwerte. Die Rollen sind in
`tokens.css` deklariert (mit neutralen Defaults) und in `theme-norwegen-2026.css` belegt.

| Rolle | Wert (Norwegen 2026) | Verwendung |
|---|---|---|
| `--bg-page` | `#0b1a24` | Seitengrund |
| `--bg-sunken` | `#070f16` | Footer, tiefer gelegte Zonen, Drohnenseite |
| `--bg-raised` | `#0f2029` | Karten, Panels, Download-Block |
| `--bg-raised-hover` | `#17303f` | Hover auf angehobenen Flächen |
| `--bg-inset` | `#060d13` | Player-Bett |
| `--text-1` | `#eaf1f4` | Überschriften, starke Aussagen (15:1) |
| `--text-2` | `#b6c7d0` | Fließtext (10:1) |
| `--text-3` | `#90a3ad` | Labels, Meta, Bildunterschriften (6,6:1) |
| `--line-1` | `#1b3140` | Trennlinien |
| `--line-2` | `#2b4757` | Rahmen, Hover-Rahmen |
| `--accent` | `#e0a458` | Primärbuttons, Links, Kennzahlen, Eyebrows |
| `--accent-hover` | `#eec089` | Hover darauf |
| `--accent-quiet` | `#5c4630` | Unterstreichungen, Panel-Kanten, Punkte |
| `--accent-2` | `#6fb2c0` | kühler Zweitakzent, sparsam (jede dritte Fun-Fact-Zahl) |
| `--mark`, `--mark-2` | `#ba0c2f`, `#00205b` | ausschließlich Flaggenmarke und Favicon |
| `--focus-color` | `#eec089` | Fokusring |

Kontrast: Fließtext ≥ 4,5:1 ist überall erfüllt; `--text-3` liegt bei 6,6:1 und wird trotzdem
nur für Kurzangaben verwendet.

## Typo-Skala

Fluid via `clamp()`, Bezug 360 → 1600 px Viewport.

| Token | klein → groß | Einsatz |
|---|---|---|
| `--step-7` | 57 → 108 px | Hero-Titel |
| `--step-6` | 48 → 84 px | Reserve |
| `--step-5` | 40 → 66 px | `h1` der Unterseiten |
| `--step-4` | 34 → 51 px | Kennzahlen |
| `--step-3` | 28 → 40 px | `h2`, Karten-Titel, Fun-Fact-Zahlen |
| `--step-2` | 24 → 31 px | Reserve |
| `--step-1` | 20 → 24 px | `h3`, Lead-Absatz |
| `--step-0` | 17 → 19 px | Fließtext |
| `--step--1` | 13,5 → 15 px | Meta, Buttons, Navigation |
| `--step--2` | 11,5 → 12,6 px | Labels in Kleinversalien |

Fließtext: `--font-text`, `--leading-prose` 1,68, `--measure` 68 Zeichen.
Display: `--font-display`, `--leading-snug` 1,22, `--tracking-display` −0,022em.
Zahlen immer tabellarisch (`font-variant-numeric: tabular-nums`).

## Komponenten und ihre Regeln

| Komponente | CSS-Klasse | Regel |
|---|---|---|
| `HeroRotator` | `.hero` | Nur auf der Landing, genau einmal. 4–6 Bilder, 7 s Standzeit, 1,7 s Blende. Bilder ohne Alt-Text (dekorativ). `prefers-reduced-motion` → Standbild. |
| `PageHeader` | `.page-header` | Kopf jeder Unterseite. Nie mit Bild, nie über 40 % Viewporthöhe. Eyebrow, Titel, ein Satz, Metaliste. |
| `StatGrid` | `.stat-grid` | Vier Zahlen je Zeile, ab 720 px vierspaltig. Einheit klein und grau. Gerundete Zahlen als solche kennzeichnen. |
| `FilmCard` | `.film-card` | Immer paarweise. Genau ein Satz Text, genau ein Button. Bild + Verlauf + Hairline, nie Schatten. |
| `VideoBlock` | `.video-block` | `preload="metadata"`, Poster, nie Autoplay, nie zwei Player auf einer Seite. 4K bleibt Download. |
| `Prose` | `.prose` | Jeder Fließtext liegt darin. Zwei bis drei Absätze, dann ein anderer Baustein. |
| `MapFigure` | `.map-figure` | Statisches Bild plus externer Link. Niemals ein Maps-iframe. Bildunterschrift sagt, was nicht zu sehen ist. |
| `FactList` | `.fact-list` | Geordnete Stationen. `mark` höchstens für jede dritte Zeile. Ab 900 px zweispaltig (`--columns`). |
| `FunFacts` | `.fun-facts` | Nur auf der Faktenseite, ganz unten. Zahl links, ein Satz rechts, Pointe am Ende. |
| `Button` | `.btn` | Ein primärer Button je Abschnitt. Mindesthöhe 46 px. Kein Schatten, kein Verlauf, keine Versalien. |
| `SiteNav` / `SiteFooter` | `.nav` / `.footer` | Vier Links in der Navigation, Impressum nur im Footer. Weitergabe-Bitte im Footer jeder Seite. |
| `Notice` | `.notice` | Einordnung und Bitte, nie Warnung. Höchstens einer je Bildschirmseite. Kein Rot. |

## Barrierefreiheit

- Kontrast im Fließtext ≥ 4,5:1, tatsächlich 10:1.
- `:focus-visible` überall sichtbar, 2 px Sandgold, 3 px Abstand; nie `outline: none`.
- Skip-Link als erstes fokussierbares Element jeder Seite.
- `prefers-reduced-motion`: Hero-Rotation aus, alle Transitions auf 0,01 ms.
- Semantisches Markup: `header`/`main`/`footer`/`section` mit `aria-labelledby`, Listen als
  Listen, `figure`/`figcaption` für die Karte, `aria-current="page"` in der Navigation.
- `<track kind="captions">` ist in beiden Playern als Platzhalter angelegt.
- Dekorative Bilder tragen `alt=""`; inhaltliche Bilder beschreiben das Motiv, nicht den Anlass.

## Performance

- Fünf CSS-Dateien, ~30 KB unkomprimiert, keine JS-Abhängigkeit (der Hero ist reines CSS).
- `loading="lazy"` unterhalb des Folds; das erste Hero-Bild zusätzlich als
  `background-image`, damit in der ersten Sekunde kein schwarzes Bild steht.
- Videos liegen außerhalb des Builds unter `/videos/`; `preload="metadata"` lädt nur
  Kopfdaten.
- Ziel: unter 1,5 MB pro Seite ohne Video — mit den Bildmaßen aus `bildliste.md` erreicht.

## So entsteht die nächste Reise-Seite

**Angefasst wird:**

1. `site/assets/css/theme-<reise>.css` — neue Datei, Palette und Themen-Tokens der neuen
   Reise (Malediven: warm, hell im Wasser, tiefes Nachtblau; Schottland: Torf, Heide, Nebel).
   Die Rollennamen bleiben identisch, nur die Werte wechseln.
2. Der `<link>` auf die Theme-Datei in den fünf HTML-Seiten.
3. Die Inhalte im HTML — Texte, Zahlen, Stationen, Kuriositäten.
4. `site/assets/img/` — neue Bilder unter denselben Dateinamen.
5. Optional `fonts.css`, wenn die Reise eine andere Display-Schrift bekommen soll.
   Die Rollen `--font-display` / `--font-text` in `tokens.css` bleiben.

**Nie angefasst wird:**

- `tokens.css` (außer man ändert das System selbst)
- `base.css`
- `components.css`
- die Struktur der fünf Seiten

Faustregel: Wenn eine Änderung nur für eine Reise gilt, gehört sie ins Theme oder ins HTML.
Wenn sie für alle gilt, gehört sie ins System — und dann in alle Reisen zurück.
