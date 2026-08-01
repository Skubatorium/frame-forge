"""Tests fuer Routengeometrie, Distanz und Hoehe (Plan 0003, §B1/§B5). Alles offline."""

from __future__ import annotations

import json

import pytest

from frameforge import project as project_module
from frameforge.gpx import (
    KmlError,
    cumulative_km,
    elevation_profile,
    haversine_km,
    parse_gpx,
    parse_kml,
    total_ascent_m,
    write_gpx,
)
from frameforge.project import ProjectConfig, resolve_project
from frameforge.route import (
    RoutingError,
    build_route_gpx,
    elevations_for,
    import_kml,
    waypoints_from_stages,
)

STAGES = """day,date,from,to,via,km,overnight,note
9,2026-07-28,Geiranger,Lom,Trollstigen,190,Lom,
"""
LOCATIONS = """name,lat,lon,type,day
Geiranger,62.1049,7.2066,city,9
Trollstigen,62.4581,7.6706,poi,9
Lom,61.8386,8.5669,overnight,9
"""

KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark><LineString>
<coordinates>7.2066,62.1049,10 7.6706,62.4581,850 8.5669,61.8386,380</coordinates>
</LineString></Placemark></Document></kml>
"""


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(project_module, "CACHE_ROOT", tmp_path / "cache")
    root = projects_dir / "p"
    root.mkdir()
    ProjectConfig(name="p", media_root=tmp_path / "media").save(root / "project.yaml")
    project = resolve_project("p")
    project.route_dir.mkdir(parents=True, exist_ok=True)
    project.stages_csv_path.write_text(STAGES, encoding="utf-8")
    project.locations_csv_path.write_text(LOCATIONS, encoding="utf-8")
    return project


# -- B1: Distanz und Hoehe ---------------------------------------------------------


def test_haversine_km_matches_known_distance():
    # Geiranger -> Lom, Luftlinie ~90 km
    assert haversine_km((62.1049, 6.9394), (61.8386, 8.5669)) == pytest.approx(90.0, abs=1.0)


def test_cumulative_km_is_monotone_and_starts_at_zero():
    track = [{"lat": 62.0, "lon": 7.0}, {"lat": 62.1, "lon": 7.0}, {"lat": 62.2, "lon": 7.0}]
    km = cumulative_km(track)
    assert len(km) == 3
    assert km[0] == 0.0
    assert km[1] < km[2]
    assert km[2] == pytest.approx(2 * km[1], rel=0.01)


def test_elevation_profile_uses_gpx_values_and_asks_only_for_gaps():
    track = [{"lat": 1.0, "lon": 1.0, "ele": 100.0}, {"lat": 2.0, "lon": 2.0, "ele": None}]
    asked: list = []

    def lookup(points):
        asked.extend(points)
        return [250.0]

    assert elevation_profile(track, lookup=lookup) == [100.0, 250.0]
    assert asked == [(2.0, 2.0)]  # nur die Luecke, nicht der ganze Track


def test_elevation_profile_without_lookup_keeps_gaps():
    track = [{"lat": 1.0, "lon": 1.0}, {"lat": 2.0, "lon": 2.0, "ele": 5.0}]
    assert elevation_profile(track) == [None, 5.0]


def test_total_ascent_counts_only_upward():
    assert total_ascent_m([100.0, 150.0, 120.0, None, 200.0]) == pytest.approx(130.0)


# -- B5: Geometrie beschaffen ------------------------------------------------------


def test_parse_kml_reads_linestring_coordinates(tmp_path):
    path = tmp_path / "route.kml"
    path.write_text(KML, encoding="utf-8")
    points = parse_kml(path)
    assert len(points) == 3
    assert points[0] == {"lat": 62.1049, "lon": 7.2066, "ele": 10.0}


def test_parse_kml_without_coordinates_raises(tmp_path):
    path = tmp_path / "leer.kml"
    path.write_text('<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"/>')
    with pytest.raises(KmlError):
        parse_kml(path)


def test_write_and_reread_gpx_roundtrip(tmp_path):
    points = [{"lat": 62.1, "lon": 7.2, "ele": 10.0}, {"lat": 62.2, "lon": 7.3, "ele": 20.0}]
    path = write_gpx(points, tmp_path / "r.gpx")
    back = parse_gpx(path, require_time=False)
    assert [(p["lat"], p["lon"], p["ele"]) for p in back] == [
        (62.1, 7.2, 10.0),
        (62.2, 7.3, 20.0),
    ]


def test_parse_gpx_default_still_drops_pointless_entries(tmp_path):
    """Regression: das Zeit-Verhalten der Asset-Zuordnung bleibt unveraendert."""
    path = write_gpx([{"lat": 1.0, "lon": 1.0}], tmp_path / "ohne-zeit.gpx")
    assert parse_gpx(path) == []
    assert len(parse_gpx(path, require_time=False)) == 1


def test_import_kml_produces_the_normal_gpx_file(proj, tmp_path):
    kml = tmp_path / "maps.kml"
    kml.write_text(KML, encoding="utf-8")
    path = import_kml(proj, kml)
    assert path == proj.gpx_path
    assert len(parse_gpx(path, require_time=False)) == 3


def test_waypoints_follow_from_via_to_and_report_unknown_names():
    from frameforge.gpx import parse_locations, parse_stages

    stages = parse_stages(proj_stages := _tmp_csv(STAGES))
    locations = parse_locations(_tmp_csv(LOCATIONS))
    waypoints, unknown = waypoints_from_stages(stages, locations)
    assert waypoints == [(62.1049, 7.2066), (62.4581, 7.6706), (61.8386, 8.5669)]
    assert unknown == []
    assert proj_stages.exists()


def test_unknown_place_is_reported_not_invented(tmp_path):
    from frameforge.gpx import parse_locations, parse_stages

    stages = parse_stages(_tmp_csv(STAGES + "10,2026-07-29,Lom,Oslo,,300,Oslo,\n"))
    locations = parse_locations(_tmp_csv(LOCATIONS))
    waypoints, unknown = waypoints_from_stages(stages, locations)
    assert unknown == ["Oslo"]
    # Lom ist Ziel der ersten und Start der zweiten Etappe — direkt aufeinanderfolgende
    # identische Punkte werden zusammengefasst, sonst haette die Route Null-Segmente.
    assert len(waypoints) == 3


def test_build_route_gpx_uses_injected_router(proj):
    calls: list = []

    def fake_router(waypoints):
        calls.append(list(waypoints))
        return [{"lat": lat, "lon": lon} for lat, lon in waypoints]

    path, unknown = build_route_gpx(proj, router=fake_router)
    assert path == proj.gpx_path
    assert unknown == []
    assert len(calls) == 1
    assert len(parse_gpx(path, require_time=False)) == 3


def test_build_route_without_stages_raises(proj):
    proj.stages_csv_path.unlink()
    with pytest.raises(RoutingError, match="Etappen"):
        build_route_gpx(proj, router=lambda w: [])


def test_build_route_without_coordinates_raises(proj):
    proj.locations_csv_path.write_text("name,lat,lon\n", encoding="utf-8")
    with pytest.raises(RoutingError, match="Koordinaten"):
        build_route_gpx(proj, router=lambda w: [])


def test_elevation_cache_asks_each_coordinate_only_once(proj):
    track = [{"lat": 62.1, "lon": 7.2}, {"lat": 62.2, "lon": 7.3}]
    calls: list = []

    def lookup(points):
        calls.append(list(points))
        return [100.0, 200.0][: len(points)]

    assert elevations_for(proj, track, lookup=lookup) == [100.0, 200.0]
    assert elevations_for(proj, track, lookup=lookup) == [100.0, 200.0]
    assert len(calls) == 1  # zweiter Lauf komplett aus dem Cache

    cache = json.loads((proj.route_dir / "elevation.json").read_text())
    assert cache == {"62.10000,7.20000": 100.0, "62.20000,7.30000": 200.0}


_CSV_COUNTER = [0]


def _tmp_csv(text: str):
    import tempfile
    from pathlib import Path

    _CSV_COUNTER[0] += 1
    path = Path(tempfile.mkdtemp()) / f"f{_CSV_COUNTER[0]}.csv"
    path.write_text(text, encoding="utf-8")
    return path
