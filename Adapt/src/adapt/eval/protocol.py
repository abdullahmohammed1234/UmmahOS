"""Condition assignment and within-subject order. Frozen before analysis."""

from __future__ import annotations

import hashlib
from typing import Any

from adapt.eval.constants import CONDITIONS, RANDOM_SEED


def participant_index(participant_id: str) -> int:
    digits = "".join(ch for ch in participant_id if ch.isdigit())
    if digits:
        return int(digits)
    digest = hashlib.sha256(participant_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def assign_condition_order(participant_id: str, *, seed: int = RANDOM_SEED) -> list[str]:
    """Alternate ADAPT-first and BASELINE-first. Deterministic for a given id+seed."""
    index = participant_index(participant_id)
    mix = (index + int(seed)) % 2
    if mix == 1:
        return [CONDITIONS[0], CONDITIONS[1]]
    return [CONDITIONS[1], CONDITIONS[0]]


def assign_group(participant_id: str, *, seed: int = RANDOM_SEED) -> str:
    order = assign_condition_order(participant_id, seed=seed)
    return "group_1_adapt_first" if order[0] == "ADAPT" else "group_2_baseline_first"


def next_participant_id(existing: list[str]) -> str:
    used = set(existing)
    index = 1
    while True:
        candidate = f"P{index:03d}"
        if candidate not in used:
            return candidate
        index += 1


def assignment_record(participant_id: str, *, seed: int = RANDOM_SEED) -> dict[str, Any]:
    order = assign_condition_order(participant_id, seed=seed)
    return {
        "participant_id": participant_id,
        "seed": seed,
        "condition_order": order,
        "group": assign_group(participant_id, seed=seed),
        "design": "within_subject",
    }
