#!/usr/bin/env bash
# Deployt die Norwegen-Website nach https://norwegen.skubus.de
#
# Es wird nicht public/ direkt hochgeladen, sondern eine Kopie, in der jeder
# Asset-Verweis einen Inhalts-Hash traegt (…/base.css?v=ab12cd34). Grund:
# Cloudflare cacht Assets vier Stunden, die HTML aber nicht — ohne die Hashes
# zeigt frisches HTML stundenlang auf alte CSS und alte Bilder.
set -euo pipefail

cd "$(dirname "$0")"

SRC=web/sites/norwegen-2026/public
BUILD=$(mktemp -d)
trap 'rm -rf "$BUILD"' EXIT

rsync -a "$SRC"/ "$BUILD"/
.venv/bin/python web/sites/norwegen-2026/deploy/cache-bust.py "$BUILD"

rsync -avz --delete --exclude='videos' \
  "$BUILD"/ \
  chris@159.195.213.69:/opt/apps/norwegen/

# nginx im Container laeuft als anderer User als "chris" und braucht
# mindestens Lese-/Traversier-Rechte. Bei restriktivem lokalem umask
# koennten sonst Dateien mit z. B. 600/700 landen (macOS' openrsync
# unterstuetzt --chmod nicht zuverlaessig, deshalb Fix server-seitig).
ssh chris@159.195.213.69 "chmod -R a+rX /opt/apps/norwegen/"

echo "Norwegen-Website aktualisiert: https://norwegen.skubus.de"
