"""Farbraum-Normalisierung (`frameforge.color`).

Hintergrund: `vlog-edit` kam mit `yuvj420p / pc / bt470bg` heraus, weil die MJPEG-Foto-Inputs
ihre Tags durch den ganzen Graphen durchgereicht haben. Chromium befolgt diese Tags und zeigte
dadurch kraeftige Rotstiche auf Hauttoenen, QuickTime ignoriert sie und zeigte dieselbe Datei
unauffaellig. Die Tests hier halten beide Haelften des Fixes fest: die Normalisierung je Quelle
und die HLG→BT.709-Kurve.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from frameforge import color


def _chain(monkeypatch, pix_fmt, rng, space, transfer, **kwargs):
    monkeypatch.setattr(
        color, "probe_source_color", lambda _p: (pix_fmt, rng, space, transfer)
    )
    return color.normalize_chain(Path("/media/x"), **kwargs)


def test_every_source_class_ends_on_bt709_tv(monkeypatch):
    """Egal welche Quelle: die Kette endet auf yuv420p + BT.709/TV-Tags."""
    sources = [
        ("yuv420p10le", "tv", "bt2020nc", "arib-std-b67"),  # iPhone HLG
        ("yuvj420p", "pc", "bt470bg", ""),  # JPEG-Foto-Proxy
        ("yuv420p10le", "tv", "bt709", "bt709"),  # Drohne SDR
        ("", "", "", ""),  # ffprobe liefert nichts
    ]
    for src in sources:
        chain = _chain(monkeypatch, *src, hlg_lut=Path("/tmp/x.cube"))
        assert chain[-2] == "format=yuv420p", src
        assert chain[-1] == color.output_params_filter(), src


def test_hlg_source_gets_the_lut(monkeypatch):
    chain = _chain(
        monkeypatch, "yuv420p10le", "tv", "bt2020nc", "arib-std-b67",
        hlg_lut=Path("/tmp/hlg.cube"),
    )
    # `format=gbrp` muss VOR der LUT stehen, sonst laeuft die YUV→RGB-Konvertierung mit den
    # falschen Koeffizienten (oder zu spaet).
    assert chain[0] == "format=gbrp"
    assert chain[1] == "lut3d=file='/tmp/hlg.cube'"


def test_full_range_jpeg_is_converted_to_limited_range(monkeypatch):
    """Der eigentliche Ausloeser: Full-Range/BT.601 der Foto-Proxies explizit umrechnen."""
    chain = _chain(monkeypatch, "yuvj420p", "pc", "bt470bg", "")
    assert "in_range=full" in chain[0] and "out_range=tv" in chain[0]
    assert "in_color_matrix=bt470bg" in chain[0] and "out_color_matrix=bt709" in chain[0]


def test_sdr_source_is_not_touched_beyond_tagging(monkeypatch):
    """BT.709-Material darf keine Konvertierung abbekommen — nur die Tags."""
    chain = _chain(monkeypatch, "yuv420p", "tv", "bt709", "bt709")
    assert chain == ["format=yuv420p", color.output_params_filter()]


def test_hlg_without_lut_generates_one(tmp_path, monkeypatch):
    monkeypatch.setattr(color, "_default_lut_dir", lambda: tmp_path)
    chain = _chain(monkeypatch, "yuv420p10le", "tv", "bt2020nc", "arib-std-b67")
    lut = tmp_path / f"hlg_bt2020_to_bt709_{color._LUT_SIZE}.cube"
    assert lut.exists()
    assert str(lut) in chain[1]


# -- HLG-Kurve ----------------------------------------------------------------------

def _grey(signal: float) -> float:
    return float(color._hlg_to_bt709(np.array([[signal, signal, signal]]))[0][0])


def test_hlg_curve_endpoints():
    assert _grey(0.0) == pytest.approx(0.0, abs=1e-6)
    assert _grey(1.0) == pytest.approx(1.0, abs=1e-3)


def test_hlg_diffuse_white_stays_white():
    """HLG-Diffusweiss (Signal 0.75) muss in SDR nahe Weiss landen, nicht auf halber Höhe.

    Mit BT.2100-Systemgamma 1.2 plus Filmkurve kam hier ~0.71 heraus — die Clips waeren
    sichtbar dunkler geworden als im bisherigen Export.
    """
    assert _grey(color._HLG_DIFFUSE_WHITE_SIGNAL) > 0.9


def test_hlg_curve_is_monotonic_and_neutral():
    ramp = np.linspace(0.0, 1.0, 64)
    mapped = color._hlg_to_bt709(np.stack([ramp, ramp, ramp], axis=-1))
    assert np.all(np.diff(mapped[:, 0]) >= -1e-9), "Kurve ist nicht monoton"
    # Grauachse muss grau bleiben: ein Farbstich hier waere ein Fehler in der Gamut-Matrix.
    assert np.allclose(mapped[:, 0], mapped[:, 1], atol=2e-3)
    assert np.allclose(mapped[:, 0], mapped[:, 2], atol=2e-3)


def test_lut_file_is_valid_cube(tmp_path):
    lut = color.hlg_to_bt709_lut(tmp_path, size=9)
    lines = [ln for ln in lut.read_text().splitlines() if ln and not ln.startswith("#")]
    assert lines[0] == "LUT_3D_SIZE 9"
    values = [ln for ln in lines if len(ln.split()) == 3 and not ln.startswith(("LUT", "DOMAIN"))]
    assert len(values) == 9**3
    assert all(0.0 <= float(v) <= 1.0 for ln in values for v in ln.split())


def test_lut_generation_is_idempotent(tmp_path):
    first = color.hlg_to_bt709_lut(tmp_path, size=9)
    stamp = first.stat().st_mtime_ns
    assert color.hlg_to_bt709_lut(tmp_path, size=9) == first
    assert first.stat().st_mtime_ns == stamp, "LUT wurde unnoetig neu geschrieben"
