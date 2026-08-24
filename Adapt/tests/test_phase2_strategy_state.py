"""Strategy state is explicit and separate from mastery."""

from __future__ import annotations

import pytest

from adapt.errors import InvalidStrategyDecisionError, InvalidStrategyStateError
from adapt.models.enums import StrategyName
from adapt.models.strategy import (
    StrategyDecision,
    StrategyState,
    StrategyTransition,
    initial_strategy_state,
)
from tests.helpers_phase2 import decide, make_evidence, make_state


def test_initial_strategy_is_assess_not_mastery():
    state = initial_strategy_state()
    assert state.current_strategy == StrategyName.ASSESS
    assert state.previous_strategy is None
    assert state.strategy_confidence <= 0.3


def test_strategy_state_serializes():
    state = StrategyState(
        current_strategy=StrategyName.REMEDIATE,
        previous_strategy=StrategyName.PROBE,
        strategy_confidence=0.82,
        transition_reason="Two consecutive successful remediation responses",
        transition_evidence=("E-014",),
    )
    restored = StrategyState.from_dict(state.to_dict())
    assert restored.current_strategy == StrategyName.REMEDIATE
    assert restored.previous_strategy == StrategyName.PROBE
    assert restored.strategy_confidence == pytest.approx(0.82)


def test_mastery_is_not_strategy():
    learner = make_state(pattern="CCCC", mastery=0.8)
    evidence = make_evidence()
    decision = decide(learner, evidence)
    assert "mastery_estimate" in decision.state_snapshot
    assert decision.decision != learner.mastery_estimate
    assert decision.current_strategy in StrategyName


def test_same_mastery_different_strategy_history_can_differ():
    learner = make_state(
        pattern="CCCWCC",
        mastery=0.7,
        misconceptions=(),
    )
    evidence = make_evidence()
    maintain = decide(
        learner,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.MAINTAIN),
    )
    remediate = decide(
        learner,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert maintain.decision != remediate.decision or maintain.reason != remediate.reason


def test_invalid_confidence_rejected():
    with pytest.raises(InvalidStrategyStateError):
        StrategyState(current_strategy=StrategyName.PROBE, strategy_confidence=1.5)


def test_decision_requires_reason_and_evidence():
    with pytest.raises(InvalidStrategyDecisionError):
        StrategyTransition(
            from_strategy=StrategyName.MAINTAIN,
            to_strategy=StrategyName.PROBE,
            reason="",
            evidence_ids=("E-1",),
        )


def test_all_required_strategy_names_exist():
    required = {
        "ASSESS",
        "PROBE",
        "MAINTAIN",
        "INCREASE",
        "DECREASE",
        "REMEDIATE",
        "RECOVER",
        "GATHER_EVIDENCE",
    }
    assert required.issubset({item.value for item in StrategyName})


def test_strategy_decision_contains_contract_fields():
    decision = decide(make_state(pattern="C"), make_evidence(evidence_strength=__import__("adapt.models.enums", fromlist=["EvidenceStrength"]).EvidenceStrength.INSUFFICIENT))
    payload = decision.to_dict()
    for key in (
        "decision",
        "reason",
        "current_strategy",
        "previous_strategy",
        "evidence_ids",
        "state_snapshot",
        "confidence",
        "transition",
    ):
        assert key in payload
    assert payload["evidence_ids"]


def test_recover_is_internal_not_required_as_final_action():
    from adapt.models.learner_state import MisconceptionRecord

    state = make_state(
        pattern="WWWCCC",
        mastery=0.7,
        misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
    )
    evidence = make_evidence()
    decision = decide(
        state,
        evidence,
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert decision.decision != StrategyName.RECOVER
    assert "internal_recover" in decision.reason_codes or decision.decision != StrategyName.REMEDIATE
