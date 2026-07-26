"""Tests fuer Projekt-/Export-Pfadauflösung."""

from __future__ import annotations

import pytest

from frameforge import project as project_module
from frameforge.project import ProjectConfig, ProjectNotFoundError, resolve_project


@pytest.fixture
def projects_dir(tmp_path, monkeypatch):
    d = tmp_path / "projects"
    d.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", d)
    return d


def _write_project_yaml(root, media_root):
    root.mkdir(parents=True, exist_ok=True)
    ProjectConfig(name=root.name, media_root=media_root).save(root / "project.yaml")


def test_resolve_project_missing_raises(projects_dir):
    with pytest.raises(ProjectNotFoundError):
        resolve_project("nope")


def test_resolve_project_reads_config(projects_dir, tmp_path):
    _write_project_yaml(projects_dir / "norwegen-2026", tmp_path / "media")

    proj = resolve_project("norwegen-2026")

    assert proj.name == "norwegen-2026"
    assert proj.config.media_root == tmp_path / "media"
    assert proj.state_path == proj.root / ".state.json"
    assert proj.assets_json_path == proj.root / "index" / "assets.json"
    assert proj.design_tokens_path == proj.root / "design" / "tokens.yaml"


def test_export_paths_are_scoped_under_project(projects_dir, tmp_path):
    _write_project_yaml(projects_dir / "norwegen-2026", tmp_path / "media")
    proj = resolve_project("norwegen-2026")

    export = proj.export("teaser-90s")

    assert export.root == proj.exports_dir / "teaser-90s"
    assert export.timeline_path == export.root / "timeline.json"
    assert export.brief_path == export.root / "brief.yaml"


def test_cache_dir_is_outside_repo_and_stable(projects_dir, tmp_path):
    _write_project_yaml(projects_dir / "norwegen-2026", tmp_path / "media")
    proj = resolve_project("norwegen-2026")

    first = proj.cache_dir
    second = resolve_project("norwegen-2026").cache_dir

    assert first == second
    assert str(project_module.CACHE_ROOT) in str(first)
