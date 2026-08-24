"""Diversity scoring among otherwise eligible challenges."""

from __future__ import annotations

from adapt.content.models import CatalogChallenge
from adapt.history.memory import ChallengeHistory

DIVERSITY_TYPES_CYCLE = (
    "DIRECT",
    "ERROR_ANALYSIS",
    "APPLICATION",
    "MULTIPLE_CHOICE",
    "TRANSFER",
    "PREDICTION",
    "CONCEPT_CHECK",
    "TRUE_FALSE",
    "COMPARE",
    "SCENARIO",
    "DIAGNOSTIC",
    "REMEDIATION",
    "EXPLANATION",
    "SEQUENCE",
    "NUMERIC",
    "SHORT_ANSWER",
    "DEBUG",
    "MATCH",
    "DIAGRAM",
    "ESTIMATION",
    "EXPLAIN_CHOICE",
)


def last_type(history: ChallengeHistory) -> str | None:
    if not history.attempts:
        return None
    return history.attempts[-1].challenge_type


def last_family(history: ChallengeHistory) -> str | None:
    if not history.attempts:
        return None
    return history.attempts[-1].family_id


def diversity_bonus(item: CatalogChallenge, history: ChallengeHistory) -> int:
    """Higher is more diverse relative to recent history."""
    bonus = 0
    recent_types = {attempt.challenge_type for attempt in history.recent(4)}
    recent_families = {attempt.family_id for attempt in history.recent(4)}
    recent_ids = {attempt.challenge_id for attempt in history.recent(8)}
    if item.challenge_type not in recent_types:
        bonus += 8
    elif last_type(history) != item.challenge_type:
        bonus += 4
    else:
        bonus -= 3
    if item.family not in recent_families:
        bonus += 6
    if item.id not in recent_ids:
        bonus += 4
    if item.representation and history.attempts:
        last = history.attempts[-1]
        if last.challenge_id != item.id:
            bonus += 2
    return bonus
