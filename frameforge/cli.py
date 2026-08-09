"""Einheitlicher CLI-Entry: `python -m frameforge <cmd>` bzw. `frameforge <cmd>`.

Der Orchestrator (Claude) ruft ausschliesslich diese CLI auf, nie Module direkt
und nie `ffmpeg` nackt (CLAUDE.md). Jedes Kommando, das eine Phase voraussetzt,
prueft das Gate aus `frameforge.state` selbst — Guertel + Hosentraeger neben dem
`PreToolUse`-Hook aus Task 4.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from frameforge import backfill as backfill_module
from frameforge import brief as brief_module
from frameforge import design, qc
from frameforge import gpx as gpx_module
from frameforge import index as index_module
from frameforge import ingest as ingest_module
from frameforge import nle as nle_module
from frameforge import people as people_module
from frameforge import pipeline as pipeline_module
from frameforge import places as places_module
from frameforge import preindex as preindex_module
from frameforge import presets as presets_module
from frameforge import probe as probe_module
from frameforge import relink as relink_module
from frameforge import render as render_module
from frameforge import route as route_module
from frameforge import stats as stats_module
from frameforge import themes as themes_module
from frameforge.project import (
    CACHE_ROOT,
    PROJECTS_DIR,
    Project,
    ProjectConfig,
    ProjectNotFoundError,
    UnsafeNameError,
    UnsafePathError,
    list_projects,
    resolve_media_path,
    resolve_project,
    validate_name,
)
from frameforge.state import (
    GateError,
    Phase,
    ProjectState,
    StateError,
    gate_brief,
    gate_build,
    gate_design,
    gate_index,
    gate_preview,
    gate_render_final,
)
from frameforge.timeline import Timeline, TimelineValidationError

app = typer.Typer(help="FrameForge — orchestrierte, reproduzierbare Videoschnitt-Pipeline")
console = Console()


def _fail(message: str) -> typer.Exit:
    console.print(f"[red]Fehler:[/red] {message}")
    return typer.Exit(code=1)


def _resolve_or_fail(project: str) -> Project:
    try:
        return resolve_project(project)
    except ProjectNotFoundError as exc:
        raise _fail(str(exc)) from exc


# -- doctor -------------------------------------------------------------


@dataclass
class _Check:
    name: str
    ok: bool
    detail: str


def _check_python() -> _Check:
    ok = sys.version_info >= (3, 12)
    detail = f"{sys.version.split()[0]}" + ("" if ok else " — benoetigt >= 3.12")
    return _Check("Python", ok, detail)


def _check_executable(name: str, version_flag: str = "-version") -> _Check:
    path = shutil.which(name)
    if not path:
        return _Check(name, False, "nicht gefunden — 'brew install ffmpeg exiftool'")
    try:
        result = subprocess.run(
            [name, version_flag], capture_output=True, text=True, timeout=5, check=False
        )
        first_line = (result.stdout or result.stderr).splitlines()[0]
    except Exception as exc:  # noqa: BLE001 — doctor darf bei jedem Fehler nur den Report anzeigen
        first_line = f"gefunden, Versionsabfrage fehlgeschlagen ({exc})"
    return _Check(name, True, first_line)


def _check_cairo() -> _Check:
    try:
        design.preload_cairo()
        import cairosvg  # noqa: F401
    except Exception as exc:  # noqa: BLE001 — doctor darf bei jedem Fehler nur den Report anzeigen
        return _Check("libcairo", False, f"{exc}")
    return _Check("libcairo", True, "geladen")


def _check_cache_writable() -> _Check:
    try:
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        probe = CACHE_ROOT / ".doctor-write-test"
        probe.write_text("ok")
        probe.unlink()
    except OSError as exc:
        return _Check("Cache-Verzeichnis", False, f"{CACHE_ROOT} nicht beschreibbar: {exc}")
    return _Check("Cache-Verzeichnis", True, str(CACHE_ROOT))


_MIN_FREE_GB = 5.0


def _check_disk_space() -> _Check:
    # Informativ: wenig Platz laesst doctor NICHT durchfallen (kein Umgebungsfehler), zeigt aber
    # eine Warnung — Ingest/Render von grossem Material braucht Platz.
    try:
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        free_gb = shutil.disk_usage(CACHE_ROOT).free / (1024**3)
    except OSError as exc:
        return _Check("Plattenplatz (Cache)", True, f"nicht ermittelbar: {exc}")
    warn = "" if free_gb >= _MIN_FREE_GB else f"  [yellow]wenig (< {_MIN_FREE_GB:.0f} GB)[/yellow]"
    return _Check("Plattenplatz (Cache)", True, f"{free_gb:.1f} GB frei{warn}")


@app.command()
def doctor() -> None:
    """Prueft die Umgebung: ffmpeg, ffprobe, exiftool, libcairo, Python-Version, Cache."""
    checks = [
        _check_python(),
        _check_executable("ffmpeg"),
        _check_executable("ffprobe"),
        _check_executable("exiftool", "-ver"),
        _check_cairo(),
        _check_cache_writable(),
        _check_disk_space(),
    ]

    table = Table(title="frameforge doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")
    for check in checks:
        status = "[green]OK[/green]" if check.ok else "[red]FEHLT[/red]"
        table.add_row(check.name, status, check.detail)
    console.print(table)

    if not all(check.ok for check in checks):
        raise typer.Exit(code=1)


# -- new / status ---------------------------------------------------------


@app.command()
def new(
    name: str,
    media_root: Path = typer.Option(..., help="Externer Pfad zum Rohmaterial (nicht im Repo)"),  # noqa: B008
    timezone: str = typer.Option("UTC"),
    language: str = typer.Option("de"),
) -> None:
    """Legt ein neues Projekt unter `projects/<name>/` an."""
    try:
        validate_name(name, kind="Projekt-Name")
    except UnsafeNameError as exc:
        raise _fail(str(exc)) from exc
    root = PROJECTS_DIR / name
    if root.exists():
        raise _fail(f"Projekt '{name}' existiert bereits unter {root}")

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

    config = ProjectConfig(name=name, media_root=media_root, timezone=timezone, language=language)
    config.save(root / "project.yaml")

    project = resolve_project(name)
    project.load_state().save()  # legt .state.json mit Phase INIT an

    console.print(f"[green]Projekt '{name}' angelegt[/green] unter {root}")
    if not media_root.exists():
        console.print(f"[yellow]Hinweis:[/yellow] media_root {media_root} existiert (noch) nicht")


def _colorize_pipeline_line(line: str) -> str:
    """Faerbt die Marker in einer Pipeline-Zeile fuer die Terminal-Ausgabe."""
    line = line.replace(pipeline_module.DONE, "[green][✓][/green]")
    line = line.replace(pipeline_module.CURRENT, "[bold yellow][→][/bold yellow]")
    line = line.replace(pipeline_module.PENDING, "[dim][ ][/dim]")
    return line


@app.command()
def status(project: str) -> None:
    """Visuelle Pipeline-Uebersicht: was erledigt (✓), was jetzt dran (→), was offen ( )."""
    proj = _resolve_or_fail(project)
    state = proj.load_state()
    pending = pipeline_module.pending_assets(proj)
    pipeline = pipeline_module.build_pipeline(project, state, exports=proj.list_exports())
    for line in pipeline_module.format_pipeline(pipeline):
        console.print(_colorize_pipeline_line(line) if line.strip() else line)

    # Neues Rohmaterial faellt sonst niemandem auf, sobald das Projekt ueber INDEXED hinaus ist
    # (Plan 0003 §G). Reiner Hash-Vergleich, keine Kosten, deshalb in jeder Phase.
    if pending:
        console.print(
            f"\n[yellow]{len(pending)} neue Datei(en) in media_root, noch nicht indiziert[/yellow] "
            f"— /ff-ingest + /ff-index: {', '.join(p.name for p in pending[:5])}"
            + (" …" if len(pending) > 5 else "")
        )
    for export_name in proj.list_exports():
        drift = pipeline_module.asset_drift(proj, state, export_name)
        if drift:
            console.print(f"[yellow]{export_name}:[/yellow] {drift}")


# -- Pipeline-Kommandos ---------------------------------------------------
# Gates werden hier geprueft (Guertel), zusaetzlich vom PreToolUse-Hook (Hosentraeger).
# `brief`/`build` sind bewusst reine Gate-Wrapper: die kreative Arbeit (Beat-Sheet,
# Timeline-Bau) macht ein Sub-Agent, nicht die CLI (siehe .claude/commands/ff-brief,
# ff-build). Sie brechen daher nach dem Gate mit Hinweis ab.


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


@app.command()
def ingest(
    project: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Nur zeigen, was gefunden wuerde — nichts transkodieren"),
) -> None:
    """Scan + Proxy-Erzeugung fuer das Rohmaterial. Setzt Projekt-Phase auf INGESTED.

    `--dry-run` scannt nur und zeigt Anzahl/Groesse/Typen — nuetzlich vor dem Transkodieren
    von 100 GB, ohne etwas zu schreiben.
    """
    proj = _resolve_or_fail(project)
    try:
        found = ingest_module.scan_media(proj.config.media_root)
    except FileNotFoundError as exc:
        raise _fail(str(exc)) from exc

    if dry_run:
        by_ext: dict[str, list[int]] = {}
        for p in found:
            by_ext.setdefault(p.suffix.lower(), []).append(p.stat().st_size)
        total = sum(s for sizes in by_ext.values() for s in sizes)
        table = Table(title=f"Dry-Run: {len(found)} Mediendateien, {_human_size(total)}")
        table.add_column("Endung")
        table.add_column("Anzahl", justify="right")
        table.add_column("Groesse", justify="right")
        for ext, sizes in sorted(by_ext.items(), key=lambda kv: -sum(kv[1])):
            table.add_row(ext, str(len(sizes)), _human_size(sum(sizes)))
        console.print(table)
        console.print("[dim]Nichts geschrieben. Ohne --dry-run werden Proxies erzeugt.[/dim]")
        return

    proxies_dir = proj.cache_dir / "proxies"
    result = ingest_module.build_proxies(found, proxies_dir, media_root=proj.config.media_root)

    with ProjectState.transaction(proj.state_path) as state:
        state.ensure_project_at_least(Phase.INGESTED)
    console.print(
        f"[green]{len(found)} Assets gefunden, {len(result.proxies)} Proxies bereit.[/green] "
        f"Proxy-Verzeichnis: {proxies_dir}"
    )
    # Fehlschlaege persistent festhalten (Audit D4), nicht nur auf der Konsole.
    report_path = proj.cache_dir / "ingest-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "when": datetime.now(UTC).isoformat(),
                "found": len(found),
                "proxies": len(result.proxies),
                "failures": [{"asset": str(f.asset), "reason": f.reason} for f in result.failures],
            },
            indent=2,
        )
    )
    if result.failures:
        console.print(
            f"[yellow]{len(result.failures)} Asset(s) uebersprungen (Proxy fehlgeschlagen), "
            f"Details in {report_path}:[/yellow]"
        )
        for failure in result.failures:
            console.print(f"  {failure.asset.name}: {failure.reason}")


@app.command()
def relink(
    project: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Nur zeigen, was korrigiert wuerde"),
) -> None:
    """Repariert `path`-Eintraege in `assets.json` nach dem Umsortieren von `media_root`.

    Matcht per Datei-Hash (nicht per Pfad), aktualisiert nur das Feld `path` und meldet
    verwaiste Eintraege (Datei nicht mehr auffindbar) sowie neue, noch nicht indizierte
    Dateien. Keine erneute Analyse, kein Vision-Call, `content`/`rating`/Notizen bleiben
    unangetastet.
    """
    proj = _resolve_or_fail(project)
    try:
        result = relink_module.plan_relink(proj)
    except FileNotFoundError as exc:
        raise _fail(str(exc)) from exc

    if result.changed:
        table = Table(title=f"{len(result.changed)} Pfad(e) zu korrigieren")
        table.add_column("Asset")
        table.add_column("alt")
        table.add_column("neu")
        for change in result.changed:
            table.add_row(change.asset_id, change.old_path, change.new_path)
        console.print(table)

    if result.ambiguous:
        console.print(
            f"[yellow]{len(result.ambiguous)} Asset(s) mehrdeutig (gleicher Hash an mehreren "
            "Stellen) — nicht automatisch geaendert:[/yellow]"
        )
        for amb in result.ambiguous:
            console.print(f"  {amb.asset_id}: {', '.join(amb.candidates)}")

    if result.orphans:
        console.print(f"[yellow]{len(result.orphans)} verwaiste(r) Eintrag/Eintraege:[/yellow]")
        for orphan in result.orphans:
            console.print(f"  {orphan.asset_id}: {orphan.path}")

    if result.new_files:
        console.print(
            f"[yellow]{len(result.new_files)} neue, noch nicht indizierte Datei(en)[/yellow] "
            f"— 'frameforge ingest {project}' + '/ff-index':"
        )
        for rel in result.new_files[:20]:
            console.print(f"  {rel}")
        if len(result.new_files) > 20:
            console.print(f"  … und {len(result.new_files) - 20} weitere")

    console.print(f"[dim]{result.unchanged} Asset(s) unveraendert.[/dim]")

    if dry_run:
        console.print("[dim]Dry-Run: nichts geschrieben.[/dim]")
        return
    written = relink_module.apply_relink(proj, result)
    if written:
        console.print(
            f"[green]{written} Pfad(e) in assets.json korrigiert, "
            f"{result.moved_proxies} Proxy(s) im Cache mitgezogen.[/green]"
        )
    else:
        console.print("[green]Nichts zu korrigieren.[/green]")


@app.command(name="backfill-metadata")
def backfill_metadata(
    project: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Nur zeigen, was nachgetragen wuerde"),
) -> None:
    """Traegt fehlende **technische** Metadaten nach, ohne neu zu indizieren.

    Probt die Originaldateien erneut und ergaenzt `captured_at`, `duration`, `probe.*` und
    `gps.lat/lon/elevation_m`. `content`, `tags`, `rating`, `source`, `gps.place` und die
    Freitext-Notizen bleiben unangetastet — kein Vision-Call, keine CV-Analyse.
    """
    proj = _resolve_or_fail(project)
    result = backfill_module.plan_backfill(proj)

    counts = result.count_by_field()
    if counts:
        table = Table(title=f"{len(result.touched_assets)} Asset(s) zu ergaenzen")
        table.add_column("Feld")
        table.add_column("Assets", justify="right")
        table.add_column("davon neu", justify="right")
        for name, count in counts.items():
            new = sum(1 for u in result.updates if u.field == name and u.is_new)
            table.add_row(name, str(count), str(new))
        console.print(table)

    if result.missing_files:
        console.print(
            f"[yellow]{len(result.missing_files)} Asset(s) ohne auffindbare Datei[/yellow] "
            f"— erst 'frameforge relink {project}': {', '.join(result.missing_files[:10])}"
            + (" …" if len(result.missing_files) > 10 else "")
        )
    for failure in result.failures:
        console.print(f"[yellow]  {failure.asset_id}: {failure.reason}[/yellow]")

    console.print(
        f"[dim]{result.scanned} Asset(s) geprueft, {result.unchanged} bereits vollstaendig.[/dim]"
    )
    if proj.config.originals_root is None:
        console.print(
            "[dim]Kein 'originals_root' in project.yaml — GPS aus den ungeschnittenen "
            "Originalen wird uebersprungen (Plan 0003 §A2).[/dim]"
        )
    else:
        console.print(
            f"[dim]originals_root: {result.originals_found} Datei(en) gefunden unter "
            f"{proj.config.originals_root}[/dim]"
        )

    if dry_run:
        console.print("[dim]Dry-Run: nichts geschrieben.[/dim]")
        return

    written = backfill_module.apply_backfill(proj, result)
    console.print(f"[green]{written} Asset(s) in assets.json ergaenzt.[/green]")

    with_time, total = backfill_module.captured_at_coverage(proj, kind="video")
    if total:
        console.print(
            f"Aufnahmezeit bei Videos: {with_time}/{total} ({with_time / total:.0%})"
        )


@app.command(name="assign-places")
def assign_places(
    project: str,
    dry_run: bool = typer.Option(False, "--dry-run", help="Nur den Report zeigen, nichts schreiben"),
    force: bool = typer.Option(False, "--force", help="Auch manuell gesetzte Orte ueberschreiben"),
    tolerance_km: float = typer.Option(
        places_module.DEFAULT_POI_TOLERANCE_KM, "--tolerance-km", help="Radius fuer POI-Treffer"
    ),
    gpx_tolerance_min: float = typer.Option(
        places_module.DEFAULT_GPX_TOLERANCE_S / 60,
        "--gpx-tolerance-min",
        help="Wie weit ein GPX-Trackpunkt zeitlich entfernt sein darf, um als Position zu gelten",
    ),
) -> None:
    """Ordnet jedem Asset Tag, Etappe und Ort zu — aus `stages.csv`/`locations.csv`/GPX.

    Reihenfolge der Ort-Logik: echte GPS-Position → naechstgelegener POI in Reichweite →
    bei Fahretappen 'unterwegs: A → B' → 'unknown'. Manuell gesetzte Orte bleiben ohne
    `--force` unangetastet. Kein Vision-Call.
    """
    proj = _resolve_or_fail(project)
    try:
        result = places_module.plan_assignment(
            proj,
            tolerance_km=tolerance_km,
            gpx_tolerance_s=gpx_tolerance_min * 60,
            force=force,
        )
    except (gpx_module.StagesError, gpx_module.LocationsError) as exc:
        raise _fail(str(exc)) from exc

    if not proj.stages_csv_path.exists():
        console.print(
            f"[yellow]Keine {proj.stages_csv_path} — ohne Etappenliste gibt es weder Tag noch "
            "Etappe. Siehe /ff-route bzw. templates/prompts/route.md.[/yellow]"
        )

    if result.by_day:
        table = Table(title="Assets je Reisetag")
        table.add_column("Tag", justify="right")
        table.add_column("Assets", justify="right")
        for day, count in sorted(result.by_day.items()):
            table.add_row(str(day), str(count))
        console.print(table)

    if result.by_place_source:
        console.print(
            "Ortsquelle: "
            + ", ".join(f"{k}={v}" for k, v in sorted(result.by_place_source.items()))
        )

    for label, ids in (
        ("ohne Aufnahmezeit", result.without_time),
        ("Tag fehlt in stages.csv", result.without_stage),
        ("Ort unklar (siehe places-todo)", result.unresolved),
        ("manuell gesetzt, nicht angefasst", result.protected),
    ):
        if ids:
            console.print(f"[yellow]{len(ids)} {label}[/yellow]: {', '.join(ids[:8])}"
                          + (" …" if len(ids) > 8 else ""))

    if result.conflicts:
        table = Table(title=f"{len(result.conflicts)} Konflikt(e): bisheriger vs. berechneter Ort")
        table.add_column("Asset")
        table.add_column("bisher")
        table.add_column("berechnet")
        table.add_column("Quelle")
        for conflict in result.conflicts[:30]:
            table.add_row(conflict.asset_id, conflict.old_place, conflict.new_place, conflict.source)
        console.print(table)
        if len(result.conflicts) > 30:
            console.print(f"[dim]… und {len(result.conflicts) - 30} weitere[/dim]")

    console.print(
        f"[dim]{result.scanned} Asset(s) geprueft, {len(result.touched_assets)} zu aendern.[/dim]"
    )
    if dry_run:
        console.print("[dim]Dry-Run: nichts geschrieben.[/dim]")
        return
    written = places_module.apply_assignment(proj, result)
    console.print(f"[green]{written} Asset(s) aktualisiert (day/stage/place).[/green]")


@app.command(name="route-build")
def route_build(
    project: str,
    from_kml: Path = typer.Option(  # noqa: B008
        None, "--from-kml", help="KML-Export (Google Maps) statt Routing-Dienst verwenden"
    ),
) -> None:
    """Erzeugt `route/roadtrip.gpx` — aus einem KML-Export oder per Routing über die Etappen.

    Rangfolge laut Plan 0003 §B5: echter GPX-Track (dann ist nichts zu tun) → KML-Export
    (`--from-kml`) → Routing aus `stages.csv` + `locations.csv`.
    """
    proj = _resolve_or_fail(project)
    try:
        if from_kml is not None:
            path = route_module.import_kml(proj, from_kml)
            unknown: list[str] = []
        else:
            path, unknown = route_module.build_route_gpx(proj)
    except (route_module.RoutingError, gpx_module.KmlError, gpx_module.StagesError) as exc:
        raise _fail(str(exc)) from exc

    points = gpx_module.parse_gpx(path, require_time=False)
    console.print(f"[green]{path} geschrieben — {len(points)} Punkte.[/green]")
    if unknown:
        console.print(
            f"[yellow]Ohne Koordinaten und daher nicht in der Route:[/yellow] "
            f"{', '.join(unknown)} — in route/locations.csv ergaenzen."
        )


@app.command(name="set-source")
def set_source_cmd(project: str, asset: str, source: str) -> None:
    """Korrigiert die Aufnahme-Quelle eines Assets (`drone`/`phone`/`camera`/`action_cam`).

    Der `media-indexer` setzt `source` beim Indizieren aus Keyframes + EXIF-Vorschlag; liegt er
    daneben, ist das hier die Korrektur — ohne Neu-Indizierung und ohne Vision-Call.
    """
    proj = _resolve_or_fail(project)
    if source not in probe_module.SOURCE_TYPES:
        raise _fail(f"source '{source}' nicht in {probe_module.SOURCE_TYPES}")
    assets = index_module.load_assets(proj)
    target = next((a for a in assets if a.get("id") == asset or a.get("hash") == asset), None)
    if target is None:
        raise _fail(f"Kein Asset mit ID oder Hash '{asset}'")
    old = target.get("source")
    target["source"] = source
    index_module.save_assets(proj, assets)
    index_module.write_asset_md(proj, target)
    console.print(f"[green]{target['id']}: source {old} → {source}[/green]")


@app.command(name="color-match")
def color_match_cmd(
    project: str,
    export: str,
    strength: str = typer.Option(
        None, "--strength", help="off | soft | strong (Default: aus dem Brief, sonst soft)"
    ),
) -> None:
    """Gleicht die Clips eines Exports farblich aneinander an (Plan 0003 §H2).

    Schreibt je Clip `color_match` in die `timeline.json` — nachvollziehbar, überschreibbar,
    reproduzierbar und im NLE-Export mit dabei. Grundlage ist `asset["color_stats"]` aus dem
    Backfill (Keyframes, kein neues Decoding). Referenz ist der Median über die **in diesem
    Export verwendeten** Clips.
    """
    proj = _resolve_or_fail(project)
    exp = proj.export(export)
    if not exp.timeline_path.exists():
        raise _fail(f"Keine timeline.json fuer '{export}' — erst /ff-build.")

    if strength is None:
        try:
            brief = brief_module.Brief.load(exp.brief_path).merged() if exp.brief_path.exists() else {}
        except brief_module.BriefError as exc:
            raise _fail(str(exc)) from exc
        strength = brief.get("color_match", render_module.DEFAULT_COLOR_MATCH)

    timeline = Timeline.load(exp.timeline_path)
    stats_by_asset = {
        a["id"]: a.get("color_stats") or {} for a in index_module.load_assets(proj)
    }
    used = [stats_by_asset.get(c.asset, {}) for c in timeline.tracks.video]
    reference = render_module.reference_stats(used)
    if not reference:
        raise _fail(
            "Keine color_stats an den verwendeten Assets — erst 'frameforge backfill-metadata' "
            f"{project} (braucht die Keyframes im Cache)."
        )

    try:
        matched = 0
        for clip in timeline.tracks.video:
            clip.color_match = render_module.color_match_for(
                stats_by_asset.get(clip.asset, {}), reference, strength=strength
            )
            matched += clip.color_match is not None
    except ValueError as exc:
        raise _fail(str(exc)) from exc

    exp.timeline_path.write_text(timeline.model_dump_json(indent=2, exclude_none=True) + "\n")
    console.print(
        f"[green]{matched} von {len(timeline.tracks.video)} Clip(s) angeglichen "
        f"(strength={strength}).[/green] Werte stehen in {exp.timeline_path}."
    )
    if strength == "off":
        console.print("[dim]strength=off — alle color_match-Werte entfernt.[/dim]")


@app.command(name="places-todo")
def places_todo_cmd(
    project: str,
    day: int = typer.Option(None, "--day", help="Nur einen Reisetag zeigen"),
    limit: int = typer.Option(None, "--limit", help="Nur die ersten N Assets zeigen"),
) -> None:
    """Worklist der Assets, deren Ort unklar ist — Gegenstueck zu `index-todo`."""
    proj = _resolve_or_fail(project)
    todo = places_module.places_todo(proj, day=day)
    if limit:
        todo = todo[:limit]
    if not todo:
        console.print("[green]Kein Asset mit unklarem Ort.[/green]")
        return
    console.print(json.dumps(todo, indent=2, ensure_ascii=False))
    console.print(
        f"[dim]{len(todo)} Asset(s). Ort setzen: frameforge set-place {project} <asset-id> "
        '--place "…" [--kind stop|leg][/dim]'
    )


@app.command(name="set-place")
def set_place_cmd(
    project: str,
    asset: str,
    place: str = typer.Option(..., "--place", help="Ortsname, z.B. 'Trollstigen'"),
    kind: str = typer.Option("stop", "--kind", help="stop = benannter Ort, leg = 'unterwegs: …'"),
) -> None:
    """Setzt den Ort eines Assets von Hand (Asset-ID oder Hash). Markiert ihn als `manual`."""
    proj = _resolve_or_fail(project)
    try:
        updated = places_module.set_place(proj, asset, place, kind=kind)
    except (KeyError, ValueError) as exc:
        raise _fail(str(exc)) from exc
    console.print(
        f"[green]{updated['id']}: Ort = {updated['gps']['place']} (manual)[/green]"
    )


@app.command(name="index")
def index_cmd(project: str) -> None:
    """Zeigt den Index-Stand und hebt die Phase auf INDEXED, sobald alles indiziert ist.

    Erfordert Projekt-Phase >= INGESTED. Die eigentliche Keyframe-/CV-Vorbereitung macht
    `frameforge prepare-index`; Beschreibung/Tags/Rating schreibt der `media-indexer`-Agent
    (Claude Vision auf den Keyframes), siehe `/ff-index`. Dieses Kommando meldet nur, welche
    Assets noch offen sind, und setzt die Phase, wenn `assets.json` alle abdeckt.
    """
    proj = _resolve_or_fail(project)
    state = proj.load_state()
    try:
        gate_index(state)
    except GateError as exc:
        raise _fail(str(exc)) from exc

    try:
        found = ingest_module.scan_media(proj.config.media_root)
    except FileNotFoundError as exc:
        raise _fail(str(exc)) from exc

    existing_hashes = {a.get("hash") for a in index_module.load_assets(proj)}
    pending = [p for p in found if ingest_module.hash_file(p) not in existing_hashes]

    console.print(f"{len(found)} Mediendateien gefunden, {len(pending)} noch nicht indiziert.")
    if not found:
        raise _fail("Keine Mediendateien gefunden — media_root pruefen, dann erneut ingest/index.")
    if not pending:
        # Alle gescannten Assets haben einen Eintrag in assets.json (vom media-indexer-Agenten
        # geschrieben) -> das Projekt gilt als vollstaendig indiziert. Das ist der einzige Ort,
        # der die Phase auf INDEXED hebt (Audit-Finding P1b: vorher erreichte kein Kommando
        # INDEXED, damit war design/brief nach dem P1-Gate unerreichbar).
        with ProjectState.transaction(proj.state_path) as tx:
            tx.ensure_project_at_least(Phase.INDEXED)
        console.print("[green]Alle Assets indiziert — Projekt-Phase: INDEXED.[/green]")
        return

    prepared = len(preindex_module.load_prep(proj))
    console.print(
        f"[yellow]Naechster Schritt:[/yellow] 'frameforge prepare-index {project}' "
        "(Keyframes + CV-Analyse), dann an den media-indexer-Agenten delegieren (siehe "
        f"/ff-index). Bereits vorbereitet (Prep vorhanden): {prepared}. Danach 'frameforge "
        "index' erneut, um die Phase auf INDEXED zu heben."
    )


@app.command(name="index-todo")
def index_todo(
    project: str,
    limit: int = typer.Option(None, "--limit", help="Nur die ersten N offenen Assets zeigen"),
) -> None:
    """Kompakte Worklist der noch nicht indizierten (vorbereiteten) Assets fuer den media-indexer.

    Eine Zeile je Asset: `hash | kind | source_guess | ein-Keyframe-Pfad`. Bewusst schlank —
    der Agent liest das Keyframe und ruft dann `frameforge index-asset`, ohne grosse JSON-Dumps.
    """
    proj = _resolve_or_fail(project)
    preps = preindex_module.load_prep(proj)
    if limit is not None:
        preps = preps[:limit]
    if not preps:
        console.print("Nichts offen — alle vorbereiteten Assets sind indiziert.")
        return
    # Plain-Ausgabe (typer.echo, nicht Rich): sonst bricht ein schmales Terminal die
    # Keyframe-Pfade um und der Agent parst sie falsch.
    for p in preps:
        kfs = p.get("keyframes", [])
        mid = next((k for k in kfs if "_kf01" in k), kfs[0] if kfs else "")
        digest = p["hash"].split(":")[-1]
        folder = p.get("path", "").split("/")[0]  # Tages-/Ort-Ordner als Kontext-Hinweis
        typer.echo(f"{digest}\t{p['kind']}\t{p.get('source_guess', 'unknown')}\t{folder}\t{mid}")
    typer.echo(f"# {len(preps)} offen. Spalten: hash|kind|quelle|ordner|keyframe. Dann 'index-asset'.")


@app.command(name="index-asset")
def index_asset_cmd(
    project: str,
    asset_hash: str = typer.Argument(..., help="Hash des Assets (Hex, aus 'index-todo')"),
    summary: str = typer.Option(..., "--summary", help="1 Satz, faktenbasiert"),
    tags: str = typer.Option(..., "--tags", help="Komma-getrennt, 4-8 kurze deutsche Tags"),
    usable_as: str = typer.Option("", "--usable", help="Komma-getrennt: establisher,b-roll,outro …"),
    rating: int = typer.Option(..., "--rating", help="1-5 Nutzbarkeit fuer den Schnitt"),
    source: str = typer.Option(..., "--source", help="drone/phone/camera/action_cam/unknown"),
    people: bool = typer.Option(False, "--people/--no-people", help="Personen im Bild?"),
    place: str = typer.Option(None, "--place", help="Ortsname (optional)"),
) -> None:
    """Schreibt einen indizierten Asset-Eintrag (Prep + Inhaltsfelder) — ein Befehl je Asset."""
    proj = _resolve_or_fail(project)
    digest = asset_hash if asset_hash.startswith("sha256:") else f"sha256:{asset_hash}"
    try:
        asset = preindex_module.index_prepared_asset(
            proj,
            digest,
            summary=summary,
            tags=[t.strip() for t in tags.split(",") if t.strip()],
            usable_as=[u.strip() for u in usable_as.split(",") if u.strip()],
            rating=rating,
            source=source,
            people=people,
            place=place,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise _fail(str(exc)) from exc
    console.print(f"[green]indiziert:[/green] {asset['id']}  (rating {rating}, {source})")


@app.command(name="prepare-index")
def prepare_index_cmd(
    project: str,
    filter_substr: str = typer.Option(
        None, "--filter", help="Nur Assets, deren Pfad diesen Teilstring enthaelt (z.B. ein Tag/Ordner)"
    ),
    limit: int = typer.Option(None, "--limit", help="Hoechstens so viele Assets neu vorbereiten"),
) -> None:
    """Keyframes + CV-Analyse fuer noch nicht indizierte Assets (Vorstufe zum media-indexer).

    Probe laeuft auf dem Original (EXIF/Quelle/GPS), CV-Analyse und Keyframe-Extraktion auf dem
    Proxy (schnell). Ergebnis: `prep/<hash>.json` + Keyframe-JPEGs im Cache. Idempotent —
    vorhandene Prep-Dateien und bereits indizierte Assets werden uebersprungen. `--filter` fuer
    etappenweises Indizieren (ein Reisetag), `--limit` zum Deckeln.
    """
    proj = _resolve_or_fail(project)
    try:
        gate_index(proj.load_state())
    except GateError as exc:
        raise _fail(str(exc)) from exc
    result = preindex_module.prepare_index(proj, filter_substr=filter_substr, limit=limit)
    console.print(
        f"[green]{len(result.prepared)} Asset(s) vorbereitet[/green] "
        f"(uebersprungen: {result.skipped_existing} bereits vorbereitet, "
        f"{result.skipped_indexed} bereits indiziert)."
    )
    if result.failures:
        console.print(f"[yellow]{len(result.failures)} Fehlschlag/-schlaege:[/yellow]")
        for f in result.failures:
            console.print(f"  {f.asset.name}: {f.reason}")
    if result.prepared:
        console.print(
            "Naechster Schritt: an den media-indexer delegieren (er liest die Prep-Dateien + "
            "Keyframes, schreibt Beschreibung/Tags/Rating), dann 'frameforge index'."
        )


@app.command()
def query(
    project: str,
    tag: str = typer.Option(None),
    place: str = typer.Option(None),
    min_rating: int = typer.Option(None),
    kind: str = typer.Option(None),
    person: str = typer.Option(None, help="Nur Assets mit dieser (benannten) Person"),
    source: str = typer.Option(None, help="Nur diese Quelle: drone/phone/camera/action_cam"),
) -> None:
    """Kompaktes JSON aus `assets.json`, gefiltert — statt ganze Verzeichnisse zu lesen.

    `--source drone` liefert z.B. nur Drohnen-Shots; `--person <name>` filtert auf Assets, in
    denen die per `name-person` benannte Person vorkommt (setzt `frameforge faces` voraus).
    """
    proj = _resolve_or_fail(project)
    results = index_module.query_assets(
        proj, tag=tag, place=place, min_rating=min_rating, kind=kind, source=source
    )
    if person is not None:
        allowed = set(people_module.assets_for_person(proj, person))
        results = [a for a in results if a.get("id") in allowed]
    console.print_json(json.dumps(results))


def _print_design_inventory(proj: Project) -> None:
    """Zeigt Tokens-Status, Schriften und das Grafik-Inventar (angefordert vs. abgelegt)."""
    tokens_ok = proj.design_tokens_path.exists()
    console.print(
        f"tokens.yaml: {'[green]✓ vorhanden[/green]' if tokens_ok else '[yellow]✗ fehlt[/yellow]'}"
    )
    fonts = (
        sorted(p.name for p in proj.design_fonts_dir.iterdir() if p.is_file())
        if proj.design_fonts_dir.is_dir()
        else []
    )
    if fonts:
        console.print(f"Schriften (design/fonts/): {', '.join(fonts)}")

    inv = design.asset_inventory(proj)
    if not inv.requested and not inv.present:
        console.print("Grafiken: keine angefordert, keine abgelegt (Text-Overlays reichen).")
        return
    table = Table(title="Design-Grafiken (design/assets/)")
    table.add_column("Datei")
    table.add_column("Status")
    for name in inv.requested:
        present = name in {p.lower() for p in inv.present}
        table.add_row(name, "[green]✓ abgelegt[/green]" if present else "[yellow]✗ fehlt noch[/yellow]")
    for name in inv.extra:
        table.add_row(name, "[dim]zusätzlich (nicht angefordert)[/dim]")
    console.print(table)
    if inv.missing:
        console.print(
            f"[yellow]{len(inv.missing)} Grafik(en) fehlen noch:[/yellow] {', '.join(inv.missing)}. "
            "Prompts in design/prompts.md, Bilder nach design/assets/ ablegen — sind optional."
        )
    else:
        console.print("[green]Alle angeforderten Grafiken sind abgelegt.[/green]")


@app.command(name="design-status")
def design_status(project: str) -> None:
    """Read-only: Design-Stand zeigen (tokens.yaml, Schriften, Grafik-Inventar).

    Praktisch beim Wiedereinstieg nach dem externen Erstellen von Logo/Marker/Freistellern:
    zeigt, welche angeforderten Grafiken schon in `design/assets/` liegen und welche fehlen.
    """
    proj = _resolve_or_fail(project)
    _print_design_inventory(proj)


@app.command(name="design")
def design_cmd(project: str) -> None:
    """Uebernimmt `design/tokens.yaml` als Designsystem, setzt Projekt-Phase auf DESIGNED.

    Der eigentliche Wizard (Stimmung -> Farbpalette/Typo -> Motion -> Asset-Inventur) ist
    Sache des `design-system`-Agenten (`/ff-design`) — der schreibt `tokens.yaml`, bevor dieses
    Kommando läuft. Zeigt danach das Grafik-Inventar (angefordert vs. abgelegt).
    """
    proj = _resolve_or_fail(project)
    if not proj.design_tokens_path.exists():
        raise _fail(
            f"{proj.design_tokens_path} fehlt — zuerst Tokens definieren (siehe /ff-design)"
        )
    try:
        with ProjectState.transaction(proj.state_path) as state:
            gate_design(state)
            state.advance_project(Phase.DESIGNED)
    except GateError as exc:
        raise _fail(str(exc)) from exc
    console.print(f"[green]Designsystem uebernommen:[/green] {proj.design_tokens_path}")
    _print_design_inventory(proj)


@app.command()
def brief(project: str, export: str) -> None:
    """Prueft nur das Gate (Projekt-Phase >= DESIGNED). Das Briefing selbst fuehrt der

    `/ff-brief`-Wizard mit dem Nutzer durch und schreibt `brief.yaml` — nicht diese CLI.
    """
    proj = _resolve_or_fail(project)
    state = proj.load_state()
    try:
        gate_brief(state)
    except GateError as exc:
        raise _fail(str(exc)) from exc
    console.print(
        f"[yellow]Gate offen fuer '{export}'.[/yellow] Das Briefing macht der /ff-brief-Wizard "
        "(schreibt brief.yaml), nicht dieses Kommando."
    )
    raise typer.Exit(code=1)


@app.command(name="brief-show")
def brief_show(project: str, export: str) -> None:
    """Gibt den *aufgeloesten* Brief als YAML aus (Preset-Parameter untergelegt, inkl. `arc`).

    Fuer den Orchestrator/story-architect: zeigt die vollstaendige Sicht (pacing,
    transition_vocabulary, music_energy_curve, text_density, map_usage, arc ...), die der
    Brief selbst nur ueber `preset:` referenziert.
    """
    proj = _resolve_or_fail(project)
    exp = proj.export(export)
    if not exp.brief_path.exists():
        raise _fail(f"Export '{export}' hat kein brief.yaml.")
    try:
        merged = brief_module.Brief.load(exp.brief_path).merged()
    except brief_module.BriefError as exc:
        raise _fail(str(exc)) from exc
    import yaml as _yaml

    console.print(_yaml.safe_dump(merged, allow_unicode=True, sort_keys=False).rstrip())


@app.command()
def build(project: str, export: str) -> None:
    """Prueft nur das Gate (Export-Phase >= BRIEFED). Beat-Sheet und `timeline.json` bauen

    die Sub-Agenten `story-architect`/`timeline-builder` (siehe `/ff-build`), nicht diese CLI.
    """
    proj = _resolve_or_fail(project)
    state = proj.load_state()
    try:
        gate_build(state, export)
    except GateError as exc:
        raise _fail(str(exc)) from exc
    exp = proj.export(export)
    # Phase mitziehen, sobald die Agenten geliefert haben. Vorher hob kein Kommando den Export
    # ueber BRIEFED hinaus; damit gab es auch keinen Zeitpunkt, an dem sich der Stand des
    # Asset-Inventars festhalten liess (Plan 0003 §G).
    if not exp.beatsheet_path.exists():
        console.print(
            f"[yellow]Gate offen fuer '{export}'.[/yellow] Beat-Sheet und Timeline bauen die "
            "Agenten des /ff-build-Ablaufs (story-architect + timeline-builder), nicht dieses "
            "Kommando."
        )
        raise typer.Exit(code=1)

    # `TIMELINE` nur setzen, wenn die Datei auch **lesbar und schema-gueltig** ist. Sonst meldet
    # erst der Preview den Fehler, obwohl der Status bereits "fertig gebaut" behauptet.
    timeline_ok = False
    if exp.timeline_path.exists():
        try:
            Timeline.load(exp.timeline_path).validate_semantics()
            timeline_ok = True
        except (ValidationError, TimelineValidationError, ValueError) as exc:
            console.print(f"[red]timeline.json ist ungueltig:[/red] {exc}")

    fingerprint = pipeline_module.asset_inventory_fingerprint(proj)
    with ProjectState.transaction(proj.state_path) as tx:
        tx.advance_export(export, Phase.STORYBOARDED)
        tx.set_export_hash(export, pipeline_module.ASSET_INVENTORY_KEY, fingerprint)
        if timeline_ok:
            tx.advance_export(export, Phase.TIMELINE)
    if timeline_ok:
        console.print(f"[green]Beat-Sheet und Timeline vorhanden — '{export}' ist TIMELINE.[/green]")
    elif exp.timeline_path.exists():
        console.print(
            f"[yellow]'{export}' bleibt STORYBOARDED[/yellow] — die timeline.json muss erst "
            "korrigiert werden (timeline-builder), dann 'frameforge build' erneut."
        )
        raise typer.Exit(code=1)
    else:
        console.print(
            f"[green]Beat-Sheet vorhanden — '{export}' ist STORYBOARDED.[/green] Jetzt fehlt "
            "noch die timeline.json (timeline-builder), dann 'frameforge build' erneut."
        )


def _music_durations(proj, timeline) -> dict[str, float]:
    """Laufzeit jeder in der Timeline referenzierten Musikdatei, fuer `qc.validate`.

    Ein zu kurzer Track laesst den Film stumm zu Ende laufen, ohne Fehlermeldung (gefunden
    2026-08-09: 11,4s Stille am Schluss von `vlog-edit`). Nicht ermittelbare Dateien werden
    weggelassen statt gemeldet -- die Pruefung ist eine Zusatzsicherung, kein Gatekeeper fuer
    exotische Formate.
    """
    def duration_of(src: str) -> float | None:
        try:
            return probe_module.probe_duration(proj.root / src)
        except Exception:  # noqa: BLE001 -- fehlende/unlesbare Datei faellt woanders auf
            return None

    durations: dict[str, float] = {}
    for clip in timeline.tracks.audio:
        src = getattr(clip, "src", None)
        if not src or str(src) in durations:
            continue
        found = duration_of(str(src))
        if found is not None:
            durations[str(src)] = found
    return durations


@app.command()
def preview(project: str, export: str) -> None:
    """1080p-Proxy-Render. Erfordert `timeline.json` + Export-Phase >= TIMELINE + QC-Pass."""
    proj = _resolve_or_fail(project)
    exp = proj.export(export)
    state = proj.load_state()
    try:
        gate_preview(state, export, timeline_exists=exp.timeline_path.exists())
    except (GateError, StateError) as exc:
        raise _fail(str(exc)) from exc

    drift = pipeline_module.asset_drift(proj, state, export)
    if drift:
        console.print(f"[yellow]Hinweis:[/yellow] {drift}")

    timeline = Timeline.load(exp.timeline_path)
    try:
        brief = brief_module.Brief.load(exp.brief_path).merged() if exp.brief_path.exists() else None
    except brief_module.BriefError as exc:
        raise _fail(str(exc)) from exc
    assets = index_module.load_assets(proj)
    known_ids = {a["id"] for a in assets}
    # Quell-Laufzeiten mitgeben: ein `src_out` ueber die Cliplaenge hinaus kappt sonst still den
    # gesamten Film (gefunden 2026-08-09, Preview war 26,7s statt 18 Minuten lang).
    durations = {
        a["id"]: (a.get("probe") or {}).get("dur")
        for a in assets
        if a.get("kind") != "photo" and (a.get("probe") or {}).get("dur")
    }
    issues = qc.validate(
        timeline, brief=brief, known_asset_ids=known_ids, asset_durations=durations,
        music_durations=_music_durations(proj, timeline),
    )
    if issues:
        for issue in issues:
            console.print(f"[red]QC:[/red] {issue}")
        raise typer.Exit(code=1)

    try:
        out_path = render_module.render_proxy(
            proj, exp, timeline, color_grade=(brief or {}).get("color_grade")
        )
    except render_module.RenderError as exc:
        raise _fail(str(exc)) from exc

    with ProjectState.transaction(proj.state_path) as tx:
        tx.advance_export(export, Phase.PREVIEWED)
    console.print(f"[green]Preview gerendert:[/green] {out_path}")


@app.command()
def render(
    project: str,
    export: str,
    lut: Path = typer.Option(None, "--lut", help="Optionale 3D-LUT (.cube) fuer Farbkorrektur"),  # noqa: B008
    resolution: str = typer.Option(None, "--resolution", help="Ausgabe-Aufloesung, z.B. 1920x1080"),
    crf: int = typer.Option(18, "--crf", help="Qualitaet (kleiner = besser, groesser = kleinere Datei)"),
    preset: str = typer.Option("medium", "--preset", help="x264-Preset (fast/medium/slow)"),
    chunk_s: float = typer.Option(
        None, "--chunk-s",
        help="Chunk-Render: Film in Stuecke von ~N Sekunden rendern und ohne Neukodierung "
             "zusammensetzen (noetig, wenn zu viele gleichzeitig offene Inputs den RAM sprengen)",
    ),
) -> None:
    """Final-Render. Erfordert Export-Phase == APPROVED (explizite Freigabe nach Preview)."""
    proj = _resolve_or_fail(project)
    exp = proj.export(export)
    if lut is not None and not lut.exists():
        raise _fail(f"LUT-Datei nicht gefunden: {lut}")
    lut_path = lut
    res_tuple = None
    if resolution is not None:
        try:
            w, h = (int(x) for x in resolution.lower().split("x"))
            res_tuple = (w, h)
        except ValueError:
            raise _fail(f"--resolution '{resolution}' ungueltig — Format WxH, z.B. 1920x1080") from None
    state = proj.load_state()
    try:
        gate_render_final(state, export)
    except GateError as exc:
        raise _fail(str(exc)) from exc

    drift = pipeline_module.asset_drift(proj, state, export)
    if drift:
        console.print(f"[yellow]Hinweis:[/yellow] {drift}")

    # Freigabe an den Timeline-Stand binden: wurde timeline.json seit dem approve geaendert,
    # ist die Freigabe veraltet und der Final-Render wird blockiert (Audit P3).
    approved_fp = state.get_export_hash(export, "timeline")
    current_fp = qc.timeline_fingerprint(exp.timeline_path)
    if approved_fp is not None and current_fp != approved_fp:
        raise _fail(
            "timeline.json wurde seit der Freigabe geaendert — Freigabe ist veraltet. "
            "Erneut 'frameforge preview' und 'frameforge approve' ausfuehren."
        )

    timeline = Timeline.load(exp.timeline_path)
    # QC vor dem Final-Render wiederholen (nicht nur beim Preview vertrauen).
    try:
        brief = brief_module.Brief.load(exp.brief_path).merged() if exp.brief_path.exists() else None
    except brief_module.BriefError as exc:
        raise _fail(str(exc)) from exc
    assets = index_module.load_assets(proj)
    known_ids = {a["id"] for a in assets}
    # Quell-Laufzeiten mitgeben: ein `src_out` ueber die Cliplaenge hinaus kappt sonst still den
    # gesamten Film (gefunden 2026-08-09, Preview war 26,7s statt 18 Minuten lang).
    durations = {
        a["id"]: (a.get("probe") or {}).get("dur")
        for a in assets
        if a.get("kind") != "photo" and (a.get("probe") or {}).get("dur")
    }
    issues = qc.validate(
        timeline, brief=brief, known_asset_ids=known_ids, asset_durations=durations,
        music_durations=_music_durations(proj, timeline),
    )
    if issues:
        for issue in issues:
            console.print(f"[red]QC:[/red] {issue}")
        raise typer.Exit(code=1)

    try:
        out_path = render_module.render_final(
            proj, exp, timeline, lut_path=lut_path, resolution=res_tuple, crf=crf, preset=preset,
            color_grade=(brief or {}).get("color_grade"),
            chunk_s=chunk_s,
            on_progress=lambda msg: console.print(f"[dim]{msg}[/dim]"),
        )
    except render_module.RenderError as exc:
        raise _fail(str(exc)) from exc

    with ProjectState.transaction(proj.state_path) as tx:
        tx.advance_export(export, Phase.RENDERED)

    # Datenblatt neben den Final-Render legen (<stem>.report.md).
    report_path = out_path.parent / f"{out_path.stem}.report.md"
    report_path.write_text(stats_module.build_report(proj, exp, timeline))
    console.print(f"[green]Final-Render fertig:[/green] {out_path}")
    console.print(f"[green]Report:[/green] {report_path}")


@app.command()
def nle(
    project: str,
    export: str,
    nle_format: str = typer.Option("fcpxml", "--format", help="fcpxml oder otio"),
) -> None:
    """FCPXML/OTIO-Export fuer DaVinci Resolve. Erfordert eine gebaute `timeline.json`."""
    if nle_format not in ("fcpxml", "otio"):
        raise _fail("--format muss 'fcpxml' oder 'otio' sein")

    proj = _resolve_or_fail(project)
    exp = proj.export(export)
    if not exp.timeline_path.exists():
        raise _fail(f"{exp.timeline_path} existiert nicht — zuerst 'frameforge build' ausfuehren")

    timeline = Timeline.load(exp.timeline_path)
    assets_by_id = {a["id"]: a for a in index_module.load_assets(proj)}

    def resolve(asset_id: str) -> Path:
        asset = assets_by_id.get(asset_id)
        if asset is None:
            raise _fail(f"Asset '{asset_id}' nicht in assets.json gefunden")
        try:
            return resolve_media_path(proj.config.media_root, asset["path"])
        except UnsafePathError as exc:
            raise _fail(str(exc)) from exc

    exp.nle_dir.mkdir(parents=True, exist_ok=True)
    out_path = exp.nle_dir / f"{export}.{nle_format}"
    export_fn = nle_module.export_fcpxml if nle_format == "fcpxml" else nle_module.export_otio
    export_fn(timeline, out_path, resolve_asset=resolve, project_root=proj.root)
    console.print(f"[green]NLE-Export fertig:[/green] {out_path}")


def _print_people(proj: Project, crops: dict[str, Path] | None = None) -> None:
    """Zeigt die Personen-Cluster als Tabelle: Cluster, Name (falls gesetzt), #Assets, Crop."""
    clusters = people_module.load_clusters(proj)
    if not clusters:
        console.print("Noch keine Personen-Cluster — zuerst 'frameforge faces' ausfuehren.")
        return
    names = people_module.load_people_names(proj)
    crops = crops or {}
    table = Table(title="Personen")
    table.add_column("Cluster")
    table.add_column("Name")
    table.add_column("#Assets", justify="right")
    table.add_column("Gesichts-Ausschnitt")
    for key in sorted(clusters):
        table.add_row(
            key,
            names.get(key, "[dim]—[/dim]"),
            str(len(clusters[key])),
            str(crops.get(key, "")),
        )
    console.print(table)
    unnamed = [k for k in clusters if k not in names]
    if unnamed:
        console.print(
            f"[yellow]{len(unnamed)} Cluster noch ohne Namen.[/yellow] Benennen: "
            "'frameforge name-person <projekt> <cluster> <name>'."
        )


