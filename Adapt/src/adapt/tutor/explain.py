"""Human-readable explanations for Phase 3 challenge decisions."""

from __future__ import annotations

from adapt.models.enums import StrategyName
from adapt.tutor.session import StepTrace, TutorSession


def explain_step(step: StepTrace) -> str:
    before = step.state_before
    after = step.state_after
    evidence = step.evidence
    purpose = _purpose(step.decision, step.next_challenge.challenge_type.value)
    return (
        f"Strategy: {step.decision.value}\n\n"
        f"Reason:\n{step.reason}\n\n"
        f"Evidence:\n{evidence.response_id}\n"
        f"Answer = {evidence.answer_status.value}\n"
        f"Reasoning = {evidence.reasoning_quality.value}\n"
        f"Confidence = {evidence.confidence_signal.value}\n"
        f"Strength = {evidence.evidence_strength.value}\n"
        f"Misconception = {evidence.misconception_signal or 'none'}\n\n"
        f"State:\n"
        f"Mastery {before.mastery_estimate:.2f} → {after.mastery_estimate:.2f}\n"
        f"Uncertainty {before.uncertainty.value} → {after.uncertainty.value}\n"
        f"Trajectory {after.learning_trajectory.value}\n\n"
        f"Strategy transition:\n"
        f"{step.strategy_before.current_strategy.value} → {step.strategy_after.current_strategy.value}\n\n"
        f"Why this strategy was selected:\n{step.reason}\n"
        f"Reason codes: {', '.join(step.reason_codes)}\n\n"
        f"Next challenge:\n{step.next_challenge_id}\n"
        f"Difficulty: {step.next_challenge.difficulty.value}\n"
        f"Type: {step.next_challenge.challenge_type.value}\n"
        f"Purpose:\n{purpose}\n"
    )


def explain_session(session: TutorSession, step_number: int | None = None) -> str:
    if not session.traces:
        return (
            f"Strategy: {session.strategy_state.current_strategy.value}\n\n"
            f"Reason:\nSession initialized with insufficient knowledge; "
            f"the tutor gathers evidence before aggressive difficulty decisions.\n\n"
            f"Next challenge:\n{session.current_challenge.challenge_id}\n"
            f"Purpose:\nEstablish a baseline observation of learner capability.\n"
        )
    if step_number is None:
        return session.traces[-1].explanation or explain_step(session.traces[-1])
    for item in session.traces:
        if item.step_number == step_number:
            return item.explanation or explain_step(item)
    raise KeyError(f"No trace for step {step_number}")


def _purpose(strategy: StrategyName, challenge_type: str) -> str:
    if strategy == StrategyName.PROBE:
        return "Determine whether the misconception persists or was an isolated error."
    if strategy == StrategyName.REMEDIATE:
        return "Target the relevant weakness with a remediation challenge."
    if strategy == StrategyName.INCREASE:
        return "Increase difficulty because evidence supports stronger performance."
    if strategy == StrategyName.DECREASE:
        return "Reduce complexity because evidence indicates broader difficulty."
    if strategy == StrategyName.GATHER_EVIDENCE:
        return "Collect higher-information evidence before committing to a major change."
    if strategy == StrategyName.ASSESS:
        return "Establish learner capability; mastery is not yet assumed."
    if strategy == StrategyName.MAINTAIN:
        return "Keep similar difficulty with variation while evidence accumulates."
    return f"Continue instruction with a {challenge_type} challenge."
