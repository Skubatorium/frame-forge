"""Tests fuer die State-Machine: verbotene Phasensprünge, Gates, Persistenz."""

from __future__ import annotations

import pytest

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


@pytest.fixture
def state(tmp_path):
    return ProjectState.load(tmp_path / ".state.json")


# -- Projekt-Phase ------------------------------------------------------


def test_fresh_state_starts_at_init(state):
    assert state.project_phase == Phase.INIT


def test_advance_project_rejects_export_only_phase(state):
    """BRIEFED gehoert zu Export-Sub-States, nicht zur Projekt-Phase — muss abgelehnt werden."""
    with pytest.raises(StateError):
        state.advance_project(Phase.BRIEFED)


def test_advance_project_allows_forward_and_backward(state):
    state.advance_project(Phase.DESIGNED)
    assert state.project_phase == Phase.DESIGNED
    state.invalidate_project(Phase.INGESTED)
    assert state.project_phase == Phase.INGESTED


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / ".state.json"
    st = ProjectState.load(path)
    st.advance_project(Phase.INDEXED, content_hash="abc123")
    st.save()

    reloaded = ProjectState.load(path)
    assert reloaded.project_phase == Phase.INDEXED
    assert reloaded.data.content_hashes["_project"] == "abc123"


def test_load_missing_file_defaults_to_init(tmp_path):
    st = ProjectState.load(tmp_path / "does-not-exist" / ".state.json")
    assert st.project_phase == Phase.INIT


# -- Export-Phase & das Gate-Loch aus PROGRESS.md ------------------------


def test_gate_build_blocks_export_that_was_never_briefed(state):
    """Regressionstest fuer den Bug aus PROGRESS.md: ein nie angelegter Export

    (kein brief.yaml) darf `ff-build` nicht passieren lassen.
    """
    with pytest.raises(GateError):
        gate_build(state, "gibts-nicht")


def test_reading_export_phase_does_not_create_phantom_entry(state):
    """`export_phase`/Gates duerfen `.state.json` nicht mit Eintraegen fuer Exporte

    fuellen, die nie explizit angelegt wurden (reiner Lesezugriff).
    """
    assert state.export_phase("nie-angelegt") == Phase.NEW
    with pytest.raises(GateError):
        gate_build(state, "nie-angelegt")
    assert "nie-angelegt" not in state.data.exports


def test_advance_export_rejects_new_as_target(state):
    with pytest.raises(StateError):
        state.advance_export("teaser-90s", Phase.NEW)


def test_advance_export_rejects_project_only_phase(state):
    with pytest.raises(StateError):
        state.advance_export("teaser-90s", Phase.INGESTED)


def test_gate_build_passes_once_briefed(state):
    state.advance_export("teaser-90s", Phase.BRIEFED)
    gate_build(state, "teaser-90s")  # darf nicht werfen


def test_invalidate_export_falls_back_to_briefed(state):
    state.advance_export("teaser-90s", Phase.TIMELINE)
    state.invalidate_export("teaser-90s")
    assert state.export_phase("teaser-90s") == Phase.BRIEFED


# -- Gate-Funktionen pro Kommando (Plan Abschnitt 2) ---------------------


def test_gate_index_requires_ingested(state):
    with pytest.raises(GateError):
        gate_index(state)
    state.advance_project(Phase.INGESTED)
    gate_index(state)


def test_gate_design_requires_indexed(state):
    state.advance_project(Phase.INGESTED)
    with pytest.raises(GateError):
        gate_design(state)
    state.advance_project(Phase.INDEXED)
    gate_design(state)


def test_gate_brief_requires_designed(state):
    state.advance_project(Phase.INDEXED)
    with pytest.raises(GateError):
        gate_brief(state)
    state.advance_project(Phase.DESIGNED)
    gate_brief(state)


def test_ensure_project_at_least_never_regresses(state):
    state.advance_project(Phase.DESIGNED)
    state.ensure_project_at_least(Phase.INGESTED)
    assert state.project_phase == Phase.DESIGNED
    state.ensure_project_at_least(Phase.DESIGNED)
    assert state.project_phase == Phase.DESIGNED


def test_gate_preview_requires_timeline_file_and_phase(state):
    state.advance_export("teaser-90s", Phase.STORYBOARDED)
    with pytest.raises(StateError):
        gate_preview(state, "teaser-90s", timeline_exists=False)
    with pytest.raises(GateError):
        gate_preview(state, "teaser-90s", timeline_exists=True)
    state.advance_export("teaser-90s", Phase.TIMELINE)
    gate_preview(state, "teaser-90s", timeline_exists=True)


def test_gate_render_final_requires_exact_approved(state):
    state.advance_export("teaser-90s", Phase.PREVIEWED)
    with pytest.raises(GateError):
        gate_render_final(state, "teaser-90s")

    state.advance_export("teaser-90s", Phase.APPROVED)
    gate_render_final(state, "teaser-90s")  # darf nicht werfen

    # Bereits gerendert -> erneuter Final-Render braucht wieder explizite Freigabe.
    state.advance_export("teaser-90s", Phase.RENDERED)
    with pytest.raises(GateError):
        gate_render_final(state, "teaser-90s")


# -- P4: transaktionales Lesen-Aendern-Schreiben ------------------------------


def test_transaction_persists_changes(tmp_path):
    path = tmp_path / ".state.json"
    with ProjectState.transaction(path) as st:
        st.advance_project(Phase.INGESTED)
    assert ProjectState.load(path).project_phase == Phase.INGESTED


def test_transaction_sees_previous_write(tmp_path):
    path = tmp_path / ".state.json"
    with ProjectState.transaction(path) as st:
        st.advance_project(Phase.INGESTED)
    with ProjectState.transaction(path) as st:
        assert st.project_phase == Phase.INGESTED
        st.advance_project(Phase.INDEXED)
    assert ProjectState.load(path).project_phase == Phase.INDEXED


def test_transaction_does_not_write_on_exception(tmp_path):
    path = tmp_path / ".state.json"
    ProjectState.load(path).save()  # INIT
    with pytest.raises(RuntimeError), ProjectState.transaction(path) as st:
        st.advance_project(Phase.INGESTED)
        raise RuntimeError("boom")
    assert ProjectState.load(path).project_phase == Phase.INIT
