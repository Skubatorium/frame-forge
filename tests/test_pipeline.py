"""Tests fuer die Pipeline-Uebersicht (`frameforge status` / `/ff-wizard`)."""

from __future__ import annotations

import pytest

from frameforge.pipeline import (
    ASSET_INVENTORY_KEY,
    asset_drift,
    asset_inventory_fingerprint,
    build_pipeline,
    format_pipeline,
    pending_assets,
)
from frameforge.state import Phase, ProjectState


@pytest.fixture
def state(tmp_path):
    return ProjectState.load(tmp_path / ".state.json")


def _step(pipeline, key):
    for s in pipeline.project_steps:
        if s.key == key:
            return s
    for steps in pipeline.export_steps.values():
        for s in steps:
            if s.key == key:
                return s
    raise KeyError(key)


def test_fresh_project_next_step_is_ingest(state):
    p = build_pipeline("norwegen", state)
    assert _step(p, "ingest").current
    assert not _step(p, "ingest").done
    assert p.next_command == "/ff-ingest norwegen"


def test_ingested_next_step_is_index(state):
    state.advance_project(Phase.INGESTED)
    p = build_pipeline("norwegen", state)
    assert _step(p, "ingest").done
    assert _step(p, "index").current
    assert "index" in p.next_command


def test_designed_without_exports_suggests_brief(state):
    state.advance_project(Phase.DESIGNED)
    p = build_pipeline("norwegen", state)
    assert all(s.done for s in p.project_steps)
    assert "ff-brief" in p.next_command
    assert "export" in p.next_command.lower()


def test_export_progression_marks_next_export_step(state):
    state.advance_project(Phase.DESIGNED)
    state.advance_export("teaser", Phase.TIMELINE)
    p = build_pipeline("norwegen", state, exports=["teaser"])
    steps = {s.key: s for s in p.export_steps["teaser"]}
    assert steps["brief"].done and steps["build"].done
    assert steps["preview"].current
    assert not steps["approve"].current
    assert p.next_command == "/ff-preview norwegen teaser"


def test_one_current_per_lane_and_single_next_command(state):
    state.advance_project(Phase.DESIGNED)
    state.advance_export("a", Phase.BRIEFED)
    state.advance_export("b", Phase.BRIEFED)
    p = build_pipeline("norwegen", state, exports=["a", "b"])

    # Projekt fertig -> keine current-Markierung mehr auf Projekt-Ebene.
    assert not any(s.current for s in p.project_steps)
    # Jede Export-Spur zeigt ihr eigenes "du bist hier" (hier: build).
    for steps in p.export_steps.values():
        currents = [s for s in steps if s.current]
        assert len(currents) == 1
        assert currents[0].key == "build"
    # Der eine global naechste Befehl ist der erste offene Export-Schritt.
    assert p.next_command == "/ff-build norwegen a"


def test_fully_rendered_offers_new_export(state):
    """Quereinstieg: ist alles gerendert, ist der naechste Zug ein weiterer Export aus

    derselben Basis (kein Re-Ingest/Index/Design).
    """
    state.advance_project(Phase.DESIGNED)
    state.advance_export("teaser", Phase.RENDERED)
    p = build_pipeline("norwegen", state, exports=["teaser"])
    assert all(s.done for s in p.export_steps["teaser"])
    assert p.next_command == "/ff-brief norwegen <neuer-export>"
    assert "weiteren Export" in p.next_hint


def test_format_pipeline_renders_markers(state):
    state.advance_project(Phase.INGESTED)
    text = "\n".join(format_pipeline(build_pipeline("norwegen", state)))
    assert "[✓] ingest" in text
    assert "[→] index" in text
    assert "[ ] design" in text
    assert "Naechster Schritt:" in text


# -- G: Invalidierung bei neuem Material (Plan 0003) --------------------------------


@pytest.fixture
def proj_with_assets(tmp_path, monkeypatch):
    import shutil

    from frameforge import project as project_module
    from frameforge.index import write_asset
    from frameforge.ingest import hash_file
    from frameforge.project import ProjectConfig, resolve_project

    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(project_module, "CACHE_ROOT", tmp_path / "cache")

    media = tmp_path / "media"
    media.mkdir()
    shutil.copy2("tests/fixtures/clip.mp4", media / "clip.mp4")

    root = projects_dir / "p"
    root.mkdir()
    ProjectConfig(name="p", media_root=media).save(root / "project.yaml")
    project = resolve_project("p")
    write_asset(
        project,
        {
            "id": "a1",
            "hash": hash_file(media / "clip.mp4"),
            "path": "clip.mp4",
            "kind": "video",
            "content": {"summary": "x", "tags": []},
        },
    )
    return project


def test_pending_assets_finds_only_unindexed_files(proj_with_assets):
    import shutil

    assert pending_assets(proj_with_assets) == []
    shutil.copy("tests/fixtures/clip.mp4", proj_with_assets.config.media_root / "neu.mp4")
    assert [p.name for p in pending_assets(proj_with_assets)] == ["neu.mp4"]


def test_pending_assets_with_unreachable_media_root_is_empty(proj_with_assets):
    import shutil

    shutil.rmtree(proj_with_assets.config.media_root)
    assert pending_assets(proj_with_assets) == []  # nicht gemountet != neues Material


def test_fingerprint_ignores_technical_changes_but_not_new_assets(proj_with_assets):
    from frameforge.index import load_assets, save_assets, write_asset

    before = asset_inventory_fingerprint(proj_with_assets)

    assets = load_assets(proj_with_assets)
    assets[0]["captured_at"] = "2026-07-28T14:00:00+00:00"  # Backfill-artige Aenderung
    save_assets(proj_with_assets, assets)
    assert asset_inventory_fingerprint(proj_with_assets) == before

    write_asset(proj_with_assets, {"id": "a2", "hash": "sha256:neu", "kind": "video"})
    assert asset_inventory_fingerprint(proj_with_assets) != before


def test_asset_drift_warns_only_after_storyboarded(proj_with_assets):
    from frameforge.index import write_asset
    from frameforge.state import ProjectState

    state = ProjectState.load(proj_with_assets.state_path)
    assert asset_drift(proj_with_assets, state, "teaser") is None  # nie storyboarded

    state.set_export_hash(
        "teaser", ASSET_INVENTORY_KEY, asset_inventory_fingerprint(proj_with_assets)
    )
    assert asset_drift(proj_with_assets, state, "teaser") is None

    write_asset(proj_with_assets, {"id": "a2", "hash": "sha256:neu", "kind": "video"})
    message = asset_drift(proj_with_assets, state, "teaser")
    assert message and "geaendert" in message
