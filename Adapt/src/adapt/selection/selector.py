"""Phase 7 challenge selector.

Consumes learner state and strategy. Never updates mastery or strategy.
"""

from __future__ import annotations

from adapt.content.catalog import CATALOG, ChallengeCatalog
from adapt.content.models import CatalogChallenge
from adapt.content.types import engine_difficulty_to_product
from adapt.errors import InvalidAdaptationDecisionError, InvalidChallengeError
from adapt.history.memory import ChallengeHistory
from adapt.models.adaptation_decision import AdaptationDecision
from adapt.models.challenge import Challenge
from adapt.models.enums import StrategyName
from adapt.models.learner_state import LearnerState
from adapt.selection.diversity import diversity_bonus
from adapt.selection.reasons import SelectionResult
from adapt.selection.repetition import (
    FAMILY_WINDOW,
    HARD_WINDOW,
    RECENT_WINDOW,
    is_consecutive_type,
    is_family_repeat,
    is_recent_repeat,
    repetition_allowed,
)
from adapt.tutor.selector import ACTION_TO_STRATEGY, AdaptiveChallengeSelector

PREFERRED_TYPES = {
    StrategyName.INCREASE: (
        "TRANSFER",
        "APPLICATION",
        "SCENARIO",
        "DIRECT",
        "SEQUENCE",
        "NUMERIC",
        "ESTIMATION",
    ),
    StrategyName.PROBE: (
        "DIAGNOSTIC",
        "PREDICTION",
        "ERROR_ANALYSIS",
        "COMPARE",
        "EXPLANATION",
        "TRUE_FALSE",
        "CONCEPT_CHECK",
        "DEBUG",
        "MATCH",
        "EXPLAIN_CHOICE",
        "DIAGRAM",
    ),
    StrategyName.REMEDIATE: ("REMEDIATION", "ERROR_ANALYSIS", "COMPARE", "TRUE_FALSE", "DEBUG"),
    StrategyName.DECREASE: ("DIRECT", "CONCEPT_CHECK", "MULTIPLE_CHOICE", "REMEDIATION", "NUMERIC"),
    StrategyName.MAINTAIN: (
        "DIRECT",
        "MULTIPLE_CHOICE",
        "APPLICATION",
        "PREDICTION",
        "SEQUENCE",
        "CONCEPT_CHECK",
        "NUMERIC",
        "SHORT_ANSWER",
        "MATCH",
        "DIAGRAM",
    ),
    StrategyName.RECOVER: ("DIRECT", "CONCEPT_CHECK", "MULTIPLE_CHOICE", "APPLICATION", "NUMERIC"),
    StrategyName.GATHER_EVIDENCE: (
        "DIAGNOSTIC",
        "PREDICTION",
        "ERROR_ANALYSIS",
        "COMPARE",
        "EXPLANATION",
        "CONCEPT_CHECK",
        "DEBUG",
        "EXPLAIN_CHOICE",
        "SHORT_ANSWER",
    ),
    StrategyName.ASSESS: (
        "DIAGNOSTIC",
        "CONCEPT_CHECK",
        "MULTIPLE_CHOICE",
        "TRUE_FALSE",
        "PREDICTION",
        "MATCH",
        "SHORT_ANSWER",
    ),
}


def _target_difficulty(strategy: StrategyName, current: int, mastery: float) -> tuple[int, ...]:
    current = max(1, min(5, current))
    if strategy == StrategyName.INCREASE:
        if mastery >= 0.78:
            return (min(5, current + 1), min(5, current + 2), current)
        return (min(5, current + 1), current, min(5, current + 2))
    if strategy == StrategyName.DECREASE:
        return (max(1, current - 1), current, 1)
    if strategy == StrategyName.REMEDIATE:
        return (max(1, current - 1), current, max(1, current - 2))
    if strategy in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE, StrategyName.ASSESS}:
        return (current, max(1, current - 1), min(5, current + 1))
    return (current, min(5, current + 1), max(1, current - 1))


