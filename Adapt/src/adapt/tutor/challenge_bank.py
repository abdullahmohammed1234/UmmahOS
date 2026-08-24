"""Phase 3 challenge bank.

Does not modify the frozen Phase 1D or Phase 1F banks. Existing items are
re-declared here with diagnostic_value and strategy compatibility metadata.
"""

from __future__ import annotations

from dataclasses import replace

from adapt.adaptation.challenge_bank import CHALLENGE_BANK
from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty

ALGEBRA = "basic_algebra"
FRACTIONS = "fractions"
DIST_PROP = "DIST_PROP"
ADD_DENOM = "ADD_DENOM"
COMBINE_UNLIKE = "COMBINE_UNLIKE"

DIST_CUES = (
    "2x+3",
    "2x + 3",
    "didn't distribute",
    "did not distribute",
    "two x plus three",
)
ADD_CUES = ("2/5", "add the denominators", "add tops and bottoms")
UNLIKE_CUES = ("5x", "combine like", "2x+3=5x")

ALG_METHOD = ("subtract", "both sides", "divide", "inverse", "isolate", "undo")
ALG_REASON = ("subtract", "both sides", "divide", "inverse operations", "isolate")
FRAC_METHOD = ("common denominator", "equivalent", "numerators", "denominator")
FRAC_REASON = ("common denominator", "equivalent fractions", "add the numerators")


def _c(
    challenge_id: str,
    concept_id: str,
    difficulty: Difficulty,
    question: str,
    challenge_type: ChallengeType,
    expected_answer: str,
    expected_reasoning_cues: tuple[str, ...],
    correct_method_cues: tuple[str, ...],
    *,
    misconception_cues: tuple[tuple[str, tuple[str, ...]], ...] = (),
    target_misconception: str | None = None,
    representation: str = "symbolic",
    diagnostic_value: float = 0.5,
    strategy_compatibility: tuple[str, ...] = (),
) -> Challenge:
    return Challenge(
        challenge_id=challenge_id,
        concept_id=concept_id,
        difficulty=difficulty,
        question=question,
        challenge_type=challenge_type,
        expected_answer=expected_answer,
        expected_reasoning_cues=expected_reasoning_cues,
        correct_method_cues=correct_method_cues,
        misconception_cues=misconception_cues,
        target_misconception=target_misconception,
        representation=representation,
        diagnostic_value=diagnostic_value,
        strategy_compatibility=strategy_compatibility,
    )


def _upgrade_existing() -> tuple[Challenge, ...]:
    upgraded = []
    for item in CHALLENGE_BANK:
        extra_misc = item.misconception_cues
        if item.concept_id == ALGEBRA and not extra_misc:
            extra_misc = ((DIST_PROP, DIST_CUES),)
        diagnostic = 0.85 if item.challenge_type.value == "DIAGNOSTIC" else 0.72 if item.challenge_type.value == "REMEDIATION" else 0.55
        if item.challenge_type.value == "DIAGNOSTIC":
            diagnostic = 0.88
        upgraded.append(
            replace(
                item,
                misconception_cues=extra_misc,
                diagnostic_value=diagnostic,
                target_misconception=item.target_misconception or (DIST_PROP if extra_misc else None),
            )
        )
    return tuple(upgraded)


