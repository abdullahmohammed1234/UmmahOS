"""Adaptive Strategy Engine.

Decides what instructional strategy should happen next. Learner state is an input,
not a synonym for strategy. Deterministic. No concept-name branching.
"""

from __future__ import annotations

from adapt.errors import InvalidEvidenceError, InvalidLearnerStateError, InvalidStrategyStateError
from adapt.models.enums import (
    AdaptationAction,
    AnswerStatus,
    EvidenceStrength,
    LearnerConfidence,
    ReasoningQuality,
    StrategyName,
)
from adapt.models.evidence import Evidence
from adapt.models.learner_response import LearnerResponse
from adapt.models.learner_state import LearnerState
from adapt.models.strategy import (
    EXTREME_STRATEGIES,
    STRATEGY_TO_ACTION,
    StrategyDecision,
    StrategyState,
    StrategyTransition,
    initial_strategy_state,
)
from adapt.strategy.config import StrategyConfig
from adapt.strategy.features import StrategyFeatures, extract_features


def _cap_confidence(score: float, evidence: Evidence, config: StrategyConfig) -> float:
    capped = max(0.0, min(1.0, score))
    if evidence.evidence_strength == EvidenceStrength.INSUFFICIENT:
        return min(capped, config.max_strategy_confidence_insufficient)
    if evidence.evidence_strength == EvidenceStrength.WEAK:
        return min(capped, config.max_strategy_confidence_weak_evidence)
    if evidence.evidence_strength == EvidenceStrength.CONTRADICTORY:
        return min(capped, 0.50)
    return capped


def _snapshot(state: LearnerState, strategy: StrategyState) -> dict:
    return {
        "mastery_estimate": round(state.mastery_estimate, 4),
        "confidence": round(state.confidence, 4),
        "uncertainty": state.uncertainty.value,
        "learning_trajectory": state.learning_trajectory.value,
        "evidence_strength": state.evidence_strength.value,
        "reasoning_quality": state.reasoning_quality.value,
        "error_pattern": state.error_pattern.value,
        "active_misconceptions": [item.to_dict() for item in state.active_misconceptions],
        "current_strategy": strategy.current_strategy.value,
        "previous_strategy": None
        if strategy.previous_strategy is None
        else strategy.previous_strategy.value,
    }


def _supporting(features: StrategyFeatures, extra: tuple[str, ...] = ()) -> tuple[str, ...]:
    items = [
        f"consecutive_correct={features.consecutive_correct}",
        f"consecutive_negative={features.consecutive_negative}",
        f"max_misconception_occurrences={features.max_misconception_occurrences}",
        f"isolated_misconception={features.isolated_misconception}",
        f"global_regression={features.global_regression}",
        f"recovery_successes={features.recovery_successes}",
        f"mastery={features.mastery_estimate:.2f}",
    ]
    items.extend(extra)
    return tuple(items)


def _next_strategy_state(
    previous: StrategyState,
    chosen: StrategyName,
    reason: str,
    evidence_ids: tuple[str, ...],
    confidence: float,
    features: StrategyFeatures,
) -> StrategyState:
    same = previous.current_strategy == chosen
    last_extreme = previous.last_extreme_strategy
    steps_since = previous.steps_since_extreme
    if chosen in EXTREME_STRATEGIES:
        last_extreme = chosen
        steps_since = 0
    elif last_extreme is not None:
        steps_since = previous.steps_since_extreme + 1
    flag = previous.misconception_flag
    flagged_id = previous.flagged_misconception_id
    if features.new_misconception or features.isolated_misconception:
        flag = "FLAGGED"
        flagged_id = flagged_id
    if chosen == StrategyName.REMEDIATE:
        flag = "FLAGGED"
    if (
        flag == "FLAGGED"
        and not features.persistent_misconception
        and features.max_misconception_occurrences <= 1
        and features.consecutive_correct >= 1
        and chosen in {StrategyName.MAINTAIN, StrategyName.PROBE, StrategyName.INCREASE}
    ):
        flag = "CLEARED"
    recovering = chosen in {StrategyName.MAINTAIN, StrategyName.PROBE, StrategyName.INCREASE} and (
        previous.current_strategy == StrategyName.REMEDIATE or previous.recovering
    )
    if chosen == StrategyName.REMEDIATE:
        recovering = False
    failures = previous.consecutive_remediation_failures
    if previous.current_strategy == StrategyName.REMEDIATE and chosen == StrategyName.REMEDIATE:
        if features.consecutive_negative >= 1:
            failures += 1
        else:
            failures = 0
    else:
        failures = 0
    return StrategyState(
        current_strategy=chosen,
        previous_strategy=previous.current_strategy,
        strategy_confidence=confidence,
        transition_reason=reason,
        transition_evidence=evidence_ids,
        consecutive_same_strategy=previous.consecutive_same_strategy + 1 if same else 1,
        consecutive_recovery_successes=features.recovery_successes if recovering or previous.current_strategy == StrategyName.REMEDIATE else 0,
        consecutive_remediation_failures=failures,
        misconception_flag=flag,
        flagged_misconception_id=flagged_id,
        steps_in_strategy=previous.steps_in_strategy + 1 if same else 1,
        last_extreme_strategy=last_extreme,
        steps_since_extreme=steps_since,
        recovering=recovering,
    )


