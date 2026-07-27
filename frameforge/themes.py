"""Design-Token-Themes (wählbare Farb-/Typo-Startsets).

Analog zu den Stil-Presets, aber für den *Look*: ein Theme ist ein benanntes Startset an
Design-Tokens (Palette, Schriften, Motion) unter `themes/`. Der Design-Schritt kann eines als
Ausgangspunkt nach `design/tokens.yaml` schreiben (`apply_theme`) — der Nutzer/Agent passt es
dann an. Es ersetzt nicht das Gespräch, es gibt ihm nur einen guten Startpunkt.
"""

from __future__ import annotations

from pathlib import Path

import yaml

THEMES_DIR = Path(__file__).resolve().parent.parent / "themes"

_META_KEYS = ("slug", "name", "description")


class ThemeNotFoundError(ValueError):
    """Es gibt kein Theme mit diesem Slug."""


def list_themes() -> list[dict]:
    """Alle Themes als `{slug, name, description}`, sortiert nach Slug."""
    out = []
    for path in sorted(THEMES_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        out.append(
            {
                "slug": data.get("slug", path.stem),
                "name": data.get("name", path.stem),
                "description": (data.get("description") or "").strip(),
            }
        )
    return out


def load_theme(slug: str) -> dict:
    """Vollständiges Theme (inkl. Metadaten)."""
    path = THEMES_DIR / f"{slug}.yaml"
    if not path.exists():
        known = ", ".join(t["slug"] for t in list_themes())
        raise ThemeNotFoundError(f"Theme '{slug}' unbekannt — verfügbar: {known}")
    return yaml.safe_load(path.read_text()) or {}


def theme_tokens(slug: str) -> dict:
    """Nur die Token-Werte eines Themes (ohne slug/name/description)."""
    theme = load_theme(slug)
    return {k: v for k, v in theme.items() if k not in _META_KEYS}


def apply_theme(slug: str, tokens_path: Path) -> Path:
    """Schreibt die Tokens eines Themes nach `tokens_path` (z.B. `design/tokens.yaml`)."""
    tokens = theme_tokens(slug)
    tokens_path.parent.mkdir(parents=True, exist_ok=True)
    tokens_path.write_text(yaml.safe_dump(tokens, allow_unicode=True, sort_keys=False))
    return tokens_path
