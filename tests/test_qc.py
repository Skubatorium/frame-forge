"""Tests fuer das QC-Regelwerk (Plan §5): Schema, Video-Lücken/Überlappungen,

Audio-Clipping-Risiko, Overlay-Lesbarkeit, Clip-Wiederholung, Brief-Abgleich.
"""

from __future__ import annotations

from frameforge.qc import _check_video_length_consistency, validate
from frameforge.timeline import Timeline


def _timeline(**tracks) -> Timeline:
    return Timeline(export="teaser", fps=25, resolution=(1920, 1080), duration=10.0, tracks=tracks)


def test_validate_returns_empty_for_valid_timeline():
    tl = Timeline(
        export="teaser-90s",
        fps=25,
        resolution=(3840, 2160),
        duration=10.0,
        tracks={"video": [{"id": "c001", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}]},
    )
    assert validate(tl) == []


def test_validate_reports_clip_exceeding_duration():
    tl = Timeline(
        export="teaser-90s",
        fps=25,
        resolution=(3840, 2160),
        duration=3.0,
        tracks={"video": [{"id": "c001", "asset": "a1", "src_in": 0, "src_out": 8, "tl_in": 0}]},
    )
    issues = validate(tl)
    assert len(issues) == 1
    assert "c001" in issues[0]


# -- Video-Lücken/Überlappungen ------------------------------------------


def test_validate_reports_gap_between_clips():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 2, "tl_in": 5},
        ]
    )
    issues = validate(tl)
    assert any("Lücke" in i for i in issues)


def test_validate_reports_overlapping_clips():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 3, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 2, "tl_in": 1},
        ]
    )
    issues = validate(tl)
    assert any("überlappt" in i for i in issues)


def test_validate_accepts_contiguous_clips():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 3, "tl_in": 0},
            {"id": "c2", "asset": "a2", "src_in": 0, "src_out": 3, "tl_in": 3},
        ]
    )
    assert validate(tl) == []


# -- Crossfade-Timing: tl_in muss um die Crossfade-Dauer überlappen ----------


def test_validate_accepts_crossfade_with_matching_overlap():
    # c1 endet bei 3.0, c2 hat 1.0s Crossfade und startet bei 2.0 (Überlappung = 1.0).
    tl = _timeline(
        duration=5.0,
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 3, "tl_in": 0},
            {
                "id": "c2",
                "asset": "a2",
                "src_in": 0,
                "src_out": 3,
                "tl_in": 2,
                "transition_in": {"type": "dissolve", "dur": 1.0},
            },
        ],
    )
    assert validate(tl) == []


def test_validate_flags_crossfade_without_overlap_desync():
    # Crossfade, aber tl_in hart am Ende (keine Überlappung) -> Bild/Ton-Desync.
    tl = _timeline(
        duration=6.0,
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 3, "tl_in": 0},
            {
                "id": "c2",
                "asset": "a2",
                "src_in": 0,
                "src_out": 3,
                "tl_in": 3,
                "transition_in": {"type": "fade", "dur": 1.0},
            },
        ],
    )
    issues = validate(tl)
    assert any("Crossfade" in i and "c2" in i for i in issues)


def test_validate_flags_crossfade_overlap_larger_than_duration():
    tl = _timeline(
        duration=5.0,
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 3, "tl_in": 0},
            {
                "id": "c2",
                "asset": "a2",
                "src_in": 0,
                "src_out": 3,
                "tl_in": 0.5,
                "transition_in": {"type": "fade", "dur": 1.0},
            },
        ],
    )
    issues = validate(tl)
    assert any("mehr als" in i and "c2" in i for i in issues)


# -- Audio-Clipping-Risiko -------------------------------------------------


def test_validate_flags_positive_audio_gain():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        audio=[{"id": "au1", "src": "music/x.wav", "tl_in": 0, "gain_db": 3.0}],
    )
    issues = validate(tl)
    assert any("Clipping" in i for i in issues)


def test_validate_accepts_negative_or_missing_gain():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        audio=[
            {"id": "au1", "src": "music/x.wav", "tl_in": 0, "gain_db": -6.0},
            {"id": "au2", "src": "music/y.wav", "tl_in": 0},
        ],
    )
    assert validate(tl) == []


# -- Overlay-Lesbarkeit -----------------------------------------------------


