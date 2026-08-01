"""Tests fuer `frameforge relink` (Plan 0003, Arbeitspaket E)."""

from __future__ import annotations

import json
import shutil

import pytest

from frameforge import project as project_module
from frameforge.index import load_assets, write_asset
from frameforge.ingest import hash_file
from frameforge.project import ProjectConfig, resolve_project
from frameforge.relink import apply_relink, plan_relink

FIXTURE_CLIP = "tests/fixtures/clip.mp4"
FIXTURE_PHOTO = "tests/fixtures/photo.jpg"


@pytest.fixture
def proj(tmp_path, monkeypatch):
    """Projekt mit zwei indizierten Assets (`a/clip.mp4`, `b/photo.jpg`) unter media_root."""
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(project_module, "CACHE_ROOT", tmp_path / "cache")

    media = tmp_path / "media"
    (media / "a").mkdir(parents=True)
    (media / "b").mkdir(parents=True)
    shutil.copy2(FIXTURE_CLIP, media / "a" / "clip.mp4")
    shutil.copy2(FIXTURE_PHOTO, media / "b" / "photo.jpg")

    root = projects_dir / "p"
    root.mkdir()
    ProjectConfig(name="p", media_root=media).save(root / "project.yaml")
    project = resolve_project("p")

    for asset_id, rel in (("a1", "a/clip.mp4"), ("a2", "b/photo.jpg")):
        write_asset(
            project,
            {
                "id": asset_id,
                "hash": hash_file(media / rel),
                "path": rel,
                "kind": "video" if rel.endswith(".mp4") else "photo",
                "rating": 4,
                "content": {"summary": "Testmaterial", "tags": ["test"]},
            },
        )
    return project


def _media(project):
    return project.config.media_root


def test_nothing_to_do_when_paths_are_intact(proj):
    result = plan_relink(proj)
    assert result.changed == []
    assert result.unchanged == 2
    assert result.orphans == []
    assert result.new_files == []


def test_moved_file_is_detected_and_path_corrected(proj):
    media = _media(proj)
    (media / "neu").mkdir()
    shutil.move(media / "a" / "clip.mp4", media / "neu" / "clip.mp4")

    result = plan_relink(proj)
    assert [(c.asset_id, c.old_path, c.new_path) for c in result.changed] == [
        ("a1", "a/clip.mp4", "neu/clip.mp4")
    ]
    assert result.unchanged == 1
    assert result.orphans == []
    assert result.new_files == []

    assert apply_relink(proj, result) == 1
    by_id = {a["id"]: a for a in load_assets(proj)}
    assert by_id["a1"]["path"] == "neu/clip.mp4"
    assert by_id["a2"]["path"] == "b/photo.jpg"


def test_relink_touches_only_the_path_field(proj):
    media = _media(proj)
    before = json.loads(proj.assets_json_path.read_text())
    (media / "neu").mkdir()
    shutil.move(media / "a" / "clip.mp4", media / "neu" / "clip.mp4")

    apply_relink(proj, plan_relink(proj))

    after = json.loads(proj.assets_json_path.read_text())
    for old, new in zip(before, after, strict=True):
        old.pop("path")
        new.pop("path")
        assert old == new  # Hash, content, rating, kind — alles unveraendert


def test_relink_keeps_freetext_notes_in_markdown(proj):
    media = _media(proj)
    md_path = proj.assets_dir / "a1.md"
    md_path.write_text(md_path.read_text() + "\nEigene Notiz: bester Take.\n")

    (media / "neu").mkdir()
    shutil.move(media / "a" / "clip.mp4", media / "neu" / "clip.mp4")
    apply_relink(proj, plan_relink(proj))

    text = md_path.read_text()
    assert "Eigene Notiz: bester Take." in text
    assert "neu/clip.mp4" in text


def test_missing_file_is_reported_as_orphan(proj):
    (_media(proj) / "a" / "clip.mp4").unlink()

    result = plan_relink(proj)
    assert [(o.asset_id, o.path) for o in result.orphans] == [("a1", "a/clip.mp4")]
    assert result.changed == []
    assert apply_relink(proj, result) == 0
    # Der verwaiste Eintrag bleibt stehen — relink loescht nichts.
    assert {a["id"] for a in load_assets(proj)} == {"a1", "a2"}


