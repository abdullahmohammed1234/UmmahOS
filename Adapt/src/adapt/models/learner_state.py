"""C-001 Learner State — Phase 1C schema with Phase 1D confidence split."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.errors import InvalidLearnerStateError
from adapt.models.enums import (
    DiagnosticConfidence,
    ErrorPattern,
    EvidenceReliability,
    EvidenceStrength,
    LearnerConfidence,
    LearningTrajectory,
    ReasoningQuality,
    Uncertainty,
    parse_enum,
)

MAX_RECENT_OUTCOMES = 8


@dataclass(frozen=True)
class MisconceptionRecord:
    misconception_id: str
    occurrences: int
    status: str = "SUSPECTED"

    def __post_init__(self) -> None:
        if not self.misconception_id:
            raise InvalidLearnerStateError("misconception_id is required")
        if self.occurrences < 0:
            raise InvalidLearnerStateError("misconception occurrences cannot be negative")
        if self.status not in {"SUSPECTED", "REPEATED", "RESOLVED"}:
            raise InvalidLearnerStateError(f"Unsupported misconception status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "misconception_id": self.misconception_id,
            "occurrences": self.occurrences,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MisconceptionRecord:
        if not isinstance(data, dict):
            raise InvalidLearnerStateError("misconception must be an object")
        return cls(
            misconception_id=data["misconception_id"],
            occurrences=int(data["occurrences"]),
            status=data.get("status", "SUSPECTED"),
        )


@dataclass(frozen=True)
class PerformanceOutcome:
    response_id: str
    answer_status: str
    polarity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "answer_status": self.answer_status,
            "polarity": self.polarity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PerformanceOutcome:
        return cls(
            response_id=data["response_id"],
            answer_status=data["answer_status"],
            polarity=data["polarity"],
        )


@dataclass(frozen=True)
class RecentPerformance:
    """Phase 1C counts plus a recent outcome sequence for trajectory detection."""

    outcomes: tuple[PerformanceOutcome, ...] = ()
    correct: int = 0
    incorrect: int = 0
    partial: int = 0
    ambiguous: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "correct": self.correct,
            "incorrect": self.incorrect,
            "partial": self.partial,
            "ambiguous": self.ambiguous,
            "outcomes": [item.to_dict() for item in self.outcomes],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RecentPerformance:
        if not isinstance(data, dict):
            raise InvalidLearnerStateError("recent_performance must be an object")
        outcomes = tuple(
            PerformanceOutcome.from_dict(item) for item in data.get("outcomes", [])
        )
        return cls(
            outcomes=outcomes,
            correct=int(data.get("correct", 0)),
            incorrect=int(data.get("incorrect", 0)),
            partial=int(data.get("partial", 0)),
            ambiguous=int(data.get("ambiguous", 0)),
        )


@dataclass(frozen=True)
class LearnerState:
    """Structured, serializable learner state. Mastery is an estimate, not ground truth."""

    learner_id: str
    concept_id: str
    mastery_estimate: float
    confidence: float
    reasoning_quality: ReasoningQuality
    error_pattern: ErrorPattern
    misconceptions: tuple[MisconceptionRecord, ...]
    recent_performance: RecentPerformance
    evidence_strength: EvidenceStrength
    evidence_reliability: EvidenceReliability
    learning_trajectory: LearningTrajectory
    uncertainty: Uncertainty
    learner_confidence: LearnerConfidence = LearnerConfidence.UNKNOWN
    diagnostic_confidence: DiagnosticConfidence = DiagnosticConfidence.UNKNOWN

    def __post_init__(self) -> None:
        if not self.learner_id:
            raise InvalidLearnerStateError("learner_id is required")
        if not self.concept_id:
            raise InvalidLearnerStateError("concept_id is required")
        if not isinstance(self.mastery_estimate, (int, float)) or isinstance(
            self.mastery_estimate, bool
        ):
            raise InvalidLearnerStateError("mastery_estimate must be a number")
        if not 0.0 <= float(self.mastery_estimate) <= 1.0:
            raise InvalidLearnerStateError("mastery_estimate must be in [0, 1]")
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise InvalidLearnerStateError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise InvalidLearnerStateError("confidence (diagnostic) must be in [0, 1]")
        if not isinstance(self.misconceptions, tuple):
            raise InvalidLearnerStateError("misconceptions must be a tuple")

    @property
    def active_misconceptions(self) -> tuple[MisconceptionRecord, ...]:
        return tuple(item for item in self.misconceptions if item.status != "RESOLVED")

    @property
    def repeated_misconceptions(self) -> tuple[MisconceptionRecord, ...]:
        return tuple(
            item
            for item in self.active_misconceptions
            if item.occurrences >= 3 or item.status == "REPEATED"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "learner_id": self.learner_id,
            "concept_id": self.concept_id,
            "mastery_estimate": round(self.mastery_estimate, 4),
            "confidence": round(self.confidence, 4),
            "learner_confidence": self.learner_confidence.value,
            "diagnostic_confidence": self.diagnostic_confidence.value,
            "reasoning_quality": self.reasoning_quality.value,
            "error_pattern": self.error_pattern.value,
            "misconceptions": [item.to_dict() for item in self.misconceptions],
            "recent_performance": self.recent_performance.to_dict(),
            "evidence_strength": self.evidence_strength.value,
            "evidence_reliability": self.evidence_reliability.value,
            "learning_trajectory": self.learning_trajectory.value,
            "uncertainty": self.uncertainty.value,
        }

    def to_json(self) -> str:
        import json

        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LearnerState:
        if not isinstance(data, dict):
            raise InvalidLearnerStateError("learner state must be an object")
        try:
            misconceptions_raw = data.get("misconceptions") or []
            misconceptions = tuple(
                MisconceptionRecord.from_dict(item) for item in misconceptions_raw
            )
            recent_raw = data.get("recent_performance") or {}
            return cls(
                learner_id=data["learner_id"],
                concept_id=data["concept_id"],
                mastery_estimate=float(data["mastery_estimate"]),
                confidence=float(data["confidence"]),
                reasoning_quality=parse_enum(
                    data["reasoning_quality"],
                    ReasoningQuality,
                    field_name="reasoning_quality",
                    error_cls=InvalidLearnerStateError,
                ),
                error_pattern=parse_enum(
                    data.get("error_pattern") or ErrorPattern.NONE,
                    ErrorPattern,
                    field_name="error_pattern",
                    error_cls=InvalidLearnerStateError,
                ),
                misconceptions=misconceptions,
                recent_performance=RecentPerformance.from_dict(recent_raw),
                evidence_strength=parse_enum(
                    data["evidence_strength"],
                    EvidenceStrength,
                    field_name="evidence_strength",
                    error_cls=InvalidLearnerStateError,
                ),
                evidence_reliability=parse_enum(
                    data["evidence_reliability"],
                    EvidenceReliability,
                    field_name="evidence_reliability",
                    error_cls=InvalidLearnerStateError,
                ),
                learning_trajectory=parse_enum(
                    data["learning_trajectory"],
                    LearningTrajectory,
                    field_name="learning_trajectory",
                    error_cls=InvalidLearnerStateError,
                ),
                uncertainty=parse_enum(
                    data["uncertainty"],
                    Uncertainty,
                    field_name="uncertainty",
                    error_cls=InvalidLearnerStateError,
                ),
                learner_confidence=parse_enum(
                    data.get("learner_confidence", LearnerConfidence.UNKNOWN),
                    LearnerConfidence,
                    field_name="learner_confidence",
                    error_cls=InvalidLearnerStateError,
                ),
                diagnostic_confidence=parse_enum(
                    data.get("diagnostic_confidence", DiagnosticConfidence.UNKNOWN),
                    DiagnosticConfidence,
                    field_name="diagnostic_confidence",
                    error_cls=InvalidLearnerStateError,
                ),
            )
        except KeyError as exc:
            raise InvalidLearnerStateError(f"Missing learner-state field: {exc}") from exc
        except (TypeError, ValueError) as exc:
            raise InvalidLearnerStateError(f"Malformed learner state: {exc}") from exc


def initial_learner_state(learner_id: str, concept_id: str) -> LearnerState:
    return LearnerState(
        learner_id=learner_id,
        concept_id=concept_id,
        mastery_estimate=0.5,
        confidence=0.2,
        reasoning_quality=ReasoningQuality.UNKNOWN,
        error_pattern=ErrorPattern.NONE,
        misconceptions=(),
        recent_performance=RecentPerformance(),
        evidence_strength=EvidenceStrength.INSUFFICIENT,
        evidence_reliability=EvidenceReliability.UNKNOWN,
        learning_trajectory=LearningTrajectory.UNKNOWN,
        uncertainty=Uncertainty.INSUFFICIENT_EVIDENCE,
        learner_confidence=LearnerConfidence.UNKNOWN,
        diagnostic_confidence=DiagnosticConfidence.UNKNOWN,
    )
