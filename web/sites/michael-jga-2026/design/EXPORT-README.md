# Micha im Delirium 2026 — Design System

Comic-/Party-Designsystem für einen ~6–7-minütigen Junggesellenabschieds-Film und die
dazugehörige private Website **https://micha-jga.skubus.de** (Link + Passwort gehen an die
zehn Beteiligten und ein paar Freunde).

Zehn Freunde, ein Wochenende in Brüssel. Der Film hat bewusst **zwei Gesichter**: ein
ruhiger, fast selbstironisch „gediegener" Auftakt (Ankunft, Pizza, Waffeln, Schokolade —
„wir sind schon ziemlich alt geworden") kippt beim Zusammentreffen der ganzen Gruppe in eine
laute, schnelle Partynacht (Kneipentour, Karaoke, Tequila) und klingt danach ruhig aus.
**Diese Zweiteilung ist das Designsystem.** Fast jede Entscheidung hier hat eine laute und
eine ruhige Variante — Kinoplakat vs. Programmheft.

## Quellen

- `uploads/style-reference-jga-poster.png` — **das verbindliche Stilreferenz-Bild** (Poster,
  1672 × 941). Alle Farben, Glows und der Text-Look sind daraus abgelesen. Daraus abgeleitet:
  `assets/img/poster.jpg`, `assets/img/hero.jpg`, `assets/img/film-poster.jpg`,
  `assets/img/cast/cast-01…10.jpg`.
- Der Prompt-Text des Auftrags (Seitenstruktur, Komponentenliste, harte Technikregeln).
- Farbwerte abgestimmt mit dem FrameForge-Designsystem des Videos (Plan 0004 §4.1) —
  `#1e1640`, `#d9a441`, `#ff2e8a`, `#fdf6ec`; hier als Ausgangspunkt, nicht als Zwang.
- Kein Codebase, kein Figma, kein Logo vorhanden. **Es gibt keine Wortmarke als Datei** —
  wo eine Marke stünde, steht der Name in Bangers-Gold (siehe `.nav__brand`,
  `.footer__mark`, `thumbnail.html`). Bitte keine Marke erfinden.

## Harte Regeln (aus dem Auftrag, gelten für jede Ausgabe)

1. Statische Dateien. Plain HTML + CSS mit Custom Properties, minimal Vanilla-JS.
   Kein Build, kein npm, kein Sass, kein Framework.
2. **Keine externen Requests.** Keine CDNs, keine Google-Fonts per `<link>`, kein Analytics.
   Fonts liegen selbst gehostet in `assets/fonts/`.
3. Dark/kontrastreich als feste Optik. Kein Theme-Toggle, kein Light Mode.
4. Video: `preload="metadata"`, Poster, nie Autoplay mit Ton. 1080p streamen, 4K nur Download.
   Die Videodateien liegen serverseitig unter `/videos/…`, nicht im Build.
5. Responsiv 360–2560 px. Kontrast ≥ 4.5:1 im Fließtext, sichtbarer Fokus,
   `prefers-reduced-motion` schaltet Sticker-Bewegung ab, Alt-Texte überall.
6. Ziel: < 1,5 MB pro Seite ohne Video.
7. Nicht erwünscht: Stock-Party-Fotos, Cliparts, Bootstrap-/Tailwind-Default-Look, Emoji als
   Icons, Blink-/Flash-Animationen (Fotosensibilität), Kindergeburtstags-Flyer-Optik.

---

## CONTENT FUNDAMENTALS

**Sprache:** Deutsch, informell, Duzen. Englisch nur in den Marker-Captions, weil das die
Stimme des Posters ist („Good friends, bad decisions", „Same men, different city").

**Tonfall:** trocken, selbstironisch, warm. Der Witz kommt aus dem Understatement, nicht aus
Ausrufezeichen. Nichts wird angepriesen, nichts hat Superlative. Ein Satz darf kurz
abbiegen: *„Es fing so vernünftig an."* / *„Braucht Leitung, Geduld und Platz auf der
Platte."*

