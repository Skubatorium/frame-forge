# Deployment — https://norwegen.skubus.de

Plattform: skubus-VPS. Zwei getrennte Dinge, die nicht zusammen ausgeliefert werden.

## 1. Die Website

Alles aus `../public/` kommt **1:1 in den Docroot** — `index.html` und `assets/` liegen flach
im Wurzelverzeichnis, keine zusätzliche Verschachtelung.

```bash
rsync -avz --delete web/sites/norwegen-2026/public/ user@vps:<docroot>/
```

## 2. Die Videos

Liegen **nicht** im Website-Build, sondern separat auf dem Server unter `/videos/` relativ zur
Domain — erreichbar als `https://norwegen.skubus.de/videos/<dateiname>`.

```bash
rsync -avP projects/norwegen-2026/exports/vlog-edit/final/vlog-edit_1080p.mp4 \
           projects/norwegen-2026/exports/vlog-edit/final/vlog-edit_4k.mp4 \
           projects/norwegen-2026/exports/drone-edit/final/drone-edit_1080p.mp4 \
           projects/norwegen-2026/exports/drone-edit/final/drone-edit_4k.mp4 \
           user@vps:<video-verzeichnis>/
```

`-P` (= `--partial --progress`) ist wichtig: ~14 GB, ein Abbruch soll fortsetzbar sein.
Kein `--delete`.

Im HTML werden sie absolut referenziert:

```html
<video src="/videos/vlog-edit-1080p.mp4" poster="assets/img/vlog-poster.jpg"></video>
<a href="/videos/vlog-edit-4k.mp4" download>4K-Fassung herunterladen</a>
```

## 3. Passwortschutz

Läuft über **Traefik Basic Auth** auf Infrastruktur-Ebene. Die Website baut dafür nichts ein —
kein Login-Formular, keine Auth-Logik im Code. Der Schutz greift damit auch für die Videos
unter `/videos/`, solange die Middleware auf dem gesamten Router liegt.

## 4. Was auf Serverseite geprüft sein sollte

- **Range-Requests** müssen durchgereicht werden, sonst kann im Video nicht gesprungen werden
  und der Player lädt bei jedem Klick von vorn.
- **Kein gzip auf MP4** — bringt nichts und stört das Ausliefern in Teilstücken.
- **Plattenplatz:** ~14 GB für alle vier Fassungen.
- **Traffic:** jede vollständige Ansicht überträgt die volle Dateigröße der 1080p-Fassung
  (1,8 GB bzw. 1,5 GB). Inklusivvolumen im Blick behalten.
- **`Content-Disposition: attachment`** für die `*-4k.mp4`, damit sie heruntergeladen und
  nicht im Tab abgespielt werden (optional, aber sinnvoll — 4K liegt bei 54–82 Mbit/s).

## Dateinamen

Die Renderpipeline schreibt die Fassungen mit der Auflösung im Namen:

| Datei | Zweck | Größe |
|---|---|---|
| `vlog-edit_1080p.mp4` | Streaming | 1,8 GB |
| `vlog-edit_4k.mp4` | Download | 7,3 GB |
| `drone-edit_1080p.mp4` | Streaming | 1,5 GB |
| `drone-edit_4k.mp4` | Download | 5,8 GB |

Auf dem Server dürfen sie umbenannt werden (z. B. Bindestrich statt Unterstrich) — dann die
vier Referenzen im HTML anpassen. Alle vier Dateien werden mit `faststart` gerendert, das
moov-Atom liegt also vorn und die Wiedergabe startet sofort.