@app.command()
def people(project: str) -> None:
    """Personen-Cluster anzeigen (Cluster, Name, Anzahl Assets). Namen setzt `name-person`."""
    proj = _resolve_or_fail(project)
    _print_people(proj)


@app.command(name="name-person")
def name_person(project: str, cluster: str, name: str) -> None:
    """Benennt einen Personen-Cluster (`person_1` → z.B. `Oskar`).

    `cluster` darf ein Cluster-Key (`person_1`) oder ein bereits vergebener Name (Umbenennen)
    sein. Danach versteht `frameforge query --person <name>` bzw. der Brief den Namen.
    """
    proj = _resolve_or_fail(project)
    try:
        key = people_module.set_person_name(proj, cluster, name)
    except KeyError as exc:
        raise _fail(str(exc)) from exc
    n_assets = len(people_module.load_clusters(proj).get(key, []))
    console.print(f"[green]{key} = '{name}'[/green] ({n_assets} Assets)")


@app.command()
def exclude(
    project: str,
    asset_id: str,
    reason: str = typer.Option("", "--reason", help="Warum (Notiz, optional)"),
    undo: bool = typer.Option(False, "--undo", help="Sperre wieder aufheben"),
) -> None:
    """Sperrt ein Asset dauerhaft fuer ALLE Exporte (z.B. Fehlaufnahme) — oder hebt die Sperre auf.

    Setzt `exclude` im `assets.json`-Eintrag; `frameforge query` (und damit die Clip-Auswahl
    aller Filme) ueberspringt gesperrte Assets. `--undo` entfernt die Sperre.
    """
    proj = _resolve_or_fail(project)
    assets = {a["id"]: a for a in index_module.load_assets(proj)}
    asset = assets.get(asset_id)
    if asset is None:
        raise _fail(f"Asset '{asset_id}' nicht in assets.json.")
    if undo:
        asset.pop("exclude", None)
        asset.pop("exclude_reason", None)
    else:
        asset["exclude"] = True
        if reason:
            asset["exclude_reason"] = reason
    index_module.write_asset(proj, asset)
    state = "entsperrt" if undo else "gesperrt"
    console.print(f"[green]Asset '{asset_id}' {state}.[/green]" + (f" ({reason})" if reason and not undo else ""))


