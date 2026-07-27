#!/usr/bin/env python3
"""`PreToolUse`-Hook auf `Bash`: erzwingt die State-Machine aus `frameforge.state`.

Liest den Hook-Payload von stdin (Claude Code PreToolUse-Kontrakt), inspiziert
`tool_input.command` und blockt mit Exit-Code 2 (Meldung auf stderr), wenn:

1. das Kommando `ffmpeg`/`ffprobe` nackt aufruft (immer verboten — nur
   `frameforge.render` darf FFmpeg aufrufen), oder
2. ein `frameforge`-Kommando eine Prozessphase voraussetzt, die das
   betroffene Projekt/Export laut `.state.json` noch nicht erreicht hat.

Guertel + Hosentraeger: dieselben `gate_*`-Funktionen prueft `cli.py` bereits
selbst. Dieser Hook fängt zusätzlich Faelle ab, in denen der Orchestrator
`ffmpeg` oder `frameforge` direkt in Bash aufruft, statt ueber die CLI.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from frameforge.project import Project, ProjectNotFoundError, resolve_project
from frameforge.state import (
    GateError,
    ProjectState,
    StateError,
    gate_brief,
    gate_build,
    gate_design,
    gate_index,
    gate_preview,
    gate_render_final,
)

_SEGMENT_SPLIT = re.compile(r"&&|\|\||[;&|\n]")
_ENV_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_HEREDOC_START = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?")


def _strip_heredocs(command: str) -> str:
    """Entfernt Heredoc-Rumpfinhalte (`<<'EOF' ... EOF`), bevor in Segmente zerlegt wird.

    Ohne das wuerde z.B. `git commit -m "$(cat <<'EOF' ... EOF)"` jede Zeile der
    Commit-Message als eigenes Bash-Segment behandeln — enthaelt eine Zeile zufaellig
    das Wort "ffmpeg" am Anfang, wird das faelschlich als nackter ffmpeg-Aufruf geblockt.
    Multi-Line-Kommandos ohne Heredoc (Zeilen als echte Befehlstrenner) sind davon nicht
    betroffen, die werden weiterhin pro Zeile geprueft.
    """
    lines = command.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        match = _HEREDOC_START.search(line)
        if match:
            delimiter = match.group(1)
            while i < len(lines) and lines[i].strip() != delimiter:
                i += 1
            i += 1  # Trennzeile selbst ueberspringen, nicht in `out` uebernehmen
    return "\n".join(out)


def _command_segments(command: str) -> list[list[str]]:
    """Zerlegt ein Bash-Kommando in einzelne Aufrufe (getrennt durch `&&`, `;`, `|`, ...).

    Jedes Segment wird per `shlex` in Tokens zerlegt; fuehrende Env-Zuweisungen
    (`FOO=bar cmd ...`) werden uebersprungen, damit `tokens[0]` das eigentliche
    Programm ist.
    """
    segments: list[list[str]] = []
    for raw in _SEGMENT_SPLIT.split(_strip_heredocs(command)):
        raw = raw.strip()
        if not raw:
            continue
        try:
            tokens = shlex.split(raw)
        except ValueError:
            continue  # unparsebares Fragment (z.B. offenes Quote) -> ignorieren, nicht blockieren
        while tokens and _ENV_ASSIGNMENT.match(tokens[0]):
            tokens = tokens[1:]
        if tokens:
            segments.append(tokens)
    return segments


def _program_name(token: str) -> str:
    return Path(token).name


def _frameforge_invocation(tokens: list[str]) -> list[str] | None:
    """Gibt `[subcommand, *args]` zurueck, falls `tokens` einen frameforge-Aufruf darstellt."""
    program = _program_name(tokens[0])
    if program in ("python", "python3"):
        if len(tokens) >= 3 and tokens[1] == "-m" and tokens[2] == "frameforge":
            return tokens[3:]
        return None
    if program == "frameforge":
        return tokens[1:]
    return None


def _load_state_or_reason(project_name: str) -> tuple[Project, ProjectState] | str:
    try:
        project = resolve_project(project_name)
    except ProjectNotFoundError as exc:
        return str(exc)
    return project, project.load_state()


def _check_frameforge_gate(rest: list[str]) -> str | None:
    if not rest:
        return None
    subcommand, args = rest[0], rest[1:]
    positional = [a for a in args if not a.startswith("-")]

    if subcommand == "index":
        if not positional:
            return None
        loaded = _load_state_or_reason(positional[0])
        if isinstance(loaded, str):
            return loaded
        _, state = loaded
        try:
            gate_index(state)
        except (GateError, StateError) as exc:
            return str(exc)
        return None

    if subcommand in ("design", "brief"):
        if not positional:
            return None
        loaded = _load_state_or_reason(positional[0])
        if isinstance(loaded, str):
            return loaded
        _, state = loaded
        gate = gate_design if subcommand == "design" else gate_brief
        try:
            gate(state)
        except (GateError, StateError) as exc:
            return str(exc)
        return None

    if subcommand in ("build", "preview", "render"):
        if len(positional) < 2:
            return None
        project_name, export_name = positional[0], positional[1]
        loaded = _load_state_or_reason(project_name)
        if isinstance(loaded, str):
            return loaded
        project, state = loaded
        try:
            if subcommand == "build":
                gate_build(state, export_name)
            elif subcommand == "preview":
                timeline_exists = project.export(export_name).timeline_path.exists()
                gate_preview(state, export_name, timeline_exists=timeline_exists)
            else:  # render
                gate_render_final(state, export_name)
        except (GateError, StateError) as exc:
            return str(exc)
        return None

    return None


def evaluate_command(command: str) -> str | None:
    """Erste Blockade-Begruendung fuer ein Bash-Kommando, oder `None` wenn erlaubt."""
    for tokens in _command_segments(command):
        program = _program_name(tokens[0])
        if program in ("ffmpeg", "ffprobe"):
            return (
                f"Nackter '{program}'-Aufruf ist verboten. Nur frameforge.render darf "
                f"FFmpeg aufrufen — nutze 'frameforge preview <projekt> <export>' bzw. "
                f"'frameforge render <projekt> <export>'."
            )
        rest = _frameforge_invocation(tokens)
        if rest is not None:
            reason = _check_frameforge_gate(rest)
            if reason:
                return reason
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    reason = evaluate_command(command)
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
