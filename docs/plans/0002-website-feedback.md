# 0002 — Norwegen-Website: Umbau nach Nutzer-Feedback

*Angelegt 2026-08-10. Grundlage: ausführliches Feedback nach dem ersten Deployment auf
https://norwegen.skubus.de.*

## Kontext

Die fünfseitige Reise-Website steht und funktioniert (Videos laufen, Links stimmen). Das
Feedback betrifft **Text, Struktur, Bildauswahl und Gestaltung** — keine neue Technik. Ziel:
weniger generisch, weniger „KI-Deutsch", faktisch korrekt, optisch ruhiger.

Nur `web/sites/norwegen-2026/public/` wird deployed. Der Zwilling unter
`design/export/site/` ist Designsystem-Ausgabe und wird **nicht** mitgepflegt.

## Geprüfte Fakten (gemessen, nicht geschätzt)

| | Roadtrip Edition | Drone Edition |
|---|---|---|
| Länge | 18:00 min (1080,4 s) | 9:28 min (568,2 s) |
| Auflösung/fps | 3840 × 2160, **30 fps** | 3840 × 2160, **30 fps** |
| Einstellungen | 167 | 78 |
| Streaming 1080p | 1,78 GB · 13,2 Mbit/s | 1,48 GB · 20,8 Mbit/s |
| Download 4K | 7,28 GB · **53,9 Mbit/s** | 5,80 GB · **81,6 Mbit/s** |

- Quelle: `frameforge.probe.probe_video` über alle vier Finals. 60 fps gibt es nicht — die
  Timeline steht auf 30 fps, beide Filme sind so gerendert. Nutzerentscheid: 30 fps ausweisen.
- Fundus: 1.181 Assets = **465 Video + 716 Foto**, ~4 h Rohvideo. Die bisherige Formulierung
  „1.181 Aufnahmen, knapp vier Stunden Rohmaterial" verschweigt den Fotoanteil.
- Musik Roadtrip: *Cuatro Vientos* (Danit) · *Naturaleza (Mose Edit)* (Mose & Danit) ·
  *Aguila de Oro (Ecstatic Mix)* (Little Whale, Sariel Orenda & UAK).
  Drone: *Naturaleza (Mose Edit)* → *Cuatro Vientos*.
- Route neu: Rundkurs **1.332 km / 22 h 40 min** (ausgetauschte `index/final-route.png`,
  Rückweg identisch über Heddal). Alte Angabe 1.319 km / 22 h 31 min ist überall zu ersetzen.
- Anreise laut `route/stages.csv`: 17.07. Verladen zu Hause · 18.07. Grevenbroich → Flensburg
  (578 km, via Hamburg), Übernachtung Flensburg · 19.07. Flensburg → Hirtshals → Fähre →
  Larvik → Skien. Die Seite behauptet bisher „Hirtshals, Verladen am Vorabend" — falsch.

## A · Global (alle fünf Seiten)

1. **Geviertstriche (—) raus.** Überall durch normalen Bindestrich, Komma oder Satzende
   ersetzen. Halbgeviert bleibt nur in Zahl-/Datumsspannen (`17.–18.07.`).
2. **Benennung**: „Drone Edit" → **Drone Edition**, „Roadtrip" → **Roadtrip Edition** in
   Navigation, Fußzeile, Seitentiteln, Buttons. Grund: In den Filmen selbst steht „Edition".
3. **Flagge oben links**: `.flagmark` im Header ist ein waagerechter Streifenverlauf und liest
   sich als falsche Flagge. Ersatz durch das korrekte Flaggen-SVG aus
   `assets/img/favicon.svg` (neue Variante `.flagmark--flag`). Der 40 × 3 px Streifen in der
   Fußzeile bleibt als Trenner.
4. **Fußzeilen-Text neu**, entschärft: kein „Menschen, die nicht gefragt wurden", kein „jeder
   Abruf kostet Serverdaten". Neu sinngemäß: private Familienseite, Link und Passwort bitte
   nicht weitergeben, Zugang gibt es auf Nachfrage, Passwort wird in Abständen gewechselt.
   Basiszeile: „Norwegen 2026 · private Reiseseite, nicht kommerziell".
