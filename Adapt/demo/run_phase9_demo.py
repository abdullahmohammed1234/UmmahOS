#!/usr/bin/env python3
"""Phase 9 competition demo: lightweight answers, live engine, counterfactual.

Target: about 2–3 minutes. Seed 20260815.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapt.product.labels import DEMO_SCENARIO_LABEL, PROMISE
from adapt.product.service import ProductService

SEED = 20260815


def main() -> int:
    print(PROMISE)
    print("ADAPT — Learn differently with ADAPT.")
    print(DEMO_SCENARIO_LABEL)
    print(f"seed={SEED}")
    print()
    service = ProductService(seed=SEED)
    print("LANDING")
    print("  Learn differently.")
    print("  ADAPT changes what you learn next based on how you learn.")
    print()
    print("CHOOSE — Quantum / Superposition")
    view = service.create_session(
        concept_id="q_superposition",
        subject_id="quantum",
        learner_id="demo-p9",
        max_steps=4,
        mode="demo",
    )
    print(f"  Challenge: {view['challenge']['prompt_display'] or view['challenge']['prompt']}")
    print()
    first = service.submit_response(
        view["session_id"],
        answer="False",
        confidence=5,
        approach="knew",
        challenge_id=view["challenge"]["challenge_id"],
    )
    engine = service._experience_tutor.get_trace(view["session_id"])[-1]
    noticed = first["result"]["noticed"]
    print("ANSWER 1 — correct, confident, knew the method")
    print(f"  ADAPT noticed: {noticed.get('body') or noticed.get('summary')}")
    print(f"  Strategy: {first['result']['adaptation']['decision']} (engine {engine.decision.value})")
    print(f"  Why: {first['result']['why_this_question']['text']}")
    print()
    second = service.submit_response(
        first["session_id"],
        answer=first["challenge"]["choices"][0] if first.get("challenge", {}).get("choices") else "False",
        confidence=1,
        approach="guessed",
        challenge_id=first["challenge"]["challenge_id"],
    )
    engine2 = service._experience_tutor.get_trace(view["session_id"])[-1]
    print("ANSWER 2 — lightweight confidence, guessed")
    print(f"  Strategy: {second['result']['adaptation']['decision']} (engine {engine2.decision.value})")
    print()
    print("RESEARCH MODE")
    trace = service.get_trace(view["session_id"])
    last = trace["chain"][-1]
    print(f"  Evidence → {last['evidence']['answer_status']}")
    print(f"  State → mastery {last['state']['mastery']}")
    print(f"  Strategy → {last['strategy']['decision']}")
    print(f"  Challenge → {last['next_challenge']['challenge_id']}")
    print()
    print("COUNTERFACTUAL")
    cf = service.run_counterfactual()
    print(f"  {cf['headline']}")
    print(f"  Learner A → {cf['learner_a']['final_decision']}")
    print(f"  Learner B → {cf['learner_b']['final_decision']}")
    print(f"  Differentiated: {cf['differentiated']}")
    payload = {
        "seed": SEED,
        "decisions": [
            first["result"]["adaptation"]["decision"],
            second["result"]["adaptation"]["decision"],
        ],
        "counterfactual": {
            "a": cf["learner_a"]["final_decision"],
            "b": cf["learner_b"]["final_decision"],
        },
        "live_engine": True,
    }
    print(json.dumps(payload, indent=2))
    return 0 if cf["differentiated"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
