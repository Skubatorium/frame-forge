"""Tests fuer die Pipeline-Uebersicht (`frameforge status` / `/ff-wizard`)."""

from __future__ import annotations

import pytest

from frameforge.pipeline import build_pipeline, format_pipeline
from frameforge.state import Phase, ProjectState


@pytest.fixture
def state(tmp_path):
    return ProjectState.load(tmp_path / ".state.json")


def _step(pipeline, key):
    for s in pipeline.project_steps:
        if s.key == key:
            return s
    for steps in pipeline.export_steps.values():
        for s in steps:
            if s.key == key:
                return s
    raise KeyError(key)


def test_fresh_project_next_step_is_ingest(state):
    p = build_pipeline("norwegen", state)
    assert _step(p, "ingest").current
    assert not _step(p, "ingest").done
    assert p.next_command == "/ff-ingest norwegen"


def test_ingested_next_step_is_index(state):
    state.advance_project(Phase.INGESTED)
    p = build_pipeline("norwegen", state)
    assert _step(p, "ingest").done
    assert _step(p, "index").current
    assert "index" in p.next_command


def test_designed_without_exports_suggests_brief(state):
    state.advance_project(Phase.DESIGNED)
    p = build_pipeline("norwegen", state)
    assert all(s.done for s in p.project_steps)
    assert "ff-brief" in p.next_command
    assert "<export>" in p.next_command


def test_export_progression_marks_next_export_step(state):
    state.advance_project(Phase.DESIGNED)
    state.advance_export("teaser", Phase.TIMELINE)
    p = build_pipeline("norwegen", state, exports=["teaser"])
    steps = {s.key: s for s in p.export_steps["teaser"]}
    assert steps["brief"].done and steps["build"].done
    assert steps["preview"].current
    assert not steps["approve"].current
    assert p.next_command == "/ff-preview norwegen teaser"


def test_one_current_per_lane_and_single_next_command(state):
    state.advance_project(Phase.DESIGNED)
    state.advance_export("a", Phase.BRIEFED)
    state.advance_export("b", Phase.BRIEFED)
    p = build_pipeline("norwegen", state, exports=["a", "b"])

    # Projekt fertig -> keine current-Markierung mehr auf Projekt-Ebene.
    assert not any(s.current for s in p.project_steps)
    # Jede Export-Spur zeigt ihr eigenes "du bist hier" (hier: build).
    for steps in p.export_steps.values():
        currents = [s for s in steps if s.current]
        assert len(currents) == 1
        assert currents[0].key == "build"
    # Der eine global naechste Befehl ist der erste offene Export-Schritt.
    assert p.next_command == "/ff-build norwegen a"


def test_fully_rendered_has_no_next_command(state):
    state.advance_project(Phase.DESIGNED)
    state.advance_export("teaser", Phase.RENDERED)
    p = build_pipeline("norwegen", state, exports=["teaser"])
    assert p.next_command is None
    assert all(s.done for s in p.export_steps["teaser"])


def test_format_pipeline_renders_markers(state):
    state.advance_project(Phase.INGESTED)
    text = "\n".join(format_pipeline(build_pipeline("norwegen", state)))
    assert "[✓] ingest" in text
    assert "[→] index" in text
    assert "[ ] design" in text
    assert "Naechster Schritt:" in text
