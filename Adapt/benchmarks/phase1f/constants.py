"""Phase 1F frozen constants. Do not change after holdout execution."""

from __future__ import annotations

BENCHMARK_VERSION = "phase1f-v1"
RANDOM_SEED = 20260813

CONSERVATIVE = (
    "MAINTAIN_DIFFICULTY",
    "PROBE_UNCERTAINTY",
    "GATHER_MORE_EVIDENCE",
)
REMEDIATE_FAMILY = (
    "REMEDIATE",
    "CHANGE_REPRESENTATION",
    "GATHER_MORE_EVIDENCE",
)
STRATEGY_CHANGE = (
    "CHANGE_REPRESENTATION",
    "GATHER_MORE_EVIDENCE",
    "DECREASE_DIFFICULTY",
    "REMEDIATE",
)
NO_ESCALATE = CONSERVATIVE + ("DECREASE_DIFFICULTY", "REMEDIATE", "CHANGE_REPRESENTATION")

# Frozen qualitative bands. Assigned after execution; not tuned afterward.
INTERPRETATION_BANDS = {
    "ROBUST": {
        "holdout_min": 0.80,
        "gap_max": 0.10,
        "metamorphic_min": 0.80,
        "adversarial_no_override": True,
        "recovery_min": 0.70,
    },
    "PARTIALLY_ROBUST": {
        "holdout_min": 0.65,
        "gap_max": 0.20,
    },
    "NOT_ROBUST": {
        "holdout_max": 0.50,
    },
}
