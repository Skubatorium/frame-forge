# Norwegen 2026 — Design-System

Ein kleines, eigenständiges Design-System für **private Reise-Websites** und die erste
Anwendung darauf: die fünfseitige Familienseite zur Norwegenreise vom 18.07. bis 04.08.2026
(zwei Erwachsene, ein sechsjähriger Sohn, 18 Tage, knapp 4.000 km, zwei fertige Filme).

Die Seite läuft unter `https://norwegen.skubus.de` hinter einer Basic Auth auf
Infrastruktur-Ebene (Traefik). Die Website selbst enthält **keine** Auth-Logik, kein
Login-Formular, kein Passwortfeld.

## Quellen

Es gab keinen Vorgänger-Codebase, keine Figma-Datei und kein bestehendes Markenmaterial.
Grundlage sind ausschließlich das Briefing des Auftraggebers und die beiden Filme:

- Film 1 „Norwegen 2026 · Roadtrip", 18:00 min, 3840 × 2160/30p, 167 Einstellungen
- Film 2 „Norwegen 2026 · Drone Edit", 9:28 min, 3840 × 2160/30p, 78 Aufnahmen
- Farbhinweis aus den Filmen (Bauchbinden): `#12222f`, `#2c4a5a`, `#e0a458`

**Es existiert kein Logo.** Wo eine Marke stünde, steht der Reisetitel in Display-Type,
begleitet von einem 40 × 3 px großen Flaggenstrich (`.flagmark`). Es wurde bewusst keine
Wort- oder Bildmarke erfunden.

## Index

| Datei / Ordner | Inhalt |
|---|---|
| `styles.css` | Einstieg des Design-Systems, nur `@import`-Zeilen |
| `site/` | **Die fertige Website** — flach im Docroot, direkt auf den Server kopierbar |
| `site/assets/css/tokens.css` | System-Tokens (reisenübergreifend) |
| `site/assets/css/theme-norwegen-2026.css` | Themen-Tokens dieser Reise |
| `site/assets/css/fonts.css` | `@font-face`, selbst gehostet |
| `site/assets/css/base.css` | Reset, Grundtypografie, Seitengerüst |
| `site/assets/css/components.css` | alle Komponenten |
| `components/` | React-Nachbauten der Komponenten (fürs Prototyping) |
| `guidelines/` | Specimen-Karten für Farbe, Typo, Abstand, Motion, Marke |
| `docs/design-dokumentation.md` | Prinzipien, Farbrollen, Typo-Skala, Komponentenregeln, nächste Reise |
| `docs/schriften.md` | Font-Empfehlung mit Lizenz und Bezugsquelle |
| `docs/bildliste.md` | benötigte Bilder mit Maßen, Seitenverhältnis, Dateinamen |
| `SKILL.md` | Einstiegspunkt für Agenten |

## Komponenten

- **Core** — `Button`, `Notice`, `Prose`
- **Layout** — `SiteNav`, `PageHeader`, `SiteFooter`
- **Media** — `HeroRotator`, `FilmCard`, `VideoBlock`
- **Daten** — `StatGrid`, `FactList`, `FunFacts`, `MapFigure`

Jede Komponente existiert doppelt: als CSS-Klasse in `components.css` (das ist die Fassung,
die auf dem Server läuft) und als React-Komponente in `components/` (das ist die Fassung für
Entwürfe und Prototypen). Beide benutzen dieselben Klassennamen und dieselben Tokens.

## CONTENT FUNDAMENTALS

