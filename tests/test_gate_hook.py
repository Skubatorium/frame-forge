"""Tests fuer den `PreToolUse`-Gate-Hook (`.claude/hooks/gate.py`).

Importiert das Hook-Modul per Pfad, da `.claude/hooks/` kein regulaeres
Python-Package ist.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from frameforge import project as project_module
from frameforge.project import ProjectConfig, resolve_project
from frameforge.state import Phase

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "gate.py"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("gate_hook", HOOK_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = _load_gate_module()


@pytest.fixture
def proj(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr(project_module, "PROJECTS_DIR", projects_dir)

    root = projects_dir / "proto"
    root.mkdir()
    ProjectConfig(name="proto", media_root=tmp_path / "media").save(root / "project.yaml")
    return resolve_project("proto")


# -- Nackte ffmpeg/ffprobe-Aufrufe ---------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "ffmpeg -i in.mp4 out.mp4",
        "ffprobe -v error in.mp4",
        "cd /tmp && ffmpeg -i in.mp4 out.mp4",
        "/opt/homebrew/bin/ffmpeg -i in.mp4 out.mp4",
    ],
)
def test_bare_ffmpeg_calls_are_blocked(command):
    assert gate.evaluate_command(command) is not None


@pytest.mark.parametrize(
    "command",
    [
        "brew install ffmpeg exiftool",
        "echo 'planning to run ffmpeg later'",
        "ls -la",
    ],
)
def test_unrelated_commands_pass(command):
    assert gate.evaluate_command(command) is None


# -- frameforge-Gates -----------------------------------------------------


def test_index_before_ingest_is_blocked(proj):
    reason = gate.evaluate_command("python -m frameforge index proto")
    assert reason is not None
    assert "INGESTED" in reason


def test_index_after_ingest_passes(proj):
    state = proj.load_state()
    state.advance_project(Phase.INGESTED)
    state.save()
    assert gate.evaluate_command("python -m frameforge index proto") is None


def test_render_before_approved_is_blocked(proj):
    reason = gate.evaluate_command("frameforge render proto teaser-90s")
    assert reason is not None
    assert "APPROVED" in reason


def test_render_after_approved_passes(proj):
    state = proj.load_state()
    state.advance_export("teaser-90s", Phase.APPROVED)
    state.save()
    assert gate.evaluate_command("frameforge render proto teaser-90s") is None


def test_heredoc_body_mentioning_ffmpeg_is_not_blocked():
    """Regressionstest: eine Commit-Message per Heredoc, die zufaellig mit 'ffmpeg' beginnt,

    darf nicht als nackter ffmpeg-Aufruf durchgehen (jede Zeile wurde vorher faelschlich
    als eigenes Bash-Segment behandelt).
    """
    command = (
        "git commit -m \"$(cat <<'EOF'\n"
        "Proxy-Encoding nutzt ffmpeg intern per subprocess.\n"
        "ffmpeg direkt aus Bash bleibt trotzdem verboten.\n"
        "EOF\n"
        ")\""
    )
    assert gate.evaluate_command(command) is None


def test_real_multiline_ffmpeg_call_without_heredoc_is_still_blocked():
    command = "cd /tmp\nffmpeg -i in.mp4 out.mp4"
    assert gate.evaluate_command(command) is not None


def test_unknown_project_is_blocked(proj):
    reason = gate.evaluate_command("python -m frameforge index gibts-nicht")
    assert reason is not None


def test_doctor_and_status_are_never_gated(proj):
    assert gate.evaluate_command("python -m frameforge doctor") is None
    assert gate.evaluate_command("python -m frameforge status proto") is None


# -- End-to-End: echter Subprozess-Aufruf mit JSON-Payload ----------------


def test_main_blocks_via_subprocess_exit_code(proj):
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "ffmpeg -i in.mp4 out.mp4"},
    }
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "ffmpeg" in result.stderr


def test_main_allows_non_bash_tools():
    payload = {"tool_name": "Read", "tool_input": {"file_path": "x.py"}}
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
