"""Tests fuer GPX-Parsing und Asset-Ort-Zuordnung."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from frameforge.gpx import (
    StagesError,
    nearest_location,
    parse_gpx,
    parse_stages,
    stage_for,
    stage_label,
)

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


# -- A3: Etappen aus route/stages.csv (Plan 0003) ----------------------------------

STAGES_CSV = """day,date,from,to,via,km,overnight,note
1,2026-07-19,Zuhause,Flensburg,,320,Flensburg,Anreise
2,2026-07-20,Flensburg,Skien,Fähre Hirtshals-Larvik,410,Hütte am See,
9,2026-07-28,Geiranger,Lom,Trollstigen,190,Lom,Passstraße
10,2026-07-29,Lom,Lom,,0,Lom,Standtag
"""


def _stages_file(tmp_path, text=STAGES_CSV):
    path = tmp_path / "stages.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_stages_reads_all_columns(tmp_path):
    stages = parse_stages(_stages_file(tmp_path))
    assert [s["day"] for s in stages] == [1, 2, 9, 10]
    assert stages[2] == {
        "day": 9,
        "date": date(2026, 7, 28),
        "from": "Geiranger",
        "to": "Lom",
        "via": "Trollstigen",
        "km": 190.0,
        "overnight": "Lom",
        "note": "Passstraße",
    }


def test_parse_stages_missing_file_is_empty(tmp_path):
    assert parse_stages(tmp_path / "gibts-nicht.csv") == []


def test_parse_stages_empty_km_stays_none_instead_of_guessed(tmp_path):
    path = _stages_file(tmp_path, "day,date,from,to,km\n1,2026-07-19,A,B,\n")
    assert parse_stages(path)[0]["km"] is None


def test_parse_stages_missing_column_raises_with_hint(tmp_path):
    path = _stages_file(tmp_path, "day,from,to\n1,A,B\n")
    with pytest.raises(StagesError, match="date"):
        parse_stages(path)


@pytest.mark.parametrize(
    ("row", "match"),
    [("eins,2026-07-19,A,B", "day"), ("1,19.07.2026,A,B", "date"), ("1,2026-07-19,A,B,,viel", "km")],
)
def test_parse_stages_reports_line_number(tmp_path, row, match):
    path = _stages_file(tmp_path, f"day,date,from,to,via,km\n{row}\n")
    with pytest.raises(StagesError) as exc:
        parse_stages(path)
    assert "Zeile 2" in str(exc.value)
    assert match in str(exc.value)


def test_stage_for_matches_by_date(tmp_path):
    stages = parse_stages(_stages_file(tmp_path))
    stage = stage_for(datetime(2026, 7, 28, 23, 50, tzinfo=UTC), stages)
    assert stage["from"] == "Geiranger"
    assert stage_for(datetime(2026, 1, 1, tzinfo=UTC), stages) is None


def test_stage_label(tmp_path):
    stages = parse_stages(_stages_file(tmp_path))
    assert stage_label(stages[2]) == "Geiranger → Lom"
    assert stage_label(stages[3]) == "Lom"  # Standtag: from == to
