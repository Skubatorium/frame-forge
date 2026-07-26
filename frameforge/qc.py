"""Timeline-Checks vor dem Render.

`validate()` deckt bisher nur die Schema-Semantik ab (delegiert an
`Timeline.validate_semantics()`). Das echte Regelwerk aus Plan §5
(schwarze Frames, Audio-Clipping, Textlesbarkeit, Clip-Doppler gegen den
Brief) kommt mit dem `qc-reviewer`-Agenten in M2.
"""

from __future__ import annotations

from frameforge.timeline import Timeline, TimelineValidationError


def validate(timeline: Timeline) -> list[str]:
    """Liste gefundener Probleme; leer heisst "besteht die Pruefung"."""
    try:
        timeline.validate_semantics()
    except TimelineValidationError as exc:
        return [str(exc)]
    return []