**Ich vs. du:** Es gibt kein „wir sind ein Team" und kein Marketing-„Sie". Über die Gruppe
wird in der ersten Person Plural gesprochen („wir sind schon ziemlich alt geworden"), der
Leser wird geduzt („Am besten groß, mit Ton, und nicht im Büro.").

**Casing:** Sätze normal. Display-Zeilen in Bangers erscheinen optisch als Versalien (das
macht die Schrift), werden aber normal geschrieben. Die ruhige Stimme nutzt echte
`text-transform:uppercase` mit `--tracking-caps` — sparsam, nur Kicker, Labels, Ortsangaben.

**Keine Emoji.** Nie, auch nicht im Fließtext. Akzente sind glühende Doodle-Glyphen
(♛ ★ ❤ ✦) im `Sticker`, dekorativ und `aria-hidden`.

**Länge:** Absätze 2–4 Zeilen. Die Landing hat drei Absätze, mehr nicht. Labels 1–3 Wörter.
Buttons 2–4 Wörter, Imperativ („Hier abspielen", „4K-Fassung herunterladen").

**Zahlen und Fakten bleiben vage, wenn sie vage sind:** „ca. 6–7 Minuten", „Wochenende
folgt". Nichts erfinden — offene Inhalte stehen als `<!-- TODO -->` im Markup.

**Beispiele, die den Ton treffen**
- Lead: „Zehn Männer, eine Stadt mit sehr gutem Bier und ein Film, der ungefähr in der Mitte
  die Fassung verliert."
- Hinweis: „Bitte den Link nicht weitergeben — auch nicht ‚nur kurz' in eine andere Gruppe."
- Sektionstitel: „Die Crew", „Der Film", „Streamen oder Laden".
- Kicker: „Sonnenbrille auf, Krone drauf".

---

## VISUAL FOUNDATIONS

**Farbe.** Grundfarbe ist ein sehr dunkles Indigo-Purpur, nie reines Schwarz: `--ink-900`
`#120a2a` als Seite, `--ink-950` `#0d0722` als tiefster Grund, `--ink-800` `#1e1640` als
Basiswert des Briefings. Darüber liegt ein ruhiger Nachtwash (`--grad-night`): violettes
Glühen oben links, pinkes oben rechts — `background-attachment:fixed`, damit die Seite wie
ein Raum wirkt und nicht wie eine Fläche.
**Gold ist die dominante Farbe** (`--gold-500` `#d9a441`, Highlight `#ffcf5c`, Tiefe
`#b07c22`): Titel, Primäraktion, Cast-Namen. Immer als Verlauf `--grad-gold` mit
Textclipping, nie als flaches Gelb.
**Pink/Magenta ist Zweitfarbe** (`--pink-500` `#ff2e8a`): Umgebungsglühen, Hover, Kicker,
sekundäre Aktion.
**Cyan ist ein einzelner Sonderakzent** (`--cyan-500` `#35d6ff`) — im Film das leuchtende
Accessoire einer Person, hier: der Ring des Bräutigams in der `cast-grid` und der
Fokusring. Sonst nirgends.
Weiß existiert nicht; Text ist warmes Cremeweiß `--cream-050` `#fdf6ec`.
Maximal zwei Flächenfarben pro Seite (Nacht + eine Kartenfläche).

**Typografie.** Zwei Familien, zwei Stimmen, beide selbst gehostet:
- **Bangers 400** (`--font-display`) — laut. Titel, Sektionsüberschriften, Cast-Namen,
  Marker-Captions. Zeilenhöhe `.92`, Tracking fast null. Immer mit Gold-Verlauf plus
  Halo (`.shout`) oder in Creme mit hartem dunklen Versatzschatten.
- **Poppins 400/500/600/700** (`--font-body`) — alles zum Lesen. Zeilenhöhe `1.65`,
  Maß 64ch. In Versalien mit `--tracking-caps` (.18em) bzw. `--tracking-caps-wide` (.32em)
  wird Poppins zur *ruhigen* Stimme: Kicker, Meta, `.ruled-caps` mit dünnen Trennlinien
  links und rechts — exakt die Ortsangabe „— BRÜSSEL —" des Posters.
Skala fluid, `--step--1` bis `--step-6` (clamp), Titel bis 9rem.
Der raue Pinsel-/Spray-Look des Posters wird **nicht** mit Webfonts nachgebaut — er kommt
ausschließlich aus Hero-Grafiken mit eingebranntem Text.

**Raster & Layout.** Eine Spalte, mittig, `--page-max` 1180px, Gutter
`clamp(1rem,4vw,3rem)`. Sektionen `padding-block: clamp(3rem,7vw,6rem)`. Textspalten
zentriert auf 64ch. Grids immer `auto-fit`/`minmax`, damit von 360 bis 2560 px nichts bricht
(`cast-grid` minmax 150px, `quality-box` minmax 270px). Fest positioniert ist nur die
Navigation (`position:sticky`, `--z-nav`).

**Hintergründe & Bilder.** Full-Bleed-Standbilder nur im Kopfbereich, `object-fit:cover`,
`object-position:50% 38%` (Gesichter oben halten). Über jedem Bild mit Text liegt eine
Schutz-Abdunklung (`--grad-protect` bzw. der Header-Scrim von .45 → 1.0) — Text steht
niemals ungeschützt auf einem Foto. Bildstimmung: nachtwarm, kräftig gesättigt
(`saturate(1.05–1.15)`), Neon-Reflexe, kein Schwarzweiß, kein Grain-Overlay. Keine
wiederholenden Muster, keine Texturen. Keine gezeichneten SVG-Illustrationen.

**Ecken & Linien.** `--radius-xs` 4 · `sm` 8 · `md` 14 · `lg` 22 · `pill` 999. Karten sind
`md`, Buttons `pill`, Cast-Stempel `pill`. Striche: `--border-hair` 1px (stille Trennung),
`--border-strong` 2px (Karten mit Aussage), `--border-chunky` 4px (nur der Comic-Ring der
Cast-Stempel).

**Karten.** `--surface-card` (Indigo mit 12 % Creme gemischt), 1–2px Rand in
`--border-quiet`, Radius 14px, `--shadow-2`. Keine farbige linke Kante, kein Glas.

**Schatten & Glühen sind zwei getrennte Systeme.** Elevation: `--shadow-1/2/3`, kalt und
tief (`rgb(6 2 20 / …)`). Neon: `--glow-gold/pink/cyan` als Box-Shadow und
`--text-glow-*`/`drop-shadow` für Schrift — immer **dünne Kontur + weicher Halo**, nie eine
flache Leuchtfläche. Glow wird additiv zur Elevation gesetzt, ersetzt sie nicht.

**Transparenz & Blur.** Genau zwei Stellen: die Navigation
(`color-mix(ink-950 82%, transparent)` + `blur(10px) saturate(1.3)`) und die
Veil-Schicht des `PlayTeaser`. Sonst deckende Flächen — Glasoptik überall wäre Default-Look.

**Bewegung.** Sparsam und weich. `--ease-out` `cubic-bezier(.2,.7,.25,1)` für alles Normale,
`--ease-pop` `cubic-bezier(.2,1.5,.4,1)` für den kleinen Übermut (Button-Lift,
Stempel-Kipper). Dauern: 120 / 240 / 600 ms. Die einzige Endlos-Animation ist das
5,5-Sekunden-Schweben der Sticker (`alternate`, ±9px, ±6°). **Kein Blinken, kein Flackern,
kein Autoplay-Motion.** `prefers-reduced-motion` setzt alle Dauern auf ~0.

**Hover.** `translateY(-2…-4px)` plus intensiverer Glow, nie ein Farbwechsel ins Graue.
Links wechseln von Gold zu Pink samt Unterstreichungsfarbe. Der Cast-Stempel hebt sich und
kippt um −2°. **Press:** `translateY(1px) scale(.985)` — die Karte drückt sich rein.
**Disabled:** `opacity .45` + `saturate(.4)`, keine Grautöne.

**Fokus.** Immer sichtbar, immer cyan: `2px solid var(--cyan-400)`, Offset 3px. Cyan, weil es
sowohl auf Gold als auch auf Pink und auf Nacht sicher liest.

---

## ICONOGRAPHY

Es gibt **kein** Icon-Set in den Quellen — keine Icon-Font, kein Sprite, keine SVGs, kein
Logo. Entsprechend gilt hier bewusst:

- **Genau ein echtes Icon** im ganzen System: das Play-Dreieck im `PlayTeaser`, ein inline
  `<path d="M8 5.5v13l11-6.5z">` in einem 24er-Viewbox, `fill:currentColor`. Mehr braucht
  eine Drei-Seiten-Seite nicht.
- **Deko-Akzente sind Unicode-Glyphen in der Display-Schrift**, gesetzt als glühende
  Doodles über `Sticker`: ♛ (Krone), ★ (Stern), ❤ (Herz), ✦ (Funke). Sie sind Dekoration,
  nie Bedeutungsträger — immer `aria-hidden="true"`, nie klickbar. Das ist die Web-Antwort
  auf die Neon-Doodle-Kronen des Posters: dünne Kontur, weicher Glow.
- **Keine Emoji.** Auch nicht als Aufzählungszeichen.
- **Kein CDN-Icon-Set** (Lucide, Heroicons …) — die Regel „keine externen Requests" gilt, und
  ein Stroke-Set würde neben Bangers fremd aussehen. Sollte doch einmal ein Icon nötig
  werden: inline SVG, 24×24, `currentColor`, 2px Strichstärke, runde Enden.
- **Wortmarke statt Logo:** „Micha im Delirium" in Bangers, Gold mit Halo. Wenn ein echtes
  Logo geliefert wird, kommt es nach `assets/logo.svg` und ersetzt `.nav__brand` /
  `.footer__mark` / `thumbnail.html`.

---

## Farbrollen (Kurzreferenz)

| Rolle | Token | Wert |
|---|---|---|
| Seite | `--surface-page` | `#120a2a` |
| Tiefster Grund | `--surface-deep` | `#0d0722` |
| Karte | `--surface-card` | Indigo + 12 % Creme |
| Fließtext | `--text-body` | `#fdf6ec` |
| Meta | `--text-muted` | `#b3a692` |
| Titel/Primäraktion | `--accent-primary` | `#d9a441` |
| Glühen/Hover/Zweitaktion | `--accent-secondary` | `#ff2e8a` |
| Sonderakzent + Fokus | `--accent-special` | `#35d6ff` |

## Index

**Root**
- `styles.css` — Einstiegspunkt, nur `@import`-Zeilen (für Konsumenten dieses Systems).
- `index.html`, `film.html`, `impressum.html` — die drei Seiten der Website (Auslieferung).
- `thumbnail.html` — Kachel des Designsystems.
- `SKILL.md` — Einstieg für Agent-Nutzung.

**CSS** (`assets/css/`, in dieser Reihenfolge einbinden)
`fonts.css` (`@font-face`) → `tokens.css` (System-Tokens) → `theme-jga-2026.css`
(Party-Palette, semantische Rollen) → `base.css` (Reset, Typo, Fokus, Stimmen) →
`components.css` (alle Komponentenklassen).

**Assets**
- `assets/fonts/` — Bangers-Regular, Poppins 400/500/600/700 (TTF) + OFL-Lizenztexte.
- `assets/img/poster.jpg` (Key Art), `hero.jpg` (Landing-Kopf), `film-poster.jpg`
  (Player-Poster), `cast/cast-01…10.jpg` (**Platzhalter**, aus dem Poster geschnitten).

**Komponenten** (React-Spiegel der CSS-Klassen, `components/<gruppe>/`)
- `core/` — **Button**, **Notice**, **Prose**, **Sticker**, **MarkerCaption**
- `site/` — **Nav**, **PageHeader**, **SiteFooter**
- `film/` — **PlayTeaser**, **CastGrid**, **VideoBlock**, **QualityBox**

Jede Komponente hat `.jsx`, `.d.ts` (Props-Vertrag) und `.prompt.md` (wann/wie), plus eine
`*.card.html` je Ordner für die Design-System-Ansicht.

*Intentional additions:* Der Auftrag nennt `page-header`, `cast-grid`, `video-block`,
`quality-box`, `prose`, `sticker`, `notice`, `nav`, `footer`. Zusätzlich gebaut:
**Button** (jede Seite braucht Aktionen; sonst wäre er in vier Dateien kopiert),
**PlayTeaser** (der „große, prominente Player-Button" der Landing als eigene Einheit) und
**MarkerCaption** (die handschriftlichen Rand-Captions des Posters).

**Foundations** (`guidelines/*.html`) — 20 Specimen-Karten: Farben (Nacht, Gold, Pink,
Sonderakzent, Creme, Textrollen, Glow, Verläufe), Typo (Display, Body, ruhige Versalien,
Skala, die zwei Stimmen), Spacing (Skala, Radien, Elevation), Brand (Key Art, Cast-Stempel,
Doodles, Fokus).

## Offen — bitte nicht raten

- **Genaues Datum** des Wochenendes (steht als „Wochenende folgt" im Kicker).
- **Die zehn Namen** und die zehn echten Sonnenbrillen-Fotos. Aktuell: Ausschnitte aus dem
  Referenzposter unter `assets/img/cast/`, Namen als „Name 02"…„Name 10".
- **Musik-Credits**: Interpret/Aufnahme von Vivaldis „L'inverno", exakter
  Pulp-Fiction-Titel, Titel des Outro-Tracks.
- Verantwortlicher (Name, Anschrift, E-Mail) im Impressum.
- Optional: Zahlen für eine spätere „Kuriositäten"-Seite.
- **Schriftdateien:** Bangers und Poppins liegen als **TTF** aus dem offiziellen
  google/fonts-Repository (SIL OFL 1.1) hier. Für die Auslieferung besser als `.woff2`
  subsetten (z. B. mit `fonttools`/`woff2_compress`, Latin + Latin-Extended) und die
  `src`-Zeilen in `assets/css/fonts.css` auf `.woff2` umstellen — spart rund 400 KB.
