"""Prompt versions change extraction behavior. That is the Phase 12 point."""

from __future__ import annotations

from adapt.llm.simulator import PromptSimulatorClient
from benchmarks.phase12.runner import run_workflow_scenario
from benchmarks.phase12.scenarios import SCENARIOS_BY_ID


def test_injection_prompt_versions_are_not_identical():
    scenario = SCENARIOS_BY_ID["J-001"]
    client = PromptSimulatorClient()
    p2 = run_workflow_scenario(scenario, client=client, prompt_id="evidence_v2")
    p3 = run_workflow_scenario(scenario, client=PromptSimulatorClient(), prompt_id="evidence_v3")
    assert p2["injection_ok"] is False
    assert p3["injection_ok"] is True
    assert (p2.get("llm_evidence") or {}).get("evidence_strength") == "strong"
    assert (p3.get("llm_evidence") or {}).get("evidence_strength") in {"weak", "insufficient", "moderate"}


def test_lucky_guess_is_not_strong_under_contract_prompt():
    scenario = SCENARIOS_BY_ID["A-001"]
    row = run_workflow_scenario(
        scenario,
        client=PromptSimulatorClient(),
        prompt_id="evidence_v3",
    )
    evidence = row.get("llm_evidence") or {}
    assert evidence.get("correctness") == "correct"
    assert evidence.get("reasoning_quality") == "weak"
    assert evidence.get("evidence_strength") in {"weak", "insufficient"}
    assert row["adapt_strategy"] != "INCREASE"