@app.command()
def faces(project: str) -> None:
    """Gesichtserkennung fuer Foto-Assets — expliziter Opt-in, kein Teil von `frameforge index`.

    Verarbeitet biometrische Daten (siehe `frameforge.people`-Datenschutzhinweis). Schreibt
    `index/people.json` (Encodings pro Asset) und `index/people_clusters.json`
    (Personen-Cluster) — beide sind per `.gitignore` vom Tracking ausgeschlossen. Die
    Gesichts-Ausschnitte pro Cluster (fuers Benennen) landen im Cache.
    """
    proj = _resolve_or_fail(project)
    photo_assets = [a for a in index_module.load_assets(proj) if a.get("kind") == "photo"]
    if not photo_assets:
        console.print("Keine Foto-Assets in assets.json gefunden.")
        return

    faces_by_asset: dict[str, list] = {}
    for asset in photo_assets:
        try:
            path = resolve_media_path(proj.config.media_root, asset["path"])
            detected = people_module.detect_faces(path)
        except (people_module.FaceDetectionError, UnsafePathError) as exc:
            console.print(f"[yellow]Warnung:[/yellow] {exc}")
            continue
        if detected:
            faces_by_asset[asset["id"]] = detected

    proj.index_dir.mkdir(parents=True, exist_ok=True)
    people_path = proj.index_dir / "people.json"
    people_path.write_text(json.dumps(faces_by_asset, indent=2))

    encodings_by_asset = {
        asset_id: [face["encoding"] for face in faces] for asset_id, faces in faces_by_asset.items()
    }
    detailed = people_module.cluster_people_detailed(encodings_by_asset)
    clusters = {key: sorted({aid for aid, _ in members}) for key, members in detailed.items()}
    clusters_path = proj.index_dir / "people_clusters.json"
    clusters_path.write_text(json.dumps(clusters, indent=2))

    # Repraesentative Gesichts-Ausschnitte pro Cluster (fuers Benennen) in den Cache.
    def _resolve(asset_id: str) -> Path:
        asset = next(a for a in photo_assets if a["id"] == asset_id)
        return resolve_media_path(proj.config.media_root, asset["path"])

    crops_dir = proj.cache_dir / "people_crops"
    crops = people_module.write_representative_crops(faces_by_asset, detailed, _resolve, crops_dir)

    total_faces = sum(len(v) for v in faces_by_asset.values())
    console.print(
        f"[green]{total_faces} Gesichter in {len(faces_by_asset)} von {len(photo_assets)} "
        f"Fotos, {len(clusters)} Personen-Cluster.[/green]"
    )
    if crops:
        console.print(
            f"Gesichts-Ausschnitte pro Cluster: {crops_dir}\n"
            "Zum Benennen: die Crops ansehen und 'frameforge name-person "
            "<projekt> <cluster> <name>' setzen (oder ueber /ff-wizard fuehren lassen)."
        )
    _print_people(proj, crops)


