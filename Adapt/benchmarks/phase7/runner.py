"""Phase 7 adaptive learning experience benchmark.

python -m benchmarks.phase7.runner
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
from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.enums import AdaptationAction, DiagnosticConfidence, StrategyName
from adapt.models.learner_state import initial_learner_state
from adapt.product.service import ProductService
from adapt.selection.selector import Phase7ChallengeSelector
from adapt.tutor.tutor import DEFAULT_SEED
from benchmarks.phase7.expected import BENCHMARK_VERSION, RANDOM_SEED
from benchmarks.phase7.metrics import compute_metrics

RESULTS_DIR = ROOT / "results" / "phase7"

PROBE_TYPES = {
    "DIAGNOSTIC",
    "PREDICTION",
    "ERROR_ANALYSIS",
    "COMPARE",
    "EXPLANATION",
    "TRUE_FALSE",
    "CONCEPT_CHECK",
}
REMEDIATE_TYPES = {"REMEDIATION", "ERROR_ANALYSIS", "COMPARE", "TRUE_FALSE", "DIAGNOSTIC"}
INCREASE_TYPES = {"TRANSFER", "APPLICATION", "SCENARIO", "DIRECT", "SEQUENCE", "MULTIPLE_CHOICE"}


def _decision(action: AdaptationAction) -> AdaptationDecision:
    return AdaptationDecision(
        decision=action,
        reason=("benchmark",),
        confidence=DiagnosticConfidence.MODERATE,
        evidence_used=("B-1",),
    )


def _consistent(strategy: StrategyName, chosen, current) -> bool:
    if strategy == StrategyName.INCREASE:
        return chosen.difficulty >= current.difficulty or chosen.challenge_type in INCREASE_TYPES
    if strategy == StrategyName.PROBE:
        return chosen.challenge_type in PROBE_TYPES or chosen.diagnostic_value >= 0.7
    if strategy == StrategyName.REMEDIATE:
        return chosen.challenge_type in REMEDIATE_TYPES or bool(chosen.target_misconception)
    if strategy == StrategyName.DECREASE:
        return chosen.difficulty <= current.difficulty
    return True


def run_catalog() -> dict[str, Any]:
    metrics = CATALOG.metrics()
    types = sorted({item.challenge_type for item in CATALOG.challenges})
    return {**metrics, "type_names": types, "errors": CATALOG.validate()}


def run_repetition_and_selection() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    selector = Phase7ChallengeSelector()
    current = CATALOG.engine_challenge("CSAFE-CTX-001")
    state = initial_learner_state("B7", "csafety_context_preservation")
    used = ["CSAFE-CTX-001"]
    eligible = 0
    avoided = 0
    ok = 0
    total = 0
    type_hits: set[str] = set()
    challenge = current
    pairs = (
        (AdaptationAction.MAINTAIN_DIFFICULTY, StrategyName.MAINTAIN),
        (AdaptationAction.INCREASE_DIFFICULTY, StrategyName.INCREASE),
        (AdaptationAction.PROBE_UNCERTAINTY, StrategyName.PROBE),
        (AdaptationAction.REMEDIATE, StrategyName.REMEDIATE),
        (AdaptationAction.MAINTAIN_DIFFICULTY, StrategyName.MAINTAIN),
        (AdaptationAction.GATHER_MORE_EVIDENCE, StrategyName.GATHER_EVIDENCE),
        (AdaptationAction.INCREASE_DIFFICULTY, StrategyName.INCREASE),
        (AdaptationAction.PROBE_UNCERTAINTY, StrategyName.PROBE),
        (AdaptationAction.DECREASE_DIFFICULTY, StrategyName.DECREASE),
        (AdaptationAction.MAINTAIN_DIFFICULTY, StrategyName.MAINTAIN),
    )
    recent_window = 3
    for action, strategy in pairs * 4:
        current_meta = CATALOG.challenge(challenge.challenge_id)
        chosen = selector.select(_decision(action), state, challenge, list(used), strategy)
        meta = CATALOG.challenge(chosen.challenge_id)
        type_hits.add(meta.challenge_type)
        total += 1
        if _consistent(strategy, meta, current_meta):
            ok += 1
        recent = used[-recent_window:]
        alternatives = [
            item
            for item in CATALOG.challenges
            if item.domain == "community-safety" and item.id not in recent and item.id != challenge.challenge_id
        ]
        if strategy != StrategyName.REMEDIATE and alternatives:
            eligible += 1
            if chosen.challenge_id not in recent:
                avoided += 1
        if chosen.challenge_id not in used:
            used.append(chosen.challenge_id)
        challenge = chosen
    a = Phase7ChallengeSelector()
    b = Phase7ChallengeSelector()
    first = a.select(_decision(AdaptationAction.INCREASE_DIFFICULTY), state, current, ["CSAFE-CTX-001"], StrategyName.INCREASE)
    second = b.select(_decision(AdaptationAction.INCREASE_DIFFICULTY), state, current, ["CSAFE-CTX-001"], StrategyName.INCREASE)
    return (
        {"eligible": eligible, "avoided": avoided},
        {"ok": ok, "total": total, "types": sorted(type_hits)},
        {"identical": first.challenge_id == second.challenge_id, "id": first.challenge_id},
    )


def run_product_traces(*, seed: int) -> dict[str, Any]:
    service = ProductService(seed=seed)
    view = service.create_session(
        topic_id="csafety-context",
        session_id="P7-BENCH-CS",
        max_steps=6,
        initial_challenge="CSAFE-CTX-001",
    )
    kinds = ("strong_correct", "strong_correct", "weak_correct", "misconception", "misconception", "strong_correct")
    from tests.phase4.helpers import scripted_submit

    for kind in kinds:
        session = service.get_session(view["session_id"])
        if session.get("complete"):
            break
        scripted_submit(service, view["session_id"], kind)
    trace = service.get_trace(view["session_id"])
    complete = sum(1 for item in trace["chain"] if item["complete"])
    cf = service.run_counterfactual()
    return {
        "traces": {"complete": complete, "total": len(trace["chain"])},
        "counterfactual": {
            "preserved": bool(cf["differentiated"])
            and cf["learner_a"]["final_decision"] != cf["learner_b"]["final_decision"]
        },
        "session_strategies": [item["strategy"]["decision"] for item in trace["chain"]],
    }


def run_benchmark(*, persist: bool = True, seed: int = RANDOM_SEED) -> dict[str, Any]:
    catalog = run_catalog()
    repetition, consistency, determinism = run_repetition_and_selection()
    product = run_product_traces(seed=seed)
    payload = {
        "meta": {
            "phase": 7,
            "benchmark_version": BENCHMARK_VERSION,
            "seed": seed,
            "executed": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "default_seed": DEFAULT_SEED,
        },
        "catalog": catalog,
        "repetition": repetition,
        "consistency": consistency,
        "determinism": determinism,
        "traces": product["traces"],
        "counterfactual": product["counterfactual"],
        "session_strategies": product["session_strategies"],
    }
    scored = compute_metrics(payload)
    payload.update(scored)
    if persist:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "metrics.json").write_text(json.dumps(payload["metrics"], indent=2) + "\n", encoding="utf-8")
        (RESULTS_DIR / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def print_summary(payload: dict[str, Any]) -> None:
    print("Phase 7 benchmark")
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
