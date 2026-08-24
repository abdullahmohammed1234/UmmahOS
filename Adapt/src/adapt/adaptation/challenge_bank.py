"""Deterministic basic-algebra challenge bank."""

from __future__ import annotations

from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty

CONCEPT_ID = "basic_algebra"
DIST_PROP = "DIST_PROP"

METHOD_CUES = (
    "subtract",
    "both sides",
    "divide",
    "inverse",
    "isolate",
    "undo",
)
REASONING_CUES = (
    "subtract",
    "both sides",
    "divide",
    "inverse operations",
    "isolate",
)
DIST_CUES = (
    "2x+3",
    "2x + 3",
    "didn't distribute",
    "did not distribute",
    "two x plus three",
)


def build_challenge_bank() -> tuple[Challenge, ...]:
    return (
        Challenge(
            challenge_id="ALG-E-001",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.EASY,
            question="What is 2 + 3?",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="5",
            expected_reasoning_cues=("add", "sum", "two plus three"),
            correct_method_cues=("add", "sum"),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-E-002",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.EASY,
            question="What is 7 - 4?",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="3",
            expected_reasoning_cues=("subtract", "difference"),
            correct_method_cues=("subtract", "difference"),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-M-001",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.MEDIUM,
            question="Solve for x: 2x + 3 = 11",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="4",
            expected_reasoning_cues=REASONING_CUES,
            correct_method_cues=METHOD_CUES,
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-M-002",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.MEDIUM,
            question="Solve for x: 3(x + 1) = 12",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="3",
            expected_reasoning_cues=("divide", "both sides", "distribute", "subtract"),
            correct_method_cues=("divide", "both sides", "distribute", "subtract"),
            misconception_cues=((DIST_PROP, DIST_CUES),),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-H-001",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.HARD,
            question="Solve for x: 2(x - 3) + 4 = 3x + 1",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="-3",
            expected_reasoning_cues=("distribute", "both sides", "isolate"),
            correct_method_cues=("distribute", "both sides", "combine like terms"),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-H-002",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.HARD,
            question="Solve for x: (x + 2) / 3 = 5",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="13",
            expected_reasoning_cues=("multiply", "both sides", "subtract"),
            correct_method_cues=("multiply", "both sides", "subtract"),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-D-001",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.MEDIUM,
            question="Expand 2(x + 3). What is the result?",
            challenge_type=ChallengeType.DIAGNOSTIC,
            expected_answer="2x+6",
            expected_reasoning_cues=("distribute", "multiply both terms", "2x+6"),
            correct_method_cues=("distribute", "multiply both"),
            misconception_cues=((DIST_PROP, DIST_CUES + ("2x+3", "2x + 3")),),
            target_misconception=DIST_PROP,
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-R-001",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.EASY,
            question=(
                "The expression 2(x + 3) means two groups of (x + 3). "
                "Which expansion is correct: 2x+3 or 2x+6?"
            ),
            challenge_type=ChallengeType.REMEDIATION,
            expected_answer="2x+6",
            expected_reasoning_cues=("two groups", "distribute", "2x+6"),
            correct_method_cues=("distribute", "two groups"),
            misconception_cues=((DIST_PROP, DIST_CUES),),
            target_misconception=DIST_PROP,
            representation="grouped",
        ),
        Challenge(
            challenge_id="ALG-D-002",
            concept_id=CONCEPT_ID,
            difficulty=Difficulty.EASY,
            question=(
                "If you have two bags, and each bag contains x apples plus 3 more, "
                "how many apples are there in total? Write an expression."
            ),
            challenge_type=ChallengeType.DIAGNOSTIC,
            expected_answer="2x+6",
            expected_reasoning_cues=("two bags", "2x", "6"),
            correct_method_cues=("two", "each"),
            misconception_cues=((DIST_PROP, DIST_CUES),),
            target_misconception=DIST_PROP,
            representation="worded",
        ),
    )


CHALLENGE_BANK = build_challenge_bank()
CHALLENGE_BY_ID = {item.challenge_id: item for item in CHALLENGE_BANK}


def get_challenge(challenge_id: str) -> Challenge:
    return CHALLENGE_BY_ID[challenge_id]
