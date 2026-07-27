"""Tests fuer Index-Statistik und Export-Datenblatt."""

from __future__ import annotations

import json

import pytest

from frameforge import project as project_module
from frameforge.project import ProjectConfig, resolve_project
from frameforge.stats import build_report, index_stats, usage_stats, used_asset_ids
from frameforge.timeline import Timeline

ASSETS = [
    {
        "id": "v1",
        "kind": "video",
        "path": "day01/v1.mp4",
        "rating": 5,
        "gps": {"place": "Geiranger"},
        "content": {"summary": "Fjord von oben", "tags": ["fjord"], "people": False},
        "tech": {"w": 3840, "h": 2160, "fps": 25, "dur": 12.0, "codec": "hevc"},
        "quality": {"sharpness": 0.8, "stability": 0.9, "exposure": 0.7, "score": 0.8},
    },
    {
        "id": "v2",
        "kind": "video",
        "path": "day01/v2.mp4",
        "rating": 3,
        "gps": {"place": "Geiranger"},
        "content": {"summary": "Wasser", "tags": ["wasser"], "people": True},
        "tech": {"w": 1920, "h": 1080, "fps": 25, "dur": 8.0, "codec": "h264"},
        "quality": {"sharpness": 0.6, "stability": 0.7, "exposure": 0.9, "score": 0.7},
    },
    {
        "id": "p1",
        "kind": "photo",
        "path": "fotos/p1.jpg",
        "rating": 4,
        "gps": {"place": "Bergen"},
        "content": {"summary": "Stadt", "tags": ["stadt"], "people": False},
        "quality": {"sharpness": 0.5, "exposure": 0.8, "score": 0.65},
    },
]


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    root = projects_dir / "norwegen"
    root.mkdir()
    ProjectConfig(name="norwegen", media_root=tmp_path / "media").save(root / "project.yaml")
    project = resolve_project("norwegen")
    project.assets_dir.mkdir(parents=True, exist_ok=True)
    project.assets_json_path.write_text(json.dumps(ASSETS))
    return project


# -- index_stats -----------------------------------------------------------


def test_index_stats_counts_kinds_and_duration(proj):
    s = index_stats(proj, scan_disk=False)
    assert s.indexed == 3
    assert s.videos == 2
    assert s.photos == 1
    assert s.total_video_seconds == pytest.approx(20.0)
    assert s.on_disk is None  # scan_disk=False


def test_index_stats_distributions(proj):
    s = index_stats(proj, scan_disk=False)
    assert s.resolutions == {"3840x2160": 1, "1920x1080": 1}
    assert s.codecs == {"hevc": 1, "h264": 1}
    assert s.rating_hist == {3: 1, 4: 1, 5: 1}
    assert s.places == {"Geiranger": 2, "Bergen": 1}
    assert s.with_people == 1


def test_index_stats_avg_quality_video_only(proj):
    s = index_stats(proj, scan_disk=False)
    assert s.avg_quality["sharpness"] == pytest.approx(0.7)  # (0.8+0.6)/2, Foto zaehlt nicht
    assert "stability" in s.avg_quality


def test_index_stats_missing_media_root_is_not_an_error(proj):
    s = index_stats(proj, scan_disk=True)  # media_root existiert nicht
    assert s.on_disk is None
    assert s.indexed == 3


# -- usage_stats -----------------------------------------------------------


def _timeline(**tracks) -> Timeline:
    return Timeline(export="teaser", fps=25, resolution=(1920, 1080), duration=10.0, tracks=tracks)


def test_used_asset_ids_includes_video_and_asset_audio():
    tl = _timeline(
        video=[{"id": "c1", "asset": "v1", "src_in": 0, "src_out": 2, "tl_in": 0}],
        audio=[
            {"id": "a1", "src": "music/x.wav", "tl_in": 0},
            {"id": "a2", "asset": "v2", "type": "original", "tl_in": 1, "dur": 1},
        ],
    )
    assert used_asset_ids(tl) == {"v1", "v2"}


def test_usage_stats_across_exports(proj):
    export = proj.export("teaser")
    export.ensure_dirs()
    _timeline(
        video=[{"id": "c1", "asset": "v1", "src_in": 0, "src_out": 2, "tl_in": 0}]
    ).save(export.timeline_path)

    u = usage_stats(proj)
    assert u.total_assets == 3
    assert u.per_export == {"teaser": 1}
    assert u.used_union == {"v1"}
    assert u.union_coverage == pytest.approx(1 / 3)


# -- build_report ----------------------------------------------------------


def test_build_report_contains_key_sections(proj):
    export = proj.export("teaser")
    export.ensure_dirs()
    import yaml

    export.brief_path.write_text(yaml.safe_dump({"preset": "nordic-cinematic", "target_duration_s": 10}))
    proj.design_dir.mkdir(parents=True, exist_ok=True)
    proj.design_tokens_path.write_text(yaml.safe_dump({"font_display": "Inter", "primary_color": "#111"}))
    timeline = _timeline(
        video=[{"id": "c1", "asset": "v1", "src_in": 0.0, "src_out": 3.0, "tl_in": 0}],
        audio=[{"id": "a1", "src": "music/theme.wav", "tl_in": 0, "gain_db": -6}],
    )

    md = build_report(proj, export, timeline)

    assert "# Report — norwegen / teaser" in md
    assert "## Verwendung in diesem Export" in md
    assert "nordic-cinematic" in md
    assert "music/theme.wav" in md
    assert "Inter" in md
    assert "Fjord von oben" in md  # Beschreibung des genutzten Clips
    assert "v1" in md
