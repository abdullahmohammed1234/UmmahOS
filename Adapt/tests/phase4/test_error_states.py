"""Product error states stay learner-safe."""

from __future__ import annotations

import pytest

from adapt.product.errors import (
    ChallengeUnavailableError,
    InvalidResponseError,
    SessionCompleteError,
    SessionUnavailableError,
)
from tests.phase4.helpers import LiveApp, make_service


def test_unknown_session():
    service = make_service()
    with pytest.raises(SessionUnavailableError):
        service.get_session("missing")


def test_unsupported_topic():
    service = make_service()
    with pytest.raises(InvalidResponseError):
        service.create_session(topic_id="calculus")


def test_invalid_confidence_and_empty_answer():
    service = make_service()
    view = service.create_session(topic_id="algebra", session_id="ERR-001", max_steps=2)
    with pytest.raises(InvalidResponseError):
        service.submit_response(view["session_id"], answer="4", confidence=9)
    with pytest.raises(InvalidResponseError):
        service.submit_response(view["session_id"], answer="", confidence=3)


def test_stale_challenge_id():
    service = make_service()
    view = service.create_session(
        topic_id="algebra", session_id="ERR-002", initial_challenge="ALG-M-001", max_steps=2
    )
    with pytest.raises(InvalidResponseError):
        service.submit_response(
            view["session_id"],
            answer="4",
            confidence=3,
            challenge_id="ALG-H-001",
        )


def test_http_maps_errors():
    app = LiveApp()
    try:
        try:
            app.request("GET", "/api/sessions/nope")
            raise AssertionError("expected failure")
        except RuntimeError as exc:
            assert exc.code == "session_unavailable"  # type: ignore[attr-defined]
            assert exc.status == 404  # type: ignore[attr-defined]
        try:
            app.request("POST", "/api/sessions", {"topic_id": "trigonometry"})
            raise AssertionError("expected failure")
        except RuntimeError as exc:
            assert exc.code == "invalid_response"  # type: ignore[attr-defined]
    finally:
        app.close()


def test_unknown_challenge_is_session_unavailable():
    service = make_service()
    with pytest.raises(SessionUnavailableError):
        service.create_session(
            topic_id="algebra",
            session_id="ERR-UNAVAIL",
            initial_challenge="NOT-A-CHALLENGE",
        )


def test_unavailable_challenge_view_is_flagged():
    from adapt.product.present import challenge_view
    from adapt.tutor.challenge_bank import UNAVAILABLE_CHALLENGE

    view = challenge_view(UNAVAILABLE_CHALLENGE, include_answer=False)
    assert view["unavailable"] is True
    assert ChallengeUnavailableError is not None


def test_session_complete_error_type():
    service = make_service()
    view = service.create_session(
        topic_id="algebra", session_id="ERR-003", initial_challenge="ALG-M-001", max_steps=1
    )
    service.submit_response(view["session_id"], answer="4", confidence=5, reasoning="subtract and divide")
    with pytest.raises(SessionCompleteError):
        service.submit_response(view["session_id"], answer="4", confidence=5)
