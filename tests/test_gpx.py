"""Tests fuer GPX-Parsing und Asset-Ort-Zuordnung."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

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
