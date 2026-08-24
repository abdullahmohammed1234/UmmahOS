"""Configurable thresholds for the Phase 2 strategy layer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyConfig:
    misconception_flag_threshold: int = 1
    misconception_remediate_threshold: int = 3
    isolated_misconception_max: int = 2
    strong_prior_correct_streak: int = 3
    strong_prior_mastery: float = 0.60
    global_regression_negative_streak: int = 3
    recovery_min_successes: int = 2
    recovery_require_strong_reasoning: int = 1
    hysteresis_min_steps: int = 2
    assess_max_outcomes: int = 1
    increase_correct_rate: float = 0.80
    increase_min_consecutive: int = 3
    change_representation_occurrences: int = 4
    failed_remediation_streak: int = 2
    max_strategy_confidence_weak_evidence: float = 0.55
    max_strategy_confidence_insufficient: float = 0.40
