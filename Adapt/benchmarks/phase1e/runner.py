"""Phase 1E benchmark runner."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from benchmarks.phase1e.constants import BENCHMARK_VERSION, RANDOM_SEED
from benchmarks.phase1e.evaluator import evaluate_suite
from benchmarks.phase1e.metrics import compute_metrics
from benchmarks.phase1e.report import render_report
from benchmarks.phase1e.scenarios import SCENARIOS

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "phase1e"


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


def comparable_payload(raw: dict[str, Any]) -> dict[str, Any]:
    """Strip run-specific metadata so two runs can be compared."""
    clone = json.loads(json.dumps(_jsonable(raw)))
    meta = clone.get("meta") or {}
    meta.pop("timestamp", None)
    clone["meta"] = meta
    return clone


def run_benchmark(*, persist: bool = True) -> dict[str, Any]:
    evaluation = evaluate_suite(SCENARIOS)
    metrics = compute_metrics(
        adapt_records=evaluation["adapt_records"],
        baseline_records=evaluation["baseline_records"],
        paired=evaluation["paired"],
        adapt_pairs=evaluation["adapt_pairs"],
        baseline_pairs=evaluation["baseline_pairs"],
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {
        "benchmark_version": BENCHMARK_VERSION,
        "random_seed": RANDOM_SEED,
        "timestamp": timestamp,
        "python_version": platform.python_version(),
        "git_commit": _git_commit(),
        "scenario_count": len(SCENARIOS),
        "platform": platform.platform(),
    }
    raw = {
        "meta": meta,
        "adapt_records": evaluation["adapt_records"],
        "baseline_records": evaluation["baseline_records"],
        "paired": [
            {
                "scenario_id": item["scenario_id"],
                "family": item["family"],
                "adapt": item["adapt"],
                "baseline": item["baseline"],
            }
            for item in evaluation["paired"]
        ],
        "adapt_pairs": evaluation["adapt_pairs"],
        "baseline_pairs": evaluation["baseline_pairs"],
    }
    report = render_report(
        meta=meta,
        metrics=metrics,
        paired=evaluation["paired"],
        adapt_pairs=evaluation["adapt_pairs"],
        baseline_pairs=evaluation["baseline_pairs"],
        adapt_records=evaluation["adapt_records"],
        baseline_records=evaluation["baseline_records"],
    )
    if persist:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        run_dir = RESULTS_DIR / "runs" / timestamp.replace(":", "")
        run_dir.mkdir(parents=True, exist_ok=True)
        for directory in (RESULTS_DIR, run_dir):
            (directory / "raw_results.json").write_text(
                json.dumps(_jsonable(raw), indent=2, sort_keys=True),
                encoding="utf-8",
            )
            (directory / "metrics.json").write_text(
                json.dumps(_jsonable({"meta": meta, **metrics}), indent=2, sort_keys=True),
                encoding="utf-8",
            )
            (directory / "report.md").write_text(report, encoding="utf-8")
    return {"meta": meta, "raw": raw, "metrics": metrics, "report": report, "evaluation": evaluation}


def print_summary(result: dict[str, Any]) -> None:
    metrics = result["metrics"]
    primary = metrics["primary"]
    print("========================================")
    print("ADAPT PHASE 1E BENCHMARK")
    print("========================================")
    print(f"Scenarios: {result['meta']['scenario_count']}")
    print(f"Seed: {result['meta']['random_seed']}")
    print(f"Version: {result['meta']['benchmark_version']}")
    print()
    print("ADAPT:")
    print(f"  Appropriateness: {primary['M-001_decision_appropriateness']['adapt']['display']}")
    print(f"  Counterfactual:  {primary['M-002_counterfactual_differentiation']['adapt']['display']}")
    print(f"  Traceability:    {primary['M-008_decision_traceability']['adapt']['display']}")
    print()
    print("BASELINE:")
    print(f"  Appropriateness: {primary['M-001_decision_appropriateness']['baseline']['display']}")
    print(f"  Counterfactual:  {primary['M-002_counterfactual_differentiation']['baseline']['display']}")
    print(f"  Traceability:    {primary['M-008_decision_traceability']['baseline']['display']}")
    print()
    print("COUNTERFACTUAL:")
    for item in result["raw"]["adapt_pairs"]:
        print(
            f"  ADAPT {item['pair_id']}: {item['decision_a']} vs {item['decision_b']} "
            f"diff={item['differentiated']}"
        )
    print()
    print("========================================")


def main() -> int:
    result = run_benchmark(persist=True)
    print_summary(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
