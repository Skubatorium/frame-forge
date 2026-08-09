# Prompt für das Design-System — Reise-Website „Norwegen 2026"

> **Verwendung:** Diesen Text vollständig in ein neues Claude-Design-System-Projekt geben.
> Der Empfänger hat **keinen Zugriff auf das Quell-Repo** — alles Nötige steht hier drin.
> Rückfluss: siehe „Was ich zurückbekommen möchte" am Ende.

---

## Auftrag in einem Satz

Bau ein eigenständiges, thematisch norwegisches Design-System und daraus eine
**fünfseitige, private Familien-Website**, auf der zwei fertige Reisefilme geschaut und
heruntergeladen werden können.

## Kontext

Eine Familie (2 Erwachsene + Sohn, 6 Jahre) war 18 Tage in Norwegen. Daraus sind zwei Filme
entstanden: ein 18-minütiger Roadtrip-Vlog und ein 9,5-minütiger reiner Drohnenfilm. Die
Seite ist die kleine Premierenbühne dafür — Link plus Passwort gehen an ~10–15 Menschen aus
Familie und Freundeskreis.

**Umfang bewusst klein halten.** Das soll kein Portfolio-Stück werden. Fünf Seiten, ein
sauberes Farbsystem, gute Typografie, ein paar gut gemachte Komponenten — fertig. Lieber
wenige Dinge richtig als viele Ideen halb.

Die Energie gehört ins **Aussehen**, nicht in Technik: es soll beim Öffnen kurz „oh, schön"
machen und dann aus dem Weg gehen.

## Gestalterische Richtung

**Norwegen als Thema, nicht als Klischee.** Was passt: die Farbwelt des Landes — tiefes
Fjordblau, Gletschertürkis, Granitgrau, Moos- und Kieferngrün, dazu das warme Licht der
Mitternachtssonne als Akzent. Die norwegische Flagge (Rot / Weiß / Marineblau) darf
vorkommen, aber als präzises kleines Element (Favicon, Trenner, Akzentmarke) — nicht als
wehendes Banner über die halbe Seite.

Was nicht passt: Trolle, Wikingerhelme, Runenschriften, Elch-Silhouetten, verschnörkelte
„nordische" Deko-Schriften.

**Grundstimmung dunkel und cineastisch.** Das Material sind 4K-Aufnahmen von Fjorden,
Hochebenen und Gletscherflüssen — die liefern die Farbe, das Interface tritt zurück. Denk an
die Umgebung eines guten Videoplayers: dunkler Grund, viel Luft, wenige präzise Akzente.

Ausdrücklich unerwünscht: Bootstrap-/Tailwind-Default-Look, Schlagschatten auf allem, Emoji
als Icons, Ganzseiten-Verläufe, Parallax-Gewaber, animierte Zähler, Cookie-Banner-Ästhetik.

Zur Orientierung, **nicht als Vorgabe**: Die Filme selbst verwenden ein sehr dunkles Blaugrün
(`#12222f`), gedecktes Petrol (`#2c4a5a`) und warmes Sandgold (`#e0a458`) für ihre wenigen
Bauchbinden. Wenn die Seite daran anknüpft, entsteht ein Zusammenhang — aber die Website
braucht ein **eigenes, reichhaltigeres System**. Die Filme haben faktisch kein Design, nur
Textfarben. Du hast hier freie Hand und sollst sie nutzen.

## Die fünf Seiten

### 1. `index.html` — Landing

- **Hero-Banner mit rotierenden Szenen.** Das Kernstück: 4–6 großformatige Standbilder aus
  den Filmen (Fjord, Trollstigen, Hochebene, Schärenküste …), die langsam ineinander
  überblenden — ruhig, ca. 6–8 s pro Bild, weiche Blende, gern mit sehr langsamem Ken-Burns.
  Darüber der Titel **„Norwegen 2026"**, darunter „18 Tage · 3.829 km · zwei Filme". Reines
  CSS wenn möglich, sonst ein paar Zeilen Vanilla-JS. Muss `prefers-reduced-motion`
  respektieren (dann Standbild statt Rotation).
- **Kurzer Einführungstext**, 2–3 Absätze: worum es ging, wie die Reise aufgebaut war (Basis
  bei Freunden in Skien, dazwischen ein zehntägiger Roadtrip), was die zwei Filme
  unterscheidet.
