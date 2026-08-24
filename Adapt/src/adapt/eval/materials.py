"""Frozen Phase 5 pre-test, post-test, and training materials.

Pre/post items are equivalent but not identical to each other or to training
challenges. Correct answers are not included in learner-facing views.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.eval.constants import BASELINE_SEQUENCE
from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty
from adapt.tutor.challenge_bank import PHASE3_BY_ID


@dataclass(frozen=True)
class AssessmentItem:
    item_id: str
    concept: str
    difficulty: str
    question: str
    correct_answer: str
    accepted_answers: tuple[str, ...]
    scoring_rule: str
    misconception_target: str | None = None
    expected_reasoning_cues: tuple[str, ...] = ()

    def learner_view(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "concept": self.concept,
            "difficulty": self.difficulty,
            "question": self.question,
        }

    def to_dict(self, *, include_answer: bool = False) -> dict[str, Any]:
        payload = self.learner_view()
        payload["scoring_rule"] = self.scoring_rule
        payload["misconception_target"] = self.misconception_target
        if include_answer:
            payload["correct_answer"] = self.correct_answer
            payload["accepted_answers"] = list(self.accepted_answers)
            payload["expected_reasoning_cues"] = list(self.expected_reasoning_cues)
        return payload

    def as_challenge(self) -> Challenge:
        difficulty = Difficulty[self.difficulty.upper()]
        return Challenge(
            challenge_id=self.item_id,
            concept_id=self.concept,
            difficulty=difficulty,
            question=self.question,
            challenge_type=ChallengeType.DIAGNOSTIC,
            expected_answer=self.correct_answer,
            expected_reasoning_cues=self.expected_reasoning_cues,
        )


def _item(
    item_id: str,
    concept: str,
    difficulty: str,
    question: str,
    correct_answer: str,
    *,
    accepted: tuple[str, ...] = (),
    scoring_rule: str = "normalized_exact_or_alias",
    misconception_target: str | None = None,
    cues: tuple[str, ...] = (),
) -> AssessmentItem:
    aliases = (correct_answer,) + tuple(a for a in accepted if a != correct_answer)
    return AssessmentItem(
        item_id=item_id,
        concept=concept,
        difficulty=difficulty,
        question=question,
        correct_answer=correct_answer,
        accepted_answers=aliases,
        scoring_rule=scoring_rule,
        misconception_target=misconception_target,
        expected_reasoning_cues=cues,
    )


ALG = "basic_algebra"
FR = "fractions"

PRETEST: tuple[AssessmentItem, ...] = (
    _item("PRE-A-001", ALG, "easy", "What is 8 - 3?", "5", cues=("subtract", "difference")),
    _item(
        "PRE-A-002", ALG, "medium", "Solve for x: 4x + 2 = 18", "4",
        accepted=("x=4", "x = 4"), cues=("subtract", "divide", "both sides", "isolate"),
    ),
    _item(
        "PRE-A-003", ALG, "medium", "Expand 3(x + 4). What is the result?", "3x+12",
        accepted=("3x + 12",), misconception_target="DIST_PROP",
        cues=("distribute", "both terms", "3x+12"),
    ),
    _item(
        "PRE-A-004", ALG, "medium", "Solve for x: 5x - 5 = 20", "5",
        accepted=("x=5", "x = 5"), cues=("add", "divide", "both sides", "isolate"),
    ),
    _item(
        "PRE-F-001", FR, "easy", "What is 2/8 + 3/8?", "5/8",
        accepted=("0.625",), cues=("same denominator", "add the numerators"),
    ),
    _item(
        "PRE-F-002", FR, "medium", "What is 1/3 + 1/6?", "1/2",
        accepted=("3/6", "0.5"), misconception_target="ADD_DENOM",
        cues=("common denominator", "equivalent", "numerators"),
    ),
    _item(
        "PRE-F-003", FR, "easy", "What is 3/5 + 1/5?", "4/5",
        accepted=("0.8",), cues=("same denominator", "add the numerators"),
    ),
    _item(
        "PRE-F-004", FR, "hard", "What is 1/2 + 1/5?", "7/10",
        accepted=("0.7",), misconception_target="ADD_DENOM",
        cues=("common denominator", "equivalent", "tenths"),
    ),
)

POSTTEST_ADAPT: tuple[AssessmentItem, ...] = (
    _item("POST-A-001", ALG, "easy", "What is 9 - 4?", "5", cues=("subtract", "difference")),
    _item(
        "POST-A-002", ALG, "medium", "Solve for x: 4x + 1 = 17", "4",
        accepted=("x=4", "x = 4"), cues=("subtract", "divide", "both sides", "isolate"),
    ),
    _item(
        "POST-A-003", ALG, "medium", "Expand 3(x + 5). What is the result?", "3x+15",
        accepted=("3x + 15",), misconception_target="DIST_PROP",
        cues=("distribute", "both terms", "3x+15"),
    ),
    _item(
        "POST-A-004", ALG, "medium", "Solve for x: 5x - 4 = 21", "5",
        accepted=("x=5", "x = 5"), cues=("add", "divide", "both sides", "isolate"),
    ),
    _item(
        "POST-A-005", FR, "easy", "What is 1/8 + 4/8?", "5/8",
        accepted=("0.625",), cues=("same denominator", "add the numerators"),
    ),
    _item(
        "POST-A-006", FR, "medium", "What is 1/5 + 1/10?", "3/10",
        accepted=("0.3",), misconception_target="ADD_DENOM",
        cues=("common denominator", "equivalent", "tenths"),
    ),
    _item(
        "POST-A-007", FR, "easy", "What is 2/7 + 2/7?", "4/7",
        cues=("same denominator", "add the numerators"),
    ),
    _item(
        "POST-A-008", FR, "hard", "What is 1/3 + 1/4?", "7/12",
        misconception_target="ADD_DENOM",
        cues=("common denominator", "equivalent", "twelfths"),
    ),
)

POSTTEST_BASELINE: tuple[AssessmentItem, ...] = (
    _item("POST-B-001", ALG, "easy", "What is 6 - 1?", "5", cues=("subtract", "difference")),
    _item(
        "POST-B-002", ALG, "medium", "Solve for x: 3x + 3 = 15", "4",
        accepted=("x=4", "x = 4"), cues=("subtract", "divide", "both sides", "isolate"),
    ),
    _item(
        "POST-B-003", ALG, "medium", "Expand 4(x + 3). What is the result?", "4x+12",
        accepted=("4x + 12",), misconception_target="DIST_PROP",
        cues=("distribute", "both terms", "4x+12"),
    ),
    _item(
        "POST-B-004", ALG, "medium", "Solve for x: 6x - 6 = 24", "5",
        accepted=("x=5", "x = 5"), cues=("add", "divide", "both sides", "isolate"),
    ),
    _item(
        "POST-B-005", FR, "easy", "What is 4/9 + 1/9?", "5/9",
        cues=("same denominator", "add the numerators"),
    ),
    _item(
        "POST-B-006", FR, "medium", "What is 2/5 + 1/10?", "1/2",
        accepted=("5/10", "0.5"), misconception_target="ADD_DENOM",
        cues=("common denominator", "equivalent", "tenths"),
    ),
    _item(
        "POST-B-007", FR, "easy", "What is 3/10 + 4/10?", "7/10",
        accepted=("0.7",), cues=("same denominator", "add the numerators"),
    ),
    _item(
        "POST-B-008", FR, "hard", "What is 2/3 + 1/5?", "13/15",
        misconception_target="ADD_DENOM",
        cues=("common denominator", "equivalent", "fifteenths"),
    ),
)

POSTTEST_BY_CONDITION = {
    "ADAPT": POSTTEST_ADAPT,
    "BASELINE": POSTTEST_BASELINE,
}

FORMS = {
    "PRE": PRETEST,
    "POST_ADAPT": POSTTEST_ADAPT,
    "POST_BASELINE": POSTTEST_BASELINE,
}


def items_by_id() -> dict[str, AssessmentItem]:
    mapping: dict[str, AssessmentItem] = {}
    for form in FORMS.values():
        for item in form:
            mapping[item.item_id] = item
    return mapping


def learner_form(form: tuple[AssessmentItem, ...]) -> list[dict[str, Any]]:
    return [item.learner_view() for item in form]


def baseline_challenges() -> tuple[Challenge, ...]:
    return tuple(PHASE3_BY_ID[item_id] for item_id in BASELINE_SEQUENCE)


def training_question_set() -> frozenset[str]:
    questions = {PHASE3_BY_ID[item_id].question for item_id in BASELINE_SEQUENCE}
    for item in PHASE3_BY_ID.values():
        questions.add(item.question)
    return frozenset(questions)


def assert_forms_frozen() -> None:
    """Invariant: pre/post questions are not copies of training prompts."""
    training = training_question_set()
    for form_name, form in FORMS.items():
        ids = [item.item_id for item in form]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate item ids in {form_name}")
        for item in form:
            if item.question in training:
                raise ValueError(
                    f"{item.item_id} repeats a training question: {item.question}"
                )
