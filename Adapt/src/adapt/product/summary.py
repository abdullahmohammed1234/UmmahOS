"""Session summary derived only from actual session traces."""

from __future__ import annotations

from collections import Counter
from typing import Any

from adapt.product.present import concept_label
from adapt.tutor.session import TutorSession


def session_summary(session: TutorSession, *, max_steps: int) -> dict[str, Any]:
    traces = session.traces
    concepts = []
    seen_concepts: set[str] = set()
    for step in traces:
        cid = step.challenge.concept_id
        if cid not in seen_concepts:
            seen_concepts.add(cid)
            concepts.append(cid)
    if session.concept_id not in seen_concepts:
        concepts.insert(0, session.concept_id)
        seen_concepts.add(session.concept_id)

    strategies = [step.decision.value for step in traces]
    unique_strategies = list(dict.fromkeys(strategies))
    adjustments = sum(
        1
        for step in traces
        if step.strategy_before.current_strategy != step.strategy_after.current_strategy
    )

    strongest = None
    keep_practicing = None
    if traces:
        by_concept: dict[str, list[float]] = {}
        for step in traces:
            by_concept.setdefault(step.challenge.concept_id, []).append(
                step.state_after.mastery_estimate
            )
        ranked = sorted(
            ((cid, values[-1]) for cid, values in by_concept.items()),
            key=lambda item: item[1],
            reverse=True,
        )
        strongest = concept_label(ranked[0][0])
        keep_practicing = concept_label(ranked[-1][0]) if len(ranked) > 1 else strongest

    return {
        "title": "Your ADAPT session",
        "challenges_completed": len(traces),
        "max_steps": max_steps,
        "concepts_explored": len(seen_concepts),
        "concept_names": [concept_label(item) for item in concepts],
        "strategies_used": len(unique_strategies),
        "strategy_names": unique_strategies,
        "strongest_area": strongest,
        "area_to_keep_practicing": keep_practicing,
        "adapt_adjusted_path": adjustments,
        "final_strategy": session.strategy_state.current_strategy.value,
        "strategy_counts": dict(Counter(strategies)),
    }