- **Zwei Teaser-Karten** für die Filme — großes Standbild, Titel, Länge, ein Satz, Button.
  Das ist der wichtigste interaktive Moment der Seite, entsprechend gut gestalten.
- **Kleine Kennzahlen-Leiste** (Zeitraum, Kilometer, höchster Punkt, Reisetage) mit Link
  auf die Fakten-Seite.
- Footer mit Weitergabe-Hinweis (siehe unten) und Link zum Impressum.

### 2. `film-vlog.html` — „Roadtrip"

- Schmaler Kopfbereich (kein Vollbild-Hero), Titel + Kerndaten.
- **Vorspann-Text:** worum es in diesem Film geht, wie er aufgebaut ist, was ihn ausmacht.
- **Der Player**: HTML5-`<video controls preload="metadata" poster>` in 16:9, groß, zentriert.
- **Darunter zwei Blöcke:** „Über den Film" (Dramaturgie, Musik, Kartenanimation) und
  „Technisches" (Länge, Auflösung, verwendete Aufnahmen).
- **Download-Bereich:** die 4K-Fassung als expliziter Download-Button mit Größenangabe und
  einem Satz Warnung, dass das eine große Datei ist.
- Navigation zum anderen Film und zurück.

### 3. `film-drone.html` — „Drone Edit"

Gleicher Bautyp, eigener Charakter: reduzierter, dunkler, mehr Luft — der Film ist textfrei
und ruhig, die Seite spiegelt das.

Inhaltliche Besonderheit: es war die **erste Reise mit der Drohne überhaupt** (DJI Lito X1
mit RC2-Fernsteuerung und Fly-More-Paket). Erstflüge über Fjord, Hochebene, Schärenküste.
Ein Tag fehlt bewusst: in Aurland hat es geregnet, die Drohne blieb unten.

### 4. `fakten.html` — „Zahlen & Fakten"

Die verspielteste Seite. Aufgebaut aus Blöcken:

- **Kennzahlen-Raster** (siehe Faktenteil unten) — groß gesetzte Zahlen, kleine Labels.
- **Die Karte:** ein Kartenbild des Roadtrip-Rundkurses mit Bildunterschrift, die klarstellt,
  dass nur der norwegische Rundkurs zu sehen ist (die Anreise durch Deutschland, Dänemark und
  über die Fähre kommt dazu). Dazu ein Link „in Google Maps öffnen". **Kein eingebettetes
  Maps-iframe** — das wäre ein externer Request, siehe technische Regeln.
- **Die Route in Textform** — Anreise, Rundkurs, Rückreise als kompakte Stationsliste.
- **Die Drohne** — kleiner Technik-Block.
- **Kuriositäten** — die augenzwinkernden Zahlen. Eigene Optik, gern etwas lockerer als der
  Rest der Seite.

### 5. `impressum.html`

Schlicht, textlastig, gleiche Grundgestaltung. Inhalt liefere ich selbst — bau die Seite mit
Platzhaltern für: Verantwortlicher (Name, Anschrift, E-Mail), Hinweis auf den privaten,
nicht-kommerziellen Charakter, Musiklizenzen der Filme, Kartenmaterial (Google Maps),
Schriftlizenzen, kurzer Datenschutzabsatz (keine Cookies, kein Tracking, nur Server-Logs).

## Weitergabe-Hinweis (in den Footer aller Seiten)

Sinngemäß, gern besser formuliert:

> Diese Seite ist privat. Bitte gib Link und Passwort nicht weiter — auf den Bildern sind
> Menschen zu sehen, die nicht gefragt wurden, und jeder Abruf kostet Serverdaten. Soll
> jemand sie sehen: sag Bescheid, ich schicke den Zugang.

Ruhig und beiläufig gestalten. Kein rotes Warndreieck, keine Alarm-Optik — es ist eine Bitte,
kein Compliance-Banner.

## Komponenten

Als benannte, dokumentierte Bausteine, jeweils Markup + CSS + kurze Anwendungsnotiz:

