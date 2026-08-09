# Prompt für das Design-System — „Reise-Mini-Site" (Pilot: Norwegen 2026)

> **Verwendung:** Diesen Text vollständig in ein neues Claude-Design-System-Projekt geben.
> Der Empfänger hat **keinen Zugriff auf dieses Repo** — alles Nötige steht hier drin.
> Erwarteter Rückfluss: siehe Abschnitt „Was ich zurückbekommen möchte".

---

## Rolle und Auftrag

Du baust ein **kleines, in sich geschlossenes Design-System für private Reise-Mini-Websites**.
Der Pilot ist eine Norwegen-Roadtrip-Seite für Familie und Freunde. Es sollen später weitere
Seiten desselben Bautyps entstehen (eine pro Reise), deshalb: **Design-System zuerst,
Norwegen als erste Ausprägung** — nicht umgekehrt. Reise-spezifische Farben und Bilder müssen
über Tokens austauschbar sein, ohne dass die Komponenten angefasst werden.

Kein Framework, kein Build-Schritt, keine externen Requests: **statisches HTML + CSS**, ein
paar Zeilen Vanilla-JS wo unvermeidbar. Die Seite liegt später auf einem kleinen VPS hinter
nginx Basic Auth. Fonts, Bilder, Videos, Icons — alles lokal. Kein CDN, kein Google Fonts,
kein Analytics, kein Tracking. Das ist eine harte Anforderung, keine Präferenz.

## Zielgruppe und Ton

Zuschauer sind ~5–15 Menschen: Familie, Freunde, die Freunde in Norwegen. Sie bekommen Link
und Passwort per Nachricht. Der Ton ist **persönlich, aber nicht kitschig** — es ist eine
kleine Filmpremieren-Seite, keine Reise-Influencer-Landingpage. Kein Marketing-Sprech, keine
Buttons namens „Jetzt entdecken", keine Social-Icons, keine Newsletter-Box, keine
Cookie-Banner-Optik.

## Gestalterische Richtung

Modern, ruhig, **cineastisch-dunkel**. Das Material (4K-Drohnenaufnahmen von Fjorden,
Hochebenen, Gletscherflüssen) soll die Farbe liefern, das Interface tritt zurück. Denk an das
Umfeld eines guten Videoplayers: dunkler Grund, großzügige Weißräume, wenige, präzise
gesetzte Akzente, viel Typografie-Disziplin.

Ausdrücklich **nicht** erwünscht: generisches Bootstrap-/Tailwind-Default-Aussehen, Karten mit
Schlagschatten überall, Emoji als Icons, Verläufe über die ganze Seite, wabernde
Parallax-Effekte, animierte Zähler, Glassmorphism als Selbstzweck.

Die Filme selbst sind bereits nach einem Video-Designsystem gebaut. Übernimm dessen Tokens als
Ausgangspunkt, damit Seite und Film als eine Sache wirken:

```
primary   #12222f   (sehr dunkles Blaugrün-Blau — Grundfläche)
secondary #2c4a5a   (gedecktes Petrol — Flächen zweiter Ordnung, Ränder)
accent    #e0a458   (warmes Sandgold — Akzent, sparsam)
text      #ffffff
Schrift im Film: Avenir Next (Display und Text)
```

Avenir Next ist eine System-/Lizenz-Schrift von Apple und darf nicht mit auf den Server. Such
eine **frei lizenzierte, selbst hostbare Alternative** (Empfehlung willkommen, z. B. aus der
Inter-/Söhne-/Grotesk-Ecke für Text und etwas mit mehr Charakter für Display) und begründe
die Wahl kurz. Ich lade die Dateien selbst herunter — nenn mir Familie, Schnitte, Formate
(woff2) und die Lizenz.

Die Akzentfarbe darf pro Reise wechseln (Norwegen = Sandgold). Bau das so, dass eine künftige
Seite nur einen Token-Block tauscht.

## Aufbau: zwei Seiten

