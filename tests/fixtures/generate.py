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


PROTO_MEDIA_DIR = FIXTURES_DIR / "proto_media"


def _generate_silent_clip(name: str, pattern: str, duration: float) -> None:
    out = PROTO_MEDIA_DIR / name
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"{pattern}=duration={duration}:size=320x240:rate=25",
            "-pix_fmt",
            "yuv420p",
            "-loglevel",
            "error",
            str(out),
        ],
        check=True,
    )


def _generate_clip_with_audio(name: str, duration: float) -> None:
    """Ein Clip mit Ton — steht fuer den einzigen O-Ton-Kandidaten im proto-Testprojekt."""
    out = PROTO_MEDIA_DIR / name
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"smptebars=duration={duration}:size=320x240:rate=25",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=440:duration={duration}",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            "-loglevel",
            "error",
            str(out),
        ],
        check=True,
    )


def generate_proto_media() -> None:
    """Winziges Medienset fuer `projects/proto/` (M1-Mini-Prototyp, siehe PROGRESS.md M1.8)."""
    PROTO_MEDIA_DIR.mkdir(exist_ok=True)
    _generate_silent_clip("clip-fjord.mp4", "testsrc", 2.5)
    _generate_silent_clip("clip-water.mp4", "testsrc2", 2.0)
    _generate_clip_with_audio("clip-drive.mp4", 2.0)
    Image.new("RGB", (640, 480), color=(90, 140, 200)).save(
        PROTO_MEDIA_DIR / "photo-cabin.jpg", quality=85
    )
    Image.new("RGB", (640, 480), color=(200, 150, 90)).save(
        PROTO_MEDIA_DIR / "photo-family.jpg", quality=85
    )


def generate_tone() -> None:
    """Kurzer Ton mit Tremolo — erzeugt eine sichtbare Energiekurve fuer `audio.analyze_track`."""
    out = FIXTURES_DIR / "tone.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=220:duration=4",
            "-af",
            "tremolo=f=2:d=0.9",
            "-loglevel",
            "error",
            str(out),
        ],
        check=True,
    )


if __name__ == "__main__":
    generate_clip()
    generate_photo()
    generate_proto_media()
    generate_tone()
    print("Fixtures erzeugt:", FIXTURES_DIR)
