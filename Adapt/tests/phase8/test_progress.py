"""Honest progress from recorded learner state."""

from tests.phase4.helpers import make_service, scripted_submit


def test_progress_is_empty_until_recorded():
    service = make_service()
    progress = service.get_progress(learner_id="nobody-yet")
    assert progress["overall_available"] is False
    assert progress["overall_percent"] is None
    assert progress["persistence"] == "in_memory_while_running"
    assert "not a long-term saved learning record" in progress["disclaimer"].lower()
    for subject in progress["subjects"]:
        assert subject["mastery_percent"] is None
        assert subject["status_label"] == "New"


def test_progress_matches_recorded_mastery():
    service = make_service()
    view = service.create_session(
        topic_id="csafety-context",
        session_id="P8-PR-001",
        learner_id="p8-progress",
        max_steps=2,
    )
    scripted_submit(service, view["session_id"], "strong_correct")
    session = service.engine_session(view["session_id"])
    progress = service.get_progress(view["session_id"])
    assert progress["overall_available"] is True
    assert progress["concepts_practiced"] >= 1
    recorded = session.learner_state.mastery_estimate
    matching = [
        item
        for item in progress["subjects"]
        if item["subject_id"] == "community-safety"
    ]
    assert matching
    assert matching[0]["mastery_percent"] == int(round(recorded * 100))
    other = service.get_subject("community-safety", learner_id="p8-progress")
    explored = [item for item in other["concepts"] if item["concept_id"] == "csafety_context_preservation"]
    assert explored
