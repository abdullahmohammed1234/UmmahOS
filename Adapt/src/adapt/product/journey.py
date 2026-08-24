"""Learning-journey presentation from recorded session and catalog state."""

from __future__ import annotations

from typing import Any

from adapt.content.catalog import CATALOG
from adapt.product.explanations import learner_explanation, why_from_strategy
from adapt.product.present import concept_label
from adapt.product.progress import STATUS_LABELS, derive_status
from adapt.product.trace_explain import human_trace_explanation
from adapt.tutor.session import TutorSession


def journey_stages(session: TutorSession) -> list[dict[str, Any]]:
    """Learner-facing path. Does not claim mastery from mere completion."""
    traces = session.traces
    increased = any(step.decision.value == "INCREASE" for step in traces)
    remediated = any(step.decision.value == "REMEDIATE" for step in traces)
    strong = False
    if traces:
        last = traces[-1].state_after
        strong = last.mastery_estimate >= 0.7 and last.evidence_strength.value in {"MODERATE", "STRONG"}
    current_name = concept_label(session.concept_id)
    if traces:
        current_name = concept_label(session.current_challenge.concept_id)
    stages = [
        {
            "id": "foundations",
            "name": "Foundations",
            "status": "completed" if traces else "in_progress",
            "marker": "✓" if traces else "◉",
        },
        {
            "id": "core",
            "name": "Core concept",
            "status": "completed" if traces else "upcoming",
            "marker": "✓" if traces else "○",
        },
        {
            "id": "current",
            "name": current_name or "Current challenge",
            "status": "in_progress",
            "marker": "◉",
        },
        {
            "id": "advanced",
            "name": "Advanced application",
            "status": "completed" if increased else "upcoming",
            "marker": "✓" if increased else "○",
        },
        {
            "id": "check",
            "name": "Mastery check",
            "status": "completed" if strong else "upcoming",
            "marker": "✓" if strong else "○",
            "note": None
            if strong
            else "Shown only as a path marker — not a claim that the idea is mastered.",
        },
    ]
    if remediated:
        stages[1]["name"] = "Core concept (rebuilding)"
    return stages


def session_journey(session: TutorSession) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    opening = (
        session.traces[0].strategy_before.current_strategy.value
        if session.traces
        else session.strategy_state.current_strategy.value
    )
    steps.append(
        {
            "id": "start",
            "step": 0,
            "kind": "start",
            "status": "completed",
            "status_label": "Completed",
            "name": concept_label(session.concept_id),
            "strategy": opening,
            "label": opening,
            "evidence": "Opening state",
            "state": "ADAPT is ready to observe how you learn.",
            "strategy_text": "See how you approach this",
            "challenge_id": session.current_challenge.challenge_id if not session.traces else session.traces[0].challenge_id,
        }
    )
    seen: set[str] = set()
    for step in session.traces:
        explain = human_trace_explanation(step)
        learner = learner_explanation(step)
        name = concept_label(step.challenge.concept_id)
        seen.add(step.challenge.concept_id)
        steps.append(
            {
                "id": f"step-{step.step_number}",
                "step": step.step_number,
                "kind": "decision",
                "status": "completed",
                "status_label": "Completed",
                "name": name,
                "strategy": step.decision.value,
                "label": name,
                "changed": step.strategy_before.current_strategy != step.strategy_after.current_strategy,
                "evidence": explain["evidence"],
                "state": explain["state"],
                "strategy_text": why_from_strategy(step),
                "challenge_id": step.challenge_id,
                "next_challenge_id": step.next_challenge_id,
                "prompt": step.challenge.question,
                "noticed": learner["noticed"],
            }
        )
    current_name = concept_label(session.concept_id)
    if session.traces:
        current_name = concept_label(session.current_challenge.concept_id)
        steps.append(
            {
                "id": "current",
                "step": session.step_number + 1,
                "kind": "current",
                "status": "in_progress",
                "status_label": "In Progress",
                "name": current_name,
                "strategy": session.strategy_state.current_strategy.value,
                "label": current_name,
                "challenge_id": session.current_challenge.challenge_id,
            }
        )
    return {
        "title": "Your Journey",
        "steps": steps,
        "concepts_seen": [concept_label(cid) for cid in seen] or [concept_label(session.concept_id)],
        "stages": journey_stages(session),
    }


def catalog_journey(
    *,
    subject_id: str | None,
    concept_mastery: dict[str, float],
    activity: dict[str, dict[str, Any]] | None = None,
    recommended_id: str | None = None,
) -> dict[str, Any]:
    activity = activity or {}
    focus = subject_id or "mathematics"
    concepts = CATALOG.concepts_for_subject(focus)
    subject = CATALOG.subject(focus)
    steps = []
    for concept in concepts:
        mastery = concept_mastery.get(concept.concept_id)
        info = activity.get(concept.concept_id) or {}
        status = derive_status(
            mastery,
            attempts=int(info.get("attempts") or 0),
            last_correct=info.get("last_correct"),
        )
        if recommended_id == concept.concept_id and status == "new":
            status = "new"
            marker = "recommended"
            label = "Recommended"
        elif status == "completed":
            marker = "completed"
            label = STATUS_LABELS[status]
        elif status == "new":
            marker = "new"
            label = "New"
        else:
            marker = "in_progress"
            label = STATUS_LABELS[status]
        if recommended_id == concept.concept_id:
            marker = "recommended" if status == "new" else marker
            if status == "new":
                label = "Recommended"
        steps.append(
            {
                "id": concept.concept_id,
                "kind": "concept",
                "name": concept.name,
                "description": concept.description,
                "status": status,
                "status_label": label,
                "marker": marker,
                "topic_id": concept.topic_id,
                "subject_id": concept.subject_id,
                "recommended": concept.concept_id == recommended_id,
                "progress_percent": None if mastery is None else int(round(mastery * 100)),
            }
        )
    return {
        "title": "Your Journey",
        "subject": None if subject is None else subject.name,
        "subject_id": focus,
        "steps": steps,
        "empty": not concept_mastery,
        "disclaimer": (
            "This journey reflects concepts in the catalog and any recorded visit progress. "
            "Unstarted concepts are marked New."
        ),
    }
