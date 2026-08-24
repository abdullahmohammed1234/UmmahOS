"""Human-readable explanations must match actual engine evidence."""

from __future__ import annotations

from adapt.product.trace_explain import evidence_summary, human_trace_explanation
from tests.phase4.helpers import make_service, scripted_submit


def test_explanation_matches_engine_trace():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P6-EX-001",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    result = scripted_submit(service, view["session_id"], "strong_correct")
    engine = service.tutor.get_trace(view["session_id"])[-1]
    explain = result["research"]["human_explanation"]
    assert explain["decision"] == engine.decision.value
    assert explain["reason"] == engine.reason
    assert explain["answer_status"] == engine.evidence.answer_status.value
    assert explain["reasoning_quality"] == engine.evidence.reasoning_quality.value
    assert explain["confidence_signal"] == engine.evidence.confidence_signal.value
    assert "strong reasoning" in explain["evidence"].lower()
    assert explain["misconception_signal"] == engine.evidence.misconception_signal


def test_weak_reasoning_does_not_claim_strong_evidence():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P6-EX-002",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    result = scripted_submit(service, view["session_id"], "weak_correct")
    engine = service.tutor.get_trace(view["session_id"])[-1]
    explain = human_trace_explanation(engine)
    summary = evidence_summary(engine.evidence)
    assert engine.evidence.reasoning_quality.value == "WEAK"
    assert "strong reasoning" not in explain["evidence"].lower()
    assert "weak reasoning" in summary.lower()
    assert result["research"]["human_explanation"]["evidence"] == summary


def test_misconception_explanation_requires_signal():
    service = make_service()
    view = service.create_session(
        topic_id="algebra",
        session_id="P6-EX-003",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    scripted_submit(service, view["session_id"], "misconception")
    engine = service.tutor.get_trace(view["session_id"])[-1]
    explain = human_trace_explanation(engine)
    if engine.evidence.misconception_signal:
        assert "misconception" in explain["evidence"].lower()
    else:
        assert "misconception signal" not in explain["evidence"].lower()
    assert explain["decision"] == engine.decision.value
