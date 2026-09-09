"""Audio-Vorbereitung für Export `JGA` Runde 2 (Tasks T3 + T4).

Erzeugt die Dateien, die `music/*` (gitignoriert) NICHT versioniert, aber reproduzierbar
sein müssen:

  T3  music/sfx/sfx-cast-whoosh.wav        (Mixkit SFX #1485, "Fast whoosh transition")
      music/sfx/sfx-cast-stamp.wav         (Mixkit SFX #752, Kategorie "thud")
      music/sfx/sfx-cast-stamp-micha.wav   (#752, -5 Halbtöne + kurzer Raum, für den Bräutigam)
      -> Mixkit Free License (kommerziell frei, keine Attribution, nicht als Stock weiter).

  T4  music/01 Miserlou (loop-196).m4a     (Miserlou 136 s -> ~196 s, nahtlose interne
      Wiederholung eines 60-s-Phrasenblocks Downbeat->Downbeat, 28 ms Equal-Power-Xfade
      an beiden Nahtstellen; kein Zeitdehnen).

KEIN ffmpeg (Gate-Hook `.claude/hooks/gate.py`): Dekodieren/Encoden über `afconvert`
(macOS), Verarbeitung über soundfile/numpy/librosa. m4a-Quellen kann soundfile nicht
lesen -> vorher per afconvert nach temp-WAV.

Aufruf von Repo-Root:
  ./.venv/bin/python projects/michael-jga-2026/exports/JGA/audio-prep.py [--sfx] [--loop]
Ohne Flag: beides. Mixkit-Rohdateien werden bei Bedarf nach /tmp/jga-sfx-src/ geladen.
"""
from __future__ import annotations

import subprocess
import sys
import urllib.request
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

MUSIC = Path("projects/michael-jga-2026/music")
SFX_DIR = MUSIC / "sfx"
SRC_DIR = Path("/tmp/jga-sfx-src")
SR = 48000

# Mixkit-Asset-URL-Muster: assets.mixkit.co/active_storage/sfx/<id>/<id>.wav
MIXKIT = {
    "whoosh": 1485,   # "Fast whoosh transition"
    "thud": 752,      # Kategorie "thud", kurzer punchiger Impact
}


def _fetch_mixkit() -> dict[str, Path]:
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, sid in MIXKIT.items():
        p = SRC_DIR / f"mixkit-{sid}.wav"
        if not p.exists():
            url = f"https://assets.mixkit.co/active_storage/sfx/{sid}/{sid}.wav"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            p.write_bytes(urllib.request.urlopen(req).read())  # noqa: S310
        out[name] = p
    return out


def _load_mono(p: Path) -> np.ndarray:
    y, sr = sf.read(p, always_2d=True)
    y = y.mean(axis=1)
    if sr != SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    return y.astype(np.float32)


def _trim_head(y: np.ndarray, thresh_db: float = -50.0) -> np.ndarray:
    thr = 10 ** (thresh_db / 20)
    idx = int(np.argmax(np.abs(y) > thr))
    return y[max(0, idx - int(0.003 * SR)):]


def _peak_norm(y: np.ndarray, target_db: float) -> np.ndarray:
    peak = float(np.max(np.abs(y))) or 1.0
    return y * (10 ** (target_db / 20) / peak)


def _fade_out(y: np.ndarray, dur_s: float) -> np.ndarray:
    n = min(len(y), int(dur_s * SR))
    if n:
        y = y.copy()
        y[-n:] *= np.linspace(1.0, 0.0, n) ** 1.5
    return y


def _stereo_write(path: Path, y: np.ndarray) -> None:
    y = np.clip(y, -1.0, 1.0)
    sf.write(path, np.stack([y, y], axis=1), SR, subtype="PCM_16")
    print(f"  {path.name:28s} {len(y)/SR:0.3f}s  "
          f"peak {20*np.log10(np.max(np.abs(y))+1e-9):+0.1f} dBFS")


