"""Phase 3 counterfactual end-to-end tests."""

from __future__ import annotations

from adapt.models.enums import StrategyName
from adapt.models.learner_state import MisconceptionRecord, initial_learner_state, LearnerState
from adapt.models.strategy import StrategyState
from tests.helpers_phase3 import make_tutor, run_kinds


def _remediate_state(learner_id: str) -> tuple[LearnerState, StrategyState]:
    base = initial_learner_state(learner_id, "basic_algebra")
    state = LearnerState(
        learner_id=base.learner_id,
        concept_id=base.concept_id,
        mastery_estimate=0.42,
        confidence=0.35,
        reasoning_quality=base.reasoning_quality,
        error_pattern=base.error_pattern,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
        recent_performance=base.recent_performance,
        evidence_strength=base.evidence_strength,
        evidence_reliability=base.evidence_reliability,
        learning_trajectory=base.learning_trajectory,
        uncertainty=base.uncertainty,
        learner_confidence=base.learner_confidence,
        diagnostic_confidence=base.diagnostic_confidence,
    )
    strategy = StrategyState(
        current_strategy=StrategyName.REMEDIATE,
        previous_strategy=StrategyName.PROBE,
        strategy_confidence=0.7,
        transition_reason="Initialized in remediation.",
        transition_evidence=("init",),
        misconception_flag="FLAGGED",
        flagged_misconception_id="DIST_PROP",
    )
    return state, strategy


def test_cf1_strong_vs_weak_correct_evidence():
    _, a, ta = run_kinds(
        ("strong_correct",) * 4,
        session_id="CF1A",
        learner_id="A",
        initial_challenge="ALG-M-001",
    )
    _, b, tb = run_kinds(
        ("weak_correct",) * 4,
        session_id="CF1B",
        learner_id="B",
        initial_challenge="ALG-M-001",
    )
    assert a.learner_state.mastery_estimate > b.learner_state.mastery_estimate
    assert b.strategy_state.current_strategy in {
        StrategyName.PROBE,
        StrategyName.MAINTAIN,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.ASSESS,
    }
    assert a.strategy_state.current_strategy in {
        StrategyName.INCREASE,
        StrategyName.MAINTAIN,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.PROBE,
    }
    different = (
        a.strategy_state.current_strategy != b.strategy_state.current_strategy
        or a.current_challenge.challenge_id != b.current_challenge.challenge_id
        or [x.decision for x in ta] != [x.decision for x in tb]
    )
    assert different


def test_cf1_difference_emerges_from_pipeline_not_manual_assignment():
    _, a, _ = run_kinds(("strong_correct",) * 4, session_id="CF1A2", learner_id="A")
    _, b, _ = run_kinds(("weak_correct",) * 4, session_id="CF1B2", learner_id="B")
    assert a.learner_state.mastery_estimate != 1.0
    assert b.learner_state.mastery_estimate != 0.0


def test_cf2_four_correct_vs_misconception():
    _, a, _ = run_kinds(
        ("strong_correct",) * 4,
        session_id="CF2A",
        initial_challenge="ALG-M-002",
    )
    _, b, tb = run_kinds(
        ("strong_correct", "strong_correct", "misconception"),
        session_id="CF2B",
        initial_challenge="ALG-M-002",
    )
    assert b.strategy_state.current_strategy in {
        StrategyName.PROBE,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.REMEDIATE,
        StrategyName.MAINTAIN,
    }
    assert b.strategy_state.current_strategy != StrategyName.DECREASE
    assert a.strategy_state.current_strategy != b.strategy_state.current_strategy or a.current_challenge.challenge_id != b.current_challenge.challenge_id
    assert any(item.evidence.misconception_signal for item in tb) or tb[-1].decision in {
        StrategyName.PROBE,
        StrategyName.REMEDIATE,
        StrategyName.GATHER_EVIDENCE,
    }


def test_cf2_one_misconception_is_not_global_regression():
    _, session, traces = run_kinds(
        ("strong_correct", "strong_correct", "strong_correct", "misconception"),
        session_id="CF2C",
        initial_challenge="ALG-M-002",
    )
    assert traces[-1].decision != StrategyName.DECREASE
    assert traces[-1].decision in {
        StrategyName.PROBE,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.REMEDIATE,
        StrategyName.MAINTAIN,
    }


def test_cf3_remediation_failure_vs_recovery():
    state_a, strat_a = _remediate_state("RA")
    state_b, strat_b = _remediate_state("RB")
    _, a, _ = run_kinds(
        ("wrong_weak", "wrong_weak"),
        session_id="CF3A",
        learner_id="RA",
        initial_challenge="ALG-R-001",
        learner_state=state_a,
        strategy_state=strat_a,
    )
    _, b, _ = run_kinds(
        ("weak_correct", "strong_correct", "strong_correct"),
        session_id="CF3B",
        learner_id="RB",
        initial_challenge="ALG-R-001",
        learner_state=state_b,
        strategy_state=strat_b,
    )
    assert a.strategy_state.current_strategy in {
        StrategyName.REMEDIATE,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.PROBE,
        StrategyName.DECREASE,
    }
    assert b.strategy_state.current_strategy in {
        StrategyName.MAINTAIN,
        StrategyName.PROBE,
        StrategyName.INCREASE,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.REMEDIATE,
    }
    assert a.strategy_state.current_strategy != b.strategy_state.current_strategy or a.current_challenge.challenge_id != b.current_challenge.challenge_id


def test_cf3_next_challenge_reflects_recovery_difference():
    state_a, strat_a = _remediate_state("RA2")
    state_b, strat_b = _remediate_state("RB2")
    _, a, _ = run_kinds(
        ("wrong_weak", "wrong_weak"),
        session_id="CF3A2",
        learner_id="RA2",
        initial_challenge="ALG-R-001",
        learner_state=state_a,
        strategy_state=strat_a,
    )
    _, b, _ = run_kinds(
        ("strong_correct", "strong_correct", "strong_correct"),
        session_id="CF3B2",
        learner_id="RB2",
        initial_challenge="ALG-R-001",
        learner_state=state_b,
        strategy_state=strat_b,
    )
    if a.strategy_state.current_strategy == StrategyName.REMEDIATE:
        assert a.current_challenge.challenge_type.value in {"REMEDIATION", "DIAGNOSTIC", "PROBE", "PRACTICE", "STANDARD"}
    assert a.current_challenge.challenge_id != b.current_challenge.challenge_id or a.strategy_state.current_strategy != b.strategy_state.current_strategy


def test_same_start_conditions_for_counterfactuals():
    tutor = make_tutor()
    a = tutor.start_session(learner_id="A", session_id="SAMEA", initial_challenge="ALG-M-001")
    b = tutor.start_session(learner_id="B", session_id="SAMEB", initial_challenge="ALG-M-001")
    assert a.current_challenge.challenge_id == b.current_challenge.challenge_id
    assert a.strategy_state.current_strategy == b.strategy_state.current_strategy
    assert a.learner_state.mastery_estimate == b.learner_state.mastery_estimate
