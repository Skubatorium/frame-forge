"""Tests fuer GPX-Parsing und Asset-Ort-Zuordnung."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from frameforge.gpx import nearest_location, parse_gpx

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_gpx_returns_sorted_points_with_time_and_coords():
    points = parse_gpx(FIXTURES / "route.gpx")

    assert len(points) == 3
    assert points == sorted(points, key=lambda p: p["time"])
    assert points[0]["lat"] == 62.1049
    assert points[0]["lon"] == 6.9394


def test_nearest_location_picks_closest_by_time():
    points = parse_gpx(FIXTURES / "route.gpx")
    timestamp = datetime(2026, 7, 14, 9, 9, 0, tzinfo=UTC)

    result = nearest_location(timestamp, points)

    assert result["lat"] == 62.1100


def test_nearest_location_exact_match():
    points = parse_gpx(FIXTURES / "route.gpx")
    timestamp = points[2]["time"]

    result = nearest_location(timestamp, points)

    assert result == points[2]


def test_nearest_location_empty_track_returns_none():
    assert nearest_location(datetime.now(UTC), []) is None


# -- locations.csv ------------------------------------------------------------


def test_parse_locations_reads_rows(tmp_path):
    from frameforge.gpx import parse_locations

    csv_path = tmp_path / "locations.csv"
    csv_path.write_text(
        "name,lat,lon,type,day\n"
        "Geiranger,62.10,7.20,overnight,3\n"
        "Trollstigen,62.45,7.66,poi,4\n"
    )
    locs = parse_locations(csv_path)
    assert [l["name"] for l in locs] == ["Geiranger", "Trollstigen"]
    assert locs[0]["lat"] == 62.10
    assert locs[0]["type"] == "overnight"
    assert locs[1]["day"] == "4"


def test_parse_locations_missing_file_returns_empty(tmp_path):
    from frameforge.gpx import parse_locations

    assert parse_locations(tmp_path / "nope.csv") == []


def test_parse_locations_missing_column_raises(tmp_path):
    from frameforge.gpx import LocationsError, parse_locations

    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("name,lat\nX,1.0\n")
    with pytest.raises(LocationsError):
        parse_locations(csv_path)


def test_parse_locations_bad_coordinate_raises(tmp_path):
    from frameforge.gpx import LocationsError, parse_locations

    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("name,lat,lon\nX,nope,7.0\n")
    with pytest.raises(LocationsError):
        parse_locations(csv_path)
