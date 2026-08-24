"""Learner-facing explanations generated from actual traces.

Presentation only. Does not choose strategy or the next challenge.
Never claims a misconception unless the step evidence contains the signal.
"""

from __future__ import annotations

from typing import Any

from adapt.content.catalog import CATALOG
from adapt.models.enums import AnswerStatus, Difficulty, ReasoningQuality, StrategyName
from adapt.product.present import concept_label, delta_arrow
from adapt.product.trace_explain import human_trace_explanation
from adapt.tutor.session import StepTrace

LEARNER_WHY = {
    StrategyName.INCREASE: (
        "You're showing strong understanding, so I'm making the next challenge harder."
    ),
    StrategyName.MAINTAIN: (
        "Your understanding looks steady, so I'm keeping the difficulty here."
    ),
    StrategyName.PROBE: (
        "Your recent answers are mixed, so I'm checking one more thing before changing difficulty."
    ),
    StrategyName.REMEDIATE: (
        "This idea needs another approach, so we're going to work on it directly."
    ),
    StrategyName.GATHER_EVIDENCE: (
        "I need a little more evidence before deciding what to change."
    ),
    StrategyName.DECREASE: (
        "This level looks too hard right now, so I'm stepping back to rebuild the idea."
    ),
    StrategyName.ASSESS: (
        "I'm still getting a first picture of how you approach this."
    ),
    StrategyName.RECOVER: (
        "Your recent responses improved, so we can move forward from here."
    ),
}

LEARNER_DOING = {
    StrategyName.INCREASE: "↗ Increasing difficulty",
    StrategyName.MAINTAIN: "◎ Staying at this level",
    StrategyName.PROBE: "◎ Probing",
    StrategyName.REMEDIATE: "↻ Remediating",
    StrategyName.GATHER_EVIDENCE: "◎ Gathering evidence",
    StrategyName.DECREASE: "↘ Simplifying",
    StrategyName.ASSESS: "◎ Seeing how you approach this",
    StrategyName.RECOVER: "↗ Moving forward",
}

LEARNER_MOMENT = {
    StrategyName.INCREASE: "You're ready for a bigger challenge.",
    StrategyName.MAINTAIN: "Let's stay here and keep practicing.",
    StrategyName.PROBE: "Let's check your understanding from another angle.",
    StrategyName.REMEDIATE: "Let's work on this idea before moving on.",
    StrategyName.GATHER_EVIDENCE: "ADAPT needs a little more evidence first.",
    StrategyName.DECREASE: "Let's rebuild this from a simpler version.",
    StrategyName.ASSESS: "This opening question helps ADAPT see how you think.",
    StrategyName.RECOVER: "Your recent answers improved, so we can move forward.",
}

LEARNER_NEXT = {
    StrategyName.INCREASE: "A slightly harder challenge",
    StrategyName.MAINTAIN: "Another challenge at this level",
    StrategyName.PROBE: "A check from a different angle",
    StrategyName.REMEDIATE: "A focused practice question",
    StrategyName.GATHER_EVIDENCE: "One more observation",
    StrategyName.DECREASE: "A simpler version of the idea",
    StrategyName.ASSESS: "An opening challenge",
    StrategyName.RECOVER: "A challenge that moves you forward",
}


def _first_sentences(text: str, *, limit: int = 2) -> str:
    raw = " ".join(str(text or "").split())
    if not raw:
        return ""
    parts: list[str] = []
    buf = ""
    for char in raw:
        buf += char
        if char in ".!?":
            parts.append(buf.strip())
            buf = ""
            if len(parts) >= limit:
                break
    if buf.strip() and len(parts) < limit:
        parts.append(buf.strip())
    return " ".join(parts)


def why_from_strategy(step: StepTrace) -> str:
    evidence = step.evidence
    decision = step.decision
    if decision == StrategyName.REMEDIATE and evidence.misconception_signal:
        return (
            "I noticed the same misunderstanding more than once, "
            "so we're going to work on it directly."
        )
    if decision == StrategyName.PROBE:
        if evidence.reasoning_quality == ReasoningQuality.WEAK:
            return (
                "Your answer was correct, but the reasoning was thin, "
                "so I'm checking one more thing before changing difficulty."
            )
        if evidence.confidence_signal.value == "LOW":
            return (
                "You seemed unsure, so I'm checking one more thing before changing difficulty."
            )
        if evidence.answer_status == AnswerStatus.CORRECT:
            return (
                "The recent evidence is mixed, so I'm checking one more thing before changing difficulty."
            )
    if decision == StrategyName.INCREASE:
        if (
            evidence.answer_status == AnswerStatus.CORRECT
            and evidence.confidence_signal.value == "HIGH"
        ):
            return "You're showing strong understanding, so I'm making the next challenge harder."
    return LEARNER_WHY.get(decision, "This next question follows from what ADAPT observed.")


