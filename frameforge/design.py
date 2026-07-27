"""Design-Tokens -> SVG-Templates -> PNG mit Alpha.

`preload_cairo()` ist der (gegenueber `docs/plans/HANDOVER.md` korrigierte) Fix fuer
den bekannten Fallstrick: `cairosvg` laedt `libcairo` ueber `cairocffi`, das intern
`ctypes.util.find_library()` fragt und bei Fehlschlag bloss den nackten Dateinamen
(`libcairo.2.dylib`) an `ffi.dlopen()` weiterreicht. Auf Apple Silicon liefert
`find_library()` dafuer nichts, weil die Lib nicht im dyld-Cache steht — und ein
CDLL-Preload der Datei hilft *nicht*, weil macOS' Loader beim Nachladen per nacktem
Namen nicht dedupliziert (empirisch geprueft: `ctypes.CDLL(name)` schlaegt danach
weiterhin fehl). Setzen von `DYLD_FALLBACK_LIBRARY_PATH` in `os.environ` zur Laufzeit
wirkt ebenfalls nicht — dyld liest die `DYLD_*`-Variablen nur beim Prozessstart.

Der einzige Ort, an dem wir eingreifen koennen, bevor `cairocffi` (via `cairosvg`)
zum ersten Mal importiert wird: `ctypes.util.find_library` selbst monkeypatchen, sodass
es fuer die von `cairocffi` versuchten Namen (`cairo-2`, `cairo`, `libcairo-2`) den
tatsaechlichen Homebrew-Pfad liefert. `cairocffi` bindet den Namen per
`from ctypes.util import find_library` beim eigenen Modul-Import — der Patch muss also
strikt *vor* dem ersten `import cairosvg`/`import cairocffi` im Prozess passieren.
"""

from __future__ import annotations

import ctypes.util
import glob
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frameforge.project import Project

# Dateiendungen, die als Design-Grafik zaehlen.
_GRAPHIC_EXTS = (".png", ".jpg", ".jpeg", ".svg", ".webp")
# Bildschirm-Dateinamen in prompts.md erkennen (z.B. "logo.png", "marker-icon.png").
_FILENAME_RE = re.compile(r"\b([\w-]+\.(?:png|jpe?g|svg|webp))\b", re.IGNORECASE)

_CAIRO_NAMES = ("cairo-2", "cairo", "libcairo-2")
_CAIRO_LIB_PATTERNS = (
    "/opt/homebrew/lib/libcairo.2.dylib",
    "/usr/local/lib/libcairo.2.dylib",
)

_patched = False


class CairoNotFoundError(RuntimeError):
    """libcairo konnte weder ueber den Loader noch ueber bekannte Homebrew-Pfade gefunden werden."""


def preload_cairo() -> None:
    """Muss vor dem ersten `import cairosvg` aufgerufen werden. Siehe Modul-Docstring."""
    global _patched
    if _patched or ctypes.util.find_library("cairo"):
        return

    lib_path = next(
        (path for pattern in _CAIRO_LIB_PATTERNS for path in glob.glob(pattern)), None
    )
    if lib_path is None:
        raise CairoNotFoundError("libcairo nicht gefunden — 'brew install cairo' ausfuehren")

    original_find_library = ctypes.util.find_library

    def _patched_find_library(name: str) -> str | None:
        if name in _CAIRO_NAMES:
            return lib_path
        return original_find_library(name)

    ctypes.util.find_library = _patched_find_library
    _patched = True


class TemplateError(RuntimeError):
    """Ein SVG-Template referenziert einen Platzhalter, der nicht in `tokens` vorkommt."""


def build_svg_from_tokens(template_path: Path, tokens: dict) -> str:
    """Fuellt ein SVG-Template (lower-third, title-card, ...) mit Design-Tokens.

    Einfaches `{{key}}`-Templating, kein Jinja — die Templates sind klein und statisch,
    eine zusaetzliche Abhaengigkeit dafuer lohnt sich nicht. Bricht mit `TemplateError` ab,
    wenn nach dem Ersetzen noch ein `{{...}}`-Platzhalter uebrig ist (fehlender Token), statt
    ihn still im gerenderten SVG stehen zu lassen.
    """
    svg = template_path.read_text()
    for key, value in tokens.items():
        svg = svg.replace(f"{{{{{key}}}}}", str(value))

    remaining = re.findall(r"{{\s*[\w.]+\s*}}", svg)
    if remaining:
        raise TemplateError(f"{template_path.name}: fehlende Tokens {sorted(set(remaining))}")
    return svg


def render_svg_to_png(svg: str, out_path: Path) -> None:
    """Rendert SVG-Markup zu PNG mit Alphakanal. Ruft vorher `preload_cairo()` auf."""
    preload_cairo()
    import cairosvg

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(out_path))


# -- Design-Asset-Inventar (fuer Resume nach externem Grafik-Erstellen) -------


@dataclass
class AssetInventory:
    """Abgleich: welche in `prompts.md` angeforderten Grafiken liegen schon in `design/assets/`?"""

    requested: list[str]  # in prompts.md genannte Dateinamen
    present: list[str]  # tatsaechlich in design/assets/ vorhandene Grafiken
    missing: list[str]  # angefordert, aber noch nicht abgelegt
    extra: list[str]  # abgelegt, aber nicht in prompts.md genannt

    @property
    def complete(self) -> bool:
        """True, wenn nichts Angefordertes mehr fehlt (auch True, wenn nichts angefordert war)."""
        return not self.missing


def requested_graphics(prompts_md: Path) -> list[str]:
    """Dateinamen der in `prompts.md` angeforderten Grafiken (aus dem Freitext extrahiert)."""
    if not prompts_md.exists():
        return []
    found = _FILENAME_RE.findall(prompts_md.read_text())
    # dedupliziert, Reihenfolge stabil
    return list(dict.fromkeys(name.lower() for name in found))


def present_graphics(assets_dir: Path) -> list[str]:
    """Grafiken, die tatsaechlich in `design/assets/` liegen."""
    if not assets_dir.is_dir():
        return []
    return sorted(
        p.name for p in assets_dir.iterdir() if p.is_file() and p.suffix.lower() in _GRAPHIC_EXTS
    )


def asset_inventory(project: Project) -> AssetInventory:
    """Gleicht angeforderte Grafiken (`design/prompts.md`) gegen vorhandene (`design/assets/`) ab.

    Damit sieht man beim Wiedereinstieg sofort, welche extern erstellten Grafiken schon abgelegt
    sind und welche noch fehlen (Resume nach dem Bildgenerator-Schritt).
    """
    requested = requested_graphics(project.design_prompts_path)
    present = present_graphics(project.design_assets_dir)
    present_lower = {p.lower() for p in present}
    missing = [r for r in requested if r not in present_lower]
    extra = [p for p in present if p.lower() not in set(requested)]
    return AssetInventory(requested=requested, present=present, missing=missing, extra=extra)
