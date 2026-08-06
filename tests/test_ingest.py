"""Tests fuer den Ingest-Cache-Schluessel, Scan und Proxy-Erzeugung."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from frameforge.ingest import build_proxies, hash_file, proxy_path, scan_media

FIXTURES = Path(__file__).parent / "fixtures"


def _streams(path: Path) -> list[dict]:
    """Streams einer Mediendatei per ffprobe — fuer Assertions ueber Spurauswahl."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)["streams"]


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


def test_proxy_path_normalizes_heic_to_jpg(tmp_path):
    """HEIC-Proxies sind JPEGs — ffmpeg kann HEIC nicht lesen (PROGRESS.md HEIC-1)."""
    result = proxy_path(Path("/media/IMG_0001.HEIC"), tmp_path, media_root=Path("/media"))
    assert result.suffix == ".jpg"
    assert result.stem.startswith("IMG_0001_")


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


def test_build_proxies_takes_exactly_the_first_audio_track(media_root, tmp_path):
    """Der Proxy traegt genau **eine** Tonspur, und zwar die erste.

    **Was dieser Test nicht leistet:** Er reproduziert den Absturz von `IMG_9838.MOV` nicht.
    Ausloeser dort ist eine `apac`-Spur ohne ffmpeg-Decoder; ein solches Fixture liess sich
    nicht bauen (ffmpeg verweigert den Tag beim Muxen, ein Byte-Patch setzt zwar den Tag,
    ffmpeg findet aber weiterhin einen Decoder). Gegengeprueft: dieser Test besteht auch mit
    zurueckgebautem `-map`. Der Fix ist stattdessen **direkt an der echten Datei** belegt
    (Exit 234 ohne, Exit 0 mit Mapping) — siehe PROGRESS.md.

    Was er leistet: er haelt die Spurauswahl fest. Ein spaeteres `-map 0:a` (alle Spuren)
    oder `-map 0:a:1` faellt hier auf.
    """
    shutil.copy(FIXTURES / "clip_multiaudio.mov", media_root / "spatial.mov")
    out_dir = tmp_path / "proxies"

    result = build_proxies([media_root / "spatial.mov"], out_dir, media_root=media_root)

    assert result.failures == []
    audio = [s for s in _streams(result.proxies[0]) if s["codec_type"] == "audio"]
    assert len(audio) == 1, "genau eine Tonspur im Proxy"
    assert audio[0]["channels"] == 2, "die erste (Stereo-), nicht die kanalreichere Spur"


def test_build_proxies_handles_video_without_audio(media_root, tmp_path):
    """`-map 0:a:0?` ist optional — ein stummer Clip darf daran nicht scheitern."""
    out_dir = tmp_path / "proxies"

    result = build_proxies([media_root / "clip.mp4"], out_dir, media_root=media_root)

    assert result.failures == []
    assert [s["codec_type"] for s in _streams(result.proxies[0])] == ["video"]


def test_build_proxies_converts_heic_to_full_resolution_jpeg(media_root, tmp_path):
    """HEIC wird **nicht** 1:1 kopiert, sondern nach JPEG umgesetzt — in voller Aufloesung.

    Der Proxy ist hier nicht "kleiner", sondern schlicht "lesbar": er geht auch in den
    Final-Render (`render_final`), weil ffmpeg das Original nicht verwenden kann. Ein
    Downscale wuerde dort echte Bildgroesse kosten.
    """
    shutil.copy(FIXTURES / "photo.heic", media_root / "IMG_0001.HEIC")
    out_dir = tmp_path / "proxies"

    result = build_proxies(scan_media(media_root), out_dir, media_root=media_root)

    assert result.failures == []
    heic_proxy = next(p for p in result.proxies if p.stem.startswith("IMG_0001_"))
    assert heic_proxy.suffix == ".jpg"
    image = Image.open(heic_proxy)
    assert image.format == "JPEG"
    assert image.size == Image.open(FIXTURES / "photo.heic").size


def test_build_proxies_reports_unreadable_photo_instead_of_copying_it(media_root, tmp_path):
    """Ein kaputtes HEIC landet als `IngestFailure`, nicht als unbrauchbare Kopie im Cache."""
    (media_root / "kaputt.heic").write_bytes(b"kein heif")
    out_dir = tmp_path / "proxies"

    result = build_proxies(scan_media(media_root), out_dir, media_root=media_root)

    assert [f.asset.name for f in result.failures] == ["kaputt.heic"]
    assert not any(p.stem.startswith("kaputt_") for p in result.proxies)


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
