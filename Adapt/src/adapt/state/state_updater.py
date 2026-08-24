"""C-004 State Updater.

Bounded incremental update. New evidence modifies state; it does not replace it.
"""

from __future__ import annotations

from adapt.errors import InvalidEvidenceError, InvalidLearnerStateError
from adapt.models.enums import (
    AnswerStatus,
    DiagnosticConfidence,
    ErrorPattern,
    EvidencePolarity,
    EvidenceReliability,
    EvidenceStrength,
    LearnerConfidence,
    LearningTrajectory,
    ReasoningQuality,
    Uncertainty,
)
from adapt.models.evidence import Evidence
from adapt.models.learner_state import (
    MAX_RECENT_OUTCOMES,
    LearnerState,
    MisconceptionRecord,
    PerformanceOutcome,
    RecentPerformance,
)

STRENGTH_WEIGHT = {
    EvidenceStrength.STRONG: 1.0,
    EvidenceStrength.MODERATE: 0.55,
    EvidenceStrength.WEAK: 0.25,
    EvidenceStrength.INSUFFICIENT: 0.08,
    EvidenceStrength.CONTRADICTORY: 0.05,
}

RELIABILITY_WEIGHT = {
    EvidenceReliability.HIGH: 1.0,
    EvidenceReliability.MODERATE: 0.6,
    EvidenceReliability.LOW: 0.35,
    EvidenceReliability.UNKNOWN: 0.25,
}

REASONING_WEIGHT = {
    ReasoningQuality.STRONG: 1.0,
    ReasoningQuality.MODERATE: 0.7,
    ReasoningQuality.WEAK: 0.35,
    ReasoningQuality.UNKNOWN: 0.25,
}

ERROR_DIRECTION = {
    ErrorPattern.NONE: 1.0,
    ErrorPattern.ARITHMETIC: -0.35,
    ErrorPattern.CARELESS: -0.25,
    ErrorPattern.PROCEDURAL: -0.5,
    ErrorPattern.CONCEPTUAL: -1.0,
    ErrorPattern.UNKNOWN: -0.4,
}

DIAGNOSTIC_SCORE = {
    DiagnosticConfidence.HIGH: 0.9,
    DiagnosticConfidence.MODERATE: 0.6,
    DiagnosticConfidence.LOW: 0.3,
    DiagnosticConfidence.UNKNOWN: 0.2,
}

BASE_STEP = 0.10
MAX_STEP = 0.12


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _mastery_delta(previous: LearnerState, evidence: Evidence, contradicted: bool) -> float:
    strength_w = STRENGTH_WEIGHT[evidence.evidence_strength]
    reliability_w = RELIABILITY_WEIGHT[evidence.evidence_reliability]
    reasoning_w = REASONING_WEIGHT[evidence.reasoning_quality]

    if evidence.answer_status == AnswerStatus.CORRECT:
        direction = 1.0 * reasoning_w
    elif evidence.answer_status == AnswerStatus.PARTIAL:
        direction = 0.2
    elif evidence.answer_status in {AnswerStatus.AMBIGUOUS, AnswerStatus.UNKNOWN}:
        direction = 0.0
    else:
        direction = ERROR_DIRECTION.get(evidence.error_type, -0.4)

    delta = BASE_STEP * direction * strength_w * reliability_w

    recent = previous.recent_performance.outcomes
    same_polarity_streak = 0
    for outcome in reversed(recent):
        if outcome.polarity == evidence.polarity.value:
            same_polarity_streak += 1
        else:
            break
    if same_polarity_streak >= 2 and evidence.evidence_strength in {
        EvidenceStrength.STRONG,
        EvidenceStrength.MODERATE,
    }:
        delta *= 1.25

    if contradicted:
        delta *= 0.3

    return _clamp(delta, -MAX_STEP, MAX_STEP)


def _detect_contradiction(previous: LearnerState, evidence: Evidence) -> bool:
    recent = previous.recent_performance.outcomes
    if len(recent) < 2:
        return False
    if evidence.polarity == EvidencePolarity.NEUTRAL:
        return False

    last_polarities = [item.polarity for item in recent[-3:]]
    positive_history = last_polarities.count(EvidencePolarity.POSITIVE.value) >= 2
    negative_history = last_polarities.count(EvidencePolarity.NEGATIVE.value) >= 2
    historically_strong = previous.evidence_strength == EvidenceStrength.STRONG or (
        previous.uncertainty == Uncertainty.LOW_UNCERTAINTY and previous.mastery_estimate >= 0.65
    )

    if historically_strong and positive_history and evidence.polarity == EvidencePolarity.NEGATIVE:
        return True
    if historically_strong and negative_history and evidence.polarity == EvidencePolarity.POSITIVE:
        return True
    if previous.evidence_strength == EvidenceStrength.STRONG and evidence.polarity == EvidencePolarity.NEGATIVE:
        return True
    return False