def test_validate_flags_overlay_too_short_to_read():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        overlay=[{"id": "o1", "png": "title.png", "tl_in": 0, "dur": 0.4}],
    )
    issues = validate(tl)
    assert any("lesbar" in i for i in issues)


def test_validate_accepts_long_enough_overlay():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        overlay=[{"id": "o1", "png": "title.png", "tl_in": 0, "dur": 2.0}],
    )
    assert validate(tl) == []


# -- Clip-Wiederholung -------------------------------------------------------


def test_validate_flags_excessive_repetition():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 1, "tl_in": 0},
            {"id": "c2", "asset": "a1", "src_in": 1, "src_out": 2, "tl_in": 1},
            {"id": "c3", "asset": "a1", "src_in": 2, "src_out": 3, "tl_in": 2},
        ]
    )
    issues = validate(tl)
    assert any("a1" in i and "3x" in i for i in issues)


def test_validate_accepts_repetition_within_limit():
    tl = _timeline(
        video=[
            {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 1, "tl_in": 0},
            {"id": "c2", "asset": "a1", "src_in": 1, "src_out": 2, "tl_in": 1},
        ]
    )
    assert validate(tl) == []


# -- Brief-Abgleich -----------------------------------------------------------


def test_validate_without_brief_skips_brief_checks():
    tl = _timeline(video=[{"id": "c1", "asset": "forbidden", "src_in": 0, "src_out": 5, "tl_in": 0}])
    assert validate(tl, brief=None) == []


def test_validate_flags_duration_mismatch_against_brief():
    tl = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}])
    issues = validate(tl, brief={"target_duration_s": 60})
    assert any("Ziellänge" in i for i in issues)


def test_validate_flags_forbidden_shot():
    tl = _timeline(video=[{"id": "c1", "asset": "banned", "src_in": 0, "src_out": 5, "tl_in": 0}])
    issues = validate(tl, brief={"forbidden_shots": ["banned"]})
    assert any("Verbotenes Asset 'banned'" in i for i in issues)


def test_validate_flags_missing_must_shot():
    tl = _timeline(video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}])
    issues = validate(tl, brief={"must_shots": ["hero-shot"]})
    assert any("Muss-Shot 'hero-shot'" in i for i in issues)


def test_validate_passes_matching_brief():
    tl = _timeline(video=[{"id": "hero-shot", "asset": "hero-shot", "src_in": 0, "src_out": 10, "tl_in": 0}])
    issues = validate(
        tl,
        brief={"target_duration_s": 10, "must_shots": ["hero-shot"], "forbidden_shots": ["other"]},
    )
    assert issues == []


# -- K6: Asset-Existenz gegen assets.json -------------------------------------


def test_validate_flags_unknown_asset_id():
    tl = _timeline(video=[{"id": "c1", "asset": "fehlt", "src_in": 0, "src_out": 5, "tl_in": 0}])
    issues = validate(tl, known_asset_ids={"vorhanden"})
    assert any("fehlt" in i and "assets.json" in i for i in issues)


def test_validate_passes_when_all_assets_known():
    tl = _timeline(
        video=[{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 5, "tl_in": 0}],
        audio=[{"id": "au1", "asset": "a1", "type": "original", "tl_in": 0, "dur": 5}],
    )
    assert validate(tl, known_asset_ids={"a1"}) == []


def test_validate_without_known_asset_ids_skips_existence_check():
    tl = _timeline(video=[{"id": "c1", "asset": "irgendwas", "src_in": 0, "src_out": 5, "tl_in": 0}])
    assert validate(tl) == []


# -- C: Schwarzblende (Plan 0003) ---------------------------------------------------


def _black_tl(tl_in_second: float, hold: float = 1.0):
    return Timeline(
        export="e",
        fps=25,
        resolution=(320, 240),
        duration=2.0 + hold,
        tracks={
            "video": [
                {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 1.0, "tl_in": 0},
                {
                    "id": "c2",
                    "asset": "a2",
                    "src_in": 0,
                    "src_out": 1.0,
                    "tl_in": tl_in_second,
                    "transition_in": {"type": "black", "dur": 0.4, "hold": hold},
                },
            ]
        },
    )


def test_black_transition_timing_is_accepted_when_hold_is_respected():
    # Schwarzblende verlaengert: Folgeclip beginnt um die Standzeit spaeter.
    assert validate(_black_tl(2.0, hold=1.0)) == []