| Komponente | Zweck |
|---|---|
| `hero-rotator` | Vollbild-Hero mit überblendenden Szenen, Titel-Overlay |
| `page-header` | schmaler Kopf für die Unterseiten |
| `stat-grid` | Kennzahlen-Raster (Zahl groß, Label klein) |
| `film-card` | Teaser-Karte für einen Film |
| `video-block` | Player + Info-Panel + Download-Button |
| `prose` | Textabschnitt, ~65–75 Zeichen Zeilenlänge |
| `map-figure` | Kartenbild, Bildunterschrift, externer Link |
| `fact-list` | Stationsliste / Aufzählung mit Struktur |
| `fun-facts` | die kuriosen Zahlen, lockerere Optik |
| `button` | primär / sekundär / Download, inkl. Zuständen |
| `nav` + `footer` | Navigation über fünf Seiten, Footer mit Hinweis |
| `notice` | dezenter Hinweiskasten |

## Technische Regeln (hart)

- **Statische Dateien.** Plain HTML + CSS mit Custom Properties, minimal Vanilla-JS. Kein
  Build, kein npm, kein Sass, kein Framework.
- **Keine externen Requests, ausnahmslos.** Keine CDNs, keine Google Fonts, kein Maps-iframe,
  kein Analytics. Einziger erlaubter Außenkontakt: ein anklickbarer Google-Maps-Link.
  Die Seite läuft hinter nginx Basic Auth auf einem kleinen VPS.
- **Schrift selbst gehostet.** Die Filme nutzen Avenir Next (Apple-Systemschrift, darf nicht
  auf den Server). Empfiehl eine frei lizenzierte Alternative — Display mit Charakter, Text
  ruhig und gut lesbar — mit Familie, Schnitten, woff2 und Lizenz. Dateien besorge ich.
- **Videos sind sehr groß.** `preload="metadata"`, Poster-Bild, niemals Autoplay mit Ton,
  nie beide Filme gleichzeitig laden. Gestreamt wird 1080p, die 4K-Fassung ist reiner
  Download.
- **Responsiv** 360–2560 px. Am Handy wird gelesen, am großen Monitor geschaut.
- **Dark ist die Grundstimmung**, kein umschaltbarer Modus.
- **Barrierefreiheit** im vernünftigen Rahmen: Kontrast ≥ 4.5:1 im Fließtext, sichtbarer
  Fokus, `prefers-reduced-motion`, sinnvolle Alt-Texte, semantisches Markup,
  `<track>`-Platzhalter für spätere Untertitel.
- **Ziel: unter ~1,5 MB pro Seite** ohne Video. `loading="lazy"` unterhalb des Folds.

## Wiederverwendbarkeit

Zu jedem Reiseprojekt soll später eine eigene Website gehören (Malediven, Schottland, …) —
jeweils **thematisch eigenständig**, aber nach demselben Bauplan. Trenne deshalb sauber:

- **System** (Abstände, Typo-Skala, Radien, Motion, Komponenten-Struktur, Seitenaufbau) —
  bleibt über alle Reisen gleich.
- **Thema** (Palette, Schriftwahl, Hero-Bilder, Akzentmotiv) — pro Reise ausgetauscht, in
  einer eigenen Datei `theme-norwegen-2026.css`.
- **Inhalt** steht im HTML.

Beschreib knapp, welche Dateien man für eine neue Reise anfasst und welche nie.

---

# Die Inhalte

## Reise-Eckdaten

| | |
|---|---|
| Zeitraum | Sa 18.07. – Di 04.08.2026 (Verladen am Vorabend, 17.07.) |
| Dauer | 18 Tage |
| Reisende | 2 Erwachsene + Sohn (6) |
| Fahrzeug | SEAT Leon ST mit Dachbox |
| Gesamtstrecke | ca. 3.829 km, davon ca. 325 km auf zwei Fährüberfahrten |
| Roadtrip-Rundkurs | 23.07. – 01.08., 1.319 km ab/bis Skien (22 h 31 min reine Fahrzeit) |
| Basis | bei Freunden in Skien, Telemark |
| Höchster Punkt | Valdresflye, 1.183 m |
| Tiefster Punkt | Meereshöhe — Fjord- und Küstenetappen (Nærøyfjord, Schärenküste) |
| Höhenunterschied | rund **1.180 m** zwischen tiefstem und höchstem Punkt der Reise; Start in Grevenbroich liegt auf ca. 40 m |
| Längster Tag | 1.052 km am Rückreisetag |

Weitere Höhenmarken für die Fakten-Seite: Trollstigen 702 m · Aurlandsfjellet-Pass 506 m ·
Stegastein 639 m · Hakkesetstølen (Unterkunft Geilo) 1.041 m · Valdresflye 1.183 m.

