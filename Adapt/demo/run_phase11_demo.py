#!/usr/bin/env python3
"""Phase 11 competition demo: polished product path plus live counterfactual.

Target: about 2–3 minutes. Seed 20260819.
Uses AdaptiveTutor through ProductService. Does not hardcode decisions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapt.product.labels import PROMISE
from adapt.product.service import ProductService

SEED = 20260819


def main() -> int:
    print(PROMISE)
    print("ADAPT — Learn differently.")
    print("An AI tutor that adapts to how you learn, not just whether you are right.")
    print(f"seed={SEED}")
    print()
    service = ProductService(seed=SEED)

    print("0:00  LANDING")
    print("  Learn differently.")
    print("  Answer → ADAPT notices → ADAPT adapts")
    print()
    print("0:15  CHOOSE — Quantum / Superposition")
    view = service.create_session(
        concept_id="q_superposition",
        subject_id="quantum",
        learner_id="demo-p11",
        max_steps=4,
        mode="demo",
    )
    prompt = view["challenge"].get("prompt_display") or view["challenge"]["prompt"]
    print(f"  Challenge: {prompt}")
    print()

    print("0:30  ANSWER 1 — correct, confident, knew it")
    first = service.submit_response(
        view["session_id"],
        answer="False",
        confidence=5,
        approach="knew",
        challenge_id=view["challenge"]["challenge_id"],
    )
    engine = service._experience_tutor.get_trace(view["session_id"])[-1]
    noticed = first["result"]["noticed"]
    print("0:45  WHAT ADAPT NOTICED")
    print(f"  {noticed.get('headline') or noticed.get('summary')}")
    print(f"  {noticed.get('body') or noticed.get('summary')}")
    print()
    print("1:00  ADAPTATION MOMENT")
    print(f"  ADAPT ADAPTED → {first['result']['adaptation']['decision']} (engine {engine.decision.value})")
    print(f"  Why this question? {first['result']['why_this_question']['text']}")
    print()
    print("1:15  NEXT CHALLENGE")
    nxt = first.get("challenge") or {}
    print(f"  {nxt.get('prompt_display') or nxt.get('prompt') or 'session complete'}")
    print()

    print("1:30  DIFFERENT EVIDENCE PATH — guessed, low confidence")
    if first.get("challenge"):
        answer = first["challenge"]["choices"][0] if first["challenge"].get("choices") else "False"
        second = service.submit_response(
            first["session_id"],
            answer=answer,
            confidence=1,
            approach="guessed",
            challenge_id=first["challenge"]["challenge_id"],
        )
        engine2 = service._experience_tutor.get_trace(view["session_id"])[-1]
        print(f"  Strategy: {second['result']['adaptation']['decision']} (engine {engine2.decision.value})")
        second_decision = second["result"]["adaptation"]["decision"]
    else:
        second_decision = None
        print("  Session had no second challenge.")
    print()

    print("1:50  COUNTERFACTUAL — same start, different evidence")
    cf = service.run_counterfactual()
    a_engine = service.tutor.get_trace(cf["learner_a"]["session"]["session_id"])[-1]
    b_engine = service.tutor.get_trace(cf["learner_b"]["session"]["session_id"])[-1]
    print(f"  {cf['headline']}")
    print(f"  Learner A → {cf['learner_a']['final_decision']} (engine {a_engine.decision.value})")
    print(f"  Learner B → {cf['learner_b']['final_decision']} (engine {b_engine.decision.value})")
    print(f"  Differentiated: {cf['differentiated']}")
    print()

    print("2:10  Research Mode")
    trace = service.get_trace(view["session_id"])
    last = trace["chain"][-1]
    print(f"  Evidence → {last['evidence']['answer_status']}")
    print(f"  State → mastery {last['state']['mastery']}")
    print(f"  Strategy → {last['strategy']['decision']}")
    print(f"  Next challenge → {last['next_challenge']['challenge_id']}")
    print()
    print("2:30  CLOSE")
    print("  Different evidence.")
    print("  Different adaptation.")
    payload = {
        "seed": SEED,
        "decisions": [
            first["result"]["adaptation"]["decision"],
            second_decision,
        ],
        "counterfactual": {
            "a": cf["learner_a"]["final_decision"],
            "b": cf["learner_b"]["final_decision"],
            "engine_a": a_engine.decision.value,
            "engine_b": b_engine.decision.value,
        },
        "live_engine": True,
        "differentiated": cf["differentiated"],
    }
    print(json.dumps(payload, indent=2))
    if a_engine.decision.value != cf["learner_a"]["final_decision"]:
        return 1
    if b_engine.decision.value != cf["learner_b"]["final_decision"]:
        return 1
    return 0 if cf["differentiated"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
