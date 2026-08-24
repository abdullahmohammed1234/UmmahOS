"""Product-layer challenge types. Engine ChallengeType remains frozen."""

from __future__ import annotations

from adapt.models.enums import ChallengeType, Difficulty

PRODUCT_CHALLENGE_TYPES = (
    "DIRECT",
    "MULTIPLE_CHOICE",
    "ERROR_ANALYSIS",
    "PREDICTION",
    "APPLICATION",
    "TRANSFER",
    "DIAGNOSTIC",
    "REMEDIATION",
    "CONCEPT_CHECK",
    "TRUE_FALSE",
    "EXPLANATION",
    "COMPARE",
    "SCENARIO",
    "SEQUENCE",
    "NUMERIC",
    "SHORT_ANSWER",
    "DEBUG",
    "MATCH",
    "DIAGRAM",
    "ESTIMATION",
    "EXPLAIN_CHOICE",
)

TYPE_TO_ENGINE = {
    "DIRECT": ChallengeType.STANDARD,
    "MULTIPLE_CHOICE": ChallengeType.STANDARD,
    "ERROR_ANALYSIS": ChallengeType.DIAGNOSTIC,
    "PREDICTION": ChallengeType.PROBE,
    "APPLICATION": ChallengeType.TRANSFER,
    "TRANSFER": ChallengeType.TRANSFER,
    "DIAGNOSTIC": ChallengeType.DIAGNOSTIC,
    "REMEDIATION": ChallengeType.REMEDIATION,
    "CONCEPT_CHECK": ChallengeType.STANDARD,
    "TRUE_FALSE": ChallengeType.STANDARD,
    "EXPLANATION": ChallengeType.PROBE,
    "COMPARE": ChallengeType.DIAGNOSTIC,
    "SCENARIO": ChallengeType.TRANSFER,
    "SEQUENCE": ChallengeType.PRACTICE,
    "NUMERIC": ChallengeType.STANDARD,
    "SHORT_ANSWER": ChallengeType.STANDARD,
    "DEBUG": ChallengeType.DIAGNOSTIC,
    "MATCH": ChallengeType.DIAGNOSTIC,
    "DIAGRAM": ChallengeType.STANDARD,
    "ESTIMATION": ChallengeType.STANDARD,
    "EXPLAIN_CHOICE": ChallengeType.PROBE,
}

DEFAULT_STRATEGY_FIT = {
    "DIRECT": ("MAINTAIN", "GATHER_EVIDENCE", "ASSESS", "DECREASE", "RECOVER"),
    "MULTIPLE_CHOICE": ("MAINTAIN", "GATHER_EVIDENCE", "ASSESS", "RECOVER"),
    "ERROR_ANALYSIS": ("PROBE", "GATHER_EVIDENCE", "ASSESS", "REMEDIATE"),
    "PREDICTION": ("PROBE", "GATHER_EVIDENCE", "ASSESS"),
    "APPLICATION": ("INCREASE", "MAINTAIN", "RECOVER"),
    "TRANSFER": ("INCREASE", "MAINTAIN"),
    "DIAGNOSTIC": ("PROBE", "GATHER_EVIDENCE", "ASSESS"),
    "REMEDIATION": ("REMEDIATE", "DECREASE", "PROBE"),
    "CONCEPT_CHECK": ("MAINTAIN", "GATHER_EVIDENCE", "ASSESS", "DECREASE"),
    "TRUE_FALSE": ("PROBE", "GATHER_EVIDENCE", "ASSESS", "MAINTAIN"),
    "EXPLANATION": ("PROBE", "GATHER_EVIDENCE", "ASSESS"),
    "COMPARE": ("PROBE", "GATHER_EVIDENCE", "ASSESS", "REMEDIATE"),
    "SCENARIO": ("INCREASE", "MAINTAIN", "PROBE"),
    "SEQUENCE": ("MAINTAIN", "GATHER_EVIDENCE", "ASSESS"),
    "NUMERIC": ("MAINTAIN", "GATHER_EVIDENCE", "ASSESS", "DECREASE", "RECOVER"),
    "SHORT_ANSWER": ("MAINTAIN", "GATHER_EVIDENCE", "ASSESS", "PROBE"),
    "DEBUG": ("PROBE", "GATHER_EVIDENCE", "ASSESS", "REMEDIATE"),
    "MATCH": ("PROBE", "GATHER_EVIDENCE", "ASSESS", "MAINTAIN"),
    "DIAGRAM": ("MAINTAIN", "PROBE", "GATHER_EVIDENCE", "ASSESS"),
    "ESTIMATION": ("MAINTAIN", "PROBE", "INCREASE"),
    "EXPLAIN_CHOICE": ("PROBE", "GATHER_EVIDENCE", "ASSESS"),
}


def product_difficulty_to_engine(level: int) -> Difficulty:
    if level <= 2:
        return Difficulty.EASY
    if level == 3:
        return Difficulty.MEDIUM
    return Difficulty.HARD


def engine_difficulty_to_product(difficulty: Difficulty) -> int:
    if difficulty == Difficulty.EASY:
        return 2
    if difficulty == Difficulty.MEDIUM:
        return 3
    return 4


def engine_type_for_product(product_type: str, *, difficulty: int) -> ChallengeType:
    if difficulty >= 4 and product_type in {
        "DIRECT",
        "APPLICATION",
        "TRANSFER",
        "SCENARIO",
        "NUMERIC",
        "ESTIMATION",
    }:
        return ChallengeType.INCREASED_DIFFICULTY
    return TYPE_TO_ENGINE.get(product_type, ChallengeType.STANDARD)


def engine_type_to_product(challenge_type: ChallengeType) -> str:
    mapping = {
        ChallengeType.STANDARD: "DIRECT",
        ChallengeType.PRACTICE: "DIRECT",
        ChallengeType.DIAGNOSTIC: "DIAGNOSTIC",
        ChallengeType.REMEDIATION: "REMEDIATION",
        ChallengeType.PROBE: "PREDICTION",
        ChallengeType.TRANSFER: "TRANSFER",
        ChallengeType.INCREASED_DIFFICULTY: "DIRECT",
    }
    return mapping.get(challenge_type, "DIRECT")
