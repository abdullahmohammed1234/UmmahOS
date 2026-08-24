"""Serializable tutor session and end-to-end step trace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.errors import InvalidSessionError
from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.challenge import Challenge
from adapt.models.enums import AdaptationAction, StrategyName, parse_enum
from adapt.models.evidence import Evidence
from adapt.models.learner_response import LearnerResponse
from adapt.models.learner_state import LearnerState
from adapt.models.strategy import StrategyState
from adapt.trace.decision_trace import DecisionTrace


def _full_learner_state(state: LearnerState) -> dict[str, Any]:
    data = state.to_dict()
    data["mastery_estimate"] = state.mastery_estimate
    data["confidence"] = state.confidence
    return data


def _full_strategy_state(state: StrategyState) -> dict[str, Any]:
    data = state.to_dict()
    data["strategy_confidence"] = state.strategy_confidence
    return data


@dataclass(frozen=True)
class StepTrace:
    """One atomic interaction: response → evidence → state → strategy → challenge."""

    step_number: int
    session_id: str
    challenge_id: str
    response: LearnerResponse
    evidence: Evidence
    state_before: LearnerState
    state_after: LearnerState
    strategy_before: StrategyState
    strategy_after: StrategyState
    decision: StrategyName
    adaptation_action: AdaptationAction
    reason: str
    reason_codes: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    next_challenge_id: str
    next_challenge: Challenge
    challenge: Challenge
    explanation: str
    pipeline_trace: DecisionTrace

    def is_complete(self) -> bool:
        return bool(
            self.challenge_id
            and self.response.response_id
            and self.evidence.response_id
            and self.state_before.learner_id
            and self.state_after.learner_id
            and self.strategy_before.current_strategy
            and self.strategy_after.current_strategy
            and self.decision
            and self.next_challenge_id
            and self.reason
            and self.evidence_ids
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_number": self.step_number,
            "session_id": self.session_id,
            "challenge_id": self.challenge_id,
            "response": self.response.to_dict(),
            "evidence": self.evidence.to_dict(),
            "state_before": _full_learner_state(self.state_before),
            "state_after": _full_learner_state(self.state_after),
            "strategy_before": _full_strategy_state(self.strategy_before),
            "strategy_after": _full_strategy_state(self.strategy_after),
            "decision": self.decision.value,
            "adaptation_action": self.adaptation_action.value,
            "reason": self.reason,
            "reason_codes": list(self.reason_codes),
            "evidence_ids": list(self.evidence_ids),
            "next_challenge_id": self.next_challenge_id,
            "next_challenge": self.next_challenge.to_dict(),
            "challenge": self.challenge.to_dict(),
            "explanation": self.explanation,
            "pipeline_trace": self.pipeline_trace.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StepTrace:
        if not isinstance(data, dict):
            raise InvalidSessionError("step trace must be an object")
        pipeline = DecisionTrace(
            interaction_id=data["pipeline_trace"]["interaction_id"],
            learner_state_before=LearnerState.from_dict(data["pipeline_trace"]["learner_state_before"]),
            challenge=Challenge.from_dict(data["pipeline_trace"]["challenge"]),
            learner_response=LearnerResponse.from_dict(data["pipeline_trace"]["learner_response"]),
            evidence=Evidence.from_dict(data["pipeline_trace"]["evidence"]),
            learner_state_after=LearnerState.from_dict(data["pipeline_trace"]["learner_state_after"]),
            adaptation_decision=AdaptationDecision.from_dict(
                data["pipeline_trace"]["adaptation_decision"]
            ),
            next_challenge=Challenge.from_dict(data["pipeline_trace"]["next_challenge"]),
        )
        return cls(
            step_number=int(data["step_number"]),
            session_id=str(data["session_id"]),
            challenge_id=str(data["challenge_id"]),
            response=LearnerResponse.from_dict(data["response"]),
            evidence=Evidence.from_dict(data["evidence"]),
            state_before=LearnerState.from_dict(data["state_before"]),
            state_after=LearnerState.from_dict(data["state_after"]),
            strategy_before=StrategyState.from_dict(data["strategy_before"]),
            strategy_after=StrategyState.from_dict(data["strategy_after"]),
            decision=parse_enum(
                data["decision"], StrategyName, field_name="decision", error_cls=InvalidSessionError
            ),
            adaptation_action=parse_enum(
                data["adaptation_action"],
                AdaptationAction,
                field_name="adaptation_action",
                error_cls=InvalidSessionError,
            ),
            reason=str(data["reason"]),
            reason_codes=tuple(data.get("reason_codes") or ()),
            evidence_ids=tuple(data.get("evidence_ids") or ()),
            next_challenge_id=str(data["next_challenge_id"]),
            next_challenge=Challenge.from_dict(data["next_challenge"]),
            challenge=Challenge.from_dict(data["challenge"]),
            explanation=str(data.get("explanation") or ""),
            pipeline_trace=pipeline,
        )


@dataclass(frozen=True)
class TutorSession:
    session_id: str
    learner_id: str
    concept_id: str
    current_challenge: Challenge
    learner_state: LearnerState
    strategy_state: StrategyState
    history: tuple[LearnerResponse, ...]
    recent_evidence: tuple[Evidence, ...]
    used_challenge_ids: tuple[str, ...]
    step_number: int
    traces: tuple[StepTrace, ...]
    seed: int

    def __post_init__(self) -> None:
        if not self.session_id:
            raise InvalidSessionError("session_id is required")
        if not self.learner_id:
            raise InvalidSessionError("learner_id is required")
        if self.step_number < 0:
            raise InvalidSessionError("step_number cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "learner_id": self.learner_id,
            "concept_id": self.concept_id,
            "current_challenge": self.current_challenge.to_dict(),
            "learner_state": _full_learner_state(self.learner_state),
            "strategy_state": _full_strategy_state(self.strategy_state),
            "history": [item.to_dict() for item in self.history],
            "recent_evidence": [item.to_dict() for item in self.recent_evidence],
            "used_challenge_ids": list(self.used_challenge_ids),
            "step_number": self.step_number,
            "traces": [item.to_dict() for item in self.traces],
            "seed": self.seed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TutorSession:
        if not isinstance(data, dict):
            raise InvalidSessionError("session snapshot must be an object")
        try:
            return cls(
                session_id=data["session_id"],
                learner_id=data["learner_id"],
                concept_id=data["concept_id"],
                current_challenge=Challenge.from_dict(data["current_challenge"]),
                learner_state=LearnerState.from_dict(data["learner_state"]),
                strategy_state=StrategyState.from_dict(data["strategy_state"]),
                history=tuple(LearnerResponse.from_dict(item) for item in data.get("history") or []),
                recent_evidence=tuple(
                    Evidence.from_dict(item) for item in data.get("recent_evidence") or []
                ),
                used_challenge_ids=tuple(data.get("used_challenge_ids") or ()),
                step_number=int(data.get("step_number", 0)),
                traces=tuple(StepTrace.from_dict(item) for item in data.get("traces") or []),
                seed=int(data.get("seed", 0)),
            )
        except KeyError as exc:
            raise InvalidSessionError(f"Missing session field: {exc}") from exc
