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

from frameforge import render as render_module
from frameforge.render import _CROSSFADE_TYPES
from frameforge.timeline import Timeline, TimelineValidationError

MIN_OVERLAY_READABLE_S = 1.2
MAX_ASSET_REPEATS = 2
DURATION_TOLERANCE_S = 2.0
# Toleranz beim Abgleich Crossfade-Dauer <-> tl_in-Überlappung (Rundung/fps-Raster).
_XFADE_OVERLAP_TOLERANCE_S = 0.05
# Toleranz zwischen sequenzieller Renderlaenge und den tl_in-Positionen der Video-Spur.
# Grosszuegiger als die Crossfade-Toleranz, weil sich Rundungen ueber viele Clips summieren
# duerfen; ab einer halben Sekunde ist die Verschiebung im Bild sichtbar.
DURATION_MISMATCH_TOLERANCE_S = 0.5


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
    for i, clip in enumerate(clips):
        # Schwarzblende (Plan 0003 §C): der Renderer haengt `dur`-Ausblendung + `hold`
        # Standzeit an, der Folgeclip beginnt also SPAETER. Die Luecke ist hier also korrekt
        # und muss exakt der Standzeit entsprechen — sonst laufen Audio/Overlays weg.
        if (
            i > 0
            and clip.transition_in
            and clip.transition_in.type == render_module.BLACK_TRANSITION
        ):
            expected = prev_end + clip.transition_in.hold
            if abs(clip.tl_in - expected) > _XFADE_OVERLAP_TOLERANCE_S:
                issues.append(
                    f"Clip '{clip.id}' hat eine Schwarzblende mit {clip.transition_in.hold:.2f}s "
                    f"Standzeit, muesste also bei {expected:.2f}s beginnen, beginnt aber bei "
                    f"{clip.tl_in:.2f}s — Bild laeuft gegen Ton/Overlays"
                )
            prev_end = max(prev_end, clip.tl_in + clip.duration)
            continue

        # transition_in am ERSTEN Clip meint "Fade aus Schwarz", nicht Crossfade vom Vorgänger.
        xfade = (
            clip.transition_in.dur
            if i > 0 and clip.transition_in and clip.transition_in.type in _CROSSFADE_TYPES
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


def _check_video_length_consistency(timeline: Timeline) -> list[str]:
    """Sequenzielle Renderlänge der Video-Spur muss zu den `tl_in`-Positionen passen.

    Der Renderer schneidet die Video-Clips **sequenziell** aneinander: Summe der Clipdauern,
    minus Crossfades (`xfade` verkürzt), plus Schwarzblenden-Standzeiten (`tpad` verlängert).
    Audio (`adelay`), Overlays und Karten-Clips liegen dagegen an ihren **absoluten**
    `tl_in`-Positionen. Beide Modelle stimmen nur überein, wenn die sequenzielle Länge genau
    dort endet, wo der letzte Clip laut `tl_in` endet.

    Die Einzelprüfungen in `_check_video_coverage` decken jeden Übergang für sich ab; diese
    Regel ist die Gesamtsumme — sie fängt auch eine Kombination aus mehreren Übergangstypen,
    bei der sich Einzelabweichungen unterhalb der Toleranz aufaddieren (Plan 0003 §C:
    „Gesamtdauer stimmt mit `timeline.duration` überein").

    **Nicht** geprüft wird, ob `timeline.duration` größer ist als das letzte Bild: ein
    Musik-Ausklang oder eine Abspann-Fläche nach dem letzten Clip ist zulässig (der Render ist
    dann so lang wie die Audio-Spur, empirisch geprüft). Zu *kurz* deklarierte Dauern fängt
    bereits `Timeline.validate_semantics`.
    """
    clips = sorted(timeline.tracks.video, key=lambda c: c.tl_in)
    if not clips:
        return []

    crossfades = sum(
        min(c.transition_in.dur, c.duration)
        for c in clips[1:]
        if c.transition_in and c.transition_in.type in _CROSSFADE_TYPES
    )
    holds = render_module.black_transition_extra_s(clips)
    sequential = sum(c.duration for c in clips) - crossfades + holds
    positioned = max(c.tl_in + c.duration for c in clips)

    if abs(sequential - positioned) > DURATION_MISMATCH_TOLERANCE_S:
        message = (
            f"Video-Spur: der Renderer erzeugt {sequential:.2f}s (Clips "
            f"{sum(c.duration for c in clips):.2f}s − Crossfades {crossfades:.2f}s + "
            f"Schwarzblenden {holds:.2f}s), laut tl_in endet das Bild aber bei "
            f"{positioned:.2f}s — Audio und Overlays laufen um die Differenz gegen das Bild"
        )
        return [message]
    return []


def _check_audio_clipping_risk(timeline: Timeline) -> list[str]:
    """Positiver Gain ist ein Clipping-Risiko — die Pipeline soll nur abschwächen, nie verstärken.

    Ausnahme mit Nachweis: traegt der Clip `gain_verified: true` (erlaubt durch `extra="allow"`
    im Schema, gleiche Bauart wie `intentional_repeat` bei den Videoclips), gilt die Anhebung
    als am fertigen Ton geprueft und wird nicht gemeldet. Gebraucht fuer O-Ton-Betten, die von
    Haus aus sehr leise aufgenommen sind — das Meeresrauschen am Schluss von `vlog-edit` liegt
    bei -34 dBFS RMS und waere ohne Anhebung schlicht nicht hoerbar. Die Regel bleibt der
    Default; wer sie umgeht, muss den Spitzenpegel gemessen haben und das in der `note`
    festhalten.
    """
    return [
        f"Audio-Clip '{clip.id}' hat positiven Gain ({clip.gain_db:+.1f} dB) — Clipping-Risiko"
        for clip in timeline.tracks.audio
        if clip.gain_db is not None
        and clip.gain_db > 0
        and not getattr(clip, "gain_verified", False)
    ]


def _check_overlay_readability(timeline: Timeline) -> list[str]:
    return [
        f"Overlay '{clip.id}' ist nur {clip.dur:.2f}s sichtbar "
        f"(< {MIN_OVERLAY_READABLE_S}s gilt als kaum lesbar)"
        for clip in timeline.tracks.overlay
        if clip.dur < MIN_OVERLAY_READABLE_S
    ]


def _check_clip_repetition(timeline: Timeline) -> list[str]:
    """Mehr als `MAX_ASSET_REPEATS` Verwendungen desselben Assets sind meist ein Versehen —
    ausser der Timeline-Builder markiert jede Verwendung explizit als beabsichtigt (z.B. ein
    einzelner langer Quellclip, der fuer einen Klimax-Beat in mehrere Sub-Segmente zerlegt
    wird). Dafuer traegt jeder betroffene `VideoClip` das Zusatzfeld `intentional_repeat: true`
    (erlaubt durch `extra="allow"` im Schema) plus idealerweise eine `note` mit Begruendung.
    Nur wenn *alle* Verwendungen eines Assets so markiert sind, wird die Wiederholung nicht als
    Fehler gemeldet.
    """
    clips_by_asset: dict[str, list] = {}
    for clip in timeline.tracks.video:
        clips_by_asset.setdefault(clip.asset, []).append(clip)

    issues = []
    for asset_id, clips in clips_by_asset.items():
        if len(clips) <= MAX_ASSET_REPEATS:
            continue
        if all(getattr(clip, "intentional_repeat", False) for clip in clips):
            continue
        issues.append(
            f"Asset '{asset_id}' wird {len(clips)}x in der Timeline verwendet "
            f"(> {MAX_ASSET_REPEATS}) — ggf. unbeabsichtigte Wiederholung"
        )
    return issues


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


def _check_source_windows(timeline: Timeline, durations: dict[str, float]) -> list[str]:
    """`src_out` darf die Laufzeit des Quellclips nicht ueberschreiten.

    Das ist keine Kosmetik: laeuft ein Clip mitten im Film aus, endet der **gesamte** Video-Pfad
    dort. Gefunden 2026-08-09 — ein Titelbett verlangte 24s aus einer 18,7s-Datei, und der
    fertige Preview war 26,7s lang statt 18 Minuten. Ohne Ton- oder Fehlermeldung: die
    Ausgabedatei war formal gueltig, nur der Film fehlte. Genau die Klasse Fehler, die eine
    QC-Stufe abfangen muss, weil sie im Render nicht auffaellt.

    Fotos sind ausgenommen (`-loop 1` liefert beliebig lange). Assets ohne bekannte Laufzeit
    werden uebersprungen, nicht gemeldet.
    """
    issues = []
    for clip in timeline.tracks.video:
        src_dur = durations.get(clip.asset)
        if src_dur is None:
            continue
        # Toleranz von einem halben Frame gegen Rundungsdifferenzen.
        if clip.src_out > src_dur + 0.05:
            issues.append(
                f"Clip '{clip.id}' ({clip.asset}) verlangt Quelle bis {clip.src_out:.2f}s, "
                f"der Clip ist aber nur {src_dur:.2f}s lang — der Video-Pfad endet dort und "
                f"der Rest des Films fehlt"
            )
    return issues


def _check_music_coverage(timeline: Timeline, durations: dict[str, float]) -> list[str]:
    """Ein Musiktrack darf nicht mehr Sekunden liefern muessen, als die Datei lang ist.

    Gegenstueck zu `_check_source_windows` fuer die Tonspur, und derselbe Fehlermodus: es gibt
    keine Fehlermeldung, der Ton hoert einfach auf. Gefunden 2026-08-09 am `vlog-edit`-Preview
    — der letzte Titel war ab `src_in` 373,96s lang, die Timeline verlangte 385,35s, also lief
    der Film **11,4 Sekunden stumm** zu Ende. Aufgefallen ist es dem Nutzer beim Zusehen, keiner
    Pruefung.

    Zusaetzlich: endet der letzte Musikclip mehr als eine Sekunde vor der Timeline, ist das
    ebenfalls Stille am Schluss — dann fehlt schlicht Musik, unabhaengig von der Dateilaenge.
    """
    issues = []
    music = [clip for clip in timeline.tracks.audio if getattr(clip, "src", None)]
    for clip in music:
        src_dur = durations.get(str(clip.src))
        if src_dur is None:
            continue
        needed = float(clip.src_in or 0.0) + float(clip.dur)
        if needed > src_dur + 0.05:
            issues.append(
                f"Musik '{clip.id}' verlangt {needed:.2f}s aus einer {src_dur:.2f}s langen "
                f"Datei — die letzten {needed - src_dur:.2f}s laufen stumm"
            )
    if music:
        last_end = max(float(c.tl_in) + float(c.dur) for c in music)
        if last_end < timeline.duration - 1.0:
            issues.append(
                f"Musik endet bei {last_end:.2f}s, der Film laeuft bis {timeline.duration:.2f}s "
                f"— {timeline.duration - last_end:.2f}s Stille am Schluss"
            )
    return issues


def validate(
    timeline: Timeline,
    *,
    brief: dict | None = None,
    known_asset_ids: set[str] | None = None,
    asset_durations: dict[str, float] | None = None,
    music_durations: dict[str, float] | None = None,
) -> list[str]:
    """Liste gefundener Probleme; leer heisst "besteht die Pruefung".

    `brief` ist optional (z.B. aus `yaml.safe_load(export.brief_path.read_text())`) —
    ohne Brief werden nur die timeline-internen Regeln geprüft. `known_asset_ids` (z.B. die
    IDs aus `assets.json`) aktiviert die Pruefung, dass alle referenzierten Assets existieren.
    `asset_durations` (`{asset_id: Laufzeit in s}`, z.B. aus `probe.dur` in `assets.json`)
    aktiviert die Pruefung der Quell-Fenster — ohne die kann ein zu langes `src_out` den ganzen
    Film abschneiden, ohne dass der Render meckert. `music_durations` (`{src-Pfad: Laufzeit}`,
    z.B. aus `probe.probe_duration`) aktiviert dasselbe fuer die Musikspur.
    """
    try:
        timeline.validate_semantics()
    except TimelineValidationError as exc:
        return [str(exc)]

    issues = [
        *_check_video_coverage(timeline),
        *_check_video_length_consistency(timeline),
        *_check_audio_clipping_risk(timeline),
        *_check_overlay_readability(timeline),
        *_check_clip_repetition(timeline),
    ]
    if known_asset_ids is not None:
        issues.extend(_check_known_assets(timeline, known_asset_ids))
    if asset_durations is not None:
        issues.extend(_check_source_windows(timeline, asset_durations))
    if music_durations is not None:
        issues.extend(_check_music_coverage(timeline, music_durations))
    if brief is not None:
        issues.extend(_check_against_brief(timeline, brief))
    return issues
