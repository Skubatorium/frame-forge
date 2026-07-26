"""ffprobe, EXIF, GPS, Zeitstempel — technische Rohdaten pro Asset.

Kommt mit der Ingest-Pipeline in M1.
"""

from __future__ import annotations

from pathlib import Path


def probe_video(path: Path) -> dict:
    """ffprobe-Wrapper: Codec, Aufloesung, fps, Dauer, Bitrate."""
    raise NotImplementedError("probe.probe_video kommt in M1")


def probe_photo_exif(path: Path) -> dict:
    """EXIF/GPS/Zeitstempel eines Fotos via exiftool."""
    raise NotImplementedError("probe.probe_photo_exif kommt in M1")