class Phase7ChallengeSelector(AdaptiveChallengeSelector):
    """Rank catalog challenges from strategy, state, history, and diversity."""

    def __init__(
        self,
        bank: tuple[Challenge, ...] | None = None,
        *,
        catalog: ChallengeCatalog | None = None,
    ) -> None:
        self.catalog = catalog or CATALOG
        super().__init__(bank=bank or self.catalog.engine_bank)
        self.last_result: SelectionResult | None = None

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

        strategy = strategy_name or ACTION_TO_STRATEGY.get(decision.decision, StrategyName.GATHER_EVIDENCE)
        used = list(used_challenge_ids or [])
        if current_challenge.challenge_id not in used:
            used.append(current_challenge.challenge_id)
        history = ChallengeHistory()
        history.from_used_ids(used, lookup=self.catalog.challenge)

        chosen_meta, reasons, scores = self._rank(
            strategy=strategy,
            state=state,
            current=current_challenge,
            history=history,
        )
        if chosen_meta is None:
            try:
                chosen = super().select(decision, state, current_challenge, used_challenge_ids, strategy)
            except (InvalidChallengeError, InvalidAdaptationDecisionError):
                chosen = current_challenge
            meta = self.catalog.challenge(chosen.challenge_id)
            if meta is not None:
                self.last_result = SelectionResult(meta, strategy, ("engine_fallback",), {})
            return chosen

        engine = self.catalog.engine_challenge(chosen_meta.id)
        self.last_result = SelectionResult(chosen_meta, strategy, reasons, scores)
        return engine or chosen_meta.to_engine()

    def _rank(
        self,
        *,
        strategy: StrategyName,
        state: LearnerState,
        current: Challenge,
        history: ChallengeHistory,
    ) -> tuple[CatalogChallenge | None, tuple[str, ...], dict[str, int]]:
        current_meta = self.catalog.challenge(current.challenge_id)
        concept_id = state.concept_id or current.concept_id
        current_diff = (
            current_meta.difficulty
            if current_meta is not None
            else engine_difficulty_to_product(current.difficulty)
        )
        topic_id = current_meta.topic_id if current_meta is not None else None
        pool = [
            item
            for item in self.catalog.challenges
            if item.concept_id == concept_id or (topic_id and item.topic_id == topic_id)
        ]
        if not pool:
            pool = [item for item in self.catalog.challenges if item.domain == (current_meta.domain if current_meta else "")]
        if not pool:
            return None, (), {}

        allow_repeat = repetition_allowed(strategy)
        preferred = PREFERRED_TYPES.get(strategy, ())
        targets = _target_difficulty(strategy, current_diff, state.mastery_estimate)
        target_misc = {item.misconception_id for item in state.repeated_misconceptions} or {
            item.misconception_id for item in state.active_misconceptions
        }

        eligible = []
        for item in pool:
            if not self._strategy_ok(item, strategy):
                continue
            if item.id == current.challenge_id and not allow_repeat:
                continue
            eligible.append(item)
        if not eligible:
            eligible = list(pool)

        def score(item: CatalogChallenge) -> tuple[int, str]:
            strategy_pts = 8 if self._strategy_ok(item, strategy) else 0
            if item.challenge_type in preferred:
                strategy_pts += 5
            concept_pts = 8 if item.concept_id == concept_id else 3 if topic_id and item.topic_id == topic_id else 0
            if item.difficulty in targets:
                difficulty_pts = 8 - targets.index(item.difficulty)
            else:
                difficulty_pts = max(0, 4 - abs(item.difficulty - targets[0]))
            evidence_pts = int(round(item.diagnostic_value * 8))
            if strategy in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE, StrategyName.ASSESS}:
                evidence_pts += 2
            diversity_pts = diversity_bonus(item, history)
            repetition_pts = 8
            if is_recent_repeat(item.id, history, window=RECENT_WINDOW):
                repetition_pts = 0 if not allow_repeat else 4
            if is_family_repeat(item.family, history, window=FAMILY_WINDOW) and not allow_repeat:
                repetition_pts = min(repetition_pts, 2)
            if is_consecutive_type(item.challenge_type, history) and not allow_repeat:
                repetition_pts = min(repetition_pts, 1)
            if history.attempts:
                last_id = history.attempts[-1].challenge_id
                last_meta = self.catalog.challenge(last_id)
                if last_meta is not None and item.representation and item.representation != last_meta.representation:
                    diversity_pts += 4
            progress_pts = 3
            if strategy == StrategyName.REMEDIATE and item.target_misconception in target_misc:
                progress_pts += 8
                strategy_pts += 4
            if strategy == StrategyName.INCREASE and item.difficulty > current_diff:
                progress_pts += 3
            total = (
                strategy_pts * 10000
                + concept_pts * 1000
                + difficulty_pts * 100
                + evidence_pts * 50
                + diversity_pts * 20
                + repetition_pts * 10
                + progress_pts
            )
            return total, item.id

        ranked = sorted(eligible, key=score, reverse=True)
        # Identical scores break ties by challenge_id via the tuple; reverse=True
        # would invert ids, so sort explicitly.
        ranked = sorted(eligible, key=lambda item: (-score(item)[0], item.id))

        filtered = ranked
        if not allow_repeat:
            not_recent = [item for item in ranked if not is_recent_repeat(item.id, history, window=HARD_WINDOW)]
            if not_recent:
                filtered = not_recent
            not_family = [
                item for item in filtered if not is_family_repeat(item.family, history, window=FAMILY_WINDOW)
            ]
            if not_family:
                filtered = not_family
            not_same_type = [item for item in filtered if not is_consecutive_type(item.challenge_type, history)]
            if not_same_type:
                filtered = not_same_type
            if history.attempts:
                last_meta = self.catalog.challenge(history.attempts[-1].challenge_id)
                if last_meta is not None and last_meta.representation:
                    other_repr = [item for item in filtered if item.representation != last_meta.representation]
                    if other_repr:
                        filtered = other_repr

        chosen = filtered[0]
        reasons = [
            f"strategy:{strategy.value}",
            f"concept:{chosen.concept_id}",
            f"difficulty:{chosen.difficulty}",
            f"type:{chosen.challenge_type}",
        ]
        if chosen.challenge_type in preferred:
            reasons.append("strategy_type_match")
        if not is_recent_repeat(chosen.id, history, window=RECENT_WINDOW):
            reasons.append("avoided_recent_repeat")
        if diversity_bonus(chosen, history) >= 6:
            reasons.append("diversity")
        if strategy == StrategyName.REMEDIATE and chosen.target_misconception in target_misc:
            reasons.append("misconception_targeted")
        scores = {
            "total": score(chosen)[0],
            "strategy": 1 if self._strategy_ok(chosen, strategy) else 0,
            "difficulty": chosen.difficulty,
        }
        return chosen, tuple(reasons), scores

    def _strategy_ok(self, item: CatalogChallenge, strategy: StrategyName) -> bool:
        engine = item.to_engine()
        if engine.strategy_compatibility and strategy.value not in engine.strategy_compatibility:
            return False
        if strategy == StrategyName.INCREASE and item.challenge_type == "REMEDIATION":
            return False
        if strategy == StrategyName.PROBE and item.challenge_type in {"TRANSFER"} and item.difficulty >= 5:
            return False
        return True
