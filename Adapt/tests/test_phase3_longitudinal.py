"""Longitudinal 20-step trajectory tests."""

from __future__ import annotations

from adapt.models.enums import StrategyName
from benchmarks.phase3.trajectories import TRAJECTORY_BY_ID
from tests.helpers_phase3 import run_kinds


def _run(trajectory_id: str):
    spec = TRAJECTORY_BY_ID[trajectory_id]
    return run_kinds(
        spec.kinds,
        session_id=spec.trajectory_id,
        learner_id=f"L-{spec.trajectory_id}",
        concept_id=spec.concept,
        initial_challenge=spec.initial_challenge_id,
    )


def test_t001_strong_learner_reaches_increase():
    _, session, traces = _run("T-001")
    assert session.step_number >= 20
    names = [item.decision.value for item in traces]
    assert names[0] in {"ASSESS", "GATHER_EVIDENCE", "PROBE", "MAINTAIN"}
    assert "INCREASE" in names
    assert "REMEDIATE" not in names
    assert "DECREASE" not in names


def test_t002_struggling_learner_does_not_increase():
    _, session, traces = _run("T-002")
    names = [item.decision.value for item in traces]
    assert "INCREASE" not in names
    assert any(name in {"PROBE", "REMEDIATE", "GATHER_EVIDENCE", "DECREASE", "ASSESS"} for name in names)
    assert session.step_number >= 20


def test_t003_improving_learner_ends_constructively():
    _, session, traces = _run("T-003")
    names = [item.decision.value for item in traces]
    assert names[0] in {"ASSESS", "GATHER_EVIDENCE", "PROBE", "DECREASE", "REMEDIATE", "MAINTAIN"}
    assert session.strategy_state.current_strategy in {
        StrategyName.MAINTAIN,
        StrategyName.INCREASE,
        StrategyName.PROBE,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.REMEDIATE,
    }
    assert session.learner_state.mastery_estimate > traces[3].state_after.mastery_estimate


def test_t004_oscillating_learner_does_not_thrash():
    _, _, traces = _run("T-004")
    compact = "->".join(item.decision.value for item in traces)
    assert "INCREASE->DECREASE->INCREASE" not in compact
    assert "DECREASE->INCREASE->DECREASE" not in compact


def test_t005_misconception_then_recovery():
    _, session, traces = _run("T-005")
    names = [item.decision.value for item in traces]
    assert any(name in {"PROBE", "REMEDIATE", "GATHER_EVIDENCE"} for name in names)
    assert "DECREASE" not in names or names.count("DECREASE") <= 1
    assert session.step_number >= 20


def test_t006_mixed_noisy_stays_coherent():
    _, session, traces = _run("T-006")
    compact = "->".join(item.decision.value for item in traces)
    assert "INCREASE->DECREASE->INCREASE" not in compact
    assert session.step_number >= 20


def test_longitudinal_state_stays_in_range():
    for trajectory_id in ("T-001", "T-002", "T-003", "T-004", "T-005", "T-006"):
        _, session, _ = _run(trajectory_id)
        assert 0.0 <= session.learner_state.mastery_estimate <= 1.0
        assert 0.0 <= session.learner_state.confidence <= 1.0


def test_longitudinal_does_not_manually_set_state():
    _, session, traces = _run("T-001")
    for previous, current in zip(traces, traces[1:]):
        assert current.state_before == previous.state_after


def test_holdout_trajectories_execute():
    _, session_a, _ = _run("T-H-001")
    _, session_b, traces_b = _run("T-H-002")
    assert session_a.step_number >= 20
    assert session_b.step_number >= 20
    compact = "->".join(item.decision.value for item in traces_b)
    assert "INCREASE->DECREASE->INCREASE" not in compact
