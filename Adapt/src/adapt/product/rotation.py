"""Product-level challenge rotation. Presentation/selection policy only.

Does not choose strategy. AdaptiveTutor remains the source of the decision.
The selector uses this policy to prefer a different challenge when several
eligible items exist.
"""

from __future__ import annotations

from adapt.history.memory import ChallengeHistory
from adapt.models.enums import StrategyName
from adapt.selection.repetition import (
    FAMILY_WINDOW,
    HARD_WINDOW,
    RECENT_WINDOW,
    TYPE_STREAK_LIMIT,
    is_consecutive_type,
    is_family_repeat,
    is_recent_repeat,
    recent_ids,
    repetition_allowed,
)

POLICY = {
    "same_challenge": f"avoid within the last {RECENT_WINDOW} challenges",
    "same_concept": "allowed",
    "same_type": f"avoid more than {TYPE_STREAK_LIMIT} consecutive repeats when alternatives exist",
    "same_wording": "avoid by treating identical ids as repeats",
    "same_concept_different_representation": "preferred",
    "repeat_when": (
        "the eligible bank is exhausted, the strategy is REMEDIATE, "
        "or the strategy explicitly allows repetition"
    ),
}


def should_avoid_repeat(strategy: StrategyName) -> bool:
    return not repetition_allowed(strategy)


def filter_repeats(
    candidates: list,
    history: ChallengeHistory,
    *,
    strategy: StrategyName,
    current_id: str | None = None,
) -> list:
    """Drop recently shown items unless repetition is required or the bank is empty."""
    if not candidates:
        return []
    if repetition_allowed(strategy):
        return list(candidates)
    remaining = [
        item
        for item in candidates
        if not is_recent_repeat(getattr(item, "id", item), history, window=HARD_WINDOW)
        and getattr(item, "id", item) != current_id
    ]
    if remaining:
        candidates = remaining
    remaining = [
        item
        for item in candidates
        if not is_family_repeat(getattr(item, "family", getattr(item, "id", "")), history)
    ]
    if remaining:
        candidates = remaining
    remaining = [item for item in candidates if not is_consecutive_type(getattr(item, "challenge_type", ""), history)]
    if remaining:
        candidates = remaining
    return list(candidates)


def session_recent_ids(history: ChallengeHistory) -> list[str]:
    return recent_ids(history, window=RECENT_WINDOW)


__all__ = [
    "FAMILY_WINDOW",
    "POLICY",
    "RECENT_WINDOW",
    "TYPE_STREAK_LIMIT",
    "filter_repeats",
    "session_recent_ids",
    "should_avoid_repeat",
]
