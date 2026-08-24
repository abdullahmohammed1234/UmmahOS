"""Session snapshot and restore tests."""

from __future__ import annotations

from tests.helpers_phase3 import make_tutor, run_kinds


def test_snapshot_contains_required_fields():
    tutor, session, _ = run_kinds(("strong_correct",) * 2, session_id="SNAP-1")
    snap = tutor.snapshot("SNAP-1")
    inner = snap["session"]
    assert inner["learner_state"]["mastery_estimate"] == session.learner_state.mastery_estimate
    assert inner["strategy_state"]["current_strategy"] == session.strategy_state.current_strategy.value
    assert inner["step_number"] == 2
    assert inner["traces"]
    assert inner["current_challenge"]["challenge_id"] == session.current_challenge.challenge_id


def test_restore_preserves_state_strategy_history_trace():
    tutor, session, _ = run_kinds(("strong_correct", "weak_correct"), session_id="SNAP-2")
    snap = tutor.snapshot("SNAP-2")
    other = make_tutor()
    restored = other.restore(snap)
    assert restored.learner_state == session.learner_state
    assert restored.strategy_state == session.strategy_state
    assert restored.step_number == session.step_number
    assert len(restored.traces) == len(session.traces)
    assert restored.current_challenge.challenge_id == session.current_challenge.challenge_id
    assert [item.response_id for item in restored.history] == [item.response_id for item in session.history]


def test_resume_matches_continuous_run():
    kinds = ("strong_correct",) * 10
    _, continuous, _ = run_kinds(kinds, session_id="RESUME", learner_id="RC")
    tutor = make_tutor()
    run_kinds(kinds[:5], session_id="RESUME", learner_id="RC", tutor=tutor)
    snap = tutor.snapshot("RESUME")
    resumed_tutor = make_tutor()
    resumed_tutor.restore(snap)
    from adapt.tutor.responses import build_scripted_response

    for index, kind in enumerate(kinds[5:], start=6):
        challenge = resumed_tutor.get_next_challenge("RESUME")
        response = build_scripted_response(
            challenge, kind, learner_id="RC", response_id=f"RESUME-R-{index:03d}"
        )
        resumed_tutor.submit_response("RESUME", response)
    resumed = resumed_tutor.get_session("RESUME")
    assert resumed.learner_state == continuous.learner_state
    assert resumed.strategy_state == continuous.strategy_state
    assert [item.next_challenge_id for item in resumed.traces] == [
        item.next_challenge_id for item in continuous.traces
    ]
    assert resumed.current_challenge.challenge_id == continuous.current_challenge.challenge_id


def test_restore_invalid_snapshot_raises():
    from adapt.errors import InvalidSessionError
    import pytest

    tutor = make_tutor()
    with pytest.raises(InvalidSessionError):
        tutor.restore({})


def test_session_to_dict_round_trip():
    _, session, _ = run_kinds(("moderate_correct",) * 3, session_id="SNAP-3")
    from adapt.tutor.session import TutorSession

    restored = TutorSession.from_dict(session.to_dict())
    assert restored.step_number == session.step_number
    assert restored.strategy_state.current_strategy == session.strategy_state.current_strategy
    assert restored.current_challenge.challenge_id == session.current_challenge.challenge_id
