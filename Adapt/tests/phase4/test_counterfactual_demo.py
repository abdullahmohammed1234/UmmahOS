"""Critical Phase 4 test: same challenge, different evidence, application boundary."""

from __future__ import annotations

from tests.phase4.helpers import LiveApp, make_service, run_kinds_through_product, run_kinds_through_tutor


def test_product_counterfactual_preserves_engine_distinction():
    service = make_service()
    result = service.run_counterfactual()
    assert result["challenge"]["challenge_id"] == "ALG-M-001"
    assert result["challenge"]["prompt"]
    assert result["differentiated"] is True
    assert result["learner_a"]["final_decision"] != result["learner_b"]["final_decision"]
    a_engine = service.tutor.get_trace(result["learner_a"]["session"]["session_id"])[-1]
    b_engine = service.tutor.get_trace(result["learner_b"]["session"]["session_id"])[-1]
    assert result["learner_a"]["final_decision"] == a_engine.decision.value
    assert result["learner_b"]["final_decision"] == b_engine.decision.value
    assert result["learner_a"]["final_challenge"] == a_engine.next_challenge_id
    assert result["learner_b"]["final_challenge"] == b_engine.next_challenge_id
    assert result["learner_a"]["final_decision"] == "INCREASE"
    assert result["learner_b"]["final_decision"] in {"PROBE", "GATHER_EVIDENCE", "ASSESS", "MAINTAIN"}


def test_application_boundary_matches_phase3_tutor_for_counterfactual():
    kinds_a = ("strong_correct",) * 3
    kinds_b = ("weak_correct",) * 3
    _, product_a, results_a = run_kinds_through_product(kinds_a, session_id="P4-CF-A")
    _, product_b, results_b = run_kinds_through_product(kinds_b, session_id="P4-CF-B", learner_id="L-B")
    _, tutor_a, traces_a = run_kinds_through_tutor(kinds_a, session_id="P3-CF-A")
    _, tutor_b, traces_b = run_kinds_through_tutor(kinds_b, session_id="P3-CF-B", learner_id="L-B")
    assert [item["result"]["adaptation"]["decision"] for item in results_a] == [
        item.decision.value for item in traces_a
    ]
    assert [item["result"]["adaptation"]["decision"] for item in results_b] == [
        item.decision.value for item in traces_b
    ]
    assert results_a[-1]["research"]["next_challenge"]["challenge_id"] == traces_a[-1].next_challenge_id
    assert results_b[-1]["research"]["next_challenge"]["challenge_id"] == traces_b[-1].next_challenge_id
    assert product_a["status"]
    assert tutor_a.current_challenge.challenge_id != tutor_b.current_challenge.challenge_id or (
        traces_a[-1].decision != traces_b[-1].decision
    )


def test_http_counterfactual_is_not_hardcoded():
    app = LiveApp()
    try:
        payload = app.request("POST", "/api/demo/counterfactual", {})
        assert payload["differentiated"] is True
        assert payload["learner_a"]["final_decision"] != payload["learner_b"]["final_decision"]
        # The HTTP payload must reflect the live engine, not a canned string table.
        live = app.service.run_counterfactual()
        assert payload["learner_a"]["final_decision"] == live["learner_a"]["final_decision"]
        assert payload["learner_b"]["final_decision"] == live["learner_b"]["final_decision"]
        assert payload["learner_a"]["final_challenge"] == live["learner_a"]["final_challenge"]
        assert payload["learner_b"]["final_challenge"] == live["learner_b"]["final_challenge"]
    finally:
        app.close()
