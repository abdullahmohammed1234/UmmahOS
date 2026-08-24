"""Product boundary uses Gemini only when enabled; default path is unchanged."""

from __future__ import annotations

from adapt.llm.testing import MockLLMClient
from adapt.product.service import ProductService
from tests.phase4.helpers import make_service, run_kinds_through_product, run_kinds_through_tutor
from tests.phase12.helpers import VALID_EVIDENCE, dumps


def test_default_product_matches_direct_tutor():
    kinds = ("strong_correct", "weak_correct")
    _service, _session, product_results = run_kinds_through_product(kinds, session_id="P12-PROD")
    _tutor, _tsession, traces = run_kinds_through_tutor(kinds, session_id="P12-TUT", learner_id="P12-L")
    assert [item["result"]["adaptation"]["decision"] for item in product_results] == [
        item.decision.value for item in traces
    ]


def test_gemini_enabled_session_exposes_source_not_raw_json_to_learner_feedback():
    service = ProductService(llm_client=MockLLMClient(text=dumps(VALID_EVIDENCE)), seed=20260819)
    view = service.create_session(
        topic_id="algebra",
        session_id="P12-GEM-1",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    result = service.submit_response(
        view["session_id"],
        answer="2",
        confidence=1,
        reasoning="I guessed.",
        approach="guessed",
    )
    assert result["result"]["evidence_source"] == "GEMINI"
    assert result["result"]["evidence_source_label"] == "AI-assisted evidence analysis"
    assert result["llm_enabled"] is True
    noticed = result["result"]["noticed"]
    assert "correctness" not in str(noticed).lower() or "What ADAPT noticed" in noticed["title"]
    trace = service.get_trace(view["session_id"])
    assert "Human Input" in trace["workflow_chain"]
    assert trace["workflow"]["source"] == "GEMINI"


def test_make_service_does_not_enable_gemini():
    service = make_service()
    assert service._llm_analyzer is None


def test_nvidia_success_is_labeled_ai_assisted_not_fallback():
    class NvidiaMock(MockLLMClient):
        provider = "nvidia"

    service = ProductService(llm_client=NvidiaMock(text=dumps(VALID_EVIDENCE)), seed=20260819)
    view = service.create_session(
        topic_id="algebra",
        session_id="P12-NV-LABEL",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    result = service.submit_response(
        view["session_id"],
        answer="2",
        confidence=1,
        reasoning="I guessed.",
        approach="guessed",
    )
    assert result["result"]["evidence_source"] == "NVIDIA"
    assert result["result"]["evidence_source_label"] == "AI-assisted evidence analysis"


def test_unavailable_llm_is_labeled_fallback_not_ai():
    from adapt.llm.testing import UnavailableLLMClient

    service = ProductService(llm_client=UnavailableLLMClient(), seed=20260819)
    view = service.create_session(
        topic_id="algebra",
        session_id="P12-FB-LABEL",
        initial_challenge="ALG-M-001",
        max_steps=2,
    )
    result = service.submit_response(
        view["session_id"],
        answer="2",
        confidence=1,
        reasoning="I guessed.",
        approach="guessed",
    )
    assert result["result"]["evidence_source"] == "DETERMINISTIC_FALLBACK"
    assert result["result"]["evidence_source_label"] == "Deterministic fallback evidence analysis"
