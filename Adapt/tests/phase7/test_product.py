from pathlib import Path

from adapt.product.errors import InvalidResponseError
from tests.phase4.helpers import LiveApp, make_service, scripted_submit

STATIC = Path(__file__).resolve().parents[2] / "src" / "app" / "static"


def test_subject_and_topic_selection():
    service = make_service()
    subjects = service.list_subjects()
    assert len(subjects) == 1
    safety = service.get_subject("community-safety")
    topic_ids = {item["topic_id"] for item in safety["topics"]}
    assert "csafety-context" in topic_ids
    for topic in safety["topics"]:
        assert topic["mastery"] is None
        assert topic["status"] == "not_started"


def test_challenge_submission_and_confidence():
    service = make_service()
    view = service.create_session(
        topic_id="csafety-context",
        subject_id="community-safety",
        session_id="P7-SUB-001",
        max_steps=3,
    )
    assert view["challenge"]["prompt"]
    assert "expected_answer" not in view["challenge"]
    assert view["evidence_plan"]["ask_confidence"] is True
    answer = (
        view["challenge"].get("choices", ["Preserve the surrounding conversation context before deciding how to respond or report"])[0]
        if view["challenge"].get("choices")
        else "Preserve the surrounding conversation context before deciding how to respond or report"
    )
    result = service.submit_response(
        view["session_id"],
        answer=answer,
        confidence=5,
        approach="worked",
        explanation="Context can change how a message should be interpreted.",
        challenge_id=view["challenge"]["challenge_id"],
    )
    assert result["result"]["feedback"]
    assert result["result"]["noticed"]
    assert result["result"]["why_this_question"]["from_trace"] is True
    assert result["research"]["strategy"]["decision"] == result["result"]["adaptation"]["decision"]


def test_optional_explanation_and_feedback_render():
    service = make_service()
    view = service.create_session(topic_id="csafety-context", session_id="P7-SUB-002", max_steps=2)
    answer = (
        view["challenge"].get("choices", ["Preserve the surrounding conversation context before deciding how to respond or report"])[0]
        if view["challenge"].get("choices")
        else "Preserve the surrounding conversation context before deciding how to respond or report"
    )
    result = service.submit_response(
        view["session_id"],
        answer=answer,
        confidence=3,
        approach="unsure",
        explanation="",
        challenge_id=view["challenge"]["challenge_id"],
    )
    assert result["result"]["feedback"]["headline"]
    assert "Why this question?" in result["result"]["why_this_question"]["title"]


def test_progress_and_research_views():
    service = make_service()
    view = service.create_session(topic_id="csafety-context", session_id="P7-PR-001", max_steps=2)
    scripted_submit(service, view["session_id"], "strong_correct")
    progress = service.get_progress(view["session_id"])
    assert progress["title"] == "Your progress"
    insights = service.get_insights(view["session_id"])
    assert insights["from_evidence"] is True
    journey = service.get_journey(view["session_id"])
    assert journey["steps"]
    trace = service.get_trace(view["session_id"])
    assert trace["chain"][0]["complete"] is True
    assert trace["trace_complete"] is True


def test_counterfactual_still_differentiates():
    service = make_service()
    result = service.run_counterfactual()
    assert result["differentiated"] is True
    assert result["learner_a"]["final_decision"] != result["learner_b"]["final_decision"]


def test_http_subject_session_flow():
    app = LiveApp()
    try:
        subjects = app.request("GET", "/api/subjects")
        assert len(subjects["subjects"]) == 1
        created = app.request(
            "POST",
            "/api/sessions",
            {"topic_id": "csafety-context", "subject_id": "community-safety", "max_steps": 2},
        )
        answer = (
            created["challenge"].get("choices", ["Preserve the surrounding conversation context before deciding how to respond or report"])[0]
            if created["challenge"].get("choices")
            else "Preserve the surrounding conversation context before deciding how to respond or report"
        )
        submitted = app.request(
            "POST",
            f"/api/sessions/{created['session_id']}/responses",
            {
                "answer": answer,
                "confidence": 4,
                "approach": "worked",
                "explanation": "preserve surrounding messages before concluding",
                "challenge_id": created["challenge"]["challenge_id"],
            },
        )
        assert submitted["result"]["adaptation"]["decision"]
        progress = app.request("GET", f"/api/sessions/{created['session_id']}/progress")
        assert "subjects" in progress
    finally:
        app.close()


def test_legacy_topics_still_work():
    service = make_service()
    view = service.create_session(topic_id="algebra", session_id="P7-LEG-001", max_steps=2)
    assert view["runtime"] == "core"
    try:
        service.create_session(topic_id="not-a-real-topic")
        raise AssertionError("unknown topic must remain unsupported")
    except InvalidResponseError:
        pass


def test_ui_contains_learner_copy_and_accessibility():
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    css = (STATIC / "css" / "styles.css").read_text(encoding="utf-8")
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert "Start Learning" in app_js
    assert "Learn differently with ADAPT" in app_js
    assert "A tutor that adapts to how you learn" in html or "A tutor that adapts to how you learn" in app_js
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css
    assert "increaseDifficulty" not in app_js
    assert "if (correct)" not in app_js
