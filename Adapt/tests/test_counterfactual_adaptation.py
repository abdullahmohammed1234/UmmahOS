"""CRITICAL TEST — Counterfactual adaptation.

Materially different evidence must produce a different adaptation decision
even when raw accuracy is similar.
"""

from __future__ import annotations

import pytest

from adapt.adaptation.adaptation_engine import AdaptationEngine
from adapt.adaptation.challenge_bank import DIST_PROP, get_challenge
from adapt.models.enums import (
    AdaptationAction,
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
    LearnerState,
    MisconceptionRecord,
    PerformanceOutcome,
    RecentPerformance,
)

pytestmark = pytest.mark.counterfactual

MEDIUM = get_challenge("ALG-M-001")


def _outcomes() -> tuple[PerformanceOutcome, ...]:
    # Same 4/5 accuracy for both learners. The isolated error is not the
    # most recent outcome, so Learner A's recent window can still be consistent.
    return (
        PerformanceOutcome("CF-C0", AnswerStatus.CORRECT.value, "POSITIVE"),
        PerformanceOutcome("CF-I0", AnswerStatus.INCORRECT.value, "NEGATIVE"),
        PerformanceOutcome("CF-C1", AnswerStatus.CORRECT.value, "POSITIVE"),
        PerformanceOutcome("CF-C2", AnswerStatus.CORRECT.value, "POSITIVE"),
        PerformanceOutcome("CF-C3", AnswerStatus.CORRECT.value, "POSITIVE"),
    )


def _recent() -> RecentPerformance:
    outcomes = _outcomes()
    return RecentPerformance(
        outcomes=outcomes,
        correct=4,
        incorrect=1,
        partial=0,
        ambiguous=0,
    )


def test_counterfactual_adaptation_different_evidence_different_decision():
    recent = _recent()
    learner_a = LearnerState(
        learner_id="L-A",
        concept_id="basic_algebra",
        mastery_estimate=0.78,
        confidence=0.86,
        reasoning_quality=ReasoningQuality.STRONG,
        error_pattern=ErrorPattern.NONE,
        misconceptions=(),
        recent_performance=recent,
        evidence_strength=EvidenceStrength.STRONG,
        evidence_reliability=EvidenceReliability.HIGH,
        learning_trajectory=LearningTrajectory.STABLE,
        uncertainty=Uncertainty.LOW_UNCERTAINTY,
        learner_confidence=LearnerConfidence.HIGH,
        diagnostic_confidence=DiagnosticConfidence.HIGH,
    )
    learner_b = LearnerState(
        learner_id="L-B",
        concept_id="basic_algebra",
        mastery_estimate=0.76,
        confidence=0.32,
        reasoning_quality=ReasoningQuality.WEAK,
        error_pattern=ErrorPattern.CONCEPTUAL,
        misconceptions=(
            MisconceptionRecord(
                misconception_id=DIST_PROP,
                occurrences=3,
                status="REPEATED",
            ),
        ),
        recent_performance=recent,
        evidence_strength=EvidenceStrength.WEAK,
        evidence_reliability=EvidenceReliability.LOW,
        learning_trajectory=LearningTrajectory.STABLE,
        uncertainty=Uncertainty.HIGH_UNCERTAINTY,
        learner_confidence=LearnerConfidence.LOW,
        diagnostic_confidence=DiagnosticConfidence.LOW,
    )

    evidence_a = Evidence(
        response_id="CF-A",
        answer_status=AnswerStatus.CORRECT,
        reasoning_quality=ReasoningQuality.STRONG,
        error_type=ErrorPattern.NONE,
        misconception_signal=None,
        confidence_signal=LearnerConfidence.HIGH,
        evidence_strength=EvidenceStrength.STRONG,
        diagnostic_confidence=DiagnosticConfidence.HIGH,
        evidence_reliability=EvidenceReliability.HIGH,
        polarity=EvidencePolarity.POSITIVE,
    )
    evidence_b = Evidence(
        response_id="CF-B",
        answer_status=AnswerStatus.CORRECT,
        reasoning_quality=ReasoningQuality.WEAK,
        error_type=ErrorPattern.CONCEPTUAL,
        misconception_signal=DIST_PROP,
        confidence_signal=LearnerConfidence.LOW,
        evidence_strength=EvidenceStrength.WEAK,
        diagnostic_confidence=DiagnosticConfidence.LOW,
        evidence_reliability=EvidenceReliability.LOW,
        polarity=EvidencePolarity.POSITIVE,
    )

    engine = AdaptationEngine()
    decision_a = engine.decide(learner_a, MEDIUM, evidence_a)
    decision_b = engine.decide(learner_b, MEDIUM, evidence_b)

    assert decision_a.decision == AdaptationAction.INCREASE_DIFFICULTY
    assert decision_b.decision in {
        AdaptationAction.REMEDIATE,
        AdaptationAction.PROBE_UNCERTAINTY,
        AdaptationAction.GATHER_MORE_EVIDENCE,
        AdaptationAction.CHANGE_REPRESENTATION,
    }
    assert decision_a.decision != decision_b.decision
    assert "strong_recent_evidence" in decision_a.reason
    assert any("misconception" in reason or "uncertainty" in reason or "weak" in reason
               for reason in decision_b.reason)
