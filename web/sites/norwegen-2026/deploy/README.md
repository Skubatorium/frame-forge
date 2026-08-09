# Deployment — norwegen.scoobus.de

Ziel: statische Seite plus zwei MP4s auf dem VPS, hinter nginx Basic Auth.

## 1. Verzeichnis auf dem Server

```
/var/www/norwegen.scoobus.de/
  index.html
  drone.html
  assets/...
  video/
    vlog-edit.mp4
    drone-edit.mp4
```

## 2. Passwortdatei anlegen

```bash
sudo apt install apache2-utils          # liefert htpasswd
sudo htpasswd -c /etc/nginx/.htpasswd-norwegen norwegen
# Passwort zweimal eingeben. -c nur beim ersten Mal (legt die Datei neu an)!
sudo chown root:www-data /etc/nginx/.htpasswd-norwegen
sudo chmod 640 /etc/nginx/.htpasswd-norwegen
```

Verteilt wird dann: `https://norwegen.scoobus.de` · Benutzer `norwegen` · Passwort.

## 3. nginx-Site

`nginx.conf.example` nach `/etc/nginx/sites-available/norwegen.scoobus.de` kopieren,
Serverpfade prüfen, verlinken, testen, neu laden:

```bash
sudo ln -s /etc/nginx/sites-available/norwegen.scoobus.de /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 4. TLS

```bash
sudo certbot --nginx -d norwegen.scoobus.de
```

Vorher muss der DNS-A-Record der Subdomain auf die VPS-IP zeigen.

## 5. Dateien hochladen

Website (klein, jederzeit wiederholbar):

```bash
rsync -avz --delete \
  web/sites/norwegen-2026/public/ \
  user@vps:/var/www/norwegen.scoobus.de/ \
  --exclude video/
```

Videos (groß, einmalig — `--partial --progress`, damit ein Abbruch fortsetzbar ist):

```bash
rsync -avP web/sites/norwegen-2026/public/video/ \
  user@vps:/var/www/norwegen.scoobus.de/video/
```

`--delete` ist bei den Videos absichtlich **nicht** gesetzt.

## Hinweise

- **Basic Auth schützt auch die MP4s**, weil sie unter demselben `location /` liegen. Das ist
  der Grund für diese Variante statt eines JS-Logins.
- **Traffic im Auge behalten:** Jede vollständige Ansicht überträgt die volle Dateigröße.
  Beim VPS-Tarif auf das Inklusivvolumen achten.
- **Range-Requests** müssen funktionieren, sonst kann im Video nicht gesprungen werden —
  nginx kann das ab Werk, solange kein Gzip auf MP4s läuft (siehe Beispielkonfiguration).
