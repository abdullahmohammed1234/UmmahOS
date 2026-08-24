"""Phase 1F-only challenges. Does not modify the Phase 1D/1E algebra bank."""

from __future__ import annotations

from adapt.adaptation.challenge_bank import CHALLENGE_BANK
from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty

FRACTIONS = "fractions"
ADD_DENOM = "ADD_DENOM"
COMBINE_UNLIKE = "COMBINE_UNLIKE"
DIST_PROP = "DIST_PROP"

FRAC_METHOD = ("common denominator", "equivalent", "numerators", "denominator")
FRAC_REASON = ("common denominator", "equivalent fractions", "add the numerators")


def _frac_bank() -> tuple[Challenge, ...]:
    return (
        Challenge(
            challenge_id="FR-E-001",
            concept_id=FRACTIONS,
            difficulty=Difficulty.EASY,
            question="What is 1/2 + 1/2?",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="1",
            expected_reasoning_cues=("same denominator", "add the numerators", "one whole"),
            correct_method_cues=("numerators", "same denominator"),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="FR-E-002",
            concept_id=FRACTIONS,
            difficulty=Difficulty.EASY,
            question="What is 1/4 + 1/4?",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="1/2",
            expected_reasoning_cues=("same denominator", "add the numerators", "two fourths"),
            correct_method_cues=("numerators", "same denominator"),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="FR-M-001",
            concept_id=FRACTIONS,
            difficulty=Difficulty.MEDIUM,
            question="What is 1/2 + 1/3?",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="5/6",
            expected_reasoning_cues=FRAC_REASON,
            correct_method_cues=FRAC_METHOD,
            misconception_cues=(
                (ADD_DENOM, ("2/5", "add the denominators", "add tops and bottoms")),
            ),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="FR-M-002",
            concept_id=FRACTIONS,
            difficulty=Difficulty.MEDIUM,
            question="What is 3/4 - 1/4?",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="1/2",
            expected_reasoning_cues=("same denominator", "subtract the numerators"),
            correct_method_cues=("same denominator", "numerators"),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="FR-H-001",
            concept_id=FRACTIONS,
            difficulty=Difficulty.HARD,
            question="What is 2/3 + 1/6?",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="5/6",
            expected_reasoning_cues=FRAC_REASON,
            correct_method_cues=FRAC_METHOD,
            representation="symbolic",
        ),
        Challenge(
            challenge_id="FR-H-002",
            concept_id=FRACTIONS,
            difficulty=Difficulty.HARD,
            question="What is 3/5 - 1/10?",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="1/2",
            expected_reasoning_cues=FRAC_REASON,
            correct_method_cues=FRAC_METHOD,
            representation="symbolic",
        ),
        Challenge(
            challenge_id="FR-D-001",
            concept_id=FRACTIONS,
            difficulty=Difficulty.MEDIUM,
            question="Is 1/2 + 1/3 equal to 2/5? If not, what is the sum?",
            challenge_type=ChallengeType.DIAGNOSTIC,
            expected_answer="5/6",
            expected_reasoning_cues=FRAC_REASON,
            correct_method_cues=FRAC_METHOD,
            misconception_cues=(
                (ADD_DENOM, ("2/5", "add the denominators", "add tops and bottoms")),
            ),
            target_misconception=ADD_DENOM,
            representation="symbolic",
        ),
        Challenge(
            challenge_id="FR-R-001",
            concept_id=FRACTIONS,
            difficulty=Difficulty.EASY,
            question=(
                "One half of a pan plus one third of a pan is not two fifths. "
                "Rewrite both fractions with denominator 6, then add."
            ),
            challenge_type=ChallengeType.REMEDIATION,
            expected_answer="5/6",
            expected_reasoning_cues=("denominator 6", "3/6", "2/6", "5/6"),
            correct_method_cues=("common denominator", "equivalent"),
            misconception_cues=((ADD_DENOM, ("2/5", "add the denominators")),),
            target_misconception=ADD_DENOM,
            representation="area",
        ),
        Challenge(
            challenge_id="FR-D-002",
            concept_id=FRACTIONS,
            difficulty=Difficulty.EASY,
            question="A pizza is cut into sixths. You eat 3/6 and then 2/6. How much did you eat?",
            challenge_type=ChallengeType.DIAGNOSTIC,
            expected_answer="5/6",
            expected_reasoning_cues=("same denominator", "add the numerators"),
            correct_method_cues=("numerators", "same denominator"),
            target_misconception=ADD_DENOM,
            representation="worded",
        ),
        Challenge(
            challenge_id="ALG-D-003",
            concept_id="basic_algebra",
            difficulty=Difficulty.MEDIUM,
            question="Simplify 2x + 3. Can this be written as a single term 5x?",
            challenge_type=ChallengeType.DIAGNOSTIC,
            expected_answer="2x+3",
            expected_reasoning_cues=("unlike terms", "cannot combine", "different"),
            correct_method_cues=("unlike terms", "cannot combine"),
            misconception_cues=(
                (COMBINE_UNLIKE, ("5x", "combine like", "2x+3=5x")),
            ),
            target_misconception=COMBINE_UNLIKE,
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-R-002",
            concept_id="basic_algebra",
            difficulty=Difficulty.EASY,
            question=(
                "2x means two groups of x. 3 means three ones. Why can they not be added "
                "to make 5x?"
            ),
            challenge_type=ChallengeType.REMEDIATION,
            expected_answer="2x+3",
            expected_reasoning_cues=("unlike terms", "cannot combine"),
            correct_method_cues=("unlike", "ones"),
            target_misconception=COMBINE_UNLIKE,
            representation="grouped",
        ),
        Challenge(
            challenge_id="ALG-M-003",
            concept_id="basic_algebra",
            difficulty=Difficulty.MEDIUM,
            question="Solve for x: 4x - 1 = 11",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="3",
            expected_reasoning_cues=("add", "both sides", "divide", "isolate"),
            correct_method_cues=("add", "both sides", "divide", "isolate"),
            representation="symbolic",
        ),
        Challenge(
            challenge_id="ALG-M-004",
            concept_id="basic_algebra",
            difficulty=Difficulty.MEDIUM,
            question="Solve for x: x/2 + 3 = 7",
            challenge_type=ChallengeType.PRACTICE,
            expected_answer="8",
            expected_reasoning_cues=("subtract", "both sides", "multiply", "isolate"),
            correct_method_cues=("subtract", "both sides", "multiply"),
            representation="worded",
        ),
    )


PHASE1F_CHALLENGES = _frac_bank()
COMBINED_BANK = CHALLENGE_BANK + PHASE1F_CHALLENGES
CHALLENGE_BY_ID = {item.challenge_id: item for item in COMBINED_BANK}


def get_challenge(challenge_id: str) -> Challenge:
    return CHALLENGE_BY_ID[challenge_id]