def _hysteresis_override(
    previous: StrategyState,
    candidate: StrategyName,
    features: StrategyFeatures,
    config: StrategyConfig,
) -> StrategyName | None:
    if (
        candidate == StrategyName.INCREASE
        and previous.current_strategy == StrategyName.REMEDIATE
        and not features.recovery_ready
    ):
        return StrategyName.REMEDIATE
    if candidate == StrategyName.INCREASE and previous.current_strategy == StrategyName.REMEDIATE:
        return StrategyName.MAINTAIN
    if candidate == StrategyName.DECREASE and previous.last_extreme_strategy == StrategyName.INCREASE:
        if features.global_regression and features.consecutive_negative >= config.global_regression_negative_streak:
            return None
        if previous.steps_since_extreme < config.hysteresis_min_steps or features.consecutive_negative < 3:
            return StrategyName.PROBE
    if candidate == StrategyName.INCREASE and previous.last_extreme_strategy == StrategyName.DECREASE:
        if (
            features.consecutive_correct >= config.increase_min_consecutive
            and previous.steps_since_extreme >= config.hysteresis_min_steps
            and features.increase_supported
        ):
            return None
        return StrategyName.PROBE
    if (
        candidate in {StrategyName.INCREASE, StrategyName.DECREASE}
        and previous.current_strategy in {StrategyName.INCREASE, StrategyName.DECREASE}
        and candidate != previous.current_strategy
        and previous.steps_in_strategy < config.hysteresis_min_steps
        and not (candidate == StrategyName.DECREASE and features.global_regression)
    ):
        return StrategyName.PROBE
    return None


