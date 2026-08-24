"""Session summary and restoration from actual session data."""

from __future__ import annotations

from tests.phase4.helpers import make_service, scripted_submit


def test_summary_derives_from_traces():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="SUM-001",
        initial_challenge="ALG-D-001",
        max_steps=4,
    )
    for kind in ("strong_correct", "strong_correct", "strong_correct", "weak_correct"):
        scripted_submit(service, view["session_id"], kind)
    summary = service.get_summary(view["session_id"])
    traces = service.tutor.get_trace(view["session_id"])
    assert summary["challenges_completed"] == len(traces)
    assert summary["adapt_adjusted_path"] == sum(
        1 for item in traces if item.strategy_before.current_strategy != item.strategy_after.current_strategy
    )
    assert summary["strategies_used"] == len({item.decision.value for item in traces})
    assert summary["strongest_area"]
    story = service.get_story(view["session_id"])
    assert story["beats"][0]["text"] == "You started"
    assert len(story["beats"]) >= 2


def test_snapshot_restore_preserves_trajectory():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="SUM-002",
        initial_challenge="ALG-M-001",
        max_steps=5,
    )
    scripted_submit(service, view["session_id"], "strong_correct")
    scripted_submit(service, view["session_id"], "weak_correct")
    snap = service.snapshot(view["session_id"])
    before = [item.decision.value for item in service.tutor.get_trace(view["session_id"])]
    restored_service = make_service()
    restored_service.restore(snap)
    after = [item.decision.value for item in restored_service.tutor.get_trace(view["session_id"])]
    assert after == before
    scripted_submit(restored_service, view["session_id"], "strong_correct")
    scripted_submit(service, view["session_id"], "strong_correct")
    assert [item.decision.value for item in restored_service.tutor.get_trace(view["session_id"])] == [
        item.decision.value for item in service.tutor.get_trace(view["session_id"])
    ]
    assert restored_service.get_session(view["session_id"])["challenge"]["challenge_id"] == service.get_session(
        view["session_id"]
    )["challenge"]["challenge_id"]