### Seite 1 — Start / „Der Vlog"

1. **Header / Hero.** Ganzflächiges Standbild oder kurze Videoschleife, darüber der Titel
   „Norwegen 2026". Dezente Abdunklung, damit Text lesbar bleibt. Darunter eine schmale
   Faktenzeile: Zeitraum, Dauer, Strecke, Reisende.
2. **Teaser / Intro.** Zwei bis drei Absätze: worum es ging, wie die Reise aufgebaut war
   (Basis bei Freunden in Skien, dazwischen ein zehntägiger Roadtrip), was die zwei Filme
   unterscheidet.
3. **Streckenübersicht.** Ein Kartenbild (statisches Bild, kein eingebettetes Google Maps —
   das würde externe Requests bedeuten) mit den Etappenpunkten, dazu die harten Zahlen und
   optional ein Link „in Google Maps öffnen" für die, die es interaktiv wollen.
4. **Der Film.** HTML5-`<video>`, 16:9, groß, mit Poster-Bild. Daneben/darunter ein
   Info-Block: Länge, Auflösung, worum es im Film geht, wie er dramaturgisch aufgeteilt ist,
   Musik. Zusätzlich ein dezenter Download-Hinweis (4K-Fassung).
5. **Roadtrip-Log / Tagebuch.** Die 18 Reisetage als Liste. Pro Tag: Datum, Etappe
   (von → nach), Kilometer, ein bis drei Sätze, was passiert ist, optional ein kleines Bild.
   Das ist der längste Abschnitt der Seite — er braucht ein Muster, das 18-mal funktioniert,
   ohne zu ermüden: Zeitstrahl, Tageskarten, aufklappbare Einträge o. ä. Schlag eine Lösung
   vor und begründe sie. Wichtig: auf dem Handy muss das noch angenehm lesbar sein.
6. **Verweis auf Seite 2** (Drone Edit) als eigener, bildstarker Block.
7. **Footer** mit dem Hinweis zur Weitergabe (siehe unten).

### Seite 2 — „Drone Edit"

Gleicher Bautyp, eigener Charakter: reduzierter, dunkler, mehr Luft — der Film ist textfrei
und ruhig, die Seite sollte das spiegeln.

1. Hero mit dem Drone-Edit-Titelbild.
2. Kurztext: reiner Drohnenfilm, keine Karte, keine Bauchbinden; Bildsprache ruhig und
   episch. Erwähnt wird, dass es **die erste Reise mit der Drohne überhaupt** war — also
   Erstflüge über Fjord, Hochebene und Schärenküste, mit allem, was dazugehört.
3. Technik-Block: Drohne DJI Lito X1 mit RC2-Fernsteuerung und Fly-More-Paket, 4K.
4. Der Film (gleiche Player-Komponente wie Seite 1).
5. Rückverweis auf Seite 1, gleicher Footer.

## Komponenten, die ich brauche

Bitte als benannte, dokumentierte Bausteine — jeweils Markup + CSS + kurze Anwendungsnotiz:

- `hero` — vollflächig, Bild oder Video-Loop, Titel, Untertitel, Overlay-Abdunklung
- `fact-strip` — Zeile mit 3–5 Kennzahlen (Zahl groß, Label klein)
- `prose` — Textabschnitt, angenehme Zeilenlänge (~65–75 Zeichen), klare Hierarchie
- `video-player` — `<video controls preload="metadata" poster>` in 16:9, plus Info-Panel
- `map-figure` — Kartenbild mit Bildunterschrift und optionalem externem Link
- `day-log` — das Tagebuch-Muster (18 Einträge)
- `gallery` — kleine Bildstrecke, 3–8 Bilder, klickvergrößerbar ohne Lightbox-Bibliothek
- `cta-card` — der bildstarke Verweis zwischen den beiden Seiten
- `nav` — minimale Navigation zwischen den zwei Seiten
- `footer` — inklusive Weitergabe-Hinweis
- `notice` — dezenter Hinweiskasten für ebendiesen Text