**Wer spricht.** Eine Person aus der Familie, in der ersten Person Singular, aber sehr
sparsam — meist gar nicht. Angesprochen wird geduzt („Bitte gib Link und Passwort nicht
weiter"), weil alle Leser bekannt sind.

**Ton.** Trocken, warm, untertrieben. Sachen werden benannt, nicht angepriesen. Kein
Reisebüro-Vokabular („atemberaubend", „unvergesslich", „Traumkulisse"), keine Superlative,
die nicht messbar sind. Wo Superlative stimmen, stehen sie nüchtern da: „die größte
Stabkirche Norwegens", „die steilste Normalspurbahn Nordeuropas".

**Beispiele für den Ton:**

- „Es beginnt still. Ein Cold Open ohne Musik, nur Wind."
- „In Aurland hat es geregnet, die Drohne blieb im Rucksack."
- „1 Fisch — gefangen an der Schärenküste, vom Sechsjährigen, winzig."
- „Weil schöner." (zur bewusst längeren Rückfahrt über Notodden)

**Zahlen.** Deutsches Format mit Punkt als Tausendertrennung (1.183 m, 3.829 km). Gerundete
Werte werden als gerundet gekennzeichnet („knapp 4.000 km", „~4.000 km") und einmal pro Seite
in einem `Notice` erklärt. Nie eine Scheingenauigkeit behaupten. Zeiten als `18:00 min`,
Auflösung als `3840 × 2160` mit echtem Mal-Zeichen.

**Kasus und Schreibweisen.** Normale deutsche Groß-/Kleinschreibung, keine Versalien außer in
Labels (dort per CSS, nicht im Text). Norwegische Ortsnamen mit korrekten Zeichen: Nærøyfjord,
Lærdalstunnel, Ålesund, Stegastein. Typografische Anführungszeichen „so".

**Länge.** Überschriften ein bis drei Wörter. Teaser-Karten genau ein Satz. Fließtext zwei bis
drei Absätze am Stück, dann ein anderer Baustein.

**Emoji: nie.** Auch keine Unicode-Symbole als Dekoration. Erlaubt sind genau drei
Sonderzeichen als Struktur: `·` als Trenner in Metazeilen, `→` als Weiterführungspfeil,
`←` als Rückweg.

**Was nicht vorkommt.** Trolle, Wikingerhelme, Runen, Elche; Ausrufezeichen; „Jetzt ansehen!";
Countdown-Rhetorik; Compliance-Sprache. Die Weitergabe-Bitte ist eine Bitte, kein Hinweisbanner.

## VISUAL FOUNDATIONS

**Grundstimmung.** Dunkel und cineastisch, wie die Umgebung eines guten Videoplayers: tiefer
blaugrüner Grund (`#0b1a24`), viel Luft, sehr wenige, sehr präzise Akzente. Das Interface
tritt hinter das 4K-Material zurück. Es gibt keinen umschaltbaren Hellmodus.

**Farbe.** Fünf Familien: Fjord (Grund und Flächen), Petrol/Gletscher (kühler Zweitakzent),
Granit (Neutrale), Kiefer/Moos (selten, für Vegetation), Mitternachtssonne/Sandgold
(Primärakzent). Sandgold `#e0a458` trägt Buttons, Links, Kennzahlen und die Eyebrow-Zeilen —
mehr Akzentflächen als das gibt es nicht. Die Flaggenfarben Rot/Weiß/Marine erscheinen nur in
zwei Bauteilen: Favicon und `.flagmark` (40 × 3 px). Nie flächig, nie als Banner.

**Bildwelt.** Kühl, kontrastreich, aus dem Filmmaterial geschnitten; per CSS leicht entsättigt
(`--img-filter: saturate(.94) contrast(1.03)`), damit Fotos und Interface derselben Familie
angehören. Kein Grain, keine Duotone-Filter, keine Schwarzweiß-Umsetzungen.

**Hintergründe.** Flächen, keine Verläufe — mit genau zwei Ausnahmen: die Schutzverläufe über
Bildern (`--scrim-hero`, `--scrim-card`) und ein sehr kurzer Verlauf im `page-header`. Keine
Ganzseiten-Gradienten, keine Muster, keine Texturen, kein Parallax.

**Typografie.** Zwei Familien. *Schibsted Grotesk* für Display, Navigation, Labels, Buttons und
alle Zahlen (tabellarische Ziffern, `-0.022em` Laufweite ab Größe 2). *Source Serif 4* für
Fließtext, 18–19 px, Zeilenhöhe 1,68, maximal 68 Zeichen je Zeile. Die Skala ist fluid
(`clamp()`) zwischen 360 und 1600 px Viewport; darüber wächst nur der Weißraum.

**Abstände.** 4-px-Basis, `--space-1` … `--space-10`. Blöcke trennt `--section-gap`
(56–120 px, fluid). Seitenrand `--page-gutter` (20–64 px). Inhalt maximal 1360 px breit,
Textspalten 1080 px.

**Ecken.** Klein und ruhig: 2/4/8/14 px. Karten und Player 8 px, Buttons 4 px, Punkte rund.
Nichts ist vollrund außer den 5-px-Punkten der `fact-list`.

**Karten.** Eine Karte ist eine Fläche (`--bg-raised`) mit 1-px-Hairline (`--line-1`) und 8 px
Radius — **kein Schatten**. Bildkarten (`film-card`) haben stattdessen ein Bild, einen
Schutzverlauf und dieselbe Hairline. Kein farbiger Linksrand als Deko; die einzige farbige
Kante ist die 2-px-Linie über einem `panel` und links am `notice`.

**Schatten.** Nur zwei Tokens, und nur einer wird tatsächlich benutzt: `--shadow-media` unter
dem Videoplayer, damit das schwarze Bild nicht in den Grund fällt. Sonst keine Schatten,
weder außen noch innen.

**Transparenz und Blur.** Genau einmal: die Kopfzeile ist zu 82 % deckend mit
`backdrop-filter: blur(14px)`. Sonst wird nichts durchscheinend.

**Bewegung.** Langsam und weich, nie federnd. `--dur-1` 130 ms für Farbe und Fokus,
`--dur-2` 240 ms für Hover, `--dur-3` 480 ms für Einblendungen. Der Hero blendet 1,7 s über
und lässt jedes Bild ~7 s stehen, mit sehr langsamem Ken-Burns (scale 1.06 → 1.12). Kurven:
`--ease-out` cubic-bezier(.22,.61,.36,1). Keine animierten Zähler, kein Parallax, kein
Scroll-Hijacking. `prefers-reduced-motion` schaltet die Rotation ab und zeigt ein Standbild;
zusätzlich werden global alle Transitions auf 0,01 ms gesetzt.

**Hover.** Text wird heller (`--text-3` → `--text-1`), Flächen eine Stufe heller
(`--bg-raised` → `--bg-raised-hover`), Rahmen wechseln von `--line-2` auf `--accent-quiet`.
Der primäre Button geht von Sandgold auf Sandgold hell. Bilder in `film-card` skalieren um
3 % und werden von 0,85 auf volle Deckkraft geführt. Nie Farbumkehr, nie Unterstreichung als
Hover-Effekt (Links sind ohnehin unterstrichen, dort wird nur die Linienfarbe kräftiger).

**Press.** 1 px nach unten (`translateY(1px)`). Kein Scale, kein Farbsprung.

**Fokus.** `:focus-visible` mit 2 px Sandgold-Outline und 3 px Abstand — sichtbar auf jedem
Grund, nie entfernt. Skip-Link oben links fährt bei Fokus ein.

**Linien.** `--line-1` (#1b3140) trennt, `--line-2` (#2b4757) rahmt. 1 px ist der Normalfall,
2 px (`--rule`) markiert Panel-Oberkanten und den linken Rand des `notice`.

**Layout-Regeln.** Nur ein fixiertes Element: die Kopfzeile (sticky). Kein Sticky-Footer,
keine schwebenden Buttons, keine Overlays, keine Modals, kein Cookie-Banner. Responsiv von
360 bis 2560 px; Umbruchpunkte bei 720, 860 und 900 px.

## ICONOGRAPHY

**Es gibt kein Icon-Set — mit Absicht.** Die Seite kommt mit fünf Seiten und zwölf
Komponenten aus; jedes Icon wäre Dekoration. Statt Symbolen arbeitet das System mit Typografie
und Fläche.

Was tatsächlich benutzt wird:

- `→` und `←` (U+2192 / U+2190) als Weiterführungs- und Rückwegpfeil in Buttons und Links.
  Sie sitzen in `.btn__arrow` und wandern beim Hover 3 px nach rechts.
- `·` (U+00B7) als Trenner in Metazeilen.
- `.flagmark` — ein 40 × 3 px breiter Streifen in Rot/Weiß/Marine, per CSS-Gradient
  (`--flag-stripe`) erzeugt. Er steht in der Kopfzeile, im Footer und als Favicon
  (`site/assets/img/favicon.svg`, die einzige SVG-Datei des Projekts).
- Die Abspielsteuerung liefert der Browser (`<video controls>`); es gibt bewusst keine
  eigenen Player-Icons.

**Emoji: nein.** Keine Piktogramm-Fonts, keine Icon-Bibliothek, kein CDN. Wenn später doch
Icons nötig werden, ist die Vorgabe: eine einzige Strichstärke (1,5 px), quadratisches
Raster, ausschließlich als lokale SVG-Dateien in `site/assets/img/` — nie von einem
fremden Server.

## Intentional additions

- `Prose` ist kein „Bauteil" im engeren Sinn, sondern der Textcontainer, der die Zeilenlänge
  garantiert. Ohne ihn wandert die Verantwortung für `max-width` in jede Seite.
- `Notice` steht im Briefing als `notice` und wird hier auch als React-Komponente geführt,
  weil er auf zwei Seiten vorkommt (Fakten, Impressum).
