"""Learner-facing labels for engine values. No adaptive decisions live here."""

from __future__ import annotations

from adapt.models.enums import Difficulty, StrategyName
from adapt.models.learner_state import LearnerState
from adapt.models.strategy import StrategyState

STRATEGY_DISPLAY = {
    StrategyName.ASSESS: "ASSESS",
    StrategyName.PROBE: "PROBE",
    StrategyName.MAINTAIN: "MAINTAIN",
    StrategyName.INCREASE: "INCREASE DIFFICULTY",
    StrategyName.DECREASE: "DECREASE DIFFICULTY",
    StrategyName.REMEDIATE: "REMEDIATE",
    StrategyName.RECOVER: "RECOVER",
    StrategyName.GATHER_EVIDENCE: "GATHER EVIDENCE",
}

DIFFICULTY_DISPLAY = {
    Difficulty.EASY: "easier",
    Difficulty.MEDIUM: "similar-difficulty",
    Difficulty.HARD: "harder",
}

PROMISE = "ADAPT — A tutor that adapts to how you learn, not just whether you are right."
PROMISE_SHORT = "A tutor that adapts to how you learn, not just whether you are right."
TAGLINE = "Evidence-driven adaptive tutoring."
HERO = "Learn differently with ADAPT."
SUPPORTING = "An adaptive tutor that changes what you learn next based on how you learn."
CTA_PRIMARY = "Start Learning"
CTA_SECONDARY = "See How ADAPT Works"
DEMO_SCENARIO_LABEL = "DEMO SCENARIO"
FINAL_MESSAGE = (
    "ADAPT doesn't just ask whether you're right. "
    "It learns from how you answer and changes what happens next."
)

LEARNER_STRATEGY_PLAIN = {
    StrategyName.ASSESS: "See how you approach this",
    StrategyName.PROBE: "Check understanding another way",
    StrategyName.MAINTAIN: "Keep this level",
    StrategyName.INCREASE: "Make the next challenge harder",
    StrategyName.DECREASE: "Simplify the next challenge",
    StrategyName.REMEDIATE: "Work on this idea directly",
    StrategyName.RECOVER: "Move forward",
    StrategyName.GATHER_EVIDENCE: "Gather a bit more evidence",
}


def strategy_label(value: StrategyName | str) -> str:
    if isinstance(value, str):
        try:
            value = StrategyName(value)
        except ValueError:
            return value
    return STRATEGY_DISPLAY[value]


def learner_strategy_plain(value: StrategyName | str) -> str:
    if isinstance(value, str):
        try:
            value = StrategyName(value)
        except ValueError:
            return value
    return LEARNER_STRATEGY_PLAIN.get(value, strategy_label(value))


def mastery_plain(state: LearnerState) -> str:
    if state.evidence_strength.value in {"INSUFFICIENT", "WEAK"} and state.mastery_estimate <= 0.55:
        return "uncertain"
    if state.mastery_estimate >= 0.8:
        return "strong"
    if state.mastery_estimate >= 0.6:
        return "growing"
    if state.mastery_estimate >= 0.4:
        return "developing"
    return "building"


def confidence_plain(state: LearnerState) -> str:
    if state.confidence < 0.35:
        return "low"
    if state.confidence < 0.65:
        return "moderate"
    return "high"


def opening_state(state: LearnerState, strategy: StrategyState, *, concept: str) -> dict[str, str]:
    return {
        "concept": concept,
        "mastery": mastery_plain(state),
        "confidence": confidence_plain(state),
        "strategy": strategy_label(strategy.current_strategy),
        "strategy_code": strategy.current_strategy.value,
    }
