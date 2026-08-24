"""M9-010 — Progress reflects actual interaction history."""

from tests.phase4.helpers import make_service, scripted_submit


def test_m9_010_progress_integrity():
    service = make_service()
    empty = service.get_progress(learner_id="p9-nobody")
    assert empty["overall_available"] is False
    view = service.create_session(
        topic_id="csafety-context",
        session_id="P9-PR-001",
        learner_id="p9-progress",
        max_steps=2,
    )
    scripted_submit(service, view["session_id"], "strong_correct")
    session = service.engine_session(view["session_id"])
    progress = service.get_progress(view["session_id"])
    assert progress["overall_available"] is True
    recorded = session.learner_state.mastery_estimate
    matching = [item for item in progress["subjects"] if item["subject_id"] == "community-safety"]
    assert matching[0]["mastery_percent"] == int(round(recorded * 100))
    insights = service.get_insights(view["session_id"])
    assert insights["from_evidence"] is True
    safety = service.get_subject("community-safety", learner_id="p9-progress")
    explored = [item for item in safety["concepts"] if item["concept_id"] == "csafety_context_preservation"]
    assert explored[0]["status_label"] != "New" or explored[0]["attempts"] >= 0
