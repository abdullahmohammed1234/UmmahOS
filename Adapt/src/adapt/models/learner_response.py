"""C-002 (Phase 1D) Learner Response. Optional fields stay optional."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.errors import InvalidLearnerResponseError
from adapt.models.enums import LearnerConfidence, parse_enum


@dataclass(frozen=True)
class LearnerResponse:
    response_id: str
    learner_id: str
    concept_id: str
    challenge_id: str
    answer: str
    reasoning: str | None = None
    learner_confidence: LearnerConfidence = LearnerConfidence.UNKNOWN
    timestamp: str | None = None
    response_time: float | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.response_id:
            raise InvalidLearnerResponseError("response_id is required")
        if not self.learner_id:
            raise InvalidLearnerResponseError("learner_id is required")
        if not self.concept_id:
            raise InvalidLearnerResponseError("concept_id is required")
        if not self.challenge_id:
            raise InvalidLearnerResponseError("challenge_id is required")
        if self.answer is None:
            raise InvalidLearnerResponseError("answer is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "learner_id": self.learner_id,
            "concept_id": self.concept_id,
            "challenge_id": self.challenge_id,
            "answer": self.answer,
            "reasoning": self.reasoning,
            "learner_confidence": self.learner_confidence.value,
            "timestamp": self.timestamp,
            "response_time": self.response_time,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LearnerResponse:
        if not isinstance(data, dict):
            raise InvalidLearnerResponseError("learner response must be an object")
        try:
            raw_confidence = data.get("learner_confidence", LearnerConfidence.UNKNOWN)
            if raw_confidence is None:
                raw_confidence = LearnerConfidence.UNKNOWN
            return cls(
                response_id=data["response_id"],
                learner_id=data["learner_id"],
                concept_id=data["concept_id"],
                challenge_id=data["challenge_id"],
                answer=data["answer"],
                reasoning=data.get("reasoning"),
                learner_confidence=parse_enum(
                    raw_confidence,
                    LearnerConfidence,
                    field_name="learner_confidence",
                    error_cls=InvalidLearnerResponseError,
                ),
                timestamp=data.get("timestamp"),
                response_time=data.get("response_time"),
                metadata=data.get("metadata"),
            )
        except KeyError as exc:
            raise InvalidLearnerResponseError(f"Missing response field: {exc}") from exc
