"""Evidence produced by analysis. Correctness is not mastery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.errors import InvalidEvidenceError
from adapt.models.enums import (
    AnswerStatus,
    DiagnosticConfidence,
    ErrorPattern,
    EvidencePolarity,
    EvidenceReliability,
    EvidenceStrength,
    LearnerConfidence,
    ReasoningQuality,
    parse_enum,
)


@dataclass(frozen=True)
class Evidence:
    response_id: str
    answer_status: AnswerStatus
    reasoning_quality: ReasoningQuality
    error_type: ErrorPattern
    misconception_signal: str | None
    confidence_signal: LearnerConfidence
    evidence_strength: EvidenceStrength
    diagnostic_confidence: DiagnosticConfidence
    evidence_reliability: EvidenceReliability
    polarity: EvidencePolarity

    def __post_init__(self) -> None:
        if not self.response_id:
            raise InvalidEvidenceError("response_id is required")
        if self.misconception_signal == "":
            raise InvalidEvidenceError("misconception_signal must be None when absent")

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "answer_status": self.answer_status.value,
            "reasoning_quality": self.reasoning_quality.value,
            "error_type": self.error_type.value,
            "misconception_signal": self.misconception_signal,
            "confidence_signal": self.confidence_signal.value,
            "evidence_strength": self.evidence_strength.value,
            "diagnostic_confidence": self.diagnostic_confidence.value,
            "evidence_reliability": self.evidence_reliability.value,
            "polarity": self.polarity.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Evidence:
        if not isinstance(data, dict):
            raise InvalidEvidenceError("evidence must be an object")
        try:
            signal = data.get("misconception_signal")
            if signal == "":
                signal = None
            return cls(
                response_id=data["response_id"],
                answer_status=parse_enum(
                    data["answer_status"],
                    AnswerStatus,
                    field_name="answer_status",
                    error_cls=InvalidEvidenceError,
                ),
                reasoning_quality=parse_enum(
                    data["reasoning_quality"],
                    ReasoningQuality,
                    field_name="reasoning_quality",
                    error_cls=InvalidEvidenceError,
                ),
                error_type=parse_enum(
                    data["error_type"],
                    ErrorPattern,
                    field_name="error_type",
                    error_cls=InvalidEvidenceError,
                ),
                misconception_signal=signal,
                confidence_signal=parse_enum(
                    data["confidence_signal"],
                    LearnerConfidence,
                    field_name="confidence_signal",
                    error_cls=InvalidEvidenceError,
                ),
                evidence_strength=parse_enum(
                    data["evidence_strength"],
                    EvidenceStrength,
                    field_name="evidence_strength",
                    error_cls=InvalidEvidenceError,
                ),
                diagnostic_confidence=parse_enum(
                    data["diagnostic_confidence"],
                    DiagnosticConfidence,
                    field_name="diagnostic_confidence",
                    error_cls=InvalidEvidenceError,
                ),
                evidence_reliability=parse_enum(
                    data.get("evidence_reliability", EvidenceReliability.UNKNOWN),
                    EvidenceReliability,
                    field_name="evidence_reliability",
                    error_cls=InvalidEvidenceError,
                ),
                polarity=parse_enum(
                    data.get("polarity", EvidencePolarity.NEUTRAL),
                    EvidencePolarity,
                    field_name="polarity",
                    error_cls=InvalidEvidenceError,
                ),
            )
        except KeyError as exc:
            raise InvalidEvidenceError(f"Missing evidence field: {exc}") from exc
