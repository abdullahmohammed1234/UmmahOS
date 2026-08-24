"""Phase 5 statistics. Methods frozen before inspecting human outcomes.

Small samples: descriptive statistics first. Do not treat p-values as confirmatory.
"""

from __future__ import annotations

import math
import random
from typing import Any

from adapt.eval.constants import (
    MIN_N_FOR_EXPLORATORY_DIRECTION,
    MIN_N_FOR_INFERENCE,
    SMALL_SAMPLE_NOTE,
)
from adapt.eval.scoring import paired_delta

Z_95 = 1.959963984540054


def _clean(values: list[float | None]) -> list[float]:
    return [float(item) for item in values if item is not None]


def mean(values: list[float | None]) -> float | None:
    data = _clean(values)
    if not data:
        return None
    return sum(data) / len(data)


def median(values: list[float | None]) -> float | None:
    data = sorted(_clean(values))
    if not data:
        return None
    mid = len(data) // 2
    if len(data) % 2:
        return data[mid]
    return (data[mid - 1] + data[mid]) / 2.0


def stdev(values: list[float | None], *, sample: bool = True) -> float | None:
    data = _clean(values)
    n = len(data)
    if n == 0:
        return None
    if n == 1:
        return 0.0 if not sample else None
    avg = sum(data) / n
    denom = n - 1 if sample else n
    variance = sum((item - avg) ** 2 for item in data) / denom
    return math.sqrt(variance)


def cohen_dz(deltas: list[float | None]) -> float | None:
    """Paired effect size: mean(delta) / sd(delta). Undefined for n<2."""
    data = _clean(deltas)
    spread = stdev(data)
    avg = mean(data)
    if spread is None or avg is None or spread == 0:
        return None
    return avg / spread


def bootstrap_mean_ci(
    values: list[float | None],
    *,
    seed: int,
    n_boot: int = 2000,
) -> tuple[float, float] | None:
    data = _clean(values)
    if len(data) < 2:
        return None
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        sample = [data[rng.randrange(len(data))] for _ in range(len(data))]
        means.append(sum(sample) / len(sample))
    means.sort()
    low_i = int(0.025 * (n_boot - 1))
    high_i = int(0.975 * (n_boot - 1))
    return (means[low_i], means[high_i])