@app.command()
def approve(project: str, export: str) -> None:
    """Explizite Freigabe eines Exports nach dem Preview. Erfordert Export-Phase == PREVIEWED."""
    proj = _resolve_or_fail(project)
    exp = proj.export(export)
    current = proj.load_state().export_phase(export)
    if current != Phase.PREVIEWED:
        raise _fail(
            f"Export '{export}' ist in Phase {current.name} — Freigabe erst nach PREVIEWED moeglich"
        )
    if not typer.confirm(f"Export '{export}' fuer Final-Render freigeben?"):
        raise typer.Exit(code=1)
    with ProjectState.transaction(proj.state_path) as state:
        # Innerhalb der Transaktion erneut pruefen — zwischen Anzeige und Bestaetigung koennte
        # sich der Zustand geaendert haben.
        if state.export_phase(export) != Phase.PREVIEWED:
            raise _fail(f"Export '{export}' ist nicht mehr in Phase PREVIEWED — abgebrochen.")
        state.advance_export(export, Phase.APPROVED)
        # Freigabe an den exakten Timeline-Stand binden, damit render eine nachtraegliche
        # Aenderung erkennt (Audit P3).
        state.set_export_hash(export, "timeline", qc.timeline_fingerprint(exp.timeline_path))
    console.print(f"[green]Export '{export}' freigegeben (APPROVED)[/green]")


