"""Baut `projects/proto/` komplett durch die Pipeline (M1.8, siehe `docs/plans/PROGRESS.md`).

Steht fuer die Schritte, die im echten Betrieb interaktiv per Slash-Command + Sub-Agenten
liefen (`/ff-index` -> `media-indexer`, `/ff-design`, `/ff-brief`, `/ff-build` ->
`story-architect`/`timeline-builder`): hier deterministisch nachgebaut, damit der
Mini-Prototyp reproduzierbar ohne LLM-Aufrufe entsteht. Nur bei Bedarf neu ausfuehren:
`.venv/bin/python tests/fixtures/build_proto_project.py`.
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

import yaml

from frameforge.analyze import analyze_clip, analyze_photo
from frameforge.design import build_svg_from_tokens, render_svg_to_png
from frameforge.gpx import nearest_location, parse_gpx
from frameforge.index import write_asset
from frameforge.ingest import build_proxies, hash_file, scan_media
from frameforge.keyframes import extract_keyframes
from frameforge.map import encode_alpha_video, render_route_frames
from frameforge.probe import probe_video
from frameforge.project import PROJECTS_DIR, ProjectConfig, resolve_project
from frameforge.qc import validate
from frameforge.render import render_proxy
from frameforge.state import Phase
from frameforge.timeline import Timeline

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
MEDIA_ROOT = FIXTURES_DIR / "proto_media"
PROJECT_NAME = "proto"
EXPORT_NAME = "teaser"

DESCRIPTIONS = {
    "clip-fjord.mp4": {
        "summary": "Weite Einstellung auf den Fjord, ruhiges Wasser, klares Licht.",
        "tags": ["fjord", "wasser", "weitwinkel", "ruhig"],
        "usable_as": ["establisher", "b-roll"],
        "rating": 4,
    },
    "clip-water.mp4": {
        "summary": "Nahaufnahme von Wellenbewegung am Ufer.",
        "tags": ["wasser", "detail", "bewegung"],
        "usable_as": ["b-roll"],
        "rating": 3,
    },
    "clip-drive.mp4": {
        "summary": "Fahrt entlang der Serpentine, Motorengeraeusch im O-Ton.",
        "tags": ["strasse", "fahrt", "auto"],
        "usable_as": ["b-roll", "outro"],
        "rating": 4,
    },
    "photo-cabin.jpg": {
        "summary": "Huette am Wasser in blauem Licht.",
        "tags": ["huette", "architektur"],
        "usable_as": ["establisher"],
        "rating": 5,
    },
    "photo-family.jpg": {
        "summary": "Warmes Abendlicht ueber der Landschaft.",
        "tags": ["abend", "landschaft", "warm"],
        "usable_as": ["b-roll", "outro"],
        "rating": 4,
    },
}

TOKENS = {
    "primary_color": "#12222f",
    "accent_color": "#e0a458",
    "text_color": "#ffffff",
    "font_display": "Helvetica",
    "font_text": "Helvetica",
}


def step_new(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for sub in (
        "design/fonts",
        "design/assets",
        "index/assets",
        "index/days",
        "route",
        "music/analysis",
        "exports",
    ):
        (root / sub).mkdir(parents=True, exist_ok=True)
    ProjectConfig(name=PROJECT_NAME, media_root=MEDIA_ROOT, timezone="Europe/Oslo", language="de").save(
        root / "project.yaml"
    )
    resolve_project(PROJECT_NAME).load_state().save()


def step_ingest(project) -> None:
    found = scan_media(MEDIA_ROOT)
    build_proxies(found, project.cache_dir / "proxies")
    state = project.load_state()
    state.advance_project(Phase.INGESTED)
    state.save()


def step_index(project, track: list[dict]) -> dict[str, str]:
    """Gibt `{dateiname: asset_id}` zurueck, fuer den Timeline-Bau weiter unten."""
    asset_ids: dict[str, str] = {}
    base_time = track[0]["time"]
    keyframes_dir = project.cache_dir / "keyframes"

    for i, path in enumerate(sorted(MEDIA_ROOT.iterdir())):
        if path.name not in DESCRIPTIONS:
            continue
        captured_at = base_time + timedelta(minutes=3 * i)
        is_photo = path.suffix.lower() in {".jpg", ".jpeg"}
        kind = "photo" if is_photo else "video"
        desc = DESCRIPTIONS[path.name]
        asset_id = f"{captured_at:%Y%m%d}-{path.stem}"
        asset_ids[path.name] = asset_id
        location = nearest_location(captured_at, track)

        if is_photo:
            analysis = analyze_photo(path)
            extract_keyframes(path, kind="photo", out_dir=keyframes_dir)
            tech = None
        else:
            probe_data = probe_video(path)
            analysis = analyze_clip(path, probe_data)
            extract_keyframes(
                path,
                kind="video",
                out_dir=keyframes_dir,
                duration=probe_data["dur"],
                scenes=[(s["start"], s["end"]) for s in analysis["scenes"]],
            )
            tech = probe_data

        asset = {
            "id": asset_id,
            "hash": hash_file(path),
            "path": path.relative_to(MEDIA_ROOT).as_posix(),
            "kind": kind,
            "captured_at": captured_at.isoformat(),
            "gps": (
                {"lat": location["lat"], "lon": location["lon"], "place": "Trollstigen"}
                if location
                else None
            ),
            "content": {
                "summary": desc["summary"],
                "tags": desc["tags"],
                "people": False,
                "usable_as": desc["usable_as"],
            },
            "rating": desc["rating"],
            **({"tech": tech} if tech else {}),
            **analysis,
        }
        write_asset(project, asset)

    state = project.load_state()
    state.advance_project(Phase.INDEXED)
    state.save()
    return asset_ids


def step_design(project) -> None:
    project.design_tokens_path.write_text(yaml.safe_dump(TOKENS, allow_unicode=True))
    state = project.load_state()
    state.advance_project(Phase.DESIGNED)
    state.save()


def step_brief(project, export) -> None:
    brief = {
        "preset": "nordic-cinematic",
        # Bewusst klein: das Testmaterial umfasst nur Sekunden, nicht Minuten. Ein reales
        # Projekt setzt hier 60-90s (Plan Abschnitt 8), das waere mit den winzigen
        # Fixtures aus tests/fixtures/proto_media/ nicht ehrlich erreichbar.
        "target_duration_s": 12,
        "must_shots": [],
        "forbidden_shots": [],
        "language": "de",
    }
    export.brief_path.write_text(yaml.safe_dump(brief, allow_unicode=True))
    state = project.load_state()
    state.advance_export(EXPORT_NAME, Phase.BRIEFED)
    state.save()


def step_beatsheet(export) -> None:
    export.beatsheet_path.write_text(
        "# Beat-Sheet — teaser (proto)\n\n"
        "1. Establisher — clip-fjord (0.0-2.2s), Titel-Overlay\n"
        "2. Huette — photo-cabin (2.2-4.2s)\n"
        "3. Fahrt mit O-Ton — clip-drive (4.2-6.2s), Musik geduckt\n"
        "4. Wasser-Detail + Karte — clip-water (6.2-8.2s)\n"
        "5. Ausklang — photo-family (8.2-10.2s)\n"
    )


def step_build(project, export, asset_ids: dict[str, str], track: list[dict]) -> Timeline:
    title_svg = build_svg_from_tokens(
        REPO_ROOT / "templates" / "svg" / "title-card.svg",
        {
            **TOKENS,
            "width": 320,
            "height": 240,
            "title_size": 24,
            "subtitle_size": 12,
            "title": "Proto-Tour",
            "subtitle": "Mini-Prototyp",
        },
    )
    export.overlays_dir.mkdir(parents=True, exist_ok=True)
    render_svg_to_png(title_svg, export.overlays_dir / "title.png")

    export.map_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = project.cache_dir / "map_frames"
    render_route_frames(track, frames_dir, fps=10, dur=2.0, width=160, height=120)
    encode_alpha_video(frames_dir, export.map_dir / "leg-01.mov", fps=10)

    music_path = project.music_dir / "theme.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=220:duration=10.5",
            "-loglevel",
            "error",
            str(music_path),
        ],
        check=True,
    )

    timeline = Timeline(
        export=EXPORT_NAME,
        fps=25,
        resolution=(320, 240),
        duration=10.5,
        tracks={
            "video": [
                {
                    "id": "c1",
                    "asset": asset_ids["clip-fjord.mp4"],
                    "src_in": 0,
                    "src_out": 2.2,
                    "tl_in": 0.0,
                    "transition_in": {"type": "fade", "dur": 0.3},
                },
                {
                    "id": "c2",
                    "asset": asset_ids["photo-cabin.jpg"],
                    "src_in": 0,
                    "src_out": 2.0,
                    "tl_in": 2.2,
                },
                {
                    "id": "c3",
                    "asset": asset_ids["clip-drive.mp4"],
                    "src_in": 0,
                    "src_out": 2.0,
                    "tl_in": 4.2,
                },
                {
                    "id": "c4",
                    "asset": asset_ids["clip-water.mp4"],
                    "src_in": 0,
                    "src_out": 2.0,
                    "tl_in": 6.2,
                },
                {
                    "id": "c5",
                    "asset": asset_ids["photo-family.jpg"],
                    "src_in": 0,
                    "src_out": 2.0,
                    "tl_in": 8.2,
                },
            ],
            "overlay": [
                {"id": "o1", "png": "overlays/title.png", "tl_in": 0.0, "dur": 2.2},
            ],
            "map": [
                {"id": "m1", "clip": "map/leg-01.mov", "tl_in": 6.2, "dur": 2.0},
            ],
            "audio": [
                {"id": "a1", "src": "music/theme.wav", "tl_in": 0.0, "gain_db": -8},
                {
                    "id": "a2",
                    "asset": asset_ids["clip-drive.mp4"],
                    "type": "original",
                    "tl_in": 4.2,
                    "dur": 2.0,
                    "duck_music_db": -14,
                },
            ],
        },
    )
    timeline.save(export.timeline_path)

    state = project.load_state()
    state.advance_export(EXPORT_NAME, Phase.TIMELINE)
    state.save()
    return timeline


def step_preview(project, export, timeline: Timeline) -> Path:
    issues = validate(timeline)
    if issues:
        raise RuntimeError(f"QC-Probleme: {issues}")
    out_path = render_proxy(project, export, timeline)
    state = project.load_state()
    state.advance_export(EXPORT_NAME, Phase.PREVIEWED)
    state.save()
    return out_path


def main() -> None:
    root = PROJECTS_DIR / PROJECT_NAME
    step_new(root)
    project = resolve_project(PROJECT_NAME)

    project.route_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES_DIR / "route.gpx", project.gpx_path)
    track = parse_gpx(project.gpx_path)

    step_ingest(project)
    asset_ids = step_index(project, track)
    step_design(project)

    export = project.export(EXPORT_NAME)
    export.ensure_dirs()
    step_brief(project, export)
    step_beatsheet(export)
    timeline = step_build(project, export, asset_ids, track)
    out_path = step_preview(project, export, timeline)

    print("Preview gerendert:", out_path)
    print(probe_video(out_path))
    print("Projekt-Phase:", project.load_state().project_phase.name)
    print("Export-Phase:", project.load_state().export_phase(EXPORT_NAME).name)


if __name__ == "__main__":
    main()
