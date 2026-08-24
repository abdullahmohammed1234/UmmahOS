"""Controlled vocabularies frozen by Phase 1C / required by Phase 1D."""

from __future__ import annotations

from enum import Enum


class ReasoningQuality(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    UNKNOWN = "UNKNOWN"


class ErrorPattern(str, Enum):
    NONE = "NONE"
    CONCEPTUAL = "CONCEPTUAL"
    PROCEDURAL = "PROCEDURAL"
    ARITHMETIC = "ARITHMETIC"
    CARELESS = "CARELESS"
    UNKNOWN = "UNKNOWN"


class EvidenceStrength(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    INSUFFICIENT = "INSUFFICIENT"
    CONTRADICTORY = "CONTRADICTORY"


class EvidenceReliability(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class LearningTrajectory(str, Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    REGRESSING = "REGRESSING"
    OSCILLATING = "OSCILLATING"
    UNKNOWN = "UNKNOWN"


class Uncertainty(str, Enum):
    LOW_UNCERTAINTY = "LOW_UNCERTAINTY"
    MODERATE_UNCERTAINTY = "MODERATE_UNCERTAINTY"
    HIGH_UNCERTAINTY = "HIGH_UNCERTAINTY"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONTRADICTORY_EVIDENCE = "CONTRADICTORY_EVIDENCE"


class AnswerStatus(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    PARTIAL = "PARTIAL"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"


class LearnerConfidence(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class DiagnosticConfidence(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class AdaptationAction(str, Enum):
    INCREASE_DIFFICULTY = "INCREASE_DIFFICULTY"
    MAINTAIN_DIFFICULTY = "MAINTAIN_DIFFICULTY"
    DECREASE_DIFFICULTY = "DECREASE_DIFFICULTY"
    REMEDIATE = "REMEDIATE"
    PROBE_UNCERTAINTY = "PROBE_UNCERTAINTY"
    CHANGE_REPRESENTATION = "CHANGE_REPRESENTATION"
    GATHER_MORE_EVIDENCE = "GATHER_MORE_EVIDENCE"


class StrategyName(str, Enum):
    """Instructional strategy. Distinct from learner mastery and from AdaptationAction."""

    ASSESS = "ASSESS"
    PROBE = "PROBE"
    MAINTAIN = "MAINTAIN"
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    REMEDIATE = "REMEDIATE"
    RECOVER = "RECOVER"
    GATHER_EVIDENCE = "GATHER_EVIDENCE"


class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ChallengeType(str, Enum):
    PRACTICE = "PRACTICE"
    DIAGNOSTIC = "DIAGNOSTIC"
    REMEDIATION = "REMEDIATION"
    STANDARD = "STANDARD"
    PROBE = "PROBE"
    TRANSFER = "TRANSFER"
    INCREASED_DIFFICULTY = "INCREASED_DIFFICULTY"


class EvidencePolarity(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


STRENGTH_RANK = {
    EvidenceStrength.CONTRADICTORY: 0,
    EvidenceStrength.INSUFFICIENT: 1,
    EvidenceStrength.WEAK: 2,
    EvidenceStrength.MODERATE: 3,
    EvidenceStrength.STRONG: 4,
}

DIFFICULTY_ORDER = (Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD)


def parse_enum(value, enum_cls, *, field_name: str, error_cls: type[Exception]):
    """Parse an enum without silently mapping unknown strings to a default."""
    if isinstance(value, enum_cls):
        return value
    if value is None:
        raise error_cls(f"{field_name} is required")
    if isinstance(value, str):
        try:
            return enum_cls(value)
        except ValueError as exc:
            allowed = ", ".join(item.value for item in enum_cls)
            raise error_cls(
                f"Unsupported {field_name}={value!r}. Allowed: {allowed}"
            ) from exc
    raise error_cls(f"Unsupported {field_name} type: {type(value).__name__}")
