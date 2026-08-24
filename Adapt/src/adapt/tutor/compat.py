"""Strategy-to-challenge consistency checks for Phase 3."""

from __future__ import annotations

from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty, StrategyName, DIFFICULTY_ORDER
from adapt.models.learner_state import LearnerState

PROBE_TYPES = {ChallengeType.PROBE, ChallengeType.DIAGNOSTIC}
REMEDIATE_TYPES = {ChallengeType.REMEDIATION}
INCREASE_TYPES = {
    ChallengeType.INCREASED_DIFFICULTY,
    ChallengeType.PRACTICE,
    ChallengeType.STANDARD,
    ChallengeType.TRANSFER,
}
MAINTAIN_TYPES = {
    ChallengeType.PRACTICE,
    ChallengeType.STANDARD,
    ChallengeType.TRANSFER,
    ChallengeType.DIAGNOSTIC,
    ChallengeType.PROBE,
}
GATHER_TYPES = {
    ChallengeType.DIAGNOSTIC,
    ChallengeType.PROBE,
    ChallengeType.PRACTICE,
    ChallengeType.STANDARD,
}


def _rank(difficulty: Difficulty) -> int:
    return DIFFICULTY_ORDER.index(difficulty)


def challenge_compatible_with_strategy(
    *,
    strategy: StrategyName,
    challenge: Challenge,
    previous: Challenge | None,
    state: LearnerState | None = None,
) -> bool:
    """Return whether a selected challenge is a reasonable match for the strategy."""
    if not challenge.compatible_with(strategy.value):
        return False
    if strategy == StrategyName.PROBE:
        if challenge.challenge_type == ChallengeType.INCREASED_DIFFICULTY:
            return False
        if previous is not None and _rank(challenge.difficulty) > _rank(previous.difficulty) + 1:
            return False
        return True
    if strategy == StrategyName.GATHER_EVIDENCE or strategy == StrategyName.ASSESS:
        if challenge.challenge_type == ChallengeType.INCREASED_DIFFICULTY:
            return False
        if previous is not None and _rank(challenge.difficulty) > _rank(previous.difficulty) + 1:
            return False
        return challenge.challenge_type in GATHER_TYPES or challenge.diagnostic_value >= 0.4
    if strategy == StrategyName.REMEDIATE:
        if challenge.challenge_type in REMEDIATE_TYPES:
            return True
        if challenge.target_misconception:
            return True
        if state is not None:
            targets = {item.misconception_id for item in state.active_misconceptions}
            if challenge.target_misconception in targets:
                return True
        return challenge.challenge_type in {ChallengeType.DIAGNOSTIC, ChallengeType.PROBE}
    if strategy == StrategyName.INCREASE:
        if previous is None:
            return challenge.challenge_type in INCREASE_TYPES
        return _rank(challenge.difficulty) >= _rank(previous.difficulty) or challenge.challenge_type in {
            ChallengeType.INCREASED_DIFFICULTY,
            ChallengeType.TRANSFER,
        }
    if strategy == StrategyName.DECREASE:
        if previous is None:
            return True
        return _rank(challenge.difficulty) <= _rank(previous.difficulty) or challenge.challenge_type in REMEDIATE_TYPES
    if strategy in {StrategyName.MAINTAIN, StrategyName.RECOVER}:
        if previous is None:
            return challenge.challenge_type in MAINTAIN_TYPES
        return abs(_rank(challenge.difficulty) - _rank(previous.difficulty)) <= 1
    return True
