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


def _reach_indexed(env):
    state = env.load_state()
    state.advance_project(Phase.INDEXED)
    state.save()


def test_design_before_indexed_is_blocked(env):
    """Audit-Finding P1: design darf INGESTED/INDEXED nicht ueberspringen."""
    env.design_dir.mkdir(parents=True, exist_ok=True)
    env.design_tokens_path.write_text("primary_color: '#000000'\n")

    result = runner.invoke(app, ["design", "proto"])

    assert result.exit_code == 1
    assert "INDEXED" in result.output
    assert env.load_state().project_phase != Phase.DESIGNED


def test_design_without_tokens_yaml_fails_cleanly(env):
    _reach_indexed(env)
    result = runner.invoke(app, ["design", "proto"])
    assert result.exit_code == 1
    assert "tokens.yaml" in result.output


def test_design_with_tokens_yaml_advances_phase(env):
    _reach_indexed(env)
    env.design_dir.mkdir(parents=True, exist_ok=True)
    env.design_tokens_path.write_text("primary_color: '#000000'\n")

    result = runner.invoke(app, ["design", "proto"])

    assert result.exit_code == 0, result.output
    assert env.load_state().project_phase == Phase.DESIGNED


def test_index_sets_indexed_when_nothing_pending(env):
    """Audit-Finding P1b: index hebt die Phase auf INDEXED, sobald alle Assets erfasst sind."""
    runner.invoke(app, ["ingest", "proto"])
    for name, path in (("clip", "clip.mp4"), ("photo", "photo.jpg")):
        write_asset(
            env,
            {"id": name, "path": path, "kind": "video", "hash": hash_file(env.config.media_root / path)},
        )

    result = runner.invoke(app, ["index", "proto"])

    assert result.exit_code == 0, result.output
    assert "INDEXED" in result.output
    assert env.load_state().project_phase == Phase.INDEXED


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


# -- Audit P3: Freigabe an Timeline-Stand gebunden -----------------------------


def _make_timeline(env, duration=2.0):
    from frameforge.timeline import Timeline

    export = env.export("teaser")
    export.ensure_dirs()
    Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=duration,
        tracks={"video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": duration, "tl_in": 0}]},
    ).save(export.timeline_path)
    return export


def test_render_blocks_when_timeline_changed_after_approve(env):
    from frameforge.qc import timeline_fingerprint

    export = _make_timeline(env)
    state = env.load_state()
    state.advance_export("teaser", Phase.APPROVED)
    state.set_export_hash("teaser", "timeline", timeline_fingerprint(export.timeline_path))
    state.save()

    # Timeline nach der Freigabe veraendern.
    _make_timeline(env, duration=3.0)

    result = runner.invoke(app, ["render", "proto", "teaser"])

    assert result.exit_code == 1
    assert "veraltet" in result.output
    assert env.load_state().export_phase("teaser") == Phase.APPROVED  # nicht gerendert


def test_approve_requires_previewed(env):
    _make_timeline(env)
    result = runner.invoke(app, ["approve", "proto", "teaser"], input="y\n")
    assert result.exit_code == 1
    assert "PREVIEWED" in result.output


# -- Audit S1: Namens-Validierung in new ---------------------------------------


def test_new_rejects_traversal_name(env):
    result = runner.invoke(
        app, ["new", "../evil", "--media-root", str(env.config.media_root)]
    )
    assert result.exit_code == 1
    assert "unzulaessig" in result.output


# -- stats / report -----------------------------------------------------------


def test_stats_reports_index_summary(env):
    write_asset(
        env,
        {
            "id": "clip1", "kind": "video", "path": "clip.mp4",
            "hash": hash_file(env.config.media_root / "clip.mp4"),
            "tech": {"w": 320, "h": 240, "fps": 25, "dur": 2.0, "codec": "h264"},
            "quality": {"sharpness": 0.9, "stability": 0.8, "exposure": 0.7, "score": 0.8},
            "rating": 4,
        },
    )
    result = runner.invoke(app, ["stats", "proto"])
    assert result.exit_code == 0, result.output
    assert "Fundus" in result.output


