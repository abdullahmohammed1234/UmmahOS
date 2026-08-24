"""Frozen pre/post forms and gain calculation."""

from __future__ import annotations

from adapt.eval.materials import (
    POSTTEST_ADAPT,
    POSTTEST_BASELINE,
    PRETEST,
    assert_forms_frozen,
    learner_form,
)
from adapt.eval.scoring import learning_gain, score_test


def test_forms_are_frozen_and_not_training_copies():
    assert_forms_frozen()
    assert len(PRETEST) == 8
    assert len(POSTTEST_ADAPT) == 8
    assert len(POSTTEST_BASELINE) == 8


def test_learner_view_hides_correct_answers():
    for item in learner_form(PRETEST):
        assert "correct_answer" not in item
        assert "accepted_answers" not in item
        assert item["question"]


def test_pre_and_post_questions_differ():
    pre_q = {item.question for item in PRETEST}
    post_q = {item.question for item in POSTTEST_ADAPT + POSTTEST_BASELINE}
    assert pre_q.isdisjoint(post_q)


def test_pre_post_gain_from_scores():
    pre = score_test(PRETEST, {item.item_id: item.correct_answer for item in PRETEST[:4]})
    post = score_test(
        POSTTEST_ADAPT,
        {item.item_id: item.correct_answer for item in POSTTEST_ADAPT[:6]},
    )
    gain = learning_gain(pre["score"], post["score"])
    assert pre["score"] == 0.5
    assert post["score"] == 0.75
    assert gain == 0.25
