"""Phase 8 product navigation contracts."""

from pathlib import Path

from tests.phase4.helpers import LiveApp, make_service

STATIC = Path(__file__).resolve().parents[2] / "src" / "app" / "static"


def test_primary_nav_is_learner_facing():
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    assert "Learn" in app_js
    assert "Progress" in app_js
    assert "Journey" in app_js
    assert "How ADAPT Works" in app_js
    assert "Research mode" in app_js
    assert "Learn differently with ADAPT." in app_js
    assert "An adaptive tutor that changes what you learn next based on how you learn." in app_js
    assert "Start Learning" in app_js
    assert "See How ADAPT Works" in app_js


def test_subjects_and_concepts_are_reachable():
    service = make_service()
    subjects = service.list_subjects()
    names = {item["name"] for item in subjects}
    assert names == {"Community Safety"}
    safety = service.get_subject("community-safety")
    assert safety["concept_count"] >= 10
    assert safety["concepts"]
    assert all("status_label" in item for item in safety["concepts"])
    assert all(item["status_label"] == "New" for item in safety["concepts"])
    assert any(item["recommended"] for item in safety["concepts"])


def test_http_navigation_endpoints():
    app = LiveApp()
    try:
        health = app.request("GET", "/api/health")
        assert health["ok"] is True
        content = app.request("GET", "/api/content")
        assert content["hero"] == "Learn differently with ADAPT."
        subjects = app.request("GET", "/api/subjects")
        assert len(subjects["subjects"]) == 1
        safety = app.request("GET", "/api/subjects/community-safety")
        assert safety["concepts"]
        progress = app.request("GET", "/api/progress")
        assert progress["overall_available"] is False
        journey = app.request("GET", "/api/journey?subject_id=community-safety")
        assert journey["steps"]
    finally:
        app.close()
