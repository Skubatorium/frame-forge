"""Tests fuer `frameforge.imageio` — HEIC-Lesbarkeit und klare Fehler statt stillem Ueberspringen.

Kernaussage des Arbeitspakets: ein nicht lesbares Bildformat darf nicht mehr wortlos aus dem
Index fallen. Vorher lieferte `cv2.imread` bei HEIC schlicht `None`, `preindex` fing die
Ausnahme pro Datei ab und der Lauf meldete Erfolg — mehrere hundert Fotos waeren so
verschwunden.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from frameforge.imageio import HEIF_AVAILABLE, ImageReadError, open_image, read_bgr

FIXTURES = Path(__file__).parent / "fixtures"


# -- HEIC lesen ---------------------------------------------------------------------


def test_heif_opener_is_registered():
    assert HEIF_AVAILABLE, "pillow-heif fehlt — 'uv pip install -e .' ausfuehren"


def test_open_image_reads_heic():
    image = open_image(FIXTURES / "photo.heic")
    assert image.size == (64, 48)


def test_read_bgr_reads_heic_where_cv2_imread_fails():
    """Die eigentliche Zusicherung: `cv2.imread` kann HEIC auch mit pillow-heif nicht.

    Die Registrierung wirkt nur auf Pillow. Genau deshalb fuehrt der Weg fuer alle
    OpenCV-Konsumenten ueber `read_bgr` und nicht ueber `cv2.imread`.
    """
    heic = FIXTURES / "photo.heic"
    assert cv2.imread(str(heic)) is None
    array = read_bgr(heic)
    assert array.shape == (48, 64, 3)
    assert array.dtype == np.uint8


# -- Rueckwaertskompatibilitaet: JPEG/PNG-Pfad unveraendert --------------------------


def test_read_bgr_matches_cv2_imread_for_jpeg():
    """`read_bgr` muss `cv2.imread` fuer bestehende Formate **bitgleich** ersetzen.

    Ohne diese Zusicherung koennten sich die Qualitaetsmetriken der 255 bereits
    indizierten Assets bei einer Neu-Analyse aendern.
    """
    jpeg = FIXTURES / "photo.jpg"
    assert np.array_equal(read_bgr(jpeg), cv2.imread(str(jpeg)))


# -- Klare Fehler statt stillem Ueberspringen ----------------------------------------


def test_unreadable_format_raises_named_error(tmp_path):
    """Abnahmekriterium: nicht lesbares Format -> klare Meldung, kein stilles Ueberspringen."""
    broken = tmp_path / "kaputt.jpg"
    broken.write_bytes(b"kein bild, nur bytes")

    with pytest.raises(ImageReadError) as excinfo:
        read_bgr(broken)
    message = str(excinfo.value)
    assert "kaputt.jpg" in message
    assert "nicht lesbar" in message


def test_dng_raises_with_actionable_message(tmp_path):
    """`.dng` bleibt in PHOTO_EXTENSIONS, scheitert aber benannt statt still.

    Entscheidung siehe PROGRESS.md HEIC-5: die Endung zu entfernen wuerde DNG-Dateien
    schon im Scan verschwinden lassen — auch das waere still, nur eine Ebene frueher.
    """
    dng = tmp_path / "raw.dng"
    dng.write_bytes(b"\x00" * 64)

    with pytest.raises(ImageReadError) as excinfo:
        open_image(dng)
    message = str(excinfo.value)
    assert "DNG" in message
    assert "rawpy" in message, "Die Meldung muss einen Ausweg nennen, nicht nur scheitern"


def test_missing_file_raises_image_read_error(tmp_path):
    with pytest.raises(ImageReadError, match="existiert nicht"):
        open_image(tmp_path / "gibts-nicht.jpg")
