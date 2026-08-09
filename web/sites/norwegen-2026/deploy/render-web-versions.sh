#!/usr/bin/env bash
# Erzeugt die 1080p-Streaming-Fassungen beider Norwegen-Exporte.
#
# Laeuft mehrere Stunden. Starten mit:
#   nohup ./web/sites/norwegen-2026/deploy/render-web-versions.sh > /tmp/ff-web-render.log 2>&1 &
#   disown
#
# Fortsetzbar: der Chunk-Render legt Zwischenstuecke unter
# exports/<export>/final/.<export>_chunks/ ab und ueberspringt beim Neustart, was fertig ist.

set -u
cd "$(dirname "$0")/../../../.." || exit 1

PY=.venv/bin/python
PROJECT=norwegen-2026

# CRF 20 bei 1080p ergibt bei diesem Material grob 8-12 Mbit/s — gut aussehend und ueber
# normale Anschluesse streambar. --chunk-s 110 wie beim 4K-Lauf: die Zahl gleichzeitig
# offener Inputs sprengt sonst den RAM.
render() {
  local export_name="$1"
  echo "=== $(date '+%F %T') START $export_name 1080p ==="
  $PY -m frameforge render "$PROJECT" "$export_name" \
    --resolution 1920x1080 \
    --crf 20 \
    --preset medium \
    --chunk-s 110
  echo "=== $(date '+%F %T') ENDE $export_name (exit $?) ==="
}

render drone-edit
render vlog-edit

echo "=== $(date '+%F %T') FERTIG ==="
ls -lh projects/$PROJECT/exports/*/final/*.mp4
