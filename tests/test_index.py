"""Tests fuer das Query-Interface auf `assets.json`."""

from __future__ import annotations

import json

import pytest

from frameforge import project as project_module
from frameforge.index import load_assets, query_assets, write_asset
from frameforge.project import ProjectConfig, resolve_project

ASSETS = [
    {
        "id": "a1",
        "kind": "video",
        "rating": 4,
        "gps": {"place": "Geirangerfjord"},
        "content": {"tags": ["fjord", "drohne"]},
    },
    {
        "id": "a2",
        "kind": "photo",
        "rating": 2,
        "gps": {"place": "Bergen"},
        "content": {"tags": ["stadt"]},
    },
]


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)

    root = projects_dir / "norwegen-2026"
    root.mkdir()
    ProjectConfig(name="norwegen-2026", media_root=tmp_path / "media").save(root / "project.yaml")
    project = resolve_project("norwegen-2026")
    project.assets_dir.mkdir(parents=True, exist_ok=True)
    project.assets_json_path.write_text(json.dumps(ASSETS))
    return project


def test_load_assets_missing_file_returns_empty(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    root = projects_dir / "leer"
    root.mkdir()
    ProjectConfig(name="leer", media_root=tmp_path / "media").save(root / "project.yaml")
    assert load_assets(resolve_project("leer")) == []


def test_query_filters_by_tag(proj):
    assert [a["id"] for a in query_assets(proj, tag="fjord")] == ["a1"]


def test_query_filters_by_place(proj):
    assert [a["id"] for a in query_assets(proj, place="Bergen")] == ["a2"]


def test_query_filters_by_min_rating(proj):
    assert [a["id"] for a in query_assets(proj, min_rating=3)] == ["a1"]


def test_query_filters_by_kind(proj):
    assert [a["id"] for a in query_assets(proj, kind="photo")] == ["a2"]


def test_query_without_filters_returns_all(proj):
    assert {a["id"] for a in query_assets(proj)} == {"a1", "a2"}


NEW_ASSET = {
    "id": "a3",
    "kind": "video",
    "path": "video/day01/clip.mp4",
    "captured_at": "2026-07-14T09:12:33+02:00",
    "rating": 5,
    "gps": {"place": "Trollstigen"},
    "tech": {"w": 1920, "h": 1080, "fps": 25.0, "dur": 12.4, "codec": "h264"},
    "quality": {"sharpness": 0.8, "stability": 0.9, "exposure": 0.75, "score": 0.82},
    "content": {"summary": "Serpentinen von oben.", "tags": ["berge", "strasse"]},
}


def test_write_asset_appends_new_entry_to_assets_json(proj):
    write_asset(proj, NEW_ASSET)

    ids = {a["id"] for a in load_assets(proj)}
    assert ids == {"a1", "a2", "a3"}


def test_write_asset_upserts_existing_entry_by_id(proj):
    updated = dict(NEW_ASSET, rating=1)
    write_asset(proj, NEW_ASSET)
    write_asset(proj, updated)

    assets = load_assets(proj)
    matches = [a for a in assets if a["id"] == "a3"]
    assert len(matches) == 1
    assert matches[0]["rating"] == 1


def test_write_asset_creates_markdown_with_content(proj):
    write_asset(proj, NEW_ASSET)

    md_path = proj.assets_dir / "a3.md"
    text = md_path.read_text()
    assert "# a3" in text
    assert "Trollstigen" in text
    assert "Serpentinen von oben." in text
    assert "berge, strasse" in text


def test_write_asset_preserves_user_notes_on_reindex(proj):
    write_asset(proj, NEW_ASSET)
    md_path = proj.assets_dir / "a3.md"
    original = md_path.read_text()
    md_path.write_text(original + "\nMeine eigene Notiz zu diesem Clip.\n")

    write_asset(proj, dict(NEW_ASSET, rating=3))

    text = md_path.read_text()
    assert "Meine eigene Notiz zu diesem Clip." in text
    assert "**Rating:** 3/5" in text
