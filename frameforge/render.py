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

from frameforge.imageio import HEIF_EXTENSIONS
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
    # Konvention (siehe cool_highlights_warm_lights): negatives temperature = wärmer.
    "teal_orange": {"saturation": 1.20, "temperature": -0.03, "contrast_boost": 0.05},
    "clean_modern": {"saturation": 1.08},
    "soft_pastel": {"saturation": 0.9, "contrast_boost": -0.03},
    "warm_nostalgic": {"saturation": 0.95, "temperature": -0.08, "contrast_boost": -0.02},
}


# Übergangstypen, die als Crossfade (xfade) gerendert werden.
_CROSSFADE_TYPES = {"fade", "dissolve", "slow_dissolve", "crossfade"}


def _kenburns_expr(clip, dur: float, fps: float, res: tuple[int, int]) -> str | None:
    """`zoompan`-Ausdruck für Ken-Burns (langsamer Zoom) auf einem Foto-Clip.

    Aktiv nur, wenn der Clip einen Effekt vom Typ `kenburns` trägt (Timeline = Single Source of
    Truth). Zoomrichtung/-stärke aus `from`/`to` (falls gesetzt), sonst dezenter Default-Zoom.

    **`d=1` ist Pflicht, nicht Geschmackssache.** `zoompan` hält *jeden Eingabeframe* `d`
    Ausgabeframes lang. Der Foto-Zweig erzeugt über `trim=duration=…` bereits `dur*fps` Frames;
    mit `d={frames}` wurde daraus `frames²` — ein 1-s-Foto bei 25 fps ergab 25 s Video statt 1 s
    (Audit 2026-08-01). `d=1` liefert genau einen Ausgabeframe je Eingabeframe, der Zoom läuft
    über `on` (fortlaufender Ausgabeframe-Index) trotzdem über die volle Clipdauer.
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
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}:fps={fps:g}"
    )


BLACK_TRANSITION = "black"


def black_transition_extra_s(clips) -> float:
    """Zusatzdauer, die Schwarzblenden der Timeline hinzufuegen (`dur + hold` je Blende).

    Anders als `xfade` (verkuerzt) **verlaengert** eine Schwarzblende den Film. `qc.validate`
    und `timeline.duration` muessen das kennen, sonst laufen Audio und Overlays weg.
    """
    return sum(
        c.transition_in.dur + c.transition_in.hold
        for c in clips[1:]
        if c.transition_in and c.transition_in.type == BLACK_TRANSITION
    )


def _join_video_segments(clips, labels: list[str], filters: list[str]) -> str:
    """Verbindet die Video-Segmente: harte Schnitte (concat), Crossfades (xfade) wo im

    `transition_in` eines Clips gefordert. Ohne Crossfade bleibt es beim einzelnen concat
    (identisch zum bisherigen Verhalten), damit sich an bestehenden Timelines nichts ändert.

    Timing-Invariante: `xfade` verkürzt die Gesamtlänge um die Crossfade-Dauer. Audio/Overlays
    laufen aber über absolute `tl_in`. Damit Bild und Ton zusammenbleiben, muss die Timeline
    Crossfade-Clips mit überlappendem `tl_in` (Überlappung = Crossfade-Dauer) schreiben — genau
    das prüft `qc._check_video_coverage` vor dem Render.
    """
    special = {*_CROSSFADE_TYPES, BLACK_TRANSITION}
    has_crossfade = any(c.transition_in and c.transition_in.type in special for c in clips[1:])
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
        elif t and t.type == BLACK_TRANSITION:
            # Ausblenden des bisherigen Materials, optionale Standzeit auf Schwarz, Aufblenden
            # des naechsten. Umgesetzt mit `fade` statt `xfade`, weil hier nichts ineinander
            # blendet — und mit `tpad`, um die Standzeit als echte schwarze Frames anzuhaengen.
            d = min(t.dur, cur_dur, clip.duration)
            fade_out_start = max(0.0, cur_dur - d)
            faded_out, faded_in = f"vbo{i}", f"vbi{i}"
            pad = (
                f",tpad=stop_duration={t.hold:.3f}:stop_mode=add:color=black"
                if t.hold > 0
                else ""
            )
            filters.append(
                f"[{cur}]fade=t=out:st={fade_out_start:.3f}:d={d:.3f}:color=black"
                f"{pad}[{faded_out}]"
            )
            filters.append(f"[{labels[i]}]fade=t=in:st=0:d={d:.3f}:color=black[{faded_in}]")
            out = f"vb{i}"
            filters.append(f"[{faded_out}][{faded_in}]concat=n=2:v=1:a=0[{out}]")
            # Die Blende verlaengert: beide Clips bleiben vollstaendig, die Standzeit kommt
            # obendrauf. Genau das muss in den `tl_in`-Werten der Folgeclips stehen.
            cur_dur = cur_dur + clip.duration + t.hold
        else:
            out = f"vc{i}"
            filters.append(f"[{cur}][{labels[i]}]concat=n=2:v=1:a=0[{out}]")
            cur_dur = cur_dur + clip.duration
        cur = out
    return cur


# Deckel je Staerke: (max. Helligkeitsverschiebung, max. Saettigungsabweichung,
# max. Farbtemperatur-Korrektur). Eine Nachtaufnahme darf nicht auf Tageslicht gezogen werden.
COLOR_MATCH_LIMITS = {
    "off": (0.0, 0.0, 0.0),
    "soft": (0.08, 0.15, 0.08),
    "strong": (0.16, 0.30, 0.16),
}
DEFAULT_COLOR_MATCH = "soft"


def match_filter(color_match) -> str | None:
    """FFmpeg-Filterkette fuer die Angleichung eines Clips, oder `None` ohne Angleichung."""
    if color_match is None:
        return None
    brightness = color_match.brightness
    saturation = color_match.saturation
    temperature = color_match.temperature
    if brightness == 0.0 and saturation == 1.0 and temperature == 0.0:
        return None
    chain = f"eq=brightness={brightness:.4f}:saturation={saturation:.4f}"
    if temperature:
        # positiv = waermer (mehr Rot, weniger Blau), analog zu `grade_filter`
        chain += f",colorbalance=rs={temperature:.4f}:bs={-temperature:.4f}"
    return chain


def color_match_for(stats: dict, reference: dict, *, strength: str = DEFAULT_COLOR_MATCH):
    """Angleichungs-Werte eines Clips gegen eine Referenz — gedeckelt, `None` bei `off`.

    `stats`/`reference` sind `analyze.color_stats`-Ergebnisse. Die Korrektur ist bewusst mild
    und begrenzt (`COLOR_MATCH_LIMITS`): Ziel ist, Sprünge zwischen Drohne, Handy und Kamera zu
    dämpfen — nicht, jeden Clip gleich aussehen zu lassen.
    """
    from frameforge.timeline import ColorMatch

    limits = COLOR_MATCH_LIMITS.get(strength)
    if limits is None:
        raise ValueError(f"strength muss {sorted(COLOR_MATCH_LIMITS)} sein, nicht {strength!r}")
    if strength == "off" or not stats or not reference:
        return None

    max_brightness, max_saturation, max_temperature = limits

    def clamp(value: float, limit: float) -> float:
        return max(-limit, min(limit, value))

    brightness = clamp((reference["luma"] - stats["luma"]) / 255.0, max_brightness)
    temperature = clamp(reference["temperature"] - stats["temperature"], max_temperature)

    spread = sum(stats["std"].values()) / 3 or 1e-6
    ref_spread = sum(reference["std"].values()) / 3
    saturation = 1.0 + clamp(ref_spread / spread - 1.0, max_saturation)

    match = ColorMatch(
        brightness=round(brightness, 4),
        saturation=round(saturation, 4),
        temperature=round(temperature, 4),
    )
    return None if match_filter(match) is None else match


def reference_stats(stats_list: list[dict]) -> dict:
    """Median-Referenz über die im Export **verwendeten** Clips (nicht über den ganzen Fundus).

    Ein Export ist die relevante Einheit — Clips, die gar nicht vorkommen, dürfen den Zielton
    nicht verschieben. Median statt Mittelwert, damit ein einzelner Nacht- oder
    Gegenlicht-Clip die Referenz nicht wegzieht.
    """
    usable = [s for s in stats_list if s]
    if not usable:
        return {}

    def median(values: list[float]) -> float:
        ordered = sorted(values)
        mid = len(ordered) // 2
        return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2

    return {
        "luma": median([s["luma"] for s in usable]),
        "temperature": median([s["temperature"] for s in usable]),
        "std": {
            channel: median([s["std"][channel] for s in usable]) for channel in ("r", "g", "b")
        },
    }


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
        # negatives temp => mehr Rot/weniger Blau = wärmer; positives => kühler.
        chain += f",colorbalance=rs={-temp:.3f}:bs={temp:.3f}"
    return chain


# Defaults fuer die Overlay-Bewegungsanimation (Plan 0003-Feature "Slide-in-Titel"):
# `slide_in_s` ohne explizite Angabe, sobald `slide_from_px` != 0 ist; `drift_period_s` ohne
# explizite Angabe, sobald `drift_px` != 0 ist. Beide Werte sind bei "kein Slide/kein Drift"
# (0/None) bedeutungslos, damit bestehende Overlays ohne diese `anim`-Schluessel exakt das alte
# statische `x=0` reproduzieren.
_DEFAULT_SLIDE_IN_S = 1.5
_DEFAULT_DRIFT_PERIOD_S = 4.0


def _overlay_x_expr(anim: dict, tl_in: float, dur: float) -> str:
    """FFmpeg-`overlay`-x-Ausdruck (Funktion von `t`) fuer Slide-in + Drift eines Overlays.

    `anim` kennt (alle optional, Strings wie der Rest von `OverlayClip.anim`):
    - `slide_from_px`: X-Versatz bei `tl_in` in Pixeln (negativ = von links einlaufend,
      positiv = von rechts, 0/fehlend = keine Slide-Bewegung -- wie bisher).
    - `slide_in_s`: Dauer der Einlaufbewegung (Default 1.5s, gedeckelt auf `dur`).
    - `drift_px`: Amplitude einer sinusfoermigen Restbewegung waehrend der Hold-Phase, nach
      Abschluss des Slide-ins (0/fehlend = keine Drift).
    - `drift_period_s`: Periodendauer der Drift (Default 4.0s).

    Ohne `slide_from_px` und `drift_px` liefert das exakt `"0"` -- identisch zum bisherigen
    festen `x=0`, damit sich an bestehenden Overlays (z.B. `label-*.png`) nichts aendert.
    """
    slide_from = float(anim.get("slide_from_px", 0) or 0)
    drift_px = float(anim.get("drift_px", 0) or 0)
    if slide_from == 0 and drift_px == 0:
        return "0"

    slide_in_s = float(anim.get("slide_in_s", _DEFAULT_SLIDE_IN_S) or _DEFAULT_SLIDE_IN_S)
    slide_in_s = max(0.001, min(slide_in_s, dur))
    t0 = tl_in
    t1 = tl_in + slide_in_s

    terms = []
    if slide_from:
        # Linear von `slide_from_px` (bei t0) auf 0 (bei t1), danach konstant 0.
        terms.append(f"{slide_from:.2f}*max(0,min(1,({t1:.3f}-t)/{slide_in_s:.6f}))")
    if drift_px:
        drift_period_s = float(anim.get("drift_period_s", _DEFAULT_DRIFT_PERIOD_S) or _DEFAULT_DRIFT_PERIOD_S)
        drift_period_s = max(0.001, drift_period_s)
        # Drift erst NACH dem Slide-in, sonst ueberlagert sie die Einlaufbewegung.
        terms.append(
            f"if(gte(t,{t1:.3f}),{drift_px:.2f}*sin(2*PI*(t-{t1:.3f})/{drift_period_s:.3f}),0)"
        )
    return "+".join(terms)


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
        # Farbangleichung **pro Clip** und VOR dem Stil-Grade (Plan 0003 §H2): erst die
        # Kameras auf einen Nenner bringen, dann den Look darüber. Andersherum wäre "kühl"
        # eine Aussage über die zufällige Kameramischung statt über den Film.
        match = match_filter(clip.color_match)
        if match:
            chain.append(match)
        # Konstante fps sichern, damit concat/xfade sauber zusammenpassen. `fps` allein
        # normalisiert aber nicht die Timebase: `zoompan` (Ken-Burns-Fotos) liefert
        # AV_TIME_BASE (1/1000000), `fps` laesst das unangetastet, wenn sich an der
        # Framerate nichts aendert. Ohne `settb=AVTB` bricht `xfade` dann mit
        # "timebase do not match", sobald ein Foto-Clip direkt vor/nach einem
        # Crossfade liegt. Explizit auf jedem Segment erzwingen, nicht nur beim Foto-Zweig
        # -- normale Video-Clips laufen schon auf AVTB, der Filter ist fuer sie ein No-op.
        chain.append(f"fps={fps:g}")
        chain.append("settb=AVTB")
        filters.append(f"[{idx}:v]{','.join(chain)}[{label}]")
        video_labels.append(label)

    cur_video = _join_video_segments(clips, video_labels, filters)

    # -- Color-Grade auf das Footage, VOR den Overlays -------------------------------
    # Reihenfolge zählt: Grade/LUT gehören auf die Bilder, nicht auf Titel/Grafik — sonst
    # bekommt weißer Text einen Farbstich. Erst der Grundton aus dem Preset (dezent) …
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

    # -- Overlay: PNGs mit Alpha, Zeitfenster ueber `enable` -------------------------
    # Optional sanftes Ein-/Ausblenden ueber `anim.fade_in_s`/`anim.fade_out_s` (Alpha-Fade).
    for j, overlay in enumerate(timeline.tracks.overlay):
        anim = overlay.anim or {}
        fi = float(anim.get("fade_in_s", 0) or 0)
        fo = float(anim.get("fade_out_s", 0) or 0)
        x_expr = _overlay_x_expr(anim, overlay.tl_in, overlay.dur)
        ov_label = f"ov{j}"
        next_video = f"vov{j}"
        if fi > 0 or fo > 0:
            # Endliches, gefadetes Clip an tl_in verschieben (fade relativ zum eigenen Start).
            idx = add_input(
                ["-loop", "1", "-t", f"{overlay.dur:.3f}", "-framerate", str(timeline.fps),
                 "-i", str(export_root / overlay.png)]
            )
            chain = "format=rgba"
            if fi > 0:
                chain += f",fade=t=in:st=0:d={min(fi, overlay.dur):.3f}:alpha=1"
            if fo > 0:
                st = max(0.0, overlay.dur - fo)
                chain += f",fade=t=out:st={st:.3f}:d={min(fo, overlay.dur):.3f}:alpha=1"
            chain += f",setpts=PTS+{overlay.tl_in}/TB"
            filters.append(f"[{idx}:v]{chain}[{ov_label}]")
            filters.append(
                f"[{cur_video}][{ov_label}]overlay=x='{x_expr}':y=0:"
                f"enable='between(t,{overlay.tl_in},{overlay.tl_in + overlay.dur})'[{next_video}]"
            )
        else:
            idx = add_input(
                ["-loop", "1", "-framerate", str(timeline.fps), "-i", str(export_root / overlay.png)]
            )
            filters.append(f"[{idx}:v]format=rgba[{ov_label}]")
            filters.append(
                f"[{cur_video}][{ov_label}]overlay=x='{x_expr}':y=0:shortest=1:"
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

    # -- Schwarzblende ganz außen: fade-in aus Schwarz / fade-out nach Schwarz --------
    # Gesteuert über transition_in/out (Typ "fade") am ersten/letzten Video-Clip. Liegt bewusst
    # als letzter Schritt über allem (auch Overlays/Karte), damit wirklich alles ein-/ausblendet.
    if clips:
        first_t = clips[0].transition_in
        if first_t and first_t.type == "fade":
            d = min(first_t.dur, timeline.duration)
            out = f"{cur_video}_fin"
            filters.append(f"[{cur_video}]fade=t=in:st=0:d={d:.3f}[{out}]")
            cur_video = out
        last_t = clips[-1].transition_out
        if last_t and last_t.type == "fade":
            d = min(last_t.dur, timeline.duration)
            st = max(0.0, timeline.duration - d)
            out = f"{cur_video}_fout"
            filters.append(f"[{cur_video}]fade=t=out:st={st:.3f}:d={d:.3f}[{out}]")
            cur_video = out

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
        # Blenden liegen VOR `adelay` — `afade` rechnet in Clip-Zeit, nicht in Timeline-Zeit.
        # Ohne fade_in_s/fade_out_s (Default 0) entsteht exakt die bisherige Kette.
        fades = ""
        if audio.fade_in_s > 0:
            fades += f",afade=t=in:st=0:d={audio.fade_in_s:.3f}"
        if audio.fade_out_s > 0:
            fade_start = max(0.0, dur - audio.fade_out_s)
            fades += f",afade=t=out:st={fade_start:.3f}:d={audio.fade_out_s:.3f}"
        src_end = audio.src_in + dur
        filters.append(
            f"[{idx}:a]atrim=start={audio.src_in}:end={src_end},asetpts=PTS-STARTPTS{fades},"
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

    **Ausnahme HEIC/HEIF:** ffmpeg kann diese Dateien nicht in den Foto-Renderpfad geben
    (PROGRESS.md HEIC-1), deshalb wird für sie der JPEG-Proxy verwendet — eine verlustarme
    Umsetzung in voller Auflösung, kein Downscale.
    """
    assets_by_id = {a["id"]: a for a in load_assets(project)}
    proxies_dir = project.cache_dir / "proxies"

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
        # Einzige Ausnahme vom Prinzip "Final rendert aus den Originalen": ffmpeg kann HEIC
        # im Foto-Renderpfad nicht verwenden (PROGRESS.md HEIC-1). Der Proxy ist hier eine
        # verlustarme JPEG-Umsetzung in **voller** Aufloesung, kein Downscale — es geht keine
        # Bildgroesse verloren. Fehlt er, ist das ein Fehler und keine stille Notloesung.
        if original.suffix.lower() in HEIF_EXTENSIONS:
            proxy = proxy_path(original, proxies_dir, media_root=project.config.media_root)
            if not proxy.exists():
                raise RenderError(
                    f"HEIC-Asset '{asset_id}': ffmpeg kann HEIC nicht lesen, der JPEG-Proxy "
                    f"fehlt aber unter {proxy} — 'frameforge ingest {project.name}' ausfuehren"
                )
            return proxy
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