## Weitergabe-Hinweis (muss auf beide Seiten)

Sinngemäß, gerne in bessere Worte gefasst:

> Diese Seite ist privat. Bitte gib Link und Passwort nicht weiter — auf den Bildern sind
> Menschen zu sehen, die nicht gefragt wurden, und jede Ansicht kostet Serverdaten. Wenn
> jemand sie sehen soll: sag mir Bescheid, ich schicke den Zugang.

Gestalterisch: ruhig und beiläufig, kein rotes Warndreieck, keine Alarm-Optik. Es ist eine
Bitte, kein Compliance-Banner.

## Technische Rahmenbedingungen

- **Nur statische Dateien.** `index.html`, `drone.html`, `assets/css/`, `assets/img/`,
  `assets/fonts/`, `video/`. Keine Buildpipeline, kein npm, kein Sass — plain CSS mit Custom
  Properties.
- **Keine externen Requests, ausnahmslos.** Der einzige erlaubte Link nach außen ist ein
  anklickbarer Google-Maps-Link, den der Nutzer bewusst öffnet.
- **Videos sind sehr groß** (mehrere hundert MB bis GB). Also: `preload="metadata"`,
  Poster-Bild als JPEG/WebP, niemals Autoplay mit Ton, kein automatisches Laden beider Filme.
- **Responsiv** von 360 px bis 2560 px. Auf dem Handy wird das Log gelesen, am großen Monitor
  der Film geschaut — beide Fälle müssen gut sein.
- **Dark ist die Grundstimmung**, nicht ein Modus. Ein Light-Theme ist nicht nötig; wenn du
  eins vorsiehst, dann sauber über dieselben Tokens.
- **Barrierefreiheit** im vernünftigen Rahmen: Kontraste ≥ 4.5:1 für Fließtext, sichtbarer
  Fokus, `prefers-reduced-motion` respektiert, sinnvolle Alt-Texte, Untertitel-Spur optional
  vorgesehen (`<track>`), semantisches Markup.
- **Performance:** Ziel ist eine Seite unter ~1,5 MB ohne Videos. Bilder in passenden
  Größen, `loading="lazy"` unterhalb des Folds.

## Mehrfachverwendung für spätere Reisen

Trenne sauber:

- **System-Tokens** (Abstände, Typo-Skala, Radien, Motion, Grundstruktur der Palette) —
  bleiben über alle Reisen gleich.
- **Reise-Tokens** (Akzentfarbe, Hero-Bilder, Titel, ggf. eine zweite Akzentfarbe) — pro Reise
  ausgetauscht, am besten ein einzelner `:root`-Block in einer eigenen Datei
  `theme-<reise>.css`.
- **Inhalte** stehen im HTML, nicht im CSS.

Beschreib in einem kurzen Abschnitt, welche Dateien man für eine neue Reise anfasst und
welche man nie anfasst.

---

## Die Fakten für die Norwegen-Ausprägung

Damit du echte Inhalte statt Lorem Ipsum einsetzen kannst.

### Reise

| | |
|---|---|
| Zeitraum | Sa 18.07. – Di 04.08.2026 (Verladen am Vorabend, 17.07.) |
| Dauer | 18 Tage |
| Reisende | 2 Erwachsene + Sohn (6 Jahre) |
| Fahrzeug | SEAT Leon ST mit Dachbox |
| Gesamtstrecke | ca. 3.829 km inkl. zweier Fährüberfahrten |
| Roadtrip-Teil | 23.07. – 01.08., ca. 1.332 km Rundkurs ab/bis Skien |
| Basis | Freunde in Skien, Telemark |
| Höchster Punkt | Valdresflye, 1.183 m |
| Route grob | Grevenbroich → Hamburg → Flensburg → Hirtshals → Fähre Color Line → Larvik → Skien → [Roadtrip: Geilo → Aurland → Geiranger → Lom → Uvdal] → Skien → Larvik → Fähre → Hirtshals → Grevenbroich |

