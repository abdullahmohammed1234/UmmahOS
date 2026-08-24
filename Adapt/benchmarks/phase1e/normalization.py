"""Decision normalization for Phase 1E.

Rules are frozen. Equivalent phrasing maps to the canonical vocabulary.
Unknown strings are NOT coerced into a convenient canonical label.
"""

from __future__ import annotations

from adapt.models.enums import AdaptationAction
from benchmarks.phase1e.constants import CANONICAL_DECISIONS

# Frozen normalization table. Only exact, documented aliases are mapped.
_ALIASES: dict[str, str] = {
    "INCREASE_DIFFICULTY": "INCREASE_DIFFICULTY",
    "MAKE HARDER": "INCREASE_DIFFICULTY",
    "MAKE_HARDER": "INCREASE_DIFFICULTY",
    "INCREASE DIFFICULTY": "INCREASE_DIFFICULTY",
    "HARDER": "INCREASE_DIFFICULTY",
    "ADVANCE": "INCREASE_DIFFICULTY",
    "MAINTAIN_DIFFICULTY": "MAINTAIN_DIFFICULTY",
    "MAINTAIN DIFFICULTY": "MAINTAIN_DIFFICULTY",
    "KEEP DIFFICULTY": "MAINTAIN_DIFFICULTY",
    "SAME DIFFICULTY": "MAINTAIN_DIFFICULTY",
    "DECREASE_DIFFICULTY": "DECREASE_DIFFICULTY",
    "MAKE EASIER": "DECREASE_DIFFICULTY",
    "MAKE_EASIER": "DECREASE_DIFFICULTY",
    "DECREASE DIFFICULTY": "DECREASE_DIFFICULTY",
    "EASIER": "DECREASE_DIFFICULTY",
    "REMEDIATE": "REMEDIATE",
    "REMEDIATE MISCONCEPTION": "REMEDIATE",
    "TARGETED REMEDIATION": "REMEDIATE",
    "PROBE_UNCERTAINTY": "PROBE_UNCERTAINTY",
    "PROBE UNCERTAINTY": "PROBE_UNCERTAINTY",
    "DIAGNOSTIC": "PROBE_UNCERTAINTY",
    "CHANGE_REPRESENTATION": "CHANGE_REPRESENTATION",
    "CHANGE REPRESENTATION": "CHANGE_REPRESENTATION",
    "ALTERNATIVE REPRESENTATION": "CHANGE_REPRESENTATION",
    "GATHER_MORE_EVIDENCE": "GATHER_MORE_EVIDENCE",
    "GATHER MORE EVIDENCE": "GATHER_MORE_EVIDENCE",
    "ASK ANOTHER DIAGNOSTIC QUESTION": "GATHER_MORE_EVIDENCE",
    "COLLECT MORE EVIDENCE": "GATHER_MORE_EVIDENCE",
}


def normalize_decision(value: object) -> str:
    """Convert a system output into a canonical decision label.

    Returns one of the frozen canonical decisions, or ``UNMAPPED:<original>``
    when the value is not in the documented alias table.
    """
    if isinstance(value, AdaptationAction):
        return value.value
    if value is None:
        return "UNMAPPED:None"
    text = str(value).strip().upper().replace("-", "_")
    collapsed = " ".join(text.replace("_", " ").split())
    underscore = collapsed.replace(" ", "_")
    if underscore in CANONICAL_DECISIONS:
        return underscore
    if text in _ALIASES:
        return _ALIASES[text]
    if collapsed in _ALIASES:
        return _ALIASES[collapsed]
    if underscore in _ALIASES:
        return _ALIASES[underscore]
    return f"UNMAPPED:{value}"
