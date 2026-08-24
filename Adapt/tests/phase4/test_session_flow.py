"""Start session → challenge → submit → result → next challenge."""

from __future__ import annotations

from tests.phase4.helpers import LiveApp, make_service, scripted_submit


def test_start_session_returns_challenge_without_expected_answer():
    service = make_service()
    view = service.create_session(topic_id="algebra", learner_id="flow", session_id="FLOW-001")
    assert view["status"] == "awaiting_answer"
    assert view["challenge"]["prompt"]
    assert "expected_answer" not in view["challenge"]
    assert view["can_submit"] is True
    assert view["progress"]["total"] == 10


def test_submit_returns_engine_result_and_next_challenge():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        learner_id="flow",
        session_id="FLOW-002",
        initial_challenge="ALG-M-001",
        max_steps=5,
    )
    first_id = view["challenge"]["challenge_id"]
    result = scripted_submit(service, view["session_id"], "strong_correct")
    assert result["result"]["feedback"]["headline"] in {"Correct", "Needs another look"}
    assert result["result"]["adaptation"]["decision"]
    assert result["research"]["strategy"]["decision"] == result["result"]["adaptation"]["decision"]
    next_challenge = result["session_id"] and result["challenge"]
    assert next_challenge["challenge_id"] != first_id or result["result"]["next_challenge"]["challenge_id"]


def test_multi_step_flow_never_invents_strategy_in_product_layer():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="FLOW-003",
        initial_challenge="ALG-M-001",
        max_steps=4,
    )
    kinds = ("strong_correct", "strong_correct", "weak_correct", "strong_correct")
    for kind in kinds:
        result = scripted_submit(service, view["session_id"], kind)
        engine = service.tutor.get_trace(view["session_id"])[-1]
        assert result["result"]["adaptation"]["decision"] == engine.decision.value
        assert result["research"]["next_challenge"]["challenge_id"] == engine.next_challenge_id


def test_http_session_flow_uses_product_boundary():
    app = LiveApp()
    try:
        created = app.request(
            "POST",
            "/api/sessions",
            {"topic_id": "algebra", "learner_id": "http-flow", "max_steps": 3, "initial_challenge": "ALG-M-001"},
        )
        session_id = created["session_id"]
        challenge_id = created["challenge"]["challenge_id"]
        submitted = app.request(
            "POST",
            f"/api/sessions/{session_id}/responses",
            {
                "answer": "4",
                "confidence": 5,
                "reasoning": "I subtracted 3 from both sides and then divided by 2 to isolate x.",
                "challenge_id": challenge_id,
            },
        )
        assert submitted["result"]["adaptation"]["decision"]
        fetched = app.request("GET", f"/api/sessions/{session_id}")
        assert fetched["progress"]["completed"] == 1
        trace = app.request("GET", f"/api/sessions/{session_id}/trace")
        assert trace["chain"][0]["strategy"]["decision"] == submitted["result"]["adaptation"]["decision"]
    finally:
        app.close()
