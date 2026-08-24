"""Counterfactual still comes from the live engine, including the Gemini-enabled path."""

from __future__ import annotations

from adapt.llm.simulator import PromptSimulatorClient
from adapt.product.service import ProductService
from tests.phase4.helpers import make_service


def test_existing_counterfactual_still_differentiates():
    service = make_service()
    result = service.run_counterfactual()
    assert result["live_engine"] is True
    assert result["learner_a"]["final_decision"] != result["learner_b"]["final_decision"]


def test_gemini_enabled_counterfactual_is_not_hardcoded():
    service = ProductService(llm_client=PromptSimulatorClient(), seed=20260819, use_gemini=True)
    result = service.run_counterfactual()
    assert result["live_engine"] is True
    a = result["learner_a"]["final_decision"]
    b = result["learner_b"]["final_decision"]
    assert a != b
    # Decisions come from AdaptiveTutor traces, not a UI table.
    assert result["learner_a"]["trace"]["chain"]
    assert result["learner_b"]["trace"]["chain"]
    assert result["learner_a"]["final_decision"] == result["learner_a"]["trace"]["chain"][-1]["strategy"]["decision"]
    assert result["learner_b"]["final_decision"] == result["learner_b"]["trace"]["chain"][-1]["strategy"]["decision"]
