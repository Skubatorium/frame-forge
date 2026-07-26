"""Scan, Hashing, Proxy-Erzeugung fuer Rohmaterial."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

_HASH_PREFIX_BYTES = 1024 * 1024

VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".mxf", ".avi", ".mkv"})
PHOTO_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".heic", ".dng"})
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | PHOTO_EXTENSIONS

PROXY_WIDTH = 1920
PROXY_HEIGHT = 1080


def hash_file(path: Path) -> str:
    """Cache-Schluessel: `sha256(erste 1 MB + Dateigroesse + mtime)`.

    Bewusst kein Full-File-Hash — bei ~100 GB Material waere das zu teuer, und
    Groesse+mtime+Prefix reichen aus, um eine unveraenderte Datei zu erkennen.
    """
    stat = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        digest.update(fh.read(_HASH_PREFIX_BYTES))
    digest.update(str(stat.st_size).encode())
    digest.update(str(stat.st_mtime_ns).encode())
    return f"sha256:{digest.hexdigest()}"


def scan_media(media_root: Path) -> list[Path]:
    """Findet alle Video-/Foto-Dateien unter `media_root` (rekursiv, sortiert).

    Ignoriert versteckte Dateien (z.B. `.DS_Store`, Sidecar-Dateien mit fuehrendem `.`).
    """
    if not media_root.is_dir():
        raise FileNotFoundError(f"media_root existiert nicht oder ist kein Verzeichnis: {media_root}")
    return sorted(
        p
        for p in media_root.rglob("*")
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in MEDIA_EXTENSIONS
    )


def proxy_path(asset_path: Path, out_dir: Path) -> Path:
    """Zielpfad des Proxys fuer ein Asset — Video wird zu `.mp4`, Fotos bleiben unveraendert."""
    if asset_path.suffix.lower() in VIDEO_EXTENSIONS:
        return out_dir / f"{asset_path.stem}.mp4"
    return out_dir / asset_path.name


def build_proxies(assets: list[Path], out_dir: Path) -> list[Path]:
    """Erzeugt 1080p-H.264-Proxies fuer Video-Assets (schnelles Preset), kopiert Fotos 1:1.

    Fotos brauchen keinen Transcode fuer den Schnitt-Workflow — sie werden ohnehin nur als
    Keyframe/Standbild verwendet, ein Proxy-Encoding waere unnoetiger Aufwand.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for asset in assets:
        target = proxy_path(asset, out_dir)
        if asset.suffix.lower() in VIDEO_EXTENSIONS:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(asset),
                    "-vf",
                    f"scale='min({PROXY_WIDTH},iw)':'min({PROXY_HEIGHT},ih)':force_original_aspect_ratio=decrease",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    "-loglevel",
                    "error",
                    str(target),
                ],
                check=True,
            )
        else:
            target.write_bytes(asset.read_bytes())
        outputs.append(target)
    return outputs
