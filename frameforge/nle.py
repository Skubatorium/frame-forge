"""FCPXML / OTIO Export fuer DaVinci Resolve.

Liest ausschliesslich `frameforge.timeline.Timeline` — dasselbe Schema wie
`frameforge.render`, damit Render und NLE-Export nie auseinanderlaufen
(Plan §4). Kommt in M4.
"""

from __future__ import annotations

from pathlib import Path

from frameforge.timeline import Timeline


def export_fcpxml(timeline: Timeline, out_path: Path) -> None:
    """Schreibt die Timeline als FCPXML fuer DaVinci Resolve."""
    raise NotImplementedError("nle.export_fcpxml kommt in M4")


def export_otio(timeline: Timeline, out_path: Path) -> None:
    """Schreibt die Timeline als OpenTimelineIO-Datei."""
    raise NotImplementedError("nle.export_otio kommt in M4")
