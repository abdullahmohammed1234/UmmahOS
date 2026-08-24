"""Chronological 'How ADAPT Adapted' story built from actual traces."""

from __future__ import annotations

from typing import Any

from adapt.models.enums import AnswerStatus, ReasoningQuality, StrategyName
from adapt.product.present import learner_strategy_message
from adapt.tutor.session import StepTrace, TutorSession


def _evidence_beat(step: StepTrace) -> str:
    evidence = step.evidence
    if evidence.misconception_signal:
        return "A misconception appeared"
    if (
        evidence.answer_status == AnswerStatus.CORRECT
        and evidence.reasoning_quality == ReasoningQuality.STRONG
    ):
        return "You demonstrated strong reasoning"
    if (
        evidence.answer_status == AnswerStatus.CORRECT
        and evidence.reasoning_quality in {ReasoningQuality.WEAK, ReasoningQuality.UNKNOWN}
    ):
        return "You showed uncertainty"
    if evidence.answer_status == AnswerStatus.CORRECT:
        return "You answered correctly"
    if evidence.answer_status in {AnswerStatus.INCORRECT, AnswerStatus.PARTIAL}:
        return "This challenge didn't fully land"
    return "ADAPT collected another observation"


def _strategy_beat(step: StepTrace) -> str | None:
    decision = step.decision
    changed = step.strategy_before.current_strategy != step.strategy_after.current_strategy
    before = step.strategy_before.current_strategy
    if before == StrategyName.REMEDIATE and decision in {
        StrategyName.MAINTAIN,
        StrategyName.INCREASE,
        StrategyName.GATHER_EVIDENCE,
        StrategyName.PROBE,
        StrategyName.RECOVER,
        StrategyName.ASSESS,
    }:
        return "ADAPT recognized recovery and moved you forward"
    if decision == StrategyName.INCREASE and (changed or before != StrategyName.INCREASE):
        return "Difficulty increased"
    if decision == StrategyName.PROBE:
        return "ADAPT probed the concept"
    if decision == StrategyName.REMEDIATE:
        return "ADAPT switched to remediation"
    if decision == StrategyName.DECREASE:
        return "ADAPT stepped back to a simpler version"
    if decision == StrategyName.GATHER_EVIDENCE and step.step_number == 1:
        return "ADAPT assessed your understanding"
    if decision == StrategyName.ASSESS:
        return "ADAPT assessed your understanding"
    if changed:
        return learner_strategy_message(decision)
    return None


def adaptation_story(session: TutorSession) -> dict[str, Any]:
    beats: list[dict[str, Any]] = [
        {
            "kind": "start",
            "text": "You started",
            "step_number": 0,
        }
    ]
    last_text = beats[0]["text"]
    if not session.traces:
        beats.append(
            {
                "kind": "assess",
                "text": "ADAPT is ready to assess your understanding",
                "step_number": 0,
            }
        )
    for step in session.traces:
        evidence_text = _evidence_beat(step)
        if evidence_text != last_text:
            beats.append(
                {
                    "kind": "evidence",
                    "text": evidence_text,
                    "step_number": step.step_number,
                    "decision": step.decision.value,
                }
            )
            last_text = evidence_text
        strategy_text = _strategy_beat(step)
        if strategy_text and strategy_text != last_text:
            beats.append(
                {
                    "kind": "strategy",
                    "text": strategy_text,
                    "step_number": step.step_number,
                    "decision": step.decision.value,
                    "reason": step.reason,
                }
            )
            last_text = strategy_text
    return {
        "title": "How ADAPT adapted",
        "beats": beats,
        "step_count": len(session.traces),
    }
