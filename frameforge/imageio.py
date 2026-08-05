"""Zentrales Bild-IO — der **einzige** Weg, ein Standbild in Python zu oeffnen.

Warum ein eigenes Modul: HEIC/HEIF liest weder Pillow noch OpenCV von Haus aus.
`pillow-heif` ruestet Pillow nach, muss dafuer aber einen Opener registrieren — und zwar
**genau einmal**. Verstreut man diesen Aufruf ueber `analyze`, `keyframes`, `people` und
`map`, haengt die Lesbarkeit einer Datei davon ab, welches Modul zufaellig zuerst importiert
wurde. Deshalb: alle Standbild-Zugriffe gehen ueber `open_image`/`read_bgr`, die Registrierung
passiert hier beim Import.

`cv2.imread` kann HEIC auch mit `pillow-heif` nicht — die Registrierung wirkt nur auf Pillow.
Der Weg fuer OpenCV-Konsumenten fuehrt deshalb ueber Pillow und dann ins Array (`read_bgr`),
nicht ueber `cv2.imread`.

Nicht lesbare Formate (z.B. `.dng`) werfen `ImageReadError` mit einer Meldung, die Format und
Ursache benennt. Vorher lieferte `cv2.imread` bei HEIC schlicht `None` und die Datei fiel
ueber `preindex`'s Fehlersammlung still aus dem Index.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

__all__ = ["HEIF_EXTENSIONS", "ImageReadError", "open_image", "read_bgr"]

HEIF_EXTENSIONS = frozenset({".heic", ".heif"})

# Formate, die `scan_media` einsammelt, fuer die es aber bewusst keinen Lesepfad gibt.
# Sie werden nicht stillschweigend uebersprungen, sondern erzeugen eine benannte Meldung.
_UNSUPPORTED_HINTS: dict[str, str] = {
    ".dng": (
        "RAW-Format (Adobe DNG) — Pillow und OpenCV lesen es nicht. Im Fundus kommt es "
        "nicht vor; wird es gebraucht, exportiere die Dateien vorher nach JPEG/HEIC oder "
        "ergaenze einen RAW-Decoder (z.B. rawpy) in frameforge.imageio."
    ),
}


class ImageReadError(RuntimeError):
    """Ein Standbild konnte nicht gelesen werden — mit Grund, nicht still."""


def _register_heif_opener() -> bool:
    """Registriert den HEIF-Opener in Pillow. Genau einmal, beim Import dieses Moduls."""
    try:
        from pillow_heif import register_heif_opener
    except ImportError:  # pragma: no cover — Abhaengigkeit steht in pyproject.toml
        return False
    register_heif_opener()
    return True


HEIF_AVAILABLE = _register_heif_opener()


def open_image(path: Path) -> Image.Image:
    """Oeffnet ein Standbild als PIL-Image.

    Wirft `ImageReadError` statt `None` zurueckzugeben oder eine Pillow-interne Ausnahme
    durchzureichen — der Aufrufer soll am Typ erkennen, dass die *Datei* das Problem ist.

    **Bewusst ohne `ImageOps.exif_transpose`.** `cv2.imread` hat die EXIF-Orientierung nie
    ausgewertet; sie hier nachzuruesten wuerde den JPEG-Pfad aendern. Noetig waere es
    ohnehin nicht: `pillow-heif` wendet die HEIF-Transformationsboxen (`irot`/`imir`) beim
    Oeffnen an — alle 670 HEIC-Dateien des Fundus liegen bereits richtig herum und tragen
    Orientierung 1. Faellt spaeter Material mit gesetztem Orientierungs-Tag an, gehoert die
    Drehung hierher, mit eigenem Test.
    """
    suffix = path.suffix.lower()
    if not path.exists():
        raise ImageReadError(f"{path}: Datei existiert nicht")
    if suffix in HEIF_EXTENSIONS and not HEIF_AVAILABLE:
        raise ImageReadError(
            f"{path}: HEIC/HEIF, aber pillow-heif ist nicht installiert — "
            f"'uv pip install -e .' im Projekt ausfuehren"
        )
    hint = _UNSUPPORTED_HINTS.get(suffix)
    if hint:
        raise ImageReadError(f"{path}: {hint}")
    try:
        image = Image.open(path)
        image.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageReadError(f"{path}: Bild nicht lesbar ({type(exc).__name__}: {exc})") from exc
    return image


def read_bgr(path: Path) -> np.ndarray:
    """Liest ein Standbild als BGR-`uint8`-Array — das Layout, das OpenCV erwartet.

    Ersetzt `cv2.imread`: identisches Ergebnis fuer JPEG/PNG, funktioniert zusaetzlich fuer
    HEIC. Graustufen- und Palettenbilder werden nach RGB konvertiert, damit das Array immer
    drei Kanaele hat (`cv2.cvtColor(..., COLOR_BGR2GRAY)` setzt das voraus).
    """
    image = open_image(path).convert("RGB")
    rgb = np.asarray(image, dtype=np.uint8)
    return rgb[:, :, ::-1].copy()  # RGB -> BGR; copy(), damit das Array zusammenhaengend ist
