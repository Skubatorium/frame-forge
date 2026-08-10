"""Farbraum-Normalisierung — jede Quelle auf BT.709/TV, bevor irgendein Look darauf kommt.

Warum es dieses Modul gibt (Nutzer-Report 2026-08-10, `vlog-edit`): der Fundus mischt drei
Farbräume, und `render` hat sie bis dahin alle unbehandelt in denselben Filtergraph gekippt:

- iPhone-Video: `bt2020nc` / `arib-std-b67` (HLG, HDR), 10 bit — 41 Clips im vlog-edit
- Drohnen-Video: `bt709` / `bt709` — 65 Clips
- HEIC-Foto → JPEG-Proxy: `yuvj420p`, Full-Range, `bt470bg` (BT.601) — 61 Clips

Zwei Folgen, beide gemessen:

1. **Die Foto-Inputs haben die Farbtags des ganzen Films gekapert.** Ohne explizite Vorgabe
   übernimmt ffmpeg die Metadaten aus dem Filtergraph; die MJPEG-Frames bringen `pc` +
   `bt470bg` mit, und `-pix_fmt yuv420p` greift dagegen nicht (ffmpeg hält `yuv420p` und
   `yuvj420p` für kompatibel). Ergebnis: `vlog-edit_*.mp4` trug `yuvj420p / pc / bt470bg`,
   während `drone-edit_*.mp4` (keine Fotos, alle Quellen bt709) korrekt `yuv420p / tv / bt709`
   trug. Player, die die Tags befolgen (Chromium), dekodieren dann mit BT.601-Matrix im
   Full-Range-Modus → kräftiger Rot-/Sättigungs-Shift, am deutlichsten auf Hauttönen. Player,
   die die Tags ignorieren (QuickTime, macOS-Vorschau), zeigen dieselbe Datei unauffällig —
   deshalb war der Fehler lokal unsichtbar und erst nach dem Upload da.
2. **Die HLG-Clips wurden als BT.709 durchgereicht.** Ein HLG-Signal auf einer BT.709-Kurve
   gelesen ist flau und entsättigt; schneidet der Film davon auf ein Foto oder einen
   Drohnenshot, springt die Farbigkeit hart. Genau das ist der Umschalter bei 1:43.

Der Fix ist bewusst früh: **jedes** Segment wird direkt an der Quelle nach BT.709/TV
konvertiert, danach existiert im Graphen nur noch ein Farbraum. Look-Filter (`grade_filter`,
Projekt-LUT) arbeiten damit auf definierten Werten statt auf dem, was der jeweilige Clip
zufällig mitbringt.

**Kein `zscale`.** Der Homebrew-ffmpeg dieser Umgebung ist ohne libzimg gebaut, und der
`colorspace`-Filter kennt `arib-std-b67` nicht (`Unable to parse "itrc" option value`).
HLG→BT.709 läuft deshalb über eine hier erzeugte 3D-LUT — reine Numpy-Mathematik, keine neue
Systemabhängigkeit, und das Ergebnis ist als `.cube`-Datei reproduzierbar und inspizierbar.
"""

from __future__ import annotations

import json
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np

__all__ = [
    "OUTPUT_COLOR_ARGS",
    "SourceColor",
    "hlg_to_bt709_lut",
    "normalize_chain",
    "output_params_filter",
    "probe_source_color",
]

# Zieltags am Encoder. Ohne diese schreibt libx264, was die Filterkette gerade durchreicht.
OUTPUT_COLOR_ARGS = [
    "-colorspace", "bt709",
    "-color_primaries", "bt709",
    "-color_trc", "bt709",
    "-color_range", "tv",
]

# Muss identisch zu OUTPUT_COLOR_ARGS sein: der Encoder schreibt nur Tags, `setparams` sorgt
# dafuer, dass die Frames auch tatsaechlich so vorliegen.
_TARGET_PARAMS = "range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709"

_HLG_TRANSFERS = {"arib-std-b67"}
_FULL_RANGE_PIX_FMTS = {"yuvj420p", "yuvj422p", "yuvj444p", "yuvj440p"}


class SourceColor:
    """Farbklasse einer Quelldatei — bestimmt, welche Normalisierung sie braucht."""

    HLG = "hlg"  # BT.2020 + HLG-Transfer (iPhone-HDR)
    FULL_RANGE = "full_range"  # JPEG/MJPEG: Full-Range, BT.601-Matrix
    SDR = "sdr"  # bereits BT.709/TV oder unspezifiziert-SDR


