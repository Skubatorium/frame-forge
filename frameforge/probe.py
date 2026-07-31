"""ffprobe, EXIF, GPS, Zeitstempel — technische Rohdaten pro Asset."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


class ProbeError(RuntimeError):
    """ffprobe/exiftool ist fehlgeschlagen oder lieferte kein auswertbares Ergebnis."""


# Kontrolliertes Vokabular fuer `asset["source"]` (Aufnahme-Quelle). Der media-indexer-Agent
# setzt das Feld; `guess_source` liefert einen Vorschlag aus EXIF-Kamera-Angaben.
SOURCE_TYPES = ("drone", "phone", "camera", "action_cam", "unknown")

# Marker in Make/Model/Handler -> Quelle. Reihenfolge = Prioritaet.
_SOURCE_MARKERS: tuple[tuple[str, str], ...] = (
    ("dji", "drone"),
    ("autel", "drone"),
    ("skydio", "drone"),
    ("parrot", "drone"),
    ("gopro", "action_cam"),
    ("insta360", "action_cam"),
    ("osmo action", "action_cam"),
    ("iphone", "phone"),
    ("ipad", "phone"),
    ("pixel", "phone"),
    ("galaxy", "phone"),
    ("samsung sm-", "phone"),
    ("xiaomi", "phone"),
    ("oneplus", "phone"),
)


def guess_source(*hints: str | None, name_hint: str | None = None) -> str:
    """Raet die Aufnahme-Quelle aus EXIF-Kamera-Angaben (Make/Model/Handler).

    Best-effort-Vorschlag fuer den media-indexer — der Agent darf ihn ueberschreiben, wenn die
    Keyframes etwas anderes zeigen. Ohne Treffer: `"camera"` bei vorhandener Kamera-Angabe, sonst
    `"unknown"`.

    `name_hint` (Dateiname) wird nur fuer eindeutige Marker herangezogen (z.B. `DJI_…` → drone),
    da re-encodete Proxys die EXIF verlieren. Er beeinflusst aber NICHT die camera/unknown-
    Entscheidung — ein blosser Dateiname ohne Kamera-Angabe bleibt `"unknown"`.
    """
    blob = " ".join(h for h in hints if h).lower()
    for marker, source in _SOURCE_MARKERS:
        if marker in blob:
            return source
    if name_hint:
        name = name_hint.lower()
        for marker, source in _SOURCE_MARKERS:
            if marker in name:
                return source
    return "camera" if blob.strip() else "unknown"


def _run_json(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    if result.returncode != 0:
        raise ProbeError(f"{cmd[0]} fehlgeschlagen: {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError(f"{cmd[0]} lieferte kein gueltiges JSON: {exc}") from exc


def _parse_frame_rate(rate: str) -> float:
    """`"30000/1001"` -> `29.97`."""
    if "/" not in rate:
        return float(rate)
    num, den = rate.split("/")
    den_f = float(den)
    return float(num) / den_f if den_f else 0.0


def probe_video(path: Path) -> dict:
    """ffprobe-Wrapper: Codec, Aufloesung, fps, Dauer, Bitrate (Format `tech` aus Plan §4)."""
    data = _run_json(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
    )
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    if video_stream is None:
        raise ProbeError(f"{path}: kein Video-Stream gefunden")

    fmt = data.get("format", {})
    duration = float(fmt.get("duration") or video_stream.get("duration") or 0.0)
    bitrate = int(fmt.get("bit_rate") or video_stream.get("bit_rate") or 0)

    # Kamera-Hinweise aus Container-/Stream-Tags (DJI, GoPro ... setzen z.B. make/handler_name).
    tags = {**fmt.get("tags", {}), **video_stream.get("tags", {})}
    hints = [tags.get(k) for k in ("make", "model", "handler_name", "encoder", "com.apple.quicktime.make")]

    return {
        "w": int(video_stream.get("width", 0)),
        "h": int(video_stream.get("height", 0)),
        "fps": _parse_frame_rate(video_stream.get("r_frame_rate", "0/1")),
        "dur": duration,
        "bitrate": bitrate,
        "codec": video_stream.get("codec_name", "unknown"),
        "source_guess": guess_source(*hints, name_hint=path.name),
    }


def probe_photo_exif(path: Path) -> dict:
    """EXIF/GPS/Zeitstempel eines Fotos via `exiftool -j`.

    Rueckgabe passend zu `assets.json`: `{"captured_at": ..., "gps": {...} | None}`.
    GPS/Zeitstempel fehlen bei vielen Fotos (kein GPS-Chip, keine EXIF-Zeit) — dann `None`,
    kein Fehler.
    """
    data = _run_json(["exiftool", "-j", str(path)])
    if not data:
        raise ProbeError(f"{path}: exiftool lieferte keinen Eintrag")
    entry = data[0]

    captured_at = None
    raw_date = entry.get("DateTimeOriginal") or entry.get("CreateDate")
    if raw_date:
        try:
            captured_at = datetime.strptime(raw_date, "%Y:%m:%d %H:%M:%S").replace(
                tzinfo=UTC
            ).isoformat()
        except ValueError:
            captured_at = None

    gps = None
    lat, lon = entry.get("GPSLatitude"), entry.get("GPSLongitude")
    if lat is not None and lon is not None:
        gps = {"lat": _to_signed_degrees(lat), "lon": _to_signed_degrees(lon)}

    make, model = entry.get("Make"), entry.get("Model")
    return {
        "captured_at": captured_at,
        "gps": gps,
        "make": make,
        "model": model,
        "source_guess": guess_source(make, model, name_hint=path.name),
    }


def _to_signed_degrees(value: float | str) -> float:
    """exiftool liefert je nach Version Dezimalgrad als float oder `"62 deg 6' 17.64\" N"`."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    sign = -1.0 if text.strip().endswith(("S", "W")) else 1.0
    parts = text.replace("deg", " ").replace("'", " ").replace('"', " ")
    parts = parts.replace("N", " ").replace("S", " ").replace("E", " ").replace("W", " ")
    numbers = [float(p) for p in parts.split() if p.replace(".", "", 1).isdigit()]
    degrees, minutes, seconds = (numbers + [0.0, 0.0, 0.0])[:3]
    return sign * (degrees + minutes / 60 + seconds / 3600)
