"""Phase 2 metrics, invariants, and scenario-suite smoke tests."""

from __future__ import annotations

import pytest

from adapt.models.enums import EvidenceStrength, StrategyName
from adapt.models.strategy import StrategyState
from adapt.strategy.invariants import (
    invariant_1_weak_evidence_not_high_mastery,
    invariant_4_successful_remediation_can_recover,
    invariant_5_equivalent_evidence_equivalent_strategy,
    invariant_9_oscillation_requires_evidence,
)
from benchmarks.phase2.metrics import compute_metrics
from benchmarks.phase2.scenarios import SCENARIOS
from tests.helpers_phase2 import decide, make_evidence, make_state


def test_at_least_sixty_phase2_scenarios():
    assert len(SCENARIOS) >= 60
    families = {item.family for item in SCENARIOS}
    assert len(families) >= 15


def test_wilson_payload_shape():
    metrics = compute_metrics(
        records=[
            {"appropriate": True, "family": "P2-001", "traceable": True, "concept": "basic_algebra", "unnecessary_transition": False},
            {"appropriate": True, "family": "P2-002", "traceable": True, "concept": "fractions", "unnecessary_transition": False},
        ],
        counterfactuals=[{"differentiated": True, "evidence_sensitive": True}],
        recovery_records=[{"recovered_strategy": True, "recovery_latency": 2}],
        cross_concept_records=[
            {"appropriate": True, "concept": "basic_algebra"},
            {"appropriate": True, "concept": "fractions"},
        ],
    )
    app = metrics["M2-001_strategy_appropriateness"]
    assert app["numerator"] == 2
    assert app["denominator"] == 2
    assert app["wilson_95"]
    assert "display" in app


def test_invariant_1_weak_evidence_cannot_high_mastery():
    assert invariant_1_weak_evidence_not_high_mastery(
        evidence_strength=EvidenceStrength.WEAK.value,
        mastery_before=0.5,
        mastery_after=0.53,
        strategy_confidence=0.4,
    )
    assert not invariant_1_weak_evidence_not_high_mastery(
        evidence_strength=EvidenceStrength.WEAK.value,
        mastery_before=0.5,
        mastery_after=0.8,
        strategy_confidence=0.9,
    )


def test_invariant_4_recovery():
    decision = decide(
        make_state(
            pattern="WWWCCC",
            mastery=0.7,
            misconceptions=(__import__("adapt.models.learner_state", fromlist=["MisconceptionRecord"]).MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
        ),
        make_evidence(),
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert invariant_4_successful_remediation_can_recover(decision)
    assert decision.decision != StrategyName.REMEDIATE


def test_invariant_5_determinism():
    state = make_state(pattern="CCCC")
    evidence = make_evidence()
    first = decide(state, evidence)
    second = decide(state, evidence)
    assert invariant_5_equivalent_evidence_equivalent_strategy(first, second)


def test_invariant_9_oscillation_string():
    assert invariant_9_oscillation_requires_evidence(["INCREASE", "PROBE", "MAINTAIN"])
    assert not invariant_9_oscillation_requires_evidence(["INCREASE", "DECREASE", "INCREASE"])


def test_phase2_metrics_traceability_target_field_exists():
    metrics = compute_metrics(
        records=[{"appropriate": True, "traceable": True, "family": "P2-001", "concept": "basic_algebra", "unnecessary_transition": False}],
        counterfactuals=[],
        recovery_records=[],
        cross_concept_records=[],
    )
    assert metrics["M2-006_strategy_traceability"]["rate"] == 1.0


def test_phase1_pipeline_default_does_not_use_strategy_engine():
    from adapt.pipeline import AdaptPipeline
    from tests.helpers import MEDIUM, STRONG_REASONING, make_response, new_state, run_one

    trace = run_one(
        new_state(),
        MEDIUM,
        make_response(
            response_id="P1",
            challenge_id=MEDIUM.challenge_id,
            answer="4",
            reasoning=STRONG_REASONING,
            learner_confidence=__import__("adapt.models.enums", fromlist=["LearnerConfidence"]).LearnerConfidence.HIGH,
        ),
        pipeline=AdaptPipeline(),
    )
    assert trace.strategy_decision is None


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item.scenario_id)
def test_phase2_scenario_strategy_is_appropriate(scenario):
    from benchmarks.phase2.evaluator import run_scenario

    record = run_scenario(scenario)
    assert record["traceable"]
    assert record["appropriate"], (
        f"{scenario.scenario_id} got {record['strategy']} "
        f"expected {scenario.expected_strategies} forbidden {scenario.forbidden_strategies}"
    )