def output_params_filter() -> str:
    """`setparams`-Filter, der Frames als BT.709/TV kennzeichnet."""
    return f"setparams={_TARGET_PARAMS}"


@lru_cache(maxsize=4096)
def probe_source_color(path: str) -> tuple[str, str, str, str]:
    """`(pix_fmt, color_range, color_space, color_transfer)` des ersten Videostreams.

    Leere Strings, wo ffprobe nichts liefert (unspezifiziert ist bei SDR-Material der
    Normalfall und kein Fehler). Ergebnis gecached — ein Export fasst dieselbe Datei oft
    mehrfach an, und `ffprobe` pro Clip waere bei 170 Segmenten spuerbar.
    """
    try:
        raw = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=pix_fmt,color_range,color_space,color_transfer",
                "-of", "json", path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        ).stdout
        stream = json.loads(raw)["streams"][0]
    except (subprocess.SubprocessError, json.JSONDecodeError, KeyError, IndexError):
        return ("", "", "", "")
    return (
        stream.get("pix_fmt") or "",
        stream.get("color_range") or "",
        stream.get("color_space") or "",
        stream.get("color_transfer") or "",
    )


def classify(path: Path) -> str:
    """Farbklasse einer Quelldatei (`SourceColor.*`)."""
    pix_fmt, color_range, _space, transfer = probe_source_color(str(path))
    if transfer in _HLG_TRANSFERS:
        return SourceColor.HLG
    if color_range == "pc" or pix_fmt in _FULL_RANGE_PIX_FMTS:
        return SourceColor.FULL_RANGE
    return SourceColor.SDR


def _default_lut_dir() -> Path:
    from frameforge.project import CACHE_ROOT

    return CACHE_ROOT / "luts"


def normalize_chain(path: Path, *, hlg_lut: Path | None = None) -> list[str]:
    """Filter, die `path` von seinem Quellfarbraum nach BT.709/TV bringen.

    Wird pro Segment direkt hinter Fit/Ken-Burns eingehaengt, also **vor** Farbangleichung und
    Look — sonst wuerde ein Grade auf drei verschiedenen Farbraeumen drei verschiedene
    Ergebnisse liefern.
    """
    kind = classify(path)
    chain: list[str] = []
    if kind == SourceColor.HLG:
        if hlg_lut is None:
            hlg_lut = hlg_to_bt709_lut(_default_lut_dir())
        # `format=gbrp` erzwingt den YUV→RGB-Schritt mit den Quelltags (BT.2020, TV) *vor*
        # der LUT. Ohne das wuerde ffmpeg die Konvertierung erst spaeter und moeglicherweise
        # mit den falschen Koeffizienten einziehen.
        chain.append("format=gbrp")
        chain.append(f"lut3d=file='{hlg_lut}'")
        chain.append("scale=out_range=tv:out_color_matrix=bt709")
    elif kind == SourceColor.FULL_RANGE:
        # JPEG-Proxies der HEIC-Fotos: Full-Range mit BT.601-Matrix. Beides explizit angeben,
        # sonst raet swscale und die Helligkeit kippt.
        chain.append(
            "scale=in_range=full:in_color_matrix=bt470bg:out_range=tv:out_color_matrix=bt709"
        )
    chain.append("format=yuv420p")
    chain.append(output_params_filter())
    return chain


# -- HLG → BT.709 SDR ----------------------------------------------------------------

_HLG_A = 0.17883277
_HLG_B = 1.0 - 4.0 * _HLG_A
_HLG_C = 0.5 - _HLG_A * float(np.log(4.0 * _HLG_A))

# BT.2020 → BT.709 im Linearlicht.
_BT2020_TO_BT709 = np.array(
    [
        [1.6605, -0.5876, -0.0728],
        [-0.1246, 1.1329, -0.0083],
        [-0.0182, -0.1006, 1.1187],
    ]
)

# HLG-Diffusweiss liegt laut BT.2408 beim Signalwert 0.75; im Szenenlicht sind das ~0.265 des
# Peaks. Genau darauf wird normiert, damit Diffusweiss in SDR wieder Weiss ist und nicht auf
# halbe Helligkeit faellt. Darueber bleiben ~3.8 Blenden Headroom fuer Spitzlichter.
_HLG_DIFFUSE_WHITE_SIGNAL = 0.75
_HIGHLIGHT_KNEE = 0.7  # bis hierhin 1:1, danach weiche Schulter gegen 1.0

_LUT_SIZE = 33


