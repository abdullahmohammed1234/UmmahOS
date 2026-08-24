"""Select the next challenge so that it reflects the adaptation decision."""

from __future__ import annotations

from adapt.adaptation.challenge_bank import CHALLENGE_BANK, CONCEPT_ID
from adapt.errors import InvalidAdaptationDecisionError, InvalidChallengeError
from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.challenge import Challenge
from adapt.models.enums import (
    AdaptationAction,
    ChallengeType,
    Difficulty,
    DIFFICULTY_ORDER,
)
from adapt.models.learner_state import LearnerState


def _shift_difficulty(current: Difficulty, delta: int) -> Difficulty:
    index = DIFFICULTY_ORDER.index(current)
    next_index = min(len(DIFFICULTY_ORDER) - 1, max(0, index + delta))
    return DIFFICULTY_ORDER[next_index]


def _pick(
    candidates: list[Challenge],
    *,
    current_id: str | None,
    used_ids: set[str],
) -> Challenge | None:
    unused = [item for item in candidates if item.challenge_id not in used_ids]
    pool = unused or candidates
    for item in pool:
        if item.challenge_id != current_id:
            return item
    return pool[0] if pool else None


class ChallengeSelector:
    def __init__(self, bank: tuple[Challenge, ...] | None = None) -> None:
        self.bank = bank or CHALLENGE_BANK

    def select(
        self,
        decision: AdaptationDecision,
        state: LearnerState,
        current_challenge: Challenge | None,
        used_challenge_ids: list[str] | None = None,
    ) -> Challenge:
        if current_challenge is None:
            raise InvalidChallengeError("challenge selection requires the current challenge")
        if not isinstance(decision, AdaptationDecision):
            raise InvalidAdaptationDecisionError("next-challenge selection requires a decision")

        used = set(used_challenge_ids or [])
        used.add(current_challenge.challenge_id)
        concept_id = state.concept_id or current_challenge.concept_id or CONCEPT_ID
        available = [item for item in self.bank if item.concept_id == concept_id]
        if not available:
            available = list(self.bank)

        action = decision.decision
        current_id = current_challenge.challenge_id
        current_difficulty = current_challenge.difficulty

        if action == AdaptationAction.INCREASE_DIFFICULTY:
            target = _shift_difficulty(current_difficulty, 1)
            chosen = _pick(
                [item for item in available if item.difficulty == target and item.challenge_type == ChallengeType.PRACTICE],
                current_id=current_id,
                used_ids=used,
            )
            if chosen:
                return chosen
        elif action == AdaptationAction.DECREASE_DIFFICULTY:
            target = _shift_difficulty(current_difficulty, -1)
            chosen = _pick(
                [item for item in available if item.difficulty == target and item.challenge_type == ChallengeType.PRACTICE],
                current_id=current_id,
                used_ids=used,
            )
            if chosen:
                return chosen
        elif action == AdaptationAction.REMEDIATE:
            target_ids = {item.misconception_id for item in state.repeated_misconceptions} or {
                item.misconception_id for item in state.active_misconceptions
            }
            targeted = [
                item
                for item in available
                if item.target_misconception in target_ids
                and item.challenge_type == ChallengeType.REMEDIATION
            ]
            chosen = _pick(targeted, current_id=current_id, used_ids=used)
            if chosen:
                return chosen
            fallback = [
                item
                for item in available
                if item.target_misconception in target_ids
            ]
            chosen = _pick(fallback, current_id=current_id, used_ids=used)
            if chosen:
                return chosen
        elif action == AdaptationAction.CHANGE_REPRESENTATION:
            target_ids = {item.misconception_id for item in state.active_misconceptions}
            different = [
                item
                for item in available
                if item.representation != current_challenge.representation
                and (not target_ids or item.target_misconception in target_ids or item.challenge_type == ChallengeType.DIAGNOSTIC)
            ]
            chosen = _pick(different, current_id=current_id, used_ids=used)
            if chosen:
                return chosen
        elif action in {
            AdaptationAction.PROBE_UNCERTAINTY,
            AdaptationAction.GATHER_MORE_EVIDENCE,
        }:
            diagnostic = [
                item for item in available if item.challenge_type == ChallengeType.DIAGNOSTIC
            ]
            chosen = _pick(diagnostic, current_id=current_id, used_ids=used)
            if chosen:
                return chosen
        elif action == AdaptationAction.MAINTAIN_DIFFICULTY:
            same = [
                item
                for item in available
                if item.difficulty == current_difficulty
                and item.challenge_type == ChallengeType.PRACTICE
            ]
            chosen = _pick(same, current_id=current_id, used_ids=used)
            if chosen:
                return chosen
        else:
            raise InvalidAdaptationDecisionError(
                f"Unsupported adaptation decision: {action}"
            )

        chosen = _pick(available, current_id=current_id, used_ids=used)
        if chosen is None:
            raise InvalidChallengeError("challenge bank is empty")
        return chosen
