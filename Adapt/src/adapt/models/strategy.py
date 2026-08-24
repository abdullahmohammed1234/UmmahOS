"""Phase 2 strategy objects. Strategy is not mastery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.errors import InvalidStrategyDecisionError, InvalidStrategyStateError
from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.enums import AdaptationAction, DiagnosticConfidence, StrategyName, parse_enum

STRATEGY_TO_ACTION = {
    StrategyName.ASSESS: AdaptationAction.GATHER_MORE_EVIDENCE,
    StrategyName.PROBE: AdaptationAction.PROBE_UNCERTAINTY,
    StrategyName.MAINTAIN: AdaptationAction.MAINTAIN_DIFFICULTY,
    StrategyName.INCREASE: AdaptationAction.INCREASE_DIFFICULTY,
    StrategyName.DECREASE: AdaptationAction.DECREASE_DIFFICULTY,
    StrategyName.REMEDIATE: AdaptationAction.REMEDIATE,
    StrategyName.RECOVER: AdaptationAction.MAINTAIN_DIFFICULTY,
    StrategyName.GATHER_EVIDENCE: AdaptationAction.GATHER_MORE_EVIDENCE,
}

EXTREME_STRATEGIES = {StrategyName.INCREASE, StrategyName.DECREASE}


def diagnostic_from_score(score: float) -> DiagnosticConfidence:
    if score >= 0.75:
        return DiagnosticConfidence.HIGH
    if score >= 0.45:
        return DiagnosticConfidence.MODERATE
    return DiagnosticConfidence.LOW


@dataclass(frozen=True)
class StrategyState:
    current_strategy: StrategyName
    previous_strategy: StrategyName | None = None
    strategy_confidence: float = 0.2
    transition_reason: str = "Initial strategy: learner capability is insufficiently known."
    transition_evidence: tuple[str, ...] = ()
    consecutive_same_strategy: int = 1
    consecutive_recovery_successes: int = 0
    consecutive_remediation_failures: int = 0
    misconception_flag: str | None = None
    flagged_misconception_id: str | None = None
    steps_in_strategy: int = 0
    last_extreme_strategy: StrategyName | None = None
    steps_since_extreme: int = 0
    recovering: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.strategy_confidence, (int, float)) or isinstance(
            self.strategy_confidence, bool
        ):
            raise InvalidStrategyStateError("strategy_confidence must be a number")
        if not 0.0 <= float(self.strategy_confidence) <= 1.0:
            raise InvalidStrategyStateError("strategy_confidence must be in [0, 1]")
        if self.misconception_flag not in {None, "FLAGGED", "CLEARED"}:
            raise InvalidStrategyStateError(
                f"Unsupported misconception_flag: {self.misconception_flag}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_strategy": self.current_strategy.value,
            "previous_strategy": None
            if self.previous_strategy is None
            else self.previous_strategy.value,
            "strategy_confidence": round(self.strategy_confidence, 4),
            "transition_reason": self.transition_reason,
            "transition_evidence": list(self.transition_evidence),
            "consecutive_same_strategy": self.consecutive_same_strategy,
            "consecutive_recovery_successes": self.consecutive_recovery_successes,
            "consecutive_remediation_failures": self.consecutive_remediation_failures,
            "misconception_flag": self.misconception_flag,
            "flagged_misconception_id": self.flagged_misconception_id,
            "steps_in_strategy": self.steps_in_strategy,
            "last_extreme_strategy": None
            if self.last_extreme_strategy is None
            else self.last_extreme_strategy.value,
            "steps_since_extreme": self.steps_since_extreme,
            "recovering": self.recovering,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StrategyState:
        if not isinstance(data, dict):
            raise InvalidStrategyStateError("strategy state must be an object")
        previous = data.get("previous_strategy")
        extreme = data.get("last_extreme_strategy")
        return cls(
            current_strategy=parse_enum(
                data["current_strategy"],
                StrategyName,
                field_name="current_strategy",
                error_cls=InvalidStrategyStateError,
            ),
            previous_strategy=None
            if previous is None
            else parse_enum(
                previous,
                StrategyName,
                field_name="previous_strategy",
                error_cls=InvalidStrategyStateError,
            ),
            strategy_confidence=float(data.get("strategy_confidence", 0.2)),
            transition_reason=str(data.get("transition_reason") or ""),
            transition_evidence=tuple(data.get("transition_evidence") or ()),
            consecutive_same_strategy=int(data.get("consecutive_same_strategy", 1)),
            consecutive_recovery_successes=int(data.get("consecutive_recovery_successes", 0)),
            consecutive_remediation_failures=int(data.get("consecutive_remediation_failures", 0)),
            misconception_flag=data.get("misconception_flag"),
            flagged_misconception_id=data.get("flagged_misconception_id"),
            steps_in_strategy=int(data.get("steps_in_strategy", 0)),
            last_extreme_strategy=None
            if extreme is None
            else parse_enum(
                extreme,
                StrategyName,
                field_name="last_extreme_strategy",
                error_cls=InvalidStrategyStateError,
            ),
            steps_since_extreme=int(data.get("steps_since_extreme", 0)),
            recovering=bool(data.get("recovering", False)),
        )


def initial_strategy_state() -> StrategyState:
    return StrategyState(current_strategy=StrategyName.ASSESS)


@dataclass(frozen=True)
class StrategyTransition:
    from_strategy: StrategyName
    to_strategy: StrategyName
    reason: str
    evidence_ids: tuple[str, ...]
    internal: bool = False

    def __post_init__(self) -> None:
        if not self.reason:
            raise InvalidStrategyDecisionError("strategy transition requires a reason")
        if not self.evidence_ids:
            raise InvalidStrategyDecisionError("strategy transition requires evidence_ids")

    @property
    def label(self) -> str:
        return f"{self.from_strategy.value} -> {self.to_strategy.value}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_strategy": self.from_strategy.value,
            "to_strategy": self.to_strategy.value,
            "reason": self.reason,
            "evidence_ids": list(self.evidence_ids),
            "internal": self.internal,
            "label": self.label,
        }


@dataclass(frozen=True)
class StrategyDecision:
    decision: StrategyName
    reason: str
    current_strategy: StrategyName
    previous_strategy: StrategyName | None
    evidence_ids: tuple[str, ...]
    state_snapshot: dict[str, Any]
    confidence: float
    transition: StrategyTransition
    supporting_evidence: tuple[str, ...]
    reason_codes: tuple[str, ...]
    uncertainty: str
    strategy_state: StrategyState
    adaptation_action: AdaptationAction

    def __post_init__(self) -> None:
        if not self.reason:
            raise InvalidStrategyDecisionError(
                "Strategy decision is invalid without an evidence-based reason"
            )
        if not self.evidence_ids:
            raise InvalidStrategyDecisionError(
                "Strategy decision is invalid without an evidence trail"
            )
        if not self.reason_codes:
            raise InvalidStrategyDecisionError(
                "Strategy decision is invalid without reason codes"
            )
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise InvalidStrategyDecisionError("strategy decision confidence must be in [0, 1]")

    def to_adaptation_decision(self) -> AdaptationDecision:
        return AdaptationDecision(
            decision=self.adaptation_action,
            reason=self.reason_codes,
            confidence=diagnostic_from_score(self.confidence),
            evidence_used=self.evidence_ids,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "current_strategy": self.current_strategy.value,
            "previous_strategy": None
            if self.previous_strategy is None
            else self.previous_strategy.value,
            "evidence_ids": list(self.evidence_ids),
            "state_snapshot": self.state_snapshot,
            "confidence": round(self.confidence, 4),
            "transition": self.transition.to_dict(),
            "supporting_evidence": list(self.supporting_evidence),
            "reason_codes": list(self.reason_codes),
            "uncertainty": self.uncertainty,
            "strategy_state": self.strategy_state.to_dict(),
            "adaptation_action": self.adaptation_action.value,
        }
