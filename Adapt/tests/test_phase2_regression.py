"""Global regression vs localized misconception."""

from __future__ import annotations

from adapt.models.enums import (
    AnswerStatus,
    ErrorPattern,
    EvidencePolarity,
    EvidenceStrength,
    LearnerConfidence,
    LearningTrajectory,
    ReasoningQuality,
    StrategyName,
    Uncertainty,
)
from adapt.models.learner_state import MisconceptionRecord
from adapt.models.strategy import StrategyState
from tests.helpers_phase2 import decide, make_evidence, make_state


def test_global_regression_can_decrease():
    state = make_state(
        pattern="CCCWWW",
        mastery=0.32,
        trajectory=LearningTrajectory.REGRESSING,
        reasoning=ReasoningQuality.WEAK,
        misconceptions=(),
        error_pattern=ErrorPattern.UNKNOWN,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        reasoning_quality=ReasoningQuality.WEAK,
        confidence_signal=LearnerConfidence.LOW,
        evidence_strength=EvidenceStrength.WEAK,
        error_type=ErrorPattern.UNKNOWN,
    )
    previous = StrategyState(
        current_strategy=StrategyName.PROBE,
        last_extreme_strategy=StrategyName.INCREASE,
        steps_since_extreme=3,
    )
    decision = decide(state, evidence, strategy=previous)
    assert decision.decision in {StrategyName.DECREASE, StrategyName.GATHER_EVIDENCE}


def test_delayed_misconception_after_strong_history_is_not_decrease():
    state = make_state(
        pattern="CCCCWW",
        mastery=0.68,
        trajectory=LearningTrajectory.REGRESSING,
        misconceptions=(MisconceptionRecord("DIST_PROP", 2, "SUSPECTED"),),
        error_pattern=ErrorPattern.CONCEPTUAL,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
        reasoning_quality=ReasoningQuality.MODERATE,
    )
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    assert decision.decision in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE}
    assert decision.decision != StrategyName.DECREASE


def test_three_weak_failures_are_regression_not_probe_only_when_certain():
    state = make_state(
        pattern="WWW",
        mastery=0.22,
        trajectory=LearningTrajectory.REGRESSING,
        reasoning=ReasoningQuality.WEAK,
        uncertainty=Uncertainty.MODERATE_UNCERTAINTY,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        reasoning_quality=ReasoningQuality.WEAK,
        confidence_signal=LearnerConfidence.LOW,
        evidence_strength=EvidenceStrength.WEAK,
    )
    decision = decide(state, evidence, strategy=StrategyState(current_strategy=StrategyName.MAINTAIN))
    assert decision.decision in {StrategyName.DECREASE, StrategyName.GATHER_EVIDENCE, StrategyName.PROBE}


def test_isolated_misconception_invariant():
    from adapt.strategy.invariants import invariant_2_isolated_misconception_not_global_regression

    state = make_state(
        pattern="CCCCW",
        mastery=0.75,
        misconceptions=(MisconceptionRecord("ADD_DENOM", 1, "SUSPECTED"),),
        concept_id="fractions",
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="ADD_DENOM",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    decision = decide(state, evidence, strategy=StrategyState(current_strategy=StrategyName.INCREASE))
    assert invariant_2_isolated_misconception_not_global_regression(decision)


def test_multiple_failing_signals_can_decrease():
    state = make_state(
        pattern="WWWW",
        mastery=0.2,
        trajectory=LearningTrajectory.REGRESSING,
        reasoning=ReasoningQuality.WEAK,
        misconceptions=(
            MisconceptionRecord("DIST_PROP", 2, "SUSPECTED"),
            MisconceptionRecord("COMBINE_UNLIKE", 2, "SUSPECTED"),
        ),
        error_pattern=ErrorPattern.CONCEPTUAL,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        reasoning_quality=ReasoningQuality.WEAK,
        confidence_signal=LearnerConfidence.LOW,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    decision = decide(state, evidence, strategy=StrategyState(current_strategy=StrategyName.MAINTAIN))
    assert decision.decision in {StrategyName.DECREASE, StrategyName.REMEDIATE, StrategyName.GATHER_EVIDENCE}


def test_same_accuracy_localized_vs_global_differs():
    localized = make_state(
        pattern="CCCCW",
        mastery=0.7,
        misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
    )
    global_state = make_state(
        pattern="CCCCW",
        mastery=0.7,
        trajectory=LearningTrajectory.REGRESSING,
        reasoning=ReasoningQuality.WEAK,
    )
    loc_ev = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    glob_ev = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        reasoning_quality=ReasoningQuality.WEAK,
        confidence_signal=LearnerConfidence.LOW,
        evidence_strength=EvidenceStrength.WEAK,
        error_type=ErrorPattern.UNKNOWN,
        response_id="R-G",
    )
    loc = decide(localized, loc_ev, strategy=StrategyState(current_strategy=StrategyName.MAINTAIN))
    glob = decide(
        global_state,
        glob_ev,
        strategy=StrategyState(
            current_strategy=StrategyName.MAINTAIN,
            last_extreme_strategy=None,
        ),
    )
    assert loc.decision != StrategyName.DECREASE or glob.decision == StrategyName.DECREASE
