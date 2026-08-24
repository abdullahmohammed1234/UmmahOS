"""Structured evidence schema for Gemini extraction.

These fields describe learner evidence. They are not adaptive decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.models.enums import (
    AnswerStatus,
    DiagnosticConfidence,
    ErrorPattern,
    EvidencePolarity,
    EvidenceReliability,
    EvidenceStrength,
    LearnerConfidence,
    ReasoningQuality,
)
from adapt.models.evidence import Evidence

CORRECTNESS_VALUES = ("correct", "incorrect", "unclear")
REASONING_VALUES = ("strong", "partial", "weak", "missing")
CONFIDENCE_VALUES = ("high", "medium", "low", "unclear")
STRENGTH_VALUES = ("strong", "moderate", "weak", "insufficient")
UNCERTAINTY_VALUES = ("low", "medium", "high")
ERROR_TYPE_VALUES = (
    "conceptual",
    "procedural",
    "arithmetic",
    "misreading",
    "insufficient_evidence",
    "unknown",
)

REQUIRED_FIELDS = (
    "correctness",
    "reasoning_quality",
    "confidence_signal",
    "misconception",
    "error_type",
    "evidence_strength",
    "uncertainty",
    "supporting_evidence",
)

FORBIDDEN_DECISION_KEYS = frozenset(
    {
        "strategy",
        "decision",
        "next_action",
        "adaptation",
        "adaptation_action",
        "action",
        "next_challenge",
        "next_challenge_id",
        "tutoring_action",
        "mastery_decision",
    }
)

FORBIDDEN_STRATEGY_VALUES = frozenset(
    {
        "INCREASE",
        "DECREASE",
        "REMEDIATE",
        "PROBE",
        "MAINTAIN",
        "RECOVER",
        "ASSESS",
        "GATHER_EVIDENCE",
        "INCREASE_DIFFICULTY",
        "DECREASE_DIFFICULTY",
        "MAINTAIN_DIFFICULTY",
        "PROBE_UNCERTAINTY",
        "CHANGE_REPRESENTATION",
        "GATHER_MORE_EVIDENCE",
    }
)

EVIDENCE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": list(REQUIRED_FIELDS),
    "additionalProperties": True,
    "properties": {
        "correctness": {"enum": list(CORRECTNESS_VALUES)},
        "reasoning_quality": {"enum": list(REASONING_VALUES)},
        "confidence_signal": {"enum": list(CONFIDENCE_VALUES)},
        "misconception": {"type": ["string", "null"]},
        "error_type": {"enum": list(ERROR_TYPE_VALUES) + [None]},
        "evidence_strength": {"enum": list(STRENGTH_VALUES)},
        "uncertainty": {"enum": list(UNCERTAINTY_VALUES)},
        "supporting_evidence": {"type": "array", "items": {"type": "string"}},
    },
}


@dataclass(frozen=True)
class LLMEvidence:
    correctness: str
    reasoning_quality: str
    confidence_signal: str
    misconception: str | None
    error_type: str | None
    evidence_strength: str
    uncertainty: str
    supporting_evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "correctness": self.correctness,
            "reasoning_quality": self.reasoning_quality,
            "confidence_signal": self.confidence_signal,
            "misconception": self.misconception,
            "error_type": self.error_type,
            "evidence_strength": self.evidence_strength,
            "uncertainty": self.uncertainty,
            "supporting_evidence": list(self.supporting_evidence),
        }

    def to_adapt_evidence(self, response_id: str) -> Evidence:
        answer_status = {
            "correct": AnswerStatus.CORRECT,
            "incorrect": AnswerStatus.INCORRECT,
            "unclear": AnswerStatus.AMBIGUOUS,
        }[self.correctness]
        reasoning = {
            "strong": ReasoningQuality.STRONG,
            "partial": ReasoningQuality.MODERATE,
            "weak": ReasoningQuality.WEAK,
            "missing": ReasoningQuality.UNKNOWN,
        }[self.reasoning_quality]
        confidence = {
            "high": LearnerConfidence.HIGH,
            "medium": LearnerConfidence.MODERATE,
            "low": LearnerConfidence.LOW,
            "unclear": LearnerConfidence.UNKNOWN,
        }[self.confidence_signal]
        error = _map_error_type(self.error_type, answer_status)
        strength = {
            "strong": EvidenceStrength.STRONG,
            "moderate": EvidenceStrength.MODERATE,
            "weak": EvidenceStrength.WEAK,
            "insufficient": EvidenceStrength.INSUFFICIENT,
        }[self.evidence_strength]
        diagnostic, reliability = _map_uncertainty(self.uncertainty, strength)
        if answer_status == AnswerStatus.CORRECT:
            polarity = EvidencePolarity.POSITIVE
        elif answer_status == AnswerStatus.INCORRECT:
            polarity = EvidencePolarity.NEGATIVE
        else:
            polarity = EvidencePolarity.NEUTRAL
        misconception = self.misconception
        if misconception == "":
            misconception = None
        return Evidence(
            response_id=response_id,
            answer_status=answer_status,
            reasoning_quality=reasoning,
            error_type=error,
            misconception_signal=misconception,
            confidence_signal=confidence,
            evidence_strength=strength,
            diagnostic_confidence=diagnostic,
            evidence_reliability=reliability,
            polarity=polarity,
        )


def _map_error_type(value: str | None, answer_status: AnswerStatus) -> ErrorPattern:
    if value is None:
        return ErrorPattern.NONE if answer_status == AnswerStatus.CORRECT else ErrorPattern.UNKNOWN
    return {
        "conceptual": ErrorPattern.CONCEPTUAL,
        "procedural": ErrorPattern.PROCEDURAL,
        "arithmetic": ErrorPattern.ARITHMETIC,
        "misreading": ErrorPattern.CARELESS,
        "insufficient_evidence": ErrorPattern.UNKNOWN,
        "unknown": ErrorPattern.UNKNOWN,
    }[value]


def _map_uncertainty(
    uncertainty: str,
    strength: EvidenceStrength,
) -> tuple[DiagnosticConfidence, EvidenceReliability]:
    if strength == EvidenceStrength.INSUFFICIENT:
        return DiagnosticConfidence.UNKNOWN, EvidenceReliability.LOW
    if uncertainty == "low":
        return DiagnosticConfidence.HIGH, EvidenceReliability.HIGH
    if uncertainty == "medium":
        return DiagnosticConfidence.MODERATE, EvidenceReliability.MODERATE
    return DiagnosticConfidence.LOW, EvidenceReliability.LOW


SCHEMA_PROMPT_BLOCK = """Required JSON object (no markdown, no extra commentary):
{
  "correctness": "correct | incorrect | unclear",
  "reasoning_quality": "strong | partial | weak | missing",
  "confidence_signal": "high | medium | low | unclear",
  "misconception": null or string,
  "error_type": null or "conceptual | procedural | arithmetic | misreading | insufficient_evidence | unknown",
  "evidence_strength": "strong | moderate | weak | insufficient",
  "uncertainty": "low | medium | high",
  "supporting_evidence": ["short quotes or observations from the learner input"]
}
"""
