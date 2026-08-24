"""Phase 5 evaluation runner.

python -m benchmarks.phase5.runner

Does not modify historical Phase 1E–4 artifacts. Does not fabricate humans.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapt.eval.constants import PLANNED_PARTICIPANTS, RANDOM_SEED
from adapt.eval.experiment import run_adapt_training
from adapt.eval.integrity import baseline_forbidden_imports
from adapt.eval.materials import assert_forms_frozen
from adapt.eval.metrics import comparison_table, compute_metrics
from adapt.eval.records import list_human_records
from adapt.eval.report import metric_markdown_table, render_report, simple_svg_bars, trajectory_table
from adapt.eval.scoring import paired_delta
from adapt.eval.synthetic import SYNTHETIC_CASES
from adapt.product.service import ProductService
from adapt.tutor.responses import build_scripted_response
from adapt.tutor.tutor import AdaptiveTutor, DEFAULT_SEED
from benchmarks.phase5.expected import BENCHMARK_VERSION, HISTORICAL_SHA256, SYNTHETIC_EXPECTED

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "phase5"


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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_historical_artifacts() -> dict[str, Any]:
    rows = []
    ok = True
    for relative, expected in HISTORICAL_SHA256.items():
        path = ROOT / relative
        exists = path.exists()
        digest = file_sha256(path) if exists else None
        match = exists and digest == expected
        if not match:
            ok = False
        rows.append(
            {
                "path": relative,
                "exists": exists,
                "sha256": digest,
                "expected": expected,
                "unchanged": match,
            }
        )
    return {"unchanged": ok, "files": rows}


def run_synthetic_validation() -> dict[str, Any]:
    cases = []
    all_pass = True
    for spec in SYNTHETIC_CASES:
        record = spec["record"]
        observed = paired_delta(record["adapt"]["gain"], record["baseline"]["gain"])
        expected = SYNTHETIC_EXPECTED[spec["id"]]
        passed = observed is not None and abs(observed - expected) < 1e-12
        if not passed:
            all_pass = False
        cases.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "expected_delta": expected,
                "observed_delta": observed,
                "passed": passed,
                "source": "synthetic",
            }
        )
    metrics = compute_metrics([item["record"] for item in SYNTHETIC_CASES], label="synthetic")
    return {"all_passed": all_pass, "cases": cases, "metrics": metrics, "table": comparison_table(metrics)}


def run_application_boundary() -> dict[str, Any]:
    """One full scripted participant-shaped flow through the Phase 4 product."""
    service = ProductService(seed=DEFAULT_SEED)
    kinds = ("strong_correct", "weak_correct", "misconception", "strong_correct")
    answers = []
    view = service.create_session(
        topic_id="algebra",
        learner_id="boundary-learner",
        session_id="P5-BOUNDARY-ALG",
        initial_challenge="ALG-D-001",
        max_steps=len(kinds),
    )
    chain_ok = True
    steps = []
    for kind in kinds:
        tutor_session = service.tutor.get_session(view["session_id"])
        challenge = tutor_session.current_challenge
        scripted = build_scripted_response(
            challenge,
            kind,
            learner_id="boundary-learner",
            response_id=f"P5-B-{len(steps)+1:03d}",
        )
        answers.append(
            {"answer": scripted.answer, "confidence": 4, "reasoning": scripted.reasoning}
        )
        result = service.submit_response(
            view["session_id"],
            answer=scripted.answer,
            confidence=4,
            reasoning=scripted.reasoning,
            challenge_id=challenge.challenge_id,
        )
        last = service.tutor.get_session(view["session_id"]).traces[-1]
        link_ok = bool(
            last.evidence
            and last.state_after
            and last.decision
            and last.next_challenge_id
            and result["research"]["next_challenge"]["challenge_id"] == last.next_challenge_id
        )
        chain_ok = chain_ok and link_ok
        steps.append(
            {
                "kind": kind,
                "challenge_id": last.challenge_id,
                "strategy": last.decision.value,
                "next_challenge_id": last.next_challenge_id,
                "complete_link": link_ok,
            }
        )
        view = service.get_session(view["session_id"])
    http_ok = "tested_in_pytest"
    adapt_batch = run_adapt_training(
        answers + answers,
        participant_id="P5-BOUNDARY",
        service=ProductService(seed=DEFAULT_SEED),
    )
    return {
        "tutor_class": type(service.tutor).__name__,
        "uses_adaptive_tutor": isinstance(service.tutor, AdaptiveTutor),
        "chain_ok": chain_ok,
        "http_ok": http_ok,
        "steps": steps,
        "adapt_batch_engine": adapt_batch["engine"],
        "baseline_forbidden_imports": baseline_forbidden_imports(),
    }


def human_reason(n: int) -> str:
    if n == 0:
        return (
            "No consented human participants were available during this automated "
            "execution. Missing participants remain missing."
        )
    if n < PLANNED_PARTICIPANTS:
        return (
            f"Only {n} consented human participant(s) were tested of {PLANNED_PARTICIPANTS} planned."
        )
    return "Planned sample was collected."


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fieldnames = [
        "participant_id",
        "source",
        "condition",
        "pre_score",
        "post_score",
        "gain",
        "training_score",
        "completed",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            pre = (record.get("pre_test") or {}).get("score")
            for condition in ("ADAPT", "BASELINE"):
                block = record.get(condition.lower()) or {}
                writer.writerow(
                    {
                        "participant_id": record.get("participant_id"),
                        "source": record.get("source"),
                        "condition": condition,
                        "pre_score": pre,
                        "post_score": block.get("post_test_score"),
                        "gain": block.get("gain"),
                        "training_score": block.get("training_score"),
                        "completed": block.get("completed"),
                    }
                )


def render_methodology() -> str:
    return """# Phase 5 methodology (frozen before human analysis)

