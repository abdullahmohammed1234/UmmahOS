"""Frozen Phase 3 expectations and holdout IDs.

Holdout IDs were chosen before implementation tuning and must not be edited
to chase holdout scores.
"""

from __future__ import annotations

HOLDOUT_IDS = frozenset(
    {
        "S-004",
        "S-008",
        "S-012",
        "S-018",
        "S-019",
        "S-020",
        "S-021",
        "S-022",
        "S-023",
        "S-024",
        "T-H-001",
        "T-H-002",
    }
)

COUNTERFACTUAL_PAIRS = (
    "P3-CF-001",
    "P3-CF-002",
    "P3-CF-003",
)

REQUIRED_TRAJECTORIES = (
    "T-001",
    "T-002",
    "T-003",
    "T-004",
    "T-005",
    "T-006",
)

TRACE_REQUIRED_FIELDS = (
    "challenge_id",
    "response",
    "evidence",
    "state_before",
    "state_after",
    "strategy_before",
    "strategy_after",
    "decision",
    "next_challenge_id",
)
