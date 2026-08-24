"""C-003 / C-005 Adaptation Engine.

Decisions are produced from structured learner-state evidence, not accuracy alone.
Reasons are collected as the rule fires — they are not invented afterward.
"""

from __future__ import annotations

from adapt.errors import InvalidAdaptationDecisionError, InvalidLearnerStateError
from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.challenge import Challenge
from adapt.models.enums import (
    AdaptationAction,
    AnswerStatus,
    DiagnosticConfidence,
    EvidenceReliability,
    EvidenceStrength,
    LearningTrajectory,
    ReasoningQuality,
    Uncertainty,
)
from adapt.models.evidence import Evidence
from adapt.models.learner_state import LearnerState


def _evidence_ids(state: LearnerState, evidence: Evidence) -> tuple[str, ...]:
    ids = [item.response_id for item in state.recent_performance.outcomes]
    if evidence.response_id not in ids:
        ids.append(evidence.response_id)
    if not ids:
        ids = [evidence.response_id]
    return tuple(ids)


def _consecutive_polarity(state: LearnerState, polarity: str) -> int:
    count = 0
    for item in reversed(state.recent_performance.outcomes):
        if item.polarity == polarity:
            count += 1
        else:
            break
    return count


def _recent_correct_rate(state: LearnerState) -> float | None:
    outcomes = state.recent_performance.outcomes[-5:]
    if not outcomes:
        return None
    correct = sum(item.answer_status == AnswerStatus.CORRECT.value for item in outcomes)
    return correct / len(outcomes)


def _consistent_recent_performance(state: LearnerState) -> bool:
    outcomes = state.recent_performance.outcomes[-3:]
    if len(outcomes) < 3:
        return False
    return all(item.answer_status == AnswerStatus.CORRECT.value for item in outcomes)


def _sudden_improvement(state: LearnerState) -> bool:
    outcomes = state.recent_performance.outcomes[-6:]
    if len(outcomes) < 6:
        return False
    first = outcomes[:3]
    second = outcomes[3:]
    first_correct = sum(item.answer_status == AnswerStatus.CORRECT.value for item in first)
    second_correct = sum(item.answer_status == AnswerStatus.CORRECT.value for item in second)
    return first_correct <= 1 and second_correct >= 3