def wilcoxon_signed_rank(deltas: list[float | None]) -> dict[str, Any]:
    """Descriptive Wilcoxon signed-rank. Not used as a fishing expedition."""
    nonzero = [item for item in _clean(deltas) if item != 0]
    n = len(nonzero)
    if n == 0:
        return {
            "n": 0,
            "W": None,
            "note": "no non-zero paired differences",
            "confirmatory": False,
        }
    ranked = sorted(range(n), key=lambda i: abs(nonzero[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(nonzero[ranked[j + 1]]) == abs(nonzero[ranked[i]]):
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[ranked[k]] = avg_rank
        i = j + 1
    w_pos = sum(ranks[i] for i in range(n) if nonzero[i] > 0)
    w_neg = sum(ranks[i] for i in range(n) if nonzero[i] < 0)
    w = min(w_pos, w_neg)
    return {
        "n": n,
        "W": w,
        "W_positive": w_pos,
        "W_negative": w_neg,
        "note": SMALL_SAMPLE_NOTE if n < MIN_N_FOR_INFERENCE else "paired Wilcoxon signed-rank",
        "confirmatory": n >= MIN_N_FOR_INFERENCE,
    }


def interpret_h1(deltas: list[float | None], *, n_human: int) -> dict[str, Any]:
    """Frozen decision rule. Do not alter after seeing outcomes."""
    data = _clean(deltas)
    if n_human < MIN_N_FOR_EXPLORATORY_DIRECTION:
        return {
            "h1": "INCONCLUSIVE",
            "reason": "No human participants were tested.",
            "exploratory": True,
        }
    if n_human < MIN_N_FOR_INFERENCE:
        avg = mean(data)
        med = median(data)
        if data and all(item > 0 for item in data) and avg is not None and avg > 0:
            verdict = "SUPPORTED"
            reason = (
                "All paired deltas favor ADAPT in this exploratory sample. "
                "This is not confirmatory."
            )
        elif data and all(item < 0 for item in data) and avg is not None and avg < 0:
            verdict = "NOT SUPPORTED"
            reason = "All paired deltas favor baseline in this exploratory sample."
        elif avg is None:
            verdict = "INCONCLUSIVE"
            reason = "Paired gains are missing."
        else:
            verdict = "INCONCLUSIVE"
            reason = (
                "The exploratory sample does not show a consistent paired direction. "
                + SMALL_SAMPLE_NOTE
            )
        _ = med
        return {"h1": verdict, "reason": reason, "exploratory": True}
    avg = mean(data)
    med = median(data)
    ci = bootstrap_mean_ci(data, seed=20260814)
    if avg is None or med is None or ci is None:
        return {
            "h1": "INCONCLUSIVE",
            "reason": "Insufficient paired values for the pre-specified inferential rule.",
            "exploratory": False,
        }
    if med > 0 and ci[0] > 0:
        return {
            "h1": "SUPPORTED",
            "reason": "Median paired delta > 0 and bootstrap 95% CI excludes 0.",
            "exploratory": False,
        }
    if med < 0 and ci[1] < 0:
        return {
            "h1": "NOT SUPPORTED",
            "reason": "Median paired delta < 0 and bootstrap 95% CI excludes 0.",
            "exploratory": False,
        }
    return {
        "h1": "INCONCLUSIVE",
        "reason": "The pre-specified interval does not exclude no difference.",
        "exploratory": False,
    }


def summarize_numeric(values: list[float | None]) -> dict[str, Any]:
    data = _clean(values)
    return {
        "n": len(data),
        "mean": mean(data),
        "median": median(data),
        "stdev": stdev(data),
        "values": data,
    }


def analyze_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    gains_adapt: list[float | None] = []
    gains_base: list[float | None] = []
    deltas: list[float | None] = []
    pre_scores: list[float | None] = []
    post_adapt: list[float | None] = []
    post_base: list[float | None] = []
    recover_adapt: list[float | None] = []
    recover_base: list[float | None] = []
    survey_adapt: dict[str, list[float | None]] = {
        "perceived_adaptiveness": [],
        "challenge_appropriateness": [],
        "explanation_clarity": [],
        "learning_helpfulness": [],
        "would_use_again": [],
    }
    survey_base = {key: [] for key in survey_adapt}
    completed_adapt = 0
    completed_base = 0
    dropout_adapt = 0
    dropout_base = 0

    for record in records:
        pre = (record.get("pre_test") or {}).get("score")
        pre_scores.append(pre)
        adapt = record.get("adapt") or {}
        base = record.get("baseline") or {}
        gains_adapt.append(adapt.get("gain"))
        gains_base.append(base.get("gain"))
        deltas.append(paired_delta(adapt.get("gain"), base.get("gain")))
        post_adapt.append(adapt.get("post_test_score"))
        post_base.append(base.get("post_test_score"))
        rec_a = (adapt.get("misconception_recovery") or {}).get("rate")
        rec_b = (base.get("misconception_recovery") or {}).get("rate")
        recover_adapt.append(rec_a)
        recover_base.append(rec_b)
        if adapt.get("completed"):
            completed_adapt += 1
        if adapt.get("dropout"):
            dropout_adapt += 1
        if base.get("completed"):
            completed_base += 1
        if base.get("dropout"):
            dropout_base += 1
        for key in survey_adapt:
            survey_adapt[key].append((adapt.get("survey") or {}).get(key))
            survey_base[key].append((base.get("survey") or {}).get(key))

    n = len(records)
    interpretation = interpret_h1(deltas, n_human=n)
    return {
        "n": n,
        "pre_test": summarize_numeric(pre_scores),
        "post_test_adapt": summarize_numeric(post_adapt),
        "post_test_baseline": summarize_numeric(post_base),
        "gain_adapt": summarize_numeric(gains_adapt),
        "gain_baseline": summarize_numeric(gains_base),
        "delta": {
            **summarize_numeric(deltas),
            "cohen_dz": cohen_dz(deltas),
            "bootstrap_ci_95": bootstrap_mean_ci(deltas, seed=20260814),
            "wilcoxon": wilcoxon_signed_rank(deltas),
        },
        "misconception_recovery_adapt": summarize_numeric(recover_adapt),
        "misconception_recovery_baseline": summarize_numeric(recover_base),
        "survey_adapt": {key: summarize_numeric(vals) for key, vals in survey_adapt.items()},
        "survey_baseline": {key: summarize_numeric(vals) for key, vals in survey_base.items()},
        "session_completion_adapt": completed_adapt,
        "session_completion_baseline": completed_base,
        "dropout_adapt": dropout_adapt,
        "dropout_baseline": dropout_base,
        "interpretation": interpretation,
        "method": {
            "design": "within_subject",
            "primary_metric": "paired delta = gain_ADAPT - gain_BASELINE",
            "inferential": (
                "Wilcoxon signed-rank + bootstrap CI on mean delta "
                f"only if n>={MIN_N_FOR_INFERENCE}"
            ),
            "effect_size": "Cohen dz for paired deltas when n>=2 and sd>0",
            "small_sample": SMALL_SAMPLE_NOTE,
        },
    }