class AdaptiveStrategyEngine:
    def __init__(self, config: StrategyConfig | None = None) -> None:
        self.config = config or StrategyConfig()

    def decide(
        self,
        *,
        learner_state: LearnerState,
        evidence: Evidence,
        history: list[LearnerResponse] | None = None,
        current_strategy: StrategyState | None = None,
        recent_evidence: list[Evidence] | None = None,
    ) -> StrategyDecision:
        if not isinstance(learner_state, LearnerState):
            raise InvalidLearnerStateError("strategy decision requires a valid learner state")
        if not isinstance(evidence, Evidence):
            raise InvalidEvidenceError("strategy decision requires structured evidence")
        if current_strategy is not None and not isinstance(current_strategy, StrategyState):
            raise InvalidStrategyStateError("current_strategy must be a StrategyState")

        previous = current_strategy or initial_strategy_state()
        features = extract_features(
            state=learner_state,
            evidence=evidence,
            history=history,
            strategy=previous,
            recent_evidence=recent_evidence,
            config=self.config,
        )
        chosen, codes, reason, confidence, internal = self._select(previous, features, evidence)
        override = _hysteresis_override(previous, chosen, features, self.config)
        if override is not None:
            chosen = override
            codes = codes + ("hysteresis_stability", "prefer_probe_when_ambiguous")
            reason = (
                f"{reason} Strategy oscillation is blocked until additional evidence "
                f"accumulates, so the action is {chosen.value}."
            )
            confidence = min(confidence, 0.62)
            internal = False

        if chosen == StrategyName.RECOVER:
            internal = True
            chosen = self._exit_recovery(features, previous)
            codes = codes + ("internal_recover", f"exit_to_{chosen.value.lower()}")
            reason = (
                f"{reason} Recovery is an internal transition; the exposed strategy is {chosen.value}."
            )

        confidence = _cap_confidence(confidence, evidence, self.config)
        action = STRATEGY_TO_ACTION[chosen]
        if (
            chosen == StrategyName.REMEDIATE
            and features.max_misconception_occurrences >= self.config.change_representation_occurrences
        ):
            action = AdaptationAction.CHANGE_REPRESENTATION
            codes = codes + ("change_representation_after_failed_remediation",)

        new_state = _next_strategy_state(
            previous, chosen, reason, features.evidence_ids, confidence, features
        )
        transition = StrategyTransition(
            from_strategy=previous.current_strategy,
            to_strategy=chosen,
            reason=reason,
            evidence_ids=features.evidence_ids,
            internal=internal,
        )
        return StrategyDecision(
            decision=chosen,
            reason=reason,
            current_strategy=chosen,
            previous_strategy=previous.current_strategy,
            evidence_ids=features.evidence_ids,
            state_snapshot=_snapshot(learner_state, previous),
            confidence=confidence,
            transition=transition,
            supporting_evidence=_supporting(features, codes),
            reason_codes=codes,
            uncertainty=learner_state.uncertainty.value,
            strategy_state=new_state,
            adaptation_action=action,
        )

    def _exit_recovery(self, features: StrategyFeatures, previous: StrategyState) -> StrategyName:
        _ = previous
        if features.increase_supported:
            return StrategyName.MAINTAIN
        if features.high_uncertainty or features.conflicting_evidence:
            return StrategyName.PROBE
        return StrategyName.MAINTAIN

    def _select(
        self,
        previous: StrategyState,
        features: StrategyFeatures,
        evidence: Evidence,
    ) -> tuple[StrategyName, tuple[str, ...], str, float, bool]:
        config = self.config

        if features.conflicting_evidence:
            if features.persistent_misconception:
                pass
            elif features.global_regression and features.consecutive_negative >= config.global_regression_negative_streak:
                pass
            elif features.isolated_misconception or (
                features.new_misconception and features.strong_prior and not features.global_regression
            ):
                return (
                    StrategyName.PROBE,
                    (
                        "conflicting_evidence",
                        "delayed_or_isolated_misconception",
                        "strong_prior_performance",
                        "not_global_regression",
                    ),
                    (
                        "A new misconception appeared after a strong history; additional evidence is required "
                        "before reducing difficulty."
                    ),
                    0.74,
                    False,
                )
            else:
                return (
                    StrategyName.GATHER_EVIDENCE,
                    ("conflicting_evidence", "avoid_extreme_adaptation"),
                    "Evidence is conflicting, so additional evidence is required before a major instructional change.",
                    0.52,
                    False,
                )

        if previous.current_strategy == StrategyName.REMEDIATE:
            if features.recovery_ready:
                return (
                    StrategyName.RECOVER,
                    (
                        "successful_remediation",
                        "strategy_recovery",
                        f"recovery_successes={features.recovery_successes}",
                        "not_correctness_alone",
                    ),
                    (
                        "Successful remediation produced repeated correct responses with strong reasoning, "
                        "so strategy recovers away from REMEDIATE."
                    ),
                    0.80 if features.recovery_successes >= 3 else 0.68,
                    True,
                )
            if evidence.answer_status == AnswerStatus.CORRECT and features.recovery_successes < config.recovery_min_successes:
                return (
                    StrategyName.REMEDIATE,
                    (
                        "partial_recovery_insufficient",
                        "remain_in_remediate",
                        f"recovery_successes={features.recovery_successes}",
                    ),
                    (
                        "The learner answered correctly during remediation, but recovery requires more than "
                        "a single success before leaving REMEDIATE."
                    ),
                    0.58,
                    False,
                )
            if features.persistent_misconception or evidence.misconception_signal:
                return (
                    StrategyName.REMEDIATE,
                    ("failed_or_ongoing_remediation", "misconception_still_active"),
                    "Remediation continues because misconception evidence is still present.",
                    0.78,
                    False,
                )
            return (
                StrategyName.REMEDIATE,
                ("remediate_until_recovery_evidence",),
                "The current strategy remains REMEDIATE until recovery evidence is sufficient.",
                0.60,
                False,
            )

        if features.n_outcomes <= config.assess_max_outcomes and previous.current_strategy == StrategyName.ASSESS:
            if evidence.answer_status in {AnswerStatus.AMBIGUOUS, AnswerStatus.UNKNOWN}:
                return (
                    StrategyName.ASSESS,
                    ("insufficient_evidence", "assess_unknown_capability"),
                    "The learner's current capability is insufficiently known, so the strategy remains ASSESS.",
                    0.35,
                    False,
                )
            return (
                StrategyName.GATHER_EVIDENCE,
                ("sparse_evidence", "gather_before_commit"),
                "Evidence is still sparse, so the system gathers more evidence before committing to a major change.",
                0.40,
                False,
            )

        if features.insufficient_evidence and not features.persistent_misconception:
            if features.n_outcomes <= config.assess_max_outcomes:
                return (
                    StrategyName.ASSESS,
                    ("insufficient_evidence", "assess_unknown_capability"),
                    "The learner's current capability is insufficiently known, so the strategy is ASSESS.",
                    0.35,
                    False,
                )
            return (
                StrategyName.GATHER_EVIDENCE,
                ("insufficient_evidence", "conservative_adaptation"),
                "Evidence is insufficient, so the system gathers more evidence rather than changing difficulty.",
                0.42,
                False,
            )

        if features.persistent_misconception:
            return (
                StrategyName.REMEDIATE,
                (
                    "repeated_misconception",
                    "persistent_misconception_evidence",
                    f"occurrences={features.max_misconception_occurrences}",
                ),
                "Repeated misconception evidence supports targeted remediation.",
                0.84,
                False,
            )

        if features.isolated_misconception or (
            features.new_misconception and features.strong_prior and not features.global_regression
        ):
            return (
                StrategyName.PROBE,
                (
                    "delayed_or_isolated_misconception",
                    "strong_prior_performance",
                    "not_global_regression",
                    "limited_evidence",
                ),
                (
                    "A new misconception appeared after a strong history; additional evidence is required "
                    "before reducing difficulty."
                ),
                0.78,
                False,
            )

        if features.global_regression:
            if features.high_uncertainty and features.consecutive_negative < config.global_regression_negative_streak:
                return (
                    StrategyName.GATHER_EVIDENCE,
                    ("possible_regression", "uncertainty_still_high"),
                    "Regression is possible but certainty is limited, so more evidence is gathered.",
                    0.55,
                    False,
                )
            return (
                StrategyName.DECREASE,
                (
                    "global_regression",
                    "consecutive_negative_evidence",
                    "not_localized_misconception",
                ),
                "Evidence indicates broader regression rather than a localized misconception, so difficulty decreases.",
                0.76,
                False,
            )

        if features.temporary_noise:
            return (
                StrategyName.MAINTAIN,
                ("temporary_or_noisy_error", "not_global_regression"),
                "A temporary or noisy error is not sufficient evidence for a strategy change.",
                0.70,
                False,
            )

        if features.localized_error and not features.persistent_misconception:
            return (
                StrategyName.PROBE,
                ("localized_error", "probe_before_decrease"),
                "The error appears localized, so the system probes rather than treating it as global regression.",
                0.72,
                False,
            )

        if (
            evidence.answer_status == AnswerStatus.CORRECT
            and features.weak_reasoning
            and evidence.confidence_signal == LearnerConfidence.HIGH
        ):
            return (
                StrategyName.PROBE,
                ("confidence_mastery_conflict", "weak_reasoning", "do_not_increase"),
                "Correctness with weak reasoning and high stated confidence is a conflict; the system probes rather than increasing difficulty.",
                0.64,
                False,
            )

        if evidence.reasoning_quality == ReasoningQuality.UNKNOWN and features.n_outcomes < 3:
            return (
                StrategyName.GATHER_EVIDENCE,
                ("unknown_reasoning", "gather_evidence"),
                "Reasoning quality is unknown, so additional evidence is required.",
                0.45,
                False,
            )

        if features.increase_supported and previous.current_strategy != StrategyName.REMEDIATE:
            return (
                StrategyName.INCREASE,
                (
                    "strong_recent_evidence",
                    "strong_reasoning",
                    "consistent_recent_performance",
                    "no_active_persistent_misconception",
                ),
                "Evidence supports increased difficulty: strong reasoning, reliable performance, and no persistent misconception.",
                0.86,
                False,
            )

        if features.high_uncertainty:
            return (
                StrategyName.PROBE,
                ("high_uncertainty", "avoid_extreme_adaptation"),
                "Uncertainty is still high, so the system probes rather than making an extreme change.",
                0.50,
                False,
            )

        return (
            StrategyName.MAINTAIN,
            ("maintain_until_stronger_signal", "current_trajectory_appropriate"),
            "The current challenge trajectory remains appropriate given the available evidence.",
            0.62,
            False,
        )