def _stats_table(title: str, rows: dict) -> Table:
    table = Table(title=title, show_header=False)
    table.add_column()
    table.add_column(justify="right")
    for key, value in rows.items():
        table.add_row(str(key), str(value))
    return table


@app.command()
def stats(project: str) -> None:
    """Index-Statistik: Fundus-Umfang, Qualitaet, Aufloesungen, Orte, Nutzung je Export."""
    proj = _resolve_or_fail(project)
    idx = stats_module.index_stats(proj)
    usage = stats_module.usage_stats(proj)

    if idx.indexed == 0:
        console.print("Noch nichts indiziert — zuerst 'frameforge index' ausfuehren.")
        return

    coverage = (
        f"{idx.indexed}/{idx.on_disk} indiziert ({idx.indexed_coverage:.0%})"
        if idx.on_disk
        else f"{idx.indexed} indiziert (Quellordner nicht erreichbar)"
    )
    console.print(
        _stats_table(
            f"{proj.name} — Fundus",
            {
                "Assets (Index)": f"{idx.indexed}  ({idx.videos} Video, {idx.photos} Foto)",
                "Dateien im Quellordner": coverage,
                "Rohmaterial (Video)": f"{idx.total_video_seconds:.0f} s",
                "mit Personen": idx.with_people,
            },
        )
    )
    if idx.avg_quality:
        console.print(_stats_table("Qualitaet (Ø Video)", idx.avg_quality))
    if idx.rating_hist:
        console.print(_stats_table("Ratings", {f"{k}★": v for k, v in idx.rating_hist.items()}))
    if idx.resolutions:
        console.print(_stats_table("Aufloesungen", idx.resolutions))
    if idx.codecs:
        console.print(_stats_table("Codecs", idx.codecs))
    if idx.places:
        console.print(_stats_table("Orte", idx.places))

    # Inhalts-Zusammensetzung (Anteile in Sekunden + %).
    comp = stats_module.content_composition(proj)
    total_s = comp["total_video_seconds"] or 1  # Division vermeiden

    def _share(bucket: dict) -> str:
        return f"{bucket['count']}× · {bucket['seconds']:.0f}s ({100 * bucket['seconds'] / total_s:.0f}%)"

    console.print(
        _stats_table(
            "Zusammensetzung",
            {
                "Video": _share(comp["by_kind"]["video"]),
                "Foto": f"{comp['by_kind']['photo']['count']}× (Standbilder)",
                "mit Personen": _share(comp["people"]["mit_personen"]),
                "ohne Personen (Landschaft o.ae.)": _share(comp["people"]["ohne_personen"]),
            },
        )
    )
    if comp.get("by_source"):
        console.print(
            _stats_table("Quelle/Kamera", {k: _share(v) for k, v in comp["by_source"].items()})
        )
    if comp["motion"]:
        console.print(
            _stats_table("Kamera/Motion (Video)", {k: _share(v) for k, v in comp["motion"].items()})
        )
    if comp["top_tags"]:
        console.print(_stats_table("Top-Motive (Tags)", dict(comp["top_tags"])))

    presence = stats_module.person_presence(proj)
    if presence:
        console.print(
            _stats_table(
                "Personen (benannt)",
                {name: f"{v['assets']} Assets · {v['seconds']:.0f}s" for name, v in presence.items()},
            )
        )

    if usage.per_export:
        rows = {name: f"{n} Assets" for name, n in usage.per_export.items()}
        union = (
            f"{len(usage.used_union)}/{usage.total_assets} ({usage.union_coverage:.0%})"
            if usage.union_coverage is not None
            else str(len(usage.used_union))
        )
        rows["— gesamt genutzt"] = union
        console.print(_stats_table("Nutzung je Export", rows))
    else:
        console.print("Noch kein Export mit Timeline — Nutzungsstatistik folgt nach 'build'.")


