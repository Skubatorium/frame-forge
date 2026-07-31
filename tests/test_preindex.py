"""Tests fuer die Index-Vorbereitung (Keyframes + CV-Analyse pro Asset)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from frameforge import ingest as ingest_module
from frameforge import project as project_module
from frameforge.index import load_assets, write_asset
from frameforge.preindex import index_prepared_asset, load_prep, prepare_index
from frameforge.project import ProjectConfig, resolve_project

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(project_module, "CACHE_ROOT", tmp_path / "cache")

    media_root = tmp_path / "media"
    (media_root / "tag1").mkdir(parents=True)
    shutil.copy(FIXTURES / "clip.mp4", media_root / "tag1" / "DJI_20260720120000_clip.mp4")
    shutil.copy(FIXTURES / "photo.jpg", media_root / "tag1" / "DJI_20260720120500_photo.jpg")

    root = projects_dir / "p"
    root.mkdir()
    ProjectConfig(name="p", media_root=media_root).save(root / "project.yaml")
    p = resolve_project("p")
    # Proxies bauen (prepare-index analysiert bevorzugt die Proxies).
    ingest_module.build_proxies(
        ingest_module.scan_media(media_root), p.cache_dir / "proxies", media_root=media_root
    )
    return p


def test_prepare_index_creates_keyframes_and_prep(proj):
    result = prepare_index(proj)
    assert len(result.prepared) == 2
    assert result.failures == []

    prep_files = list((proj.cache_dir / "prep").glob("*.json"))
    assert len(prep_files) == 2
    keyframes = list((proj.cache_dir / "keyframes").glob("*.jpg"))
    assert keyframes  # mindestens ein Keyframe

    preps = {p["kind"]: p for p in load_prep(proj)}
    assert set(preps) == {"video", "photo"}
    for p in preps.values():
        assert p["id"] and p["hash"] and p["keyframes"]
        assert p["source_guess"]  # gesetzt (ggf. "unknown"/"camera")
    assert "scenes" in preps["video"]
    assert preps["video"]["id"].startswith("20260720-")  # Datum aus Ordner/Datei


def test_prepare_index_is_idempotent(proj):
    prepare_index(proj)
    again = prepare_index(proj)
    assert again.prepared == []
    assert again.skipped_existing == 2


def test_prepare_index_filter_and_limit(proj):
    only_one = prepare_index(proj, limit=1)
    assert len(only_one.prepared) == 1

    none = prepare_index(proj, filter_substr="gibtsnicht")
    assert none.prepared == []


def test_index_prepared_asset_merges_and_writes(proj):
    prepare_index(proj)
    prep = load_prep(proj)[0]
    digest = prep["hash"]

    asset = index_prepared_asset(
        proj,
        digest,
        summary="Drohne über dem See",
        tags=["see", "drohne", "luftaufnahme"],
        usable_as=["establisher"],
        rating=4,
        source="drone",
        people=False,
    )
    assert asset["content"]["summary"] == "Drohne über dem See"
    assert asset["rating"] == 4 and asset["source"] == "drone"
    assert asset["hash"] == digest and asset["id"] == prep["id"]  # technische Felder erhalten

    stored = {a["id"]: a for a in load_assets(proj)}
    assert prep["id"] in stored
    # In assets.json geschrieben -> nicht mehr offen.
    assert all(p["hash"] != digest for p in load_prep(proj))


def test_index_prepared_asset_rejects_bad_source_and_rating(proj):
    prepare_index(proj)
    digest = load_prep(proj)[0]["hash"]
    with pytest.raises(ValueError):
        index_prepared_asset(proj, digest, summary="x", tags=["a"], usable_as=[], rating=4, source="quatsch")
    with pytest.raises(ValueError):
        index_prepared_asset(proj, digest, summary="x", tags=["a"], usable_as=[], rating=9, source="drone")


def test_load_prep_excludes_indexed_assets(proj):
    prepare_index(proj)
    preps = load_prep(proj)
    assert len(preps) == 2

    # media-indexer schreibt einen Eintrag -> load_prep laesst ihn weg.
    one = preps[0]
    write_asset(proj, {"id": one["id"], "hash": one["hash"], "kind": one["kind"]})
    remaining = load_prep(proj)
    assert len(remaining) == 1
    assert remaining[0]["hash"] != one["hash"]
