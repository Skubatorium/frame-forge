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
from rich.console import Console
from rich.table import Table

from frameforge import design, qc
from frameforge import index as index_module
from frameforge import ingest as ingest_module
from frameforge.project import (
    CACHE_ROOT,
    PROJECTS_DIR,
    Project,
    ProjectConfig,
    ProjectNotFoundError,
    list_projects,
    resolve_project,
)
from frameforge.state import (
    GateError,
    Phase,
    StateError,
    gate_brief,
    gate_build,
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


def _not_implemented(exc: NotImplementedError) -> typer.Exit:
    console.print(f"[yellow]Noch nicht implementiert:[/yellow] {exc}")
    return typer.Exit(code=1)


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


@app.command()
def status(project: str) -> None:
    """Zeigt Projekt-Phase und alle Export-Phasen."""
    proj = _resolve_or_fail(project)
    state = proj.load_state()

    console.print(f"[bold]{proj.name}[/bold] — Projekt-Phase: {state.project_phase.name}")
    exports = proj.list_exports()
    if not exports:
        console.print("keine Exporte")
        return
    table = Table()
    table.add_column("Export")
    table.add_column("Phase")
    for export_name in exports:
        table.add_row(export_name, state.export_phase(export_name).name)
    console.print(table)


# -- Pipeline-Kommandos ---------------------------------------------------
# Gates werden hier geprueft; Module ohne CV-/LLM-Abhaengigkeit sind bereits echt
# implementiert (siehe docs/plans/PROGRESS.md, M1), der Rest bis M1 abgeschlossen ist Stub.


@app.command()
def ingest(project: str) -> None:
    """Scan + Proxy-Erzeugung fuer das Rohmaterial. Setzt Projekt-Phase auf INGESTED."""
    proj = _resolve_or_fail(project)
    try:
        found = ingest_module.scan_media(proj.config.media_root)
    except FileNotFoundError as exc:
        raise _fail(str(exc)) from exc

    proxies_dir = proj.cache_dir / "proxies"
    proxies = ingest_module.build_proxies(found, proxies_dir)

    state = proj.load_state()
    state.advance_project(Phase.INGESTED)
    state.save()
    console.print(
        f"[green]{len(found)} Assets gefunden, {len(proxies)} Proxies erzeugt.[/green] "
        f"Proxy-Verzeichnis: {proxies_dir}"
    )


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
    if not pending:
        return

    keyframes_dir = proj.cache_dir / "keyframes"
    for path in pending:
        console.print(f"  {path.name}: Hash noch nicht in assets.json")
    console.print(
        f"[yellow]Naechster Schritt:[/yellow] Keyframes nach {keyframes_dir} extrahieren und "
        "an den media-indexer-Agenten delegieren (siehe /ff-index)."
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
    """Designsystem-Wizard: Tokens, SVG-Templates, Grafik-Prompts. Verarbeitung kommt in M1."""
    proj = _resolve_or_fail(project)
    try:
        design.build_svg_from_tokens(proj.design_dir / "tokens.yaml", {})
    except NotImplementedError as exc:
        raise _not_implemented(exc) from exc


@app.command()
def brief(project: str, export: str) -> None:
    """Export-Briefing. Erfordert Projekt-Phase >= DESIGNED. Wizard kommt mit Task 5 (`/ff-brief`)."""
    proj = _resolve_or_fail(project)
    state = proj.load_state()
    try:
        gate_brief(state)
    except GateError as exc:
        raise _fail(str(exc)) from exc
    console.print(
        f"[yellow]Noch nicht implementiert:[/yellow] brief-Wizard fuer '{export}' kommt mit "
        "dem `/ff-brief`-Slash-Command (Task 5)"
    )
    raise typer.Exit(code=1)


@app.command()
def build(project: str, export: str) -> None:
    """Story -> Timeline. Erfordert Export-Phase >= BRIEFED. Timeline-Builder kommt in M1."""
    proj = _resolve_or_fail(project)
    state = proj.load_state()
    try:
        gate_build(state, export)
    except GateError as exc:
        raise _fail(str(exc)) from exc
    console.print("[yellow]Noch nicht implementiert:[/yellow] timeline-builder kommt in M1")
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
    issues = qc.validate(timeline)
    if issues:
        for issue in issues:
            console.print(f"[red]QC:[/red] {issue}")
        raise typer.Exit(code=1)

    console.print("[yellow]Noch nicht implementiert:[/yellow] render.render_proxy kommt in M1")
    raise typer.Exit(code=1)


@app.command()
def render(project: str, export: str) -> None:
    """Final-Render (4K). Erfordert Export-Phase == APPROVED (explizite Freigabe nach Preview)."""
    proj = _resolve_or_fail(project)
    state = proj.load_state()
    try:
        gate_render_final(state, export)
    except GateError as exc:
        raise _fail(str(exc)) from exc
    console.print("[yellow]Noch nicht implementiert:[/yellow] render.render_final kommt in M4")
    raise typer.Exit(code=1)


@app.command()
def approve(project: str, export: str) -> None:
    """Explizite Freigabe eines Exports nach dem Preview. Erfordert Export-Phase == PREVIEWED."""
    proj = _resolve_or_fail(project)
    state = proj.load_state()
    current = state.export_phase(export)
    if current != Phase.PREVIEWED:
        raise _fail(
            f"Export '{export}' ist in Phase {current.name} — Freigabe erst nach PREVIEWED moeglich"
        )
    if not typer.confirm(f"Export '{export}' fuer Final-Render freigeben?"):
        raise typer.Exit(code=1)
    state.advance_export(export, Phase.APPROVED)
    state.save()
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