5. **Untere Navigation** als durchgehende Kette, wie das Blättern durch die Kopfnavigation:
   Start → Roadtrip Edition → Drone Edition → Zahlen & Fakten → Start.

## B · Startseite (`index.html`)

1. **Hero-Rotator**: `hero-04.jpg` (Kreuzfahrtschiff) entfernen → fünf Szenen, `--n: 5`.
   Der harte „Reinzoom"-Effekt beim Laden entsteht durch das zusätzlich als
   `background-image` gesetzte Standbild unter der bereits einblendenden Szene 1. Fix:
   Standbild raus bzw. Szene 1 ohne Zoom starten, Szenendauer erhöhen, Überblendfenster
   verbreitern, Scale-Endwert reduzieren (1,06 → 1,04) — langsamer, gleichmäßiger Ken Burns.
2. **Buttons** „Roadtrip ansehen" / „Drone Edit" sind gleichwertig → beide `btn--secondary`.
3. **Einleitung persönlicher**: kein „zwei Erwachsene, ein Sechsjähriger". Stattdessen Familie
   Skubatz, vollgepackter Kombi mit Dachbox, ein Land, das sich alle paar Kilometer neu findet.
4. **Absatz über die beiden Filme** neu: Roadtrip Edition = Reisetagebuch, chronologisch, mit
   kleinen Angaben zu den Etappen (**keine mitlaufende Karte** — die ist entfallen).
   Drone Edition = nur Drohnenaufnahmen, kein Anspruch auf Chronologie, die Landschaft selbst.
5. **Film-Karten**: Kicker „Film 1 · 18:00 min" bekommt eine dunkle Plakette, damit er auf
   hellem Bild lesbar bleibt. Neue Standbilder: Roadtrip = Serpentinen/Fjord mit Straße und
   Menschen, Drone = Trollstigen über der Wolkendecke. Texte ohne „nur Wind" und ohne „ein Tag,
   an dem sie unten blieb".
6. **Kennzahlen**: Reihenfolge Zeitraum → Reisedauer → Gesamtstrecke → Höchster Punkt.
   „18.07.–04.08." in einer Größe setzen, nicht Datum groß / Rest winzig.
7. Abstand zwischen Kennzahlen-Block und Fußzeile verkleinern.

## C · Roadtrip Edition (`film-vlog.html`)

1. Seitenkopf bekommt ein **Standbild** (Serpentinen von oben) mit Scrim, gleicher
   Seitengrund wie die Drone-Seite (`--fjord-950`), damit beide Filmseiten gleich wirken.
2. **Meta-Zeile**: `18:00 min` (Einheit grau) · 167 Einstellungen · Streaming 1080p ·
   Hinweis „4K-Download" als Sprungmarke auf den Download-Block.
3. **Fließtext** ohne Cold Open und ohne mitlaufende Karte; mehr über die Reise selbst.
4. **Technisches**: Streaming und Download klar getrennt. Einstellungen „167 von 1.181
   gesichteten Aufnahmen (465 Video, 716 Fotos)".
5. **Download-Block**: für Qualitätsliebhaber formuliert, echte Datenrate 54 Mbit/s, kein
   „ab 20 Mbit/s". Kein Cookie, kein Tracking.
