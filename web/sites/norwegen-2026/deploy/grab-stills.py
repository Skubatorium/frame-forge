#!/usr/bin/env python
"""Erzeugt die Standbilder der Website reproduzierbar aus dem Material.

Zwei Quellen:

* **Filmstandbilder (Poster)** aus den fertigen 1080p-Fassungen — die Titelbilder
  ("Norwegen 2026 / Roadtrip Edition" bzw. "Drone Edition") liegen dort schon komponiert vor.
* **Motivbilder** (Hero, Teaser, Seitenkoepfe) aus den Originalclips im `media_root`,
  referenziert ueber die Asset-ID aus `index/assets.json`.

FFmpeg wird nicht nackt aufgerufen, sondern ueber `frameforge.render._run_ffmpeg_cmd` —
dieselbe Stelle, die auch der Renderer benutzt (siehe CLAUDE.md, "Nackte ffmpeg-Aufrufe sind
verboten").

    .venv/bin/python web/sites/norwegen-2026/deploy/grab-stills.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from PIL import Image  # noqa: E402

from frameforge.project import resolve_project  # noqa: E402
from frameforge.render import _run_ffmpeg_cmd  # noqa: E402

SITE = REPO / "web/sites/norwegen-2026"
OUT = SITE / "public/assets/img"
EXPORTS = REPO / "projects/norwegen-2026/exports"

# --- Was gebraucht wird ------------------------------------------------------------------
# (Zieldatei, Asset-ID, Sekunde im Clip, Zielbreite)
MOTIFS = [
    ("teaser-vlog.jpg", "20260724-drone-902691", 6.0, 1800),    # Fjord, Ufer-Strasse, Dorf
    ("teaser-drone.jpg", "20260728-drone-c91b2a", 12.0, 1800),  # Trollstigen ueber Wolken
    ("head-vlog.jpg", "20260728-drone-eab4d9", 4.0, 2560),      # elf Haarnadelkurven
    ("head-drone.jpg", "20260726-drone-688dda", 13.0, 2560),    # Landeplatz "H", tuerkis
]

# (Zieldatei, Export, Sekunde im fertigen Film)
POSTERS = [
    ("vlog-poster.jpg", "vlog-edit", 19.0),
    ("drone-poster.jpg", "drone-edit", 13.0),
]

QUALITY = 82


def assets_by_id() -> dict[str, dict]:
    data = json.loads((REPO / "projects/norwegen-2026/index/assets.json").read_text())
    items = data if isinstance(data, list) else list(data.values())
    return {a["id"]: a for a in items if isinstance(a, dict) and "id" in a}


def grab(source: Path, second: float, target: Path, width: int) -> None:
    """Zieht einen Frame und speichert ihn als JPEG mit `width` Pixeln Breite."""
    tmp = target.with_suffix(".tmp.png")
    _run_ffmpeg_cmd(
        [
            "ffmpeg", "-y", "-ss", f"{second}", "-i", str(source),
            "-frames:v", "1", "-loglevel", "error", str(tmp),
        ],
        timeout_s=180.0,
    )
    with Image.open(tmp) as im:
        im = im.convert("RGB")
        if im.width > width:
            height = round(im.height * width / im.width)
            im = im.resize((width, height), Image.LANCZOS)
        im.save(target, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    tmp.unlink()
    print(f"  {target.name}: {target.stat().st_size // 1024} kB")


def main() -> int:
    project = resolve_project("norwegen-2026")
    media_root = Path(project.config.media_root)
    index = assets_by_id()
    OUT.mkdir(parents=True, exist_ok=True)

    print("Motivbilder aus dem Rohmaterial:")
    missing = []
    for name, asset_id, second, width in MOTIFS:
        asset = index.get(asset_id)
        if asset is None:
            missing.append(asset_id)
            print(f"  ! {name}: Asset {asset_id} nicht im Index")
            continue
        source = media_root / asset["path"]
        if not source.exists():
            missing.append(asset_id)
            print(f"  ! {name}: Datei fehlt - {source}")
            continue
        grab(source, second, OUT / name, width)

    print("Filmstandbilder (Poster):")
    for name, export, second in POSTERS:
        source = EXPORTS / export / "final" / f"{export}_1080p.mp4"
        if not source.exists():
            print(f"  ! {name}: {source} fehlt")
            continue
        grab(source, second, OUT / name, 1920)

    print("Routenkarte:")
    src = REPO / "projects/norwegen-2026/index/final-route.png"
    with Image.open(src) as im:
        im = im.convert("RGB")
        # Nicht hochrechnen: der Screenshot wird nur verkleinert, nie vergroessert.
        target_w = min(1600, im.width)
        if target_w < im.width:
            im = im.resize((target_w, round(im.height * target_w / im.width)), Image.LANCZOS)
        im.save(OUT / "route-map.jpg", "JPEG", quality=84, optimize=True, progressive=True)
        print(f"  route-map.jpg: {im.width} × {im.height}, "
              f"{(OUT / 'route-map.jpg').stat().st_size // 1024} kB")

    if missing:
        print(f"\nNicht erzeugt: {', '.join(missing)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
