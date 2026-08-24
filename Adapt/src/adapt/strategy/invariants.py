"""Phase 2 strategy invariants. Pure checks over executed traces/decisions."""

from __future__ import annotations

from typing import Any

from adapt.models.enums import EvidenceStrength, StrategyName
from adapt.models.strategy import StrategyDecision


def invariant_1_weak_evidence_not_high_mastery(
    *,
    evidence_strength: str,
    mastery_before: float,
    mastery_after: float,
    strategy_confidence: float,
) -> bool:
    if evidence_strength in {EvidenceStrength.WEAK.value, EvidenceStrength.INSUFFICIENT.value}:
        if mastery_after - mastery_before >= 0.12:
            return False
        if strategy_confidence >= 0.75:
            return False
    return True


def invariant_2_isolated_misconception_not_global_regression(decision: StrategyDecision) -> bool:
    isolated = any("isolated_misconception=True" in item for item in decision.supporting_evidence)
    if isolated:
        return decision.decision not in {StrategyName.DECREASE}
    return True


def invariant_3_repeated_misconception_can_remediate(decision: StrategyDecision) -> bool:
    persistent = any("persistent_misconception" in code for code in decision.reason_codes)
    if persistent:
        return decision.decision == StrategyName.REMEDIATE
    return True


def invariant_4_successful_remediation_can_recover(decision: StrategyDecision) -> bool:
    recovered = "strategy_recovery" in decision.reason_codes or "internal_recover" in decision.reason_codes
    if recovered:
        return decision.decision != StrategyName.REMEDIATE
    return True


def invariant_5_equivalent_evidence_equivalent_strategy(
    first: StrategyDecision, second: StrategyDecision
) -> bool:
    return first.decision == second.decision and first.adaptation_action == second.adaptation_action


def invariant_6_relevant_evidence_can_change_strategy(
    first: StrategyDecision, second: StrategyDecision
) -> bool:
    return first.decision != second.decision or first.confidence != second.confidence


def invariant_8_traceable(decision: StrategyDecision) -> bool:
    return bool(
        decision.decision
        and decision.reason
        and decision.evidence_ids
        and decision.state_snapshot
        and decision.transition
        and decision.confidence is not None
    )


def invariant_9_oscillation_requires_evidence(transitions: list[str]) -> bool:
    compact = "->".join(transitions)
    return "INCREASE->DECREASE->INCREASE" not in compact


def check_record(record: dict[str, Any]) -> dict[str, bool]:
    decision = record.get("strategy_decision") or {}
    evidence = record.get("evidence") or {}
    before = record.get("state_before") or {}
    after = record.get("state_after") or {}
    return {
        "invariant_1": invariant_1_weak_evidence_not_high_mastery(
            evidence_strength=str(evidence.get("evidence_strength") or ""),
            mastery_before=float(before.get("mastery_estimate") or 0.0),
            mastery_after=float(after.get("mastery_estimate") or 0.0),
            strategy_confidence=float(decision.get("confidence") or 0.0),
        ),
        "invariant_8": bool(
            decision.get("decision")
            and decision.get("reason")
            and decision.get("evidence_ids")
            and decision.get("state_snapshot")
            and decision.get("confidence") is not None
            and decision.get("transition")
        ),
    }