@app.command()
def days(project: str) -> None:
    """Schreibt Tageszusammenfassungen nach `index/days/<datum>.md` (Orte, Motive, Highlights).

    Überblick über den Trip Tag für Tag — hilft der Dramaturgie (v.a. beim Chronikel-Stil).
    """
    proj = _resolve_or_fail(project)
    summaries = stats_module.day_summaries(proj)
    if not summaries:
        console.print("Noch keine Assets mit Aufnahmedatum — zuerst 'frameforge index'.")
        return
    written = stats_module.write_day_summaries(proj)
    table = Table(title="Tageszusammenfassungen")
    table.add_column("Tag")
    table.add_column("Assets", justify="right")
    table.add_column("Orte")
    for day, s in summaries.items():
        table.add_row(day, str(s["assets"]), ", ".join(s["places"]) or "—")
    console.print(table)
    console.print(f"[green]{len(written)} Datei(en) geschrieben nach[/green] {proj.days_dir}")


@app.command()
def report(project: str, export: str) -> None:
    """Schreibt ein Markdown-Datenblatt zum Export nach `exports/<export>/report.md`.

    Beim Final-Render entsteht ohnehin automatisch ein Report neben dem MP4; dieses Kommando
    erzeugt ihn auch ohne (erneuten) Render, z.B. nach dem Preview.
    """
    proj = _resolve_or_fail(project)
    exp = proj.export(export)
    if not exp.timeline_path.exists():
        raise _fail(f"{exp.timeline_path} existiert nicht — zuerst 'frameforge build' ausfuehren")
    timeline = Timeline.load(exp.timeline_path)
    out_path = exp.root / "report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(stats_module.build_report(proj, exp, timeline))
    console.print(f"[green]Report geschrieben:[/green] {out_path}")


