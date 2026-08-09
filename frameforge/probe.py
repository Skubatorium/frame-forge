"""ffprobe, EXIF, GPS, Zeitstempel — technische Rohdaten pro Asset."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime, timedelta
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


# Aufnahmezeit aus dem Dateinamen: `DJI_20260720153625…`, `IMG_20260720_153625…`,
# `VID_20260720_153625…`, `PXL_20260720_153625123…` — Datum + Uhrzeit, Trenner optional.
_NAME_TIME_RE = re.compile(r"(20\d{2})(\d{2})(\d{2})[_-]?(\d{2})(\d{2})(\d{2})")

# Trim-Suffix des Vorschnitts: `…-00.02.10.556-00.02.18.774-seg5` -> In-/Out-Punkt im Original.
_TRIM_RE = re.compile(
    r"-(\d{2})\.(\d{2})\.(\d{2})\.(\d{3})-(\d{2})\.(\d{2})\.(\d{2})\.(\d{3})-seg\d+",
    re.IGNORECASE,
)

# Reines Datum irgendwo im Pfad (Ordner `2026-07-28_Norwegen_…` oder Dateiname) — letzte
# Rueckfallebene vor `mtime`, taggenau statt sekundengenau.
_PATH_DATE_RE = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")

# Konvention fuer `captured_at` im ganzen Projekt: **lokale Wanduhrzeit, mit `+00:00`
# etikettiert**. Die Fotos aus dem Realbetrieb liegen bereits so vor (EXIF `DateTimeOriginal`
# ist lokale Zeit, `probe_photo_exif` haengt `UTC` an), und Chronologie/Tageszuordnung (A4)
# vergleicht Videos mit Fotos. Eine echte UTC-Zeit fuer Videos und lokale Zeit fuer Fotos
# ergaebe eine stille Verschiebung um den Zeitzonen-Offset — genau das, was A1 beheben soll.
_WALLCLOCK_TZ = UTC


def captured_at_from_name(path: Path) -> datetime | None:
    """Aufnahmezeit aus dem Dateinamen (lokale Wanduhrzeit), oder `None`.

    Kameras schreiben ihre lokale Zeit in den Dateinamen — das ist dieselbe Zeitbasis wie
    EXIF `DateTimeOriginal` bei Fotos.
    """
    match = _NAME_TIME_RE.search(path.name)
    if not match:
        return None
    try:
        return datetime(*(int(g) for g in match.groups()), tzinfo=_WALLCLOCK_TZ)
    except ValueError:
        return None  # z.B. "20261332…" — kein gueltiges Datum, kein Treffer


def trim_offset_from_name(path: Path) -> tuple[float, float] | None:
    """In-/Out-Punkt des Vorschnitts aus dem Dateinamen (`(in_s, out_s)`), oder `None`.

    `…_D-00.02.10.556-00.02.18.774-seg5.MP4` -> `(130.556, 138.774)`. Damit ist die
    Aufnahmezeit *dieses Ausschnitts* rekonstruierbar (Originalzeit + In-Punkt) — das macht die
    Chronologie innerhalb eines Drehtags korrekt, nicht nur tagesgenau.
    """
    match = _TRIM_RE.search(path.name)
    if not match:
        return None
    h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(g) for g in match.groups())
    return (h1 * 3600 + m1 * 60 + s1 + ms1 / 1000, h2 * 3600 + m2 * 60 + s2 + ms2 / 1000)


def original_name_from_trimmed(path: Path) -> str | None:
    """Dateiname (Stem) des ungeschnittenen Originals, oder `None` ohne Trim-Suffix.

    `DJI_20260720153625_0006_D-00.02.10.556-00.02.18.774-seg5.MP4` → `DJI_20260720153625_0006_D`.
    Die Bruecke zu den Originalen mit intakten GPS-Daten (Plan 0003 §A2).
    """
    match = _TRIM_RE.search(path.name)
    if not match:
        return None
    return path.name[: match.start()]


def probe_media_gps(path: Path) -> dict:
    """GPS eines Videos **oder** Fotos via `exiftool` — `{}`, wenn keine Koordinaten drinstehen.

    Videos werden sonst nur per `ffprobe` angefasst; DJI & Co. schreiben ihre Position aber in
    EXIF-/QuickTime-Tags, die `ffprobe` nicht ausgibt.
    """
    data = _run_json(["exiftool", "-j", str(path)])
    if not data:
        return {}
    entry = data[0]
    lat, lon = entry.get("GPSLatitude"), entry.get("GPSLongitude")
    if lat is None or lon is None:
        return {}
    gps = {"lat": _to_signed_degrees(lat), "lon": _to_signed_degrees(lon)}
    elevation = _to_meters(entry.get("GPSAltitude"))
    if elevation is not None:
        gps["elevation_m"] = elevation
    return gps


def _parse_container_time(tags: dict) -> datetime | None:
    """`format.tags.creation_time` bzw. `com.apple.quicktime.creationdate` als UTC-Zeitpunkt."""
    raw = tags.get("creation_time") or tags.get("com.apple.quicktime.creationdate")
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(str(raw))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _date_from_path(path: Path) -> datetime | None:
    """Taggenaues Datum aus Ordner-/Dateiname (Mitternacht), oder `None`."""
    match = _PATH_DATE_RE.search(path.as_posix())
    if not match:
        return None
    try:
        return datetime(*(int(g) for g in match.groups()), tzinfo=_WALLCLOCK_TZ)
    except ValueError:
        return None


def captured_at_for_video(path: Path, *, container_tags: dict | None = None) -> tuple[str, str]:
    """`(captured_at, captured_at_source)` eines Videos — Prioritaet laut Plan 0003 §A1.

    Container-Zeit → Dateinamen-Zeit → Datum aus dem Pfad → `mtime`; der In-Punkt aus dem
    Trim-Suffix wird, wo vorhanden, aufaddiert.

    **Zeitbasis:** die Container-Zeit ist echte UTC, die Dateinamen-Zeit die lokale Uhr der
    Kamera. Liegen beide vor, liefert der Container den Zeitpunkt und der Dateiname den
    Zonen-Offset — das Ergebnis ist die lokale Wanduhrzeit (Quelle `container+name`), also
    dieselbe Zeitbasis wie bei den Fotos. Ohne Dateinamen-Zeit ist kein Offset ableitbar, dann
    bleibt es bei der Container-Zeit (Quelle `container`) — das ist dann moeglicherweise um den
    Zonen-Offset verschoben, aber es wird nichts geraten, und `captured_at_source` sagt es.
    """
    container = _parse_container_time(container_tags or {})
    from_name = captured_at_from_name(path)

    if container is not None and from_name is not None:
        # Der Container ist die Autoritaet fuer den Zeitpunkt, der Dateiname fuer die Zone.
        # Beide beschreiben den Start des Originalclips, die Differenz ist der Zonen-Offset.
        base, source = container + (from_name - container), "container+name"
    elif container is not None:
        base, source = container, "container"
    elif from_name is not None:
        base, source = from_name, "name"
    else:
        from_path = _date_from_path(path)
        if from_path is not None:
            base, source = from_path, "path-date"
        else:
            base, source = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC), "mtime"

    trim = trim_offset_from_name(path)
    if trim is not None and source != "mtime":
        base += timedelta(seconds=trim[0])
        source += "+trim"
    return base.isoformat(), source


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


def probe_duration(path: Path) -> float:
    """Laufzeit einer beliebigen Mediendatei in Sekunden, auch ohne Video-Stream.

    `probe_video` wirft bei reinen Audiodateien (`kein Video-Stream gefunden`), die Musiktracks
    eines Projekts sind aber genau das. Gebraucht fuer die QC-Regel "Musikquelle deckt die
    Timeline ab": ist ein Track kuerzer als die Timeline verlangt, endet die Musik mitten im
    Film und der Rest laeuft stumm weiter -- im Rendervorgang faellt das nirgends auf
    (gefunden 2026-08-09 am `vlog-edit`-Preview: 11,4s Stille am Schluss).
    """
    data = _run_json(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", str(path)]
    )
    try:
        return float(data["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ProbeError(f"{path}: keine Laufzeit ermittelbar") from exc


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
    captured_at, captured_at_source = captured_at_for_video(path, container_tags=tags)
    trim = trim_offset_from_name(path)

    return {
        "captured_at": captured_at,
        "captured_at_source": captured_at_source,
        **({"trim_in_s": trim[0], "trim_out_s": trim[1]} if trim else {}),
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
        elevation = _to_meters(entry.get("GPSAltitude"))
        if elevation is not None:
            gps["elevation_m"] = elevation

    make, model = entry.get("Make"), entry.get("Model")
    return {
        "captured_at": captured_at,
        "gps": gps,
        "make": make,
        "model": model,
        "source_guess": guess_source(make, model, name_hint=path.name),
    }


def _to_meters(value: float | str | None) -> float | None:
    """exiftool liefert die Hoehe als float oder als `"1234.5 m"` / `"12 m Below Sea Level"`."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    number = ""
    for char in text:
        if char.isdigit() or (char in "-." and not number.endswith(char)):
            number += char
        elif number:
            break
    if not number:
        return None
    try:
        meters = float(number)
    except ValueError:
        return None
    return -meters if "below" in text.lower() else meters


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
