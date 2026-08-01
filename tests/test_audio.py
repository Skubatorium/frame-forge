"""Tests fuer BPM/Beat-Grid/Energiekurve-Analyse und Ducking-Kurven."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from frameforge import project as project_module
from frameforge.audio import (
    analyze_and_cache,
    analyze_track,
    duck_curve,
    nearest_beat,
    segment_plan,
)
from frameforge.project import ProjectConfig, resolve_project

FIXTURES = Path(__file__).parent / "fixtures"


def test_analyze_track_returns_expected_shape():
    result = analyze_track(FIXTURES / "tone.wav")

    assert result["duration"] == pytest.approx(4.0, abs=0.1)
    assert isinstance(result["bpm"], float)
    assert isinstance(result["beat_grid"], list)
    assert len(result["energy_curve"]) >= 5
    for point in result["energy_curve"]:
        assert set(point.keys()) == {"t", "rms"}


def test_energy_curve_varies_due_to_tremolo():
    result = analyze_track(FIXTURES / "tone.wav")
    values = [p["rms"] for p in result["energy_curve"]]
    assert max(values) > min(values)


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    root = projects_dir / "proto"
    root.mkdir()
    ProjectConfig(name="proto", media_root=tmp_path / "media").save(root / "project.yaml")
    return resolve_project("proto")


def test_analyze_and_cache_writes_cache_file(proj):
    track = FIXTURES / "tone.wav"
    result = analyze_and_cache(proj, track)

    cache_files = list(proj.music_analysis_dir.glob("*.json"))
    assert len(cache_files) == 1
    cached = json.loads(cache_files[0].read_text())
    assert cached == result


def test_analyze_and_cache_second_call_reads_cache_without_reanalyzing(proj, monkeypatch):
    track = FIXTURES / "tone.wav"
    analyze_and_cache(proj, track)

    calls = []
    monkeypatch.setattr(
        "frameforge.audio.analyze_track", lambda p: calls.append(p) or {"should": "not run"}
    )
    result = analyze_and_cache(proj, track)

    assert calls == []
    assert "should" not in result  # kam aus dem Cache, nicht aus dem gepatchten analyze_track


def test_analyze_and_cache_identical_file_at_different_path_reuses_cache(proj, tmp_path):
    track_a = FIXTURES / "tone.wav"
    track_b = tmp_path / "tone_copy.wav"
    shutil.copy2(track_a, track_b)  # copy2 erhaelt mtime -> identischer hash_file()-Schluessel

    analyze_and_cache(proj, track_a)
    analyze_and_cache(proj, track_b)

    # Gleicher Inhalt + gleiche mtime -> gleicher Hash -> nur EIN Cache-Eintrag (Token-
    # Disziplin: nicht zweimal dieselbe Datei analysieren, nur weil sie an einem anderen
    # Pfad liegt).
    assert len(list(proj.music_analysis_dir.glob("*.json"))) == 1


# -- duck_curve -----------------------------------------------------------


def test_duck_curve_single_window_has_four_points():
    points = duck_curve({}, [(1.0, 2.0)], duck_db=-14)
    assert [p["gain_db"] for p in points] == [0.0, -14, -14, 0.0]
    assert points[0]["t"] < points[1]["t"] == 1.0
    assert points[2]["t"] == 2.0 < points[3]["t"]


def test_duck_curve_multiple_windows_are_sorted_by_start():
    points = duck_curve({}, [(5.0, 6.0), (1.0, 2.0)], duck_db=-10)
    times = [p["t"] for p in points]
    assert times == sorted(times)


def test_duck_curve_clamps_lead_in_at_zero():
    points = duck_curve({}, [(0.1, 1.0)], duck_db=-10, fade_s=0.5)
    assert points[0]["t"] == 0.0


# -- F: Musik-Segmente, Blenden, Stille (Plan 0003) ---------------------------------

TRACKS = [
    {"src": "music/a.wav", "duration": 40.0, "beat_grid": [0.0, 10.0, 20.0, 29.0, 40.0]},
    {"src": "music/b.wav", "duration": 60.0, "beat_grid": [0.0, 15.0, 30.0, 45.0]},
]


def test_nearest_beat_snaps_to_the_grid():
    assert nearest_beat(28.0, [0.0, 10.0, 29.0]) == 29.0
    assert nearest_beat(5.0, []) == 5.0  # ohne Grid unveraendert


def test_segment_plan_fits_tracks_to_sections():
    plan = segment_plan(TRACKS, [(0.0, 30.0), (30.0, 75.0)])
    assert [p["id"] for p in plan] == ["music-01", "music-02"]
    assert plan[0]["tl_in"] == 0.0
    assert plan[1]["tl_in"] == 30.0
    assert plan[0]["dur"] == 29.0  # auf den Beat bei 29.0 gezogen statt 30.0
    assert plan[0]["fade_in_s"] == 0.0  # erster Titel startet ohne Blende
    assert plan[0]["fade_out_s"] > 0
    assert plan[1]["fade_in_s"] > 0


def test_segment_plan_gap_creates_real_silence():
    plan = segment_plan(TRACKS, [(0.0, 30.0), (30.0, 75.0)], gap_s=3.0)
    first_end = plan[0]["tl_in"] + plan[0]["dur"]
    assert plan[1]["tl_in"] >= first_end + 2.0  # hoerbare Stille dazwischen


def test_segment_plan_never_exceeds_the_track_length():
    short = [{"src": "music/s.wav", "duration": 5.0, "beat_grid": [0.0, 2.5, 5.0]}]
    plan = segment_plan(short, [(0.0, 60.0)])
    assert plan[0]["dur"] <= 5.0  # kein Loop, keine Streckung


def test_segment_plan_requires_one_track_per_section():
    with pytest.raises(ValueError, match="1:1"):
        segment_plan(TRACKS, [(0.0, 10.0)])