def build_sfx() -> None:
    src = _fetch_mixkit()
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    print("T3 — Cast-Intro-SFX:")

    w = _trim_head(_load_mono(src["whoosh"]))[: int(0.42 * SR)]
    _stereo_write(SFX_DIR / "sfx-cast-whoosh.wav", _peak_norm(_fade_out(w, 0.10), -12.0))

    s = _trim_head(_load_mono(src["thud"]))[: int(0.40 * SR)]
    _stereo_write(SFX_DIR / "sfx-cast-stamp.wav", _peak_norm(_fade_out(s, 0.05), -10.0))

    m = _trim_head(_load_mono(src["thud"]))
    m = librosa.effects.pitch_shift(m, sr=SR, n_steps=-5.0)
    echo = np.pad(m * 0.35, (int(0.022 * SR), 0))
    m = np.pad(m, (0, int(0.18 * SR)))
    echo = np.pad(echo, (0, max(0, len(m) - len(echo))))[: len(m)]
    m = _fade_out((m + echo)[: int(0.55 * SR)], 0.12)
    _stereo_write(SFX_DIR / "sfx-cast-stamp-micha.wav", _peak_norm(m, -9.0))


def build_miserlou_loop(target_s: float = 196.0, xfade_ms: float = 28.0) -> None:
    print("T4 — Miserlou Loop:")
    src_m4a = MUSIC / "01 Miserlou.m4a"
    out_m4a = MUSIC / "01 Miserlou (loop-196).m4a"
    tmp_wav = SRC_DIR / "miserlou_src.wav"
    tmp_wav.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(src_m4a), str(tmp_wav)],
                   check=True)

    y, sr = sf.read(tmp_wav, always_2d=True)
    y = y.astype(np.float64)
    n_ch = y.shape[1]
    dur = len(y) / sr
    mono = y.mean(axis=1)

    _, beats = librosa.beat.beat_track(y=mono, sr=sr, units="time")
    oenv = librosa.onset.onset_strength(y=mono, sr=sr)
    o_t = librosa.times_like(oenv, sr=sr)
    phase = int(np.argmax([
        sum(float(np.interp(beats[i], o_t, oenv)) for i in range(p, len(beats), 4))
        for p in range(4)
    ]))
    downbeats = beats[phase::4]
    need = target_s - dur

    best = None
    for i, a in enumerate(downbeats):
        if not (dur * 0.20 <= a <= dur * 0.60):
            continue
        for b in downbeats[i + 1:]:
            if b > dur * 0.92:
                break
            err = abs((b - a) - need)
            if best is None or err < best[0]:
                best = (err, a, b)
    _, a, b = best
    seg_len = b - a

    xf = int(sr * xfade_ms / 1000)
    fi = np.sqrt(np.linspace(0, 1, xf))
    fo = np.sqrt(np.linspace(1, 0, xf))
    if n_ch > 1:
        fi, fo = fi[:, None], fo[:, None]
    sa, sb = int(a * sr), int(b * sr)

    def splice(left, right):
        k = min(xf, len(left), len(right))
        if k == 0:
            return np.concatenate([left, right])
        mixed = left[-k:] * fo[-k:] + right[:k] * fi[-k:]
        return np.concatenate([left[:-k], mixed, right[k:]])

    out = splice(splice(y[:sb], y[sa:sb]), y[sb:])

    loop_db = np.concatenate([downbeats[downbeats <= b], downbeats[downbeats > b] + seg_len])
    cand = loop_db[np.abs(loop_db - target_s) < 2.5]
    if len(cand) and cand.max() < len(out) / sr:
        cut = float(cand[np.argmin(np.abs(cand - target_s))])
        fo40 = np.linspace(1, 0, int(sr * 0.04))
        if n_ch > 1:
            fo40 = fo40[:, None]
        out = out[: int(cut * sr)].copy()
        out[-len(fo40):] *= fo40

    tmp_out = SRC_DIR / "miserlou_loop.wav"
    sf.write(tmp_out, np.clip(out, -1, 1), sr, subtype="PCM_24")
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "256000",
                    str(tmp_out), str(out_m4a)], check=True)
    print(f"  {out_m4a.name}  {len(out)/sr:0.3f}s  "
          f"Nahtstellen ~{b:0.1f}s / ~{b+seg_len:0.1f}s")


if __name__ == "__main__":
    flags = set(sys.argv[1:])
    if not flags or "--sfx" in flags:
        build_sfx()
    if not flags or "--loop" in flags:
        build_miserlou_loop()
