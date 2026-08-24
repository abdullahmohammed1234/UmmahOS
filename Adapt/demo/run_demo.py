#!/usr/bin/env python3
"""Run the Phase 4 guided demo through the product boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapt.product.demo import load_demo_scenario
from adapt.product.service import ProductService


def main() -> int:
    scenario = load_demo_scenario()
    service = ProductService()
    session = service.start_demo(scenario=scenario)
    session_id = session["session_id"]
    print("ADAPT guided demo")
    print(f"Challenge: {session['challenge']['prompt']}")
    print()
    while True:
        try:
            result = service.demo_step(session_id)
        except Exception as exc:  # noqa: BLE001 — demo CLI should print the product error
            print(str(exc))
            break
        research = result["research"]
        print(f"Step {research['step_number']}")
        print(f"  Evidence  {research['evidence']['answer_status']} / {research['evidence']['reasoning_quality']}")
        print(f"  State     mastery {research['state']['mastery']} {research['state']['mastery_arrow']}")
        print(f"  Strategy  {research['strategy']['decision']}")
        print(f"  Why       {research['strategy']['reason']}")
        print(f"  Next      {research['next_challenge']['challenge_id']}")
        print()
        if result.get("demo", {}).get("complete") or result.get("complete"):
            break
    summary = service.get_summary(session_id)
    story = service.get_story(session_id)
    print("Summary")
    print(json.dumps({k: summary[k] for k in (
        "challenges_completed",
        "concepts_explored",
        "strategies_used",
        "adapt_adjusted_path",
        "strategy_names",
    )}, indent=2))
    print("Story")
    for beat in story["beats"]:
        print(f"  → {beat['text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
