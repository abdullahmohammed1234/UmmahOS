"""Learner-experience helpers. Presentation only — no adaptive decisions."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from adapt.content.catalog import CATALOG
from adapt.history.memory import ChallengeAttempt
from adapt.models.enums import AnswerStatus, ReasoningQuality, StrategyName
from adapt.product.explanations import learner_explanation, why_from_strategy
from adapt.product.present import challenge_view, concept_label, delta_arrow
from adapt.product.presentation import challenge_presentation, display_prompt
from adapt.product.trace_explain import human_trace_explanation
from adapt.tutor.session import StepTrace, TutorSession

APPROACH_OPTIONS = (
    {"id": "knew", "label": "I knew the method"},
    {"id": "worked", "label": "I worked it out"},
    {"id": "pattern", "label": "I recognized the pattern"},
    {"id": "guessed", "label": "I guessed"},
    {"id": "unsure", "label": "I wasn't sure"},
)

APPROACH_TEXT = {
    "knew": "I knew the method.",
    "worked": "I worked it out.",
    "pattern": "I recognized the pattern.",
    "guessed": "I guessed.",
    "unsure": "I wasn't sure.",
}

CONFIDENCE_EMOJI = (
    {"value": 1, "label": "Not sure", "emoji": "😕"},
    {"value": 2, "label": "Not sure", "emoji": "😕"},
    {"value": 3, "label": "Somewhat", "emoji": "😐"},
    {"value": 4, "label": "Confident", "emoji": "🙂"},
    {"value": 5, "label": "Very confident", "emoji": "😎"},
)

CONFIDENCE_QUICK = (
    {"value": 1, "label": "Not sure", "emoji": "😕", "sr": "Not sure"},
    {"value": 3, "label": "Somewhat", "emoji": "🙂", "sr": "Somewhat sure"},
    {"value": 5, "label": "Very confident", "emoji": "😎", "sr": "Very confident"},
)

CONFIDENCE_VISUAL = (
    {"value": 1, "label": "Not sure", "emoji": "😕", "sr": "Not sure"},
    {"value": 3, "label": "Somewhat sure", "emoji": "😐", "sr": "Somewhat sure"},
    {"value": 4, "label": "Sure", "emoji": "🙂", "sr": "Sure"},
    {"value": 5, "label": "Very sure", "emoji": "😎", "sr": "Very sure"},
)


def combine_reasoning(approach: str | None, explanation: str | None) -> str | None:
    parts: list[str] = []
    if approach:
        parts.append(APPROACH_TEXT.get(str(approach).strip().lower(), str(approach).strip()))
    if explanation and str(explanation).strip():
        parts.append(str(explanation).strip())
    if not parts:
        return None
    return " ".join(parts)


def evidence_plan(session: TutorSession, challenge) -> dict[str, Any]:
    meta = CATALOG.challenge(challenge.challenge_id) if challenge else None
    last = session.traces[-1] if session.traces else None
    ask_reasoning = False
    prompt = "A short note is optional."
    if meta and "reasoning" in meta.evidence_requirements:
        ask_reasoning = True
        prompt = "A short explanation will help ADAPT understand this check."
    if last is not None:
        if last.decision in {StrategyName.PROBE, StrategyName.GATHER_EVIDENCE, StrategyName.ASSESS}:
            ask_reasoning = True
            prompt = "A few words about your method will help ADAPT decide what to do next."
        if last.evidence.reasoning_quality == ReasoningQuality.UNKNOWN and last.step_number >= 1:
            ask_reasoning = True
        if last.evidence.misconception_signal:
            ask_reasoning = False
            prompt = "No essay needed — just your best answer."
    return {
        "ask_approach": True,
        "ask_confidence": True,
        "ask_reasoning": ask_reasoning,
        "reasoning_optional": True,
        "reasoning_prompt": "How did you approach it?",
        "reasoning_help": "Optional — this helps ADAPT understand your thinking.",
        "note_prompt": "Add a note",
        "approach_options": [dict(item) for item in APPROACH_OPTIONS],
        "confidence_emoji": [dict(item) for item in CONFIDENCE_EMOJI],
        "confidence_visual": [dict(item) for item in CONFIDENCE_VISUAL],
        "confidence_quick": [dict(item) for item in CONFIDENCE_QUICK],
        "legacy_help": prompt,
    }


def public_challenge(challenge, *, include_answer: bool = False) -> dict[str, Any]:
    payload = challenge_view(challenge, include_answer=include_answer)
    meta = CATALOG.challenge(challenge.challenge_id)
    if meta is None:
        return payload
    extra = meta.to_dict(include_answer=include_answer)
    extra.pop("answer", None)
    if not include_answer:
        extra.pop("explanation", None)
        extra.pop("learn_more", None)
        extra.pop("solution", None)
    payload.update(extra)
    payload["prompt"] = meta.prompt
    payload["prompt_display"] = display_prompt(meta.prompt)
    payload["challenge_id"] = meta.id
    payload["presentation"] = challenge_presentation(meta.id, subject_id=meta.domain)
    return payload


def what_adapt_noticed(step: StepTrace) -> dict[str, Any]:
    evidence = step.evidence
    learner = learner_explanation(step)
    bullets: list[dict[str, Any]] = []
    correct = evidence.answer_status == AnswerStatus.CORRECT
    bullets.append({"ok": correct, "text": "Correct answer" if correct else "Not quite"})
    if evidence.reasoning_quality == ReasoningQuality.STRONG:
        bullets.append({"ok": True, "text": "Strong reasoning"})
    elif evidence.reasoning_quality == ReasoningQuality.WEAK:
        bullets.append({"ok": False, "text": "Reasoning was thin or uncertain"})
    elif evidence.reasoning_quality == ReasoningQuality.MODERATE:
        bullets.append({"ok": True, "text": "Some reasoning"})
    if evidence.confidence_signal.value == "HIGH":
        bullets.append({"ok": True, "text": "High confidence"})
    elif evidence.confidence_signal.value == "LOW":
        bullets.append({"ok": False, "text": "Low confidence"})
    elif evidence.confidence_signal.value == "MODERATE":
        bullets.append({"ok": True, "text": "Moderate confidence"})
    if evidence.misconception_signal:
        bullets.append({"ok": False, "text": "A specific mix-up showed up"})
    mastery = max(0.0, min(1.0, float(step.state_after.mastery_estimate)))
    arrow = delta_arrow(step.state_before.mastery_estimate, step.state_after.mastery_estimate)
    kind, headline, body = noticed_kind_copy(step)
    return {
        "title": "What ADAPT noticed",
        "kind": kind,
        "headline": headline,
        "body": body,
        "bullets": bullets,
        "summary": learner["noticed"],
        "mastery_percent": int(round(mastery * 100)),
        "mastery_arrow": {"up": "↑", "down": "↓", "same": "→"}[arrow],
        "strategy": step.decision.value,
        "strategy_plain": {
            StrategyName.INCREASE: "Let's raise the challenge",
            StrategyName.PROBE: "Let's check this another way",
            StrategyName.REMEDIATE: "Let's rebuild this idea",
            StrategyName.DECREASE: "Let's simplify",
            StrategyName.MAINTAIN: "Let's stay at this level",
            StrategyName.GATHER_EVIDENCE: "Let's gather a bit more evidence",
            StrategyName.ASSESS: "Let's see how you approach this",
            StrategyName.RECOVER: "Let's move forward",
        }.get(step.decision, step.decision.value),
        "explanation": human_trace_explanation(step),
        "from_trace": True,
    }


def noticed_kind_copy(step: StepTrace) -> tuple[str, str, str]:
    evidence = step.evidence
    decision = step.decision
    trajectory = step.state_after.learning_trajectory.value
    correct = evidence.answer_status == AnswerStatus.CORRECT
    if evidence.misconception_signal and decision == StrategyName.REMEDIATE:
        return (
            "misconception",
            "Misconception",
            "You're making the same mistake in a different form.",
        )
    if decision == StrategyName.REMEDIATE:
        return (
            "remediation",
            "Remediation",
            "Let's slow down and work on this idea from another angle.",
        )
    if decision in {StrategyName.GATHER_EVIDENCE, StrategyName.ASSESS} or (
        step.state_after.uncertainty.value in {"HIGH_UNCERTAINTY", "INSUFFICIENT_EVIDENCE"}
    ):
        return (
            "uncertainty",
            "Uncertainty",
            "ADAPT isn't sure yet, so let's gather more evidence.",
        )
    if trajectory == "IMPROVING" and step.step_number > 1:
        return (
            "improvement",
            "Improvement",
            "Your recent answers show improvement.",
        )
    if correct and evidence.confidence_signal.value == "LOW":
        return (
            "low_confidence",
            "Low confidence",
            "You got it right, but you're still unsure.",
        )
    if (
        correct
        and evidence.confidence_signal.value == "HIGH"
        and evidence.reasoning_quality == ReasoningQuality.STRONG
    ):
        return (
            "strong_evidence",
            "Strong evidence",
            "You seem comfortable with this idea.",
        )
    if evidence.misconception_signal:
        return (
            "misconception",
            "Misconception",
            "You're making the same mistake in a different form.",
        )
    return ("observed", "What ADAPT noticed", noticed_from_evidence_safe(step))


def noticed_from_evidence_safe(step: StepTrace) -> str:
    from adapt.product.explanations import noticed_from_evidence

    return noticed_from_evidence(step)


def why_this_question(
    step: StepTrace | None,
    *,
    selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if step is None:
        return {
            "title": "Why this question?",
            "text": "This is an opening question so ADAPT can see how you approach the topic.",
            "from_trace": True,
        }
    reasons = tuple((selection or {}).get("reasons") or [])
    text = why_from_strategy(step)
    explain = human_trace_explanation(step)
    return {
        "title": "Why this question?",
        "text": text,
        "detail": explain.get("next_challenge"),
        "strategy": step.decision.value,
        "challenge_id": step.next_challenge_id,
        "selection_reasons": list(reasons),
        "from_trace": True,
    }


def attempt_from_step(step: StepTrace, *, session_id: str) -> ChallengeAttempt:
    meta = CATALOG.challenge(step.challenge_id)
    result = "correct" if step.evidence.answer_status == AnswerStatus.CORRECT else "incorrect"
    if step.evidence.answer_status == AnswerStatus.PARTIAL:
        result = "partial"
    return ChallengeAttempt(
        challenge_id=step.challenge_id,
        session_id=session_id,
        sequence=step.step_number,
        concept_id=step.challenge.concept_id,
        difficulty=meta.difficulty if meta else engine_diff(step.challenge),
        challenge_type=meta.challenge_type if meta else step.challenge.challenge_type.value,
        family_id=meta.family if meta else step.challenge_id,
        result=result,
        strategy=step.decision.value,
        used_for_remediation=step.decision == StrategyName.REMEDIATE,
        used_as_diagnostic=step.challenge.challenge_type.value in {"DIAGNOSTIC", "PROBE"},
    )


def engine_diff(challenge) -> int:
    from adapt.content.types import engine_difficulty_to_product

    return engine_difficulty_to_product(challenge.difficulty)


def session_journey(session: TutorSession) -> dict[str, Any]:
    from adapt.product.journey import session_journey as build_journey

    return build_journey(session)


def session_insights(session: TutorSession) -> dict[str, Any]:
    traces = session.traces
    empty = {
        "title": "Learning insights",
        "good_at": None,
        "practice": None,
        "how_you_learn": None,
        "recent_change": None,
        "explore": None,
        "lines": [],
        "from_evidence": True,
    }
    if not traces:
        empty["how_you_learn"] = "No responses yet, so there is nothing to report."
        return empty
    by_concept: dict[str, list[StepTrace]] = defaultdict(list)
    for step in traces:
        by_concept[step.challenge.concept_id].append(step)
    ranked = sorted(
        by_concept.items(),
        key=lambda pair: pair[1][-1].state_after.mastery_estimate,
        reverse=True,
    )
    best_id, best_steps = ranked[0]
    worst_id, worst_steps = ranked[-1]
    strong_reason = sum(1 for step in traces if step.evidence.reasoning_quality == ReasoningQuality.STRONG)
    correct = sum(1 for step in traces if step.evidence.answer_status == AnswerStatus.CORRECT)
    conf_before = traces[0].state_before.confidence
    conf_after = traces[-1].state_after.confidence
    good = None
    if best_steps[-1].state_after.mastery_estimate >= 0.55 and any(
        item.evidence.answer_status == AnswerStatus.CORRECT for item in best_steps
    ):
        good = f"You have been consistent on {concept_label(best_id)}."
    practice = None
    if worst_id != best_id or best_steps[-1].state_after.mastery_estimate < 0.55:
        practice = f"{concept_label(worst_id)} is still less consistent."
    how = None
    if strong_reason >= 2:
        how = "You tend to perform better when you explain your approach."
    elif correct and strong_reason == 0:
        how = "Correct answers arrived, but there was little reasoning to interpret."
    recent = None
    if conf_after - conf_before > 0.05:
        recent = f"You are becoming more confident with {concept_label(best_id).lower()}."
    elif conf_before - conf_after > 0.05:
        recent = "Your confidence dipped during this session."
    recovered = any(
        step.decision == StrategyName.RECOVER
        or (
            step.evidence.misconception_signal is False
            and step.step_number > 1
            and any(prev.evidence.misconception_signal for prev in traces[: step.step_number - 1])
            and step.evidence.answer_status == AnswerStatus.CORRECT
        )
        for step in traces
    )
    if recovered and not recent:
        recent = f"You've recovered from a misconception in {concept_label(worst_id).lower()}."
    explore = None
    if worst_id and (worst_id != best_id or best_steps[-1].state_after.mastery_estimate < 0.55):
        explore = f"{concept_label(worst_id)} is still worth exploring."
    lines = [item for item in (good, how, recent, explore, practice) if item]
    return {
        "title": "Learning insights",
        "good_at": good,
        "practice": practice,
        "how_you_learn": how,
        "recent_change": recent,
        "explore": explore,
        "lines": lines,
        "from_evidence": True,
    }


def learner_progress_view(
    *,
    concept_mastery: dict[str, float],
    subject_id: str | None = None,
    activity: dict[str, dict[str, Any]] | None = None,
    session_completed: int = 0,
    session_concepts: list[str] | None = None,
) -> dict[str, Any]:
    from adapt.product.progress import learner_progress_view as build_progress

    return build_progress(
        concept_mastery=concept_mastery,
        activity=activity,
        subject_id=subject_id,
        session_completed=session_completed,
        session_concepts=session_concepts,
    )
