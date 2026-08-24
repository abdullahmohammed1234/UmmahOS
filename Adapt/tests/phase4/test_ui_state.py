"""Learner-facing view state. The UI must not receive enough to invent adaptation."""

from __future__ import annotations

from pathlib import Path

from tests.phase4.helpers import make_service, scripted_submit

STATIC = Path(__file__).resolve().parents[2] / "src" / "app" / "static"


def test_learner_challenge_hides_expected_answer_and_internal_scores():
    service = make_service()
    view = service.create_session(topic_id="fractions", session_id="UI-001")
    assert "expected_answer" not in view["challenge"]
    assert "mastery_estimate" not in view
    assert view["understanding"]["bar"]
    assert view["confidence_scale"][0]["value"] == 1
    assert view["confidence_scale"][-1]["value"] == 5


def test_feedback_uses_evidence_not_ui_correctness_rule():
    service = make_service()
    view = service.create_session(
        topic_id="algebra", session_id="UI-002", initial_challenge="ALG-M-001", max_steps=2
    )
    result = scripted_submit(service, view["session_id"], "weak_correct")
    feedback = result["result"]["feedback"]
    engine = service.tutor.get_trace(view["session_id"])[-1]
    assert feedback["answer_status"] == engine.evidence.answer_status.value
    assert feedback["reasoning_quality"] == engine.evidence.reasoning_quality.value
    if engine.evidence.reasoning_quality.value == "WEAK":
        assert "check this concept" in feedback["detail"].lower() or "reasoning" in feedback["detail"].lower()


def test_frontend_does_not_contain_independent_adaptation_logic():
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    api_js = (STATIC / "js" / "services" / "api.js").read_text(encoding="utf-8")
    blob = app_js + api_js
    assert "increaseDifficulty" not in blob
    assert "if (correct)" not in blob
    assert "INCREASE_DIFFICULTY" not in app_js


def test_landing_copy_is_present():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    css = (STATIC / "css" / "styles.css").read_text(encoding="utf-8")
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    assert "A tutor that adapts to how you learn" in html or "A tutor that adapts to how you learn" in app_js
    assert "Start Learning" in app_js
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css
