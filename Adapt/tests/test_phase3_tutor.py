"""Phase 3 AdaptiveTutor contract tests."""

from __future__ import annotations

import pytest

from adapt.errors import InvalidSessionError, SessionNotFoundError
from adapt.models.enums import StrategyName, Uncertainty
from adapt.models.strategy import initial_strategy_state
from adapt.tutor.tutor import AdaptiveTutor
from tests.helpers_phase3 import make_tutor, run_kinds


def test_start_session_begins_with_insufficient_knowledge():
    tutor = make_tutor()
    session = tutor.start_session(learner_id="L-1", session_id="S1")
    assert session.step_number == 0
    assert session.learner_state.mastery_estimate == 0.5
    assert session.learner_state.confidence == 0.2
    assert session.learner_state.uncertainty == Uncertainty.INSUFFICIENT_EVIDENCE
    assert session.strategy_state.current_strategy == StrategyName.ASSESS


def test_start_session_records_explicit_session_fields():
    tutor = make_tutor()
    session = tutor.start_session(learner_id="L-1", session_id="S1", concept_id="basic_algebra")
    assert session.session_id == "S1"
    assert session.learner_id == "L-1"
    assert session.current_challenge is not None
    assert session.history == ()
    assert session.traces == ()
    assert session.seed == 20260814


def test_submit_response_is_atomic_step():
    tutor, session, traces = run_kinds(("strong_correct",), session_id="ATOM")
    assert session.step_number == 1
    assert len(traces) == 1
    assert len(session.traces) == 1
    assert traces[0].step_number == 1


def test_getters_match_session():
    tutor, session, _ = run_kinds(("weak_correct",), session_id="GET")
    assert tutor.get_state("GET") == session.learner_state
    assert tutor.get_strategy("GET") == session.strategy_state
    assert tutor.get_next_challenge("GET") == session.current_challenge
    assert tutor.get_trace("GET") == session.traces


def test_get_unknown_session_raises():
    tutor = make_tutor()
    with pytest.raises(SessionNotFoundError):
        tutor.get_state("missing")


def test_duplicate_session_id_rejected():
    tutor = make_tutor()
    tutor.start_session(learner_id="A", session_id="DUP")
    with pytest.raises(InvalidSessionError):
        tutor.start_session(learner_id="B", session_id="DUP")


def test_start_session_requires_learner_id():
    tutor = make_tutor()
    with pytest.raises(InvalidSessionError):
        tutor.start_session(learner_id="", session_id="X")


def test_generated_session_id_is_deterministic_for_counter():
    tutor = make_tutor()
    a = tutor.start_session(learner_id="A")
    b = tutor.start_session(learner_id="B")
    assert a.session_id != b.session_id
    assert a.session_id.startswith("SES-20260814-")


def test_dict_response_is_accepted():
    tutor = make_tutor()
    tutor.start_session(learner_id="L", session_id="DICT", initial_challenge="ALG-M-001")
    step = tutor.submit_response(
        "DICT",
        {"answer": "4", "reasoning": "subtract 3 from both sides then divide", "learner_confidence": "HIGH"},
    )
    assert step.evidence.answer_status.value == "CORRECT"


def test_get_state_does_not_mutate_without_event():
    tutor = make_tutor()
    session = tutor.start_session(learner_id="L", session_id="MUTE")
    first = tutor.get_state("MUTE")
    second = tutor.get_state("MUTE")
    third = tutor.get_next_challenge("MUTE")
    assert first == second
    assert tutor.get_session("MUTE").step_number == 0
    assert third.challenge_id == session.current_challenge.challenge_id


def test_initial_strategy_is_assess_not_increase():
    tutor = make_tutor()
    session = tutor.start_session(learner_id="L", session_id="INIT")
    assert session.strategy_state.current_strategy != StrategyName.INCREASE
    assert session.strategy_state == initial_strategy_state() or session.strategy_state.current_strategy == StrategyName.ASSESS


def test_unknown_challenge_id_is_rejected():
    tutor = make_tutor()
    with pytest.raises(InvalidSessionError):
        tutor.start_session(learner_id="L", session_id="BAD", initial_challenge="NO-SUCH")


def test_empty_bank_fails_safe():
    tutor = AdaptiveTutor(bank=())
    session = tutor.start_session(learner_id="L", session_id="EMPTY", concept_id="basic_algebra")
    assert session.current_challenge.challenge_id == "UNAVAILABLE"


def test_unknown_concept_still_starts():
    tutor = make_tutor()
    session = tutor.start_session(learner_id="L", session_id="UC", concept_id="unknown_xyz")
    assert session.current_challenge is not None


def test_explain_before_any_step():
    tutor = make_tutor()
    tutor.start_session(learner_id="L", session_id="EX")
    text = tutor.explain("EX")
    assert "ASSESS" in text
    assert "insufficient" in text.lower() or "evidence" in text.lower()