def _hlg_inverse_oetf(signal: np.ndarray) -> np.ndarray:
    """HLG-Signal (0..1) → Szenenlicht (0..1), ARIB STD-B67 / BT.2100."""
    lower = signal * signal / 3.0
    upper = (np.exp((np.clip(signal, 0.5, None) - _HLG_C) / _HLG_A) + _HLG_B) / 12.0
    return np.where(signal <= 0.5, lower, upper)


def _highlight_rolloff(x: np.ndarray) -> np.ndarray:
    """Weiche Schulter: unterhalb `_HIGHLIGHT_KNEE` identisch, darueber asymptotisch gegen 1.0.

    Bewusst **keine** Filmkurve (Hable/Reinhard): die komprimieren schon die Mitteltoene und
    haetten das Material sichtbar abgedunkelt. Hier bleibt alles bis 70 % unangetastet — der
    Look der Clips aendert sich nicht, nur die Spitzlichter oberhalb SDR-Weiss werden
    eingefangen statt geclippt.
    """
    knee = _HIGHLIGHT_KNEE
    head = 1.0 - knee
    rolled = knee + head * (1.0 - np.exp(-(np.clip(x, knee, None) - knee) / head))
    return np.where(x <= knee, x, rolled)


def _bt709_oetf(linear: np.ndarray) -> np.ndarray:
    """BT.709-Uebertragungsfunktion (Linearlicht → Signal)."""
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(linear < 0.018, 4.5 * linear, 1.099 * np.power(linear, 0.45) - 0.099)


def _hlg_to_bt709(rgb: np.ndarray) -> np.ndarray:
    """HLG/BT.2020-Signal → BT.709-SDR-Signal, beides R'G'B' in 0..1.

    Schritte: Signal → Szenenlicht → auf Diffusweiss normieren → Gamut BT.2020→BT.709 →
    Spitzlichter-Schulter → BT.709-OETF. Die Gamut-Konvertierung gehoert vor die Schulter,
    sonst laufen Farben, die BT.709 gar nicht darstellen kann, erst durch die Kompression und
    werden danach trotzdem hart geclippt.

    **Ohne OOTF (Systemgamma 1.0).** BT.2100 sieht fuer einen 1000-nit-Schirm γ=1.2 vor; auf
    100 nits SDR heruntergerechnet liegt das Systemgamma nahe 1.0. Wichtiger noch: mit γ=1.2
    plus anschliessendem Tonemapping kam Diffusweiss bei ~0.71 statt ~0.94 heraus — die Clips
    waeren spuerbar dunkler geworden als im bisherigen Export. Der Nutzer hat am Bild der
    Videoclips nichts auszusetzen; der Fix soll den Farbraum richtigstellen, nicht den Look
    umbauen.
    """
    scene = _hlg_inverse_oetf(rgb)
    diffuse_white = float(_hlg_inverse_oetf(np.array(_HLG_DIFFUSE_WHITE_SIGNAL)))
    scene = scene / diffuse_white

    linear709 = np.tensordot(scene, _BT2020_TO_BT709.T, axes=([-1], [0]))
    linear709 = np.clip(linear709, 0.0, None)

    return _bt709_oetf(_highlight_rolloff(linear709))


def hlg_to_bt709_lut(cache_dir: Path, *, size: int = _LUT_SIZE) -> Path:
    """Erzeugt (einmalig) die HLG→BT.709-`.cube`-LUT im Cache und gibt ihren Pfad zurueck.

    Idempotent: existiert die Datei, wird sie wiederverwendet. Der Dateiname traegt die
    Stuetzstellenzahl, damit eine geaenderte Aufloesung nicht stillschweigend eine alte LUT
    weiterbenutzt.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"hlg_bt2020_to_bt709_{size}.cube"
    if out.exists():
        return out

    axis = np.linspace(0.0, 1.0, size)
    # .cube-Reihenfolge: rot laeuft am schnellsten, blau am langsamsten.
    b, g, r = np.meshgrid(axis, axis, axis, indexing="ij")
    grid = np.stack([r, g, b], axis=-1).reshape(-1, 3)
    mapped = _hlg_to_bt709(grid)

    lines = [
        "# FrameForge: HLG (BT.2020) -> BT.709 SDR",
        "# erzeugt von frameforge.color.hlg_to_bt709_lut - nicht von Hand editieren",
        f"LUT_3D_SIZE {size}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
    ]
    lines.extend(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}" for v in mapped)
    tmp = out.with_suffix(".cube.tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.replace(out)  # atomar: ein abgebrochener Lauf laesst keine halbe LUT liegen
    return out
