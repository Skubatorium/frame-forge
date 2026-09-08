# Prompt für das Design-System — JGA-Website „Micha im Delirium 2026"

> **Verwendung:** Diesen Text vollständig in ein neues Claude-Design-System-Projekt geben
> (z. B. eine eigene Chat-/Design-Session). Der Empfänger hat **keinen Zugriff auf das
> Quell-Repo** — alles Nötige steht hier drin. Rückfluss: siehe „Was ich zurückbekommen
> möchte" am Ende. Vorlage/Vorbild dieses Dokuments: die gleichnamige Datei aus dem
> vorherigen Reiseprojekt (`web/sites/norwegen-2026/design/PROMPT-designsystem.md`) —
> dieselbe Struktur, komplett anderes Thema.

---

## Auftrag in einem Satz

Bau ein eigenständiges, comic-/party-thematisches Design-System und daraus eine
**kleine, private Website**, auf der ein einzelner ~5,5-minütiger Junggesellenabschieds-Film
geschaut und heruntergeladen werden kann.

## Kontext

Ein Freundeskreis (10 Personen) war ein Wochenende in Brüssel für einen
Junggesellenabschied. Der Film hat bewusst zwei Gesichter: ein ruhiger, fast schon
selbstironisch „gediegener" Auftakt (Ankunft, Pizza, Waffeln, Schokolade — „wir sind schon
ziemlich alt geworden") kippt beim Zusammentreffen der ganzen Gruppe in eine laute,
schnelle Partynacht (Kneipentour, Karaoke, Tequila) und klingt danach ruhig aus. Die Seite
ist die kleine Bühne dafür — Link plus Passwort gehen an die ~10 Beteiligten und ein paar
weitere Freunde.

**Umfang bewusst klein halten**, wie beim Vorgängerprojekt: wenige Seiten, ein sauberes
System, ein paar richtig gute Komponenten. Die Energie gehört ins **Aussehen**, nicht in
Technik.

## Gestalterische Richtung

**Es gibt jetzt ein echtes Stilreferenz-Bild** — liegt neben diesem Prompt unter
`design/reference/style-reference-jga-poster.png`. **Gib dieses Bild mit in die
Design-Session**, es ist die verbindlichere Quelle als der Text unten. Kurzbeschreibung
dessen, was den Stil ausmacht:

- **Grundfarbe:** sehr dunkles Indigo-Purpur, leicht ins Blaue (Nachthimmel/Brüssel bei
  Nacht), kein reines Schwarz.
- **Hero-Farbe: warmes Gold** — der Haupt-Schriftzug ist golden mit Verlauf/Glanz, das ist
  die dominanteste Farbe.
- **Zweitfarbe: Neon-Pink/Magenta** — Umgebungsglühen, leuchtende Schilder/Deko im
  Hintergrund.
- **Ein blauer Sonderakzent** taucht gezielt bei einer Person auf (leuchtendes Accessoire) —
  eher ein persönliches Wiedererkennungsmerkmal als eine durchgängige Systemfarbe.
- **Typografische Zweiteilung:** der grobe, raue Haupt-Schriftzug wirkt wie mit dickem
  Pinsel/Graffiti-Spray gemalt (unregelmäßige Kanten, Leuchten) — passend zur lauten
  Partynacht. Eine kleinere Ortsangabe darunter dagegen ruhig, sauber, in einer schlichten
  Versalienschrift mit dünnen Trennlinien — passend zum ruhigeren Auftakt des Films. **Diese
  Zweiteilung darf die Website aufgreifen:** Landing-Hero laut/golden/rau, ruhigere
  Unterseiten-Elemente (z. B. Impressum, Meta-Angaben) in der schlichten Variante.
- **Deko-Elemente:** leuchtend-weiße/goldene Doodle-Kronen, kleine Glitzer-/Herz-Akzente als
  **leuchtende Neon-Doodles** (dünne Konturlinie + weicher Glow-Schatten), nicht als flache
  Cartoon-Symbole. Handschriftliche Rand-Captions in grobem Marker-Stil.