class AdaptationEngine:
    def decide(
        self,
        state: LearnerState,
        current_challenge: Challenge | None,
        evidence: Evidence,
        recent_evidence: list[Evidence] | None = None,
    ) -> AdaptationDecision:
        if not isinstance(state, LearnerState):
            raise InvalidLearnerStateError("adaptation requires a valid learner state")
        if not isinstance(evidence, Evidence):
            raise InvalidAdaptationDecisionError("adaptation requires structured evidence")
        _ = current_challenge
        _ = recent_evidence

        evidence_used = _evidence_ids(state, evidence)

        repeated = state.repeated_misconceptions
        if repeated:
            top = max(repeated, key=lambda item: item.occurrences)
            if top.occurrences >= 4:
                return AdaptationDecision(
                    decision=AdaptationAction.CHANGE_REPRESENTATION,
                    reason=(
                        "repeated_misconception",
                        f"misconception:{top.misconception_id}",
                        "remediation_already_indicated",
                    ),
                    confidence=DiagnosticConfidence.HIGH,
                    evidence_used=evidence_used,
                )
            return AdaptationDecision(
                decision=AdaptationAction.REMEDIATE,
                reason=(
                    "repeated_misconception",
                    f"misconception:{top.misconception_id}",
                    "reliable_misconception_pattern",
                ),
                confidence=DiagnosticConfidence.HIGH,
                evidence_used=evidence_used,
            )

        if (
            state.uncertainty == Uncertainty.CONTRADICTORY_EVIDENCE
            or state.evidence_strength == EvidenceStrength.CONTRADICTORY
        ):
            return AdaptationDecision(
                decision=AdaptationAction.PROBE_UNCERTAINTY,
                reason=(
                    "contradictory_evidence",
                    "competing_learner_state_hypotheses",
                    "avoid_extreme_adaptation",
                ),
                confidence=DiagnosticConfidence.MODERATE,
                evidence_used=evidence_used,
            )

        if (
            state.uncertainty == Uncertainty.INSUFFICIENT_EVIDENCE
            or state.evidence_strength == EvidenceStrength.INSUFFICIENT
        ):
            return AdaptationDecision(
                decision=AdaptationAction.GATHER_MORE_EVIDENCE,
                reason=(
                    "insufficient_evidence",
                    "conservative_adaptation",
                ),
                confidence=DiagnosticConfidence.LOW,
                evidence_used=evidence_used,
            )

        if (
            state.uncertainty == Uncertainty.HIGH_UNCERTAINTY
            or state.evidence_strength == EvidenceStrength.WEAK
        ):
            return AdaptationDecision(
                decision=AdaptationAction.PROBE_UNCERTAINTY,
                reason=(
                    "high_uncertainty",
                    "weak_evidence_conservative_adaptation",
                    "avoid_extreme_adaptation",
                ),
                confidence=DiagnosticConfidence.LOW,
                evidence_used=evidence_used,
            )

        consecutive_negative = _consecutive_polarity(state, "NEGATIVE")
        reliable_enough = state.evidence_reliability in {
            EvidenceReliability.HIGH,
            EvidenceReliability.MODERATE,
        }
        if (
            state.learning_trajectory == LearningTrajectory.REGRESSING
            and consecutive_negative >= 2
            and reliable_enough
            and state.uncertainty
            not in {Uncertainty.HIGH_UNCERTAINTY, Uncertainty.INSUFFICIENT_EVIDENCE}
        ):
            return AdaptationDecision(
                decision=AdaptationAction.DECREASE_DIFFICULTY,
                reason=(
                    "reliable_regression",
                    "consecutive_negative_evidence",
                    "learning_trajectory_regressing",
                ),
                confidence=DiagnosticConfidence.MODERATE,
                evidence_used=evidence_used,
            )

        increase_reasons: list[str] = []
        if state.evidence_strength == EvidenceStrength.STRONG:
            increase_reasons.append("strong_recent_evidence")
        if state.reasoning_quality == ReasoningQuality.STRONG:
            increase_reasons.append("strong_reasoning")
        if state.evidence_reliability == EvidenceReliability.HIGH:
            increase_reasons.append("high_reliability")
        if state.uncertainty == Uncertainty.LOW_UNCERTAINTY:
            increase_reasons.append("low_uncertainty")
        if not state.active_misconceptions:
            increase_reasons.append("no_active_misconception")
        if _consistent_recent_performance(state):
            increase_reasons.append("consistent_recent_performance")

        required = {
            "strong_recent_evidence",
            "strong_reasoning",
            "high_reliability",
            "low_uncertainty",
            "consistent_recent_performance",
        }
        sudden_improvement = _sudden_improvement(state)
        if required.issubset(increase_reasons) and "no_active_misconception" in increase_reasons:
            rate = _recent_correct_rate(state)
            if sudden_improvement:
                return AdaptationDecision(
                    decision=AdaptationAction.MAINTAIN_DIFFICULTY,
                    reason=(
                        "learning_trajectory_improving",
                        "sudden_improvement_insufficient_to_max_difficulty",
                        "maintain_until_stronger_signal",
                    ),
                    confidence=DiagnosticConfidence.MODERATE,
                    evidence_used=evidence_used,
                )
            if rate is not None and rate >= 0.8:
                return AdaptationDecision(
                    decision=AdaptationAction.INCREASE_DIFFICULTY,
                    reason=tuple(increase_reasons),
                    confidence=DiagnosticConfidence.HIGH,
                    evidence_used=evidence_used,
                )

        return AdaptationDecision(
            decision=AdaptationAction.MAINTAIN_DIFFICULTY,
            reason=(
                "insufficient_evidence_for_trajectory_change",
                "maintain_until_stronger_signal",
            ),
            confidence=DiagnosticConfidence.MODERATE,
            evidence_used=evidence_used,
        )
