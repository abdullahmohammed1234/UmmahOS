"""M9-003 — Displayed explanations correspond to the actual trace."""

from tests.phase4.helpers import make_service, scripted_submit


def test_m9_003_explanation_consistency():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P9-EX-001",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    result = scripted_submit(service, view["session_id"], "weak_correct")
    engine = service.tutor.get_trace(view["session_id"])[-1]
    explanation = result["result"]["explanation"]
    noticed = result["result"]["noticed"]
    why = result["result"]["why_this_question"]
    assert explanation["from_trace"] is True
    assert noticed["from_trace"] is True
    assert why["from_trace"] is True
    assert explanation["decision"] == engine.decision.value
    assert noticed["strategy"] == engine.decision.value
    assert why["strategy"] == engine.decision.value
    if not engine.evidence.misconception_signal:
        assert explanation["misconception_mentioned"] is False
