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

echo "Norwegen-Website aktualisiert: https://norwegen.skubus.de"