## Design
Within-subject: pre-test → condition A → post-test A → condition B → post-test B.
Condition order is randomized by participant id and seed 20260814.
Group 1: ADAPT then BASELINE. Group 2: BASELINE then ADAPT.

## Conditions
- ADAPT: Phase 4 ProductService wrapping AdaptiveTutor. 4 algebra + 4 fractions steps.
- BASELINE: LinearTutor, frozen 8-item sequence, feedback after each item, no learner-state strategy.

## Scoring
Normalized exact match or listed alias. Missing answers score 0 with status MISSING.
gain = post_test_score - pre_test_score
delta = gain_ADAPT - gain_BASELINE

## Statistics
n < 1: INCONCLUSIVE.
1 ≤ n < 6: exploratory descriptive statistics only.
n ≥ 6: Wilcoxon signed-rank plus bootstrap 95% CI on mean delta; Cohen dz if sd > 0.

## Delayed retention
Optional. If not run: NOT COLLECTED.

## Synthetic data
SYN-A/B/C validate arithmetic of deltas. They are not human results.
"""


def render_limitations(n: int, historical_ok: bool) -> str:
    return f"""# Phase 5 limitations

- Planned participants: {PLANNED_PARTICIPANTS}. Actual human participants: {n}.
- {human_reason(n)}
- Delayed retention: NOT COLLECTED.
- Phase 4 formative usability remains PENDING (0 of 5). Phase 5 does not rewrite that fact.
- Short study duration; single-session learning.
- Order, practice, and form effects remain even with counterbalancing.
- Keyword/heuristic evidence analyzer is unchanged; conceptual recovery uses those standards.
- Baseline is a fair linear tutor, not AdaptiveTutor and not a strawman, but it is still simpler than a full curriculum.
- Interface: ADAPT uses the Phase 4 product; baseline is the same evaluation harness without strategy UI. Residual interface differences exist.
- Historical artifacts unchanged: {historical_ok}.
"""


def run_benchmark(*, persist: bool = True, seed: int = RANDOM_SEED) -> dict[str, Any]:
    assert_forms_frozen()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    historical = verify_historical_artifacts()
    synthetic = run_synthetic_validation()
    boundary = run_application_boundary()
    human_records = list_human_records()
    actual = len(human_records)
    human_metrics = compute_metrics(human_records, label="human")
    human_metrics["table"] = comparison_table(human_metrics)
    failures = []
    if not synthetic["all_passed"]:
        failures.append("synthetic validation mismatch")
    if not historical["unchanged"]:
        failures.append("historical artifact hash mismatch")
    if not boundary["chain_ok"]:
        failures.append("application boundary chain failed")
    if boundary["baseline_forbidden_imports"]:
        failures.append("baseline imports adaptive components")
    if not boundary["uses_adaptive_tutor"]:
        failures.append("ADAPT condition is not AdaptiveTutor")
    human_metrics["failures"] = "None recorded." if not failures else "; ".join(failures)
    report = render_report(
        human=human_metrics,
        synthetic=synthetic,
        human_records=human_records,
        planned=PLANNED_PARTICIPANTS,
        actual=actual,
        reason=human_reason(actual),
    )
    methodology = render_methodology()
    limitations = render_limitations(actual, historical["unchanged"])
    meta = {
        "benchmark_version": BENCHMARK_VERSION,
        "timestamp": timestamp,
        "seed": seed,
        "python_version": platform.python_version(),
        "git_commit": _git_commit(),
        "planned_participants": PLANNED_PARTICIPANTS,
        "actual_human_participants": actual,
        "synthetic_cases": len(SYNTHETIC_CASES),
        "design": "within_subject",
        "delayed_retention": "NOT COLLECTED",
        "phase4_usability_participants": "0 / 5 PENDING",
    }
    figures = {}
    syn_deltas = [
        (case["id"], float(case["observed_delta"] or 0.0)) for case in synthetic["cases"]
    ]
    figures["synthetic_deltas.svg"] = simple_svg_bars(
        "Synthetic paired deltas",
        syn_deltas,
        note="SYNTHETIC VALIDATION — NOT HUMAN DATA",
    )
    if actual:
        human_deltas = []
        for record in human_records:
            delta = paired_delta(
                (record.get("adapt") or {}).get("gain"),
                (record.get("baseline") or {}).get("gain"),
            )
            if delta is not None:
                human_deltas.append((record["participant_id"], delta))
        if human_deltas:
            figures["human_deltas.svg"] = simple_svg_bars(
                "Human paired deltas (ADAPT − baseline)",
                human_deltas,
                note="Exploratory. No significance implied.",
            )
    payload = {
        "meta": meta,
        "human": human_metrics,
        "synthetic": synthetic,
        "boundary": boundary,
        "historical": historical,
        "failures": failures,
        "report": report,
        "methodology": methodology,
        "limitations": limitations,
    }
    if persist:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "raw").mkdir(parents=True, exist_ok=True)
        run_dir = RESULTS_DIR / "runs" / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "raw" / "README.md").write_text(
            "# Raw human records\n\n"
            "One anonymized file per human participant (P001.json, …).\n"
            "Do not overwrite. Do not store names, emails, or student numbers.\n"
            "Synthetic cases are stored separately and are not human data.\n",
            encoding="utf-8",
        )
        files = {
            "raw_results.json": {
                "meta": meta,
                "human_records": human_records,
                "synthetic": synthetic,
                "boundary": boundary,
                "historical": historical,
            },
            "metrics.json": {
                "human": human_metrics,
                "synthetic": {k: synthetic[k] for k in ("all_passed", "cases", "table")},
            },
            "statistics.json": {
                "human": human_metrics.get("analysis"),
                "synthetic": synthetic["metrics"].get("analysis"),
                "interpretation": human_metrics.get("interpretation"),
            },
            "report.md": report,
            "methodology.md": methodology,
            "limitations.md": limitations,
        }
        for name, content in files.items():
            target = RESULTS_DIR / name
            run_target = run_dir / name
            if name.endswith(".md"):
                text = content if isinstance(content, str) else str(content)
                target.write_text(text, encoding="utf-8")
                run_target.write_text(text, encoding="utf-8")
            else:
                text = json.dumps(_jsonable(content), indent=2, sort_keys=True)
                target.write_text(text, encoding="utf-8")
                run_target.write_text(text, encoding="utf-8")
        write_csv(RESULTS_DIR / "participant_results.csv", human_records)
        write_csv(run_dir / "participant_results.csv", human_records)
        fig_dir = RESULTS_DIR / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        for name, svg in figures.items():
            (fig_dir / name).write_text(svg, encoding="utf-8")
            (run_dir / name).write_text(svg, encoding="utf-8")
        (RESULTS_DIR / "synthetic_validation.json").write_text(
            json.dumps(_jsonable(synthetic), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    return payload


def main() -> int:
    payload = run_benchmark(persist=True)
    sys.stdout.write(payload["report"])
    if payload["failures"]:
        sys.stderr.write("Phase 5 engineering checks failed: " + "; ".join(payload["failures"]) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
