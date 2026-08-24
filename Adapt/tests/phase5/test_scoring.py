"""Scoring correctness, missing answers, and gain arithmetic."""

from __future__ import annotations

from adapt.eval.materials import PRETEST, items_by_id
from adapt.eval.scoring import learning_gain, paired_delta, score_item, score_test


def test_correct_normalized_answer_scores_one():
    item = items_by_id()["PRE-A-002"]
    result = score_item(item, "x = 4")
    assert result["correct"] is True
    assert result["points"] == 1.0


def test_incorrect_answer_scores_zero():
    item = items_by_id()["PRE-A-001"]
    result = score_item(item, "12")
    assert result["correct"] is False
    assert result["points"] == 0.0


def test_missing_answer_is_missing_not_fabricated():
    item = items_by_id()["PRE-F-001"]
    result = score_item(item, None)
    assert result["status"] == "MISSING"
    assert result["correct"] is False


def test_score_test_proportion():
    answers = {item.item_id: item.correct_answer for item in PRETEST}
    payload = score_test(PRETEST, answers)
    assert payload["score"] == 1.0
    assert payload["complete"] is True


def test_partial_form_does_not_invent_remaining_answers():
    payload = score_test(PRETEST, {"PRE-A-001": "5"})
    assert payload["missing"] == 7
    assert payload["score"] == 1 / 8
    assert payload["complete"] is False


def test_gain_and_delta():
    assert learning_gain(0.50, 0.70) == 0.20
    assert learning_gain(None, 0.70) is None
    assert paired_delta(0.20, 0.10) == 0.10
    assert paired_delta(0.10, 0.20) == -0.10
    assert paired_delta(0.15, 0.15) == 0.0
    assert paired_delta(None, 0.1) is None