def _trajectory(outcomes: tuple[PerformanceOutcome, ...]) -> LearningTrajectory:
    if len(outcomes) < 3:
        return LearningTrajectory.UNKNOWN

    window = outcomes[-6:]
    scores = []
    for item in window:
        if item.answer_status == AnswerStatus.CORRECT.value:
            scores.append(1.0)
        elif item.answer_status == AnswerStatus.PARTIAL.value:
            scores.append(0.5)
        elif item.answer_status == AnswerStatus.AMBIGUOUS.value:
            scores.append(0.4)
        else:
            scores.append(0.0)

    split = max(1, len(scores) // 2)
    first = sum(scores[:split]) / split
    second = sum(scores[split:]) / (len(scores) - split)
    diff = second - first

    changes = sum(a != b for a, b in zip(scores, scores[1:]))
    if len(scores) >= 4 and changes >= len(scores) - 2 and abs(diff) < 0.35:
        return LearningTrajectory.OSCILLATING
    if diff >= 0.35:
        return LearningTrajectory.IMPROVING
    if diff <= -0.35:
        return LearningTrajectory.REGRESSING
    return LearningTrajectory.STABLE


def _uncertainty(
    previous: LearnerState,
    evidence: Evidence,
    outcomes: tuple[PerformanceOutcome, ...],
    contradicted: bool,
) -> Uncertainty:
    if contradicted:
        return Uncertainty.CONTRADICTORY_EVIDENCE
    if evidence.answer_status == AnswerStatus.AMBIGUOUS:
        return Uncertainty.HIGH_UNCERTAINTY
    if len(outcomes) < 2 or evidence.evidence_strength == EvidenceStrength.INSUFFICIENT:
        if len(outcomes) < 3:
            return Uncertainty.INSUFFICIENT_EVIDENCE
        return Uncertainty.HIGH_UNCERTAINTY
    if evidence.evidence_strength == EvidenceStrength.WEAK:
        return Uncertainty.HIGH_UNCERTAINTY

    last_three = outcomes[-3:]
    consistent_positive = all(
        item.answer_status == AnswerStatus.CORRECT.value for item in last_three
    ) and len(last_three) == 3
    if (
        consistent_positive
        and evidence.evidence_strength == EvidenceStrength.STRONG
        and evidence.evidence_reliability == EvidenceReliability.HIGH
        and evidence.reasoning_quality == ReasoningQuality.STRONG
    ):
        return Uncertainty.LOW_UNCERTAINTY
    if evidence.diagnostic_confidence == DiagnosticConfidence.HIGH and consistent_positive:
        return Uncertainty.LOW_UNCERTAINTY
    if previous.uncertainty == Uncertainty.LOW_UNCERTAINTY and evidence.evidence_strength == EvidenceStrength.STRONG:
        return Uncertainty.LOW_UNCERTAINTY
    return Uncertainty.MODERATE_UNCERTAINTY


def _aggregate_strength(
    evidence: Evidence, contradicted: bool, previous: LearnerState
) -> EvidenceStrength:
    if contradicted:
        return EvidenceStrength.CONTRADICTORY
    if evidence.evidence_strength == EvidenceStrength.INSUFFICIENT and len(
        previous.recent_performance.outcomes
    ) < 2:
        return EvidenceStrength.INSUFFICIENT
    if evidence.evidence_strength == EvidenceStrength.STRONG and previous.evidence_strength in {
        EvidenceStrength.STRONG,
        EvidenceStrength.MODERATE,
    }:
        return EvidenceStrength.STRONG
    if evidence.evidence_strength == EvidenceStrength.STRONG and previous.evidence_strength in {
        EvidenceStrength.INSUFFICIENT,
        EvidenceStrength.WEAK,
    }:
        return EvidenceStrength.MODERATE
    return evidence.evidence_strength


def _update_misconceptions(
    previous: LearnerState, evidence: Evidence
) -> tuple[MisconceptionRecord, ...]:
    records = {item.misconception_id: item for item in previous.misconceptions}
    if evidence.misconception_signal:
        current = records.get(evidence.misconception_signal)
        occurrences = 1 if current is None else current.occurrences + 1
        status = "REPEATED" if occurrences >= 3 else "SUSPECTED"
        records[evidence.misconception_signal] = MisconceptionRecord(
            misconception_id=evidence.misconception_signal,
            occurrences=occurrences,
            status=status,
        )
    elif (
        evidence.answer_status == AnswerStatus.CORRECT
        and evidence.reasoning_quality == ReasoningQuality.STRONG
        and evidence.evidence_reliability == EvidenceReliability.HIGH
    ):
        updated = []
        for item in records.values():
            if item.status == "RESOLVED":
                updated.append(item)
            elif item.occurrences >= 3:
                updated.append(
                    MisconceptionRecord(item.misconception_id, item.occurrences, "RESOLVED")
                )
            else:
                updated.append(item)
        return tuple(updated)
    return tuple(records.values())


def _reasoning_quality(previous: LearnerState, evidence: Evidence) -> ReasoningQuality:
    if evidence.reasoning_quality == ReasoningQuality.UNKNOWN:
        return previous.reasoning_quality
    if evidence.evidence_reliability in {EvidenceReliability.HIGH, EvidenceReliability.MODERATE}:
        return evidence.reasoning_quality
    if previous.reasoning_quality == ReasoningQuality.UNKNOWN:
        return evidence.reasoning_quality
    return previous.reasoning_quality


def _error_pattern(previous: LearnerState, evidence: Evidence) -> ErrorPattern:
    if evidence.error_type == ErrorPattern.NONE:
        if evidence.answer_status == AnswerStatus.CORRECT:
            return ErrorPattern.NONE
        return previous.error_pattern
    return evidence.error_type


def _learner_confidence(previous: LearnerState, evidence: Evidence) -> LearnerConfidence:
    if evidence.confidence_signal == LearnerConfidence.UNKNOWN:
        return previous.learner_confidence
    return evidence.confidence_signal


def _blend_confidence(previous: LearnerState, evidence: Evidence) -> tuple[float, DiagnosticConfidence]:
    blend = 0.25 * RELIABILITY_WEIGHT[evidence.evidence_reliability]
    target = DIAGNOSTIC_SCORE[evidence.diagnostic_confidence]
    new_value = _clamp(previous.confidence * (1.0 - blend) + target * blend, 0.0, 1.0)
    if new_value >= 0.75:
        enum_value = DiagnosticConfidence.HIGH
    elif new_value >= 0.45:
        enum_value = DiagnosticConfidence.MODERATE
    elif evidence.diagnostic_confidence == DiagnosticConfidence.UNKNOWN and previous.diagnostic_confidence == DiagnosticConfidence.UNKNOWN:
        enum_value = DiagnosticConfidence.UNKNOWN
    else:
        enum_value = DiagnosticConfidence.LOW
    return new_value, enum_value


class StateUpdater:
    def update(self, previous: LearnerState, evidence: Evidence) -> LearnerState:
        if not isinstance(previous, LearnerState):
            raise InvalidLearnerStateError("previous state must be a LearnerState")
        if not isinstance(evidence, Evidence):
            raise InvalidEvidenceError("evidence must be an Evidence object")

        contradicted = _detect_contradiction(previous, evidence)
        delta = _mastery_delta(previous, evidence, contradicted)
        new_mastery = _clamp(previous.mastery_estimate + delta, 0.0, 1.0)

        outcome = PerformanceOutcome(
            response_id=evidence.response_id,
            answer_status=evidence.answer_status.value,
            polarity=evidence.polarity.value,
        )
        outcomes = (previous.recent_performance.outcomes + (outcome,))[-MAX_RECENT_OUTCOMES:]
        correct = sum(item.answer_status == AnswerStatus.CORRECT.value for item in outcomes)
        incorrect = sum(item.answer_status == AnswerStatus.INCORRECT.value for item in outcomes)
        partial = sum(item.answer_status == AnswerStatus.PARTIAL.value for item in outcomes)
        ambiguous = sum(item.answer_status == AnswerStatus.AMBIGUOUS.value for item in outcomes)
        recent = RecentPerformance(
            outcomes=outcomes,
            correct=correct,
            incorrect=incorrect,
            partial=partial,
            ambiguous=ambiguous,
        )

        confidence, diagnostic_confidence = _blend_confidence(previous, evidence)
        reliability = evidence.evidence_reliability
        if contradicted and reliability == EvidenceReliability.HIGH:
            reliability = EvidenceReliability.MODERATE

        return LearnerState(
            learner_id=previous.learner_id,
            concept_id=previous.concept_id,
            mastery_estimate=new_mastery,
            confidence=confidence,
            reasoning_quality=_reasoning_quality(previous, evidence),
            error_pattern=_error_pattern(previous, evidence),
            misconceptions=_update_misconceptions(previous, evidence),
            recent_performance=recent,
            evidence_strength=_aggregate_strength(evidence, contradicted, previous),
            evidence_reliability=reliability,
            learning_trajectory=_trajectory(outcomes),
            uncertainty=_uncertainty(previous, evidence, outcomes, contradicted),
            learner_confidence=_learner_confidence(previous, evidence),
            diagnostic_confidence=diagnostic_confidence,
        )