def test_stats_empty_index_hint(env):
    result = runner.invoke(app, ["stats", "proto"])
    assert result.exit_code == 0
    assert "index" in result.output.lower()


def test_report_writes_markdown(env):
    from frameforge.timeline import Timeline

    write_asset(
        env,
        {"id": "clip1", "kind": "video", "path": "clip.mp4",
         "hash": hash_file(env.config.media_root / "clip.mp4"),
         "content": {"summary": "Testclip"}},
    )
    export = env.export("teaser")
    export.ensure_dirs()
    Timeline(
        export="teaser", fps=25, resolution=(320, 240), duration=2.0,
        tracks={"video": [{"id": "c1", "asset": "clip1", "src_in": 0, "src_out": 2, "tl_in": 0}]},
    ).save(export.timeline_path)

    result = runner.invoke(app, ["report", "proto", "teaser"])

    assert result.exit_code == 0, result.output
    report = export.root / "report.md"
    assert report.exists()
    assert "Testclip" in report.read_text()


# -- Personen-Index (Naming) --------------------------------------------------


def _write_clusters(env, clusters):
    env.index_dir.mkdir(parents=True, exist_ok=True)
    import json as _json
    (env.index_dir / "people_clusters.json").write_text(_json.dumps(clusters))


def test_people_lists_clusters(env):
    _write_clusters(env, {"person_1": ["a1", "a2"], "person_2": ["a3"]})
    result = runner.invoke(app, ["people", "proto"])
    assert result.exit_code == 0, result.output
    assert "person_1" in result.output
    assert "ohne Namen" in result.output


def test_name_person_sets_name_and_query_filters(env):
    _write_clusters(env, {"person_1": ["clipA"]})
    write_asset(env, {"id": "clipA", "kind": "video", "path": "clip.mp4",
                      "hash": hash_file(env.config.media_root / "clip.mp4")})
    write_asset(env, {"id": "clipB", "kind": "video", "path": "photo.jpg",
                      "hash": hash_file(env.config.media_root / "photo.jpg")})

    named = runner.invoke(app, ["name-person", "proto", "person_1", "Oskar"])
    assert named.exit_code == 0, named.output
    assert "Oskar" in named.output

    q = runner.invoke(app, ["query", "proto", "--person", "Oskar"])
    assert q.exit_code == 0, q.output
    assert "clipA" in q.output
    assert "clipB" not in q.output


def test_name_person_unknown_cluster_fails(env):
    _write_clusters(env, {"person_1": ["a1"]})
    result = runner.invoke(app, ["name-person", "proto", "person_9", "X"])
    assert result.exit_code == 1


def test_query_filters_by_source(env):
    write_asset(env, {"id": "d1", "kind": "video", "source": "drone", "path": "clip.mp4",
                      "hash": hash_file(env.config.media_root / "clip.mp4")})
    write_asset(env, {"id": "ph1", "kind": "video", "source": "phone", "path": "photo.jpg",
                      "hash": hash_file(env.config.media_root / "photo.jpg")})

    result = runner.invoke(app, ["query", "proto", "--source", "drone"])

    assert result.exit_code == 0, result.output
    assert "d1" in result.output
    assert "ph1" not in result.output


# -- design-status: Grafik-Inventar -------------------------------------------


def test_design_status_shows_missing_graphics(env):
    env.design_dir.mkdir(parents=True, exist_ok=True)
    env.design_tokens_path.write_text("primary_color: '#000'\n")
    env.design_prompts_path.write_text("Logo: logo.png\nMarker: marker-icon.png\n")
    env.design_assets_dir.mkdir(parents=True, exist_ok=True)
    (env.design_assets_dir / "logo.png").write_bytes(b"x")

    result = runner.invoke(app, ["design-status", "proto"])

    assert result.exit_code == 0, result.output
    assert "logo.png" in result.output
    assert "marker-icon.png" in result.output
    assert "fehlt" in result.output.lower()
