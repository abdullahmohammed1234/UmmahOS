"""Reset must create a clean product session."""

from __future__ import annotations

from tests.phase4.helpers import LiveApp, make_service, scripted_submit


def test_reset_creates_clean_session():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P6-RST-001",
        initial_challenge="ALG-M-001",
        max_steps=5,
    )
    scripted_submit(service, view["session_id"], "strong_correct")
    before = service.get_session(view["session_id"])
    assert before["progress"]["completed"] == 1
    reset = service.reset_session(view["session_id"])
    assert reset["session_id"] != view["session_id"]
    assert reset["progress"]["completed"] == 0
    assert reset["last_result"] is None
    assert reset["opening"]["strategy"] == "ASSESS"
    assert reset["opening"]["mastery"] == "uncertain"
    engine = service.tutor.get_session(reset["session_id"])
    assert engine.step_number == 0
    assert engine.traces == ()


def test_http_reset_returns_new_session():
    app = LiveApp()
    try:
        created = app.request("POST", "/api/sessions", {"topic_id": "fractions", "max_steps": 4})
        submitted = app.request(
            "POST",
            f"/api/sessions/{created['session_id']}/responses",
            {"answer": "1/2", "confidence": 3, "reasoning": "half"},
        )
        assert submitted["progress"]["completed"] == 1
        reset = app.request("POST", f"/api/sessions/{created['session_id']}/reset", {})
        assert reset["session_id"] != created["session_id"]
        assert reset["progress"]["completed"] == 0
        assert reset["topic"]["topic_id"] == "fractions"
    finally:
        app.close()
