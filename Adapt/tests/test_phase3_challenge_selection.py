"""Challenge selection integration tests."""

from __future__ import annotations

from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.enums import AdaptationAction, ChallengeType, DiagnosticConfidence, Difficulty, StrategyName
from adapt.models.learner_state import initial_learner_state
from adapt.tutor.challenge_bank import PHASE3_BANK, get_phase3_challenge
from adapt.tutor.compat import challenge_compatible_with_strategy
from adapt.tutor.selector import AdaptiveChallengeSelector
from tests.helpers_phase3 import run_kinds


def _decision(action: AdaptationAction) -> AdaptationDecision:
    return AdaptationDecision(
        decision=action,
        reason=("test_reason",),
        confidence=DiagnosticConfidence.MODERATE,
        evidence_used=("E-1",),
    )


def test_increase_prefers_higher_difficulty():
    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-M-001")
    state = initial_learner_state("L", "basic_algebra")
    chosen = selector.select(
        _decision(AdaptationAction.INCREASE_DIFFICULTY),
        state,
        current,
        used_challenge_ids=[current.challenge_id],
        strategy_name=StrategyName.INCREASE,
    )
    assert chosen.difficulty in {Difficulty.HARD, Difficulty.MEDIUM}
    assert chosen.challenge_id != current.challenge_id


def test_decrease_prefers_lower_difficulty():
    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-M-001")
    state = initial_learner_state("L", "basic_algebra")
    chosen = selector.select(
        _decision(AdaptationAction.DECREASE_DIFFICULTY),
        state,
        current,
        strategy_name=StrategyName.DECREASE,
    )
    assert chosen.difficulty in {Difficulty.EASY, Difficulty.MEDIUM}


def test_probe_prefers_diagnostic_or_probe():
    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-M-001")
    state = initial_learner_state("L", "basic_algebra")
    chosen = selector.select(
        _decision(AdaptationAction.PROBE_UNCERTAINTY),
        state,
        current,
        strategy_name=StrategyName.PROBE,
    )
    assert chosen.challenge_type in {ChallengeType.PROBE, ChallengeType.DIAGNOSTIC, ChallengeType.PRACTICE, ChallengeType.STANDARD}
    assert chosen.challenge_type != ChallengeType.INCREASED_DIFFICULTY


def test_gather_prefers_high_information():
    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-E-003")
    state = initial_learner_state("L", "basic_algebra")
    chosen = selector.select(
        _decision(AdaptationAction.GATHER_MORE_EVIDENCE),
        state,
        current,
        strategy_name=StrategyName.GATHER_EVIDENCE,
    )
    assert chosen.diagnostic_value >= 0.5
    assert chosen.challenge_type != ChallengeType.INCREASED_DIFFICULTY


def test_remediate_targets_misconception():
    from adapt.models.learner_state import LearnerState, MisconceptionRecord, RecentPerformance
    from adapt.models.enums import (
        ErrorPattern,
        EvidenceReliability,
        EvidenceStrength,
        LearnerConfidence,
        LearningTrajectory,
        ReasoningQuality,
        Uncertainty,
    )

    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-M-002")
    state = LearnerState(
        learner_id="L",
        concept_id="basic_algebra",
        mastery_estimate=0.4,
        confidence=0.3,
        reasoning_quality=ReasoningQuality.WEAK,
        error_pattern=ErrorPattern.CONCEPTUAL,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
        recent_performance=RecentPerformance(),
        evidence_strength=EvidenceStrength.MODERATE,
        evidence_reliability=EvidenceReliability.MODERATE,
        learning_trajectory=LearningTrajectory.STABLE,
        uncertainty=Uncertainty.MODERATE_UNCERTAINTY,
        learner_confidence=LearnerConfidence.LOW,
        diagnostic_confidence=DiagnosticConfidence.MODERATE,
    )
    chosen = selector.select(
        _decision(AdaptationAction.REMEDIATE),
        state,
        current,
        strategy_name=StrategyName.REMEDIATE,
    )
    assert chosen.target_misconception == "DIST_PROP" or chosen.challenge_type == ChallengeType.REMEDIATION


def test_maintain_keeps_similar_difficulty():
    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-M-001")
    state = initial_learner_state("L", "basic_algebra")
    chosen = selector.select(
        _decision(AdaptationAction.MAINTAIN_DIFFICULTY),
        state,
        current,
        strategy_name=StrategyName.MAINTAIN,
    )
    assert chosen.difficulty == Difficulty.MEDIUM
    assert chosen.challenge_id != current.challenge_id


def test_selector_avoids_immediate_repeat():
    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-M-001")
    state = initial_learner_state("L", "basic_algebra")
    chosen = selector.select(
        _decision(AdaptationAction.MAINTAIN_DIFFICULTY),
        state,
        current,
        used_challenge_ids=["ALG-M-001"],
        strategy_name=StrategyName.MAINTAIN,
    )
    assert chosen.challenge_id != "ALG-M-001"


def test_probe_does_not_simply_increase_difficulty():
    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-E-003")
    state = initial_learner_state("L", "basic_algebra")
    chosen = selector.select(
        _decision(AdaptationAction.PROBE_UNCERTAINTY),
        state,
        current,
        strategy_name=StrategyName.PROBE,
    )
    assert chosen.challenge_type != ChallengeType.INCREASED_DIFFICULTY


def test_end_to_end_selection_is_strategy_consistent():
    _, _, traces = run_kinds(("strong_correct",) * 4, session_id="SEL-E2E")
    for item in traces:
        assert challenge_compatible_with_strategy(
            strategy=item.decision,
            challenge=item.next_challenge,
            previous=item.challenge,
            state=item.state_after,
        )


def test_no_extreme_jump_from_easy_on_gather():
    selector = AdaptiveChallengeSelector(bank=PHASE3_BANK)
    current = get_phase3_challenge("ALG-E-003")
    state = initial_learner_state("L", "basic_algebra")
    chosen = selector.select(
        _decision(AdaptationAction.GATHER_MORE_EVIDENCE),
        state,
        current,
        strategy_name=StrategyName.GATHER_EVIDENCE,
    )
    assert chosen.difficulty != Difficulty.HARD or current.difficulty == Difficulty.HARD