def noticed_from_evidence(step: StepTrace) -> str:
    evidence = step.evidence
    correct = evidence.answer_status == AnswerStatus.CORRECT
    conf = evidence.confidence_signal.value
    reason = evidence.reasoning_quality
    trajectory = step.state_after.learning_trajectory.value
    parts: list[str] = []
    if correct and conf == "HIGH":
        parts.append("You answered correctly with high confidence.")
    elif correct and conf == "LOW":
        parts.append("You got this right, but you did not feel sure.")
    elif correct:
        parts.append("You answered correctly.")
    elif evidence.answer_status == AnswerStatus.PARTIAL:
        parts.append("This answer was only partly on track.")
    else:
        parts.append("This one did not land.")
    if reason == ReasoningQuality.STRONG:
        parts.append("Your approach showed clear thinking.")
    elif reason == ReasoningQuality.WEAK:
        parts.append("There was little reasoning to interpret.")
    elif reason == ReasoningQuality.MODERATE:
        parts.append("Your approach was partly visible.")
    if evidence.misconception_signal:
        concept = concept_label(step.challenge.concept_id)
        parts.append(f"This may be a misunderstanding about {concept.lower()}.")
    if trajectory == "IMPROVING" and step.step_number > 1:
        parts.append("Your recent answers show improving understanding.")
    elif trajectory == "REGRESSING" and step.step_number > 1:
        parts.append("Recent answers suggest this idea got harder.")
    elif trajectory == "OSCILLATING" and step.step_number > 1:
        parts.append("Recent answers have been mixed.")
    return " ".join(parts)


def thinks_from_state(step: StepTrace) -> str:
    arrow = delta_arrow(step.state_before.mastery_estimate, step.state_after.mastery_estimate)
    if arrow == "up":
        return "Your understanding of this idea looks stronger."
    if arrow == "down":
        return "This idea still looks shaky."
    if step.state_after.uncertainty.value in {"HIGH_UNCERTAINTY", "INSUFFICIENT_EVIDENCE"}:
        return "ADAPT still does not have a firm picture of this idea."
    return "ADAPT's picture of your understanding did not shift much yet."


def educational_text(step: StepTrace) -> str:
    meta = CATALOG.challenge(step.challenge_id)
    if meta is None:
        return ""
    text = str(meta.explanation or "").strip()
    extra = str(meta.learn_more or "").strip()
    if extra and extra not in text:
        return f"{text} {extra}".strip()
    return text


def learner_explanation(step: StepTrace) -> dict[str, Any]:
    evidence = step.evidence
    meta = CATALOG.challenge(step.challenge_id)
    explain = human_trace_explanation(step)
    teaching = educational_text(step)
    noticed = noticed_from_evidence(step)
    why_next = why_from_strategy(step)
    correct = evidence.answer_status == AnswerStatus.CORRECT
    if correct:
        headline = "Correct"
        short = noticed
        detailed = " ".join(
            part
            for part in (
                noticed,
                explain.get("evidence_detail"),
                explain.get("state"),
                teaching,
            )
            if part
        )
    else:
        headline = "Not quite."
        key_idea = _first_sentences(teaching, limit=2)
        short = "Not quite."
        if key_idea:
            short = f"Not quite. {key_idea}"
        elif teaching:
            short = f"Not quite. {teaching}"
        if evidence.misconception_signal:
            concept = concept_label(step.challenge.concept_id)
            if "misunderstanding" not in short.lower():
                short = f"{short} ADAPT noticed that this may be a misunderstanding about {concept.lower()}."
        detailed = " ".join(
            part
            for part in (
                short,
                teaching if teaching and teaching not in short else "",
                explain.get("evidence_detail"),
                explain.get("state"),
            )
            if part
        )
    misconception_mentioned = bool(evidence.misconception_signal)
    return {
        "headline": headline,
        "short_message": short,
        "detailed_message": detailed.strip(),
        "why_next": why_next,
        "noticed": noticed,
        "from_trace": True,
        "answer_status": evidence.answer_status.value,
        "misconception_mentioned": misconception_mentioned,
        "misconception_signal": evidence.misconception_signal,
        "decision": step.decision.value,
        "teaching": teaching,
        "concept": concept_label(step.challenge.concept_id),
        "challenge_type": (
            meta.challenge_type if meta is not None else step.challenge.challenge_type.value
        ),
    }


def learner_adaptation_chain(step: StepTrace) -> dict[str, Any]:
    explanation = learner_explanation(step)
    nxt = step.next_challenge
    next_text = LEARNER_NEXT.get(step.decision, "The next challenge")
    if nxt.challenge_id == "UNAVAILABLE":
        next_text = "No further challenge was available."
    elif nxt.difficulty == Difficulty.HARD and step.challenge.difficulty != Difficulty.HARD:
        next_text = "A harder challenge"
    elif nxt.difficulty == Difficulty.EASY and step.challenge.difficulty != Difficulty.EASY:
        next_text = "A simpler challenge"
    return {
        "title": "How ADAPT adapted",
        "from_trace": True,
        "moment": {
            "response": "Your response",
            "noticed": "ADAPT noticed",
            "next": "Your next step",
        },
        "noticed": {
            "title": "What ADAPT noticed",
            "text": explanation["noticed"],
        },
        "thinks": {
            "title": "What ADAPT thinks",
            "text": thinks_from_state(step),
        },
        "doing": {
            "title": "What ADAPT is doing",
            "text": LEARNER_DOING.get(step.decision, "Choosing the next challenge"),
        },
        "next": {
            "title": "What's next",
            "text": next_text,
        },
        "why_next": explanation["why_next"],
        "decision": step.decision.value,
        "moment_copy": LEARNER_MOMENT.get(step.decision, explanation["why_next"]),
    }


def research_chain_labels() -> list[str]:
    return ["Evidence", "Learner State", "Strategy", "Next Challenge"]
