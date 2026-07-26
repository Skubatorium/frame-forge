"""Tests fuer den `preload_cairo`-Fix (siehe Modul-Docstring in `design.py`)."""

from __future__ import annotations

import ctypes.util

import pytest

from frameforge import design


def test_preload_cairo_patches_find_library_for_missing_lib(monkeypatch, tmp_path):
    fake_lib = tmp_path / "libcairo.2.dylib"
    fake_lib.write_bytes(b"")

    monkeypatch.setattr(design, "_patched", False)
    monkeypatch.setattr(design, "_CAIRO_LIB_PATTERNS", (str(fake_lib),))
    monkeypatch.setattr(ctypes.util, "find_library", lambda name: None)

    design.preload_cairo()

    assert ctypes.util.find_library("cairo-2") == str(fake_lib)
    assert ctypes.util.find_library("something-else") is None


def test_preload_cairo_raises_when_lib_truly_missing(monkeypatch):
    monkeypatch.setattr(design, "_patched", False)
    monkeypatch.setattr(design, "_CAIRO_LIB_PATTERNS", ())
    monkeypatch.setattr(ctypes.util, "find_library", lambda name: None)

    with pytest.raises(design.CairoNotFoundError):
        design.preload_cairo()


def test_preload_cairo_noop_if_already_found(monkeypatch):
    monkeypatch.setattr(design, "_patched", False)
    monkeypatch.setattr(ctypes.util, "find_library", lambda name: "/usr/lib/libcairo.dylib")

    design.preload_cairo()  # darf nicht werfen, obwohl _CAIRO_LIB_PATTERNS nicht matcht