**Hero-Grafiken (Landing-Header, Poster-Bild) dürfen eingebrannten Text enthalten** — anders
als bei generischen Icon-/Logo-Grafiken, weil sich dieser Text-Look (Farbverlauf, Leuchten,
Pinsel-Textur) mit Web-Fonts/Live-Text ohnehin nicht erreichen lässt. Das Referenzbild selbst
ist ein gutes Beispiel für diesen Look und kann als Ausgangspunkt für den Landing-Header
dienen oder direkt (ggf. beschnitten) verwendet werden.

Farbwerte zur Orientierung, **nicht als starre Vorgabe** (abgestimmt mit dem
FrameForge-Designsystem des Videos selbst, Plan 0004 §4.1): `#1e1640` (Basis, Indigo-Purpur),
`#d9a441` (Gold, Hauptakzent), `#ff2e8a` (Pink, Zweitakzent), `#fdf6ec` (warmes Cremeweiß
statt reinem Weiß).

Was nicht passt: generische Stock-Party-Fotos/Cliparts, Bootstrap-/Tailwind-Default-Look,
Emoji als Icons, aggressive Blink-/Flash-Animationen (Fotosensibilität!), alles, was wie ein
Kindergeburtstags-Flyer aussieht statt wie ein Kinoplakat mit Humor.

## Die Seiten

Kleiner Zuschnitt als beim Vorgänger, weil es nur einen Film gibt:

### 1. `index.html` — Landing

- **Ruhiger, kinoplakat-artiger Kopfbereich**: ein starkes Standbild aus dem Film (Vorschlag:
  ein Moment aus Akt 2, Karaoke oder Kneipentour) mit dem Titel **„Micha im Delirium 2026"**
  und einer kurzen Unterzeile (Ort, Wochenende — Datum liefere ich nach).
- **Kurzer Einführungstext**, 2-3 Absätze: worum es ging, die Zweiteilung des Films
  (gediegener Start → Eskalation) als Erzählhaken.
- **Ein großer, prominenter Player-Button/Teaser** zum einzigen Film (kein Zwei-Filme-Raster
  wie beim Vorgänger).
- **„Die Crew"-Sektion** (neue Komponente `cast-grid`, siehe unten): die Sonnenbrillen-Fotos
  der zehn Beteiligten mit Namen, im selben Comic-Stempel-Look wie die Cast-Intro im Film
  selbst — die Website darf diesen Moment aus dem Film aufgreifen und wiederholen.
- Footer mit Weitergabe-Hinweis (Text analog zum Vorgängerprojekt, sinngemäß: privat, Link
  nicht weitergeben, Zugang auf Nachfrage) und Link zum Impressum.

### 2. `film.html` — der Film

- Player (`<video controls preload="metadata" poster>`), 16:9, groß, zentriert.
- **Fassungs-Box** (`quality-box`, wie beim Vorgänger): Streaming 1080p vs. Download 4K,
  klar gegenübergestellt, mit Leitungshinweis bei der 4K-Fassung.
- Kurzer Text zu Aufbau/Musik des Films (zwei Songs, zwei Stimmungen — ohne zu viel zu
  verraten, es soll ja noch überraschen).
