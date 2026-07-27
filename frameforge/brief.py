"""Brief-Schema für einen Export (`exports/<export>/brief.yaml`).

Der Brief macht aus demselben Material verschiedene Filme: Stil-Preset, Ziellänge, Muss-/
verbotene Shots, Sprache — plus optionale Overrides der Preset-Parameter (color_grade, pacing …).
Ein Pydantic-Schema gibt Struktur und fängt Tippfehler früh; `merged()` legt die Parameter des
gewählten Presets unter den Brief (Overrides gewinnen), sodass Story-/Timeline-Bau eine
vollständige, aufgelöste Sicht bekommen.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from frameforge.presets import list_presets


class BriefError(ValueError):
    """`brief.yaml` ist fehlerhaft oder verweist auf ein unbekanntes Preset."""


class Brief(BaseModel):
    """Inhalt von `brief.yaml`. Zusätzliche Preset-Overrides (color_grade, pacing …) sind erlaubt."""

    model_config = ConfigDict(extra="allow")

    preset: str | None = None
    target_duration_s: float | None = Field(default=None, gt=0)
    language: str = "de"
    must_shots: list[str] = Field(default_factory=list)
    forbidden_shots: list[str] = Field(default_factory=list)

    @field_validator("preset")
    @classmethod
    def _known_preset(cls, value: str | None) -> str | None:
        if value is None:
            return value
        known = {p["slug"] for p in list_presets()}
        if value not in known:
            raise ValueError(
                f"Unbekanntes Preset '{value}' — verfügbar: {', '.join(sorted(known))}. "
                "Siehe 'frameforge presets'."
            )
        return value

    @classmethod
    def load(cls, path: Path) -> Brief:
        """Lädt und validiert `brief.yaml`. Wirft `BriefError` bei Schema-/Preset-Fehlern."""
        try:
            raw = yaml.safe_load(path.read_text()) or {}
            return cls.model_validate(raw)
        except Exception as exc:
            raise BriefError(f"{path}: {exc}") from exc

    def merged(self) -> dict:
        """Brief als Dict mit den unter das Preset gelegten Parametern (Overrides gewinnen)."""
        from frameforge.presets import apply_preset

        return apply_preset(self.model_dump(exclude_none=True))
