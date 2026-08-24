"""Explicit strategy transitions, including recovery and hysteresis."""

from __future__ import annotations

from adapt.models.enums import (
    AnswerStatus,
    ErrorPattern,
    EvidencePolarity,
    EvidenceStrength,
    LearnerConfidence,
    ReasoningQuality,
    StrategyName,
)
from adapt.models.learner_state import MisconceptionRecord
from adapt.models.strategy import StrategyState
from tests.helpers_phase2 import decide, make_evidence, make_state


def test_remediate_does_not_automatically_increase():
    state = make_state(
        pattern="WWWCC",
        mastery=0.62,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
    )
    evidence = make_evidence()
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert decision.decision != StrategyName.INCREASE
    assert decision.previous_strategy == StrategyName.REMEDIATE


def test_two_strong_successes_can_leave_remediate():
    state = make_state(
        pattern="WWWCC",
        mastery=0.66,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
    )
    evidence = make_evidence()
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert decision.decision in {StrategyName.MAINTAIN, StrategyName.PROBE}
    assert decision.decision != StrategyName.REMEDIATE


def test_one_success_does_not_exit_remediate():
    state = make_state(
        pattern="WWWC",
        mastery=0.52,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
    )
    evidence = make_evidence()
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert decision.decision == StrategyName.REMEDIATE


def test_transition_label_is_explicit():
    state = make_state(pattern="C")
    evidence = make_evidence(
        evidence_strength=EvidenceStrength.INSUFFICIENT,
        reasoning_quality=ReasoningQuality.UNKNOWN,
        answer_status=AnswerStatus.AMBIGUOUS,
        polarity=EvidencePolarity.NEUTRAL,
        confidence_signal=LearnerConfidence.UNKNOWN,
    )
    decision = decide(state, evidence)
    assert "->" in decision.transition.label
    assert decision.transition.from_strategy == StrategyName.ASSESS


def test_gather_when_evidence_conflicts():
    from adapt.models.enums import LearningTrajectory, Uncertainty

    state = make_state(
        pattern="CCCW",
        trajectory=LearningTrajectory.OSCILLATING,
        uncertainty=Uncertainty.CONTRADICTORY_EVIDENCE,
        strength=EvidenceStrength.CONTRADICTORY,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        evidence_strength=EvidenceStrength.CONTRADICTORY,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        reasoning_quality=ReasoningQuality.MODERATE,
    )
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    assert decision.decision in {StrategyName.GATHER_EVIDENCE, StrategyName.PROBE}


def test_previous_strategy_recorded():
    state = make_state(pattern="CCC")
    evidence = make_evidence()
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    assert decision.previous_strategy == StrategyName.MAINTAIN
    assert decision.strategy_state.previous_strategy == StrategyName.MAINTAIN


def test_steps_in_strategy_reset_on_change():
    state = make_state(pattern="CCCC")
    evidence = make_evidence()
    previous = StrategyState(
        current_strategy=StrategyName.MAINTAIN,
        steps_in_strategy=4,
        consecutive_same_strategy=4,
    )
    decision = decide(state, evidence, strategy=previous)
    if decision.decision != StrategyName.MAINTAIN:
        assert decision.strategy_state.steps_in_strategy == 1
        assert decision.strategy_state.consecutive_same_strategy == 1


def test_assess_when_capability_unknown():
    state = make_state(
        pattern="C",
        mastery=0.5,
        uncertainty=__import__("adapt.models.enums", fromlist=["Uncertainty"]).Uncertainty.INSUFFICIENT_EVIDENCE,
        strength=EvidenceStrength.INSUFFICIENT,
    )
    evidence = make_evidence(
        evidence_strength=EvidenceStrength.INSUFFICIENT,
        reasoning_quality=ReasoningQuality.UNKNOWN,
        confidence_signal=LearnerConfidence.UNKNOWN,
    )
    decision = decide(state, evidence)
    assert decision.decision in {StrategyName.ASSESS, StrategyName.GATHER_EVIDENCE}
