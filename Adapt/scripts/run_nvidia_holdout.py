"""Live NVIDIA holdout evaluation for Phase 12.

Runs frozen evidence_v3 holdout cases through the real NVIDIA API.
Does not re-run development prompt selection.
Does not call Gemini.
Does not overwrite historical offline simulator or Gemini artifacts.

python scripts/run_nvidia_holdout.py
python scripts/run_nvidia_holdout.py --probe
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adapt.eval.llm.criteria import prompt_score
from adapt.llm.config import load_nvidia_settings
from adapt.llm.errors import LLMError, LLMRateLimitError
from adapt.llm.fallback import SOURCE_FALLBACK, SOURCE_NVIDIA
from adapt.llm.nvidia import NvidiaClient, select_available_model
from adapt.llm.prompts import PROMPT_EXPERIMENT
from benchmarks.phase12.expected import BENCHMARK_VERSION, HOLDOUT_IDS, RANDOM_SEED, SCENARIO_VERSION
from benchmarks.phase12.metrics import compute_metrics
from benchmarks.phase12.runner import _annotate_pairs, run_workflow_scenario
from benchmarks.phase12.scenarios import SCENARIOS_BY_ID, holdout_scenarios

SELECTED_PROMPT = "evidence_v3"
OUT_DIR = ROOT / "results" / "phase12" / "live-nvidia-holdout"
PROBE_DIR = ROOT / "results" / "phase12" / "live-nvidia-probe"
# Evaluation-harness pacing only. Does not change NvidiaClient defaults or AdaptiveTutor.
# llama-3.3-70b evidence prompts are longer than the smoke ping and can exceed 60s under load.
TIMEOUT_FLOOR = 120.0
INTER_CALL_SLEEP = 12.0
RATE_LIMIT_WAIT_SECONDS = 70.0
RATE_LIMIT_EXTRA_ATTEMPTS = 1
STARTUP_COOLDOWN_SECONDS = 15.0
MAX_CONSECUTIVE_PROVIDER_FAILURES = 3
PROVIDER_STOP_CODES = {
    "LLM_RATE_LIMIT",
    "LLM_AUTHENTICATION_FAILURE",
}
_SECRET_RE = re.compile(r"nvapi-[A-Za-z0-9_-]+")

PROBE_IDS = (
    "A-010",  # lucky guess
    "B-010",  # strong correct reasoning
    "G-006",  # weak reasoning
    "D-009",  # misconception
    "E-009",  # uncertainty / ambiguous
    "J-008",  # injection resistance
)


class CountingNvidiaClient:
    """Live NVIDIA wrapper that counts calls. Does not alter generation."""

    provider = "nvidia"

    def __init__(self, inner: NvidiaClient, *, pause_s: float = INTER_CALL_SLEEP) -> None:
        self.inner = inner
        self.pause_s = pause_s
        self.calls = 0
        self.successes = 0
        self.failures = 0
        self.failure_codes: list[str] = []
        self.model = inner.model
        self.abort_reason: str | None = None

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
        self.abort_reason = "LLM_RATE_LIMIT"
        assert last_error is not None
        raise last_error


def _redact(value: Any, secret: str | None) -> Any:
    if isinstance(value, str):
        text = _SECRET_RE.sub("[REDACTED]", value)
        if secret:
            text = text.replace(secret, "[REDACTED]")
        return text
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
    out["nvidia_success"] = row.get("source") == SOURCE_NVIDIA and bool(row.get("validation_ok"))
    out["fallback"] = row.get("source") == SOURCE_FALLBACK
    out["included_in_primary_nvidia_score"] = bool(row.get("validation_ok")) and row.get("source") == SOURCE_NVIDIA
    out["final_evidence_source"] = row.get("source")
    return out


def _is_provider_failure(code: str | None) -> bool:
    if not code:
        return False
    return code.startswith("LLM_") and code != "LLM_VALIDATION_FAILURE"


def _resolve_model(settings) -> str:
    client = NvidiaClient(settings=settings, max_retries=1)
    try:
        available = client.list_models()
    except LLMError as exc:
        print(f"model catalog unavailable ({exc.code}); using configured model {settings.model}")
        return settings.model
    chosen = select_available_model(available, preferred=settings.model)
    if chosen:
        if chosen != settings.model:
            print(f"configured model={settings.model}; catalog selected={chosen}")
        return chosen
    return settings.model


def main() -> int:
    probe = "--probe" in sys.argv
    settings = load_nvidia_settings()
    if not settings.credentials_present:
        print("NVIDIA key detected: NO")
        print("Live NVIDIA evaluation cannot run.")
        return 2
    print("NVIDIA key detected: YES")
    timeout = max(float(settings.timeout_seconds), TIMEOUT_FLOOR)
    model = _resolve_model(settings)
    inner = NvidiaClient(settings=settings, model=model, timeout_seconds=timeout, max_retries=1)
    client = CountingNvidiaClient(inner)
    if probe:
        missing = [item for item in PROBE_IDS if item not in SCENARIOS_BY_ID]
        if missing:
            print(f"Probe IDs missing from frozen scenarios: {missing}")
            return 1
        cases = tuple(SCENARIOS_BY_ID[item] for item in PROBE_IDS)
        out_dir = PROBE_DIR
        label = "representative-probe"
    else:
        cases = holdout_scenarios()
        if len(cases) != 30:
            print(f"Expected 30 holdout scenarios, found {len(cases)}")
            return 1
        if {item.scenario_id for item in cases} != set(HOLDOUT_IDS):
            print("Holdout IDs do not match the frozen HOLDOUT_IDS set.")
            return 1
        out_dir = OUT_DIR
        label = "live-nvidia-holdout"

    print("provider: NVIDIA")
    print(f"model: {model}")
    print(f"configured_timeout_seconds: {settings.timeout_seconds}")
    print(f"evaluation_timeout_seconds: {timeout}")
    print(f"selected_prompt: {SELECTED_PROMPT}")
    print(f"holdout_identifier: {SCENARIO_VERSION} / frozen HOLDOUT_IDS")
    print(f"n: {len(cases)}")
    print("simulator: NOT USED")
    print("gemini: NOT USED")
    print("baseline live NVIDIA calls: NOT USED")
    print(
        f"startup cooldown {STARTUP_COOLDOWN_SECONDS:.0f}s to clear a rolling RPM window..."
    )
    time.sleep(STARTUP_COOLDOWN_SECONDS)
    print(f"starting {label}...")

    rows: list[dict[str, Any]] = []
    incomplete_reason: str | None = None
    consecutive_provider_failures = 0
    for index, scenario in enumerate(cases, start=1):
        print(
            f"[{index:02d}/{len(cases)}] workflow {scenario.scenario_id} family={scenario.family}",
            flush=True,
        )
        row = run_workflow_scenario(scenario, client=client, prompt_id=SELECTED_PROMPT)
        print(
            f"         source={row.get('source')} valid={row.get('validation_ok')} "
            f"extract={row.get('extraction_ok')} strategy={row.get('adapt_strategy')} "
            f"fail={row.get('failure_code')}",
            flush=True,
        )
        rows.append(row)
        code = row.get("failure_code")
        if _is_provider_failure(code):
            consecutive_provider_failures += 1
        else:
            consecutive_provider_failures = 0
        if code in PROVIDER_STOP_CODES or client.abort_reason:
            incomplete_reason = str(code or client.abort_reason)
            print(f"LIVE NVIDIA HOLDOUT: INCOMPLETE ({incomplete_reason})")
            break
        if consecutive_provider_failures >= MAX_CONSECUTIVE_PROVIDER_FAILURES:
            incomplete_reason = f"{consecutive_provider_failures} consecutive provider failures"
            print(f"LIVE NVIDIA HOLDOUT: INCOMPLETE ({incomplete_reason})")
            break

    _annotate_pairs(rows, cases)

    nvidia_cases = sum(1 for row in rows if row.get("source") == SOURCE_NVIDIA)
    fallback_cases = sum(1 for row in rows if row.get("source") == SOURCE_FALLBACK)
    validation_failures = sum(1 for row in rows if row.get("failure_code") == "LLM_VALIDATION_FAILURE")
    api_failures = sum(1 for row in rows if _is_provider_failure(row.get("failure_code")))
    strategy_from_engine = all(
        row.get("adapt_strategy") not in {None, ""}
        and not (row.get("llm_evidence") or {}).get("strategy")
        and not (row.get("llm_evidence") or {}).get("next_action")
        for row in rows
    ) if rows else False
    complete = incomplete_reason is None and len(rows) == len(cases)
    metrics = compute_metrics(rows, baseline_rows=[]) if rows else {}
    criteria = {
        "structured_output_validity": metrics.get("M12-002_structured_output_validity", {}).get("rate") or 0.0,
        "evidence_extraction_accuracy": metrics.get("M12-001_evidence_extraction_accuracy", {}).get("rate") or 0.0,
        "prompt_injection_robustness": metrics.get("M12-005_prompt_injection_robustness", {}).get("rate") or 0.0,
        "no_strategy_leakage": (
            0.0 if not rows else sum(1 for row in rows if not row.get("strategy_leak")) / len(rows)
        ),
        "counterfactual_sensitivity": metrics.get("M12-003_counterfactual_sensitivity", {}).get("rate") or 0.0,
    }
    now = datetime.now(timezone.utc)
    payload = {
        "meta": {
            "evaluation": label,
            "benchmark_version": BENCHMARK_VERSION,
            "scenario_version": SCENARIO_VERSION,
            "seed": RANDOM_SEED,
            "provider": "NVIDIA",
            "model": model,
            "backend": "nvidia",
            "simulator": False,
            "gemini": False,
            "prompt_id": SELECTED_PROMPT,
            "experiment": PROMPT_EXPERIMENT[SELECTED_PROMPT],
            "case_ids": [item.scenario_id for item in cases],
            "holdout_ids": sorted(HOLDOUT_IDS),
            "n_planned": len(cases),
            "n_completed": len(rows),
            "complete": complete,
            "incomplete_reason": incomplete_reason,
            "configured_timeout_seconds": settings.timeout_seconds,
            "evaluation_timeout_seconds": timeout,
            "temperature": settings.temperature,
            "timestamp": now.isoformat(),
            "nvidia_calls": client.calls,
            "nvidia_call_successes": client.successes,
            "nvidia_call_failures": client.failures,
            "nvidia_call_failure_codes": list(client.failure_codes),
            "live_baseline": False,
        },
        "metrics": metrics if complete else None,
        "criteria": criteria if complete else None,
        "score": prompt_score(criteria) if complete else None,
        "counts": {
            "cases_source_nvidia": nvidia_cases,
            "cases_source_fallback": fallback_cases,
            "validation_failures": validation_failures,
            "api_or_provider_failures": api_failures,
            "strategy_leak_cases": sum(1 for row in rows if row.get("strategy_leak")),
            "engine_owns_strategy": strategy_from_engine,
        },
        "rows": [_sanitize_row(row) for row in rows],
    }
    payload = _redact(payload, settings.api_key)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {out_dir / 'metrics.json'}")
    summary = {
        "complete": complete,
        "n_completed": len(rows),
        "n_planned": len(cases),
        "counts": payload["counts"],
        "calls": {
            "nvidia_calls": client.calls,
            "successes": client.successes,
            "failures": client.failures,
            "failure_codes": list(client.failure_codes),
        },
        "incomplete_reason": incomplete_reason,
    }
    if complete:
        summary["metrics"] = metrics
    else:
        print("LIVE NVIDIA HOLDOUT: INCOMPLETE")
        print("No full-holdout score is claimed.")
    print(json.dumps(summary, indent=2))
    return 0 if complete else 3


if __name__ == "__main__":
    raise SystemExit(main())
