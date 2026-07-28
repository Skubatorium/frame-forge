"""Design-Token-Themes (wählbare Farb-/Typo-Startsets).

Analog zu den Stil-Presets, aber für den *Look*: ein Theme ist ein benanntes Startset an
Design-Tokens (Palette, Schriften, Motion) unter `themes/` (mitgeliefert) und optional unter
`~/.frameforge/themes/` (eigene). Der Design-Schritt kann eines als Ausgangspunkt nach
`design/tokens.yaml` schreiben (`apply_theme`) — der Nutzer/Agent passt es dann an. Es ersetzt
nicht das Gespräch, es gibt ihm nur einen guten Startpunkt.

**Eigenes Theme:** eine YAML nach `~/.frameforge/themes/<slug>.yaml` legen
(`frameforge theme-new` gerüstet eine), dann per Slug wählen.
"""

from __future__ import annotations

from pathlib import Path

import yaml

THEMES_DIR = Path(__file__).resolve().parent.parent / "themes"
USER_THEMES_DIR = Path.home() / ".frameforge" / "themes"

_META_KEYS = ("slug", "name", "description", "example")


class ThemeNotFoundError(ValueError):
    """Es gibt kein Theme mit diesem Slug."""


def _theme_paths() -> dict[str, Path]:
    """Slug -> Pfad. Eigene Themes (`~/.frameforge/themes`) überschreiben mitgelieferte."""
    paths: dict[str, Path] = {}
    for d in (THEMES_DIR, USER_THEMES_DIR):
        if d.is_dir():
            for path in sorted(d.glob("*.yaml")):
                paths[path.stem] = path
    return paths


def list_themes() -> list[dict]:
    """Alle Themes als `{slug, name, description, example, custom}`, sortiert nach Slug."""
    out = []
    for slug, path in sorted(_theme_paths().items()):
        data = yaml.safe_load(path.read_text()) or {}
        out.append(
            {
                "slug": data.get("slug", slug),
                "name": data.get("name", slug),
                "description": (data.get("description") or "").strip(),
                "example": (data.get("example") or "").strip(),
                "custom": path.parent == USER_THEMES_DIR,
            }
        )
    return out


def load_theme(slug: str) -> dict:
    """Vollständiges Theme (inkl. Metadaten)."""
    path = _theme_paths().get(slug)
    if path is None:
        known = ", ".join(sorted(_theme_paths()))
        raise ThemeNotFoundError(f"Theme '{slug}' unbekannt — verfügbar: {known}")
    return yaml.safe_load(path.read_text()) or {}


def theme_tokens(slug: str) -> dict:
    """Nur die Token-Werte eines Themes (ohne Metadaten)."""
    theme = load_theme(slug)
    return {k: v for k, v in theme.items() if k not in _META_KEYS}


def apply_theme(slug: str, tokens_path: Path) -> Path:
    """Schreibt die Tokens eines Themes nach `tokens_path` (z.B. `design/tokens.yaml`)."""
    tokens = theme_tokens(slug)
    tokens_path.parent.mkdir(parents=True, exist_ok=True)
    tokens_path.write_text(yaml.safe_dump(tokens, allow_unicode=True, sort_keys=False))
    return tokens_path


_SCAFFOLD = """\
slug: {slug}
name: {slug}
description: >-
  <Charakter der Palette in ein bis zwei Saetzen.>
example: <Wofuer der Look passt / welche Stimmung.>

primary_color: "#12222f"
secondary_color: "#2c4a5a"
accent_color: "#e0a458"
text_color: "#ffffff"
font_display: "Helvetica Neue"
font_text: "Helvetica Neue"
motion: {{ fade_in_s: 0.5, fade_out_s: 0.6, overlay_hold_min_s: 2.0 }}
type_scale: {{ title: 96, subtitle: 36, caption: 28 }}
"""


def scaffold_theme(slug: str) -> Path:
    """Schreibt eine Vorlage nach `~/.frameforge/themes/<slug>.yaml` (nicht überschreibend)."""
    USER_THEMES_DIR.mkdir(parents=True, exist_ok=True)
    path = USER_THEMES_DIR / f"{slug}.yaml"
    if path.exists():
        raise FileExistsError(f"{path} existiert bereits")
    path.write_text(_SCAFFOLD.format(slug=slug))
    return path
