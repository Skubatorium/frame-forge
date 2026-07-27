"""Tests fuer Projekt-/Export-Pfadauflösung."""

from __future__ import annotations

from pathlib import Path

import pytest

from frameforge import project as project_module
from frameforge.project import (
    ProjectConfig,
    ProjectNotFoundError,
    UnsafeNameError,
    UnsafePathError,
    resolve_media_path,
    resolve_project,
    validate_name,
)


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


# -- S1: Namens-Validierung (Path-Traversal) ------------------------------


@pytest.mark.parametrize("bad", ["../evil", "..", "a/b", "/abs", ".hidden", "foo/../bar", ""])
def test_validate_name_rejects_traversal_and_slashes(bad):
    with pytest.raises(UnsafeNameError):
        validate_name(bad)


@pytest.mark.parametrize("good", ["norwegen-2026", "teaser_90s", "a.b", "Proto1"])
def test_validate_name_accepts_safe_names(good):
    assert validate_name(good) == good


def test_resolve_project_rejects_traversal_name(projects_dir):
    with pytest.raises(UnsafeNameError):
        resolve_project("../../etc")


def test_export_rejects_traversal_name(projects_dir, tmp_path):
    _write_project_yaml(projects_dir / "p", tmp_path / "media")
    proj = resolve_project("p")
    with pytest.raises(UnsafeNameError):
        proj.export("../../escape")


# -- S2: Medienpfad bleibt unter media_root -------------------------------


def test_resolve_media_path_accepts_path_inside_root(tmp_path):
    root = tmp_path / "media"
    (root / "day01").mkdir(parents=True)
    (root / "day01" / "clip.mp4").write_bytes(b"x")
    resolved = resolve_media_path(root, "day01/clip.mp4")
    assert resolved == (root / "day01" / "clip.mp4").resolve()


def test_resolve_media_path_rejects_escape(tmp_path):
    root = tmp_path / "media"
    root.mkdir()
    with pytest.raises(UnsafePathError):
        resolve_media_path(root, "../../etc/passwd")


def test_resolve_media_path_rejects_absolute_escape(tmp_path):
    root = tmp_path / "media"
    root.mkdir()
    with pytest.raises(UnsafePathError):
        resolve_media_path(root, str(Path("/etc/passwd")))
