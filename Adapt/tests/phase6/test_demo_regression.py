"""Phase 6 must not regress the guided demo or learner-safe errors."""

from __future__ import annotations

from adapt.product.errors import InvalidResponseError
from tests.phase4.helpers import LiveApp, make_service, scripted_submit


def test_guided_demo_still_reaches_increase_probe_remediate():
    service = make_service()
    view = service.start_demo()
    decisions = []
    while True:
        result = service.demo_step(view["session_id"])
        decisions.append(result["result"]["adaptation"]["decision"])
        engine = service.tutor.get_trace(view["session_id"])[-1]
        assert result["result"]["adaptation"]["decision"] == engine.decision.value
        if result.get("demo", {}).get("complete"):
            break
    assert "INCREASE" in decisions
    assert "PROBE" in decisions
    assert "REMEDIATE" in decisions


def test_empty_and_invalid_inputs_are_rejected():
    service = make_service()
    view = service.create_session(topic_id="algebra", session_id="P6-ERR-001", max_steps=2)
    try:
        service.submit_response(view["session_id"], answer="", confidence=3)
        raise AssertionError("empty answer should fail")
    except InvalidResponseError:
        pass
    try:
        service.submit_response(view["session_id"], answer="4", confidence=9)
        raise AssertionError("invalid confidence should fail")
    except InvalidResponseError:
        pass
    session = service.get_session(view["session_id"])
    assert session["progress"]["completed"] == 0


def test_long_answer_and_special_characters_do_not_crash():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P6-ERR-002",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    long_text = "x=4 " + ("αβγ <> & \" ' \n" * 50)
    result = service.submit_response(
        view["session_id"],
        answer=long_text[:200],
        confidence=2,
        reasoning=long_text,
    )
    assert result["result"]["adaptation"]["decision"]
    engine = service.tutor.get_trace(view["session_id"])[-1]
    assert result["result"]["adaptation"]["decision"] == engine.decision.value


def test_too_long_answer_is_learner_safe():
    service = make_service()
    view = service.create_session(topic_id="algebra", session_id="P6-ERR-003", max_steps=2)
    try:
        service.submit_response(view["session_id"], answer="4" * 20001, confidence=3)
        raise AssertionError("oversized answer should fail")
    except InvalidResponseError as exc:
        assert "too long" in str(exc).lower()


def test_repeated_submission_is_blocked():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P6-ERR-004",
        initial_challenge="ALG-M-001",
        max_steps=3,
    )
    scripted_submit(service, view["session_id"], "strong_correct")
    try:
        service.submit_response(
            view["session_id"],
            answer="4",
            confidence=5,
            challenge_id=view["challenge"]["challenge_id"],
        )
        raise AssertionError("repeat submit of the same challenge should fail")
    except InvalidResponseError:
        pass


def test_health_is_offline_first():
    app = LiveApp()
    try:
        health = app.request("GET", "/api/health")
        assert health["ok"] is True
        assert health["offline"] is True
        assert health["requires_api_key"] is False
        content = app.request("GET", "/api/content")
        assert content["phase5"]["n"] == 0
        assert content["phase5"]["status"] == "INCONCLUSIVE"
        assert "51/51" in " ".join(content["technical_evidence"]["phases"][0]["items"])
    finally:
        app.close()
