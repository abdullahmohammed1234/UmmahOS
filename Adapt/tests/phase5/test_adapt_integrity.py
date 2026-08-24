"""ADAPT condition must use AdaptiveTutor through the Phase 4 product."""

from __future__ import annotations

from adapt.eval.experiment import run_adapt_training
from adapt.product.service import ProductService
from adapt.tutor.responses import build_scripted_response
from adapt.tutor.tutor import AdaptiveTutor
from tests.phase4.helpers import LiveApp, make_service, scripted_submit


def test_product_service_owns_adaptive_tutor():
    service = ProductService()
    assert isinstance(service.tutor, AdaptiveTutor)


def test_next_challenge_originates_from_adaptive_tutor():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        learner_id="p5-int",
        session_id="P5-INT-001",
        max_steps=2,
    )
    result = scripted_submit(service, view["session_id"], "strong_correct")
    engine_step = service.tutor.get_trace(view["session_id"])[0]
    assert result["research"]["strategy"]["decision"] == engine_step.decision.value
    assert result["research"]["next_challenge"]["challenge_id"] == engine_step.next_challenge_id
    assert result["result"]["adaptation"]["decision"] == engine_step.decision.value


def test_http_flow_uses_the_same_engine():
    app = LiveApp()
    try:
        created = app.request(
            "POST",
            "/api/sessions",
            {
                "topic_id": "fractions",
                "learner_id": "p5-http",
                "session_id": "P5-INT-HTTP",
                "max_steps": 1,
            },
        )
        submitted = app.request(
            "POST",
            f"/api/sessions/{created['session_id']}/responses",
            {"answer": "5/6", "confidence": 4, "reasoning": "common denominator sixths"},
        )
        engine = app.service.tutor.get_trace(created["session_id"])[0]
        assert isinstance(app.service.tutor, AdaptiveTutor)
        assert submitted["research"]["next_challenge"]["challenge_id"] == engine.next_challenge_id
        assert submitted["research"]["evidence"]["answer_status"]
        assert submitted["research"]["state"]["mastery"] is not None
        assert submitted["research"]["strategy"]["decision"]
    finally:
        app.close()


def test_experiment_adapt_training_records_engine_name():
    service = ProductService(seed=20260814)
    session = service.create_session(
        topic_id="algebra",
        learner_id="prep",
        session_id="P5-PREP",
        max_steps=1,
        initial_challenge="ALG-D-001",
    )
    challenge = service.tutor.get_session(session["session_id"]).current_challenge
    scripted = build_scripted_response(
        challenge, "strong_correct", learner_id="prep", response_id="prep-1"
    )
    responses = [
        {"answer": scripted.answer, "confidence": 5, "reasoning": scripted.reasoning}
    ] * 8
    payload = run_adapt_training(
        responses,
        participant_id="P5-ADAPT-INT",
        service=ProductService(seed=20260814),
    )
    assert payload["engine"] == "AdaptiveTutor"
    assert payload["product"] == "ProductService"
    assert payload["training"]
    assert payload["training"][0]["strategy"]
    assert payload["training"][0]["next_challenge_id"]
    assert payload["training"][0]["engine"] == "AdaptiveTutor"
