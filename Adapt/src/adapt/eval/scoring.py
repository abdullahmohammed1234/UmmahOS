"""Frozen Phase 5 scoring rules.

Uses the same answer normalization as the Evidence Analyzer. Does not treat
correctness as mastery and does not invent missing answers.
"""

from __future__ import annotations

from typing import Any

from adapt.analysis.evidence_analyzer import _normalize_answer, classify_answer_status
from adapt.eval.materials import AssessmentItem
from adapt.models.enums import AnswerStatus
from adapt.models.learner_response import LearnerResponse


def normalize_answer(text: str | None) -> str:
    if text is None:
        return ""
    return _normalize_answer(str(text))


def score_item(item: AssessmentItem, answer: str | None) -> dict[str, Any]:
    """Score one assessment item. Missing answers are incorrect, not fabricated."""
    if answer is None or str(answer).strip() == "":
        return {
            "item_id": item.item_id,
            "correct": False,
            "points": 0.0,
            "status": "MISSING",
            "scoring_rule": item.scoring_rule,
        }
    given = normalize_answer(answer)
    accepted = {normalize_answer(alias) for alias in item.accepted_answers}
    accepted.add(normalize_answer(item.correct_answer))
    correct = given in accepted and given != ""
    if not correct:
        challenge = item.as_challenge()
        response = LearnerResponse(
            response_id=f"score-{item.item_id}",
            learner_id="scorer",
            concept_id=item.concept,
            challenge_id=item.item_id,
            answer=str(answer),
        )
        status = classify_answer_status(response, challenge)
        if status == AnswerStatus.CORRECT:
            correct = True
    return {
        "item_id": item.item_id,
        "correct": correct,
        "points": 1.0 if correct else 0.0,
        "status": "CORRECT" if correct else "INCORRECT",
        "scoring_rule": item.scoring_rule,
    }


def score_test(
    items: tuple[AssessmentItem, ...] | list[AssessmentItem],
    answers: dict[str, str | None] | list[str | None] | None,
) -> dict[str, Any]:
    """Score a frozen form. Missing items remain missing (scored 0, status MISSING)."""
    item_list = list(items)
    resolved: dict[str, str | None] = {}
    if answers is None:
        resolved = {item.item_id: None for item in item_list}
    elif isinstance(answers, dict):
        resolved = {item.item_id: answers.get(item.item_id) for item in item_list}
    else:
        if len(answers) != len(item_list):
            raise ValueError("answer list length must match the form")
        resolved = {item.item_id: answers[index] for index, item in enumerate(item_list)}

    scored = [score_item(item, resolved[item.item_id]) for item in item_list]
    total = len(item_list)
    points = sum(row["points"] for row in scored)
    missing = sum(1 for row in scored if row["status"] == "MISSING")
    proportion = None if total == 0 else points / total
    return {
        "n_items": total,
        "points": points,
        "score": proportion,
        "missing": missing,
        "complete": missing == 0,
        "items": scored,
    }


def learning_gain(pre_score: float | None, post_score: float | None) -> float | None:
    if pre_score is None or post_score is None:
        return None
    return round(float(post_score) - float(pre_score), 10)


def paired_delta(gain_adapt: float | None, gain_baseline: float | None) -> float | None:
    if gain_adapt is None or gain_baseline is None:
        return None
    return round(float(gain_adapt) - float(gain_baseline), 10)