def _phase3_new() -> tuple[Challenge, ...]:
    return (
        _c(
            "ALG-E-003", ALGEBRA, Difficulty.EASY, "What is 5 + 4?",
            ChallengeType.STANDARD, "9", ("add", "sum"), ("add", "sum"),
            misconception_cues=((DIST_PROP, DIST_CUES),), diagnostic_value=0.45,
        ),
        _c(
            "ALG-E-004", ALGEBRA, Difficulty.EASY, "What is 9 - 6?",
            ChallengeType.STANDARD, "3", ("subtract", "difference"), ("subtract", "difference"),
            misconception_cues=((DIST_PROP, DIST_CUES),), diagnostic_value=0.45,
        ),
        _c(
            "ALG-M-005", ALGEBRA, Difficulty.MEDIUM, "Solve for x: 5x + 1 = 16",
            ChallengeType.STANDARD, "3", ALG_REASON, ALG_METHOD,
            misconception_cues=((DIST_PROP, DIST_CUES),), diagnostic_value=0.58,
        ),
        _c(
            "ALG-M-006", ALGEBRA, Difficulty.MEDIUM, "Solve for x: 2(x + 4) = 14",
            ChallengeType.STANDARD, "3", ("divide", "both sides", "distribute", "subtract"),
            ("divide", "both sides", "distribute", "subtract"),
            misconception_cues=((DIST_PROP, DIST_CUES),), target_misconception=DIST_PROP,
            diagnostic_value=0.70,
        ),
        _c(
            "ALG-H-003", ALGEBRA, Difficulty.HARD, "Solve for x: 3(x + 2) = 2x + 11",
            ChallengeType.INCREASED_DIFFICULTY, "5", ("distribute", "both sides", "isolate"),
            ("distribute", "both sides", "isolate"),
            misconception_cues=((DIST_PROP, DIST_CUES),), target_misconception=DIST_PROP,
            diagnostic_value=0.62, strategy_compatibility=("INCREASE", "MAINTAIN"),
        ),
        _c(
            "ALG-H-004", ALGEBRA, Difficulty.HARD, "Solve for x: 4(x - 1) + 2 = 3x + 5",
            ChallengeType.INCREASED_DIFFICULTY, "7", ("distribute", "both sides", "combine"),
            ("distribute", "both sides", "combine"),
            misconception_cues=((DIST_PROP, DIST_CUES),), diagnostic_value=0.60,
            strategy_compatibility=("INCREASE", "MAINTAIN"),
        ),
        _c(
            "ALG-P-001", ALGEBRA, Difficulty.MEDIUM,
            "Does 2(x + 3) equal 2x + 3 or 2x + 6? Explain how you know.",
            ChallengeType.PROBE, "2x+6", ("distribute", "both terms", "2x+6"),
            ("distribute", "both"),
            misconception_cues=((DIST_PROP, DIST_CUES),), target_misconception=DIST_PROP,
            diagnostic_value=0.95, strategy_compatibility=("PROBE", "GATHER_EVIDENCE", "ASSESS"),
        ),
        _c(
            "ALG-P-002", ALGEBRA, Difficulty.EASY,
            "If a learner expands 2(x+3) as 2x+3, what did they forget?",
            ChallengeType.PROBE, "distribute", ("distribute", "both terms"),
            ("distribute", "both"),
            misconception_cues=((DIST_PROP, DIST_CUES),), target_misconception=DIST_PROP,
            diagnostic_value=0.92, strategy_compatibility=("PROBE", "GATHER_EVIDENCE", "ASSESS"),
        ),
        _c(
            "ALG-P-003", ALGEBRA, Difficulty.MEDIUM,
            "Expand 3(x + 1). Write every multiplied term.",
            ChallengeType.PROBE, "3x+3", ("distribute", "multiply both", "3x+3"),
            ("distribute", "multiply"),
            misconception_cues=((DIST_PROP, DIST_CUES),), target_misconception=DIST_PROP,
            diagnostic_value=0.90, strategy_compatibility=("PROBE", "GATHER_EVIDENCE", "ASSESS", "REMEDIATE"),
        ),
        _c(
            "ALG-D-004", ALGEBRA, Difficulty.MEDIUM,
            "Can 2x + 3 be written as 5x? Why or why not?",
            ChallengeType.DIAGNOSTIC, "2x+3", ("unlike terms", "cannot combine"),
            ("unlike terms", "cannot combine"),
            misconception_cues=((COMBINE_UNLIKE, UNLIKE_CUES),), target_misconception=COMBINE_UNLIKE,
            diagnostic_value=0.87,
        ),
        _c(
            "ALG-R-003", ALGEBRA, Difficulty.EASY,
            "Two groups of (x + 3) is 2x + 6. Expand 2(x + 3) using groups.",
            ChallengeType.REMEDIATION, "2x+6", ("two groups", "distribute", "2x+6"),
            ("distribute", "two groups"),
            misconception_cues=((DIST_PROP, DIST_CUES),), target_misconception=DIST_PROP,
            representation="grouped", diagnostic_value=0.80,
            strategy_compatibility=("REMEDIATE", "DECREASE", "PROBE"),
        ),
        _c(
            "ALG-T-001", ALGEBRA, Difficulty.MEDIUM,
            "A number times 2, plus 3, equals 11. What is the number?",
            ChallengeType.TRANSFER, "4", ("subtract", "both sides", "divide", "isolate"),
            ALG_METHOD, representation="worded", diagnostic_value=0.68,
            strategy_compatibility=("INCREASE", "MAINTAIN", "GATHER_EVIDENCE"),
        ),
        _c(
            "ALG-T-002", ALGEBRA, Difficulty.HARD,
            "Twice a number decreased by 3 equals the number plus 1. Find the number.",
            ChallengeType.TRANSFER, "4", ("both sides", "isolate", "subtract"),
            ("both sides", "isolate", "subtract"), representation="worded", diagnostic_value=0.64,
            strategy_compatibility=("INCREASE", "MAINTAIN"),
        ),
        _c(
            "ALG-I-001", ALGEBRA, Difficulty.HARD,
            "Solve for x: (2x + 4)/2 = x - 1",
            ChallengeType.INCREASED_DIFFICULTY, "6", ("multiply", "both sides", "isolate"),
            ("multiply", "both sides", "isolate"), diagnostic_value=0.58,
            strategy_compatibility=("INCREASE",),
        ),
        _c(
            "ALG-I-002", ALGEBRA, Difficulty.HARD,
            "Solve for x: 2(x + 3) + x = 18",
            ChallengeType.INCREASED_DIFFICULTY, "4", ("distribute", "combine", "isolate"),
            ("distribute", "combine", "isolate"),
            misconception_cues=((DIST_PROP, DIST_CUES),), diagnostic_value=0.66,
            strategy_compatibility=("INCREASE", "MAINTAIN"),
        ),
        _c(
            "FR-E-001", FRACTIONS, Difficulty.EASY, "What is 1/2 + 1/2?",
            ChallengeType.STANDARD, "1", ("same denominator", "add the numerators", "one whole"),
            ("numerators", "same denominator"),
            misconception_cues=((ADD_DENOM, ADD_CUES),), diagnostic_value=0.50,
        ),
        _c(
            "FR-E-002", FRACTIONS, Difficulty.EASY, "What is 1/4 + 1/4?",
            ChallengeType.STANDARD, "1/2", ("same denominator", "add the numerators"),
            ("numerators", "same denominator"),
            misconception_cues=((ADD_DENOM, ADD_CUES),), diagnostic_value=0.50,
        ),
        _c(
            "FR-E-003", FRACTIONS, Difficulty.EASY, "What is 2/5 + 1/5?",
            ChallengeType.STANDARD, "3/5", ("same denominator", "add the numerators"),
            ("numerators", "same denominator"),
            misconception_cues=((ADD_DENOM, ADD_CUES),), diagnostic_value=0.48,
        ),
        _c(
            "FR-M-001", FRACTIONS, Difficulty.MEDIUM, "What is 1/2 + 1/3?",
            ChallengeType.STANDARD, "5/6", FRAC_REASON, FRAC_METHOD,
            misconception_cues=((ADD_DENOM, ADD_CUES),), target_misconception=ADD_DENOM,
            diagnostic_value=0.72,
        ),
        _c(
            "FR-M-002", FRACTIONS, Difficulty.MEDIUM, "What is 3/4 - 1/4?",
            ChallengeType.STANDARD, "1/2", ("same denominator", "subtract the numerators"),
            ("same denominator", "numerators"), diagnostic_value=0.55,
        ),
        _c(
            "FR-M-003", FRACTIONS, Difficulty.MEDIUM, "What is 1/4 + 1/6?",
            ChallengeType.STANDARD, "5/12", FRAC_REASON, FRAC_METHOD,
            misconception_cues=((ADD_DENOM, ADD_CUES),), target_misconception=ADD_DENOM,
            diagnostic_value=0.70,
        ),
        _c(
            "FR-H-001", FRACTIONS, Difficulty.HARD, "What is 2/3 + 1/6?",
            ChallengeType.INCREASED_DIFFICULTY, "5/6", FRAC_REASON, FRAC_METHOD,
            misconception_cues=((ADD_DENOM, ADD_CUES),), diagnostic_value=0.60,
            strategy_compatibility=("INCREASE", "MAINTAIN"),
        ),
        _c(
            "FR-H-002", FRACTIONS, Difficulty.HARD, "What is 3/5 - 1/10?",
            ChallengeType.INCREASED_DIFFICULTY, "1/2", FRAC_REASON, FRAC_METHOD,
            diagnostic_value=0.58, strategy_compatibility=("INCREASE", "MAINTAIN"),
        ),
        _c(
            "FR-H-003", FRACTIONS, Difficulty.HARD, "What is 5/6 - 1/4?",
            ChallengeType.INCREASED_DIFFICULTY, "7/12", FRAC_REASON, FRAC_METHOD,
            diagnostic_value=0.57, strategy_compatibility=("INCREASE",),
        ),
        _c(
            "FR-D-001", FRACTIONS, Difficulty.MEDIUM,
            "Is 1/2 + 1/3 equal to 2/5? If not, what is the sum?",
            ChallengeType.DIAGNOSTIC, "5/6", FRAC_REASON, FRAC_METHOD,
            misconception_cues=((ADD_DENOM, ADD_CUES),), target_misconception=ADD_DENOM,
            diagnostic_value=0.93, strategy_compatibility=("PROBE", "GATHER_EVIDENCE", "ASSESS"),
        ),
        _c(
            "FR-D-002", FRACTIONS, Difficulty.EASY,
            "A pizza is cut into sixths. You eat 3/6 and then 2/6. How much did you eat?",
            ChallengeType.DIAGNOSTIC, "5/6", ("same denominator", "add the numerators"),
            ("numerators", "same denominator"), target_misconception=ADD_DENOM,
            representation="worded", diagnostic_value=0.80,
        ),
        _c(
            "FR-P-001", FRACTIONS, Difficulty.MEDIUM,
            "Why is 1/2 + 1/3 not 2/5? What common denominator should you use?",
            ChallengeType.PROBE, "6", ("common denominator", "equivalent", "sixths"),
            FRAC_METHOD, misconception_cues=((ADD_DENOM, ADD_CUES),),
            target_misconception=ADD_DENOM, diagnostic_value=0.94,
            strategy_compatibility=("PROBE", "GATHER_EVIDENCE", "ASSESS", "REMEDIATE"),
        ),
        _c(
            "FR-P-002", FRACTIONS, Difficulty.EASY,
            "When adding 1/2 and 1/3, do you add denominators? Explain.",
            ChallengeType.PROBE, "no", ("common denominator", "not add denominators"),
            ("common denominator", "equivalent"),
            misconception_cues=((ADD_DENOM, ADD_CUES),), target_misconception=ADD_DENOM,
            diagnostic_value=0.91, strategy_compatibility=("PROBE", "GATHER_EVIDENCE", "ASSESS"),
        ),
        _c(
            "FR-R-001", FRACTIONS, Difficulty.EASY,
            "Rewrite 1/2 and 1/3 with denominator 6, then add.",
            ChallengeType.REMEDIATION, "5/6", ("denominator 6", "3/6", "2/6", "5/6"),
            ("common denominator", "equivalent"),
            misconception_cues=((ADD_DENOM, ADD_CUES),), target_misconception=ADD_DENOM,
            representation="area", diagnostic_value=0.82,
            strategy_compatibility=("REMEDIATE", "DECREASE"),
        ),
        _c(
            "FR-R-002", FRACTIONS, Difficulty.EASY,
            "One half of a pan plus one third of a pan is not two fifths. Add with sixths.",
            ChallengeType.REMEDIATION, "5/6", ("sixths", "common denominator", "5/6"),
            ("common denominator", "equivalent"),
            misconception_cues=((ADD_DENOM, ADD_CUES),), target_misconception=ADD_DENOM,
            representation="area", diagnostic_value=0.80,
            strategy_compatibility=("REMEDIATE", "PROBE"),
        ),
        _c(
            "FR-T-001", FRACTIONS, Difficulty.MEDIUM,
            "You walk 1/2 mile then 1/3 mile. How far did you walk?",
            ChallengeType.TRANSFER, "5/6", FRAC_REASON, FRAC_METHOD, representation="worded",
            diagnostic_value=0.67, strategy_compatibility=("INCREASE", "MAINTAIN", "GATHER_EVIDENCE"),
        ),
        _c(
            "FR-I-001", FRACTIONS, Difficulty.HARD, "What is 7/8 - 1/6?",
            ChallengeType.INCREASED_DIFFICULTY, "17/24", FRAC_REASON, FRAC_METHOD,
            diagnostic_value=0.55, strategy_compatibility=("INCREASE",),
        ),
        _c(
            "ALG-M-003", ALGEBRA, Difficulty.MEDIUM, "Solve for x: 4x - 1 = 11",
            ChallengeType.STANDARD, "3", ("add", "both sides", "divide", "isolate"),
            ("add", "both sides", "divide", "isolate"),
            misconception_cues=((DIST_PROP, DIST_CUES),), diagnostic_value=0.56,
        ),
        _c(
            "ALG-M-004", ALGEBRA, Difficulty.MEDIUM, "Solve for x: x/2 + 3 = 7",
            ChallengeType.STANDARD, "8", ("subtract", "both sides", "multiply", "isolate"),
            ("subtract", "both sides", "multiply"), representation="worded", diagnostic_value=0.57,
        ),
        _c(
            "ALG-R-002", ALGEBRA, Difficulty.EASY,
            "2x means two groups of x. 3 means three ones. Why can they not make 5x?",
            ChallengeType.REMEDIATION, "2x+3", ("unlike terms", "cannot combine"),
            ("unlike", "ones"), target_misconception=COMBINE_UNLIKE, representation="grouped",
            diagnostic_value=0.78, strategy_compatibility=("REMEDIATE",),
        ),
        _c(
            "ALG-D-003", ALGEBRA, Difficulty.MEDIUM,
            "Simplify 2x + 3. Can this be written as a single term 5x?",
            ChallengeType.DIAGNOSTIC, "2x+3", ("unlike terms", "cannot combine", "different"),
            ("unlike terms", "cannot combine"),
            misconception_cues=((COMBINE_UNLIKE, UNLIKE_CUES),), target_misconception=COMBINE_UNLIKE,
            diagnostic_value=0.86,
        ),
    )


def build_phase3_bank() -> tuple[Challenge, ...]:
    existing = _upgrade_existing()
    extra = _phase3_new()
    seen: set[str] = set()
    unique: list[Challenge] = []
    for item in extra + existing:
        if item.challenge_id in seen:
            continue
        seen.add(item.challenge_id)
        unique.append(item)
    return tuple(unique)


PHASE3_BANK = build_phase3_bank()
PHASE3_BY_ID = {item.challenge_id: item for item in PHASE3_BANK}

UNAVAILABLE_CHALLENGE = Challenge(
    challenge_id="UNAVAILABLE",
    concept_id="unknown",
    difficulty=Difficulty.EASY,
    question="No challenge is currently available in the bank.",
    challenge_type=ChallengeType.DIAGNOSTIC,
    diagnostic_value=0.0,
)


def get_phase3_challenge(challenge_id: str) -> Challenge:
    return PHASE3_BY_ID[challenge_id]


def challenges_for_concept(concept_id: str) -> tuple[Challenge, ...]:
    return tuple(item for item in PHASE3_BANK if item.concept_id == concept_id)