@app.command(name="list")
def list_cmd() -> None:
    """Alle Projekte unter `projects/`."""
    projects = list_projects()
    if not projects:
        console.print("keine Projekte")
        return
    for name in projects:
        console.print(name)


@app.command(name="themes")
def themes_cmd() -> None:
    """Design-Token-Themes auflisten (Farb-/Typo-Startsets fuer das Designsystem).

    Mit `frameforge apply-theme <projekt> <slug>` als Ausgangspunkt nach design/tokens.yaml
    schreiben und dann anpassen.
    """
    themes = themes_module.list_themes()
    table = Table(title="Design-Themes")
    table.add_column("Slug", style="bold")
    table.add_column("Name")
    for t in themes:
        slug = t["slug"] + (" [dim](eigen)[/dim]" if t.get("custom") else "")
        table.add_row(slug, t["name"])
    console.print(table)
    for t in themes:
        console.print(f"\n[bold]{t['slug']}[/bold] — {t['description']}")
        if t.get("example"):
            console.print(f"  [dim]Beispiel:[/dim] {t['example']}")
    console.print(
        "\n[dim]Eigenes Theme: 'frameforge theme-new <slug>', dann apply-theme.[/dim]"
    )


@app.command(name="apply-theme")
def apply_theme_cmd(project: str, theme: str) -> None:
    """Schreibt ein Design-Theme als Startpunkt nach `design/tokens.yaml` (dann anpassen)."""
    proj = _resolve_or_fail(project)
    if proj.design_tokens_path.exists() and not typer.confirm(
        f"{proj.design_tokens_path} existiert bereits — mit Theme '{theme}' ueberschreiben?"
    ):
        raise typer.Exit(code=1)
    try:
        out = themes_module.apply_theme(theme, proj.design_tokens_path)
    except themes_module.ThemeNotFoundError as exc:
        raise _fail(str(exc)) from exc
    console.print(f"[green]Theme '{theme}' uebernommen:[/green] {out}  (jetzt anpassen)")


