"""Live counterfactual still uses two AdaptiveTutor runs."""

from tests.phase4.helpers import make_service


def test_counterfactual_uses_real_engine_and_differentiates():
    service = make_service()
    result = service.run_counterfactual()
    assert result["live_engine"] is True
    assert result["differentiated"] is True
    assert result["learner_a"]["final_decision"] != result["learner_b"]["final_decision"]
    a_id = result["learner_a"]["session"]["session_id"]
    b_id = result["learner_b"]["session"]["session_id"]
    a_engine = service.tutor.get_trace(a_id)[-1]
    b_engine = service.tutor.get_trace(b_id)[-1]
    assert result["learner_a"]["final_decision"] == a_engine.decision.value
    assert result["learner_b"]["final_decision"] == b_engine.decision.value
    assert result["chain"] == [
        "Same start",
        "Different evidence",
        "Different state",
        "Different strategy",
        "Different challenge",
    ]
    assert result["learner_a"]["final_decision_plain"]
    assert result["learner_b"]["final_decision_plain"]
