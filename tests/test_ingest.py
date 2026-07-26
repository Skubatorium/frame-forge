"""Tests fuer den Ingest-Cache-Schluessel, Scan und Proxy-Erzeugung."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from frameforge.ingest import build_proxies, hash_file, proxy_path, scan_media

FIXTURES = Path(__file__).parent / "fixtures"


def test_hash_file_is_deterministic_for_unchanged_file(tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"x" * 100)
    assert hash_file(f) == hash_file(f)


def test_hash_file_changes_when_content_changes(tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"a" * 100)
    before = hash_file(f)
    f.write_bytes(b"b" * 100)
    os.utime(f, (0, 1))
    after = hash_file(f)
    assert before != after


def test_hash_file_changes_when_mtime_changes_but_content_same(tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"x" * 100)
    before = hash_file(f)
    os.utime(f, (0, 12345))
    after = hash_file(f)
    assert before != after


@pytest.fixture
def media_root(tmp_path):
    root = tmp_path / "media"
    root.mkdir()
    shutil.copy(FIXTURES / "clip.mp4", root / "clip.mp4")
    shutil.copy(FIXTURES / "photo.jpg", root / "photo.jpg")
    (root / ".DS_Store").write_text("junk")
    (root / "notes.txt").write_text("kein Medienformat")
    sub = root / "day02"
    sub.mkdir()
    shutil.copy(FIXTURES / "photo.jpg", sub / "photo2.jpg")
    return root


def test_scan_media_finds_video_and_photo_recursively(media_root):
    found = scan_media(media_root)
    names = sorted(p.name for p in found)
    assert names == ["clip.mp4", "photo.jpg", "photo2.jpg"]


def test_scan_media_ignores_hidden_and_non_media_files(media_root):
    found = scan_media(media_root)
    assert all(not p.name.startswith(".") for p in found)
    assert all(p.suffix.lower() != ".txt" for p in found)


def test_scan_media_missing_root_raises():
    with pytest.raises(FileNotFoundError):
        scan_media(Path("/nonexistent/media/root"))


def test_proxy_path_normalizes_video_extension_to_mp4(tmp_path):
    assert proxy_path(Path("clip.MOV"), tmp_path) == tmp_path / "clip.mp4"


def test_proxy_path_keeps_photo_name(tmp_path):
    assert proxy_path(Path("photo.jpg"), tmp_path) == tmp_path / "photo.jpg"


def test_build_proxies_transcodes_video_and_copies_photo(media_root, tmp_path):
    assets = scan_media(media_root)
    out_dir = tmp_path / "proxies"

    proxies = build_proxies(assets, out_dir)

    assert len(proxies) == 3
    for proxy in proxies:
        assert proxy.exists()
        assert proxy.stat().st_size > 0
    video_proxy = next(p for p in proxies if p.suffix == ".mp4")
    assert video_proxy.parent == out_dir
