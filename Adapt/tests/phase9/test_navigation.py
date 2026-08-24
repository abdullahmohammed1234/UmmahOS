"""M9-001 — Learner navigation through Community Safety content."""

from pathlib import Path

from tests.phase4.helpers import LiveApp, make_service

STATIC = Path(__file__).resolve().parents[2] / "src" / "app" / "static"


def test_m9_001_navigation_flow():
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    for token in (
        "Learn differently with ADAPT.",
        "Start Learning",
        "What do you want to explore?",
        "Check Answer",
        "What ADAPT noticed",
        "Why this question?",
        "YOUR NEXT STEP",
    ):
        assert token in app_js
    service = make_service()
    subjects = service.list_subjects()
    assert len(subjects) == 1
    safety = service.get_subject("community-safety")
    concept = next(item for item in safety["concepts"] if item["concept_id"] == "csafety_context_preservation")
    view = service.create_session(
        concept_id=concept["concept_id"],
        subject_id="community-safety",
        session_id="P9-NAV-001",
        max_steps=3,
    )
    assert view["challenge"]["prompt"]
    first = view["challenge"]["challenge_id"]
    result = service.submit_response(
        view["session_id"],
        answer=view["challenge"]["choices"][0] if view["challenge"].get("choices") else "Preserve the surrounding conversation context before deciding how to respond or report",
        confidence=3,
        approach="worked",
        challenge_id=first,
    )
    assert result["result"]["noticed"]
    assert result["result"]["why_this_question"]["from_trace"] is True
    nxt = result["result"]["next_challenge"]["challenge_id"]
    assert nxt
    assert result["status"] in {"showing_feedback", "complete"}


def test_m9_001_http_routes():
    app = LiveApp()
    try:
        content = app.request("GET", "/api/content")
        assert content["hero"] == "Learn differently with ADAPT."
        subjects = app.request("GET", "/api/subjects")
        assert len(subjects["subjects"]) == 1
        subject = app.request("GET", "/api/subjects/community-safety")
        assert subject["concepts"]
        created = app.request(
            "POST",
            "/api/sessions",
            {"concept_id": "csafety_context_preservation", "subject_id": "community-safety", "max_steps": 2},
        )
        assert created["challenge"]
    finally:
        app.close()
