"""Scan, Hashing, Proxy-Erzeugung fuer Rohmaterial."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

_HASH_PREFIX_BYTES = 1024 * 1024

VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".mxf", ".avi", ".mkv"})
PHOTO_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".heic", ".dng"})
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | PHOTO_EXTENSIONS

PROXY_WIDTH = 1920
PROXY_HEIGHT = 1080


@dataclass(frozen=True)
class IngestFailure:
    """Ein Asset, dessen Proxy-Erzeugung fehlschlug (uebersprungen, nicht abgebrochen)."""

    asset: Path
    reason: str


@dataclass
class ProxyResult:
    """Ergebnis von `build_proxies` — erzeugte/wiederverwendete Proxies + Fehlschlaege."""

    proxies: list[Path] = field(default_factory=list)
    failures: list[IngestFailure] = field(default_factory=list)


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


def _path_key(asset_path: Path, media_root: Path) -> str:
    """Stabiler, eindeutiger Schluessel fuer ein Asset: relativer Pfad unter `media_root`.

    **Beide Seiten werden `resolve()`-t**, damit Ingest (gescannte, evtl. un-aufgeloeste Pfade)
    und Render (`resolve_media_path` liefert aufgeloeste Pfade) denselben Schluessel bilden —
    sonst zeigen sie bei symlink-behaftetem `media_root` (macOS `/var`→`/private/var`, gemountete
    Platten) auf unterschiedliche Proxy-Dateinamen und der Render findet den Proxy nicht.
    Faellt auf den aufgeloesten absoluten Pfad zurueck, falls `asset_path` nicht unter
    `media_root` liegt.
    """
    root = media_root.resolve()
    resolved = asset_path.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return str(resolved)


def proxy_path(asset_path: Path, out_dir: Path, *, media_root: Path) -> Path:
    """Zielpfad des Proxys fuer ein Asset — Video wird zu `.mp4`, Fotos behalten ihre Endung.

    Der Dateiname traegt einen 8-stelligen Hash des relativen Pfads. Ohne den wuerden zwei
    Dateien mit gleichem Basenamen in verschiedenen Ordnern (z.B. `DJI_0001.MP4` pro SD-Karte)
    auf denselben Proxy zeigen und sich gegenseitig ueberschreiben — Preview/Render zeigte dann
    still das falsche Material. Der Hash haelt die Struktur flach, aber kollisionsfrei.
    """
    digest = hashlib.sha256(_path_key(asset_path, media_root).encode()).hexdigest()[:8]
    if asset_path.suffix.lower() in VIDEO_EXTENSIONS:
        return out_dir / f"{asset_path.stem}_{digest}.mp4"
    return out_dir / f"{asset_path.stem}_{digest}{asset_path.suffix}"


def build_proxies(
    assets: list[Path], out_dir: Path, *, media_root: Path, timeout_s: float = 1800.0
) -> ProxyResult:
    """Erzeugt 1080p-H.264-Proxies fuer Video-Assets (schnelles Preset), kopiert Fotos 1:1.

    Fotos brauchen keinen Transcode fuer den Schnitt-Workflow — sie werden ohnehin nur als
    Keyframe/Standbild verwendet, ein Proxy-Encoding waere unnoetiger Aufwand.

    **Idempotent + fehlertolerant** (Resume): bereits existierende Proxies werden uebersprungen,
    eine einzelne fehlgeschlagene/haengende Datei (ffmpeg-Timeout oder Fehler) bricht **nicht**
    den ganzen Lauf ab, sondern wird als `IngestFailure` gesammelt und uebersprungen. Bei ~100 GB
    darf ein korruptes File nicht die komplette Ingestion vernichten.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    failures: list[IngestFailure] = []
    for asset in assets:
        target = proxy_path(asset, out_dir, media_root=media_root)
        if target.exists():
            outputs.append(target)
            continue
        try:
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
                    timeout=timeout_s,
                )
            else:
                target.write_bytes(asset.read_bytes())
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            target.unlink(missing_ok=True)  # halbfertigen Proxy nicht liegen lassen
            failures.append(IngestFailure(asset, str(exc)))
            continue
        outputs.append(target)
    return ProxyResult(outputs, failures)
