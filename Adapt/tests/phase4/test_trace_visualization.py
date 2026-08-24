"""Research trace must show evidence → state → strategy → challenge."""

from __future__ import annotations

from tests.phase4.helpers import make_service, scripted_submit


def test_every_step_has_complete_causal_chain():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="TRACE-001",
        initial_challenge="ALG-M-001",
        max_steps=4,
    )
    for kind in ("strong_correct", "strong_correct", "weak_correct"):
        scripted_submit(service, view["session_id"], kind)
    trace = service.get_trace(view["session_id"])
    assert trace["total_links"] == 3
    assert trace["complete_links"] == 3
    for link in trace["chain"]:
        assert link["complete"] is True
        assert link["evidence"]["answer_status"]
        assert link["state"]["mastery"] is not None
        assert link["strategy"]["decision"]
        assert link["next_challenge"]["challenge_id"]
        assert link["strategy"]["reason"]
    assert [item["strategy"] for item in trace["timeline"] if item["step"] > 0] == [
        item["strategy"]["decision"] for item in trace["chain"]
    ]


def test_research_state_exposes_numeric_mastery_for_judges():
    service = make_service()
    view = service.create_session(
        topic_id="algebra", session_id="TRACE-002", initial_challenge="ALG-M-001", max_steps=2
    )
    scripted_submit(service, view["session_id"], "strong_correct")
    trace = service.get_trace(view["session_id"])
    state = trace["research_state"]
    assert 0 <= state["mastery"] <= 1
    assert 0 <= state["confidence"] <= 1
    assert state["strategy"]
    assert trace["chain"][0]["state"]["mastery_arrow"] in {"↑", "↓", "→"}