Roadtrip-Stationen des Rundkurses: Skien → Heddal Stabkirche → Geilo (Hakkesetstølen,
1.041 m) → Aurlandsfjellet/Stegastein → Aurland/Flåm → Nærøyfjord/Gudvangen → Lærdalstunnel →
Laukifossen/Loen → Geiranger → Trollstigen (702 m) → Lom → Valdresflye (1.183 m) → Uvdal →
Notodden → Skien.

### Höhepunkte fürs Teaser-Textmaterial

Fähre über das Skagerrak · Heddal Stabkirche · Panoramastraße Aurlandsfjellet und die
Plattform Stegastein über dem Aurlandsfjord · Flåmsbana (20,2 km, 864 Höhenmeter, steilste
Normalspurbahn Nordeuropas) · Nærøyfjord (UNESCO-Welterbe) mit dem Elektroboot · Wikingerdorf
Viking Valley in Gudvangen · Lærdalstunnel, 20 km durch den Berg · Wasserfall Laukifossen ·
Geburtstag in Geiranger mit RIB-Safari zu den „Sieben Schwestern" · Trollstigen mit elf
Haarnadelkurven · Stabkirche Lom · Passstraße Valdresflye · Angeln an der Schärenküste, wo
der Sohn seinen ersten Fisch fängt.

### Film 1 — „Norwegen 2026 · Roadtrip" (der Vlog)

- Länge **18:00 min**, 3840×2160 @ 30 fps
- Chronologisch über alle 18 Tage, aus 167 ausgewählten Clips und Fotos (aus 1.181 Aufnahmen)
- Durchgehend eine mitlaufende Karte unten rechts: aktueller Ort, gefahrene Gesamtstrecke
- Beginnt mit einem stillen Cold Open — nur Wind, während die Route auf der Karte wächst
- Dreiteilig entlang von drei Musikstücken, die ineinander überblenden
- Bauchbinden nur für Datum und Etappe, sonst textfrei

### Film 2 — „Norwegen 2026 · Drone Edit"

- Länge **9:28 min**, 3840×2160 @ 30 fps
- 78 reine Drohnenaufnahmen, chronologisch, ohne Karte und ohne Text
- Ruhige, epische Bildsprache: lange Einstellungen, langsame Bewegungen, Schwarzblenden am
  Anfang und Ende
- Zwei Musikstücke, fließend ineinander
- Erste Reise überhaupt mit der Drohne (DJI Lito X1, RC2, Fly More)
- An einem Tag fehlt bewusst Material: in Aurland hat es geregnet, die Drohne blieb unten

### Roadtrip-Log — die 18 Tage in Kurzform

Das ist der Rohstoff für den `day-log`. Endgültige Formulierungen mache ich selbst, du
brauchst sie nur, um Länge und Rhythmus des Musters richtig zu treffen.