def _dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


@app.command()
def clean(project: str) -> None:
    """Loescht den Cache eines Projekts (Proxies, Keyframes, Gesichts-Crops, Karten-Frames).

    Alles regenerierbar (ingest/index bauen es neu). Rohmaterial und Projektdateien bleiben
    unberuehrt.
    """
    proj = _resolve_or_fail(project)
    cache = proj.cache_dir
    size = _dir_size(cache)
    if not cache.exists() or size == 0:
        console.print("Cache ist bereits leer.")
        return
    if not typer.confirm(f"{_human_size(size)} Cache unter {cache} loeschen?"):
        raise typer.Exit(code=1)
    shutil.rmtree(cache, ignore_errors=True)
    console.print(f"[green]{_human_size(size)} freigegeben[/green] ({cache})")


@app.command(name="clone-export")
def clone_export(project: str, source: str, target: str) -> None:
    """Legt einen neuen Export an, indem der Brief eines bestehenden als Startpunkt kopiert wird.

    Spart das Neu-Tippen bei Varianten (z.B. teaser -> hauptfilm). Der Ziel-Export beginnt bei
    Phase BRIEFED; Beat-Sheet/Timeline werden NICHT kopiert (die sollen neu entstehen).
    """
    proj = _resolve_or_fail(project)
    src, dst = proj.export(source), proj.export(target)
    if not src.brief_path.exists():
        raise _fail(f"Quell-Export '{source}' hat kein brief.yaml — nichts zu kopieren.")
    if dst.brief_path.exists():
        raise _fail(f"Ziel-Export '{target}' hat bereits ein brief.yaml — abgebrochen.")
    dst.ensure_dirs()
    dst.brief_path.write_text(src.brief_path.read_text())
    with ProjectState.transaction(proj.state_path) as state:
        state.advance_export(target, Phase.BRIEFED)
    console.print(
        f"[green]Export '{target}' aus '{source}' angelegt[/green] (brief.yaml kopiert). "
        "Brief anpassen, dann /ff-build."
    )


@app.command(name="presets")
def presets_cmd() -> None:
    """Verfuegbare Stil-Presets auflisten (fuer den Brief eines Exports).

    Ein Preset gibt den Grundton vor (Pacing, Uebergaenge, Color-Grade, Musik-Energie ...).
    Im brief.yaml `preset: <slug>` setzen; einzelne Parameter kann man dort ueberschreiben.
    """
    presets = presets_module.list_presets()
    table = Table(title="Stil-Presets")
    table.add_column("Slug", style="bold")
    table.add_column("Name")
    table.add_column("Passt zu")
    for p in presets:
        slug = p["slug"] + (" [dim](eigen)[/dim]" if p.get("custom") else "")
        table.add_row(slug, p["name"], p["best_for"])
    console.print(table)
    for p in presets:
        console.print(f"\n[bold]{p['slug']}[/bold] — {p['description']}")
        if p.get("example"):
            console.print(f"  [dim]Beispiel:[/dim] {p['example']}")
        if p.get("arc"):
            console.print(f"  [dim]Bogen:[/dim] {p['arc']}")
    console.print(
        "\n[dim]Eigenes Preset: 'frameforge preset-new <slug>' oder Parameter direkt im "
        "brief.yaml (ohne preset:).[/dim]"
    )


@app.command(name="preset-new")
def preset_new(slug: str) -> None:
    """Geruestet ein eigenes Preset unter ~/.frameforge/presets/<slug>.yaml (dann bearbeiten)."""
    try:
        validate_name(slug, kind="Preset-Slug")
    except UnsafeNameError as exc:
        raise _fail(str(exc)) from exc
    try:
        path = presets_module.scaffold_preset(slug)
    except FileExistsError as exc:
        raise _fail(str(exc)) from exc
    console.print(
        f"[green]Preset-Vorlage angelegt:[/green] {path}\n"
        "Bearbeiten, dann im brief.yaml als 'preset: " + slug + "' waehlen."
    )


@app.command(name="theme-new")
def theme_new(slug: str) -> None:
    """Geruestet ein eigenes Design-Theme unter ~/.frameforge/themes/<slug>.yaml (dann bearbeiten)."""
    try:
        validate_name(slug, kind="Theme-Slug")
    except UnsafeNameError as exc:
        raise _fail(str(exc)) from exc
    try:
        path = themes_module.scaffold_theme(slug)
    except FileExistsError as exc:
        raise _fail(str(exc)) from exc
    console.print(
        f"[green]Theme-Vorlage angelegt:[/green] {path}\n"
        "Bearbeiten, dann mit 'frameforge apply-theme <projekt> " + slug + "' uebernehmen."
    )


if __name__ == "__main__":
    app()