Der **kumulierte Aufstieg (~26.900 m)** gehört *nicht* in diese Eckdaten, sondern in die
Kuriositäten — er ist eine technische Rechengröße, keine anschauliche Reiseangabe.

## Die Route

**Anreise:** Grevenbroich → Hamburg → Flensburg → Hirtshals (DK) → Fähre Color Line über das
Skagerrak → Larvik (N) → Skien.

**Roadtrip-Rundkurs ab Skien:** Heddal Stabkirche → Geilo (Hakkesetstølen, 1.041 m) →
Aurlandsfjellet / Stegastein → Aurland & Flåm → Nærøyfjord & Gudvangen → Lærdalstunnel →
Laukifossen & Loen → Geiranger → Gudbrandsjuvet → Trollstigen (702 m) → Lom → Valdresflye
(1.183 m) → Uvdal → Notodden → zurück nach Skien.

**Rückreise:** Skien → Larvik → Fähre nach Hirtshals → quer durch Dänemark → Hamburg →
Grevenbroich, ohne Zwischenübernachtung durchgefahren.

Maps-Link für den Rundkurs (nur dieser Teil, Google Maps erlaubt maximal zehn Wegpunkte):

```
https://www.google.com/maps/dir/Tiedemannsjordet+16,+3727+Skien,+Norwegen/Hakkesetvegen+73,+3580+Geilo,+Norwegen/Bj%C3%B8rgavegen+23,+5745+Aurland,+Norwegen/Laukifossen,+Oldeelva,+Stryn,+Norwegen/Geirangervegen+200+moh,+Fv63+14,+6216+Geiranger,+Norwegen/Trollstigen,+6300+%C3%85ndalsnes,+Norwegen/Nordal+tourist+center,+Riksvei+15+79,+2686+Fossbergom,+Norwegen/Uvdalsvegen+966,+3632+Uvdal,+Norwegen/Stabkirche+Heddal,+Heddalsvegen+412,+3676+Notodden,+Norwegen/Tiedemannsjordet+16,+3727+Skien,+Norwegen
```

Das Kartenbild liegt vor (Google-Maps-Screenshot des Rundkurses, quer, ca. 2276 × 1844 px) und
kommt als `assets/img/route-map.jpg` in die Seite.

## Höhepunkte (Textmaterial für Landing und Fakten)

Fähre über das Skagerrak · Heddal Stabkirche, die größte Stabkirche Norwegens ·
Panoramastraße Aurlandsfjellet und die Plattform **Stegastein**, 650 m über dem Aurlandsfjord ·
**Flåmsbana**: 20,2 km, 864 Höhenmeter, 55 ‰ Steigung, 20 Tunnel — die steilste
Normalspurbahn Nordeuropas · **Nærøyfjord**, UNESCO-Welterbe, mit dem Elektroboot ·
Wikingerdorf Viking Valley in Gudvangen · **Lærdalstunnel**, 20 km durch den Berg ·
Wasserfall Laukifossen · **Geirangerfjord**, ebenfalls UNESCO-Welterbe, per RIB-Safari zu den
„Sieben Schwestern" · **Trollstigen**, elf Haarnadelkurven auf 702 m · Stabkirche Lom ·
Passstraße Valdresflye über die Hochebene · Angeln an der Schärenküste bei Langesund.

## Kuriositäten (für den `fun-facts`-Block)

- **1 Fisch** — gefangen an der Schärenküste, vom Sechsjährigen, winzig. Der einzige der
  ganzen Reise.
- **1.181 Aufnahmen** gesichtet, knapp **4 Stunden** Rohvideo. In die Filme geschafft haben
  es 167 bzw. 78 Einstellungen.
- **20 km** am Stück unter einem Berg (Lærdalstunnel) — das einzige Foto der Reise ohne
  GPS-Daten, weil es dort keinen Empfang gibt.
- **1 Geburtstag** unterwegs gefeiert, in Geiranger, mit Schlauchboot statt Kuchen.
- **1 Regentag ohne Drohne** — in Aurland blieb sie unten. Deshalb fehlt dieser Tag im
  Drohnenfilm komplett.
- **1 Freundschaft ohne gemeinsame Sprache** — der Sohn lernte in Uvdal einen norwegischen
  Jungen kennen; verständigt wurde sich mit Händen und Füßen, gelehrt wurde Angeln.
