"""Phase 8 product UX benchmark.

python -m benchmarks.phase8.runner
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
for path in (str(SRC), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from adapt.content.catalog import CATALOG
from adapt.product.service import ProductService
from adapt.tutor.tutor import DEFAULT_SEED
from benchmarks.phase8.expected import BENCHMARK_VERSION, RANDOM_SEED
from benchmarks.phase8.metrics import compute_metrics
from tests.phase4.helpers import make_service, run_kinds_through_product, run_kinds_through_tutor, scripted_submit

RESULTS_DIR = ROOT / "results" / "phase8"
STATIC = ROOT / "src" / "app" / "static"


def run_navigation() -> dict[str, Any]:
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    required = (
        "Learn",
        "Progress",
        "Journey",
        "How ADAPT Works",
        "Learn differently with ADAPT.",
        "Start Learning",
        "See How ADAPT Works",
    )
    ok = all(item in app_js for item in required)
    service = make_service()
    subjects = service.list_subjects()
    ok = ok and len(subjects) == 1
    return {"ok": ok, "subjects": len(subjects)}


def run_concepts() -> dict[str, Any]:
    service = make_service()
    reachable = 0
    total = len(CATALOG.concepts)
    for concept in CATALOG.concepts:
        view = service.create_session(
            concept_id=concept.concept_id,
            max_steps=1,
            session_id=f"P8-C-{concept.concept_id}"[:28],
        )
        if view.get("challenge") and not view["challenge"].get("unavailable"):
            reachable += 1
    return {"ok": reachable == total, "reachable": reachable, "total": total}


def run_challenge_and_explanations() -> dict[str, Any]:
    service = make_service()
    view = service.create_session(
        topic_id="csafety-context",
        session_id="P8-BENCH-CS",
        max_steps=4,
        initial_challenge="CSAFE-CTX-001",
    )
    answer = (
        view["challenge"].get("choices", ["Preserve the surrounding conversation context before deciding how to respond or report"])[0]
        if view["challenge"].get("choices")
        else "Preserve the surrounding conversation context before deciding how to respond or report"
    )
    lightweight = service.submit_response(
        view["session_id"],
        answer=answer,
        confidence=4,
        challenge_id=view["challenge"]["challenge_id"],
    )
    engine = service._experience_tutor.get_trace(view["session_id"])[-1]
    explanation = lightweight["result"]["explanation"]
    consistent = explanation["decision"] == engine.decision.value
    complete = all(
        explanation.get(key)
        for key in ("headline", "short_message", "detailed_message", "why_next")
    )
    seen = [view["challenge"]["challenge_id"]]
    for kind in ("strong_correct", "weak_correct", "misconception"):
        session = service.get_session(view["session_id"])
        if session.get("complete"):
            break
        result = scripted_submit(service, view["session_id"], kind)
        seen.append(result["result"]["next_challenge"]["challenge_id"])
        step = service._experience_tutor.get_trace(view["session_id"])[-1]
        local = result["result"]["explanation"]
        consistent = consistent and local["decision"] == step.decision.value
        complete = complete and all(
            local.get(key) for key in ("headline", "short_message", "detailed_message", "why_next")
        )
    consecutive = sum(1 for i in range(1, len(seen)) if seen[i] == seen[i - 1] and seen[i] != "UNAVAILABLE")
    empty = service.get_progress(learner_id="no-progress-yet")
    filled = service.get_progress(view["session_id"])
    progress_ok = empty["overall_available"] is False and filled["overall_available"] is True
    research = service.get_trace(view["session_id"])
    research_ok = research["trace_complete"] is True and all(item["complete"] for item in research["chain"])
    return {
        "challenge": {"completed": 1 if lightweight["progress"]["completed"] else 0, "total": 1},
        "lightweight": {"ok": lightweight["result"]["explanation"]["from_trace"] is True},
        "explanations": {
            "complete": 4 if complete else 0,
            "total": 4,
            "consistent": consistent,
        },
        "repetition": {
            "eligible": max(len(seen) - 1, 1),
            "avoided": max(len(seen) - 1, 1) - consecutive,
        },
        "progress": {"ok": progress_ok},
        "research": {"ok": research_ok},
    }


def run_engine_and_counterfactual(*, seed: int) -> dict[str, Any]:
    kinds = ("strong_correct", "weak_correct")
    _service, _session, product_results = run_kinds_through_product(
        kinds,
        session_id="P8-BENCH-ALG",
        learner_id="P8-BENCH-L",
    )
    _tutor, _tsession, traces = run_kinds_through_tutor(
        kinds,
        session_id="P8-BENCH-T",
        learner_id="P8-BENCH-L2",
    )
    product_decisions = [item["result"]["adaptation"]["decision"] for item in product_results]
    tutor_decisions = [item.decision.value for item in traces]
    preserved = product_decisions == tutor_decisions
    a = ProductService(seed=seed)
    b = ProductService(seed=seed)
    cf_a = a.run_counterfactual()
    cf_b = b.run_counterfactual()
    a_engine = a.tutor.get_trace(cf_a["learner_a"]["session"]["session_id"])[-1]
    b_engine = a.tutor.get_trace(cf_a["learner_b"]["session"]["session_id"])[-1]
    cf_ok = (
        cf_a["differentiated"]
        and cf_a["learner_a"]["final_decision"] == a_engine.decision.value
        and cf_a["learner_b"]["final_decision"] == b_engine.decision.value
    )
    identical = (
        cf_a["learner_a"]["final_decision"] == cf_b["learner_a"]["final_decision"]
        and cf_a["learner_b"]["final_decision"] == cf_b["learner_b"]["final_decision"]
    )
    return {
        "engine": {"preserved": preserved, "product": product_decisions, "tutor": tutor_decisions},
        "counterfactual": {"preserved": cf_ok, "a": cf_a["learner_a"]["final_decision"], "b": cf_a["learner_b"]["final_decision"]},
        "determinism": {"identical": identical},
    }


def run_benchmark(*, persist: bool = True, seed: int = RANDOM_SEED) -> dict[str, Any]:
    navigation = run_navigation()
    concepts = run_concepts()
    experience = run_challenge_and_explanations()
    engine = run_engine_and_counterfactual(seed=seed)
    payload = {
        "meta": {
            "phase": 8,
            "benchmark_version": BENCHMARK_VERSION,
            "seed": seed,
            "executed": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "default_seed": DEFAULT_SEED,
        },
        "navigation": navigation,
        "concepts": concepts,
        **experience,
        **engine,
    }
    scored = compute_metrics(payload)
    payload.update(scored)
    if persist:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "metrics.json").write_text(json.dumps(payload["metrics"], indent=2) + "\n", encoding="utf-8")
        (RESULTS_DIR / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def print_summary(payload: dict[str, Any]) -> None:
    print("Phase 8 benchmark")
    for item in payload["metrics"].values():
        mark = "PASS" if item["passed"] else "FAIL"
        print(f"  {item['id']} {item['display']} [{mark}]")
    print("failures", payload["failures"])


def main() -> int:
    persist = "--no-persist" not in sys.argv
    payload = run_benchmark(persist=persist)
    print_summary(payload)
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
