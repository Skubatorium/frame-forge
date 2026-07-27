"""Timeline-Checks vor dem Render.

Deckt das Regelwerk aus Plan §5 ab, soweit es sich aus `timeline.json` (+ optional
`brief.yaml`) ableiten laesst — ohne einen bereits gerenderten Preview zu brauchen:
Schema-Semantik, Lücken/Überlappungen in der Video-Spur ("schwarze Frames" bei diesem
Renderer, der Clips hart hintereinander schneidet statt Lücken zu respektieren,
Audio-Clipping-Risiko (positiver Gain), Text-Lesbarkeit (Mindestdauer von Overlays),
Clip-Wiederholung, und — falls ein Brief übergeben wird — Ziellänge sowie Muss-/verbotene
Shots.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from frameforge.timeline import Timeline, TimelineValidationError

MIN_OVERLAY_READABLE_S = 1.2
MAX_ASSET_REPEATS = 2
DURATION_TOLERANCE_S = 2.0


def timeline_fingerprint(path: Path) -> str:
    """SHA256 der `timeline.json`-Bytes — bindet eine Freigabe an den exakten Timeline-Stand.

    Aendert sich die Timeline nach der Freigabe, weicht der Fingerprint ab und der
    Final-Render kann die Freigabe als veraltet erkennen (Audit-Findings P2/P3).
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_video_coverage(timeline: Timeline) -> list[str]:
    """Lücken/Überlappungen in der Video-Spur.

    Der M1-Renderer (`render.build_filtergraph`) schneidet Video-Clips hart hintereinander,
    unabhängig von `tl_in` — eine Lücke fällt dort nicht als schwarzer Frame auf, sondern als
    fehlender Inhalt (die Timeline behauptet eine Position, die im Render nie auftaucht).
    Eine Überlappung bedeutet, zwei Clips beanspruchen denselben Zeitraum. Beides ist ein
    Timeline-Fehler, den QC vor dem Render fangen soll.
    """
    issues = []
    clips = sorted(timeline.tracks.video, key=lambda c: c.tl_in)
    cursor = 0.0
    for clip in clips:
        if clip.tl_in > cursor + 1e-6:
            issues.append(
                f"Lücke in der Video-Spur zwischen {cursor:.2f}s und {clip.tl_in:.2f}s "
                f"(erscheint im Render als fehlender Inhalt, nicht als schwarzer Frame)"
            )
        elif clip.tl_in < cursor - 1e-6:
            issues.append(
                f"Clip '{clip.id}' überlappt mit dem vorherigen Clip "
                f"(beginnt bei {clip.tl_in:.2f}s, vorheriger endet bei {cursor:.2f}s)"
            )
        cursor = max(cursor, clip.tl_in + clip.duration)
    return issues


def _check_audio_clipping_risk(timeline: Timeline) -> list[str]:
    """Positiver Gain ist ein Clipping-Risiko — die Pipeline soll nur abschwächen, nie verstärken."""
    return [
        f"Audio-Clip '{clip.id}' hat positiven Gain ({clip.gain_db:+.1f} dB) — Clipping-Risiko"
        for clip in timeline.tracks.audio
        if clip.gain_db is not None and clip.gain_db > 0
    ]


def _check_overlay_readability(timeline: Timeline) -> list[str]:
    return [
        f"Overlay '{clip.id}' ist nur {clip.dur:.2f}s sichtbar "
        f"(< {MIN_OVERLAY_READABLE_S}s gilt als kaum lesbar)"
        for clip in timeline.tracks.overlay
        if clip.dur < MIN_OVERLAY_READABLE_S
    ]


def _check_clip_repetition(timeline: Timeline) -> list[str]:
    counts: dict[str, int] = {}
    for clip in timeline.tracks.video:
        counts[clip.asset] = counts.get(clip.asset, 0) + 1
    return [
        f"Asset '{asset_id}' wird {count}x in der Timeline verwendet (> {MAX_ASSET_REPEATS}) "
        f"— ggf. unbeabsichtigte Wiederholung"
        for asset_id, count in counts.items()
        if count > MAX_ASSET_REPEATS
    ]


def _check_against_brief(timeline: Timeline, brief: dict) -> list[str]:
    issues = []

    target = brief.get("target_duration_s")
    if target is not None and abs(timeline.duration - target) > DURATION_TOLERANCE_S:
        issues.append(
            f"Timeline-Dauer {timeline.duration:.1f}s weicht mehr als "
            f"{DURATION_TOLERANCE_S:.0f}s von der Brief-Ziellänge {target}s ab"
        )

    used_assets = {clip.asset for clip in timeline.tracks.video}

    for forbidden in brief.get("forbidden_shots", []):
        if forbidden in used_assets:
            issues.append(f"Verbotenes Asset '{forbidden}' kommt in der Timeline vor")

    for required in brief.get("must_shots", []):
        if required not in used_assets:
            issues.append(f"Muss-Shot '{required}' fehlt in der Timeline")

    return issues


def validate(timeline: Timeline, *, brief: dict | None = None) -> list[str]:
    """Liste gefundener Probleme; leer heisst "besteht die Pruefung".

    `brief` ist optional (z.B. aus `yaml.safe_load(export.brief_path.read_text())`) —
    ohne Brief werden nur die timeline-internen Regeln geprüft.
    """
    try:
        timeline.validate_semantics()
    except TimelineValidationError as exc:
        return [str(exc)]

    issues = [
        *_check_video_coverage(timeline),
        *_check_audio_clipping_risk(timeline),
        *_check_overlay_readability(timeline),
        *_check_clip_repetition(timeline),
    ]
    if brief is not None:
        issues.extend(_check_against_brief(timeline, brief))
    return issues
