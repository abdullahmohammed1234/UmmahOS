"""Phase 7 benchmark scenarios."""

from __future__ import annotations

from adapt.models.enums import AdaptationAction, StrategyName

SELECTION_CASES = (
    {
        "id": "P7-SEL-INCREASE",
        "topic_id": "cs-algorithms",
        "initial": "CS-ALG-001",
        "action": AdaptationAction.INCREASE_DIFFICULTY,
        "strategy": StrategyName.INCREASE,
    },
    {
        "id": "P7-SEL-PROBE",
        "topic_id": "cs-algorithms",
        "initial": "CS-ALG-001",
        "action": AdaptationAction.PROBE_UNCERTAINTY,
        "strategy": StrategyName.PROBE,
    },
    {
        "id": "P7-SEL-REMEDIATE",
        "topic_id": "cs-algorithms",
        "initial": "CS-ALG-008",
        "action": AdaptationAction.REMEDIATE,
        "strategy": StrategyName.REMEDIATE,
    },
)
