"""Statistical helpers for Phase 1E. Deterministic. No optional dependencies."""

from __future__ import annotations

import math
from typing import Any

Z_95 = 1.959963984540054


def wilson_interval(successes: int, n: int, z: float = Z_95) -> tuple[float, float] | None:
    """95% Wilson score interval for a binomial proportion.

    Returns None when n == 0. Bounds are clamped to [0, 1].
    """
    if n <= 0:
        return None
    if successes < 0 or successes > n:
        raise ValueError("successes must be in [0, n]")
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    margin = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n) / denom
    low = max(0.0, center - margin)
    high = min(1.0, center + margin)
    return (low, high)


def percentage_point_difference(adapt_rate: float | None, baseline_rate: float | None) -> float | None:
    if adapt_rate is None or baseline_rate is None:
        return None
    return (adapt_rate - baseline_rate) * 100.0


def relative_improvement(adapt_rate: float | None, baseline_rate: float | None) -> float | None:
    """(ADAPT - baseline) / baseline. None when baseline is 0 or either rate is missing."""
    if adapt_rate is None or baseline_rate is None:
        return None
    if baseline_rate == 0:
        return None
    return (adapt_rate - baseline_rate) / baseline_rate


def chi_square_sf_df1(stat: float) -> float:
    """Survival function P(X > stat) for chi-square with 1 degree of freedom."""
    if stat <= 0:
        return 1.0
    return math.erfc(math.sqrt(stat / 2.0))


def mcnemar_test(n10: int, n01: int, continuity_correction: bool = True) -> dict[str, Any]:
    """McNemar test on discordant paired binary outcomes.

    n10: ADAPT appropriate, baseline not
    n01: baseline appropriate, ADAPT not
    """
    discordant = n10 + n01
    if discordant == 0:
        return {
            "n10": n10,
            "n01": n01,
            "statistic": 0.0,
            "p_value": 1.0,
            "note": "no discordant pairs",
        }
    diff = abs(n10 - n01)
    if continuity_correction:
        diff = max(0.0, diff - 1.0)
    stat = (diff * diff) / discordant
    return {
        "n10": n10,
        "n01": n01,
        "statistic": stat,
        "p_value": chi_square_sf_df1(stat),
        "continuity_correction": continuity_correction,
        "note": "descriptive prototype p-value; do not treat as confirmatory",
    }


def rate_payload(successes: int, n: int) -> dict[str, Any]:
    if n <= 0:
        return {
            "numerator": successes,
            "denominator": 0,
            "rate": None,
            "display": "n/a",
            "wilson_95": None,
        }
    rate = successes / n
    interval = wilson_interval(successes, n)
    display = f"{successes} / {n} = {rate * 100:.1f}%"
    wilson_display = None
    if interval is not None:
        wilson_display = [round(interval[0], 4), round(interval[1], 4)]
    return {
        "numerator": successes,
        "denominator": n,
        "rate": rate,
        "display": display,
        "wilson_95": wilson_display,
    }
