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
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table

from frameforge import design, qc
from frameforge import index as index_module
from frameforge import ingest as ingest_module
from frameforge import nle as nle_module
from frameforge import people as people_module
from frameforge import pipeline as pipeline_module
from frameforge import render as render_module
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
from frameforge.timeline import Timeline

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
    pipeline = pipeline_module.build_pipeline(project, state, exports=proj.list_exports())
    for line in pipeline_module.format_pipeline(pipeline):
        console.print(_colorize_pipeline_line(line) if line.strip() else line)


# -- Pipeline-Kommandos ---------------------------------------------------
# Gates werden hier geprueft (Guertel), zusaetzlich vom PreToolUse-Hook (Hosentraeger).
# `brief`/`build` sind bewusst reine Gate-Wrapper: die kreative Arbeit (Beat-Sheet,
# Timeline-Bau) macht ein Sub-Agent, nicht die CLI (siehe .claude/commands/ff-brief,
# ff-build). Sie brechen daher nach dem Gate mit Hinweis ab.


@app.command()
def ingest(project: str) -> None:
    """Scan + Proxy-Erzeugung fuer das Rohmaterial. Setzt Projekt-Phase auf INGESTED."""
    proj = _resolve_or_fail(project)
    try:
        found = ingest_module.scan_media(proj.config.media_root)
    except FileNotFoundError as exc:
        raise _fail(str(exc)) from exc

    proxies_dir = proj.cache_dir / "proxies"
    result = ingest_module.build_proxies(found, proxies_dir, media_root=proj.config.media_root)

    with ProjectState.transaction(proj.state_path) as state:
        state.ensure_project_at_least(Phase.INGESTED)
    console.print(
        f"[green]{len(found)} Assets gefunden, {len(result.proxies)} Proxies bereit.[/green] "
        f"Proxy-Verzeichnis: {proxies_dir}"
    )
    if result.failures:
        console.print(f"[yellow]{len(result.failures)} Asset(s) uebersprungen (Proxy fehlgeschlagen):[/yellow]")
        for failure in result.failures:
            console.print(f"  {failure.asset.name}: {failure.reason}")


@app.command(name="index")
def index_cmd(project: str) -> None:
    """CV-Analyse (Schaerfe/Belichtung/Scenes) + Keyframe-Extraktion fuer noch nicht

    indizierte Assets. Erfordert Projekt-Phase >= INGESTED. Schreibt noch keine
    `assets.json`-Eintraege — Beschreibung/Tags/Rating brauchen den `media-indexer`-Agenten
    (Claude Vision auf den hier erzeugten Keyframes), siehe `/ff-index`.
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

    keyframes_dir = proj.cache_dir / "keyframes"
    for path in pending:
        console.print(f"  {path.name}: Hash noch nicht in assets.json")
    console.print(
        f"[yellow]Naechster Schritt:[/yellow] Keyframes nach {keyframes_dir} extrahieren und "
        "an den media-indexer-Agenten delegieren (siehe /ff-index). Danach 'frameforge index' "
        "erneut ausfuehren, um die Phase auf INDEXED zu heben."
    )


@app.command()
def query(
    project: str,
    tag: str = typer.Option(None),
    place: str = typer.Option(None),
    min_rating: int = typer.Option(None),
    kind: str = typer.Option(None),
) -> None:
    """Kompaktes JSON aus `assets.json`, gefiltert — statt ganze Verzeichnisse zu lesen."""
    proj = _resolve_or_fail(project)
    results = index_module.query_assets(proj, tag=tag, place=place, min_rating=min_rating, kind=kind)
    console.print_json(json.dumps(results))


@app.command(name="design")
def design_cmd(project: str) -> None:
    """Uebernimmt `design/tokens.yaml` als Designsystem, setzt Projekt-Phase auf DESIGNED.

    Der eigentliche Wizard (Stimmung -> Farbpalette/Typo -> Motion -> Asset-Inventur) ist
    Sache des `design-system`-Agenten (`/ff-design`, Task 5) — der schreibt `tokens.yaml`,
    bevor dieses Kommando läuft. SVG-Rendering selbst passiert erst beim Timeline-Bau
    (`design.render_svg_to_png` pro Overlay), nicht hier global fuer das ganze Projekt.
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
    console.print(
        f"[yellow]Gate offen fuer '{export}'.[/yellow] Timeline baut der /ff-build-Ablauf "
        "(story-architect + timeline-builder), nicht dieses Kommando."
    )
    raise typer.Exit(code=1)


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

    timeline = Timeline.load(exp.timeline_path)
    brief = yaml.safe_load(exp.brief_path.read_text()) if exp.brief_path.exists() else None
    known_ids = {a["id"] for a in index_module.load_assets(proj)}
    issues = qc.validate(timeline, brief=brief, known_asset_ids=known_ids)
    if issues:
        for issue in issues:
            console.print(f"[red]QC:[/red] {issue}")
        raise typer.Exit(code=1)

    try:
        out_path = render_module.render_proxy(proj, exp, timeline)
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
) -> None:
    """Final-Render (4K). Erfordert Export-Phase == APPROVED (explizite Freigabe nach Preview)."""
    proj = _resolve_or_fail(project)
    exp = proj.export(export)
    if lut is not None and not lut.exists():
        raise _fail(f"LUT-Datei nicht gefunden: {lut}")
    lut_path = lut
    state = proj.load_state()
    try:
        gate_render_final(state, export)
    except GateError as exc:
        raise _fail(str(exc)) from exc

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
    brief = yaml.safe_load(exp.brief_path.read_text()) if exp.brief_path.exists() else None
    known_ids = {a["id"] for a in index_module.load_assets(proj)}
    issues = qc.validate(timeline, brief=brief, known_asset_ids=known_ids)
    if issues:
        for issue in issues:
            console.print(f"[red]QC:[/red] {issue}")
        raise typer.Exit(code=1)

    try:
        out_path = render_module.render_final(proj, exp, timeline, lut_path=lut_path)
    except render_module.RenderError as exc:
        raise _fail(str(exc)) from exc

    with ProjectState.transaction(proj.state_path) as tx:
        tx.advance_export(export, Phase.RENDERED)
    console.print(f"[green]Final-Render fertig:[/green] {out_path}")


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


@app.command()
def faces(project: str) -> None:
    """Gesichtserkennung fuer Foto-Assets — expliziter Opt-in, kein Teil von `frameforge index`.

    Verarbeitet biometrische Daten (siehe `frameforge.people`-Datenschutzhinweis). Schreibt
    `index/people.json` (Encodings pro Asset) und `index/people_clusters.json`
    (Personen-Cluster) — beide sind per `.gitignore` vom Tracking ausgeschlossen.
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
    clusters = people_module.cluster_people(encodings_by_asset)
    clusters_path = proj.index_dir / "people_clusters.json"
    clusters_path.write_text(json.dumps(clusters, indent=2))

    total_faces = sum(len(v) for v in faces_by_asset.values())
    console.print(
        f"[green]{total_faces} Gesichter in {len(faces_by_asset)} von {len(photo_assets)} "
        f"Fotos, {len(clusters)} Personen-Cluster.[/green]"
    )
    console.print(f"Ergebnis: {people_path}, {clusters_path}")


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


@app.command(name="list")
def list_cmd() -> None:
    """Alle Projekte unter `projects/`."""
    projects = list_projects()
    if not projects:
        console.print("keine Projekte")
        return
    for name in projects:
        console.print(name)


if __name__ == "__main__":
    app()
