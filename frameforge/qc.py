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

from frameforge.render import _CROSSFADE_TYPES
from frameforge.timeline import Timeline, TimelineValidationError

MIN_OVERLAY_READABLE_S = 1.2
MAX_ASSET_REPEATS = 2
DURATION_TOLERANCE_S = 2.0
# Toleranz beim Abgleich Crossfade-Dauer <-> tl_in-Überlappung (Rundung/fps-Raster).
_XFADE_OVERLAP_TOLERANCE_S = 0.05


def timeline_fingerprint(path: Path) -> str:
    """SHA256 der `timeline.json`-Bytes — bindet eine Freigabe an den exakten Timeline-Stand.

    Aendert sich die Timeline nach der Freigabe, weicht der Fingerprint ab und der
    Final-Render kann die Freigabe als veraltet erkennen (Audit-Findings P2/P3).
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_video_coverage(timeline: Timeline) -> list[str]:
    """Lücken/Überlappungen in der Video-Spur — abgestimmt auf das Render-Timing.

    Der Renderer (`render.build_filtergraph`) sequenziert Video-Clips in Reihenfolge und nutzt
    deren Dauern; Audio (`adelay=tl_in`), Overlays und Karte werden dagegen an ihrer **absoluten
    `tl_in`** platziert. Damit beide Modelle übereinstimmen, muss die Video-Spur lückenlos sein:

    - **Harter Schnitt:** Clip startet genau am Ende des vorigen (`tl_in == prev_end`).
    - **Crossfade** (`transition_in` vom Typ fade/dissolve/…): der Clip *überlappt* den vorigen
      um die Crossfade-Dauer (`tl_in == prev_end - dur`), weil `xfade` beide Clips um diese Zeit
      ineinander blendet und die Gesamtlänge entsprechend verkürzt. Fehlt diese Überlappung im
      `tl_in`, laufen Bild und Ton/Overlays um die Crossfade-Dauer auseinander.

    Lücke, fehlende/zu große Crossfade-Überlappung und Überlappung ohne Crossfade sind je ein
    Fehler, den QC vor dem Render fängt.
    """
    issues = []
    clips = sorted(timeline.tracks.video, key=lambda c: c.tl_in)
    prev_end = 0.0
    for clip in clips:
        xfade = (
            clip.transition_in.dur
            if clip.transition_in and clip.transition_in.type in _CROSSFADE_TYPES
            else 0.0
        )
        overlap = prev_end - clip.tl_in  # > 0: Clip beginnt vor dem Ende des vorigen
        if clip.tl_in > prev_end + 1e-6:
            issues.append(
                f"Lücke in der Video-Spur zwischen {prev_end:.2f}s und {clip.tl_in:.2f}s "
                f"(erscheint im Render als fehlender Inhalt, nicht als schwarzer Frame)"
            )
        elif xfade > 0:
            if overlap < xfade - _XFADE_OVERLAP_TOLERANCE_S:
                issues.append(
                    f"Clip '{clip.id}' hat einen Crossfade ({xfade:.2f}s), sein tl_in überlappt "
                    f"den vorigen aber nur um {max(overlap, 0.0):.2f}s — Bild läuft um die Differenz "
                    f"gegen Ton/Overlays (tl_in muss um die Crossfade-Dauer überlappen)"
                )
            elif overlap > xfade + _XFADE_OVERLAP_TOLERANCE_S:
                issues.append(
                    f"Clip '{clip.id}' überlappt den vorigen um {overlap:.2f}s, mehr als die "
                    f"Crossfade-Dauer ({xfade:.2f}s)"
                )
        elif overlap > 1e-6:
            issues.append(
                f"Clip '{clip.id}' überlappt mit dem vorherigen Clip "
                f"(beginnt bei {clip.tl_in:.2f}s, vorheriger endet bei {prev_end:.2f}s) — "
                f"ohne Crossfade ist das ein Timeline-Fehler"
            )
        prev_end = max(prev_end, clip.tl_in + clip.duration)
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


def _check_known_assets(timeline: Timeline, known_asset_ids: set[str]) -> list[str]:
    """Jede in der Timeline referenzierte Asset-ID muss in `assets.json` existieren.

    Sonst schlaegt der Render erst spaet mit einem kryptischen Fehler fehl (Audit K6) —
    besser hier fruehzeitig und klar melden.
    """
    referenced = {c.asset for c in timeline.tracks.video}
    referenced |= {c.asset for c in timeline.tracks.audio if c.asset is not None}
    return [
        f"Asset '{asset_id}' aus der Timeline fehlt in assets.json"
        for asset_id in sorted(referenced - known_asset_ids)
    ]


def validate(
    timeline: Timeline,
    *,
    brief: dict | None = None,
    known_asset_ids: set[str] | None = None,
) -> list[str]:
    """Liste gefundener Probleme; leer heisst "besteht die Pruefung".

    `brief` ist optional (z.B. aus `yaml.safe_load(export.brief_path.read_text())`) —
    ohne Brief werden nur die timeline-internen Regeln geprüft. `known_asset_ids` (z.B. die
    IDs aus `assets.json`) aktiviert die Pruefung, dass alle referenzierten Assets existieren.
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
    if known_asset_ids is not None:
        issues.extend(_check_known_assets(timeline, known_asset_ids))
    if brief is not None:
        issues.extend(_check_against_brief(timeline, brief))
    return issues
