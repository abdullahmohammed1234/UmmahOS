"""Phase 3 challenge selector.

Consumes the strategy decision. Does not pick difficulty independently of strategy.
"""

from __future__ import annotations

from adapt.adaptation.challenge_selector import ChallengeSelector, _shift_difficulty
from adapt.errors import InvalidAdaptationDecisionError, InvalidChallengeError
from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.challenge import Challenge
from adapt.models.enums import (
    AdaptationAction,
    ChallengeType,
    Difficulty,
    StrategyName,
)
from adapt.models.learner_state import LearnerState
from adapt.models.strategy import STRATEGY_TO_ACTION

ACTION_TO_STRATEGY = {action: name for name, action in STRATEGY_TO_ACTION.items()}
ACTION_TO_STRATEGY[AdaptationAction.CHANGE_REPRESENTATION] = StrategyName.REMEDIATE
ACTION_TO_STRATEGY[AdaptationAction.PROBE_UNCERTAINTY] = StrategyName.PROBE
ACTION_TO_STRATEGY[AdaptationAction.GATHER_MORE_EVIDENCE] = StrategyName.GATHER_EVIDENCE

PRACTICE_LIKE = {ChallengeType.PRACTICE, ChallengeType.STANDARD}
PROBE_LIKE = {ChallengeType.PROBE, ChallengeType.DIAGNOSTIC}


def _pick_ranked(
    candidates: list[Challenge],
    *,
    current_id: str | None,
    used_ids: set[str],
    prefer_information: bool,
    allow_repeat: bool,
) -> Challenge | None:
    if not candidates:
        return None
    unused = [item for item in candidates if item.challenge_id not in used_ids]
    if unused:
        pool = unused
    elif allow_repeat:
        pool = list(candidates)
    else:
        pool = [item for item in candidates if item.challenge_id not in used_ids] or list(candidates)
    different = [item for item in pool if item.challenge_id != current_id]
    pool = different or pool
    if prefer_information:
        pool = sorted(pool, key=lambda item: (-float(item.diagnostic_value), item.challenge_id))
    return pool[0] if pool else None


