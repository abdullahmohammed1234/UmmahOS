"""Offline sample comparison for competition recording.

Same learner cases are sent to:

1. Single-prompt baseline (`baseline_v1`) — one prompt chooses the next action
2. P-003 / evidence_v3 workflow — Gemini-style evidence extraction, validation,
   then AdaptiveTutor

This uses the frozen prompt-conditioned simulator. It is NOT live Gemini.
It does not persist results. It does not change AdaptiveTutor, P-003, or holdout IDs.

Usage (from repository root):

    python scripts/run_sample_comparison.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for path in (str(SRC), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from adapt.llm.simulator import PromptSimulatorClient
from benchmarks.phase12.expected import RANDOM_SEED
from benchmarks.phase12.runner import run_baseline_scenario, run_workflow_scenario
from benchmarks.phase12.scenarios import SCENARIOS_BY_ID

SAMPLE_IDS = ("A-001", "B-001", "C-001", "D-001", "F-001", "F-002", "J-001")
PROMPT_ID = "evidence_v3"


def _print_case(scenario_id: str) -> None:
    scenario = SCENARIOS_BY_ID[scenario_id]
    evidence_client = PromptSimulatorClient(mode="evidence")
    baseline_client = PromptSimulatorClient(mode="baseline")
    workflow = run_workflow_scenario(
        scenario,
        client=evidence_client,
        prompt_id=PROMPT_ID,
        seed=RANDOM_SEED,
    )
    baseline = run_baseline_scenario(scenario, client=baseline_client)
    evidence = workflow.get("llm_evidence") or {}
    print("=" * 72)
    print(f"CASE {scenario_id} — {scenario.title}")
    print(f"Question: {scenario.challenge.question}")
    print(f"Expected answer: {scenario.challenge.expected_answer}")
    print("--- SAME HUMAN INPUT ---")
    print(f"  answer:      {scenario.answer}")
    print(f"  confidence:  {scenario.confidence}")
    print(f"  approach:    {scenario.approach}")
    print(f"  explanation: {scenario.explanation}")
    print("--- SINGLE-PROMPT BASELINE (baseline_v1) ---")
    print(f"  architecture: single_prompt")
    print(f"  next_action:  {baseline.get('next_action')}")
    print(f"  mastery:      {baseline.get('mastery')}")
    raw = (baseline.get("raw") or {})
    print(f"  reason:       {raw.get('reason')}")
    print("--- P-003 WORKFLOW (evidence_v3 → validation → AdaptiveTutor) ---")
    print(f"  source:       {workflow.get('source')}")
    print(f"  backend:      prompt-simulator (not live Gemini)")
    print(f"  valid:        {workflow.get('validation_ok')}")
    print(f"  evidence:     {json.dumps(evidence, ensure_ascii=True)}")
    print(f"  strategy:     {workflow.get('adapt_strategy')}")
    print(f"  next:         {workflow.get('next_challenge_id')}")
    print(f"  mastery:      {workflow.get('mastery')}")
    print()


def main() -> int:
    print("ADAPT sample comparison")
    print("Backend: prompt-simulator  |  Selected prompt: evidence_v3 (P-003)")
    print("This is not a live Gemini score. Fallback is not claimed as Gemini success.")
    print()
    for scenario_id in SAMPLE_IDS:
        _print_case(scenario_id)
    print("Holdout (frozen, n=30, same methodology): workflow 20/30 vs baseline 11/30, p ≈ 0.137 (not significant).")
    print("Phase 5 remains INCONCLUSIVE (n = 0). No learning-gain claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
