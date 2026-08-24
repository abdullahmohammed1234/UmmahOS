"""Adaptation decision object. A decision without an evidence trail is invalid."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.errors import InvalidAdaptationDecisionError
from adapt.models.enums import AdaptationAction, DiagnosticConfidence, parse_enum


@dataclass(frozen=True)
class AdaptationDecision:
    decision: AdaptationAction
    reason: tuple[str, ...]
    confidence: DiagnosticConfidence
    evidence_used: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.reason:
            raise InvalidAdaptationDecisionError(
                "Adaptation decision is invalid without an evidence-based reason"
            )
        if not self.evidence_used:
            raise InvalidAdaptationDecisionError(
                "Adaptation decision is invalid without an evidence trail"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": list(self.reason),
            "confidence": self.confidence.value,
            "evidence_used": list(self.evidence_used),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AdaptationDecision:
        if not isinstance(data, dict):
            raise InvalidAdaptationDecisionError("adaptation decision must be an object")
        try:
            return cls(
                decision=parse_enum(
                    data["decision"],
                    AdaptationAction,
                    field_name="decision",
                    error_cls=InvalidAdaptationDecisionError,
                ),
                reason=tuple(data["reason"]),
                confidence=parse_enum(
                    data["confidence"],
                    DiagnosticConfidence,
                    field_name="confidence",
                    error_cls=InvalidAdaptationDecisionError,
                ),
                evidence_used=tuple(data["evidence_used"]),
            )
        except KeyError as exc:
            raise InvalidAdaptationDecisionError(
                f"Missing adaptation-decision field: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise InvalidAdaptationDecisionError(
                f"Malformed adaptation decision: {exc}"
            ) from exc