class AdaptiveChallengeSelector(ChallengeSelector):
    """Selects the next challenge from strategy, learner state, and history."""

    def select(
        self,
        decision: AdaptationDecision,
        state: LearnerState,
        current_challenge: Challenge | None,
        used_challenge_ids: list[str] | None = None,
        strategy_name: StrategyName | None = None,
    ) -> Challenge:
        if current_challenge is None:
            fallback = self._first_available(state)
            if fallback is None:
                raise InvalidChallengeError("challenge selection requires the current challenge")
            current_challenge = fallback
        if not isinstance(decision, AdaptationDecision):
            raise InvalidAdaptationDecisionError("next-challenge selection requires a decision")

        used = set(used_challenge_ids or [])
        used.add(current_challenge.challenge_id)
        strategy = strategy_name or ACTION_TO_STRATEGY.get(decision.decision, StrategyName.GATHER_EVIDENCE)
        available = self._available(state, current_challenge, strategy)
        if not available:
            available = list(self.bank) or [current_challenge]

        chosen = self._select_for_strategy(
            strategy,
            decision,
            state,
            current_challenge,
            available,
            used,
        )
        if chosen is not None:
            return chosen
        try:
            return super().select(decision, state, current_challenge, used_challenge_ids)
        except (InvalidChallengeError, InvalidAdaptationDecisionError):
            return current_challenge

    def _first_available(self, state: LearnerState) -> Challenge | None:
        concept_id = state.concept_id
        matching = [item for item in self.bank if item.concept_id == concept_id]
        pool = matching or list(self.bank)
        return pool[0] if pool else None

    def _available(
        self,
        state: LearnerState,
        current: Challenge,
        strategy: StrategyName,
    ) -> list[Challenge]:
        concept_id = state.concept_id or current.concept_id
        matching = [item for item in self.bank if item.concept_id == concept_id]
        if strategy == StrategyName.INCREASE:
            transfer = [
                item
                for item in self.bank
                if item.challenge_type == ChallengeType.TRANSFER
                and item.compatible_with(strategy.value)
            ]
            combined = matching + [item for item in transfer if item not in matching]
            matching = combined or matching
        if not matching:
            matching = list(self.bank)
        return [item for item in matching if item.compatible_with(strategy.value)] or matching

    def _select_for_strategy(
        self,
        strategy: StrategyName,
        decision: AdaptationDecision,
        state: LearnerState,
        current: Challenge,
        available: list[Challenge],
        used: set[str],
    ) -> Challenge | None:
        current_id = current.challenge_id
        current_difficulty = current.difficulty
        allow_repeat = strategy in {StrategyName.REMEDIATE, StrategyName.PROBE}

        if strategy == StrategyName.INCREASE:
            target = _shift_difficulty(current_difficulty, 1)
            preferred_types = (
                ChallengeType.INCREASED_DIFFICULTY,
                ChallengeType.TRANSFER,
                ChallengeType.PRACTICE,
                ChallengeType.STANDARD,
            )
            for difficulty in (target, current_difficulty):
                for challenge_type in preferred_types:
                    chosen = _pick_ranked(
                        [
                            item
                            for item in available
                            if item.difficulty == difficulty and item.challenge_type == challenge_type
                        ],
                        current_id=current_id,
                        used_ids=used,
                        prefer_information=False,
                        allow_repeat=False,
                    )
                    if chosen:
                        return chosen
            harder = [
                item
                for item in available
                if item.difficulty == target or item.challenge_type == ChallengeType.INCREASED_DIFFICULTY
            ]
            return _pick_ranked(
                harder or available,
                current_id=current_id,
                used_ids=used,
                prefer_information=False,
                allow_repeat=False,
            )

        if strategy == StrategyName.DECREASE:
            target = _shift_difficulty(current_difficulty, -1)
            chosen = _pick_ranked(
                [
                    item
                    for item in available
                    if item.difficulty == target and item.challenge_type in PRACTICE_LIKE
                ],
                current_id=current_id,
                used_ids=used,
                prefer_information=False,
                allow_repeat=False,
            )
            if chosen:
                return chosen
            easier = [
                item
                for item in available
                if item.difficulty in {target, Difficulty.EASY}
            ]
            return _pick_ranked(
                easier or available,
                current_id=current_id,
                used_ids=used,
                prefer_information=False,
                allow_repeat=False,
            )

        if strategy == StrategyName.PROBE:
            diagnostic = [item for item in available if item.challenge_type in PROBE_LIKE]
            same_or_easier = [
                item
                for item in diagnostic
                if item.difficulty != Difficulty.HARD or current_difficulty == Difficulty.HARD
            ]
            chosen = _pick_ranked(
                same_or_easier or diagnostic,
                current_id=current_id,
                used_ids=used,
                prefer_information=True,
                allow_repeat=allow_repeat,
            )
            if chosen:
                return chosen

        if strategy in {StrategyName.GATHER_EVIDENCE, StrategyName.ASSESS}:
            informative = sorted(
                available,
                key=lambda item: (-float(item.diagnostic_value), item.challenge_id),
            )
            not_harder = [
                item
                for item in informative
                if item.challenge_type != ChallengeType.INCREASED_DIFFICULTY
            ]
            chosen = _pick_ranked(
                not_harder or informative,
                current_id=current_id,
                used_ids=used,
                prefer_information=True,
                allow_repeat=False,
            )
            if chosen:
                return chosen

        if strategy == StrategyName.REMEDIATE or decision.decision == AdaptationAction.CHANGE_REPRESENTATION:
            target_ids = {item.misconception_id for item in state.repeated_misconceptions} or {
                item.misconception_id for item in state.active_misconceptions
            }
            targeted = [
                item
                for item in available
                if item.target_misconception in target_ids
                and item.challenge_type == ChallengeType.REMEDIATION
            ]
            chosen = _pick_ranked(
                targeted,
                current_id=current_id,
                used_ids=used,
                prefer_information=True,
                allow_repeat=True,
            )
            if chosen:
                if decision.decision == AdaptationAction.CHANGE_REPRESENTATION:
                    different = [
                        item
                        for item in targeted
                        if item.representation != current.representation
                    ]
                    alt = _pick_ranked(
                        different,
                        current_id=current_id,
                        used_ids=used,
                        prefer_information=True,
                        allow_repeat=True,
                    )
                    return alt or chosen
                return chosen
            fallback = [
                item
                for item in available
                if item.target_misconception in target_ids or item.challenge_type == ChallengeType.REMEDIATION
            ]
            chosen = _pick_ranked(
                fallback,
                current_id=current_id,
                used_ids=used,
                prefer_information=True,
                allow_repeat=True,
            )
            if chosen:
                return chosen

        if strategy in {StrategyName.MAINTAIN, StrategyName.RECOVER}:
            same = [
                item
                for item in available
                if item.difficulty == current_difficulty and item.challenge_type in PRACTICE_LIKE
            ]
            chosen = _pick_ranked(
                same,
                current_id=current_id,
                used_ids=used,
                prefer_information=False,
                allow_repeat=False,
            )
            if chosen:
                return chosen
            variation = [
                item
                for item in available
                if item.difficulty == current_difficulty
            ]
            return _pick_ranked(
                variation or available,
                current_id=current_id,
                used_ids=used,
                prefer_information=False,
                allow_repeat=False,
            )

        return _pick_ranked(
            available,
            current_id=current_id,
            used_ids=used,
            prefer_information=strategy in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE, StrategyName.ASSESS},
            allow_repeat=allow_repeat,
        )
