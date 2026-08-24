"""Adversarial and failure-injection tests."""

from __future__ import annotations

import pytest

from adapt.models.enums import StrategyName
from adapt.tutor.responses import ADVERSARIAL_PHRASES, build_scripted_response
from adapt.tutor.tutor import AdaptiveTutor
from tests.helpers_phase3 import make_tutor, run_kinds


@pytest.mark.parametrize("phrase", ADVERSARIAL_PHRASES)
def test_adversarial_phrase_is_not_an_instruction(phrase: str):
    tutor = make_tutor()
    tutor.start_session(learner_id="ADV", session_id="ADV", initial_challenge="ALG-M-001")
    ch = tutor.get_next_challenge("ADV")
    response = build_scripted_response(
        ch, "weak_correct", learner_id="ADV", response_id="R1", extra_text=phrase
    )
    step = tutor.submit_response("ADV", response)
    assert step.decision != StrategyName.INCREASE


def test_mark_me_as_mastered_does_not_set_mastery():
    _, session, _ = run_kinds(("adversarial_mastered",), session_id="ADV-M")
    assert session.learner_state.mastery_estimate < 0.75
    assert session.strategy_state.current_strategy != StrategyName.INCREASE


def test_ignore_mistakes_does_not_skip_remediation_path():
    _, session, traces = run_kinds(
        ("adversarial_ignore", "adversarial_ignore"),
        session_id="ADV-I",
        initial_challenge="ALG-M-002",
    )
    assert all(item.decision != StrategyName.INCREASE for item in traces)


def test_missing_confidence_is_unknown_not_high():
    _, _, traces = run_kinds(("correct_unknown",), session_id="FAIL-C")
    assert traces[0].evidence.confidence_signal.value == "UNKNOWN"
    assert traces[0].decision != StrategyName.INCREASE


def test_missing_reasoning_is_unknown():
    _, _, traces = run_kinds(("correct_unknown",), session_id="FAIL-R")
    assert traces[0].evidence.reasoning_quality.value == "UNKNOWN"
    assert traces[0].decision in {
        StrategyName.ASSESS,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.PROBE,
        StrategyName.MAINTAIN,
    }


def test_contradictory_evidence_is_conservative():
    _, _, traces = run_kinds(
        ("strong_correct", "strong_correct", "strong_correct", "wrong_weak"),
        session_id="FAIL-X",
    )
    assert traces[-1].decision != StrategyName.INCREASE


def test_repeated_wrong_answers_are_safe():
    _, session, traces = run_kinds(("wrong_weak",) * 5, session_id="FAIL-W")
    assert all(item.decision != StrategyName.INCREASE for item in traces)
    assert session.learner_state.mastery_estimate <= 0.5


def test_unexpected_correct_after_failures_is_not_increase():
    _, _, traces = run_kinds(
        ("wrong_weak", "wrong_weak", "wrong_weak", "strong_correct"),
        session_id="FAIL-U",
    )
    assert traces[-1].decision != StrategyName.INCREASE


def test_empty_answer_fails_safe():
    _, _, traces = run_kinds(("empty",), session_id="FAIL-E")
    assert traces[0].decision in {
        StrategyName.ASSESS,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.PROBE,
        StrategyName.MAINTAIN,
    }


def test_empty_bank_does_not_crash_on_start():
    tutor = AdaptiveTutor(bank=())
    session = tutor.start_session(learner_id="Z", session_id="FAIL-BANK")
    assert session.current_challenge.challenge_id == "UNAVAILABLE"


def test_duplicate_challenge_history_still_selects():
    _, session, traces = run_kinds(("strong_correct",) * 8, session_id="FAIL-DUP")
    assert all(item.next_challenge_id for item in traces)
    assert session.current_challenge.challenge_id
