"""Research mode exposes the actual AdaptiveTutor chain."""

from tests.phase4.helpers import make_service, scripted_submit


def test_research_trace_visibility():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P8-RS-001",
        initial_challenge="ALG-M-001",
        max_steps=2,
        mode="research",
    )
    result = scripted_submit(service, view["session_id"], "strong_correct")
    research = result["research"]
    assert research["complete"] is True
    assert research["evidence"]["answer_status"]
    assert "mastery" in research["state"]
    assert research["strategy"]["decision"]
    assert research["next_challenge"]["challenge_id"]
    trace = service.get_trace(view["session_id"])
    assert trace["trace_complete"] is True
    assert trace["research_state"]["strategy"] == research["strategy"]["after"]
    engine = service.tutor.get_trace(view["session_id"])[-1]
    assert research["strategy"]["decision"] == engine.decision.value
    assert research["human_explanation"]["decision"] == engine.decision.value