| Tag | Datum | Etappe | km | Stichworte |
|---|---|---|---|---|
| 1 | Sa 18.07. | Grevenbroich → Flensburg | 578 | Aufbruch 07:00, viel Stau, Hamburger Hafen, Hafenspaziergang, Möwe |
| 2 | So 19.07. | Flensburg → Skien | 552 | Durch Dänemark, Color-Line-Fähre ab Hirtshals, Wind auf dem Oberdeck, abends Pizza bei Freunden |
| 3 | Mo 20.07. | Skien, Hütte am See | 40 | 581 m, Wanderung zum See, Beeren, Ruderboot, Grillen, erste Drohnenflüge |
| 4 | Di 21.07. | Skien, Küste bei Langesund | 40 | Schärenküste, abgeschliffene Felsen, Muscheln, Eis |
| 5 | Mi 22.07. | Skien, Ruhetag | 20 | Kapla, Route besprechen, zweites Grillen |
| 6 | Do 23.07. | Skien → Geilo | 220 | Heddal Stabkirche, Rastplatz am See, Unterkunft auf 1.041 m |
| 7 | Fr 24.07. | Geilo → Aurland | 190 | Hardangervidda, Aurlandsfjellet, Stegastein, Flåmsbana, abends Fjordblick |
| 8 | Sa 25.07. | Aurland (Erlebnistag) | 10 | Regen, Elektroboot durch den Nærøyfjord, Viking Valley — keine Drohne |
| 9 | So 26.07. | Aurland → Geiranger | 278 | Lærdalstunnel, Fähre über den Sognefjord, Laukifossen, Loen, Ankunft am Fjord |
| 10 | Mo 27.07. | Geiranger | 10 | Geburtstag, Fossevandring am Wasserfall, RIB-Safari zu den Sieben Schwestern |
| 11 | Di 28.07. | Geiranger → Lom | 266 | Gudbrandsjuvet, Trollstigen auf 702 m, Ankunft Lom, Stabkirche, Angler am Wasser |
| 12 | Mi 29.07. | Lom → Uvdal | 300 | Valdresflye auf 1.183 m, Numedal, Camp Uvdal |
| 13 | Do 30.07. | Uvdal | 10 | Freundschaft mit Emil ohne gemeinsame Sprache, Angeln, Soccergolf, Bogenschießen, Kanu |
| 14 | Fr 31.07. | Uvdal | 0 | Kanu, Tischtennis, Bogenschießen, Steine ins Wasser |
| 15 | Sa 01.08. | Uvdal → Skien | 190 | Bewusst die schönere Westroute über Notodden statt der schnellsten |
| 16 | So 02.08. | Skien, Ruhetag | 0 | Hütte, Brettspiele, Ribbe |
| 17 | Mo 03.08. | Skien, Angeln an der Küste | 71 | Schärenküste, viele Drohnenaufnahmen, der erste Fisch |
| 18 | Di 04.08. | Skien → Grevenbroich | 1.052 | 07:00 an der Fähre in Larvik, danach durchgefahren, ~15 Stunden bis nach Hause |

(Tag 0, 17.07.: Verladen am Abend vor der Abreise — Dachbox, voller Kofferraum. Passt als
Auftakt, ist aber kein Reisetag.)

---

## Was ich zurückbekommen möchte

1. **`tokens.css`** — System-Tokens als CSS Custom Properties (Farbe, Typo-Skala, Abstände,
   Radien, Schatten, Motion, Breakpoints), kommentiert.
2. **`theme-norwegen-2026.css`** — der reise-spezifische Token-Block.
3. **`base.css` + `components.css`** — Reset/Grundlayout und die oben gelisteten Komponenten.
4. **`index.html` und `drone.html`** — vollständige, funktionierende Seiten mit den echten
   Inhalten von oben und Platzhaltern für Bilder/Videos an klar benannten Pfaden
   (`assets/img/…`, `video/…`).
5. **Eine Design-Dokumentation** (Markdown): Gestaltungsprinzipien, Typo-Skala, Farbrollen,
   Komponentenübersicht mit Anwendungsregeln, und der Abschnitt „so legt man eine neue
   Reise-Seite an".
6. **Font-Empfehlung** mit Lizenz und Bezugsquelle — Dateien lade ich selbst.
7. **Bildliste**: welche Bilder in welchen Maßen und Seitenverhältnissen gebraucht werden
   (Hero, Poster, Log-Miniaturen, Karte, Galerie), mit den erwarteten Dateinamen. Ich
   schneide sie aus dem Filmmaterial zu.

Bitte keine Screenshots-als-Design ohne Code — ich brauche die Dateien, sie gehen direkt auf
den Server.

## Wenn dir etwas fehlt

Frag lieber, als zu raten — insbesondere bei Inhalten, Bildmotiven oder wenn du eine
gestalterische Entscheidung für begründungsbedürftig hältst.
