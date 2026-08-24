"""Generalized strategy features. No concept-name branching."""

from __future__ import annotations

from dataclasses import dataclass

from adapt.models.enums import (
    AnswerStatus,
    ErrorPattern,
    EvidencePolarity,
    EvidenceReliability,
    EvidenceStrength,
    LearnerConfidence,
    LearningTrajectory,
    ReasoningQuality,
    StrategyName,
    Uncertainty,
)
from adapt.models.evidence import Evidence
from adapt.models.learner_response import LearnerResponse
from adapt.models.learner_state import LearnerState
from adapt.models.strategy import StrategyState
from adapt.strategy.config import StrategyConfig


@dataclass(frozen=True)
class StrategyFeatures:
    n_outcomes: int
    consecutive_correct: int
    consecutive_incorrect: int
    consecutive_positive: int
    consecutive_negative: int
    prior_correct_before_errors: int
    recent_correct_rate: float | None
    max_misconception_occurrences: int
    distinct_active_misconceptions: int
    new_misconception: bool
    isolated_misconception: bool
    persistent_misconception: bool
    strong_prior: bool
    global_regression: bool
    localized_error: bool
    temporary_noise: bool
    recovery_successes: int
    recovery_strong_reasoning: int
    recovery_high_confidence: int
    recovery_ready: bool
    insufficient_evidence: bool
    conflicting_evidence: bool
    high_uncertainty: bool
    increase_supported: bool
    weak_reasoning: bool
    low_learner_confidence: bool
    mastery_estimate: float
    evidence_ids: tuple[str, ...]


def _consecutive_status(state: LearnerState, status: AnswerStatus) -> int:
    count = 0
    for item in reversed(state.recent_performance.outcomes):
        if item.answer_status == status.value:
            count += 1
        else:
            break
    return count


def _consecutive_polarity(state: LearnerState, polarity: EvidencePolarity) -> int:
    count = 0
    for item in reversed(state.recent_performance.outcomes):
        if item.polarity == polarity.value:
            count += 1
        else:
            break
    return count


def _prior_correct_before_errors(state: LearnerState) -> int:
    outcomes = list(state.recent_performance.outcomes)
    idx = len(outcomes) - 1
    while idx >= 0 and outcomes[idx].answer_status != AnswerStatus.CORRECT.value:
        idx -= 1
    prior = 0
    while idx >= 0 and outcomes[idx].answer_status == AnswerStatus.CORRECT.value:
        prior += 1
        idx -= 1
    return prior


def _recent_correct_rate(state: LearnerState) -> float | None:
    outcomes = state.recent_performance.outcomes[-5:]
    if not outcomes:
        return None
    correct = sum(item.answer_status == AnswerStatus.CORRECT.value for item in outcomes)
    return correct / len(outcomes)


def _evidence_ids(
    state: LearnerState,
    evidence: Evidence,
    recent_evidence: list[Evidence] | None,
) -> tuple[str, ...]:
    ids: list[str] = []
    for item in state.recent_performance.outcomes:
        if item.response_id not in ids:
            ids.append(item.response_id)
    if recent_evidence:
        for item in recent_evidence:
            if item.response_id not in ids:
                ids.append(item.response_id)
    if evidence.response_id not in ids:
        ids.append(evidence.response_id)
    return tuple(ids)


def _recovery_counts(
    evidence: Evidence,
    recent_evidence: list[Evidence] | None,
    strategy: StrategyState,
) -> tuple[int, int, int]:
    chain = list(recent_evidence or []) + [evidence]
    if strategy.current_strategy not in {StrategyName.REMEDIATE, StrategyName.RECOVER}:
        if not strategy.recovering:
            return 0, 0, 0
    successes = 0
    strong = 0
    high_conf = 0
    for item in reversed(chain):
        if item.answer_status == AnswerStatus.CORRECT and item.polarity == EvidencePolarity.POSITIVE:
            successes += 1
            if item.reasoning_quality == ReasoningQuality.STRONG:
                strong += 1
            if item.confidence_signal == LearnerConfidence.HIGH:
                high_conf += 1
        else:
            break
    return successes, strong, high_conf


