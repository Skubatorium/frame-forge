"""Tests fuer `frameforge backfill-metadata` (Plan 0003, Arbeitspaket A0)."""

from __future__ import annotations

import copy
import json
import shutil

import pytest

from frameforge import project as project_module
from frameforge.backfill import apply_backfill, captured_at_coverage, plan_backfill
from frameforge.index import load_assets, write_asset
from frameforge.ingest import hash_file
from frameforge.project import ProjectConfig, resolve_project

FIXTURE_CLIP = "tests/fixtures/clip.mp4"
FIXTURE_PHOTO = "tests/fixtures/photo.jpg"

# So sieht ein Eintrag aus dem Realbetrieb aus: Inhalt vom media-indexer, technische Felder
# unvollstaendig (kein captured_at, veraltete/fehlende probe-Werte).
INHALT = {
    "content": {"summary": "Fjord im Abendlicht", "tags": ["fjord"], "people": False},
    "rating": 4,
    "source": "drone",
    "gps": {"place": "Geiranger"},
    "quality": {"score": 0.6},
}


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(project_module, "CACHE_ROOT", tmp_path / "cache")

    media = tmp_path / "media"
    media.mkdir()
    shutil.copy2(FIXTURE_CLIP, media / "clip.mp4")
    shutil.copy2(FIXTURE_PHOTO, media / "photo.jpg")

    root = projects_dir / "p"
    root.mkdir()
    ProjectConfig(name="p", media_root=media).save(root / "project.yaml")
    project = resolve_project("p")

    for asset_id, rel, kind in (("a1", "clip.mp4", "video"), ("a2", "photo.jpg", "photo")):
        asset = copy.deepcopy(INHALT)
        asset.update(
            {"id": asset_id, "hash": hash_file(media / rel), "path": rel, "kind": kind}
        )
        write_asset(project, asset)
    return project


def test_technical_fields_are_added(proj):
    result = plan_backfill(proj)
    fields = {u.field for u in result.updates}
    assert "probe" in fields  # Video: Aufloesung/fps/Codec/Dauer aus ffprobe
    assert "duration" in fields
    assert all(u.is_new for u in result.updates)  # nichts davon war vorher da

    assert apply_backfill(proj, result) == len(result.touched_assets)
    by_id = {a["id"]: a for a in load_assets(proj)}
    assert by_id["a1"]["probe"]["w"] > 0
    assert by_id["a1"]["duration"] > 0


def test_content_rating_and_place_stay_untouched(proj):
    """Abnahme A0: Diff auf assets.json zeigt ausschliesslich technische Felder."""
    before = {a["id"]: a for a in json.loads(proj.assets_json_path.read_text())}

    apply_backfill(proj, plan_backfill(proj))

    after = {a["id"]: a for a in json.loads(proj.assets_json_path.read_text())}
    for asset_id, old in before.items():
        new = after[asset_id]
        assert new["content"] == old["content"]
        assert new["rating"] == old["rating"]
        assert new["source"] == old["source"]
        assert new["quality"] == old["quality"]
        assert new["hash"] == old["hash"]
        assert new["path"] == old["path"]
        assert new["gps"]["place"] == old["gps"]["place"]  # Ort bleibt, nur lat/lon kommen dazu
        changed = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
        assert changed <= {"captured_at", "captured_at_source", "duration", "probe", "gps"}


def test_freetext_notes_survive(proj):
    md_path = proj.assets_dir / "a1.md"
    md_path.write_text(md_path.read_text() + "\nEigene Notiz: Lieblingsclip.\n")

    apply_backfill(proj, plan_backfill(proj))

    assert "Eigene Notiz: Lieblingsclip." in md_path.read_text()


def test_second_run_is_idempotent(proj):
    apply_backfill(proj, plan_backfill(proj))
    second = plan_backfill(proj)
    assert second.updates == []
    assert second.unchanged == second.scanned
    assert apply_backfill(proj, second) == 0


def test_missing_file_is_reported_not_dropped(proj):
    (proj.config.media_root / "clip.mp4").unlink()

    result = plan_backfill(proj)
    assert result.missing_files == ["a1"]
    apply_backfill(proj, result)
    assert {a["id"] for a in load_assets(proj)} == {"a1", "a2"}


def test_broken_file_is_collected_not_raised(proj):
    (proj.config.media_root / "clip.mp4").write_bytes(b"kein video")

    result = plan_backfill(proj)
    assert [f.asset_id for f in result.failures] == ["a1"]
    assert result.scanned == 2  # das Foto wurde trotzdem verarbeitet


def test_captured_at_coverage_counts_only_requested_kind(proj):
    assert captured_at_coverage(proj, kind="video") == (0, 1)
    apply_backfill(proj, plan_backfill(proj))
    assert captured_at_coverage(proj)[1] == 2
