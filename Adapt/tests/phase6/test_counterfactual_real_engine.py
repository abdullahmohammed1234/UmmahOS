"""Counterfactual demonstration must execute AdaptiveTutor twice."""

from __future__ import annotations

from tests.phase4.helpers import LiveApp, make_service


def test_counterfactual_runs_real_adaptive_tutor_twice():
    service = make_service()
    result = service.run_counterfactual()
    a_id = result["learner_a"]["session"]["session_id"]
    b_id = result["learner_b"]["session"]["session_id"]
    assert a_id != b_id
    a_engine = service.tutor.get_trace(a_id)
    b_engine = service.tutor.get_trace(b_id)
    assert a_engine
    assert b_engine
    assert result["learner_a"]["final_decision"] == a_engine[-1].decision.value
    assert result["learner_b"]["final_decision"] == b_engine[-1].decision.value
    assert result["learner_a"]["final_challenge"] == a_engine[-1].next_challenge_id
    assert result["learner_b"]["final_challenge"] == b_engine[-1].next_challenge_id
    assert result["learner_a"]["final_decision"] != result["learner_b"]["final_decision"]
    assert result["differentiated"] is True
    assert result["headline"] == "Same starting point. Different evidence. Different decision."
    assert result["label"] == "DEMO SCENARIO"


def test_counterfactual_displayed_labels_match_engine():
    service = make_service()
    result = service.run_counterfactual()
    a_engine = service.tutor.get_trace(result["learner_a"]["session"]["session_id"])[-1]
    b_engine = service.tutor.get_trace(result["learner_b"]["session"]["session_id"])[-1]
    assert result["learner_a"]["explanation"]["decision"] == a_engine.decision.value
    assert result["learner_b"]["explanation"]["decision"] == b_engine.decision.value
    assert a_engine.decision.value == "INCREASE"
    assert "INCREASE" in result["learner_a"]["final_decision_label"]


def test_http_counterfactual_is_live_engine():
    app = LiveApp()
    try:
        payload = app.request("POST", "/api/demo/counterfactual", {})
        live = app.service.run_counterfactual()
        assert payload["learner_a"]["final_decision"] == live["learner_a"]["final_decision"]
        assert payload["learner_b"]["final_decision"] == live["learner_b"]["final_decision"]
        a_engine = app.service.tutor.get_trace(payload["learner_a"]["session"]["session_id"])[-1]
        assert payload["learner_a"]["final_decision"] == a_engine.decision.value
    finally:
        app.close()
