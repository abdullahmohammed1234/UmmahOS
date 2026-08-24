"""Phase 2 benchmark runner."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapt.strategy.invariants import check_record
from benchmarks.phase1f.evaluator import run_adapt as run_phase1f_adapt
from benchmarks.phase1f.scenarios import SCENARIO_BY_ID as PHASE1F_BY_ID
from benchmarks.phase2.constants import BENCHMARK_VERSION, RANDOM_SEED
from benchmarks.phase2.counterfactual import run_counterfactuals
from benchmarks.phase2.evaluator import evaluate_scenarios, make_pipeline
from benchmarks.phase2.metrics import compute_metrics
from benchmarks.phase2.report import render_report
from benchmarks.phase2.scenarios import SCENARIOS

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "phase2"

PHASE1F_BASELINE = {
    "G-001-B": {
        "decision": "MAINTAIN_DIFFICULTY",
        "target": "justified strategy; do not force INCREASE",
    },
    "G-003-A": {
        "decision": "DECREASE_DIFFICULTY",
        "target": "PROBE / GATHER_EVIDENCE",
    },
    "G-003-B": {
        "decision": "DECREASE_DIFFICULTY",
        "target": "PROBE / GATHER_EVIDENCE",
    },
    "G-005-D": {
        "decision": "REMEDIATE",
        "target": "strategy recovery away from REMEDIATE",
    },
}


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip() or "unavailable"
    except OSError:
        return "unavailable"
    return "unavailable"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _phase1f_regressions(pipeline) -> list[dict[str, Any]]:
    out = []
    for scenario_id, baseline in PHASE1F_BASELINE.items():
        record = run_phase1f_adapt(PHASE1F_BY_ID[scenario_id], pipeline)
        strategy = (record.get("decision_trace") or {}).get("strategy_decision") or {}
        phase2 = strategy.get("decision")
        evidence = record.get("evidence") or {}
        note = None
        verdict = "UNRESOLVED"
        if scenario_id == "G-001-B":
            if evidence.get("reasoning_quality") != "STRONG" and phase2 != "INCREASE":
                verdict = "DOCUMENTED"
                note = (
                    "FR-M-002 is subtraction; the supplied reasoning talks about adding numerators. "
                    "Evidence is not strong enough to justify INCREASE. Phase 1F's INCREASE label "
                    "was overly optimistic for this item."
                )
            elif phase2 == "INCREASE":
                verdict = "CHANGED"
                note = "Phase 2 increased difficulty; check whether evidence actually supports it."
            else:
                verdict = "DOCUMENTED"
                note = "Phase 2 did not force INCREASE. See evidence quality."
        elif scenario_id.startswith("G-003"):
            if phase2 in {"PROBE", "GATHER_EVIDENCE"}:
                verdict = "FIXED"
            else:
                verdict = "NOT_FIXED"
        elif scenario_id == "G-005-D":
            if phase2 in {"MAINTAIN", "PROBE", "INCREASE"}:
                verdict = "FIXED"
            elif phase2 == "REMEDIATE":
                verdict = "NOT_FIXED"
        out.append(
            {
                "scenario_id": scenario_id,
                "phase1f_decision": baseline["decision"],
                "phase2_strategy": phase2,
                "phase2_action": record.get("decision"),
                "target": baseline["target"],
                "verdict": verdict,
                "note": note,
                "appropriate_under_phase1f_labels": record.get("appropriate"),
            }
        )
    return out


def _invariants(records: list[dict[str, Any]], counterfactuals: list[dict[str, Any]]) -> dict[str, bool]:
    flags = [check_record(item) for item in records]
    inv1 = all(item.get("invariant_1", True) for item in flags)
    inv8 = all(item.get("invariant_8", False) for item in flags)
    paths_ok = True
    for item in records:
        path = item.get("strategy_path") or []
        compact = "->".join(path)
        if "INCREASE->DECREASE->INCREASE" in compact:
            paths_ok = False
    cf_ok = all(item.get("differentiated") for item in counterfactuals)
    return {
        "invariant_1_weak_evidence_not_high_mastery": inv1,
        "invariant_8_traceable": inv8,
        "invariant_9_no_simple_oscillation": paths_ok,
        "invariant_6_counterfactuals_differ": cf_ok,
    }


def run_benchmark(*, persist: bool = True) -> dict[str, Any]:
    pipeline = make_pipeline()
    records = evaluate_scenarios(SCENARIOS, pipeline)
    counterfactuals = run_counterfactuals()
    metrics = compute_metrics(records=records, counterfactuals=counterfactuals)
    phase1f_failures = _phase1f_regressions(pipeline)
    invariants = _invariants(records, counterfactuals)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {
        "benchmark_version": BENCHMARK_VERSION,
        "random_seed": RANDOM_SEED,
        "timestamp": timestamp,
        "python_version": platform.python_version(),
        "git_commit": _git_commit(),
        "scenario_count": len(SCENARIOS),
        "platform": platform.platform(),
        "phase1f_frozen": True,
    }
    raw = {
        "meta": meta,
        "records": records,
        "counterfactuals": counterfactuals,
        "phase1f_failure_regressions": phase1f_failures,
        "invariants": invariants,
    }
    report = render_report(
        meta=meta,
        metrics=metrics,
        records=records,
        counterfactuals=counterfactuals,
        phase1f_failures=phase1f_failures,
        invariants=invariants,
    )
    if persist:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        run_dir = RESULTS_DIR / "runs" / timestamp.replace(":", "")
        run_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "raw_results.json": raw,
            "metrics.json": {"meta": meta, **metrics},
        }
        for directory in (RESULTS_DIR, run_dir):
            for name, data in payload.items():
                (directory / name).write_text(
                    json.dumps(_jsonable(data), indent=2, sort_keys=True),
                    encoding="utf-8",
                )
            (directory / "report.md").write_text(report, encoding="utf-8")
    return {
        "meta": meta,
        "raw": raw,
        "metrics": metrics,
        "report": report,
        "records": records,
        "counterfactuals": counterfactuals,
        "phase1f_failures": phase1f_failures,
        "invariants": invariants,
    }


def print_summary(result: dict[str, Any]) -> None:
    metrics = result["metrics"]
    print("========================================")
    print("ADAPT PHASE 2")
    print("ADAPTIVE STRATEGY LAYER")
    print("========================================")
    print()
    print(f"Scenarios: {result['meta']['scenario_count']}")
    print()
    print(f"Strategy appropriateness: {metrics['M2-001_strategy_appropriateness']['display']}")
    print(f"Strategy recovery: {metrics['M2-002_strategy_recovery']['display']}")
    print(
        "Misconception/regression separation: "
        f"{metrics['M2-003_misconception_regression_separation']['display']}"
    )
    print(f"Strategy stability: {metrics['M2-004_strategy_stability']['display']}")
    print(f"Evidence sensitivity: {metrics['M2-005_evidence_sensitivity']['display']}")
    print(f"Traceability: {metrics['M2-006_strategy_traceability']['display']}")
    print(f"Cross-concept generalization: {metrics['M2-007_cross_concept_generalization']['display']}")
    print()
    print("Counterfactual strategy tests:")
    for item in result["counterfactuals"]:
        flag = "PASS" if item.get("evidence_sensitive") else "FAIL"
        print(f"  {item['pair_id']}: {item['decision_a']} vs {item['decision_b']} [{flag}]")
    print()
    print("Overall:")
    app = metrics["M2-001_strategy_appropriateness"].get("rate")
    rec = metrics["M2-002_strategy_recovery"].get("rate")
    sep = metrics["M2-003_misconception_regression_separation"].get("rate")
    tr = metrics["M2-006_strategy_traceability"].get("rate")
    cf = metrics["M2-005_evidence_sensitivity"].get("rate")
    ok = (
        (app or 0) >= 0.80
        and (rec or 0) >= 0.70
        and (sep or 0) >= 0.70
        and (tr or 0) >= 1.0
        and (cf or 0) >= 0.75
    )
    print("  PASS" if ok else "  MIXED / SEE FAILURES")
    print("========================================")


def main() -> int:
    result = run_benchmark(persist=True)
    print_summary(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
