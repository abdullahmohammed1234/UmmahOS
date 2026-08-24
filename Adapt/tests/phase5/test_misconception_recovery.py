"""Misconception recovery requires conceptual evidence, not a lucky answer."""

from __future__ import annotations

from adapt.eval.materials import POSTTEST_ADAPT
from adapt.eval.recovery import evaluate_recovery


def test_lucky_correct_without_reasoning_is_not_recovery():
    training = [
        {
            "challenge_id": "ALG-D-001",
            "answer": "2x+3",
            "reasoning": "I multiplied only the first term, so 2x+3. I didn't distribute.",
            "answer_status": "INCORRECT",
            "evidence": {"misconception_signal": "DIST_PROP", "answer_status": "INCORRECT"},
        }
    ]
    post = [{"item_id": "POST-A-003", "answer": "3x+15", "reasoning": None}]
    result = evaluate_recovery(training_steps=training, post_items=post, post_form=POSTTEST_ADAPT)
    dist = next(item for item in result["scenarios"] if item["misconception"] == "DIST_PROP")
    assert dist["recovered"] == 0
    assert dist["status"] == "NOT_RECOVERED"


def test_conceptual_correct_after_misconception_is_recovery():
    training = [
        {
            "challenge_id": "ALG-D-001",
            "answer": "2x+3",
            "reasoning": "I didn't distribute to both terms.",
            "answer_status": "INCORRECT",
            "evidence": {"misconception_signal": "DIST_PROP", "answer_status": "INCORRECT"},
        }
    ]
    post = [
        {
            "item_id": "POST-A-003",
            "answer": "3x+15",
            "reasoning": "Distribute to both terms: 3 times x and 3 times 5.",
        }
    ]
    result = evaluate_recovery(training_steps=training, post_items=post, post_form=POSTTEST_ADAPT)
    dist = next(item for item in result["scenarios"] if item["misconception"] == "DIST_PROP")
    assert dist["recovered"] == 1
    assert dist["status"] == "RECOVERED"


def test_unobserved_misconception_is_not_applicable():
    result = evaluate_recovery(
        training_steps=[{"challenge_id": "ALG-E-001", "answer": "5", "answer_status": "CORRECT"}],
        post_items=[{"item_id": "POST-A-003", "answer": "3x+15", "reasoning": "distribute both terms"}],
        post_form=POSTTEST_ADAPT,
    )
    dist = next(item for item in result["scenarios"] if item["misconception"] == "DIST_PROP")
    assert dist["status"] == "NOT_APPLICABLE"
    assert dist["recovered"] is None
    assert result["applicable"] == 0
