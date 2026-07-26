"""FFmpeg-Graph-Bau, Proxy-/Final-Render.

**Einziger Ort im Package, der `ffmpeg` aufrufen darf** (CLAUDE.md: "Nackte
`ffmpeg`-Aufrufe sind verboten"). Baut den Filtergraph ausschliesslich aus
`timeline.json` (`frameforge.timeline.Timeline`), damit jeder Render
reproduzierbar ist. Kommt in M1 (Proxy) / M4 (Final, 4K-Mapping, EBU R128).
"""

from __future__ import annotations

from pathlib import Path

from frameforge.project import Export, Project
from frameforge.timeline import Timeline


def build_filtergraph(timeline: Timeline) -> str:
    """Baut den FFmpeg-Filtergraph-String aus einer validierten Timeline."""
    raise NotImplementedError("render.build_filtergraph kommt in M1")


def render_proxy(project: Project, export: Export, timeline: Timeline) -> Path:
    """1080p-Proxy-Render fuer `ff-preview`, mappt auf die Proxy-Assets."""
    raise NotImplementedError("render.render_proxy kommt in M1")


def render_final(project: Project, export: Export, timeline: Timeline) -> Path:
    """4K-Final-Render, mappt automatisch auf die Original-Assets. Kommt in M4."""
    raise NotImplementedError("render.render_final kommt in M4")
