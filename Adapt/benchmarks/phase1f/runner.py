"""Phase 1F benchmark runner."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from benchmarks.phase1f.adversarial import run_adversarial
from benchmarks.phase1f.constants import BENCHMARK_VERSION, RANDOM_SEED
from benchmarks.phase1f.evaluator import evaluate_scenarios, make_pipeline
from benchmarks.phase1f.holdout import HOLDOUT_IDS
from benchmarks.phase1f.longitudinal import run_longitudinal
from benchmarks.phase1f.metamorphic import run_metamorphic
from benchmarks.phase1f.metrics import compute_metrics
from benchmarks.phase1f.report import render_report
from benchmarks.phase1f.scenarios import SCENARIOS, split_scenarios

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "phase1f"


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
    clone = json.loads(json.dumps(_jsonable(raw)))
    meta = clone.get("meta") or {}
    meta.pop("timestamp", None)
    clone["meta"] = meta
    return clone


def run_benchmark(*, persist: bool = True) -> dict[str, Any]:
    pipeline = make_pipeline()
    development_scenarios = split_scenarios("development")
    holdout_scenarios = split_scenarios("holdout")
    development = evaluate_scenarios(development_scenarios, pipeline)
    holdout = evaluate_scenarios(holdout_scenarios, pipeline)
    all_records = development + holdout
    metamorphic = run_metamorphic(pipeline)
    adversarial = run_adversarial(pipeline)
    longitudinal = run_longitudinal(pipeline)
    metrics = compute_metrics(
        development=development,
        holdout=holdout,
        all_records=all_records,
        metamorphic=metamorphic,
        adversarial=adversarial,
        longitudinal=longitudinal,
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {
        "benchmark_version": BENCHMARK_VERSION,
        "random_seed": RANDOM_SEED,
        "timestamp": timestamp,
        "python_version": platform.python_version(),
        "git_commit": _git_commit(),
        "scenario_count": len(SCENARIOS),
        "holdout_count": len(HOLDOUT_IDS),
        "platform": platform.platform(),
        "holdout_ids": sorted(HOLDOUT_IDS),
    }
    raw = {
        "meta": meta,
        "development": development,
        "holdout": holdout,
        "metamorphic": metamorphic,
        "adversarial": adversarial,
        "longitudinal": longitudinal,
    }
    report = render_report(
        meta=meta,
        metrics=metrics,
        development=development,
        holdout=holdout,
        all_records=all_records,
        metamorphic=metamorphic,
        adversarial=adversarial,
        longitudinal=longitudinal,
    )
    if persist:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        run_dir = RESULTS_DIR / "runs" / timestamp.replace(":", "")
        run_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "raw_results.json": raw,
            "metrics.json": {"meta": meta, **metrics},
            "development_results.json": {"meta": meta, "records": development},
            "holdout_results.json": {"meta": meta, "records": holdout},
        }
        for directory in (RESULTS_DIR, run_dir):
            for name, data in payload.items():
                (directory / name).write_text(
                    json.dumps(_jsonable(data), indent=2, sort_keys=True),
                    encoding="utf-8",
                )
            (directory / "report.md").write_text(report, encoding="utf-8")
    return {"meta": meta, "raw": raw, "metrics": metrics, "report": report}


def print_summary(result: dict[str, Any]) -> None:
    metrics = result["metrics"]
    gap = metrics.get("M-010_development_holdout_gap")
    gap_s = "n/a" if gap is None else f"{gap * 100:+.1f} pp"
    print("========================================")
    print("ADAPT PHASE 1F")
    print("ADAPTIVE STRESS & GENERALIZATION")
    print("========================================")
    print(f"Development scenarios: {metrics['counts']['development']}")
    print(f"Holdout scenarios: {metrics['counts']['holdout']}")
    print(f"Longitudinal trajectories: {metrics['counts']['longitudinal']}")
    print()
    print("Development performance:")
    print(f"  {metrics['M-001_development']['display']}")
    print()
    print("Holdout performance:")
    print(f"  {metrics['M-001_holdout']['display']}")
    print()
    print("Generalization gap:")
    print(f"  {gap_s}")
    print()
    print("Metamorphic tests:")
    print(f"  {metrics['metamorphic']['display']}")
    print()
    print("Adversarial tests:")
    print(f"  {metrics['adversarial']['display']}")
    print()
    print("State recovery:")
    print(f"  {metrics['M-011_state_recovery_rate']['display']}")
    print()
    print("Misconception persistence:")
    print(f"  {metrics['M-012_misconception_persistence_rate']['display']}")
    print()
    print("Overall result:")
    print(f"  {metrics['outcome_band']}")
    print("========================================")


def main() -> int:
    result = run_benchmark(persist=True)
    print_summary(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
