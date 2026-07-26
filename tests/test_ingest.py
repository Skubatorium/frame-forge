"""Tests fuer den Ingest-Cache-Schluessel."""

from __future__ import annotations

import os

from frameforge.ingest import hash_file


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