def extract_features(
    *,
    state: LearnerState,
    evidence: Evidence,
    history: list[LearnerResponse] | None,
    strategy: StrategyState,
    recent_evidence: list[Evidence] | None,
    config: StrategyConfig,
) -> StrategyFeatures:
    _ = history
    consecutive_correct = _consecutive_status(state, AnswerStatus.CORRECT)
    consecutive_incorrect = _consecutive_status(state, AnswerStatus.INCORRECT)
    consecutive_positive = _consecutive_polarity(state, EvidencePolarity.POSITIVE)
    consecutive_negative = _consecutive_polarity(state, EvidencePolarity.NEGATIVE)
    prior_correct = _prior_correct_before_errors(state)
    active = state.active_misconceptions
    max_occ = max((item.occurrences for item in active), default=0)
    distinct = len({item.misconception_id for item in active})
    new_misc = bool(evidence.misconception_signal) and max_occ <= config.misconception_flag_threshold
    persistent = max_occ >= config.misconception_remediate_threshold or any(
        item.status == "REPEATED" for item in active
    )
    strong_prior = (
        prior_correct >= config.strong_prior_correct_streak
        or (
            state.mastery_estimate >= config.strong_prior_mastery
            and prior_correct >= 2
            and state.reasoning_quality == ReasoningQuality.STRONG
        )
    )
    isolated = (
        bool(evidence.misconception_signal)
        and max_occ <= config.isolated_misconception_max
        and strong_prior
        and distinct <= 1
        and consecutive_negative <= config.isolated_misconception_max
    )
    weak_reasoning = evidence.reasoning_quality in {
        ReasoningQuality.WEAK,
        ReasoningQuality.UNKNOWN,
    }
    low_conf = evidence.confidence_signal in {
        LearnerConfidence.LOW,
        LearnerConfidence.UNKNOWN,
    }
    multiple_concepts_failing = distinct >= 2 and consecutive_negative >= 2
    global_regression = False
    if consecutive_negative >= config.global_regression_negative_streak and not isolated:
        global_regression = True
    elif (
        consecutive_negative >= 2
        and not strong_prior
        and weak_reasoning
        and low_conf
        and state.learning_trajectory == LearningTrajectory.REGRESSING
    ):
        global_regression = True
    elif multiple_concepts_failing and weak_reasoning and not strong_prior:
        global_regression = True
    localized = isolated or (
        consecutive_negative <= 2
        and strong_prior
        and (evidence.misconception_signal is not None or evidence.error_type == ErrorPattern.CONCEPTUAL)
    )
    temporary_noise = (
        consecutive_incorrect == 1
        and consecutive_correct == 0
        and evidence.error_type in {ErrorPattern.ARITHMETIC, ErrorPattern.CARELESS}
        and prior_correct >= 2
    ) or (
        evidence.error_type in {ErrorPattern.ARITHMETIC, ErrorPattern.CARELESS}
        and consecutive_negative <= 1
        and strong_prior
    )
    recovery_successes, recovery_strong, recovery_high = _recovery_counts(
        evidence, recent_evidence, strategy
    )
    if (
        strategy.current_strategy == StrategyName.REMEDIATE
        and evidence.answer_status == AnswerStatus.CORRECT
    ):
        recovery_successes = max(recovery_successes, consecutive_correct)
        if recovery_strong == 0 and evidence.reasoning_quality == ReasoningQuality.STRONG:
            recovery_strong = 1
        if recovery_high == 0 and evidence.confidence_signal == LearnerConfidence.HIGH:
            recovery_high = 1
    recovery_ready = (
        strategy.current_strategy == StrategyName.REMEDIATE
        and recovery_successes >= config.recovery_min_successes
        and evidence.answer_status == AnswerStatus.CORRECT
        and (
            recovery_strong >= config.recovery_require_strong_reasoning
            or (
                recovery_successes >= 3
                and evidence.reasoning_quality in {ReasoningQuality.STRONG, ReasoningQuality.MODERATE}
                and recovery_high >= 1
            )
        )
    )
    insufficient = (
        state.uncertainty == Uncertainty.INSUFFICIENT_EVIDENCE
        or state.evidence_strength == EvidenceStrength.INSUFFICIENT
        or evidence.evidence_strength == EvidenceStrength.INSUFFICIENT
        or len(state.recent_performance.outcomes) <= config.assess_max_outcomes
    )
    conflicting = (
        state.uncertainty == Uncertainty.CONTRADICTORY_EVIDENCE
        or state.evidence_strength == EvidenceStrength.CONTRADICTORY
        or evidence.evidence_strength == EvidenceStrength.CONTRADICTORY
    )
    high_uncertainty = state.uncertainty in {
        Uncertainty.HIGH_UNCERTAINTY,
        Uncertainty.INSUFFICIENT_EVIDENCE,
        Uncertainty.CONTRADICTORY_EVIDENCE,
    }
    rate = _recent_correct_rate(state)
    increase_supported = (
        evidence.evidence_strength == EvidenceStrength.STRONG
        and evidence.reasoning_quality == ReasoningQuality.STRONG
        and evidence.evidence_reliability == EvidenceReliability.HIGH
        and consecutive_correct >= config.increase_min_consecutive
        and (rate is None or rate >= config.increase_correct_rate)
        and not persistent
        and not evidence.misconception_signal
        and not conflicting
        and evidence.answer_status == AnswerStatus.CORRECT
        and state.uncertainty
        not in {
            Uncertainty.HIGH_UNCERTAINTY,
            Uncertainty.INSUFFICIENT_EVIDENCE,
            Uncertainty.CONTRADICTORY_EVIDENCE,
        }
    )
    return StrategyFeatures(
        n_outcomes=len(state.recent_performance.outcomes),
        consecutive_correct=consecutive_correct,
        consecutive_incorrect=consecutive_incorrect,
        consecutive_positive=consecutive_positive,
        consecutive_negative=consecutive_negative,
        prior_correct_before_errors=prior_correct,
        recent_correct_rate=rate,
        max_misconception_occurrences=max_occ,
        distinct_active_misconceptions=distinct,
        new_misconception=new_misc,
        isolated_misconception=isolated,
        persistent_misconception=persistent,
        strong_prior=strong_prior,
        global_regression=global_regression,
        localized_error=localized,
        temporary_noise=temporary_noise,
        recovery_successes=recovery_successes,
        recovery_strong_reasoning=recovery_strong,
        recovery_high_confidence=recovery_high,
        recovery_ready=recovery_ready,
        insufficient_evidence=insufficient,
        conflicting_evidence=conflicting,
        high_uncertainty=high_uncertainty,
        increase_supported=increase_supported,
        weak_reasoning=weak_reasoning,
        low_learner_confidence=low_conf,
        mastery_estimate=state.mastery_estimate,
        evidence_ids=_evidence_ids(state, evidence, recent_evidence),
    )