6. **Poster** = Titelbild des Films („Norwegen 2026 / Roadtrip Edition", ca. Sekunde 20).
7. Musik-Credits statt „drei Musikstücke, kein Kommentar".

## D · Drone Edition (`film-drone.html`)

Wie C, zusätzlich:

1. Kopfbild: Türkiswasser von oben bzw. der gelbe Hubschrauber-Landeplatz („H") aus der
   Vogelperspektive.
2. Text: erste Reise mit einer Drohne, bewusste Entscheidung für die DJI Lito X1 wegen
   Sensor und Sicherheitssystemen, Einarbeitung unterwegs. Sätze „ein Tag, an dem sie unten
   blieb" und „endet, wie er beginnt, im Schwarz" entfallen. Statt „Postkarten aus derselben
   Woche" konkrete Landschaft: Wasserfälle, Wolkendecke am Trollstigen, gletschergespeiste
   Fjordfarben.
3. Technisches: „Fernsteuerung" entfällt, Drohne als „DJI Lito X1 · RC2".
4. Poster = Titelbild („Drone Edition", ca. Sekunde 13).
5. Fußnavigation: **weiter zu Zahlen & Fakten**, nicht zum Roadtrip.

## E · Zahlen & Fakten (`fakten.html`)

1. **Ausrichtung vereinheitlichen.** Aktuell mischen sich `wrap` und `wrap--content`, dadurch
   springt die Textkante zwischen Kopf, Route, Drohne und Kuriositäten. Alles auf eine Breite.
2. Karte neu einbinden (**1.332 km / 22 h 40 min**), Link nach Google Maps mit
   `target="_blank" rel="noopener noreferrer"`.
3. **Route korrigieren**: Anreise Grevenbroich → Flensburg (Übernachtung), am Folgetag
   Hirtshals → Fähre → Larvik → Skien. „Verladen am Vorabend" streichen.
   Rundkurs-Stationen durchnummerieren und die Marker erklären (Legende: hervorgehobene
   Punkte = Höhepunkte), damit die gelben Punkte nicht willkürlich wirken.
4. Kachel „2 + 1 Reisende" entfällt. Kuriosität „1 falsche Route" entfällt.
   „1.181 Aufnahmen" wird als 465 Video + 716 Fotos aufgeschlüsselt. „1 Regentag" entfällt.
5. Drohnen-Abschnitt: „ausgepackt in Norwegen", „Flugtage: alle bis auf einen" entfällt;
   Text auf die Entscheidung für die Drohne und das Ergebnis (Aufnahmen in beiden Filmen).
6. Untere Navigation → zurück zur Startseite.

## F · Impressum (`impressum.html`)

Alle Platzhalter füllen und den Ton entschärfen:

- Verantwortlich: Christian Skubatz, Auf dem Griese 89, 41515 Grevenbroich,
  christian.skubatz@gmail.com
- Privater Charakter: Familie, Freunde **und Arbeitskollegen**.
- Bitte um Rücksicht: nicht „nicht um Zustimmung gebeten", sondern: auf den Aufnahmen sind
  Familie und Freunde, damit soll sorgsam umgegangen werden — Link und Passwort nicht
  weitergeben, keine Ausschnitte in soziale Netzwerke.
- Musik: Titel und Künstler beider Filme namentlich, dazu der Hinweis, dass keine
  Veröffentlichungslizenz erworben wurde, die Nutzung rein privat ist und die Seite deshalb
  passwortgeschützt bleibt.
- Kartenmaterial: Google Maps, Screenshot der geplanten Route, keine eingebettete Karte.
- Schriften: Schibsted Grotesk und Source Serif 4, SIL OFL 1.1, vom eigenen Server; Lizenz-
  texte liegen unter `assets/fonts/` und werden verlinkt.
- Datenschutz: keine Cookies, kein Tracking; Server-Logs 30 Tage; Hosting in Deutschland
  (Hetzner, Standort Deutschland); Kontakt per E-Mail.

## Verifikation

- `python -m http.server` in `web/sites/norwegen-2026/public/`, alle fünf Seiten in Chrome
  durchklicken: Hero-Übergänge (kein Sprung beim Laden), Navigation vor/zurück,
  Video-Poster, Download-Links, Kartenlink öffnet neuen Tab.
- `grep -R "—" web/sites/norwegen-2026/public` muss leer sein.
- `grep -R "Drone Edit\b\|1\.319\|22 h 31" web/sites/norwegen-2026/public` muss leer sein.
- Kein toter Bildpfad: jedes `src=` im HTML muss existieren.
