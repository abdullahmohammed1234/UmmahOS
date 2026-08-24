"""Live Gemini holdout evaluation for Phase 12.

Runs the frozen evidence_v3 holdout (n=30) through the real Gemini API.
Does not re-run development prompt selection.
Does not overwrite the historical offline simulator artifacts.

python scripts/run_gemini_holdout.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adapt.eval.llm.criteria import prompt_score
from adapt.llm.config import load_settings
from adapt.llm.errors import LLMError, LLMRateLimitError
from adapt.llm.fallback import SOURCE_FALLBACK, SOURCE_GEMINI
from adapt.llm.gemini import GeminiClient
from adapt.llm.prompts import PROMPT_EXPERIMENT
from benchmarks.phase12.expected import BENCHMARK_VERSION, HOLDOUT_IDS, RANDOM_SEED, SCENARIO_VERSION
from benchmarks.phase12.metrics import compute_metrics
from benchmarks.phase12.runner import _annotate_pairs, run_baseline_scenario, run_workflow_scenario
from benchmarks.phase12.scenarios import holdout_scenarios
from benchmarks.phase12.statistics import paired_binary_summary

SELECTED_PROMPT = "evidence_v3"
OUT_DIR = ROOT / "results" / "phase12" / "live-gemini-holdout"
TIMEOUT_FLOOR = 60.0
# Evaluation-harness pacing only. Does not change GeminiClient or AdaptiveTutor.
INTER_CALL_SLEEP = 8.0
RATE_LIMIT_WAIT_SECONDS = 70.0
# Stop quickly on sustained quota/rate-limit so evaluation does not spin.
RATE_LIMIT_EXTRA_ATTEMPTS = 1
STARTUP_COOLDOWN_SECONDS = 5.0


class CountingGeminiClient:
    """Live Gemini wrapper that counts calls. Does not alter generation."""

    provider = "gemini"

    def __init__(self, inner: GeminiClient, *, pause_s: float = INTER_CALL_SLEEP) -> None:
        self.inner = inner
        self.pause_s = pause_s
        self.calls = 0
        self.successes = 0
        self.failures = 0
        self.failure_codes: list[str] = []
        self.model = inner.model

    def available(self) -> bool:
        return self.inner.available()

    def generate(self, prompt: str, **kwargs):
        self.calls += 1
        if self.pause_s and self.calls > 1:
            time.sleep(self.pause_s)
        last_error: LLMError | None = None
        attempts = 1 + RATE_LIMIT_EXTRA_ATTEMPTS
        for attempt in range(attempts):
            try:
                result = self.inner.generate(prompt, **kwargs)
            except LLMRateLimitError as exc:
                last_error = exc
                if attempt >= attempts - 1:
                    break
                wait = RATE_LIMIT_WAIT_SECONDS * (1.0 + 0.15 * attempt)
                print(
                    f"         rate-limited; waiting {wait:.0f}s then retrying "
                    f"(harness attempt {attempt + 2}/{attempts})",
                    flush=True,
                )
                time.sleep(wait)
                continue
            except LLMError as exc:
                self.failures += 1
                self.failure_codes.append(getattr(exc, "code", type(exc).__name__))
                raise
            self.successes += 1
            return result
        self.failures += 1
        self.failure_codes.append("LLM_RATE_LIMIT")
        assert last_error is not None
        raise last_error


def _redact(value: Any, secret: str | None) -> Any:
    if not secret:
        return value
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]")
    if isinstance(value, dict):
        return {str(key): _redact(item, secret) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, secret) for item in value]
    return value


def _sanitize_workflow(workflow: dict[str, Any] | None) -> dict[str, Any] | None:
    if not workflow:
        return None
    cleaned = dict(workflow)
    cleaned.pop("raw_text", None)
    cleaned["raw_response_present"] = bool(workflow.get("raw_text"))
    return cleaned


def _sanitize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["workflow"] = _sanitize_workflow(row.get("workflow"))
    out["gemini_success"] = row.get("source") == SOURCE_GEMINI and bool(row.get("validation_ok"))
    out["fallback"] = row.get("source") == SOURCE_FALLBACK
    out["included_in_primary_gemini_score"] = bool(row.get("validation_ok")) and row.get("source") == SOURCE_GEMINI
    return out


def _sanitize_baseline(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    raw = out.get("raw")
    if isinstance(raw, dict):
        raw = dict(raw)
        raw.pop("raw_text", None)
        out["raw"] = raw
    return out


def main() -> int:
    settings = load_settings()
    if not settings.credentials_present:
        print("GEMINI_API_KEY detected: NO")
        print("Live holdout cannot run.")
        return 2
    print("GEMINI_API_KEY detected: YES")
    timeout = max(float(settings.timeout_seconds), TIMEOUT_FLOOR)
    client = CountingGeminiClient(
        GeminiClient(settings=settings, timeout_seconds=timeout, max_retries=1)
    )
    holdout = holdout_scenarios()
    if len(holdout) != 30:
        print(f"Expected 30 holdout scenarios, found {len(holdout)}")
        return 1
    if {item.scenario_id for item in holdout} != set(HOLDOUT_IDS):
        print("Holdout IDs do not match the frozen HOLDOUT_IDS set.")
        return 1

    print("provider: Gemini")
    print(f"model: {settings.model}")
    print(f"configured_timeout_seconds: {settings.timeout_seconds}")
    print(f"evaluation_timeout_seconds: {timeout}")
    print(f"selected_prompt: {SELECTED_PROMPT}")
    print(f"holdout_identifier: {SCENARIO_VERSION} / frozen HOLDOUT_IDS")
    print(f"holdout_n: {len(holdout)}")
    print("simulator: NOT USED")
    print(
        f"startup cooldown {STARTUP_COOLDOWN_SECONDS:.0f}s to clear a rolling RPM window..."
    )
    time.sleep(STARTUP_COOLDOWN_SECONDS)
    print("starting live holdout...")

    rows: list[dict[str, Any]] = []
    for index, scenario in enumerate(holdout, start=1):
        print(f"[{index:02d}/30] workflow {scenario.scenario_id} family={scenario.family}", flush=True)
        row = run_workflow_scenario(scenario, client=client, prompt_id=SELECTED_PROMPT)
        print(
            f"         source={row.get('source')} valid={row.get('validation_ok')} "
            f"extract={row.get('extraction_ok')} strategy={row.get('adapt_strategy')} "
            f"fail={row.get('failure_code')}",
            flush=True,
        )
        rows.append(row)

    _annotate_pairs(rows, holdout)

    baseline_rows: list[dict[str, Any]] = []
    for index, scenario in enumerate(holdout, start=1):
        print(f"[{index:02d}/30] baseline {scenario.scenario_id}", flush=True)
        baseline_rows.append(run_baseline_scenario(scenario, client=client))

    metrics = compute_metrics(rows, baseline_rows=baseline_rows)
    paired = paired_binary_summary(
        [bool(row.get("adapt_appropriate")) for row in rows],
        [bool(row.get("baseline_appropriate")) for row in baseline_rows],
    )
    gemini_cases = sum(1 for row in rows if row.get("source") == SOURCE_GEMINI)
    fallback_cases = sum(1 for row in rows if row.get("source") == SOURCE_FALLBACK)
    validation_failures = sum(1 for row in rows if row.get("failure_code") == "LLM_VALIDATION_FAILURE")
    api_failures = sum(
        1
        for row in rows
        if (row.get("failure_code") or "").startswith("LLM_")
        and row.get("failure_code") != "LLM_VALIDATION_FAILURE"
    )
    strategy_from_engine = all(
        row.get("adapt_strategy") not in {None, ""}
        and not (row.get("llm_evidence") or {}).get("strategy")
        and not (row.get("llm_evidence") or {}).get("next_action")
        for row in rows
    )
    criteria = {
        "structured_output_validity": metrics["M12-002_structured_output_validity"]["rate"] or 0.0,
        "evidence_extraction_accuracy": metrics["M12-001_evidence_extraction_accuracy"]["rate"] or 0.0,
        "prompt_injection_robustness": metrics["M12-005_prompt_injection_robustness"]["rate"] or 0.0,
        "no_strategy_leakage": sum(1 for row in rows if not row.get("strategy_leak")) / len(rows),
        "counterfactual_sensitivity": metrics["M12-003_counterfactual_sensitivity"]["rate"] or 0.0,
    }
    now = datetime.now(timezone.utc)
    payload = {
        "meta": {
            "evaluation": "live-gemini-holdout",
            "benchmark_version": BENCHMARK_VERSION,
            "scenario_version": SCENARIO_VERSION,
            "seed": RANDOM_SEED,
            "provider": "Gemini",
            "model": settings.model,
            "backend": "gemini",
            "simulator": False,
            "prompt_id": SELECTED_PROMPT,
            "experiment": PROMPT_EXPERIMENT[SELECTED_PROMPT],
            "holdout_ids": sorted(HOLDOUT_IDS),
            "n": len(holdout),
            "configured_timeout_seconds": settings.timeout_seconds,
            "evaluation_timeout_seconds": timeout,
            "temperature": settings.temperature,
            "timestamp": now.isoformat(),
            "gemini_calls": client.calls,
            "gemini_call_successes": client.successes,
            "gemini_call_failures": client.failures,
            "gemini_call_failure_codes": list(client.failure_codes),
        },
        "metrics": metrics,
        "criteria": criteria,
        "score": prompt_score(criteria),
        "paired": paired,
        "counts": {
            "cases_source_gemini": gemini_cases,
            "cases_source_fallback": fallback_cases,
            "validation_failures": validation_failures,
            "api_or_provider_failures": api_failures,
            "strategy_leak_cases": sum(1 for row in rows if row.get("strategy_leak")),
            "engine_owns_strategy": strategy_from_engine,
        },
        "rows": [_sanitize_row(row) for row in rows],
        "baseline_rows": [_sanitize_baseline(row) for row in baseline_rows],
    }
    payload = _redact(payload, settings.api_key)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUT_DIR / 'metrics.json'}")
    print(json.dumps({"metrics": metrics, "counts": payload["counts"], "paired": paired, "calls": payload["meta"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
