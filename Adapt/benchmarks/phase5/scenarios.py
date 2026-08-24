"""Phase 5 synthetic and protocol scenarios."""

from __future__ import annotations

from adapt.eval.synthetic import SYNTHETIC_CASES

SCRIPT_ADAPT_FLOW = (
    {"kind": "strong_correct"},
    {"kind": "strong_correct"},
    {"kind": "misconception"},
    {"kind": "strong_correct"},
    {"kind": "strong_correct"},
    {"kind": "misconception"},
    {"kind": "strong_correct"},
    {"kind": "strong_correct"},
)

__all__ = ["SCRIPT_ADAPT_FLOW", "SYNTHETIC_CASES"]
