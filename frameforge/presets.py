"""Stil-Presets als ladbare Daten.

Die sechs Presets aus `docs/styles/style-catalog.md` liegen als YAML unter `presets/` und sind
hier maschinenlesbar: jedes ist ein vollständiger Parametersatz (Pacing, Übergänge, Color-Grade,
Text-Dichte, Musik-Energie, Karten-Nutzung, Ken-Burns, O-Ton-Politik). Der Brief wählt ein
Preset per `slug`; `apply_preset` legt die Preset-Parameter unter den Brief, sodass der Nutzer
nur überschreibt, was er anders will (Preset ≠ Zwangsjacke).
"""

from __future__ import annotations

from pathlib import Path

import yaml

PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets"

# Parameter-Schlüssel eines Presets (alles außer den Metadaten name/slug/description/best_for).
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


def list_presets() -> list[dict]:
    """Alle Presets als `{slug, name, description, best_for}` (Metadaten), sortiert nach Slug."""
    out = []
    for path in sorted(PRESETS_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        out.append(
            {
                "slug": data.get("slug", path.stem),
                "name": data.get("name", path.stem),
                "description": (data.get("description") or "").strip(),
                "best_for": data.get("best_for", ""),
            }
        )
    return out


def load_preset(slug: str) -> dict:
    """Vollständiger Parametersatz eines Presets (inkl. Metadaten)."""
    path = PRESETS_DIR / f"{slug}.yaml"
    if not path.exists():
        known = ", ".join(p["slug"] for p in list_presets())
        raise PresetNotFoundError(f"Preset '{slug}' unbekannt — verfügbar: {known}")
    return yaml.safe_load(path.read_text()) or {}


def apply_preset(brief: dict) -> dict:
    """Legt die Parameter des im Brief gewählten Presets unter den Brief.

    `brief["preset"]` = Slug. Explizite Werte im Brief gewinnen (Overrides). Ohne `preset` oder
    bei unbekanntem Slug wird der Brief unverändert zurückgegeben (der Aufrufer entscheidet, ob
    das ein Fehler ist). Rückgabe ist eine neue Kopie, das Original bleibt unangetastet.
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
    return merged
