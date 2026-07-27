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
    result = proxy_path(Path("/media/clip.MOV"), tmp_path, media_root=Path("/media"))
    assert result.parent == tmp_path
    assert result.suffix == ".mp4"
    assert result.stem.startswith("clip_")


def test_proxy_path_keeps_photo_extension(tmp_path):
    result = proxy_path(Path("/media/photo.jpg"), tmp_path, media_root=Path("/media"))
    assert result.suffix == ".jpg"
    assert result.stem.startswith("photo_")


def test_proxy_path_disambiguates_same_basename_in_different_dirs(tmp_path):
    """Regressionstest fuer K1 (Audit): gleicher Basename in verschiedenen Ordnern

    (z.B. DJI_0001.MP4 pro SD-Karte) darf nicht auf denselben Proxy zeigen.
    """
    media_root = Path("/media")
    a = proxy_path(media_root / "day01/DJI_0001.MP4", tmp_path, media_root=media_root)
    b = proxy_path(media_root / "day02/DJI_0001.MP4", tmp_path, media_root=media_root)
    assert a != b


def test_proxy_path_is_stable_for_same_file(tmp_path):
    media_root = Path("/media")
    p = media_root / "day01/DJI_0001.MP4"
    assert proxy_path(p, tmp_path, media_root=media_root) == proxy_path(
        p, tmp_path, media_root=media_root
    )


def test_build_proxies_transcodes_video_and_copies_photo(media_root, tmp_path):
    assets = scan_media(media_root)
    out_dir = tmp_path / "proxies"

    result = build_proxies(assets, out_dir, media_root=media_root)

    assert len(result.proxies) == 3
    assert result.failures == []
    for proxy in result.proxies:
        assert proxy.exists()
        assert proxy.stat().st_size > 0
    video_proxy = next(p for p in result.proxies if p.suffix == ".mp4")
    assert video_proxy.parent == out_dir


def test_build_proxies_skips_existing_proxies(media_root, tmp_path):
    """Idempotenz/Resume: ein zweiter Lauf baut nichts neu."""
    assets = scan_media(media_root)
    out_dir = tmp_path / "proxies"
    first = build_proxies(assets, out_dir, media_root=media_root)
    mtimes = {p: p.stat().st_mtime_ns for p in first.proxies}

    second = build_proxies(assets, out_dir, media_root=media_root)

    assert {p for p in second.proxies} == set(mtimes)
    for p in second.proxies:
        assert p.stat().st_mtime_ns == mtimes[p]  # nicht neu geschrieben


def test_build_proxies_skips_corrupt_video_without_aborting(media_root, tmp_path):
    """Eine kaputte Datei bricht nicht den ganzen Lauf ab, wird als failure gesammelt."""
    bad = media_root / "corrupt.mp4"
    bad.write_bytes(b"not a real video")
    out_dir = tmp_path / "proxies"

    result = build_proxies(scan_media(media_root), out_dir, media_root=media_root)

    assert any(f.asset.name == "corrupt.mp4" for f in result.failures)
    # Die intakten Assets sind trotzdem da.
    assert len(result.proxies) == 3


def test_proxy_path_stable_across_symlinked_media_root(tmp_path):
    """Regressionstest: media_root ueber einen Symlink (wie macOS /var) und aufgeloest muessen

    denselben Proxy-Schluessel ergeben — sonst findet Render den vom Ingest gebauten Proxy nicht.
    """
    real = tmp_path / "real_media"
    (real / "day01").mkdir(parents=True)
    (real / "day01" / "clip.mp4").write_bytes(b"x")
    link = tmp_path / "linked_media"
    link.symlink_to(real)

    via_link = proxy_path(link / "day01" / "clip.mp4", tmp_path / "px", media_root=link)
    via_real = proxy_path(real / "day01" / "clip.mp4", tmp_path / "px", media_root=real)
    assert via_link == via_real