- **11 Haarnadelkurven** am Trollstigen.
- **26.900 Höhenmeter** kumulierter Aufstieg über die Gesamtstrecke — dreimal auf den Mount
  Everest, nur bequemer. (Rechengröße aus dem GPS-Höhenprofil, kein Tachowert.)
- **2 Fährüberfahrten** über das Skagerrak, je etwa dreieinhalb Stunden.
- **1 bewusst falsche Route** — der Rückweg von Uvdal ging nicht über die schnelle Strecke
  bei Kongsberg, sondern eine Viertelstunde länger über Notodden. Weil schöner.

## Film 1 — „Norwegen 2026 · Roadtrip" (`film-vlog.html`)

- **18:00 min**, 3840 × 2160 bei 30 fps
- Chronologisch über alle 18 Tage, 167 ausgewählte Einstellungen aus 1.181 Aufnahmen
- Durchgehend eine mitlaufende Karte unten rechts: aktueller Ort, gefahrene Gesamtstrecke
- Beginnt mit einem stillen Cold Open — nur Wind, während die Route auf der Karte wächst
- Dreiteilig entlang dreier Musikstücke, die ineinander überblenden
- Text nur für Datum und Etappe, sonst textfrei
- Streaming-Fassung 1080p (~1,3 GB), Download-Fassung 4K (6,8 GB)

## Film 2 — „Norwegen 2026 · Drone Edit" (`film-drone.html`)

- **9:28 min**, 3840 × 2160 bei 30 fps
- 78 reine Drohnenaufnahmen, chronologisch, ohne Karte, ohne Text
- Ruhige, epische Bildsprache: lange Einstellungen, langsame Bewegungen, Schwarzblenden am
  Anfang und Ende
- Zwei Musikstücke, fließend ineinander
- Drohne: **DJI Lito X1** mit RC2-Fernsteuerung und Fly-More-Paket — die erste Reise mit ihr
- Streaming-Fassung 1080p (~0,7 GB), Download-Fassung 4K (5,4 GB)

---

## Dateipfade, die ich brauche

Bau die Seiten gegen genau diese Pfade — die Dateien liefere ich nach:

```
assets/css/tokens.css                 System-Tokens
assets/css/theme-norwegen-2026.css    Reise-Tokens
assets/css/base.css
assets/css/components.css
assets/fonts/…                        woff2
assets/img/hero-01.jpg … hero-06.jpg  Hero-Rotation
assets/img/route-map.jpg              Kartenbild
assets/img/teaser-vlog.jpg            Teaser-Karte Landing
assets/img/teaser-drone.jpg           Teaser-Karte Landing
video/vlog-edit-1080p.mp4             Stream
video/vlog-edit-4k.mp4                Download
video/vlog-edit-poster.jpg
video/drone-edit-1080p.mp4            Stream
video/drone-edit-4k.mp4               Download
video/drone-edit-poster.jpg
```

## Was ich zurückbekommen möchte

1. **`tokens.css`** — System-Tokens als Custom Properties (Farbrollen, Typo-Skala, Abstände,
   Radien, Schatten, Motion, Breakpoints), kommentiert.
2. **`theme-norwegen-2026.css`** — die norwegische Palette und Themen-Tokens.
3. **`base.css` + `components.css`** — Reset/Grundlayout und die Komponenten von oben.
4. **Die fünf HTML-Seiten**, fertig, mit den echten Inhalten aus diesem Dokument und
   Platzhaltern an den genannten Pfaden.
5. **Design-Dokumentation** (Markdown): Prinzipien, Farbrollen, Typo-Skala,
   Komponentenübersicht mit Anwendungsregeln, Abschnitt „so entsteht die nächste Reise-Seite".
6. **Font-Empfehlung** mit Lizenz und Bezugsquelle.
7. **Bildliste**: welche Bilder in welchen Maßen und Seitenverhältnissen gebraucht werden,
   mit den erwarteten Dateinamen. Ich schneide sie aus dem Filmmaterial zu.

Bitte Dateien, keine Screenshot-Mockups — das Ergebnis geht direkt auf den Server.

## Wenn dir etwas fehlt

Frag, statt zu raten — besonders bei Inhalten, Bildmotiven oder gestalterischen
Entscheidungen, die du für begründungsbedürftig hältst.
