"""Repetition policy for challenge selection. Does not change strategy."""

from __future__ import annotations

from adapt.history.memory import ChallengeHistory
from adapt.models.enums import StrategyName

RECENT_WINDOW = 8
HARD_WINDOW = 4
FAMILY_WINDOW = 6
TYPE_STREAK_LIMIT = 1
REPEAT_STRATEGIES = {StrategyName.REMEDIATE}


def repetition_allowed(strategy: StrategyName) -> bool:
    return strategy in REPEAT_STRATEGIES


def is_recent_repeat(
    challenge_id: str,
    history: ChallengeHistory,
    *,
    window: int = RECENT_WINDOW,
) -> bool:
    return history.recently_seen(challenge_id, window=window)


def is_family_repeat(
    family_id: str,
    history: ChallengeHistory,
    *,
    window: int = FAMILY_WINDOW,
) -> bool:
    return history.family_recent(family_id, window=window)


def is_consecutive_type(challenge_type: str, history: ChallengeHistory) -> bool:
    if not history.attempts:
        return False
    recent = history.recent(TYPE_STREAK_LIMIT)
    return bool(recent) and all(item.challenge_type == challenge_type for item in recent)


def recent_ids(history: ChallengeHistory, *, window: int = RECENT_WINDOW) -> list[str]:
    return [item.challenge_id for item in history.recent(window)]