- Musik-Credits (Titel folgen, siehe „Was noch fehlt" unten).

### 3. `impressum.html`

Wie beim Vorgänger: Verantwortlicher, privater/nicht-kommerzieller Hinweis, Musiklizenzen,
Schriftlizenzen, kurzer Datenschutzabsatz.

*(Eine optionale vierte Seite „Kuriositäten" — Anzahl Kneipen/Biere/Tequila-Shots o.ä. als
augenzwinkernde Zahlen, analog zum `fun-facts`-Block des Vorgängerprojekts — ist möglich,
sobald die Zahlen feststehen. Nicht Teil des ersten Entwurfs.)*

## Komponenten

| Komponente | Zweck |
|---|---|
| `page-header` | ruhiger, kinoplakat-artiger Kopfbereich (Landing) |
| `cast-grid` | **neu** — Sonnenbrillen-Fotos + Namen im Comic-Stempel-Look, rasterartig |
| `video-block` | Player + Info-Panel |
| `quality-box` | Streaming-/Download-Fassung gegenübergestellt (wie Vorgänger) |
| `prose` | Textabschnitt, gute Lesbarkeit trotz verspieltem Umfeld |
| `sticker` | dezentes Deko-Element (Herzchen/Stern), CSS-basiert, kein Bild pro Instanz nötig |
| `notice` | dezenter Hinweiskasten (Weitergabe-Hinweis) |
| `nav` + `footer` | Navigation über die drei Seiten |

## Technische Regeln (hart, wie beim Vorgängerprojekt)

- **Statische Dateien.** Plain HTML + CSS mit Custom Properties, minimal Vanilla-JS. Kein
  Build, kein npm, kein Sass, kein Framework.
- **Keine externen Requests.** Keine CDNs, keine Google-Fonts-Einbindung per `<link>` (Fonts
  selbst hosten, siehe unten), kein Analytics.
- Läuft unter **https://micha-jga.skubus.de** hinter Basic Auth auf Infrastruktur-Ebene
  (Traefik) — die Website selbst baut dafür nichts ein.
- **Schrift selbst gehostet.** Empfehlung (siehe auch FrameForge-Designsystem-Vorschlag,
  Plan 0004 §4.3): **Bangers** für Titel/Headlines/Cast-Namen (Comic-Lettering — bildet
  die Pinsel-/Graffiti-Textur des Referenzbilds nicht 1:1 nach, das übernehmen die
  Hero-Grafiken mit eingebranntem Text, siehe oben), **Poppins** für Fließtext (bleibt
  lesbar, in Versalien mit Buchstabenabstand auch für die ruhigere Unterseiten-Optik
  nutzbar). Beides freie Google Fonts — als `.woff2` selbst hosten, nicht per Google-CDN
  einbinden (Regel oben). Dateien besorge ich.
- Video: `preload="metadata"`, Poster-Bild, nie Autoplay mit Ton. Streaming 1080p,
  4K nur Download.
- Responsiv 360-2560 px. Dark/kontrastreiche Grundstimmung als feste Optik, kein Toggle.
- Barrierefreiheit: Kontrast ≥ 4.5:1 im Fließtext trotz kräftiger Farben, sichtbarer Fokus,
  `prefers-reduced-motion` (Sticker-/Rotations-Animationen dann aus), Alt-Texte.
- Ziel: unter ~1,5 MB pro Seite ohne Video.

## Dateipfade, die ich brauche

```
index.html  film.html  impressum.html
assets/css/tokens.css                    System-Tokens
assets/css/theme-jga-2026.css            Party-Tokens (Farbe, Comic-Font-Einsatz)
assets/css/base.css
assets/css/components.css
assets/fonts/…                           woff2 (Bangers, Poppins)
assets/img/hero.jpg                      Kopfbereich Landing
assets/img/cast/<name>.jpg               Sonnenbrillen-Fotos, ×10 — Namen liefere ich nach
assets/img/film-poster.jpg               Poster für den Player
```

Videopfad wie beim Vorgänger separat auf dem Server, nicht im Website-Build:

```html
<video src="/videos/jga-2026-1080p.mp4" poster="assets/img/film-poster.jpg" …></video>
<a href="/videos/jga-2026-4k.mp4" download>4K-Fassung herunterladen</a>
```

## Was noch fehlt (bewusst offen, nicht raten)

- **Genaues Datum** des Wochenendes.
- **Die zehn Namen** für die `cast-grid` (und die zehn Sonnenbrillen-Fotos selbst).
- **Musik-Credits**: Vivaldi „L'inverno" (Interpret/Aufnahme), exakter Pulp-Fiction-
  Songtitel, Titel des dritten Outro-Tracks.
- Optional: Zahlen für eine spätere Kuriositäten-Seite (Kneipen, Getränke, Karaoke-Songs …).

## Was ich zurückbekommen möchte

1. `tokens.css` (System-Tokens), `theme-jga-2026.css` (Party-Palette).
2. `base.css` + `components.css`.
3. Die drei HTML-Seiten mit Platzhaltern an den genannten Pfaden.
4. Kurze Design-Dokumentation (Prinzipien, Farbrollen, Komponentenübersicht).
5. Font-Dateien/Bezugsquelle (Bangers + Poppins, beide Google Fonts, Lizenz notieren).

Bitte Dateien, keine Screenshot-Mockups.

## Wenn dir etwas fehlt

Frag, statt zu raten — besonders bei den noch offenen Inhalten oben.