def test_unindexed_file_is_reported_as_new(proj):
    # shutil.copy (ohne 2) setzt eine neue mtime -> anderer Hash-Schluessel, echtes "neu"
    shutil.copy(FIXTURE_CLIP, _media(proj) / "b" / "extra.mp4")

    result = plan_relink(proj)
    assert result.new_files == ["b/extra.mp4"]
    assert result.changed == []
    assert result.unchanged == 2


def test_duplicate_hash_is_reported_ambiguous_not_guessed(proj):
    media = _media(proj)
    # copy2 erhaelt die mtime -> identischer Hash-Schluessel
    shutil.copy2(media / "a" / "clip.mp4", media / "b" / "kopie1.mp4")
    shutil.copy2(media / "a" / "clip.mp4", media / "b" / "kopie2.mp4")
    (media / "a" / "clip.mp4").unlink()

    result = plan_relink(proj)
    assert result.changed == []
    assert [(a.asset_id, a.candidates) for a in result.ambiguous] == [
        ("a1", ["b/kopie1.mp4", "b/kopie2.mp4"])
    ]


def test_existing_path_wins_over_duplicate(proj):
    media = _media(proj)
    shutil.copy2(media / "a" / "clip.mp4", media / "b" / "kopie.mp4")

    result = plan_relink(proj)
    # Beide Dateien tragen denselben Hash; der eingetragene Pfad existiert weiter -> nichts tun.
    assert result.changed == []
    assert result.ambiguous == []
    assert result.unchanged == 2


def test_changed_hash_at_same_path_is_not_an_orphan(proj):
    """mtime-Aenderung (git-Checkout, touch) darf keinen Waisen erzeugen — der Pfad stimmt ja."""
    clip = _media(proj) / "a" / "clip.mp4"
    clip.touch()  # neue mtime -> anderer Hash-Schluessel, gleicher Pfad

    result = plan_relink(proj)
    assert result.orphans == []
    assert result.changed == []
    assert result.new_files == []
    assert result.unchanged == 2


def test_proxy_moves_along_so_nothing_is_retranscoded(proj):
    """Der pfadgebundene Proxy-Name (Audit K1) wandert mit — sonst waere er verwaist."""
    from frameforge.ingest import proxy_path

    media = _media(proj)
    proxies = proj.cache_dir / "proxies"
    proxies.mkdir(parents=True, exist_ok=True)
    old_proxy = proxy_path(media / "a" / "clip.mp4", proxies, media_root=media)
    old_proxy.write_bytes(b"proxy-inhalt")

    (media / "neu").mkdir()
    shutil.move(media / "a" / "clip.mp4", media / "neu" / "clip.mp4")
    result = plan_relink(proj)
    apply_relink(proj, result)

    new_proxy = proxy_path(media / "neu" / "clip.mp4", proxies, media_root=media)
    assert result.moved_proxies == 1
    assert not old_proxy.exists()
    assert new_proxy.read_bytes() == b"proxy-inhalt"


def test_relink_without_existing_proxy_is_not_an_error(proj):
    media = _media(proj)
    (media / "neu").mkdir()
    shutil.move(media / "a" / "clip.mp4", media / "neu" / "clip.mp4")

    result = plan_relink(proj)
    assert apply_relink(proj, result) == 1
    assert result.moved_proxies == 0


def test_final_render_finds_original_after_relink(proj):
    """Abnahme E: verschobenes Original -> Final-Render bricht ab; nach `relink` laeuft er."""
    from frameforge.render import RenderError, render_final
    from frameforge.timeline import Timeline

    media = proj.config.media_root
    (media / "neu").mkdir()
    shutil.move(media / "a" / "clip.mp4", media / "neu" / "clip.mp4")

    export = proj.export("teaser")
    export.ensure_dirs()
    timeline = Timeline(
        export="teaser",
        fps=25,
        resolution=(320, 240),
        duration=1.0,
        tracks={"video": [{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 1.0, "tl_in": 0}]},
    )

    with pytest.raises(RenderError, match="Original-Asset"):
        render_final(proj, export, timeline)

    apply_relink(proj, plan_relink(proj))

    out_path = render_final(proj, export, timeline)
    assert out_path.exists()


def test_offline_media_root_raises_instead_of_reporting_everything_orphaned(proj, tmp_path):
    shutil.rmtree(proj.config.media_root)
    with pytest.raises(FileNotFoundError):
        plan_relink(proj)
