"""Journey views from session traces and catalog state."""

from tests.phase4.helpers import make_service, scripted_submit


def test_session_journey_has_meaningful_states():
    service = make_service()
    view = service.create_session(
        topic_id="csafety-context",
        session_id="P8-JY-001",
        max_steps=2,
    )
    scripted_submit(service, view["session_id"], "strong_correct")
    journey = service.get_journey(view["session_id"])
    assert journey["title"] == "Your Journey"
    assert journey["steps"]
    assert journey["steps"][0]["kind"] == "start"
    names = [step.get("name") for step in journey["steps"] if step.get("name")]
    assert names
    assert journey["catalog"]["steps"]
    statuses = {item["status_label"] for item in journey["catalog"]["steps"]}
    assert "New" in statuses or "In progress" in statuses or "Practicing" in statuses


def test_catalog_journey_without_session_is_honest():
    service = make_service()
    journey = service.get_journey(learner_id="fresh", subject_id="community-safety")
    assert journey["empty"] is True
    assert all(item["status"] == "new" or item["status_label"] in {"New", "Recommended"} for item in journey["steps"])
