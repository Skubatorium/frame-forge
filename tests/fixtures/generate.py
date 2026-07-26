"""Erzeugt die winzigen Test-Fixtures in diesem Ordner neu.

Kein nackter `ffmpeg`-Bash-Aufruf (der Gate-Hook blockt das zurecht) — `ffmpeg` wird hier
intern per `subprocess` aus Python gerufen, analog zu `ingest.build_proxies` (Proxy-
Transcoding ist kein "Render aus timeline.json" im Sinne von CLAUDE.md, sondern Test-Tooling).
Nur bei Bedarf neu ausfuehren: `.venv/bin/python tests/fixtures/generate.py`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

FIXTURES_DIR = Path(__file__).resolve().parent


def generate_clip() -> None:
    out = FIXTURES_DIR / "clip.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=duration=2:size=320x240:rate=25",
            "-pix_fmt",
            "yuv420p",
            "-loglevel",
            "error",
            str(out),
        ],
        check=True,
    )


def generate_photo() -> None:
    out = FIXTURES_DIR / "photo.jpg"
    Image.new("RGB", (64, 48), color=(120, 180, 220)).save(out, quality=80)


if __name__ == "__main__":
    generate_clip()
    generate_photo()
    print("Fixtures erzeugt:", FIXTURES_DIR)
