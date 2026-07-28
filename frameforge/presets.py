"""Stil-Presets als ladbare Daten.

Presets liegen als YAML unter `presets/` (mitgeliefert) und optional unter
`~/.frameforge/presets/` (eigene). Jedes ist ein vollständiger Parametersatz (Pacing,
Übergänge, Color-Grade, Text-Dichte, Musik-Energie, Karten-Nutzung, Ken-Burns, O-Ton-Politik)
plus Beschreibung, Beispiel und Dramaturgie-Bogen (`arc`). Der Brief wählt ein Preset per
`slug`; `apply_preset` legt die Preset-Parameter unter den Brief, sodass der Nutzer nur
überschreibt, was er anders will (Preset ≠ Zwangsjacke).

**Eigenes Preset:** entweder eine YAML nach `~/.frameforge/presets/<slug>.yaml` legen
(`frameforge preset-new` gerüstet eine), oder die Parameter direkt (ohne `preset:`) in
`brief.yaml` schreiben — beides funktioniert.
"""

from __future__ import annotations

from pathlib import Path

import yaml

PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets"
USER_PRESETS_DIR = Path.home() / ".frameforge" / "presets"

# Parameter-Schlüssel eines Presets (alles außer den Metadaten).
PRESET_PARAM_KEYS = (
    "pacing",
    "transition_vocabulary",
    "color_grade",
    "text_density",
    "music_energy_curve",
    "map_usage",
    "photo_treatment",
    "original_audio_policy",
)


class PresetNotFoundError(ValueError):
    """Es gibt kein Preset mit diesem Slug."""


def _preset_paths() -> dict[str, Path]:
    """Slug -> Pfad. Eigene Presets (`~/.frameforge/presets`) überschreiben mitgelieferte."""
    paths: dict[str, Path] = {}
    for d in (PRESETS_DIR, USER_PRESETS_DIR):
        if d.is_dir():
            for path in sorted(d.glob("*.yaml")):
                paths[path.stem] = path
    return paths


def list_presets() -> list[dict]:
    """Alle Presets als Metadaten (`slug, name, description, best_for, example, arc`), nach Slug."""
    out = []
    for slug, path in sorted(_preset_paths().items()):
        data = yaml.safe_load(path.read_text()) or {}
        out.append(
            {
                "slug": data.get("slug", slug),
                "name": data.get("name", slug),
                "description": (data.get("description") or "").strip(),
                "best_for": data.get("best_for", ""),
                "example": (data.get("example") or "").strip(),
                "arc": (data.get("arc") or "").strip(),
                "custom": path.parent == USER_PRESETS_DIR,
            }
        )
    return out


def load_preset(slug: str) -> dict:
    """Vollständiger Parametersatz eines Presets (inkl. Metadaten)."""
    path = _preset_paths().get(slug)
    if path is None:
        known = ", ".join(sorted(_preset_paths()))
        raise PresetNotFoundError(f"Preset '{slug}' unbekannt — verfügbar: {known}")
    return yaml.safe_load(path.read_text()) or {}


def known_slugs() -> set[str]:
    return set(_preset_paths())


def apply_preset(brief: dict) -> dict:
    """Legt die Parameter des im Brief gewählten Presets unter den Brief.

    `brief["preset"]` = Slug. Explizite Werte im Brief gewinnen (Overrides). Ohne `preset` oder
    bei unbekanntem Slug wird der Brief unverändert (als Kopie) zurückgegeben.
    """
    slug = brief.get("preset")
    if not slug:
        return dict(brief)
    try:
        preset = load_preset(slug)
    except PresetNotFoundError:
        return dict(brief)

    merged = dict(brief)
    for key in PRESET_PARAM_KEYS:
        if key in preset and key not in merged:
            merged[key] = preset[key]
    # Dramaturgischer Bogen als Orientierung fuer den story-architect mitreichen.
    if preset.get("arc") and "arc" not in merged:
        merged["arc"] = str(preset["arc"]).strip()
    return merged


_SCAFFOLD = """\
slug: {slug}
name: {slug}
description: >-
  <Ein bis zwei Sätze: Charakter des Stils.>
best_for: <wofuer>
example: <So sieht das konkret aus.>
arc: <Dramaturgischer Bogen - Intro, Aufbau, Hoehepunkt, Ausklang.>

pacing: {{ min_s: 2, max_s: 5, rhythm: steady }}
transition_vocabulary: [cut, fade]
color_grade: {{ mood: natural, contrast: medium }}
text_density: minimal
music_energy_curve: gradual_build
map_usage: between_chapters
photo_treatment: {{ ken_burns: moderate }}
original_audio_policy: selective_keep
"""


def scaffold_preset(slug: str) -> Path:
    """Schreibt eine Vorlage nach `~/.frameforge/presets/<slug>.yaml` (nicht überschreibend)."""
    USER_PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    path = USER_PRESETS_DIR / f"{slug}.yaml"
    if path.exists():
        raise FileExistsError(f"{path} existiert bereits")
    path.write_text(_SCAFFOLD.format(slug=slug))
    return path
