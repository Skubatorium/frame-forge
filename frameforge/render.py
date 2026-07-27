"""FFmpeg-Graph-Bau, Proxy-/Final-Render.

**Einziger Ort im Package, der `ffmpeg` aufrufen darf** (CLAUDE.md: "Nackte
`ffmpeg`-Aufrufe sind verboten"). Baut den Filtergraph ausschliesslich aus
`timeline.json` (`frameforge.timeline.Timeline`), damit jeder Render reproduzierbar ist.

M1-Scope (siehe `docs/plans/PROGRESS.md`): Video-Spur als harte Schnitte (kein Crossfade,
kein Ken-Burns-Zoompan — `transition_in`/`effects` werden aus der Timeline gelesen, aber noch
nicht gerendert, das ist M2-Scope), Overlay-/Karten-Kompositing per `overlay`-Filter mit
Zeitfenstern, Audio-Mix mit einfachem Ducking (statische `volume`-Fenster, kein echtes
Sidechain-Compressing).
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from frameforge.index import load_assets
from frameforge.ingest import PHOTO_EXTENSIONS, proxy_path
from frameforge.project import Export, Project
from frameforge.timeline import Timeline


class RenderError(RuntimeError):
    """`ffmpeg` ist fehlgeschlagen."""


@dataclass
class FilterGraph:
    """Ergebnis von `build_filtergraph` — alles, was `ffmpeg -filter_complex` braucht."""

    input_args: list[list[str]] = field(default_factory=list)
    filter_complex: str = ""
    video_label: str = ""
    audio_label: str | None = None


def _scale_pad(width: int, height: int) -> str:
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    )


def build_filtergraph(
    timeline: Timeline,
    *,
    resolve_asset: Callable[[str], Path],
    export_root: Path,
    project_root: Path,
    lut_path: Path | None = None,
    loudness_normalize: bool = False,
) -> FilterGraph:
    """Baut Input-Liste und `filter_complex`-String aus einer validierten Timeline.

    `resolve_asset(asset_id)` liefert den Medienpfad (Proxy oder Original, je nach Aufrufer).
    Overlay-PNGs/Karten-Clips werden relativ zu `export_root` aufgeloest (`overlays/…`,
    `map/…`), Musik relativ zu `project_root` (`music/…`) — passend zur Projekt-Struktur
    aus Plan §1.

    `lut_path`: optionale 3D-LUT (`.cube`) fuer Farbkorrektur — generischer Hook, keine
    Grade ist hier fest eingebaut, das liefert das Projekt (siehe Plan §11: "Farbmanagement
    bei HLG/D-Log-Material"). `loudness_normalize`: EBU-R128-Loudness-Normalisierung
    (`loudnorm`, Ziel -16 LUFS/-1.5 dBTP — Streaming-Standardwerte) auf den gemischten
    Audio-Output.
    """
    graph = FilterGraph()
    filters: list[str] = []

    def add_input(args: list[str]) -> int:
        graph.input_args.append(args)
        return len(graph.input_args) - 1

    # -- Video: pro Clip trimmen/skalieren, dann hart aneinanderschneiden -----------
    video_labels = []
    for i, clip in enumerate(timeline.tracks.video):
        source = resolve_asset(clip.asset)
        label = f"v{i}"
        if source.suffix.lower() in PHOTO_EXTENSIONS:
            idx = add_input(["-loop", "1", "-framerate", str(timeline.fps), "-i", str(source)])
            filters.append(
                f"[{idx}:v]trim=duration={clip.duration:.3f},setpts=PTS-STARTPTS,"
                f"{_scale_pad(*timeline.resolution)}[{label}]"
            )
        else:
            idx = add_input(["-i", str(source)])
            filters.append(
                f"[{idx}:v]trim=start={clip.src_in}:end={clip.src_out},"
                f"setpts=(PTS-STARTPTS)/{clip.speed},{_scale_pad(*timeline.resolution)}[{label}]"
            )
        video_labels.append(label)

    if not video_labels:
        raise RenderError("Timeline hat keine Video-Clips — nichts zu rendern")

    cur_video = "vbase"
    concat_inputs = "".join(f"[{lbl}]" for lbl in video_labels)
    filters.append(f"{concat_inputs}concat=n={len(video_labels)}:v=1:a=0[{cur_video}]")

    # -- Overlay: PNGs mit Alpha, Zeitfenster ueber `enable` -------------------------
    for j, overlay in enumerate(timeline.tracks.overlay):
        idx = add_input(
            ["-loop", "1", "-framerate", str(timeline.fps), "-i", str(export_root / overlay.png)]
        )
        ov_label = f"ov{j}"
        next_video = f"vov{j}"
        filters.append(f"[{idx}:v]format=rgba[{ov_label}]")
        filters.append(
            f"[{cur_video}][{ov_label}]overlay=x=0:y=0:shortest=1:"
            f"enable='between(t,{overlay.tl_in},{overlay.tl_in + overlay.dur})'[{next_video}]"
        )
        cur_video = next_video

    # -- Karten-Clips: eigene kleine Videos (mit Alpha), unten rechts eingeblendet ---
    for k, map_clip in enumerate(timeline.tracks.map):
        idx = add_input(["-i", str(export_root / map_clip.clip)])
        shifted = f"map{k}shift"
        next_video = f"vmap{k}"
        filters.append(f"[{idx}:v]setpts=PTS+{map_clip.tl_in}/TB[{shifted}]")
        filters.append(
            f"[{cur_video}][{shifted}]overlay=x=W-w-20:y=H-h-20:shortest=1:"
            f"enable='between(t,{map_clip.tl_in},{map_clip.tl_in + map_clip.dur})'[{next_video}]"
        )
        cur_video = next_video

    if lut_path is not None:
        graded = f"{cur_video}_graded"
        filters.append(f"[{cur_video}]lut3d=file='{lut_path}'[{graded}]")
        cur_video = graded

    graph.video_label = cur_video

    # -- Audio: pro Clip trimmen/verzoegern/Pegel, Musik-Ducking, dann amix ----------
    audio_labels: list[str] = []
    music_label: str | None = None
    duck_windows: list[tuple[float, float, float]] = []

    for k, audio in enumerate(timeline.tracks.audio):
        if audio.src is not None:
            source = project_root / audio.src
        else:
            source = resolve_asset(audio.asset)
        idx = add_input(["-i", str(source)])

        dur = audio.dur if audio.dur is not None else max(timeline.duration - audio.tl_in, 0.0)
        gain = 10 ** ((audio.gain_db or 0.0) / 20)
        delay_ms = round(audio.tl_in * 1000)
        label = f"a{k}"
        filters.append(
            f"[{idx}:a]atrim=start=0:end={dur},asetpts=PTS-STARTPTS,"
            f"adelay={delay_ms}|{delay_ms},volume={gain}[{label}]"
        )
        audio_labels.append(label)

        if audio.src is not None and music_label is None:
            music_label = label
        if audio.asset is not None and audio.duck_music_db is not None:
            duck_windows.append((audio.tl_in, audio.tl_in + dur, audio.duck_music_db))

    if music_label is not None:
        for w, (start, end, duck_db) in enumerate(duck_windows):
            duck_gain = 10 ** (duck_db / 20)
            ducked = f"{music_label}_duck{w}"
            filters.append(
                f"[{music_label}]volume=volume={duck_gain}:enable='between(t,{start},{end})'"
                f"[{ducked}]"
            )
            audio_labels[audio_labels.index(music_label)] = ducked
            music_label = ducked

    if audio_labels:
        mix_inputs = "".join(f"[{lbl}]" for lbl in audio_labels)
        filters.append(
            f"{mix_inputs}amix=inputs={len(audio_labels)}:duration=longest:dropout_transition=0[aout]"
        )
        graph.audio_label = "aout"
        if loudness_normalize:
            filters.append(f"[{graph.audio_label}]loudnorm=I=-16:TP=-1.5:LRA=11[aout_norm]")
            graph.audio_label = "aout_norm"

    graph.filter_complex = ";".join(filters)
    return graph


def _run_ffmpeg(graph: FilterGraph, timeline: Timeline, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    for args in graph.input_args:
        cmd.extend(args)
    cmd.extend(["-filter_complex", graph.filter_complex, "-map", f"[{graph.video_label}]"])
    if graph.audio_label:
        cmd.extend(["-map", f"[{graph.audio_label}]"])
    cmd.extend(
        [
            "-r",
            str(timeline.fps),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-loglevel",
            "error",
            str(out_path),
        ]
    )
    # Grosszuegiges, aber endliches Timeout als Sicherheitsnetz: ein Filtergraph-Fehler
    # (z.B. ein unbegrenzter `-loop 1`-Input ohne `shortest=1` an einem `overlay`) darf den
    # Prozess nicht auf unbestimmte Zeit haengen lassen.
    timeout_s = max(120.0, timeline.duration * 30)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=timeout_s
        )
    except subprocess.TimeoutExpired as exc:
        raise RenderError(
            f"ffmpeg hat nach {timeout_s:.0f}s nicht terminiert (moeglicher Filtergraph-Fehler, "
            f"z.B. unbegrenzter Input ohne 'shortest=1' an einem overlay-Filter)"
        ) from exc
    if result.returncode != 0:
        raise RenderError(f"ffmpeg fehlgeschlagen: {result.stderr.strip()}")


def render_proxy(project: Project, export: Export, timeline: Timeline) -> Path:
    """1080p-Proxy-Render fuer `ff-preview`, mappt auf die Proxy-Assets im Cache."""
    proxies_dir = project.cache_dir / "proxies"
    assets_by_id = {a["id"]: a for a in load_assets(project)}

    def resolve(asset_id: str) -> Path:
        asset = assets_by_id.get(asset_id)
        if asset is None:
            raise RenderError(f"Asset '{asset_id}' nicht in assets.json gefunden")
        original = project.config.media_root / asset["path"]
        proxy = proxy_path(original, proxies_dir, media_root=project.config.media_root)
        if not proxy.exists():
            raise RenderError(f"Kein Proxy fuer Asset '{asset_id}' unter {proxy}")
        return proxy

    graph = build_filtergraph(
        timeline, resolve_asset=resolve, export_root=export.root, project_root=project.root
    )
    out_path = export.preview_dir / f"{export.name}_preview.mp4"
    _run_ffmpeg(graph, timeline, out_path)
    return out_path


def _next_version_path(directory: Path, stem: str, ext: str) -> Path:
    """Naechster freier `<stem>_v<N><ext>`-Pfad — Render-Versionierung statt Overschreiben."""
    directory.mkdir(parents=True, exist_ok=True)
    existing = sorted(directory.glob(f"{stem}_v*{ext}"))
    max_version = 0
    for path in existing:
        suffix = path.stem.rsplit("_v", 1)[-1]
        if suffix.isdigit():
            max_version = max(max_version, int(suffix))
    return directory / f"{stem}_v{max_version + 1}{ext}"


def render_final(
    project: Project, export: Export, timeline: Timeline, *, lut_path: Path | None = None
) -> Path:
    """4K-Final-Render: mappt auf die Original-Assets (kein Proxy-Downscale), EBU-R128-

    Loudness-Normalisierung, optionale Farbkorrektur-LUT, versionierte Ausgabedatei
    (`<export>_v<N>.mp4` statt Überschreiben).
    """
    assets_by_id = {a["id"]: a for a in load_assets(project)}

    def resolve(asset_id: str) -> Path:
        asset = assets_by_id.get(asset_id)
        if asset is None:
            raise RenderError(f"Asset '{asset_id}' nicht in assets.json gefunden")
        original = project.config.media_root / asset["path"]
        if not original.exists():
            raise RenderError(f"Original-Asset '{asset_id}' nicht gefunden unter {original}")
        return original

    graph = build_filtergraph(
        timeline,
        resolve_asset=resolve,
        export_root=export.root,
        project_root=project.root,
        lut_path=lut_path,
        loudness_normalize=True,
    )
    out_path = _next_version_path(export.final_dir, export.name, ".mp4")
    _run_ffmpeg(graph, timeline, out_path)
    return out_path
