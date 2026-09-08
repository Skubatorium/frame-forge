#!/usr/bin/env bash
# Deployt die JGA-Website nach https://micha-jga.skubus.de
#
# Analog zu deploy-norway-site.sh: es wird nicht public/ direkt hochgeladen,
# sondern eine Kopie, in der jeder Asset-Verweis einen Inhalts-Hash traegt
# (…/base.css?v=ab12cd34), damit Cloudflares Asset-Cache nach einem Deploy
# nicht stundenlang alte CSS/Bilder ausliefert.
#
# Voraussetzung (einmalig, server-seitig, nicht Teil dieses Skripts):
#   - DNS-Eintrag micha-jga.skubus.de -> Server
#   - Traefik Basic-Auth-Eintrag fuer die Subdomain (wie bei den bestehenden
#     Seiten, siehe Server-Konfiguration)
#   - Zielverzeichnis /opt/apps/jga-2026/ auf dem Server
set -euo pipefail

cd "$(dirname "$0")"

SRC=web/sites/michael-jga-2026/public
BUILD=$(mktemp -d)
trap 'rm -rf "$BUILD"' EXIT

rsync -a "$SRC"/ "$BUILD"/
.venv/bin/python web/sites/michael-jga-2026/deploy/cache-bust.py "$BUILD"

rsync -avz --delete --exclude='videos' \
  "$BUILD"/ \
  chris@159.195.213.69:/opt/apps/jga-2026/

# nginx im Container laeuft als anderer User als "chris" und braucht
# mindestens Lese-/Traversier-Rechte. rsync's --chmod verlaesst sich auf
# den lokalen rsync (auf macOS oft die alte 2.6.9, die das nicht sauber
# unterstuetzt) -- deshalb stattdessen server-seitig fixen, unabhaengig
# von der lokalen rsync-Version.
ssh chris@159.195.213.69 "chmod -R a+rX /opt/apps/jga-2026/"

echo "JGA-Website aktualisiert: https://micha-jga.skubus.de"
