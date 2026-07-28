"""FFmpeg-Graph-Bau, Proxy-/Final-Render.

**Einziger Ort im Package, der `ffmpeg` aufrufen darf** (CLAUDE.md: "Nackte
`ffmpeg`-Aufrufe sind verboten"). Baut den Filtergraph ausschliesslich aus
`timeline.json` (`frameforge.timeline.Timeline`), damit jeder Render reproduzierbar ist.

Umfang: Video-Spur als harte Schnitte **oder** Crossfade (`xfade`, wo ein Clip ein
`transition_in` vom Typ fade/dissolve trägt), Ken-Burns-Zoom (`zoompan`) auf Foto-Clips mit
einem `kenburns`-Effekt, Overlay-/Karten-Kompositing per `overlay`-Filter mit Zeitfenstern,
automatischer Color-Grade aus dem Preset (`grade_filter`) + optionale Projekt-LUT, Audio-Mix
mit Ducking (statische `volume`-Fenster) und optionaler EBU-R128-Loudnorm im Final.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from frameforge.index import load_assets
from frameforge.ingest import PHOTO_EXTENSIONS, proxy_path
from frameforge.project import Export, Project, UnsafePathError, resolve_media_path
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


# Grobe, bewusst dezente Übersetzung der Preset-`color_grade`-Stimmung in FFmpeg-Filter.
# Keine Ersatz für eine echte Farbkorrektur (dafür `--lut`), aber gibt jedem Stil-Preset
# automatisch einen passenden Grundton. Werte konservativ gehalten, damit nichts "kaputt" aussieht.
_CONTRAST_MAP = {"low": 0.95, "medium": 1.05, "medium_high": 1.12, "high": 1.20}
_MOOD_MAP: dict[str, dict] = {
    "cool_highlights_warm_lights": {"saturation": 1.05, "temperature": -0.06},
    "punchy": {"saturation": 1.22, "contrast_boost": 0.05},
    "natural": {"saturation": 1.02},
    "consistent_across_theme": {"saturation": 1.05},
    "raw": {"saturation": 0.9, "contrast_boost": -0.05},
    "vivid": {"saturation": 1.28, "contrast_boost": 0.03},
    "teal_orange": {"saturation": 1.20, "temperature": 0.03, "contrast_boost": 0.05},
    "clean_modern": {"saturation": 1.08},
    "soft_pastel": {"saturation": 0.9, "contrast_boost": -0.03},
    "warm_nostalgic": {"saturation": 0.95, "temperature": 0.08, "contrast_boost": -0.02},
}


# Übergangstypen, die als Crossfade (xfade) gerendert werden.
_CROSSFADE_TYPES = {"fade", "dissolve", "slow_dissolve", "crossfade"}


def _kenburns_expr(clip, dur: float, fps: float, res: tuple[int, int]) -> str | None:
    """`zoompan`-Ausdruck für Ken-Burns (langsamer Zoom) auf einem Foto-Clip.

    Aktiv nur, wenn der Clip einen Effekt vom Typ `kenburns` trägt (Timeline = Single Source of
    Truth). Zoomrichtung/-stärke aus `from`/`to` (falls gesetzt), sonst dezenter Default-Zoom.
    """
    kb = next((e for e in clip.effects if e.type == "kenburns"), None)
    if kb is None:
        return None
    frames = max(1, round(dur * fps))
    data = kb.model_dump()
    z_from = 1.0
    z_to = 1.10
    if isinstance(data.get("from"), (list, tuple)) and len(data["from"]) >= 3:
        z_from = float(data["from"][2])
    if isinstance(data.get("to"), (list, tuple)) and len(data["to"]) >= 3:
        z_to = float(data["to"][2])
    z_from = max(1.0, z_from)
    z_to = max(z_from + 0.001, z_to)
    step = (z_to - z_from) / frames
    w, h = res
    # Auf höherer Auflösung samplen (zoompan-Ruckel-Vermeidung), dann auf Zielgröße zurück.
    return (
        f"scale={w * 2}:{h * 2},"
        f"zoompan=z='min({z_from:.4f}+on*{step:.6f},{z_to:.4f})'"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={fps:g}"
    )


def _join_video_segments(clips, labels: list[str], filters: list[str]) -> str:
    """Verbindet die Video-Segmente: harte Schnitte (concat), Crossfades (xfade) wo im

    `transition_in` eines Clips gefordert. Ohne Crossfade bleibt es beim einzelnen concat
    (identisch zum bisherigen Verhalten), damit sich an bestehenden Timelines nichts ändert.
    """
    has_crossfade = any(
        c.transition_in and c.transition_in.type in _CROSSFADE_TYPES for c in clips[1:]
    )
    if not has_crossfade:
        cur = "vbase"
        joined = "".join(f"[{lbl}]" for lbl in labels)
        filters.append(f"{joined}concat=n={len(labels)}:v=1:a=0[{cur}]")
        return cur

    # Sequenzielle Kette: pro Folgeclip entweder xfade (Crossfade) oder concat (harter Schnitt).
    cur = labels[0]
    cur_dur = clips[0].duration
    for i in range(1, len(clips)):
        clip = clips[i]
        t = clip.transition_in
        if t and t.type in _CROSSFADE_TYPES:
            d = min(t.dur, cur_dur, clip.duration)
            offset = max(0.0, cur_dur - d)
            out = f"vx{i}"
            filters.append(
                f"[{cur}][{labels[i]}]xfade=transition=fade:duration={d:.3f}:offset={offset:.3f}[{out}]"
            )
            cur_dur = cur_dur + clip.duration - d
        else:
            out = f"vc{i}"
            filters.append(f"[{cur}][{labels[i]}]concat=n=2:v=1:a=0[{out}]")
            cur_dur = cur_dur + clip.duration
        cur = out
    return cur


def grade_filter(color_grade: dict | None) -> str | None:
    """Baut einen `eq`(+`colorbalance`)-Filterstring aus `color_grade` (`{mood, contrast}`).

    `None`, wenn kein `color_grade` gesetzt ist oder die Stimmung unbekannt ist (dann keine
    automatische Gradierung — der Look bleibt neutral).
    """
    if not color_grade:
        return None
    mood = color_grade.get("mood")
    params = _MOOD_MAP.get(mood, {}) if mood else {}
    contrast = _CONTRAST_MAP.get(color_grade.get("contrast", ""), 1.0)
    contrast *= 1.0 + params.get("contrast_boost", 0.0)
    saturation = params.get("saturation", 1.0)
    if not params and contrast == 1.0:
        return None

    chain = f"eq=contrast={contrast:.3f}:saturation={saturation:.3f}"
    temp = params.get("temperature")
    if temp:
        # warm = mehr Rot/weniger Blau in den Schatten (negatives temp => kühler in Highlights)
        chain += f",colorbalance=rs={-temp:.3f}:bs={temp:.3f}"
    return chain


def build_filtergraph(
    timeline: Timeline,
    *,
    resolve_asset: Callable[[str], Path],
    export_root: Path,
    project_root: Path,
    lut_path: Path | None = None,
    loudness_normalize: bool = False,
    resolution: tuple[int, int] | None = None,
    color_grade: dict | None = None,
) -> FilterGraph:
    """Baut Input-Liste und `filter_complex`-String aus einer validierten Timeline.

    `resolve_asset(asset_id)` liefert den Medienpfad (Proxy oder Original, je nach Aufrufer).
    Overlay-PNGs/Karten-Clips werden relativ zu `export_root` aufgeloest (`overlays/…`,
    `map/…`), Musik relativ zu `project_root` (`music/…`) — passend zur Projekt-Struktur
    aus Plan §1.

    `resolution`: Ziel-Auflösung `(w, h)` — überschreibt `timeline.resolution` (z.B. ein
    1080p-Deliverable aus einer 4K-Timeline). `lut_path`: optionale 3D-LUT (`.cube`) fuer
    Farbkorrektur. `loudness_normalize`: EBU-R128-Loudness-Normalisierung (`loudnorm`,
    Ziel -16 LUFS/-1.5 dBTP) auf den gemischten Audio-Output.
    """
    target_res = resolution or timeline.resolution
    graph = FilterGraph()
    filters: list[str] = []

    def add_input(args: list[str]) -> int:
        graph.input_args.append(args)
        return len(graph.input_args) - 1

    # -- Video: pro Clip als Segment (skaliert, ggf. Ken-Burns), dann verbinden --------
    clips = timeline.tracks.video
    if not clips:
        raise RenderError("Timeline hat keine Video-Clips — nichts zu rendern")

    fps = timeline.fps
    video_labels = []
    for i, clip in enumerate(clips):
        source = resolve_asset(clip.asset)
        label = f"v{i}"
        chain: list[str] = []
        if source.suffix.lower() in PHOTO_EXTENSIONS:
            idx = add_input(["-loop", "1", "-framerate", str(fps), "-i", str(source)])
            chain.append(f"trim=duration={clip.duration:.3f}")
            chain.append("setpts=PTS-STARTPTS")
            chain.append(_scale_pad(*target_res))
            kb = _kenburns_expr(clip, clip.duration, fps, target_res)
            if kb:
                chain.append(kb)
        else:
            idx = add_input(["-i", str(source)])
            chain.append(f"trim=start={clip.src_in}:end={clip.src_out}")
            chain.append(f"setpts=(PTS-STARTPTS)/{clip.speed}")
            chain.append(_scale_pad(*target_res))
        # Konstante fps sichern, damit concat/xfade sauber zusammenpassen.
        chain.append(f"fps={fps:g}")
        filters.append(f"[{idx}:v]{','.join(chain)}[{label}]")
        video_labels.append(label)

    cur_video = _join_video_segments(clips, video_labels, filters)

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

    # Automatischer Grundton aus dem Preset (dezent) …
    grade = grade_filter(color_grade)
    if grade is not None:
        next_video = f"{cur_video}_grade"
        filters.append(f"[{cur_video}]{grade}[{next_video}]")
        cur_video = next_video

    # … dann optional eine echte Projekt-LUT obendrauf.
    if lut_path is not None:
        graded = f"{cur_video}_lut"
        filters.append(f"[{cur_video}]lut3d=file='{lut_path}'[{graded}]")
        cur_video = graded

    graph.video_label = cur_video

    # -- Audio: pro Clip trimmen/verzoegern/Pegel, Musik-Ducking, dann amix ----------
    audio_labels: list[str] = []
    music_labels: list[str] = []  # alle src-basierten (Musik-)Spuren, alle werden geduckt
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

        if audio.src is not None:
            music_labels.append(label)
        if audio.asset is not None and audio.duck_music_db is not None:
            duck_windows.append((audio.tl_in, audio.tl_in + dur, audio.duck_music_db))

    # Jede Musik-Spur bekommt die gesamte Duck-Kette (nicht nur die erste — Audit K5).
    for m, music_label in enumerate(music_labels):
        current = music_label
        for w, (start, end, duck_db) in enumerate(duck_windows):
            duck_gain = 10 ** (duck_db / 20)
            ducked = f"m{m}_duck{w}"
            filters.append(
                f"[{current}]volume=volume={duck_gain}:enable='between(t,{start},{end})'[{ducked}]"
            )
            current = ducked
        if current != music_label:
            audio_labels[audio_labels.index(music_label)] = current

    if audio_labels:
        mix_inputs = "".join(f"[{lbl}]" for lbl in audio_labels)
        # normalize=0: amix skaliert sonst automatisch mit 1/n und macht die explizit
        # gesetzten gain_db-/Ducking-Werte bedeutungslos (halbierter Pegel bei 2 Spuren).
        # Die absoluten Pegel steuern wir ueber die volume-Gains + loudnorm (Final).
        filters.append(
            f"{mix_inputs}amix=inputs={len(audio_labels)}:normalize=0:"
            f"duration=longest:dropout_transition=0[aout]"
        )
        graph.audio_label = "aout"
        if loudness_normalize:
            filters.append(f"[{graph.audio_label}]loudnorm=I=-16:TP=-1.5:LRA=11[aout_norm]")
            graph.audio_label = "aout_norm"

    graph.filter_complex = ";".join(filters)
    return graph


def _run_ffmpeg(
    graph: FilterGraph,
    timeline: Timeline,
    out_path: Path,
    *,
    crf: int | None = None,
    preset: str | None = None,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    for args in graph.input_args:
        cmd.extend(args)
    cmd.extend(["-filter_complex", graph.filter_complex, "-map", f"[{graph.video_label}]"])
    if graph.audio_label:
        cmd.extend(["-map", f"[{graph.audio_label}]"])
    cmd.extend(["-r", str(timeline.fps), "-c:v", "libx264", "-pix_fmt", "yuv420p"])
    if crf is not None:
        cmd.extend(["-crf", str(crf)])
    if preset is not None:
        cmd.extend(["-preset", preset])
    cmd.extend(["-c:a", "aac", "-loglevel", "error", str(out_path)])
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


def render_proxy(
    project: Project, export: Export, timeline: Timeline, *, color_grade: dict | None = None
) -> Path:
    """1080p-Proxy-Render fuer `ff-preview`, mappt auf die Proxy-Assets im Cache.

    `color_grade` (aus dem Brief-Preset) wird auch im Preview angewandt, damit der Preview
    schon wie der Final-Look aussieht.
    """
    proxies_dir = project.cache_dir / "proxies"
    assets_by_id = {a["id"]: a for a in load_assets(project)}

    def resolve(asset_id: str) -> Path:
        asset = assets_by_id.get(asset_id)
        if asset is None:
            raise RenderError(f"Asset '{asset_id}' nicht in assets.json gefunden")
        try:
            original = resolve_media_path(project.config.media_root, asset["path"])
        except UnsafePathError as exc:
            raise RenderError(str(exc)) from exc
        proxy = proxy_path(original, proxies_dir, media_root=project.config.media_root)
        if not proxy.exists():
            raise RenderError(f"Kein Proxy fuer Asset '{asset_id}' unter {proxy}")
        return proxy

    graph = build_filtergraph(
        timeline,
        resolve_asset=resolve,
        export_root=export.root,
        project_root=project.root,
        color_grade=color_grade,
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
    project: Project,
    export: Export,
    timeline: Timeline,
    *,
    lut_path: Path | None = None,
    resolution: tuple[int, int] | None = None,
    crf: int = 18,
    preset: str = "medium",
    color_grade: dict | None = None,
) -> Path:
    """Final-Render: mappt auf die Original-Assets (kein Proxy-Downscale), EBU-R128-

    Loudness-Normalisierung, optionale Farbkorrektur-LUT, versionierte Ausgabedatei
    (`<export>_v<N>.mp4` statt Überschreiben).

    `resolution` überschreibt die Timeline-Auflösung (z.B. ein 1080p-Deliverable aus einer
    4K-Timeline). `crf`/`preset` steuern Qualität vs. Dateigröße/Encoding-Zeit (kleineres CRF =
    bessere Qualität; Default 18 = visuell nahezu verlustfrei).
    """
    assets_by_id = {a["id"]: a for a in load_assets(project)}

    def resolve(asset_id: str) -> Path:
        asset = assets_by_id.get(asset_id)
        if asset is None:
            raise RenderError(f"Asset '{asset_id}' nicht in assets.json gefunden")
        try:
            original = resolve_media_path(project.config.media_root, asset["path"])
        except UnsafePathError as exc:
            raise RenderError(str(exc)) from exc
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
        resolution=resolution,
        color_grade=color_grade,
    )
    out_path = _next_version_path(export.final_dir, export.name, ".mp4")
    _run_ffmpeg(graph, timeline, out_path, crf=crf, preset=preset)
    return out_path
