"""Hysteresis and strategy stability."""

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
from adapt.models.strategy import StrategyState
from tests.helpers_phase2 import decide, make_evidence, make_state, phase2_pipeline
from tests.helpers import make_response, STRONG_REASONING
from adapt.adaptation.challenge_bank import get_challenge
from adapt.models.learner_state import initial_learner_state


def test_one_error_after_increase_does_not_decrease():
    state = make_state(pattern="CCCCW", mastery=0.72)
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        reasoning_quality=ReasoningQuality.WEAK,
        evidence_strength=EvidenceStrength.WEAK,
        error_type=ErrorPattern.CARELESS,
        confidence_signal=LearnerConfidence.MODERATE,
    )
    previous = StrategyState(
        current_strategy=StrategyName.INCREASE,
        last_extreme_strategy=StrategyName.INCREASE,
        steps_in_strategy=1,
        steps_since_extreme=0,
    )
    decision = decide(state, evidence, strategy=previous)
    assert decision.decision != StrategyName.DECREASE
    assert decision.decision in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE, StrategyName.MAINTAIN}


def test_one_correct_after_decrease_does_not_increase():
    state = make_state(pattern="WWWC", mastery=0.4)
    evidence = make_evidence()
    previous = StrategyState(
        current_strategy=StrategyName.DECREASE,
        last_extreme_strategy=StrategyName.DECREASE,
        steps_in_strategy=1,
        steps_since_extreme=0,
    )
    decision = decide(state, evidence, strategy=previous)
    assert decision.decision != StrategyName.INCREASE


def test_noisy_error_does_not_oscillate():
    state = make_state(pattern="CCWCC", mastery=0.66)
    evidence = make_evidence()
    previous = StrategyState(
        current_strategy=StrategyName.MAINTAIN,
        last_extreme_strategy=StrategyName.INCREASE,
        steps_since_extreme=1,
    )
    decision = decide(state, evidence, strategy=previous)
    assert decision.decision not in {StrategyName.DECREASE}


def test_pipeline_oscillation_sequence_prefers_probe():
    pipe = phase2_pipeline()
    medium = get_challenge("ALG-M-001")
    state = initial_learner_state("osc", "basic_algebra")
    steps = []
    for i in range(3):
        steps.append(
            (
                medium,
                make_response(
                    response_id=f"O-C{i}",
                    challenge_id=medium.challenge_id,
                    answer="4",
                    reasoning=STRONG_REASONING,
                    learner_confidence=LearnerConfidence.HIGH,
                    learner_id="osc",
                ),
            )
        )
    steps.append(
        (
            medium,
            make_response(
                response_id="O-W",
                challenge_id=medium.challenge_id,
                answer="0",
                reasoning="typo slip",
                learner_confidence=LearnerConfidence.MODERATE,
                learner_id="osc",
            ),
        )
    )
    steps.append(
        (
            medium,
            make_response(
                response_id="O-C3",
                challenge_id=medium.challenge_id,
                answer="4",
                reasoning=STRONG_REASONING,
                learner_confidence=LearnerConfidence.HIGH,
                learner_id="osc",
            ),
        )
    )
    traces = pipe.run_sequence(learner_state=state, steps=steps)
    names = [item.strategy_decision.decision.value for item in traces]
    compact = "->".join(names)
    assert "INCREASE->DECREASE->INCREASE" not in compact
    assert traces[-1].strategy_decision.decision != StrategyName.DECREASE


def test_ambiguous_evidence_prefers_probe_or_gather():
    from adapt.models.enums import Uncertainty

    state = make_state(
        pattern="CW",
        uncertainty=Uncertainty.HIGH_UNCERTAINTY,
        strength=EvidenceStrength.WEAK,
    )
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        evidence_strength=EvidenceStrength.WEAK,
        reasoning_quality=ReasoningQuality.UNKNOWN,
        confidence_signal=LearnerConfidence.UNKNOWN,
    )
    decision = decide(state, evidence, strategy=StrategyState(current_strategy=StrategyName.MAINTAIN))
    assert decision.decision in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE, StrategyName.ASSESS}


def test_hysteresis_allows_decrease_when_regression_is_established():
    state = make_state(pattern="CCCWWW", mastery=0.3)
    evidence = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        reasoning_quality=ReasoningQuality.WEAK,
        confidence_signal=LearnerConfidence.LOW,
        evidence_strength=EvidenceStrength.WEAK,
    )
    previous = StrategyState(
        current_strategy=StrategyName.PROBE,
        last_extreme_strategy=StrategyName.INCREASE,
        steps_since_extreme=3,
        steps_in_strategy=2,
    )
    decision = decide(state, evidence, strategy=previous)
    assert decision.decision in {StrategyName.DECREASE, StrategyName.GATHER_EVIDENCE}
