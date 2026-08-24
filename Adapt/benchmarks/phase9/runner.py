"""Phase 9 competitive product polish benchmark.

python -m benchmarks.phase9.runner
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
from benchmarks.phase9.expected import BENCHMARK_VERSION, RANDOM_SEED
from benchmarks.phase9.metrics import compute_metrics
from tests.phase4.helpers import make_service, run_kinds_through_product, run_kinds_through_tutor, scripted_submit

RESULTS_DIR = ROOT / "results" / "phase9"
STATIC = ROOT / "src" / "app" / "static"


def run_navigation() -> dict[str, Any]:
    app_js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    required = (
        "Learn differently with ADAPT.",
        "Start Learning",
        "What do you want to explore?",
        "Check Answer",
        "What ADAPT noticed",
    )
    ok = all(item in app_js for item in required)
    service = make_service(seed=RANDOM_SEED)
    subjects = service.list_subjects()
    view = service.create_session(concept_id="csafety_context_preservation", max_steps=2, session_id="P9-B-NAV")
    answer = (
        view["challenge"].get("choices", ["Preserve the surrounding conversation context before deciding how to respond or report"])[0]
        if view["challenge"].get("choices")
        else "Preserve the surrounding conversation context before deciding how to respond or report"
    )
    result = service.submit_response(
        view["session_id"],
        answer=answer,
        confidence=3,
        approach="worked",
        challenge_id=view["challenge"]["challenge_id"],
    )
    ok = ok and len(subjects) == 1 and bool(result["result"]["noticed"])
    return {"ok": ok, "subjects": len(subjects)}


def run_domains() -> dict[str, Any]:
    counts = {
        subject.subject_id: len(CATALOG.concepts_for_subject(subject.subject_id))
        for subject in CATALOG.subjects
    }
    return {
        "subjects": len(CATALOG.subjects),
        "min_concepts": min(counts.values()) if counts else 0,
        "counts": counts,
        "errors": CATALOG.validate(),
    }


def run_variety() -> dict[str, Any]:
    types = {item.challenge_type for item in CATALOG.challenges}
    return {"types": len(types), "names": sorted(types)}


def run_rest() -> dict[str, Any]:
    service = make_service(seed=RANDOM_SEED)
    view = service.create_session(
        topic_id="csafety-context",
        session_id="P9-B-CS",
        max_steps=5,
        initial_challenge="CSAFE-CTX-001",
    )
    answer = (
        view["challenge"].get("choices", ["Preserve the surrounding conversation context before deciding how to respond or report"])[0]
        if view["challenge"].get("choices")
        else "Preserve the surrounding conversation context before deciding how to respond or report"
    )
    light = service.submit_response(
        view["session_id"],
        answer=answer,
        confidence=5,
        approach="knew",
        challenge_id=view["challenge"]["challenge_id"],
    )
    engine = service._experience_tutor.get_trace(view["session_id"])[-1]
    explain = light["result"]["explanation"]
    consistent = explain["decision"] == engine.decision.value
    seen = [view["challenge"]["challenge_id"], light["result"]["next_challenge"]["challenge_id"]]
    for kind in ("weak_correct", "strong_correct"):
        session = service.get_session(view["session_id"])
        if session.get("complete"):
            break
        result = scripted_submit(service, view["session_id"], kind)
        seen.append(result["result"]["next_challenge"]["challenge_id"])
        step = service._experience_tutor.get_trace(view["session_id"])[-1]
        consistent = consistent and result["result"]["explanation"]["decision"] == step.decision.value
    consecutive = sum(1 for i in range(1, len(seen)) if seen[i] == seen[i - 1] and seen[i] != "UNAVAILABLE")
    empty = service.get_progress(learner_id="p9-none")
    filled = service.get_progress(view["session_id"])
    research = service.get_trace(view["session_id"])
    kinds = ("strong_correct", "weak_correct")
    _s, _sess, product_results = run_kinds_through_product(
        kinds, session_id="P9-B-P", learner_id="P9-B-L", service=make_service(seed=RANDOM_SEED)
    )
    _t, _ts, traces = run_kinds_through_tutor(kinds, session_id="P9-B-T", learner_id="P9-B-L2", seed=RANDOM_SEED)
    preserve = [item["result"]["adaptation"]["decision"] for item in product_results] == [
        item.decision.value for item in traces
    ]
    a = make_service(seed=RANDOM_SEED)
    b = make_service(seed=RANDOM_SEED)
    cf_a = a.run_counterfactual()
    cf_b = b.run_counterfactual()
    cf = a.run_counterfactual()
    return {
        "lightweight": {"ok": light["result"]["explanation"]["from_trace"] is True},
        "explanations": {"ok": consistent},
        "diversity": {"ok": consecutive == 0 and len(set(seen)) >= 2},
        "progress": {"ok": empty["overall_available"] is False and filled["overall_available"] is True},
        "research": {"ok": research["trace_complete"] is True},
        "preservation": {"ok": preserve},
        "counterfactual": {
            "ok": cf["differentiated"] is True and cf["live_engine"] is True,
            "a": cf["learner_a"]["final_decision"],
            "b": cf["learner_b"]["final_decision"],
        },
        "determinism": {
            "ok": cf_a["learner_a"]["final_decision"] == cf_b["learner_a"]["final_decision"]
            and cf_a["learner_b"]["final_decision"] == cf_b["learner_b"]["final_decision"]
        },
    }


def run_benchmark(*, persist: bool = True, seed: int = RANDOM_SEED) -> dict[str, Any]:
    _ = seed
    nav = run_navigation()
    domains = run_domains()
    variety = run_variety()
    rest = run_rest()
    raw = {"navigation": nav, "domains": domains, "variety": variety, **rest}
    metrics = compute_metrics(raw)
    failures = [key for key, value in metrics.items() if not value.get("ok")]
    payload = {
        "version": BENCHMARK_VERSION,
        "seed": RANDOM_SEED,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "metrics": metrics,
        "raw": raw,
        "failures": failures,
        "pass": not failures,
    }
    if persist:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (RESULTS_DIR / "summary.json").write_text(
            json.dumps({"pass": payload["pass"], "failures": failures, "seed": RANDOM_SEED}, indent=2) + "\n",
            encoding="utf-8",
        )
    return payload


def print_summary(payload: dict[str, Any]) -> None:
    print(f"Phase 9 benchmark seed={payload['seed']} pass={payload['pass']}")
    for key, value in payload["metrics"].items():
        mark = "PASS" if value.get("ok") else "FAIL"
        print(f"  {key}: {mark}")
    if payload["failures"]:
        print("failures:", ", ".join(payload["failures"]))


def main() -> int:
    persist = "--persist" in sys.argv or True
    if "--no-persist" in sys.argv:
        persist = False
    payload = run_benchmark(persist=persist)
    print_summary(payload)
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
