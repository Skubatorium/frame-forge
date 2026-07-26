"""Tests fuer die `ingest`/`index`-CLI-Kommandos (echte Verarbeitung seit M1)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from frameforge import project as project_module
from frameforge.cli import app
from frameforge.index import write_asset
from frameforge.ingest import hash_file
from frameforge.project import ProjectConfig, resolve_project
from frameforge.state import Phase

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


@pytest.fixture
def env(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    cache_root = tmp_path / "cache"
    monkeypatch.setattr(project_module, "CACHE_ROOT", cache_root)

    media_root = tmp_path / "media"
    media_root.mkdir()
    shutil.copy(FIXTURES / "clip.mp4", media_root / "clip.mp4")
    shutil.copy(FIXTURES / "photo.jpg", media_root / "photo.jpg")

    root = projects_dir / "proto"
    root.mkdir()
    ProjectConfig(name="proto", media_root=media_root).save(root / "project.yaml")
    return resolve_project("proto")


def test_ingest_creates_proxies_and_advances_phase(env):
    result = runner.invoke(app, ["ingest", "proto"])

    assert result.exit_code == 0, result.output
    assert env.load_state().project_phase == Phase.INGESTED
    assert (env.cache_dir / "proxies" / "clip.mp4").exists()
    assert (env.cache_dir / "proxies" / "photo.jpg").exists()


def test_index_before_ingest_is_blocked(env):
    result = runner.invoke(app, ["index", "proto"])
    assert result.exit_code == 1
    assert "INGESTED" in result.output


def test_index_reports_pending_assets_after_ingest(env):
    runner.invoke(app, ["ingest", "proto"])

    result = runner.invoke(app, ["index", "proto"])

    assert result.exit_code == 0, result.output
    assert "2 noch nicht indiziert" in result.output


def test_index_skips_assets_already_in_assets_json(env):
    runner.invoke(app, ["ingest", "proto"])
    write_asset(
        env,
        {
            "id": "clip",
            "hash": hash_file(env.config.media_root / "clip.mp4"),
            "kind": "video",
        },
    )

    result = runner.invoke(app, ["index", "proto"])

    assert "1 noch nicht indiziert" in result.output
