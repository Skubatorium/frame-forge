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
    from frameforge.ingest import proxy_path

    result = runner.invoke(app, ["ingest", "proto"])

    assert result.exit_code == 0, result.output
    assert env.load_state().project_phase == Phase.INGESTED
    proxies_dir = env.cache_dir / "proxies"
    mr = env.config.media_root
    assert proxy_path(mr / "clip.mp4", proxies_dir, media_root=mr).exists()
    assert proxy_path(mr / "photo.jpg", proxies_dir, media_root=mr).exists()


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


# -- design: Regressionstest fuer den write_asset({})-Klasse-Bug ------------------


def test_design_without_tokens_yaml_fails_cleanly(env):
    result = runner.invoke(app, ["design", "proto"])
    assert result.exit_code == 1
    assert "tokens.yaml" in result.output


def test_design_with_tokens_yaml_advances_phase(env):
    env.design_dir.mkdir(parents=True, exist_ok=True)
    env.design_tokens_path.write_text("primary_color: '#000000'\n")

    result = runner.invoke(app, ["design", "proto"])

    assert result.exit_code == 0, result.output
    assert env.load_state().project_phase == Phase.DESIGNED


# -- nle: FCPXML/OTIO-Export ---------------------------------------------------


def test_nle_requires_timeline(env):
    result = runner.invoke(app, ["nle", "proto", "teaser"])
    assert result.exit_code == 1
    assert "existiert nicht" in result.output


def test_nle_rejects_invalid_format(env):
    result = runner.invoke(app, ["nle", "proto", "teaser", "--format", "premiere"])
    assert result.exit_code == 1
    assert "--format" in result.output


def test_nle_exports_fcpxml_and_otio(env):
    from frameforge.timeline import Timeline

    write_asset(
        env,
        {"id": "clip1", "kind": "video", "path": "clip.mp4", "hash": hash_file(env.config.media_root / "clip.mp4")},
    )
    export = env.export("teaser")
    export.ensure_dirs()
    Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=2.0,
        tracks={"video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 2, "tl_in": 0}]},
    ).save(export.timeline_path)

    fcpxml_result = runner.invoke(app, ["nle", "proto", "teaser", "--format", "fcpxml"])
    otio_result = runner.invoke(app, ["nle", "proto", "teaser", "--format", "otio"])

    assert fcpxml_result.exit_code == 0, fcpxml_result.output
    assert otio_result.exit_code == 0, otio_result.output
    assert (export.nle_dir / "teaser.fcpxml").exists()
    assert (export.nle_dir / "teaser.otio").exists()


# -- faces: Opt-in-Gesichtserkennung ------------------------------------------


def test_faces_without_photo_assets_reports_nothing(env):
    result = runner.invoke(app, ["faces", "proto"])
    assert result.exit_code == 0, result.output
    assert "Keine Foto-Assets" in result.output


def test_faces_writes_gitignored_output_files(env):
    write_asset(
        env,
        {
            "id": "photo1",
            "kind": "photo",
            "path": "photo.jpg",
            "hash": hash_file(env.config.media_root / "photo.jpg"),
        },
    )

    result = runner.invoke(app, ["faces", "proto"])

    assert result.exit_code == 0, result.output
    assert "0 Gesichter" in result.output
    assert (env.index_dir / "people.json").exists()
    assert (env.index_dir / "people_clusters.json").exists()
