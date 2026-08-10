#!/usr/bin/env bash
set -euo pipefail

rsync -avz --delete --exclude='videos' \
  web/sites/norwegen-2026/public/ \
  chris@159.195.213.69:/opt/apps/norwegen/

echo "Norwegen-Website aktualisiert: https://norwegen.skubus.de"