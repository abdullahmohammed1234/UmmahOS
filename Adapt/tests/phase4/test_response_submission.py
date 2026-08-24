"""Response submission through the product boundary."""

from __future__ import annotations

import pytest

from adapt.product.errors import InvalidResponseError, SessionCompleteError
from tests.phase4.helpers import make_service, scripted_submit


def test_answer_is_required():
    service = make_service()
    view = service.create_session(topic_id="algebra", session_id="SUB-001")
    with pytest.raises(InvalidResponseError):
        service.submit_response(view["session_id"], answer="  ", confidence=3, reasoning="x")


def test_confidence_is_required_and_mapped():
    service = make_service()
    view = service.create_session(
        topic_id="algebra", session_id="SUB-002", initial_challenge="ALG-M-001", max_steps=2
    )
    with pytest.raises(InvalidResponseError):
        service.submit_response(view["session_id"], answer="4", confidence=None)
    result = service.submit_response(
        view["session_id"],
        answer="4",
        confidence=5,
        reasoning="subtract both sides then divide",
    )
    engine = service.tutor.get_trace(view["session_id"])[-1]
    assert engine.response.learner_confidence.value == "HIGH"
    assert result["result"]["feedback"]["answer_status"] == engine.evidence.answer_status.value


def test_reasoning_is_optional():
    service = make_service()
    view = service.create_session(
        topic_id="algebra", session_id="SUB-003", initial_challenge="ALG-M-001", max_steps=2
    )
    result = service.submit_response(view["session_id"], answer="4", confidence=3, reasoning=None)
    assert result["research"]["response"]["reasoning"] in {None, ""}


def test_duplicate_submission_is_rejected():
    service = make_service()
    view = service.create_session(
        topic_id="algebra", session_id="SUB-004", initial_challenge="ALG-M-001", max_steps=3
    )
    first = service.submit_response(
        view["session_id"],
        answer="4",
        confidence=5,
        reasoning="subtract 3 from both sides then divide by 2",
        challenge_id=view["challenge"]["challenge_id"],
    )
    with pytest.raises(InvalidResponseError, match="does not match"):
        service.submit_response(
            view["session_id"],
            answer="4",
            confidence=5,
            reasoning="subtract 3 from both sides then divide by 2",
            challenge_id=view["challenge"]["challenge_id"],
        )
    current = service.tutor.get_session(view["session_id"])
    service._meta[view["session_id"]].last_submission_key = (
        f"{current.step_number}:{current.current_challenge.challenge_id}"
    )
    with pytest.raises(InvalidResponseError, match="already submitted"):
        service.submit_response(
            view["session_id"],
            answer="4",
            confidence=5,
            challenge_id=current.current_challenge.challenge_id,
        )
    service._meta[view["session_id"]].last_submission_key = "consumed"
    second = scripted_submit(service, view["session_id"], "strong_correct")
    assert first["result"]["step_number"] == 1
    assert second["result"]["step_number"] == 2


def test_session_stops_at_max_steps():
    service = make_service()
    view = service.create_session(
        topic_id="algebra", session_id="SUB-005", initial_challenge="ALG-M-001", max_steps=2
    )
    scripted_submit(service, view["session_id"], "strong_correct")
    scripted_submit(service, view["session_id"], "strong_correct")
    with pytest.raises(SessionCompleteError):
        service.submit_response(view["session_id"], answer="4", confidence=5, reasoning="done")
    done = service.get_session(view["session_id"])
    assert done["complete"] is True
    assert done["can_submit"] is False
