"""Session isolation tests."""

from __future__ import annotations

from adapt.tutor.responses import build_scripted_response
from tests.helpers_phase3 import make_tutor, run_kinds


def test_two_sessions_do_not_share_state():
    tutor = make_tutor()
    tutor.start_session(learner_id="A", session_id="ISO-A", initial_challenge="ALG-M-001")
    tutor.start_session(learner_id="B", session_id="ISO-B", initial_challenge="ALG-M-001")
    ch = tutor.get_next_challenge("ISO-A")
    tutor.submit_response(
        "ISO-A",
        build_scripted_response(ch, "strong_correct", learner_id="A", response_id="A1"),
    )
    assert tutor.get_state("ISO-B").mastery_estimate == 0.5
    assert tutor.get_strategy("ISO-B").current_strategy.value == "ASSESS"
    assert tutor.get_trace("ISO-B") == ()
    assert tutor.get_state("ISO-A").mastery_estimate != 0.5


def test_interleaved_matches_independent():
    kinds_a = ("strong_correct", "strong_correct", "strong_correct")
    kinds_b = ("wrong_weak", "misconception", "wrong_weak")

    independent_a = run_kinds(
        kinds_a, session_id="INT-A", learner_id="A", initial_challenge="ALG-M-002", tutor=make_tutor()
    )[1]
    independent_b = run_kinds(
        kinds_b, session_id="INT-B", learner_id="B", initial_challenge="ALG-M-002", tutor=make_tutor()
    )[1]

    tutor = make_tutor()
    tutor.start_session(learner_id="A", session_id="INT-A", initial_challenge="ALG-M-002")
    tutor.start_session(learner_id="B", session_id="INT-B", initial_challenge="ALG-M-002")
    for index in range(3):
        for sid, learner, kinds in (("INT-A", "A", kinds_a), ("INT-B", "B", kinds_b)):
            ch = tutor.get_next_challenge(sid)
            tutor.submit_response(
                sid,
                build_scripted_response(
                    ch, kinds[index], learner_id=learner, response_id=f"{sid}-R-{index + 1:03d}"
                ),
            )
    interleaved_a = tutor.get_session("INT-A")
    interleaved_b = tutor.get_session("INT-B")
    assert interleaved_a.learner_state == independent_a.learner_state
    assert interleaved_b.learner_state == independent_b.learner_state
    assert interleaved_a.strategy_state == independent_a.strategy_state
    assert interleaved_b.strategy_state == independent_b.strategy_state
    assert [t.next_challenge_id for t in interleaved_a.traces] == [
        t.next_challenge_id for t in independent_a.traces
    ]
    assert [t.next_challenge_id for t in interleaved_b.traces] == [
        t.next_challenge_id for t in independent_b.traces
    ]


def test_histories_are_not_shared_lists():
    tutor = make_tutor()
    tutor.start_session(learner_id="A", session_id="H-A", initial_challenge="ALG-M-001")
    tutor.start_session(learner_id="B", session_id="H-B", initial_challenge="ALG-M-001")
    ch = tutor.get_next_challenge("H-A")
    tutor.submit_response("H-A", build_scripted_response(ch, "strong_correct", learner_id="A", response_id="h1"))
    assert tutor.get_session("H-B").history == ()
    assert tutor.get_session("H-A").history is not tutor.get_session("H-B").history
