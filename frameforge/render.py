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

import itertools
import json
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from frameforge import color as color_module
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
    # Foto-Clips mit erkannten Gesichtern, fuer die selbst mit Sicherheits-Margin kein Crop
    # existiert, der alle Gesichter vollstaendig enthaelt (siehe `_face_crop_center`). Diese
    # Clips wurden auf Bildmitte zentriert gecroppt (Fallback) -- Kandidaten fuer den
    # `timeline-builder`, den Clip durch eine Querformat-Alternative zu ersetzen.
    unsafe_face_crops: list[str] = field(default_factory=list)


def _scale_pad(width: int, height: int) -> str:
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    )


def _scale_crop(width: int, height: int, cx: float = 0.5, cy: float = 0.5) -> str:
    """`scale`(increase)+`crop` auf exakt `width`x`height` — Crop-to-Fill statt Letterbox/Pillarbox.

    Ersetzt `_scale_pad` fuer Foto-Ken-Burns-Clips (Audit 2026-08-08, QC-Befund render-engineer):
    `_scale_pad` (force_original_aspect_ratio=decrease + pad) erzeugt bei jedem Nicht-16:9-Foto
    schwarze Balken, die der nachfolgende Ken-Burns-Zoom nur mitvergroessert -- bei Hochkantfotos
    (3:4) bleiben ueber die gesamte Bewegung ca. 58% der Flaeche schwarz. `force_original_aspect_
    ratio=increase` + `crop` skaliert stattdessen so, dass das Bild die Zielflaeche IMMER
    vollstaendig deckt, und schneidet den Ueberschuss ab -- kein schwarzer Rand, dafuer echter
    Bildverlust an den Raendern (siehe `_face_crop_center` fuer die motivbewusste Positionierung).

    `cx`/`cy` in `[0, 1]`: Position des Crop-Fensters im gueltigen Versatzbereich (0=links/oben,
    0.5=zentriert=altes Zentrierungsverhalten, 1=rechts/unten). `max(0,min(...))` faengt
    Rundungsdifferenzen zwischen `scale`s Ganzzahl-Output und der exakten Zielgroesse ab.
    """
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height}:"
        f"x='max(0,min(iw-{width},(iw-{width})*{cx:.4f}))':"
        f"y='max(0,min(ih-{height},(ih-{height})*{cy:.4f}))',setsar=1"
    )


def _blur_fill_statements(src: str, dst: str, width: int, height: int) -> list[str]:
    """Bild vollstaendig sichtbar auf `width`x`height`, Rest mit einer unscharfen Kopie gefuellt.

    Der dritte Weg zwischen `_scale_pad` (schwarze Balken) und `_scale_crop` (schneidet ab):
    eine formatfuellend vergroesserte, stark weichgezeichnete Kopie liegt als Hintergrund, das
    ungeschnittene Motiv sitzt zentriert darauf.

    Nutzer-Feedback (2026-08-08, Runde 2) an beiden Enden dieses Kompromisses:
    - `_scale_crop` schnitt bei Hochkant-Fotos Personen an ("das Gesicht von Christina halb
      zerschnitten", "man sieht nur seine Kaeppi", "der halbe Oberkoerper"). Der face-aware Crop
      (`_face_crop_center`) hilft nur, wenn die Gesichtserkennung ALLE Personen gefunden hat --
      bei Kindern mit Kappe/Sonnenbrille findet sie eine zu wenig und der Ausschnitt schneidet
      genau die Person weg, die das Bild traegt.
    - `_scale_pad` erzeugte bei Hochkant-VIDEOS "dicke schwarze Balken" links und rechts
      ("genau das wollen wir nicht").

    Bei stark abweichendem Seitenverhaeltnis ist das hier die einzige Variante, die weder
    Bildinhalt verliert noch schwarze Flaechen zeigt. Ueber `VideoClip.fit = "blur"` pro Clip
    aus der Timeline gewaehlt, nicht heimlich im Renderer entschieden.

    Braucht `split` und `overlay` und ist damit kein linearer Filter-Abschnitt wie `_scale_pad`/
    `_scale_crop`, sondern mehrere `filter_complex`-Statements -- daher die explizite
    `src`/`dst`-Label-Signatur. Die Zwischenlabels werden aus `dst` abgeleitet und sind so pro
    Clip eindeutig.
    """
    return [
        f"[{src}]split=2[{dst}bg][{dst}fg]",
        f"[{dst}bg]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},gblur=sigma=42:steps=3,eq=brightness=-0.12[{dst}bgb]",
        f"[{dst}fg]scale={width}:{height}:force_original_aspect_ratio=decrease[{dst}fgs]",
        # Kein `shortest=1`: beide Zweige kommen aus demselben `split` und sind exakt gleich
        # lang -- der Schalter waere wirkungslos, koennte aber (wie beim Karten-Overlay, Runde 2)
        # bei kuenftigen Aenderungen still den ganzen Video-Pfad kappen.
        f"[{dst}bgb][{dst}fgs]overlay=x=(W-w)/2:y=(H-h)/2,setsar=1[{dst}]",
    ]


def _face_crop_center(
    faces: list[dict],
    src_w: int,
    src_h: int,
    target_w: int,
    target_h: int,
    *,
    margin: float = 0.15,
) -> tuple[float, float] | None:
    """Normalisiertes Crop-Zentrum (`cx`, `cy` fuer `_scale_crop`) aus erkannten Gesichtern.

    Legt das Crop-Fenster auf die vereinigte Bounding-Box aller `faces` (Format wie
    `people.detect_faces`: `{"top", "right", "bottom", "left"}` in Quellpixeln), mit einem
    Sicherheits-Rand (`margin`, Bruchteil der Face-Box-Groesse -- analog `people.crop_face`)
    an allen vier Seiten, damit noch "Fleisch" fuer den Ken-Burns-Zoom/-Pan bleibt.

    Ohne `faces`: Bildmitte (`(0.5, 0.5)`, identisch zum alten zentrierten Verhalten).

    Gibt `None` zurueck, wenn selbst mit Margin kein Crop-Fenster existiert, das die Gesichter
    vollstaendig enthaelt (Gesicht sitzt zu nah am kurzen Bildrand eines extremen Formats) --
    der Aufrufer faellt dann auf Bildmitte zurueck, der Clip gehoert aber auf die Liste der
    Ersetzungskandidaten (kein Crop, der das Motiv sicher erhaelt).

    Da der Ken-Burns-Zoom in `_kenburns_expr` danach nur noch **in die Mitte dieses bereits
    motivsicheren Ausschnitts hineinzoomt** (nicht in die Bildmitte des Originalfotos), bleiben
    die Gesichter ueber die gesamte Zoom-Range sichtbar, wenn sie hier schon sicher im
    Ausschnitt liegen -- nicht nur im ersten Frame.
    """
    if not faces:
        return (0.5, 0.5)
    scale = max(target_w / src_w, target_h / src_h)
    max_ox = src_w * scale - target_w
    max_oy = src_h * scale - target_h

    ux0 = min(f["left"] for f in faces) * scale
    uy0 = min(f["top"] for f in faces) * scale
    ux1 = max(f["right"] for f in faces) * scale
    uy1 = max(f["bottom"] for f in faces) * scale
    mx = (ux1 - ux0) * margin
    my = (uy1 - uy0) * margin
    rx0, rx1 = ux0 - mx, ux1 + mx
    ry0, ry1 = uy0 - my, uy1 + my

    def clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value)) if hi > lo else lo

    crop_x0 = clamp((rx0 + rx1) / 2 - target_w / 2, 0.0, max_ox)
    crop_y0 = clamp((ry0 + ry1) / 2 - target_h / 2, 0.0, max_oy)
    safe = (
        rx0 >= crop_x0 - 0.5
        and rx1 <= crop_x0 + target_w + 0.5
        and ry0 >= crop_y0 - 0.5
        and ry1 <= crop_y0 + target_h + 0.5
    )
    if not safe:
        return None
    cx = crop_x0 / max_ox if max_ox > 1e-6 else 0.5
    cy = crop_y0 / max_oy if max_oy > 1e-6 else 0.5
    return (cx, cy)


