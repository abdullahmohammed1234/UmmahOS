"""Fair baseline integrity: no AdaptiveTutor, no mastery-driven sequence."""

from __future__ import annotations

from adapt.eval.baseline import LinearTutor
from adapt.eval.constants import BASELINE_SEQUENCE
from adapt.eval.integrity import baseline_forbidden_imports
from adapt.models.enums import LearnerConfidence
from adapt.tutor.challenge_bank import PHASE3_BY_ID


def test_baseline_does_not_import_adaptive_components():
    assert baseline_forbidden_imports() == []


def test_baseline_sequence_ignores_correctness_and_mastery():
    right = LinearTutor()
    wrong = LinearTutor()
    for challenge_id in BASELINE_SEQUENCE:
        challenge = PHASE3_BY_ID[challenge_id]
        right.submit(
            answer=challenge.expected_answer or "1",
            confidence=LearnerConfidence.HIGH,
            reasoning="I used inverse operations on both sides and distribute.",
        )
        wrong.submit(
            answer="0",
            confidence=LearnerConfidence.LOW,
            reasoning="I guessed.",
        )
    assert [step.challenge_id for step in right.steps] == list(BASELINE_SEQUENCE)
    assert [step.challenge_id for step in wrong.steps] == list(BASELINE_SEQUENCE)
    assert [step.next_challenge_id for step in right.steps] == [
        step.next_challenge_id for step in wrong.steps
    ]


def test_baseline_is_deterministic_for_the_same_seed():
    first = LinearTutor(seed=20260814)
    second = LinearTutor(seed=20260814)
    for challenge_id in BASELINE_SEQUENCE:
        answer = PHASE3_BY_ID[challenge_id].expected_answer or "1"
        first.submit(answer=answer)
        second.submit(answer=answer)
    assert first.to_dict()["sequence"] == second.to_dict()["sequence"]
    assert [step.challenge_id for step in first.steps] == [
        step.challenge_id for step in second.steps
    ]


def test_baseline_uses_comparable_content():
    tutor = LinearTutor()
    ids = tutor.challenge_ids()
    assert len(ids) == 8
    concepts = {PHASE3_BY_ID[item].concept_id for item in ids}
    assert concepts == {"basic_algebra", "fractions"}
    assert tutor.to_dict()["uses_adaptive_tutor"] is False
    assert tutor.to_dict()["uses_learner_state"] is False
    assert tutor.to_dict()["uses_strategy"] is False


def test_baseline_provides_feedback():
    tutor = LinearTutor()
    step = tutor.submit(answer="999")
    assert step.feedback["headline"]
    assert step.feedback["detail"]
