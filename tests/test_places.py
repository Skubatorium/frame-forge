"""Tests fuer Tag-/Etappen-/Ortszuordnung (Plan 0003, §A4/A5)."""

from __future__ import annotations

import shutil

import pytest

from frameforge import project as project_module
from frameforge.index import load_assets, write_asset
from frameforge.places import (
    apply_assignment,
    places_todo,
    plan_assignment,
    set_place,
)
from frameforge.project import ProjectConfig, resolve_project

STAGES = """day,date,from,to,via,km,overnight,note
9,2026-07-28,Geiranger,Lom,Trollstigen,190,Lom,Passstraße
10,2026-07-29,Lom,Lom,,0,Lom,Standtag
"""

LOCATIONS = """name,lat,lon,type,day
Trollstigen,62.4581,7.6706,poi,9
Lom,61.8386,8.5669,overnight,9
"""


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(project_module, "CACHE_ROOT", tmp_path / "cache")

    media = tmp_path / "media"
    media.mkdir()
    shutil.copy2("tests/fixtures/clip.mp4", media / "clip.mp4")

    root = projects_dir / "p"
    root.mkdir()
    ProjectConfig(name="p", media_root=media).save(root / "project.yaml")
    project = resolve_project("p")
    project.route_dir.mkdir(parents=True, exist_ok=True)
    project.stages_csv_path.write_text(STAGES, encoding="utf-8")
    project.locations_csv_path.write_text(LOCATIONS, encoding="utf-8")
    return project


def _asset(project, asset_id, captured_at, **extra):
    asset = {
        "id": asset_id,
        "hash": f"sha256:{asset_id}",
        "path": "clip.mp4",
        "kind": "video",
        "captured_at": captured_at,
        "content": {"summary": "Testclip", "tags": []},
        "rating": 4,
        **extra,
    }
    write_asset(project, asset)
    return asset


def test_gps_position_wins_and_names_the_real_place(proj):
    """Abnahme A: Trollstigen-Clip bekommt Tag 9, Etappe Geiranger→Lom und Ort Trollstigen."""
    _asset(
        proj,
        "a1",
        "2026-07-28T14:05:00+00:00",
        gps={"lat": 62.4585, "lon": 7.6710, "place": "Geiranger-Lom/Trollstigen"},
    )

    result = plan_assignment(proj)
    apply_assignment(proj, result)

    asset = load_assets(proj)[0]
    assert asset["day"] == 9
    assert asset["stage"] == "Geiranger → Lom"
    assert asset["gps"]["place"] == "Trollstigen"
    assert asset["place_source"] == "gps"
    # Der aus dem Ordnernamen geratene Ort wird als Konflikt gemeldet, nicht still ersetzt.
    assert [(c.old_place, c.new_place) for c in result.conflicts] == [
        ("Geiranger-Lom/Trollstigen", "Trollstigen")
    ]


def test_position_far_from_any_poi_becomes_leg_note(proj):
    _asset(proj, "a2", "2026-07-28T11:00:00+00:00", gps={"lat": 62.0, "lon": 7.0})

    apply_assignment(proj, plan_assignment(proj))

    asset = load_assets(proj)[0]
    assert asset["gps"]["place"] == "unterwegs: Geiranger → Lom"
    assert asset["place_source"] == "leg"


def test_standing_day_without_position_uses_the_stage_place(proj):
    _asset(proj, "a3", "2026-07-29T09:00:00+00:00")

    apply_assignment(proj, plan_assignment(proj))

    asset = load_assets(proj)[0]
    assert asset["day"] == 10
    assert asset["gps"]["place"] == "Lom"
    assert asset["place_source"] == "stage"


def test_asset_outside_the_trip_gets_no_guessed_place(proj):
    _asset(proj, "a4", "2026-01-01T09:00:00+00:00")

    result = plan_assignment(proj)
    apply_assignment(proj, result)

    asset = load_assets(proj)[0]
    assert result.without_stage == ["a4"]
    assert asset["gps"]["place"] == "unknown"
    assert "day" not in asset


def test_asset_without_time_is_listed_not_assigned(proj):
    _asset(proj, "a5", None)

    result = plan_assignment(proj)
    assert result.without_time == ["a5"]
    assert result.changes == []


def test_gpx_position_is_used_when_the_asset_has_none(proj):
    proj.gpx_path.write_text(
        """<?xml version="1.0"?>
<gpx version="1.1" creator="test"><trk><trkseg>
<trkpt lat="62.4581" lon="7.6706"><time>2026-07-28T14:00:00Z</time></trkpt>
</trkseg></trk></gpx>
""",
        encoding="utf-8",
    )
    _asset(proj, "a6", "2026-07-28T14:01:00+00:00")

    apply_assignment(proj, plan_assignment(proj))

    asset = load_assets(proj)[0]
    assert asset["gps"]["place"] == "Trollstigen"
    assert asset["place_source"] == "gpx"


def test_manual_place_survives_without_force(proj):
    _asset(proj, "a7", "2026-07-28T11:00:00+00:00")
    set_place(proj, "a7", "Gudbrandsjuvet", kind="stop")

    result = plan_assignment(proj)
    apply_assignment(proj, result)

    asset = load_assets(proj)[0]
    assert asset["gps"]["place"] == "Gudbrandsjuvet"
    assert result.protected == ["a7"]

    # Mit --force wird derselbe Ort neu berechnet.
    apply_assignment(proj, plan_assignment(proj, force=True))
    assert load_assets(proj)[0]["gps"]["place"] == "unterwegs: Geiranger → Lom"


def test_set_place_leg_writes_the_stage_notation(proj):
    _asset(proj, "a8", "2026-07-28T11:00:00+00:00")
    updated = set_place(proj, "a8", "Geiranger → Lom", kind="leg")
    assert updated["gps"]["place"] == "unterwegs: Geiranger → Lom"
    assert updated["place_source"] == "manual"


def test_set_place_accepts_hash_and_rejects_unknown_asset(proj):
    _asset(proj, "a9", "2026-07-28T11:00:00+00:00")
    assert set_place(proj, "sha256:a9", "Åndalsnes")["gps"]["place"] == "Åndalsnes"
    with pytest.raises(KeyError):
        set_place(proj, "gibts-nicht", "X")
    with pytest.raises(ValueError, match="kind"):
        set_place(proj, "a9", "X", kind="quatsch")


def test_places_todo_lists_only_unclear_assets(proj):
    _asset(proj, "b1", "2026-07-28T11:00:00+00:00")  # -> leg, unklar
    _asset(proj, "b2", "2026-07-29T09:00:00+00:00")  # -> stage, klar
    _asset(proj, "b3", "2026-01-01T09:00:00+00:00")  # -> unknown, unklar
    apply_assignment(proj, plan_assignment(proj))

    todo = places_todo(proj)
    assert [t["id"] for t in todo] == ["b3", "b1"]  # chronologisch
    assert places_todo(proj, day=9) == [t for t in todo if t["day"] == 9]

    set_place(proj, "b1", "Trollstigen")
    assert [t["id"] for t in places_todo(proj)] == ["b3"]


def test_assignment_leaves_content_and_rating_alone(proj):
    _asset(proj, "c1", "2026-07-28T14:05:00+00:00", gps={"lat": 62.4585, "lon": 7.6710})
    before = load_assets(proj)[0]

    apply_assignment(proj, plan_assignment(proj))

    after = load_assets(proj)[0]
    assert after["content"] == before["content"]
    assert after["rating"] == before["rating"]
    assert after["hash"] == before["hash"]
