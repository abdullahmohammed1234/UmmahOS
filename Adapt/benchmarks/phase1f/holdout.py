"""Frozen holdout IDs. Do not change after inspecting holdout results."""

from __future__ import annotations

# 18 / 60 = 30%. Chosen before execution. Spans all 15 families (D variants)
# plus three extra high-dimension families.
HOLDOUT_IDS: frozenset[str] = frozenset(
    {
        "G-001-D",
        "G-002-D",
        "G-003-D",
        "G-004-D",
        "G-005-D",
        "G-006-D",
        "G-007-D",
        "G-008-D",
        "G-009-D",
        "G-010-D",
        "G-011-D",
        "G-012-D",
        "G-013-D",
        "G-014-D",
        "G-015-D",
        "G-005-C",
        "G-007-C",
        "G-012-C",
    }
)
