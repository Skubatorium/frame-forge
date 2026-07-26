"""Scan, Hashing, Proxy-Erzeugung fuer Rohmaterial.

`hash_file` ist bereits echt implementiert — der Cache-Schluessel aus Plan §3
("Analyse genau einmal pro Datei") haengt direkt daran. Scan und Proxy-Encoding
brauchen die Analyse-Pipeline und kommen erst in M1.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

_HASH_PREFIX_BYTES = 1024 * 1024


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
    """Findet alle Video-/Foto-Dateien unter `media_root`. Kommt in M1."""
    raise NotImplementedError("ingest.scan_media kommt mit der Ingest-Pipeline in M1")


def build_proxies(assets: list[Path], out_dir: Path) -> None:
    """Erzeugt 1080p-H.264-Proxies fuer die gegebenen Assets. Kommt in M1."""
    raise NotImplementedError("ingest.build_proxies kommt mit der Ingest-Pipeline in M1")
