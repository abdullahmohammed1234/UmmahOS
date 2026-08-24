"""Paired counterfactual strategy tests. Independent of the Phase 1F suite."""

from __future__ import annotations

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
    StrategyName,
    Uncertainty,
)
from adapt.models.evidence import Evidence
from adapt.models.learner_state import (
    LearnerState,
    MisconceptionRecord,
    PerformanceOutcome,
    RecentPerformance,
)
from adapt.models.strategy import StrategyState
from adapt.strategy.engine import AdaptiveStrategyEngine


def _evidence(**overrides) -> Evidence:
    payload = dict(
        response_id="R-001",
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
    payload.update(overrides)
    return Evidence(**payload)


def _state(pattern: str, **overrides) -> LearnerState:
    outcomes = []
    for index, token in enumerate(pattern, start=1):
        correct = token == "C"
        outcomes.append(
            PerformanceOutcome(
                response_id=f"H-{index:02d}",
                answer_status=AnswerStatus.CORRECT.value if correct else AnswerStatus.INCORRECT.value,
                polarity=EvidencePolarity.POSITIVE.value if correct else EvidencePolarity.NEGATIVE.value,
            )
        )
    correct_n = sum(item.answer_status == AnswerStatus.CORRECT.value for item in outcomes)
    incorrect_n = sum(item.answer_status == AnswerStatus.INCORRECT.value for item in outcomes)
    payload = dict(
        learner_id="cf",
        concept_id="basic_algebra",
        mastery_estimate=0.55,
        confidence=0.6,
        reasoning_quality=ReasoningQuality.STRONG,
        error_pattern=ErrorPattern.NONE,
        misconceptions=(),
        recent_performance=RecentPerformance(
            outcomes=tuple(outcomes), correct=correct_n, incorrect=incorrect_n
        ),
        evidence_strength=EvidenceStrength.MODERATE,
        evidence_reliability=EvidenceReliability.HIGH,
        learning_trajectory=LearningTrajectory.STABLE,
        uncertainty=Uncertainty.MODERATE_UNCERTAINTY,
        learner_confidence=LearnerConfidence.HIGH,
        diagnostic_confidence=DiagnosticConfidence.MODERATE,
    )
    payload.update(overrides)
    return LearnerState(**payload)


def run_counterfactuals(engine: AdaptiveStrategyEngine | None = None) -> list[dict]:
    eng = engine or AdaptiveStrategyEngine()

    def decide(state, evidence, strategy):
        return eng.decide(learner_state=state, evidence=evidence, current_strategy=strategy)

    isolated = decide(
        _state(
            "CCCCW",
            mastery_estimate=0.7,
            misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
        ),
        _evidence(
            answer_status=AnswerStatus.INCORRECT,
            polarity=EvidencePolarity.NEGATIVE,
            misconception_signal="DIST_PROP",
            error_type=ErrorPattern.CONCEPTUAL,
            evidence_strength=EvidenceStrength.MODERATE,
        ),
        StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    repeated = decide(
        _state(
            "CCCCWWW",
            mastery_estimate=0.48,
            misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
        ),
        _evidence(
            response_id="R-REP",
            answer_status=AnswerStatus.INCORRECT,
            polarity=EvidencePolarity.NEGATIVE,
            misconception_signal="DIST_PROP",
            error_type=ErrorPattern.CONCEPTUAL,
            evidence_strength=EvidenceStrength.MODERATE,
        ),
        StrategyState(current_strategy=StrategyName.PROBE),
    )
    one = decide(
        _state(
            "WWWC",
            mastery_estimate=0.5,
            misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
        ),
        _evidence(response_id="R-1"),
        StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    three = decide(
        _state(
            "WWWCCC",
            mastery_estimate=0.7,
            misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
        ),
        _evidence(response_id="R-3"),
        StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    localized = isolated
    global_reg = decide(
        _state("WWW", mastery_estimate=0.25),
        _evidence(
            response_id="R-G",
            answer_status=AnswerStatus.INCORRECT,
            polarity=EvidencePolarity.NEGATIVE,
            reasoning_quality=ReasoningQuality.WEAK,
            confidence_signal=LearnerConfidence.LOW,
            evidence_strength=EvidenceStrength.WEAK,
        ),
        StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    shared_state = _state("C", mastery_estimate=0.6)
    shared_evidence = _evidence()
    from_remediate = decide(
        shared_state, shared_evidence, StrategyState(current_strategy=StrategyName.REMEDIATE)
    )
    from_maintain = decide(
        shared_state, shared_evidence, StrategyState(current_strategy=StrategyName.MAINTAIN)
    )
    return [
        {
            "pair_id": "P2-CF-001",
            "decision_a": isolated.decision.value,
            "decision_b": repeated.decision.value,
            "confidence_a": isolated.confidence,
            "confidence_b": repeated.confidence,
            "differentiated": isolated.decision != repeated.decision,
            "evidence_sensitive": isolated.decision in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE}
            and repeated.decision == StrategyName.REMEDIATE,
            "expected": "PROBE/GATHER vs REMEDIATE",
        },
        {
            "pair_id": "P2-CF-002",
            "decision_a": one.decision.value,
            "decision_b": three.decision.value,
            "confidence_a": one.confidence,
            "confidence_b": three.confidence,
            "differentiated": one.decision != three.decision or abs(one.confidence - three.confidence) > 1e-9,
            "evidence_sensitive": one.decision == StrategyName.REMEDIATE and three.decision != StrategyName.REMEDIATE,
            "expected": "one success stays REMEDIATE; three strong successes recover",
        },
        {
            "pair_id": "P2-CF-003",
            "decision_a": localized.decision.value,
            "decision_b": global_reg.decision.value,
            "confidence_a": localized.confidence,
            "confidence_b": global_reg.confidence,
            "differentiated": localized.decision != global_reg.decision,
            "evidence_sensitive": localized.decision != global_reg.decision,
            "expected": "localized error vs global weakness yield different strategies",
        },
        {
            "pair_id": "P2-CF-004",
            "decision_a": from_remediate.decision.value,
            "decision_b": from_maintain.decision.value,
            "confidence_a": from_remediate.confidence,
            "confidence_b": from_maintain.confidence,
            "differentiated": from_remediate.decision != from_maintain.decision,
            "evidence_sensitive": from_remediate.decision != from_maintain.decision,
            "expected": "same mastery, different strategy history, different transition",
        },
    ]
