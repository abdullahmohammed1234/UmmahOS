#!/usr/bin/env python3
"""Competition demo: deterministic AdaptiveTutor path plus counterfactual."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapt.product.demo import load_demo_scenario
from adapt.product.labels import DEMO_SCENARIO_LABEL, PROMISE
from adapt.product.service import ProductService
from adapt.tutor.tutor import DEFAULT_SEED


def _print_step(result: dict) -> None:
    research = result["research"]
    explain = research["human_explanation"]
    print(f"Step {research['step_number']}")
    print(f"  Evidence  {explain['evidence']}")
    print(f"  State     {explain['state']}")
    print(f"  Strategy  {explain['strategy_label']} ({research['strategy']['decision']})")
    print(f"  Next      {research['next_challenge']['challenge_id']}")
    print(f"  Why next  {explain['next_challenge']}")
    print()


def main() -> int:
    print(PROMISE)
    print(DEMO_SCENARIO_LABEL)
    print(f"seed={DEFAULT_SEED}")
    print()
    scenario = load_demo_scenario()
    service = ProductService(seed=DEFAULT_SEED)
    session = service.start_demo(scenario=scenario)
    session_id = session["session_id"]
    opening = session["opening"]
    print("STEP 1 — INTRO")
    print("  ADAPT")
    print("  A tutor that adapts to how you learn.")
    print()
    print("STEP 2 — INITIAL ASSESSMENT")
    print(f"  Concept: {opening['concept']}")
    print(f"  Mastery: {opening['mastery']}")
    print(f"  Confidence: {opening['confidence']}")
    print(f"  Strategy: {opening['strategy']}")
    print(f"  Challenge: {session['challenge']['prompt']}")
    print()
    decisions = []
    while True:
        result = service.demo_step(session_id)
        engine = service.tutor.get_trace(session_id)[-1]
        displayed = result["result"]["adaptation"]["decision"]
        if displayed != engine.decision.value:
            raise SystemExit("displayed decision diverged from AdaptiveTutor")
        decisions.append(displayed)
        _print_step(result)
        if result.get("demo", {}).get("complete") or result.get("complete"):
            break
    print("Demo decisions:", " → ".join(decisions))
    print()
    print("COUNTERFACTUAL — same start, different evidence")
    cf = service.run_counterfactual()
    a_engine = service.tutor.get_trace(cf["learner_a"]["session"]["session_id"])[-1]
    b_engine = service.tutor.get_trace(cf["learner_b"]["session"]["session_id"])[-1]
    print(f"  {cf['headline']}")
    print(f"  Learner A → {cf['learner_a']['final_decision_label']} ({cf['learner_a']['final_decision']})")
    print(f"  Learner B → {cf['learner_b']['final_decision_label']} ({cf['learner_b']['final_decision']})")
    print(f"  Engine A  → {a_engine.decision.value}")
    print(f"  Engine B  → {b_engine.decision.value}")
    print(f"  Differentiated: {cf['differentiated']}")
    payload = {
        "seed": DEFAULT_SEED,
        "decisions": decisions,
        "counterfactual": {
            "a": cf["learner_a"]["final_decision"],
            "b": cf["learner_b"]["final_decision"],
            "differentiated": cf["differentiated"],
        },
    }
    print()
    print(json.dumps(payload, indent=2))
    return 0 if cf["differentiated"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
