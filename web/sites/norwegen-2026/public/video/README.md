# video/ — hier kommen die MP4s rein

Dateien sind gitignored. Erwartete Namen (so referenziert die Website sie):

| Datei | Zweck | Quelle | Ziel-Größe |
|---|---|---|---|
| `vlog-edit-1080p.mp4` | Streaming im Player | `exports/vlog-edit/final/vlog-edit_v1.mp4` | ~1,3 GB |
| `drone-edit-1080p.mp4` | Streaming im Player | `exports/drone-edit/final/drone-edit_v2.mp4` | ~0,7 GB |
| `vlog-edit-4k.mp4` | Download-Link (4K) | dieselbe Quelle | 6,8 GB |
| `drone-edit-4k.mp4` | Download-Link (4K) | dieselbe Quelle | 5,4 GB |
| `vlog-edit-poster.jpg` | Poster-Bild | Standbild aus dem Film | < 400 KB |
| `drone-edit-poster.jpg` | Poster-Bild | Standbild aus dem Film | < 400 KB |

Poster liegen der Einfachheit halber bei den Videos, damit `video/` als Ganzes separat
hochgeladen werden kann.

## Zu beachten

- **Alle vier MP4s brauchen `faststart`** (moov-Atom am Dateianfang). Ohne das laedt der
  Browser erst die komplette Datei, bevor irgendetwas zu sehen ist — bei 6,8 GB heisst das:
  gar nichts.
- Die 4K-Fassungen sind reine Downloads. nginx liefert sie mit
  `Content-Disposition: attachment` aus (siehe `deploy/nginx.conf.example`), damit niemand
  versehentlich 76 Mbit/s zu streamen versucht.
- **Serverbedarf:** ~14 GB Plattenplatz fuer alle vier Dateien. Vor dem Upload freien Platz
  und Traffic-Kontingent des VPS pruefen.
- Erzeugt werden die Fassungen ueber `frameforge render` — nackte ffmpeg-Aufrufe blockiert
  der Gate-Hook.
