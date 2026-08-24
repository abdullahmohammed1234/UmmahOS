"""Explanations must come from actual traces."""

from adapt.product.explanations import learner_explanation
from tests.phase4.helpers import make_service, scripted_submit


def test_explanation_model_and_coverage():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P8-EX-001",
        initial_challenge="ALG-M-001",
        max_steps=3,
    )
    result = scripted_submit(service, view["session_id"], "strong_correct")
    explanation = result["result"]["explanation"]
    assert explanation["headline"]
    assert explanation["short_message"]
    assert explanation["detailed_message"]
    assert explanation["why_next"]
    assert explanation["from_trace"] is True
    engine = service.tutor.get_trace(view["session_id"])[-1]
    assert explanation["decision"] == engine.decision.value
    assert explanation["answer_status"] == engine.evidence.answer_status.value


def test_trace_explanation_consistency():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P8-EX-002",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    result = scripted_submit(service, view["session_id"], "weak_correct")
    engine = service.tutor.get_trace(view["session_id"])[-1]
    local = learner_explanation(engine)
    shown = result["result"]["explanation"]
    assert shown["decision"] == engine.decision.value
    assert shown["noticed"] == local["noticed"]
    assert shown["why_next"] == local["why_next"]
    assert result["result"]["why_this_question"]["from_trace"] is True
    assert result["result"]["adaptation_view"]["from_trace"] is True
    assert result["research"]["strategy"]["decision"] == engine.decision.value


def test_misconception_not_claimed_without_signal():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P8-EX-003",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    result = scripted_submit(service, view["session_id"], "strong_correct")
    engine = service.tutor.get_trace(view["session_id"])[-1]
    explanation = result["result"]["explanation"]
    if not engine.evidence.misconception_signal:
        assert explanation["misconception_mentioned"] is False
        assert "misunderstanding" not in explanation["short_message"].lower()


def test_wrong_answer_uses_catalog_teaching():
    service = make_service()
    view = service.create_session(
        topic_id="csafety-coded",
        concept_id="csafety_coded_recognition",
        session_id="P8-EX-004",
        max_steps=2,
        initial_challenge="CSAFE-COD-001",
    )
    result = service.submit_response(
        view["session_id"],
        answer="If you do not understand it, it cannot be harmful",
        confidence=5,
        approach="knew",
        challenge_id=view["challenge"]["challenge_id"],
    )
    explanation = result["result"]["explanation"]
    engine = service._experience_tutor.get_trace(view["session_id"])[-1]
    assert explanation["headline"] == "Not quite."
    assert explanation["teaching"]
    assert explanation["misconception_mentioned"] == bool(engine.evidence.misconception_signal)
    if engine.evidence.misconception_signal:
        assert "misunderstanding" in explanation["short_message"].lower()
