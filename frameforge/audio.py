"""BPM/Beats/Energie, Ducking-Kurven."""

from __future__ import annotations

import json
from pathlib import Path

import librosa
import numpy as np

from frameforge.ingest import hash_file
from frameforge.project import Project

_ENERGY_SAMPLE_INTERVAL_S = 0.5


def analyze_track(path: Path) -> dict:
    """BPM, Beat-Grid, Energiekurve eines Musiktracks.

    Energiekurve auf `_ENERGY_SAMPLE_INTERVAL_S`-Schritte heruntergesampelt (RMS ist von
    Natur aus feinkoernig, ~1000 Punkte pro Minute waeren fuer Sync-Zwecke unnoetig grosz).
    """
    y, sr = librosa.load(str(path), sr=None, mono=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    # Neuere librosa-Versionen liefern `tempo` als (1,)-Array statt Skalar -> robust auspacken.
    tempo = float(np.atleast_1d(tempo)[0])
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    rms = librosa.feature.rms(y=y)[0]
    rms_times = librosa.times_like(rms, sr=sr)
    duration = float(librosa.get_duration(y=y, sr=sr))

    energy_curve = []
    t = 0.0
    while t <= duration:
        idx = int(np.argmin(np.abs(rms_times - t)))
        energy_curve.append({"t": round(t, 2), "rms": round(float(rms[idx]), 4)})
        t += _ENERGY_SAMPLE_INTERVAL_S

    return {
        "bpm": round(tempo, 2),
        "duration": round(duration, 2),
        "beat_grid": [round(float(b), 3) for b in beat_times],
        "energy_curve": energy_curve,
    }


def analyze_and_cache(project: Project, track_path: Path) -> dict:
    """Wie `analyze_track`, aber gecacht unter `music/analysis/<hash>.json` (Plan §1/§3:

    "Analyse genau einmal pro Datei" gilt auch fuer Musik, nicht nur fuer Video-/Foto-Assets).
    """
    track_hash = hash_file(track_path).split(":", 1)[1]
    cache_path = project.music_analysis_dir / f"{track_hash}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    analysis = analyze_track(track_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(analysis, indent=2))
    return analysis


def duck_curve(
    music_track: dict,
    speech_windows: list[tuple[float, float]],
    *,
    duck_db: float,
    fade_s: float = 0.3,
) -> list[dict]:
    """Gain-Keyframes (`t`, `gain_db`) fuer Musik-Ducking waehrend O-Ton-Fenstern.

    0 dB ausserhalb der Fenster, sanfte Rampen (`fade_s`) auf `duck_db` herunter und wieder
    hoch statt harter Sprünge — glatter als die statischen `enable`-Fenster, die
    `render.build_filtergraph` aktuell nutzt (siehe PROGRESS.md M2.1 fuer den Stand der
    Integration).
    """
    points: list[dict] = []
    for start, end in sorted(speech_windows):
        points.append({"t": round(max(0.0, start - fade_s), 3), "gain_db": 0.0})
        points.append({"t": round(start, 3), "gain_db": duck_db})
        points.append({"t": round(end, 3), "gain_db": duck_db})
        points.append({"t": round(end + fade_s, 3), "gain_db": 0.0})
    return points
