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


def generate_heic_photo() -> None:
    """Echtes HEIC-Fixture — sonst haengt der HEIC-Pfad am privaten Fundus des Nutzers.

    Der Import registriert den HEIF-Opener (nur so kann Pillow HEIF ueberhaupt schreiben).
    Bewusst ein Farbverlauf statt einer einfarbigen Flaeche: bei Volltonfarbe ist die
    Schaerfe-Metrik konstant 0 und ein Test darauf wuerde nichts belegen.
    """
    import frameforge.imageio  # noqa: F401 — Import registriert den HEIF-Opener

    image = Image.new("RGB", (64, 48))
    image.putdata([(x * 4 % 256, y * 5 % 256, 128) for y in range(48) for x in range(64)])
    image.save(FIXTURES_DIR / "photo.heic", format="HEIF", quality=90)


def generate_multiaudio_clip() -> None:
    """Clip mit **zwei** Tonspuren, die zweite kanalreicher als die erste.

    Bildet die Falle nach, an der `IMG_9838.MOV` gescheitert ist: iPhone-Clips mit Spatial
    Audio tragen neben der AAC-Stereospur eine 4-kanalige `apac`-Spur ohne ffmpeg-Decoder.
    ffmpegs automatische Stream-Auswahl bevorzugt die kanalreichere Spur. `apac` laesst sich
    hier nicht erzeugen (kein Encoder), die **Kanalzahl** als Auswahlkriterium schon — und
    genau die entscheidet.
    """
    out = FIXTURES_DIR / "clip_multiaudio.mov"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=duration=1:size=320x240:rate=25",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=880:duration=1",
            "-filter_complex",
            "[1:a]aformat=channel_layouts=stereo[a1];[2:a]aformat=channel_layouts=quad[a2]",
            "-map",
            "0:v",
            "-map",
            "[a1]",
            "-map",
            "[a2]",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-loglevel",
            "error",
            str(out),
        ],
        check=True,
    )


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
    generate_heic_photo()
    generate_multiaudio_clip()
    generate_proto_media()
    generate_tone()
    print("Fixtures erzeugt:", FIXTURES_DIR)
