"""FCPXML / OTIO Export fuer DaVinci Resolve.

Baut aus `frameforge.timeline.Timeline` — demselben Schema, das `frameforge.render` liest —
eine `opentimelineio`-Timeline und schreibt sie als natives `.otio` (JSON) oder FCPXML
(`otio-fcpx-xml-adapter`, Adapter-Name `fcpx_xml` — der FCPXML-Adapter ist mit OTIO 0.17+
nicht mehr im Core enthalten, siehe `pyproject.toml`). Render und NLE-Export lesen dasselbe
`Timeline`-Objekt, damit sie nie auseinanderlaufen (Plan §4).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import opentimelineio as otio

from frameforge.timeline import Timeline


def _rt(seconds: float, fps: float) -> otio.opentime.RationalTime:
    return otio.opentime.RationalTime(round(seconds * fps), fps)


def _append_gap_if_needed(track: otio.schema.Track, cursor: float, start: float, fps: float) -> None:
    if start > cursor + 1e-6:
        track.append(
            otio.schema.Gap(
                source_range=otio.opentime.TimeRange(
                    start_time=_rt(0, fps), duration=_rt(start - cursor, fps)
                )
            )
        )


def _pack_lanes(intervals: list[tuple[float, float]]) -> list[int]:
    """Greedy Interval-Packing: Lane-Index pro Eintrag, sodass sich keine zwei Eintraege

    derselben Lane ueberlappen. Ein `otio.schema.Track` ist wie unsere Video-Spur streng
    sequenziell (Items duerfen sich nicht ueberlappen) — Audio darf das aber durchaus
    (Musikbett + gleichzeitiger O-Ton). Deshalb: ueberlappende Audio-Clips landen auf
    getrennten parallelen Tracks (Lanes) statt fehlerhaft in einem einzigen Track verschachtelt
    zu werden (siehe PROGRESS.md M4.2 — das hat den `fcpx_xml`-Adapter zum Absturz gebracht).
    """
    lane_ends: list[float] = []
    order = sorted(range(len(intervals)), key=lambda i: intervals[i][0])
    result = [0] * len(intervals)
    for i in order:
        start, end = intervals[i]
        for lane_idx, lane_end in enumerate(lane_ends):
            if start >= lane_end - 1e-6:
                lane_ends[lane_idx] = end
                result[i] = lane_idx
                break
        else:
            lane_ends.append(end)
            result[i] = len(lane_ends) - 1
    return result


def build_otio_timeline(
    timeline: Timeline,
    *,
    resolve_asset: Callable[[str], Path],
    project_root: Path,
) -> otio.schema.Timeline:
    """Baut eine `opentimelineio`-Timeline — eine Video-Spur, plus so viele parallele

    Audio-Spuren wie noetig, um Überlappungen (Musikbett + gleichzeitiger O-Ton) korrekt
    als getrennte Lanes statt fälschlich in einer Spur abzubilden (`_pack_lanes`).

    `resolve_asset(asset_id)` liefert den Medienpfad fuer Video-Clips und `asset`-referenzierte
    Audio-Clips (analog zu `render.build_filtergraph`); `src`-referenzierte Audio-Clips
    (Musik) werden relativ zu `project_root` aufgeloest. Lücken in `tl_in` werden als `Gap`
    abgebildet statt stillschweigend ignoriert.
    """
    fps = timeline.fps
    otio_timeline = otio.schema.Timeline(name=timeline.export)

    video_track = otio.schema.Track(name="video", kind=otio.schema.TrackKind.Video)
    cursor = 0.0
    for clip in timeline.tracks.video:
        _append_gap_if_needed(video_track, cursor, clip.tl_in, fps)
        source = resolve_asset(clip.asset)
        clip_range = otio.opentime.TimeRange(
            start_time=_rt(clip.src_in, fps),
            duration=_rt((clip.src_out - clip.src_in) / clip.speed, fps),
        )
        video_track.append(
            otio.schema.Clip(
                name=clip.id,
                # `available_range` = die verwendete Range: wir kennen die volle Asset-Dauer
                # hier nicht (nur `resolve_asset` -> Pfad, keine Metadaten) — die Adapter
                # brauchen aber irgendeine `available_range`, sonst schlaegt z.B. `fcpx_xml`
                # fehl. Konservative Annahme: mindestens das Genutzte ist verfuegbar.
                media_reference=otio.schema.ExternalReference(
                    target_url=source.as_uri(), available_range=clip_range
                ),
                source_range=clip_range,
            )
        )
        cursor = clip.tl_in + clip.duration
    otio_timeline.tracks.append(video_track)

    if timeline.tracks.audio:
        durations = [
            a.dur if a.dur is not None else max(timeline.duration - a.tl_in, 0.0)
            for a in timeline.tracks.audio
        ]
        intervals = [(a.tl_in, a.tl_in + d) for a, d in zip(timeline.tracks.audio, durations, strict=True)]
        lanes = _pack_lanes(intervals)
        num_lanes = max(lanes) + 1
        audio_tracks = [
            otio.schema.Track(name=f"audio{i + 1}", kind=otio.schema.TrackKind.Audio)
            for i in range(num_lanes)
        ]
        lane_cursors = [0.0] * num_lanes

        order = sorted(range(len(timeline.tracks.audio)), key=lambda i: timeline.tracks.audio[i].tl_in)
        for i in order:
            audio = timeline.tracks.audio[i]
            dur = durations[i]
            lane = lanes[i]
            track = audio_tracks[lane]
            _append_gap_if_needed(track, lane_cursors[lane], audio.tl_in, fps)
            source = project_root / audio.src if audio.src is not None else resolve_asset(audio.asset)
            audio_range = otio.opentime.TimeRange(start_time=_rt(0, fps), duration=_rt(dur, fps))
            track.append(
                otio.schema.Clip(
                    name=audio.id,
                    media_reference=otio.schema.ExternalReference(
                        target_url=source.as_uri(), available_range=audio_range
                    ),
                    source_range=audio_range,
                )
            )
            lane_cursors[lane] = audio.tl_in + dur

        for track in audio_tracks:
            otio_timeline.tracks.append(track)

    return otio_timeline


def export_otio(
    timeline: Timeline, out_path: Path, *, resolve_asset: Callable[[str], Path], project_root: Path
) -> None:
    """Schreibt die Timeline als natives `.otio` (JSON)."""
    otio_timeline = build_otio_timeline(timeline, resolve_asset=resolve_asset, project_root=project_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    otio.adapters.write_to_file(otio_timeline, str(out_path))


def export_fcpxml(
    timeline: Timeline, out_path: Path, *, resolve_asset: Callable[[str], Path], project_root: Path
) -> None:
    """Schreibt die Timeline als FCPXML fuer DaVinci Resolve/Final Cut Pro."""
    otio_timeline = build_otio_timeline(timeline, resolve_asset=resolve_asset, project_root=project_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    otio.adapters.write_to_file(otio_timeline, str(out_path), adapter_name="fcpx_xml")
