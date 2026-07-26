"""Projekt- und Export-Pfadauflösung.

Loest Projektnamen zu Verzeichnisstrukturen auf (siehe Plan Abschnitt 1,
"Projekt-Struktur pro Videoprojekt"). Kennt keine Analyse- oder Render-Logik —
nur Pfade und die `project.yaml`-Konfiguration.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from frameforge.state import ProjectState

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
CACHE_ROOT = Path.home() / ".cache" / "frameforge"


class ProjectNotFoundError(RuntimeError):
    """Projektordner oder `project.yaml` fehlt."""


class ProjectConfig(BaseModel):
    """Inhalt von `project.yaml`."""

    name: str
    media_root: Path
    timezone: str = "UTC"
    language: str = "de"
    extra: dict = Field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> ProjectConfig:
        raw = yaml.safe_load(path.read_text()) or {}
        return cls.model_validate(raw)

    def save(self, path: Path) -> None:
        payload = self.model_dump(mode="json", exclude={"extra"})
        payload.update(self.extra)
        path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))


@dataclass(frozen=True)
class Export:
    """Pfade fuer einen einzelnen Export (`exports/<name>/...`)."""

    project: Project
    name: str

    @property
    def root(self) -> Path:
        return self.project.exports_dir / self.name

    @property
    def brief_path(self) -> Path:
        return self.root / "brief.yaml"

    @property
    def beatsheet_path(self) -> Path:
        return self.root / "beatsheet.md"

    @property
    def timeline_path(self) -> Path:
        return self.root / "timeline.json"

    @property
    def overlays_dir(self) -> Path:
        return self.root / "overlays"

    @property
    def map_dir(self) -> Path:
        return self.root / "map"

    @property
    def preview_dir(self) -> Path:
        return self.root / "preview"

    @property
    def final_dir(self) -> Path:
        return self.root / "final"

    @property
    def nle_dir(self) -> Path:
        return self.root / "nle"

    def ensure_dirs(self) -> None:
        for d in (self.overlays_dir, self.map_dir, self.preview_dir, self.final_dir, self.nle_dir):
            d.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Project:
    """Pfade und Konfiguration fuer ein Projekt (`projects/<name>/...`)."""

    root: Path
    config: ProjectConfig

    # -- Top-Level ------------------------------------------------------

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def config_path(self) -> Path:
        return self.root / "project.yaml"

    @property
    def state_path(self) -> Path:
        return self.root / ".state.json"

    # -- design/ ----------------------------------------------------------

    @property
    def design_dir(self) -> Path:
        return self.root / "design"

    @property
    def design_tokens_path(self) -> Path:
        return self.design_dir / "tokens.yaml"

    @property
    def design_fonts_dir(self) -> Path:
        return self.design_dir / "fonts"

    @property
    def design_assets_dir(self) -> Path:
        return self.design_dir / "assets"

    @property
    def design_prompts_path(self) -> Path:
        return self.design_dir / "prompts.md"

    # -- index/ -------------------------------------------------------------

    @property
    def index_dir(self) -> Path:
        return self.root / "index"

    @property
    def assets_json_path(self) -> Path:
        return self.index_dir / "assets.json"

    @property
    def assets_dir(self) -> Path:
        return self.index_dir / "assets"

    @property
    def days_dir(self) -> Path:
        return self.index_dir / "days"

    # -- route/ ---------------------------------------------------------

    @property
    def route_dir(self) -> Path:
        return self.root / "route"

    @property
    def gpx_path(self) -> Path:
        return self.route_dir / "roadtrip.gpx"

    @property
    def locations_csv_path(self) -> Path:
        return self.route_dir / "locations.csv"

    # -- music/ -----------------------------------------------------------

    @property
    def music_dir(self) -> Path:
        return self.root / "music"

    @property
    def music_analysis_dir(self) -> Path:
        return self.music_dir / "analysis"

    # -- exports/ -------------------------------------------------------

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    def export(self, name: str) -> Export:
        return Export(self, name)

    def list_exports(self) -> list[str]:
        if not self.exports_dir.exists():
            return []
        return sorted(p.name for p in self.exports_dir.iterdir() if p.is_dir())

    # -- Cache (ausserhalb des Repos, siehe Plan Abschnitt 1) ------------

    @property
    def cache_dir(self) -> Path:
        project_hash = hashlib.sha256(str(self.root.resolve()).encode()).hexdigest()[:16]
        return CACHE_ROOT / project_hash

    # -- State ------------------------------------------------------------

    def load_state(self) -> ProjectState:
        return ProjectState.load(self.state_path)


def list_projects() -> list[str]:
    """Alle Projektnamen unter `projects/`, die eine `project.yaml` haben."""
    if not PROJECTS_DIR.exists():
        return []
    return sorted(
        p.name
        for p in PROJECTS_DIR.iterdir()
        if p.is_dir() and (p / "project.yaml").exists()
    )


def resolve_project(name: str) -> Project:
    """Loest einen Projektnamen zu einem `Project` auf.

    Raises:
        ProjectNotFoundError: wenn der Ordner oder `project.yaml` fehlt.
    """
    root = PROJECTS_DIR / name
    config_path = root / "project.yaml"
    if not config_path.exists():
        raise ProjectNotFoundError(
            f"Projekt '{name}' nicht gefunden — erwartet: {config_path}"
        )
    config = ProjectConfig.load(config_path)
    return Project(root=root, config=config)
