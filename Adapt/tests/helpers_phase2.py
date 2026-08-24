"""Builders for Phase 2 strategy-layer tests."""

from __future__ import annotations

from adapt.adaptation.challenge_selector import ChallengeSelector
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
    LearnerState,
    MisconceptionRecord,
    PerformanceOutcome,
    RecentPerformance,
)
from adapt.models.strategy import StrategyState, initial_strategy_state
from adapt.pipeline import AdaptPipeline
from adapt.strategy.engine import AdaptiveStrategyEngine
from benchmarks.phase1f.challenge_bank import COMBINED_BANK


def phase2_pipeline() -> AdaptPipeline:
    return AdaptPipeline(
        selector=ChallengeSelector(bank=COMBINED_BANK),
        strategy_engine=AdaptiveStrategyEngine(),
    )


def make_evidence(
    *,
    response_id: str = "R-001",
    answer_status: AnswerStatus = AnswerStatus.CORRECT,
    reasoning_quality: ReasoningQuality = ReasoningQuality.STRONG,
    error_type: ErrorPattern = ErrorPattern.NONE,
    misconception_signal: str | None = None,
    confidence_signal: LearnerConfidence = LearnerConfidence.HIGH,
    evidence_strength: EvidenceStrength = EvidenceStrength.STRONG,
    diagnostic_confidence: DiagnosticConfidence = DiagnosticConfidence.HIGH,
    evidence_reliability: EvidenceReliability = EvidenceReliability.HIGH,
    polarity: EvidencePolarity = EvidencePolarity.POSITIVE,
) -> Evidence:
    return Evidence(
        response_id=response_id,
        answer_status=answer_status,
        reasoning_quality=reasoning_quality,
        error_type=error_type,
        misconception_signal=misconception_signal,
        confidence_signal=confidence_signal,
        evidence_strength=evidence_strength,
        diagnostic_confidence=diagnostic_confidence,
        evidence_reliability=evidence_reliability,
        polarity=polarity,
    )


def _outcome(index: int, correct: bool) -> PerformanceOutcome:
    status = AnswerStatus.CORRECT if correct else AnswerStatus.INCORRECT
    polarity = EvidencePolarity.POSITIVE if correct else EvidencePolarity.NEGATIVE
    return PerformanceOutcome(
        response_id=f"H-{index:02d}",
        answer_status=status.value,
        polarity=polarity.value,
    )


def make_state(
    *,
    pattern: str,
    mastery: float = 0.55,
    confidence: float = 0.6,
    reasoning: ReasoningQuality = ReasoningQuality.STRONG,
    trajectory: LearningTrajectory = LearningTrajectory.STABLE,
    uncertainty: Uncertainty = Uncertainty.MODERATE_UNCERTAINTY,
    strength: EvidenceStrength = EvidenceStrength.MODERATE,
    reliability: EvidenceReliability = EvidenceReliability.HIGH,
    misconceptions: tuple[MisconceptionRecord, ...] = (),
    learner_id: str = "L-P2",
    concept_id: str = "basic_algebra",
    error_pattern: ErrorPattern = ErrorPattern.NONE,
) -> LearnerState:
    outcomes = tuple(_outcome(i, token == "C") for i, token in enumerate(pattern, start=1))
    correct = sum(item.answer_status == AnswerStatus.CORRECT.value for item in outcomes)
    incorrect = sum(item.answer_status == AnswerStatus.INCORRECT.value for item in outcomes)
    return LearnerState(
        learner_id=learner_id,
        concept_id=concept_id,
        mastery_estimate=mastery,
        confidence=confidence,
        reasoning_quality=reasoning,
        error_pattern=error_pattern,
        misconceptions=misconceptions,
        recent_performance=RecentPerformance(
            outcomes=outcomes,
            correct=correct,
            incorrect=incorrect,
        ),
        evidence_strength=strength,
        evidence_reliability=reliability,
        learning_trajectory=trajectory,
        uncertainty=uncertainty,
        learner_confidence=LearnerConfidence.HIGH,
        diagnostic_confidence=DiagnosticConfidence.MODERATE,
    )


def decide(
    state: LearnerState,
    evidence: Evidence,
    strategy: StrategyState | None = None,
    history=None,
    recent_evidence=None,
    engine: AdaptiveStrategyEngine | None = None,
):
    eng = engine or AdaptiveStrategyEngine()
    return eng.decide(
        learner_state=state,
        evidence=evidence,
        history=history,
        current_strategy=strategy or initial_strategy_state(),
        recent_evidence=recent_evidence,
    )
