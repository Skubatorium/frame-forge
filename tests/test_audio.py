"""Tests fuer BPM/Beat-Grid/Energiekurve-Analyse und Ducking-Kurven."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from frameforge import project as project_module
from frameforge.audio import analyze_and_cache, analyze_track, duck_curve
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