def test_black_transition_without_the_hold_gap_is_flagged():
    issues = validate(_black_tl(1.0, hold=1.0))
    assert any("Schwarzblende" in i for i in issues)


def test_black_transition_with_too_large_gap_is_flagged():
    # `duration` passend gesetzt, damit die Schema-Semantik nicht vorher abbricht.
    timeline = _black_tl(3.0, hold=1.0)
    timeline.duration = 4.0
    issues = validate(timeline)
    assert any("Schwarzblende" in i for i in issues)


# -- Audit-Fix F3: sequenzielle Renderlaenge gegen die tl_in-Positionen -------------


def _mixed_timeline(*, tl_in_third: float, duration: float):
    """3 Clips: harter Schnitt, dann Crossfade, dann Schwarzblende mit Standzeit."""
    return Timeline(
        export="e",
        fps=25,
        resolution=(320, 240),
        duration=duration,
        tracks={
            "video": [
                {"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2.0, "tl_in": 0.0},
                {
                    "id": "c2",
                    "asset": "a2",
                    "src_in": 0,
                    "src_out": 2.0,
                    "tl_in": 1.5,
                    "transition_in": {"type": "fade", "dur": 0.5},
                },
                {
                    "id": "c3",
                    "asset": "a3",
                    "src_in": 0,
                    "src_out": 2.0,
                    "tl_in": tl_in_third,
                    "transition_in": {"type": "black", "dur": 0.3, "hold": 1.0},
                },
            ]
        },
    )


def test_mixed_transitions_with_correct_positions_pass():
    # 2.0 + 2.0 - 0.5 Crossfade = 3.5s Bild, + 1.0s Standzeit -> dritter Clip ab 4.5s
    assert validate(_mixed_timeline(tl_in_third=4.5, duration=6.5)) == []


def test_video_length_mismatch_is_reported():
    """Die Standzeit fehlt in den tl_in-Werten — Bild und Ton laufen 1 s auseinander."""
    timeline = _mixed_timeline(tl_in_third=3.5, duration=6.5)
    issues = validate(timeline)
    assert any("Video-Spur" in i and "gegen das Bild" in i for i in issues)


def test_music_tail_after_the_last_clip_is_allowed():
    """Musik-Ausklang nach dem letzten Bild ist zulaessig — der Render folgt der Audio-Spur."""
    timeline = Timeline(
        export="e",
        fps=25,
        resolution=(320, 240),
        duration=8.0,
        tracks={
            "video": [{"id": "c1", "asset": "a1", "src_in": 0, "src_out": 2.0, "tl_in": 0}],
            "audio": [{"id": "m1", "src": "music/t.wav", "tl_in": 0, "dur": 8.0}],
        },
    )
    assert validate(timeline) == []


def test_length_check_ignores_empty_video_track():
    timeline = Timeline(export="e", fps=25, resolution=(320, 240), duration=5.0, tracks={})
    assert _check_video_length_consistency(timeline) == []


def test_validate_reports_source_window_longer_than_the_clip():
    """Laeuft ein Clip mitten im Film aus, endet der GESAMTE Video-Pfad dort — ohne Fehler im
    Render. Gefunden 2026-08-09: ein Titelbett verlangte 24s aus einer 18,7s-Datei, der fertige
    Preview war 26,7s lang statt 18 Minuten, die Datei formal gueltig."""
    tl = Timeline(
        export="teaser", fps=25, resolution=(1920, 1080), duration=29.0,
        tracks={"video": [
            {"id": "c001", "asset": "clip-lang", "src_in": 0, "src_out": 24, "tl_in": 0},
            {"id": "c002", "asset": "clip-ok", "src_in": 0, "src_out": 5, "tl_in": 24},
        ]},
    )
    issues = validate(tl, asset_durations={"clip-lang": 18.7, "clip-ok": 30.0})
    assert any("c001" in i and "18.70" in i for i in issues), issues
    assert not any("c002" in i for i in issues)


def test_validate_ignores_source_windows_without_known_duration():
    """Ohne bekannte Laufzeit (z.B. Fotos, `-loop 1`) darf die Pruefung nicht anschlagen."""
    tl = Timeline(
        export="teaser", fps=25, resolution=(1920, 1080), duration=24.0,
        tracks={"video": [{"id": "c001", "asset": "foto", "src_in": 0, "src_out": 24, "tl_in": 0}]},
    )
    assert validate(tl, asset_durations={}) == []
    assert validate(tl) == []
