"""Phase 4 benchmark constants and targets. Frozen before execution."""

from __future__ import annotations

BENCHMARK_VERSION = "phase4-v1"
RANDOM_SEED = 20260814

TARGETS = {
    "M4-001": 0.95,
    "M4-002": 1.0,
    "M4-003": 1.0,
    "M4-004": 1.0,
    "M4-005": 1.0,
}

MIN_SESSIONS = 20
MIN_STEPS = 100
MIN_COUNTERFACTUALS = 5
MIN_RECOVERY = 5
MIN_MISCONCEPTION = 5