# Grobe, bewusst dezente Übersetzung der Preset-`color_grade`-Stimmung in FFmpeg-Filter.
# Keine Ersatz für eine echte Farbkorrektur (dafür `--lut`), aber gibt jedem Stil-Preset
# automatisch einen passenden Grundton. Werte konservativ gehalten, damit nichts "kaputt" aussieht.
_CONTRAST_MAP = {"low": 0.95, "medium": 1.05, "medium_high": 1.12, "high": 1.20}
# Konvention (einheitlich mit `match_filter`/`ColorMatch`): **positives** `temperature` =
# wärmer. Bis 2026-08-10 galt hier das Gegenteil, in `match_filter` aber schon diese Regel —
# dasselbe Feld hatte in beiden Funktionen entgegengesetzte Bedeutung.
_MOOD_MAP: dict[str, dict] = {
    "cool_highlights_warm_lights": {"saturation": 1.05, "temperature": 0.06},
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

# Referenzweiss und Umrechnung `temperature` (dimensionslos, positiv = wärmer) → Kelvin.
_NEUTRAL_KELVIN = 6500.0
# Gemessen an `colortemperature`: ~100 K entsprechen ~1.5 Punkten R−B. Die Mood-Werte
# (0.03–0.08) waren fuer den alten, viel schwaecheren Schatten-Regler getunt; mit 2000 K je
# Einheit landet `cool_highlights_warm_lights` bei 6380 K ≈ +3.5 R−B — spuerbar warm, aber
# kein Stich. Mit 4000 K waeren es ~+7 gewesen, und genau darueber kam der Nutzer-Report.
_KELVIN_PER_UNIT = 2000.0


def temperature_filter(temperature: float) -> str | None:
    """`colortemperature`-Filter für eine Farbtemperatur-Korrektur, `None` bei 0.

    **Ersetzt `colorbalance=rs=…:bs=…`** (Bug, gefunden 2026-08-10). `rs`/`bs` sind in ffmpeg
    die **Schatten**-Regler für Rot/Blau, nicht Farbtemperatur — der alte Code hob damit Rot
    in den dunklen Bildpartien an und senkte Blau, während die Lichter unberührt blieben.
    Gemessen am `vlog-edit`: farbneutrale Motive kamen mit R−B +13 statt +5 heraus, Hauttöne
    kippten sichtbar ins Rote. `colortemperature` verschiebt stattdessen das Weiss des ganzen
    Bildes, also das, was der Preset-Katalog mit "wärmer/kühler" tatsächlich meint.
    """
    if not temperature:
        return None
    kelvin = _NEUTRAL_KELVIN - temperature * _KELVIN_PER_UNIT
    # `pl=1` (preserve lightness): eine Temperaturkorrektur soll die Helligkeit nicht mitziehen.
    return f"colortemperature=temperature={kelvin:.0f}:mix=1:pl=1"


# Übergangstypen, die als Crossfade (xfade) gerendert werden.
_CROSSFADE_TYPES = {"fade", "dissolve", "slow_dissolve", "crossfade"}


def _kenburns_expr(clip, dur: float, fps: float, res: tuple[int, int]) -> str | None:
    """`zoompan`-Ausdruck für Ken-Burns (Zoom + Pan) auf einem Foto-Clip.

    Aktiv nur, wenn der Clip einen Effekt vom Typ `kenburns` trägt (Timeline = Single Source of
    Truth). Zoom aus `from[2]`/`to[2]` (falls gesetzt), sonst dezenter Default-Zoom. Pan aus
    `from[0:2]`/`to[0:2]` — Bruchteil der (skalierten) Bildbreite/-höhe, `0.0` = zentriert
    (Default, identisch zum bisherigen Verhalten ohne Pan).

    **Bugfix (Audit 2026-08-08, render-engineer):** `from`/`to` tragen `[x, y, z]`, aber diese
    Funktion las bislang nur Index `[2]` (Zoom) — die x/y-Pan-Offsets aus der Timeline waren
    komplett wirkungslos, jeder Ken-Burns war ein zentrierter Zoom ohne echten Schwenk. Jetzt
    fließen `x`/`y` linear über die Clipdauer in den `zoompan`-x/y-Ausdruck ein, geclamped auf
    den gültigen Bereich `[0, iw-iw/zoom]` (ein zu großer Pan-Wert darf `zoompan` nicht mit
    einem ungültigen Fenster crashen lassen).

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

    def xyz(key: str, default: tuple[float, float, float]) -> tuple[float, float, float]:
        val = data.get(key)
        if isinstance(val, (list, tuple)) and len(val) >= 3:
            return float(val[0]), float(val[1]), float(val[2])
        return default

    x_from, y_from, z_from = xyz("from", (0.0, 0.0, 1.0))
    x_to, y_to, z_to = xyz("to", (0.0, 0.0, 1.10))
    # Beide Richtungen erlaubt: `z_to < z_from` ist ein Zoom HERAUS und ein legitimer Stil.
    # Vorher wurde `z_to` auf `z_from + 0.001` hochgeklemmt -- damit war jeder Zoom-out still
    # ein Standbild (fiel bei den neuen Ken-Burns-Varianten aus Runde 3 auf).
    z_from = max(1.0, z_from)
    z_to = max(1.0, z_to)
    if abs(z_to - z_from) < 0.001:
        z_to = z_from + 0.001
    w, h = res
    # Fortschritt 0..1 ueber die Clipdauer. `ease: "smooth"` legt eine Smoothstep-Kurve
    # (3n²-2n³) darueber: die Bewegung startet und endet weich, statt hart mit konstanter
    # Geschwindigkeit einzusetzen und abzureissen. Nutzer-Feedback (2026-08-08, Runde 2): der
    # lineare Schwenk wirkte mechanisch und war ueber alle Fotos hinweg als immer gleiche
    # Bewegung wiedererkennbar. Default bleibt "linear" -- bestehende Timelines rendern
    # unveraendert, nur wer `ease` setzt, bekommt die neue Kurve.
    n = f"min(1,on/{frames})"
    if str(data.get("ease", "linear")).lower() in {"smooth", "smoothstep", "ease"}:
        p = f"({n})*({n})*(3-2*({n}))"
    else:
        p = n
    zoom_expr = f"{z_from:.4f}+({p})*{z_to - z_from:.6f}"
    x_pan = f"({x_from:.4f}+({p})*{x_to - x_from:.6f})*iw"
    y_pan = f"({y_from:.4f}+({p})*{y_to - y_from:.6f})*ih"
    x_expr = f"max(0,min(iw-iw/zoom,iw/2-(iw/zoom/2)+{x_pan}))"
    y_expr = f"max(0,min(ih-ih/zoom,ih/2-(ih/zoom/2)+{y_pan}))"
    # Ueber der Zielgroesse samplen, damit `zoompan` nicht auf ganze Quellpixel rasten muss
    # (sonst ruckelt der Zoom). Der Faktor richtet sich nach dem **groessten vorkommenden Zoom**
    # plus etwas Reserve, nicht mehr pauschal 2x.
    #
    # Warum das wichtig ist: 2x bedeutet bei 4K-Ziel ein 7680x4320-Zwischenbild, also ~100 MB je
    # Frame. Bei 62 Foto-Clips, die alle gleichzeitig als Input offen sind und deren Frames die
    # nachgelagerte `xfade`-Kette puffert, hat der Preview-Render dadurch den Arbeitsspeicher
    # gesprengt: macOS legte 11 GB Swap an, die Platte lief voll, der Prozess starb. Das war die
    # Ursache der wiederholt "unerklaerlich" abgebrochenen Renders (2026-08-08/09).
    # `zoompan` schneidet `iw/zoom` heraus -- ein Oversampling um `max_zoom` reicht also exakt
    # aus, damit dieser Ausschnitt noch mindestens die Zielgroesse hat; 1.15 ist die Reserve.
    # Bei typischem Zoom 1.13 sind das 1.30x statt 2x, also ~2,4x weniger Speicher je Frame.
    # Reserve abhaengig von der Zielaufloesung (Nutzer-Report 2026-08-10: "die Fotos
    # zittern"). `zoompan` rastet den Ausschnitt auf ganze QUELLpixel; ein Quellpixel
    # entspricht `1/sample` Ausgabepixeln. Bei 1.15 Reserve sind das 0,77 Ausgabepixel --
    # sichtbar als Ruckeln, gemessen 0,12-0,18 px Ruck je Frame gegenueber 0,02 px bei
    # Videoclips. In 4K faellt derselbe Fehler beim Herunterskalieren auf einen 1080p-Schirm
    # zur Haelfte weg, deshalb war er dort nie auffaellig.
    # 1080p-Ziele bekommen darum 3.0 statt 1.15: ~0,29 statt 0,77 Ausgabepixel je Rastschritt.
    # Der Speicher gibt das her, seit der Final-Render in Chunks laeuft (~24 offene Inputs
    # statt 213) -- in 4K bleibt es bei 1.15, dort waeren es sonst wieder ~600 MB je Frame.
    reserve = 3.0 if h <= 1200 else 1.15
    sample = max(1.05, max(z_from, z_to)) * reserve
    sw, sh = round(w * sample), round(h * sample)
    sw += sw % 2
    sh += sh % 2
    # `setsar=1` ist Pflicht: die Rundung von `sw`/`sh` auf gerade Werte verschiebt das
    # Seitenverhaeltnis minimal, `zoompan` gibt das als SAR weiter (z.B. 304:303) und `concat`
    # bricht dann mit "parameters do not match" ab.
    return (
        f"scale={sw}:{sh},"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d=1:s={w}x{h}:fps={fps:g},"
        f"setsar=1"
    )


def _color_pop_expr(clip) -> str | None:
    """`eq`-Filterausdruck fuer einen kurzen Saettigungs-/Farb-Puls (Plan 0004 §5, Comic-FX).

    Aktiv nur, wenn der Clip einen Effekt vom Typ `color_pop` traegt (analog zu
    `_kenburns_expr`). Parameter (alle optional, Defaults in Klammern): `at` (0.0) — Clip-
    lokale Sekunde, an der der Puls beginnt; `dur` (0.3) — Laenge des Pulses in Sekunden;
    `peak` (1.8) — Saettigung im Puls-Maximum (1.0 = unveraendert).

    `t` ist hier Clip-lokale Zeit (durch `setpts=PTS-STARTPTS` weiter oben in der Kette),
    nicht Timeline-Zeit — der Puls sitzt also relativ zum Clip-Anfang, unabhaengig davon, wo
    der Clip in der Timeline landet. `enable='between(...)'` schaltet den Filter ausserhalb
    des Fensters komplett ab (derselbe Kniff wie bei Overlay-/Duck-Fenstern), ein
    Sinus-Envelope innerhalb des Fensters sorgt fuer weiches Ein-/Ausschwingen statt eines
    harten Sprungs.
    """
    fx = next((e for e in clip.effects if e.type == "color_pop"), None)
    if fx is None:
        return None
    data = fx.model_dump()
    at = float(data.get("at", 0.0))
    dur = max(0.05, float(data.get("dur", 0.3)))
    peak = float(data.get("peak", 1.8))
    end = at + dur
    envelope = f"sin(PI*(t-{at:.3f})/{dur:.3f})"
    saturation = f"1+({peak:.3f}-1)*({envelope})"
    return f"eq=eval=frame:saturation='{saturation}':enable='between(t,{at:.3f},{end:.3f})'"


def _cartoon_outline_expr(clip) -> str | None:
    """Filterkette fuer einen Comic-/Kritzel-Rand (Plan 0004 §5, Comic-FX).

    Aktiv nur bei einem Effekt vom Typ `cartoon_outline`. FFmpeg-natives Aequivalent zum im
    Plan urspruenglich skizzierten OpenCV-Cartoonizer (Bilateral-Filter + Kantenerkennung):
    `gblur` glaettet vor der Kantenerkennung (entspricht dem Bilateral-Schritt), `edgedetect=
    mode=colormix` legt die erkannten Kanten in Originalfarbe ueber das geglaettete Bild statt
    es (wie `mode=wires`) komplett durch eine Kantenkarte zu ersetzen. Vorteil gegenueber einer
    echten OpenCV-Vorverarbeitung: bleibt im bestehenden Ein-Pass-Filtergraphen dieser Funktion,
    statt eine zweite Video-Datei vorab zu erzeugen — weniger neue Codepfade, aber auch ein
    einfacherer Look. Wirkt schwaecher als eine echte Bilateral-Kantenerkennung; falls das nach
    einem echten Render zu duenn aussieht, ist eine OpenCV-Vorstufe der naheliegende Ausbau.

    Parameter (alle optional): `at`/`dur` — Zeitfenster wie bei `_color_pop_expr` (Default: die
    ganze Clipdauer, kein `enable`-Gate); `blur` (4.0) — Glaettungsstaerke vor der
    Kantenerkennung; `edge_low`/`edge_high` (0.1/0.35) — `edgedetect`-Schwellwerte.
    """
    fx = next((e for e in clip.effects if e.type == "cartoon_outline"), None)
    if fx is None:
        return None
    data = fx.model_dump()
    blur = max(0.0, float(data.get("blur", 4.0)))
    low = float(data.get("edge_low", 0.1))
    high = float(data.get("edge_high", 0.35))
    gate = ""
    if data.get("at") is not None and data.get("dur") is not None:
        at = float(data["at"])
        end = at + max(0.05, float(data["dur"]))
        gate = f":enable='between(t,{at:.3f},{end:.3f})'"
    return f"gblur=sigma={blur:.2f}{gate},edgedetect=mode=colormix:low={low:.3f}:high={high:.3f}{gate}"


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
    temp = temperature_filter(temperature)  # positiv = waermer, analog zu `grade_filter`
    if temp:
        chain += f",{temp}"
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
    temp = temperature_filter(params.get("temperature", 0.0))
    if temp:
        chain += f",{temp}"
    return chain


# Defaults fuer die Overlay-Bewegungsanimation (Plan 0003-Feature "Slide-in-Titel"):
# `slide_in_s` ohne explizite Angabe, sobald `slide_from_px` != 0 ist; `drift_period_s` ohne
# explizite Angabe, sobald `drift_px` != 0 ist. Beide Werte sind bei "kein Slide/kein Drift"
# (0/None) bedeutungslos, damit bestehende Overlays ohne diese `anim`-Schluessel exakt das alte
# statische `x=0` reproduzieren.
_DEFAULT_SLIDE_IN_S = 1.5
_DEFAULT_DRIFT_PERIOD_S = 4.0


def _overlay_axis_expr(anim: dict, tl_in: float, dur: float, *, from_key: str, drift_key: str) -> str:
    """FFmpeg-`overlay`-Achsen-Ausdruck (Funktion von `t`) fuer Slide-in + Drift eines Overlays.

    Achsenneutral: `from_key`/`drift_key` waehlen `slide_from_px`/`drift_px` (X) oder
    `slide_from_py`/`drift_py` (Y) aus `anim` -- `slide_in_s`/`drift_period_s` gelten fuer
    beide Achsen gemeinsam (ein Overlay hat eine Einlaufdauer, nicht zwei).

    `anim` kennt (alle optional, Strings wie der Rest von `OverlayClip.anim`):
    - `slide_from_p{x,y}`: Versatz bei `tl_in` in Pixeln (negativ = von links/oben einlaufend,
      positiv = von rechts/unten, 0/fehlend = keine Slide-Bewegung auf dieser Achse).
    - `slide_in_s`: Dauer der Einlaufbewegung (Default 1.5s, gedeckelt auf `dur`).
    - `drift_p{x,y}`: Amplitude der Restbewegung waehrend der Hold-Phase, nach Abschluss des
      Slide-ins (0/fehlend = keine Drift).
    - `drift_mode`: `"sine"` (Default) laesst die Drift um die Endposition pendeln,
      `"linear"` laesst sie bis zum Clipende gleichmaessig in EINE Richtung weiterlaufen.
      Nutzer-Feedback (2026-08-08, Runde 2): das Pendeln des Titels wirkte als sichtbares
      Hin-und-Her, und weil `overlay` die Position auf ganze Pixel rundet, sieht die Umkehr
      an den Sinus-Extrema (wo die Bewegung fast stillsteht) wie Ruckeln/Pixeln aus. Linear
      heisst: die Bewegung laeuft in Slide-in-Richtung weiter, gleiche Schrittweite, kein
      Stillstand, keine Umkehr.
    - `drift_period_s`: Periodendauer der Drift (nur `drift_mode="sine"`, Default 4.0s).
    - `drift_dur_s`: Dauer der linearen Drift (nur `drift_mode="linear"`, Default: bis zum
      Clipende). Danach steht das Overlay fest. Nutzer-Feedback (2026-08-09, Runde 3-Preview):
      "das tickert so, tack tack tack" -- `overlay` positioniert ganzzahlig, eine Drift von
      56px ueber 9,7s ist 5,8 px/s, also ein Sprung alle 5 Frames (30 fps). Sichtbar gestuft,
      und daran aendert auch 4K nichts, es halbiert nur die Schrittweite. Smooth wird es erst
      ab ~1 px/Frame; deshalb dieselbe Strecke in kurzer Zeit abfahren (56px in 1.5s =
      37 px/s > 30 px/s) und danach stehen bleiben, statt sie ueber die ganze Standzeit zu
      strecken.

    Ohne Slide/Drift auf dieser Achse liefert das exakt `"0"` -- identisch zum bisherigen
    festen `x=0`/`y=0`, damit sich an bestehenden Overlays (z.B. `label-*.png`) nichts aendert.
    """
    slide_from = float(anim.get(from_key, 0) or 0)
    drift = float(anim.get(drift_key, 0) or 0)
    if slide_from == 0 and drift == 0:
        return "0"

    slide_in_s = float(anim.get("slide_in_s", _DEFAULT_SLIDE_IN_S) or _DEFAULT_SLIDE_IN_S)
    slide_in_s = max(0.001, min(slide_in_s, dur))
    t1 = tl_in + slide_in_s

    terms = []
    if slide_from:
        # Linear von `slide_from` (bei t0) auf 0 (bei t1), danach konstant 0.
        terms.append(f"{slide_from:.2f}*max(0,min(1,({t1:.3f}-t)/{slide_in_s:.6f}))")
    if drift:
        # Drift erst NACH dem Slide-in, sonst ueberlagert sie die Einlaufbewegung.
        if str(anim.get("drift_mode", "sine")).lower() == "linear":
            hold_s = max(0.001, dur - slide_in_s)
            drift_dur_s = float(anim.get("drift_dur_s", 0) or 0) or hold_s
            drift_dur_s = max(0.001, min(drift_dur_s, hold_s))
            terms.append(
                f"{drift:.2f}*max(0,min(1,(t-{t1:.3f})/{drift_dur_s:.6f}))"
            )
        else:
            drift_period_s = float(
                anim.get("drift_period_s", _DEFAULT_DRIFT_PERIOD_S) or _DEFAULT_DRIFT_PERIOD_S
            )
            drift_period_s = max(0.001, drift_period_s)
            terms.append(
                f"if(gte(t,{t1:.3f}),{drift:.2f}*sin(2*PI*(t-{t1:.3f})/{drift_period_s:.3f}),0)"
            )
    return "+".join(terms)


def _overlay_x_expr(anim: dict, tl_in: float, dur: float) -> str:
    return _overlay_axis_expr(anim, tl_in, dur, from_key="slide_from_px", drift_key="drift_px")


def _overlay_y_expr(anim: dict, tl_in: float, dur: float) -> str:
    return _overlay_axis_expr(anim, tl_in, dur, from_key="slide_from_py", drift_key="drift_py")


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
    faces_by_asset: dict[str, list[dict]] | None = None,
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

    `faces_by_asset`: optional, `{asset_id: [{"top","right","bottom","left"}, ...]}` (Format wie
    `people.detect_faces`, ohne `encoding` -- nur die Location wird gebraucht). Steuert das
    Crop-Zentrum von Foto-Ken-Burns-Clips (`_face_crop_center`); ohne diese Angabe (Default,
    z.B. wenn `frameforge faces` fuer das Projekt nie lief) wird jedes Foto crop-to-fill auf die
    Bildmitte zentriert -- kein Pillarbox/Letterbox mehr, aber auch kein motivbewusster Crop.
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
        chain: list[str] = []  # bis einschliesslich Fit-Schritt
        post: list[str] = []  # alles danach (Ken-Burns, Farbe, fps/timebase)
        # `fit="blur"` ist kein linearer Filter, sondern eigene Statements (split/overlay) --
        # der Rest der Kette laeuft darum in `post` hinter dem Fit-Schritt weiter.
        blur_fit = clip.fit == "blur"
        if source.suffix.lower() in PHOTO_EXTENSIONS:
            # **KEIN `-t` hier.** Naheliegend waere es (der Overlay-Zweig unten nutzt es), aber
            # gemessen macht es den Render kaputt: mit `-t` friert das Bild ab dem ERSTEN
            # Foto-Clip ein und bleibt es bis zum Schluss -- Frame-zu-Frame-Differenz exakt 0.0
            # ueber 100+ Sekunden, Bitrate faellt auf 168 kbit/s. Grund ist die
            # `xfade`-Kette in `_join_video_segments`: sie zieht Frames nach dem
            # `offset`-Fahrplan, und ein Input, der vorher EOF meldet, laesst den nachfolgenden
            # `xfade` den letzten Frame endlos wiederholen.
            # Die Laufzeit begrenzt stattdessen `trim=duration=` in der Kette (naechste Zeile).
            # An einem 30-Clip-Ausschnitt beide Varianten gegengemessen (siehe PROGRESS.md,
            # Abschnitt zu Runde 3).
            idx = add_input(["-loop", "1", "-framerate", str(fps), "-i", str(source)])
            chain.append(f"trim=duration={clip.duration:.3f}")
            chain.append("setpts=PTS-STARTPTS")
            cx, cy = 0.5, 0.5
            faces = (faces_by_asset or {}).get(clip.asset)
            if faces:
                try:
                    from frameforge.imageio import open_image

                    src_w, src_h = open_image(source).size
                except Exception:  # noqa: BLE001 — Bildgroesse nicht lesbar => Bildmitte, kein Render-Abbruch
                    src_w = src_h = None
                if src_w and src_h:
                    center = _face_crop_center(faces, src_w, src_h, *target_res)
                    if center is None:
                        graph.unsafe_face_crops.append(clip.asset)
                        # Es existiert KEIN Ausschnitt, der alle erkannten Gesichter ganz
                        # enthaelt. Fallback ist deshalb Blur-Fill (Bild ungeschnitten, unscharf
                        # gefuellter Rand) statt eines Crops auf die Bildmitte, der garantiert
                        # jemanden anschneidet. Nutzer-Regel aus Runde 3: "die Personen auf einem
                        # Bild muessen immer sichtbar sein ... es darf keine Person ausgelassen
                        # werden." Ein explizit gesetztes `fit` bleibt unangetastet -- wer
                        # bewusst croppt oder padded, wird nicht ueberstimmt.
                        if clip.fit is None:
                            blur_fit = True
                    else:
                        cx, cy = center
            if not blur_fit:
                chain.append(
                    _scale_pad(*target_res) if clip.fit == "pad"
                    else _scale_crop(*target_res, cx, cy)
                )
            kb = _kenburns_expr(clip, clip.duration, fps, target_res)
            if kb:
                post.append(kb)
        else:
            idx = add_input(["-i", str(source)])
            chain.append(f"trim=start={clip.src_in}:end={clip.src_out}")
            chain.append(f"setpts=(PTS-STARTPTS)/{clip.speed}")
            if not blur_fit:
                chain.append(
                    _scale_crop(*target_res) if clip.fit == "crop" else _scale_pad(*target_res)
                )
        # Farbangleichung **pro Clip** und VOR dem Stil-Grade (Plan 0003 §H2): erst die
        # Kameras auf einen Nenner bringen, dann den Look darüber. Andersherum wäre "kühl"
        # eine Aussage über die zufällige Kameramischung statt über den Film.
        # Farbraum-Normalisierung **zuerst**: HLG/BT.2020 (iPhone), Full-Range-JPEG (Foto-
        # Proxies) und BT.709 (Drohne) liegen sonst nebeneinander im selben Graphen, und jeder
        # nachfolgende Filter arbeitet je Clip auf anderen Werten. Siehe frameforge.color.
        post.extend(color_module.normalize_chain(source))
        match = match_filter(clip.color_match)
        if match:
            post.append(match)
        # Comic/Party-FX-Baukasten (Plan 0004 §5/§6): Farb-Pop und Cartoon-Outline sind
        # Effekte AUF dem Clip selbst (wie `kenburns`), keine Overlay-Datei — deshalb hier,
        # nach der Farbangleichung und vor dem Stil-Grade, damit sie auf demselben,
        # bereits farbnormalisierten Bild wirken wie alles andere.
        pop = _color_pop_expr(clip)
        if pop:
            post.append(pop)
        cartoon = _cartoon_outline_expr(clip)
        if cartoon:
            post.append(cartoon)
        # Konstante fps sichern, damit concat/xfade sauber zusammenpassen. `fps` allein
        # normalisiert aber nicht die Timebase: `zoompan` (Ken-Burns-Fotos) liefert
        # AV_TIME_BASE (1/1000000), `fps` laesst das unangetastet, wenn sich an der
        # Framerate nichts aendert. Ohne `settb=AVTB` bricht `xfade` dann mit
        # "timebase do not match", sobald ein Foto-Clip direkt vor/nach einem
        # Crossfade liegt. Explizit auf jedem Segment erzwingen, nicht nur beim Foto-Zweig
        # -- normale Video-Clips laufen schon auf AVTB, der Filter ist fuer sie ein No-op.
        post.append(f"fps={fps:g}")
        post.append("settb=AVTB")
        if blur_fit:
            filters.append(f"[{idx}:v]{','.join(chain)}[{label}pre]")
            filters.extend(_blur_fill_statements(f"{label}pre", f"{label}fit", *target_res))
            filters.append(f"[{label}fit]{','.join(post)}[{label}]")
        else:
            filters.append(f"[{idx}:v]{','.join(chain + post)}[{label}]")
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
    #
    # Die Overlay-PNGs entstehen formatfuellend in der Timeline-Auflaesung (`design.overlay_
    # tokens` rechnet alles relativ zu Breite/Hoehe). Rendert man auf eine ANDERE Auflaesung --
    # z.B. den 1080p-Preview aus einer 4K-Timeline -- muessen sie mitskaliert werden, sonst liegt
    # ein 4K-Titel in Originalgroesse auf einem 1080p-Bild. Genauso die Pixelwerte in `anim`
    # (`slide_from_px`, `drift_px`, ...), die sonst viermal zu weit schieben.
    overlay_scale = target_res[0] / timeline.resolution[0] if timeline.resolution[0] else 1.0

    def scaled_anim(anim: dict) -> dict:
        if overlay_scale == 1.0:
            return anim
        out = dict(anim)
        for key in ("slide_from_px", "slide_from_py", "drift_px", "drift_py"):
            if out.get(key):
                out[key] = str(float(out[key]) * overlay_scale)
        return out

    for j, overlay in enumerate(timeline.tracks.overlay):
        anim = scaled_anim(overlay.anim or {})
        fi = float(anim.get("fade_in_s", 0) or 0)
        fo = float(anim.get("fade_out_s", 0) or 0)
        x_expr = _overlay_x_expr(anim, overlay.tl_in, overlay.dur)
        y_expr = _overlay_y_expr(anim, overlay.tl_in, overlay.dur)
        ov_label = f"ov{j}"
        next_video = f"vov{j}"
        if fi > 0 or fo > 0:
            # Endliches, gefadetes Clip an tl_in verschieben (fade relativ zum eigenen Start).
            idx = add_input(
                ["-loop", "1", "-t", f"{overlay.dur:.3f}", "-framerate", str(timeline.fps),
                 "-i", str(export_root / overlay.png)]
            )
            chain = "format=rgba"
            if overlay_scale != 1.0:
                chain += f",scale={target_res[0]}:{target_res[1]}"
            if fi > 0:
                chain += f",fade=t=in:st=0:d={min(fi, overlay.dur):.3f}:alpha=1"
            if fo > 0:
                st = max(0.0, overlay.dur - fo)
                chain += f",fade=t=out:st={st:.3f}:d={min(fo, overlay.dur):.3f}:alpha=1"
            chain += f",setpts=PTS+{overlay.tl_in}/TB"
            filters.append(f"[{idx}:v]{chain}[{ov_label}]")
            filters.append(
                f"[{cur_video}][{ov_label}]overlay=x='{x_expr}':y='{y_expr}':"
                f"enable='between(t,{overlay.tl_in},{overlay.tl_in + overlay.dur})'[{next_video}]"
            )
        else:
            idx = add_input(
                ["-loop", "1", "-framerate", str(timeline.fps), "-i", str(export_root / overlay.png)]
            )
            scale_part = (
                f",scale={target_res[0]}:{target_res[1]}" if overlay_scale != 1.0 else ""
            )
            filters.append(f"[{idx}:v]format=rgba{scale_part}[{ov_label}]")
            filters.append(
                f"[{cur_video}][{ov_label}]overlay=x='{x_expr}':y='{y_expr}':shortest=1:"
                f"enable='between(t,{overlay.tl_in},{overlay.tl_in + overlay.dur})'[{next_video}]"
            )
        cur_video = next_video

    # -- Karten-Clips: eigene kleine Videos (mit Alpha), unten rechts eingeblendet ---
    for k, map_clip in enumerate(timeline.tracks.map):
        idx = add_input(["-i", str(export_root / map_clip.clip)])
        shifted = f"map{k}shift"
        next_video = f"vmap{k}"
        # `trim=duration=` VOR dem Shift: die Kartendatei ist oft laenger als ihr Zeitfenster
        # in der Timeline (Rezept rendert auf volle Etappen-/Dwell-Laenge, gebraucht wird nur
        # `map_clip.dur`). Ohne den Trim haengt `overlay` (ohne `shortest=1`, siehe unten) den
        # kompletten Dateirest ans Filmende (gefundener Bug: K15-Datei 50s vs. 32,887s Fenster
        # verlaengerte den Gesamtfilm um exakt die Differenz, 1073,887s -> 1091,033s).
        filters.append(
            f"[{idx}:v]trim=duration={map_clip.dur:.3f},setpts=PTS-STARTPTS+{map_clip.tl_in}/TB"
            f"[{shifted}]"
        )
        # Kein `shortest=1` hier: der Karten-Clip ist jetzt (nach dem Trim oben) auf sein eigenes
        # `enable`-Fenster begrenzt. Mit `shortest=1` haette **jeder** Karten-Clip in dieser
        # Schleife das gesamte bis dahin aufgebaute `cur_video` auf seine eigene Laenge gekappt --
        # der erste Karten-Clip (K2) hat den kompletten Film auf ~132s abgeschnitten, Ton lief
        # unbeeinflusst weiter (gefundener Bug, Video "friert ein" bei Minute 2).
        # Rand ebenfalls mit der Zielauflaesung skalieren, sonst sitzt das Inset im 1080p-Preview
        # viermal so weit vom Bildrand weg wie im 4K-Final.
        margin = max(1, round(60 * overlay_scale))
        filters.append(
            f"[{cur_video}][{shifted}]overlay=x=W-w-{margin}:y=H-h-{margin}:"
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

    # Letzter Schritt vor dem Encoder: Pixelformat und Farbtags festnageln. Grade/LUT/Overlay
    # laufen ueber RGB-Filter, und was danach herauskommt, bestimmte bisher allein die
    # ffmpeg-Aushandlung — im vlog-edit hatten die MJPEG-Foto-Inputs damit `yuvj420p / pc /
    # bt470bg` fuer den ganzen Film durchgesetzt. Siehe frameforge.color.
    final_video = f"{cur_video}_out"
    filters.append(
        f"[{cur_video}]format=yuv420p,{color_module.output_params_filter()}[{final_video}]"
    )
    graph.video_label = final_video

    graph.audio_label = _build_audio_chain(
        timeline,
        add_input=add_input,
        filters=filters,
        resolve_asset=resolve_asset,
        project_root=project_root,
        loudness_normalize=loudness_normalize,
    )

    graph.filter_complex = ";".join(filters)
    return graph


def _build_audio_chain(
    timeline: Timeline,
    *,
    add_input: Callable[[list[str]], int],
    filters: list[str],
    resolve_asset: Callable[[str], Path],
    project_root: Path,
    loudness_normalize: bool,
) -> str | None:
    """Audio-Spur der Timeline: pro Clip trimmen/verzoegern/Pegel, Musik-Ducking, dann amix.

    Haengt Inputs und Filter-Statements an die uebergebenen Sammler und liefert das Label des
    fertigen Mixes (`None`, wenn die Timeline keine Audio-Clips hat). Eigene Funktion, damit der
    Chunk-Render (`render_final(..., chunk_s=...)`) den Ton in **einem** Durchgang ohne jeden
    Video-Input bauen kann — `loudnorm` je Chunk gaebe an jeder Nahtstelle einen Pegelsprung.
    """
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
            fade = float(getattr(audio, "duck_fade_s", 0.0) or 0.0)
            duck_windows.append((audio.tl_in, audio.tl_in + dur, audio.duck_music_db, fade))

    # Jede Musik-Spur bekommt die gesamte Duck-Kette (nicht nur die erste — Audit K5).
    for m, music_label in enumerate(music_labels):
        current = music_label
        for w, (start, end, duck_db, fade) in enumerate(duck_windows):
            duck_gain = 10 ** (duck_db / 20)
            ducked = f"m{m}_duck{w}"
            if fade > 0:
                # Weiche Rampe statt Hartschalter: Musik faehrt ueber `duck_fade_s` runter,
                # haelt ueber dem O-Ton-Fenster und faehrt genauso weich wieder hoch.
                # Nutzer-Feedback (2026-08-08, Runde 2): "das Absacken vom Sound muss smooth
                # passieren, es muss einen kleinen Mini-Fade geben" -- das harte
                # `enable=between(...)` schaltete den Pegel in einem Frame um und knackte.
                # Aufbau: 1 ausserhalb, `duck_gain` innerhalb, linear dazwischen. Die Rampe
                # liegt VOR `start` bzw. NACH `end`, damit der O-Ton ueber seine ganze Laenge
                # den vollen Platz hat und nicht erst waehrend des Absenkens einsetzt.
                down = f"clip((t-{start - fade:.3f})/{fade:.3f},0,1)"
                up = f"clip(({end + fade:.3f}-t)/{fade:.3f},0,1)"
                filters.append(
                    f"[{current}]volume=eval=frame:"
                    f"volume='1-{1 - duck_gain:.6f}*{down}*{up}'[{ducked}]"
                )
            else:
                filters.append(
                    f"[{current}]volume=volume={duck_gain}:"
                    f"enable='between(t,{start},{end})'[{ducked}]"
                )
            current = ducked
        if current != music_label:
            audio_labels[audio_labels.index(music_label)] = current

    if not audio_labels:
        return None

    mix_inputs = "".join(f"[{lbl}]" for lbl in audio_labels)
    # normalize=0: amix skaliert sonst automatisch mit 1/n und macht die explizit
    # gesetzten gain_db-/Ducking-Werte bedeutungslos (halbierter Pegel bei 2 Spuren).
    # Die absoluten Pegel steuern wir ueber die volume-Gains + loudnorm (Final).
    filters.append(
        f"{mix_inputs}amix=inputs={len(audio_labels)}:normalize=0:"
        f"duration=longest:dropout_transition=0[aout]"
    )
    label = "aout"
    if loudness_normalize:
        filters.append(f"[{label}]loudnorm=I=-16:TP=-1.5:LRA=11[aout_norm]")
        label = "aout_norm"
    return label


# Ab so vielen gleichzeitig offenen Inputs wird die Threadzahl des Filtergraphen gedrosselt
# (siehe `_run_ffmpeg`). Der Chunk-Render haelt die Inputzahl je Aufruf klein (~20-25, siehe
# `CHUNK_EDGE_MARGIN_S`-Block) und bleibt damit unter der Schwelle -- bestehende Final-Renders
# aendern sich nicht. Nur der monolithische Ein-Pass-Graph (Proxy-Preview, oder ein Final ohne
# `chunk_s`) mit hunderten Inputs laeuft in die Drosselung.
_LARGE_GRAPH_INPUT_THRESHOLD = 64
# Slice-Threads je threaded Filter im grossen Graphen. Empirisch (JGA-Preview, 231 Inputs, macOS
# mit `kern.maxprocperuid` = 2666): Default (= CPU-Anzahl) sprengt das Limit, 3 laeuft mit
# komfortablem Abstand durch. Bewusst nicht 1 -- das ist ~3x langsamer, ohne mehr Sicherheit zu
# bringen.
_LARGE_GRAPH_FILTER_THREADS = 3


def _run_ffmpeg(
    graph: FilterGraph,
    timeline: Timeline,
    out_path: Path,
    *,
    crf: int | None = None,
    preset: str | None = None,
    faststart: bool = False,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    for args in graph.input_args:
        cmd.extend(args)
    # Jeder threaded Filter (scale, die auto-eingefuegten Pixelformat-Konvertierungen, zoompan,
    # xfade) legt bis zu `filter_complex_threads` Slice-Threads an -- Default ist die CPU-Anzahl.
    # In einem monolithischen Graphen mit hunderten solcher Filter (JGA-Preview: 201 Video-Clips
    # + 21 RGBA-Overlays) summiert sich das ueber das Prozess-/Thread-Limit pro Nutzer hinaus
    # (macOS `kern.maxprocperuid`, hier 2666, nicht ohne root anhebbar). `sws_init_context`
    # bekommt dann von `pthread_create` EAGAIN und meldet reihenweise "Failed initializing
    # scaling graph (Resource temporarily unavailable)"; der Encoder wird nie geoeffnet, die
    # Ausgabedatei bleibt 0 Byte. Deckeln loest das -- der Render wird langsamer, laeuft aber
    # durch. Kleine Graphen (u.a. jeder Chunk des Chunk-Renders) bleiben unangetastet.
    if len(graph.input_args) > _LARGE_GRAPH_INPUT_THRESHOLD:
        threads = str(_LARGE_GRAPH_FILTER_THREADS)
        cmd.extend(["-filter_complex_threads", threads, "-filter_threads", threads])
    cmd.extend(["-filter_complex", graph.filter_complex, "-map", f"[{graph.video_label}]"])
    if graph.audio_label:
        cmd.extend(["-map", f"[{graph.audio_label}]"])
    cmd.extend(["-r", str(timeline.fps), "-c:v", "libx264", "-pix_fmt", "yuv420p"])
    # Ohne diese Tags schreibt libx264, was die Aushandlung gerade durchreicht. Player, die
    # die Tags befolgen (Chromium), dekodieren sonst mit falscher Matrix im falschen
    # Wertebereich — sichtbar als kraeftiger Rotstich auf Hauttoenen.
    cmd.extend(color_module.OUTPUT_COLOR_ARGS)
    if crf is not None:
        cmd.extend(["-crf", str(crf)])
    if preset is not None:
        cmd.extend(["-preset", preset])
    if faststart:
        cmd.extend(["-movflags", "+faststart"])
    cmd.extend(["-c:a", "aac", "-loglevel", "error", str(out_path)])
    # Grosszuegiges, aber endliches Timeout als Sicherheitsnetz: ein Filtergraph-Fehler
    # (z.B. ein unbegrenzter `-loop 1`-Input ohne `shortest=1` an einem `overlay`) darf den
    # Prozess nicht auf unbestimmte Zeit haengen lassen.
    _run_ffmpeg_cmd(cmd, timeout_s=max(120.0, timeline.duration * 30))


def _run_ffmpeg_cmd(cmd: list[str], *, timeout_s: float) -> None:
    """Fuehrt einen fertig gebauten ffmpeg-Aufruf aus und uebersetzt Fehler in `RenderError`."""
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


def _load_faces_by_asset(project: Project) -> dict[str, list[dict]] | None:
    """Laedt `index/people.json` (Ergebnis von `frameforge faces <projekt>`), falls vorhanden.

    `None`, wenn die Datei fehlt (Gesichtserkennung ist expliziter Opt-in, siehe
    `frameforge.people`-Datenschutzhinweis) — der Foto-Ken-Burns-Zweig faellt dann auf
    zentrierten Crop-to-Fill zurueck, ganz ohne die Datei anzufassen.
    """
    people_path = project.index_dir / "people.json"
    if not people_path.exists():
        return None
    try:
        raw = json.loads(people_path.read_text())
    except (OSError, ValueError):
        return None
    return {
        asset_id: [face["location"] for face in faces if "location" in face]
        for asset_id, faces in raw.items()
    }


PREVIEW_MAX_HEIGHT = 1080


def _preview_resolution(timeline_res: tuple[int, int]) -> tuple[int, int]:
    """Preview-Auflaesung: auf `PREVIEW_MAX_HEIGHT` herunter, Seitenverhaeltnis erhalten.

    Timelines, die schon 1080p oder kleiner sind, bleiben unangetastet. Kantenlaengen werden auf
    gerade Werte gebracht (`libx264`/`yuv420p`).
    """
    w, h = timeline_res
    if h <= PREVIEW_MAX_HEIGHT:
        return w, h
    scale = PREVIEW_MAX_HEIGHT / h
    pw, ph = round(w * scale), PREVIEW_MAX_HEIGHT
    return pw + pw % 2, ph + ph % 2


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

    # 1080p, wie der Name `render_proxy` und `ff-preview` es versprechen -- vorher gab der
    # Preview stillschweigend in `timeline.resolution` aus, beim Norwegen-Projekt also 4K.
    # Das war nicht nur langsam und ~2,5 GB gross, es war der Hauptgrund, warum der Render den
    # Arbeitsspeicher sprengte: jeder Frame in jeder Stufe (Decode, Ken-Burns-Oversampling,
    # Blur-Fill, die Kette aus verschachtelten `xfade`, Encoder) ist in 4K viermal so gross wie
    # in 1080p. Bei 170 Segmenten und 213 gleichzeitig offenen Inputs entscheidet genau das.
    # Damit das stimmt, skaliert `build_filtergraph` die Overlay-PNGs und die Pixelwerte in
    # `anim` mit (die PNGs entstehen in Timeline-Auflaesung).
    preview_res = _preview_resolution(timeline.resolution)
    graph = build_filtergraph(
        timeline,
        resolve_asset=resolve,
        export_root=export.root,
        project_root=project.root,
        resolution=preview_res,
        color_grade=color_grade,
        faces_by_asset=_load_faces_by_asset(project),
    )
    out_path = export.preview_dir / f"{export.name}_preview.mp4"
    # Preview ist zum Sichten, nicht zum Ausliefern: `veryfast` + hoeheres CRF kosten sichtbar
    # nichts fuer die Beurteilung von Schnitt, Reihenfolge und Overlays, sparen aber Laufzeit und
    # Encoder-Speicher. Letzteres zaehlt hier wirklich -- der Render lief in den Swap und starb
    # (siehe `_kenburns_expr` zum Oversampling). Der Final-Render (`render_final`) bleibt
    # unangetastet.
    _run_ffmpeg(graph, timeline, out_path, crf=26, preset="veryfast")
    return out_path


def resolution_label(resolution: tuple[int, int]) -> str:
    """Kurzname einer Ausgabe-Aufloesung: `(3840, 2160)` -> `4k`, `(1920, 1080)` -> `1080p`."""
    width, height = resolution
    if width >= 3840 or height >= 2160:
        return "4k"
    return f"{height}p"


def _final_output_path(directory: Path, stem: str, resolution: tuple[int, int]) -> Path:
    """Ausgabepfad eines Final-Renders: `<stem>_<label>.mp4` (`vlog-edit_1080p.mp4`).

    Die Aufloesung steht im Dateinamen, weil von einem Export mehrere Fassungen nebeneinander
    existieren (4K zum Herunterladen, 1080p zum Streamen) und eine blosse Versionsnummer
    nicht sagt, welche Datei man vor sich hat. Eine Nummer kommt nur dazu, wenn dieselbe
    Fassung ein zweites Mal gerendert wird — dann bleibt die vorhandene Datei unangetastet.
    """
    directory.mkdir(parents=True, exist_ok=True)
    base = directory / f"{stem}_{resolution_label(resolution)}.mp4"
    if not base.exists():
        return base
    n = 2
    while (candidate := base.with_name(f"{base.stem}_v{n}.mp4")).exists():
        n += 1
    return candidate


# -- Chunk-Render: den Film stueckweise rendern und ohne Neukodierung zusammensetzen ------
#
# Warum es das gibt (gemessen 2026-08-09, PROGRESS.md): der Ein-Pass-Graph des Norwegen-Vlogs
# oeffnet 213 Inputs gleichzeitig, jeder ein 4K-Decoder, dazu 169 verschachtelte `xfade`.
# Hochgerechnet ~50 GB RSS auf einer Maschine mit 17,2 GB — ffmpeg landet nach ~40s im Swap und
# kommt nicht mehr voran. Ein echter 4K-Chunk von 103,6s mit 19 Inputs braucht 5,9 GB und laeuft
# sauber durch. Die Zahl gleichzeitig offener Inputs ist also die Stellschraube, nicht die
# Dateigroesse.

CHUNK_EDGE_MARGIN_S = 1.0
"""Sicherheitsabstand einer Chunk-Grenze zu Clipanfang/-ende, Uebergang und Overlay-Fenster."""

_MIN_CUT_WINDOW_S = 0.5  # kuerzere Restfenster in einem Clip taugen nicht als Schnittstelle


def _clip_end(clip) -> float:
    return clip.tl_in + clip.duration


def _transition_span(transition) -> float:
    return 0.0 if transition is None else transition.dur + transition.hold


def cut_windows(timeline: Timeline, *, margin_s: float | None = None) -> list[tuple[float, float]]:
    """Zeitfenster, in denen eine Chunk-Grenze liegen darf — aufsteigend, ueberschneidungsfrei.

    Erlaubt ist nur die **Mitte eines Video-Clips**: nie an einem Uebergang (die Blende ginge
    verloren, weil `xfade`/`fade` je Chunk neu gerechnet werden), nie waehrend eines Overlay-
    oder Karten-Fensters (deren Animation startet im naechsten Chunk sonst von vorn) und nie in
    einem Clip mit Effekten (Ken-Burns wuerde in beiden Haelften neu anfangen).
    """
    margin_s = CHUNK_EDGE_MARGIN_S if margin_s is None else margin_s
    windows: list[tuple[float, float]] = []
    clips = timeline.tracks.video
    for i, clip in enumerate(clips):
        if clip.effects:
            continue
        prev_out = _transition_span(clips[i - 1].transition_out) if i > 0 else 0.0
        next_in = _transition_span(clips[i + 1].transition_in) if i + 1 < len(clips) else 0.0
        head = margin_s + max(_transition_span(clip.transition_in), prev_out)
        tail = margin_s + max(_transition_span(clip.transition_out), next_in)
        lo, hi = clip.tl_in + head, _clip_end(clip) - tail
        if hi - lo >= _MIN_CUT_WINDOW_S:
            windows.append((lo, hi))

    blocked = [
        (c.tl_in - margin_s, c.tl_in + c.dur + margin_s)
        for c in (*timeline.tracks.overlay, *timeline.tracks.map)
    ]
    for b_lo, b_hi in blocked:
        remaining: list[tuple[float, float]] = []
        for lo, hi in windows:
            if b_hi <= lo or b_lo >= hi:
                remaining.append((lo, hi))
                continue
            if lo < b_lo and b_lo - lo >= _MIN_CUT_WINDOW_S:
                remaining.append((lo, b_lo))
            if hi > b_hi and hi - b_hi >= _MIN_CUT_WINDOW_S:
                remaining.append((b_hi, hi))
        windows = remaining
    return sorted(windows)


def chunk_boundaries(
    timeline: Timeline, chunk_s: float, *, margin_s: float | None = None
) -> list[float]:
    """Innere Schnittzeitpunkte fuer den Chunk-Render (ohne 0 und ohne `timeline.duration`).

    Zielt auf gleich lange Stuecke von ~`chunk_s` und verschiebt jede Grenze auf den naechsten
    zulaessigen Punkt aus `cut_windows`. Findet sich fuer eine Zielmarke keiner, waechst der
    Chunk — das kostet Speicher, ist aber immer noch korrekt. Ohne **jede** zulaessige Grenze
    ist der Chunk-Render nicht moeglich: `RenderError`.
    """
    if chunk_s <= 0:
        raise RenderError("chunk_s muss groesser als 0 sein")
    if timeline.duration <= chunk_s:
        return []
    windows = cut_windows(timeline, margin_s=margin_s)
    if not windows:
        raise RenderError(
            "Kein zulaessiger Chunk-Schnittpunkt gefunden (jeder Clip traegt Effekte, ist zu "
            "kurz oder liegt unter einem Overlay) — Chunk-Render nicht moeglich"
        )

    n = max(2, round(timeline.duration / chunk_s))
    step = timeline.duration / n
    boundaries: list[float] = []
    for k in range(1, n):
        target = k * step
        best = min(
            (max(lo, min(hi, target)) for lo, hi in windows),
            key=lambda t: abs(t - target),
        )
        # Streng monoton und keine Mini-Chunks: eine Grenze, die praktisch auf der vorigen
        # liegt, bringt nichts ausser einer zusaetzlichen Nahtstelle.
        if boundaries and best - boundaries[-1] < _MIN_CUT_WINDOW_S:
            continue
        if timeline.duration - best < _MIN_CUT_WINDOW_S:
            continue
        boundaries.append(best)
    if not boundaries:
        raise RenderError(
            "Kein zulaessiger Chunk-Schnittpunkt gefunden (jeder Clip traegt Effekte, ist zu "
            "kurz oder liegt unter einem Overlay) — Chunk-Render nicht moeglich"
        )
    return boundaries


def slice_timeline(timeline: Timeline, start: float, end: float, *, with_audio: bool = False) -> Timeline:
    """Schneidet `[start, end)` als eigenstaendige Timeline heraus, auf `tl_in = 0` geschoben.

    Video-Clips an den Raendern werden ueber `src_in`/`src_out` getrimmt (mit `speed` gerechnet);
    ihr `transition_in`/`transition_out` faellt dabei weg, weil ein angeschnittener Clip weder
    ein- noch ausblenden darf — die Blende gehoert dem Nachbarchunk. Overlays und Karten muessen
    **ganz** im Fenster liegen (`chunk_boundaries` sorgt dafuer), sonst `RenderError`.

    `with_audio=False` (Default) laesst die Tonspur weg: sie wird im Chunk-Render in einem
    einzigen eigenen Durchgang gebaut, damit `loudnorm` einmal ueber den ganzen Film rechnet.
    """
    eps = 1e-6
    if end - start <= eps:
        raise RenderError(f"Leerer Timeline-Ausschnitt [{start:.3f}, {end:.3f}]")

    video = []
    for clip in timeline.tracks.video:
        if _clip_end(clip) <= start + eps or clip.tl_in >= end - eps:
            continue
        cut = clip.model_copy(deep=True)
        if clip.tl_in < start - eps:
            cut.src_in = clip.src_in + (start - clip.tl_in) * clip.speed
            cut.tl_in = start
            cut.transition_in = None
        if _clip_end(clip) > end + eps:
            cut.src_out = clip.src_out - (_clip_end(clip) - end) * clip.speed
            cut.transition_out = None
        cut.tl_in -= start
        video.append(cut)
    if not video:
        raise RenderError(f"Timeline-Ausschnitt [{start:.3f}, {end:.3f}] enthaelt keine Video-Clips")

    def shifted_windowed(items, kind: str):
        out = []
        for item in items:
            item_end = item.tl_in + item.dur
            if item_end <= start + eps or item.tl_in >= end - eps:
                continue
            if item.tl_in < start - eps or item_end > end + eps:
                raise RenderError(
                    f"{kind} '{item.id}' ({item.tl_in:.2f}-{item_end:.2f}s) wird von der "
                    f"Chunk-Grenze [{start:.2f}, {end:.2f}] zerschnitten"
                )
            copy = item.model_copy(deep=True)
            copy.tl_in -= start
            out.append(copy)
        return out

    tracks = timeline.tracks.model_copy(deep=True)
    tracks.video = video
    tracks.overlay = shifted_windowed(timeline.tracks.overlay, "Overlay")
    tracks.map = shifted_windowed(timeline.tracks.map, "Karten-Clip")
    tracks.audio = shifted_windowed(timeline.tracks.audio, "Audio-Clip") if with_audio else []

    sub = timeline.model_copy(deep=True)
    sub.tracks = tracks
    sub.duration = end - start
    sub.validate_semantics()
    return sub


def build_audio_filtergraph(
    timeline: Timeline,
    *,
    resolve_asset: Callable[[str], Path],
    project_root: Path,
    loudness_normalize: bool = True,
) -> FilterGraph | None:
    """Nur die Tonspur der Timeline als Filtergraph — `None`, wenn die Timeline keinen Ton hat.

    Der Chunk-Render braucht den Ton in einem einzigen Durchgang (wenige Inputs, kostet fast
    nichts), damit `loudnorm` einmal ueber den ganzen Film rechnet statt je Chunk anders.
    """
    graph = FilterGraph()
    filters: list[str] = []

    def add_input(args: list[str]) -> int:
        graph.input_args.append(args)
        return len(graph.input_args) - 1

    label = _build_audio_chain(
        timeline,
        add_input=add_input,
        filters=filters,
        resolve_asset=resolve_asset,
        project_root=project_root,
        loudness_normalize=loudness_normalize,
    )
    if label is None:
        return None
    graph.audio_label = label
    graph.filter_complex = ";".join(filters)
    return graph


def _render_audio_only(graph: FilterGraph, timeline: Timeline, out_path: Path) -> None:
    cmd = ["ffmpeg", "-y"]
    for args in graph.input_args:
        cmd.extend(args)
    cmd.extend(
        [
            "-filter_complex", graph.filter_complex,
            "-map", f"[{graph.audio_label}]",
            "-vn", "-c:a", "aac", "-b:a", "320k",
            "-loglevel", "error", str(out_path),
        ]
    )
    _run_ffmpeg_cmd(cmd, timeout_s=max(120.0, timeline.duration * 10))


def _is_complete_chunk(path: Path, expected_s: float, *, tol_s: float = 0.5) -> bool:
    """Ist `path` ein fertig gerenderter Chunk der erwarteten Laenge?

    Eine abgebrochene ffmpeg-Ausgabe ist entweder 0 Bytes gross oder zu kurz — beides faellt
    hier durch, und der Chunk wird neu gerendert. Nicht lesbar = nicht brauchbar.
    """
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        from frameforge.probe import probe_duration

        return abs(probe_duration(path) - expected_s) <= tol_s
    except Exception:  # noqa: BLE001 — kaputte/halbe Datei: neu rendern, nicht abbrechen
        return False


def _concat_chunks(
    chunks: list[Path], out_path: Path, *, total_duration: float, faststart: bool = False
) -> None:
    """Fuegt die Chunk-Dateien per concat-Demuxer zusammen — **ohne Neukodierung** (`-c copy`).

    Setzt voraus, dass alle Chunks mit identischen Encoder-Settings entstanden sind (tun sie,
    sie kommen aus demselben `_run_ffmpeg`-Aufruf mit denselben Parametern).
    """
    list_path = out_path.parent / "chunks.txt"
    list_path.write_text("".join(f"file '{c.resolve()}'\n" for c in chunks))
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-c", "copy",
    ]
    if faststart:
        cmd.extend(["-movflags", "+faststart"])
    cmd.extend(["-loglevel", "error", str(out_path)])
    _run_ffmpeg_cmd(cmd, timeout_s=max(120.0, total_duration * 2))


def _mux(video_path: Path, audio_path: Path, out_path: Path, *, total_duration: float) -> None:
    """Legt die fertige Tonspur auf das zusammengesetzte Video — beides `-c copy`.

    **Kein `-shortest`:** ist der Ton kuerzer als der Film (Musik laeuft aus, letzter O-Ton
    endet vor dem Schlussbild), wuerde er sonst das Bild kappen. Das Bild gibt die Laenge vor.
    """
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path), "-i", str(audio_path),
        "-map", "0:v:0", "-map", "1:a:0", "-c", "copy",
        # Web-Auslieferung: moov-Atom nach vorn, sonst muss ein Browser die komplette Datei
        # laden, bevor er das erste Bild zeigt (bei mehreren GB heisst das: gar nichts).
        "-movflags", "+faststart",
        "-loglevel", "error", str(out_path),
    ]
    _run_ffmpeg_cmd(cmd, timeout_s=max(120.0, total_duration * 2))


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
    chunk_s: float | None = None,
    on_progress: Callable[[str], None] | None = None,
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

    `chunk_s`: Chunk-Render statt Ein-Pass-Graph — der Film wird in Stücke von ~`chunk_s`
    Sekunden zerlegt, jedes einzeln gerendert (nur seine eigenen Inputs offen), die Stücke per
    concat-Demuxer **ohne Neukodierung** zusammengefügt und der separat gerenderte Ton
    dazugemuxt. Nötig ab dem Punkt, an dem die Zahl gleichzeitig offener Decoder den
    Arbeitsspeicher sprengt (siehe Kommentar bei `CHUNK_EDGE_MARGIN_S`). `on_progress` bekommt
    dabei je Schritt eine kurze Statuszeile.
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

    out_path = _final_output_path(export.final_dir, export.name, resolution or timeline.resolution)
    faces = _load_faces_by_asset(project)

    if chunk_s is not None:
        _render_final_chunked(
            project, export, timeline, out_path,
            resolve=resolve, faces=faces, chunk_s=chunk_s, lut_path=lut_path,
            resolution=resolution, crf=crf, preset=preset, color_grade=color_grade,
            on_progress=on_progress,
        )
        return out_path

    graph = build_filtergraph(
        timeline,
        resolve_asset=resolve,
        export_root=export.root,
        project_root=project.root,
        lut_path=lut_path,
        loudness_normalize=True,
        resolution=resolution,
        color_grade=color_grade,
        faces_by_asset=faces,
    )
    _run_ffmpeg(graph, timeline, out_path, crf=crf, preset=preset, faststart=True)
    return out_path


def _render_final_chunked(
    project: Project,
    export: Export,
    timeline: Timeline,
    out_path: Path,
    *,
    resolve: Callable[[str], Path],
    faces: dict[str, list[dict]] | None,
    chunk_s: float,
    lut_path: Path | None,
    resolution: tuple[int, int] | None,
    crf: int,
    preset: str,
    color_grade: dict | None,
    on_progress: Callable[[str], None] | None,
) -> None:
    """Video stueckweise rendern, ohne Neukodierung zusammensetzen, Ton in einem Pass dazu.

    Reihenfolge und Begruendung stehen in `render_final` bzw. am `CHUNK_EDGE_MARGIN_S`-Block.

    **Fortsetzbar:** Die Zwischendateien liegen in `final/.<export>_chunks/` (bewusst ohne
    Versionsnummer im Namen, sonst faende ein zweiter Lauf sie nicht). Bricht der Lauf ab —
    Absturz, Neustart, abgewuergter Hintergrundprozess —, uebernimmt der naechste Aufruf jeden
    Chunk, der schon fertig **und** in der richtigen Laenge da ist. Beim Norwegen-Vlog haengen
    an jedem Chunk ~8 Minuten Rechenzeit; die noch einmal zu zahlen, weil ein Prozess nach
    50 Minuten gestoppt wurde, waere die teuerste Art von Sauberkeit. Nach Erfolg wird das
    Verzeichnis geloescht — bleibt es liegen, ist der Lauf gescheitert.

    Uebernommen wird nur bei **identischen Parametern**: `params.json` haelt Schnittpunkte,
    CRF, Preset, Aufloesung, LUT und Grade fest. Weicht etwas ab, faengt der Lauf von vorn an,
    damit nicht Stuecke unterschiedlicher Qualitaet aneinandergeklebt werden.
    """
    def report(msg: str) -> None:
        if on_progress is not None:
            on_progress(msg)

    cuts = chunk_boundaries(timeline, chunk_s)
    edges = [0.0, *cuts, timeline.duration]
    work_dir = out_path.parent / f".{export.name}_chunks"
    params = {
        "cuts": [round(c, 3) for c in cuts],
        "duration": round(timeline.duration, 3),
        "crf": crf,
        "preset": preset,
        "resolution": list(resolution) if resolution else None,
        "lut": str(lut_path) if lut_path else None,
        "color_grade": color_grade,
    }
    params_path = work_dir / "params.json"
    if work_dir.exists():
        try:
            reusable = json.loads(params_path.read_text()) == params
        except (OSError, ValueError):
            reusable = False
        if not reusable:
            report("Vorhandene Chunks passen nicht zu diesen Parametern — wird neu gerendert")
            shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    params_path.write_text(json.dumps(params, indent=2))

    chunk_paths: list[Path] = []
    for i, (start, end) in enumerate(itertools.pairwise(edges)):
        chunk_path = work_dir / f"chunk_{i:03d}.mp4"
        if _is_complete_chunk(chunk_path, end - start):
            report(f"Chunk {i + 1}/{len(edges) - 1}: bereits gerendert, uebernommen")
            chunk_paths.append(chunk_path)
            continue
        sub = slice_timeline(timeline, start, end)
        graph = build_filtergraph(
            sub,
            resolve_asset=resolve,
            export_root=export.root,
            project_root=project.root,
            lut_path=lut_path,
            loudness_normalize=False,
            resolution=resolution,
            color_grade=color_grade,
            faces_by_asset=faces,
        )
        report(
            f"Chunk {i + 1}/{len(edges) - 1}: {start:.1f}-{end:.1f}s, "
            f"{len(graph.input_args)} Inputs"
        )
        _run_ffmpeg(graph, sub, chunk_path, crf=crf, preset=preset)
        chunk_paths.append(chunk_path)

    video_path = work_dir / "video.mp4"
    report(f"Fuege {len(chunk_paths)} Chunks zusammen (ohne Neukodierung)")
    _concat_chunks(chunk_paths, video_path, total_duration=timeline.duration, faststart=True)
    # Chunks sofort weg: sonst liegen Chunks + zusammengesetztes Video + fertige Datei
    # gleichzeitig auf der Platte — beim Norwegen-Vlog dreimal ~9 GB, mehr als frei ist.
    for chunk in chunk_paths:
        chunk.unlink(missing_ok=True)

    audio_graph = build_audio_filtergraph(
        timeline, resolve_asset=resolve, project_root=project.root, loudness_normalize=True
    )
    if audio_graph is None:
        video_path.replace(out_path)
    else:
        audio_path = work_dir / "audio.m4a"
        report(f"Ton in einem Durchgang ({len(audio_graph.input_args)} Inputs, loudnorm)")
        _render_audio_only(audio_graph, timeline, audio_path)
        _mux(video_path, audio_path, out_path, total_duration=timeline.duration)

    shutil.rmtree(work_dir, ignore_errors=True)
