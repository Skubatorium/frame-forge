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


def test_write_asset_not_yet_implemented(proj):
    with pytest.raises(NotImplementedError):
        write_asset(proj, {})
