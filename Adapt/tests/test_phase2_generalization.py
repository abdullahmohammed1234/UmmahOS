"""Cross-concept generalization and G-001-B regression."""

from __future__ import annotations

from pathlib import Path

from adapt.models.enums import (
    AnswerStatus,
    ErrorPattern,
    EvidencePolarity,
    EvidenceStrength,
    StrategyName,
)
from adapt.models.learner_state import MisconceptionRecord
from adapt.models.strategy import StrategyState
from benchmarks.phase1f.evaluator import run_adapt
from benchmarks.phase1f.scenarios import SCENARIO_BY_ID
from tests.helpers_phase2 import decide, make_evidence, make_state, phase2_pipeline

STRATEGY_DIR = Path(__file__).resolve().parents[1] / "src" / "adapt" / "strategy"


def test_strategy_package_has_no_hardcoded_concept_names():
    banned = ("basic_algebra", "fractions", 'concept ==', "concept_id ==")
    for path in STRATEGY_DIR.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in banned:
            assert token not in text, f"{path.name} contains {token!r}"


def test_equivalent_evidence_on_two_concepts_matches():
    algebra = make_state(
        pattern="CCCCW",
        mastery=0.7,
        concept_id="basic_algebra",
        misconceptions=(MisconceptionRecord("DIST_PROP", 1, "SUSPECTED"),),
    )
    fractions = make_state(
        pattern="CCCCW",
        mastery=0.7,
        concept_id="fractions",
        misconceptions=(MisconceptionRecord("ADD_DENOM", 1, "SUSPECTED"),),
    )
    alg_ev = make_evidence(
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="DIST_PROP",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    frac_ev = make_evidence(
        response_id="R-F",
        answer_status=AnswerStatus.INCORRECT,
        polarity=EvidencePolarity.NEGATIVE,
        misconception_signal="ADD_DENOM",
        error_type=ErrorPattern.CONCEPTUAL,
        evidence_strength=EvidenceStrength.MODERATE,
    )
    a = decide(algebra, alg_ev, strategy=StrategyState(current_strategy=StrategyName.MAINTAIN))
    b = decide(fractions, frac_ev, strategy=StrategyState(current_strategy=StrategyName.MAINTAIN))
    assert a.decision == b.decision


def test_g001_b_does_not_force_increase_without_strong_evidence():
    """Phase 1F expected INCREASE. The subtraction item uses addition reasoning cues.

    Phase 2 must not relabel MAINTAIN as INCREASE just to match the old benchmark.
    """
    record = run_adapt(SCENARIO_BY_ID["G-001-B"], phase2_pipeline())
    strategy = record["decision_trace"]["strategy_decision"]["decision"]
    evidence = record["evidence"]
    assert evidence["reasoning_quality"] != "STRONG" or evidence["evidence_strength"] != "STRONG" or strategy in {
        "INCREASE",
        "MAINTAIN",
        "PROBE",
        "GATHER_EVIDENCE",
    }
    if evidence["reasoning_quality"] != "STRONG":
        assert strategy != "INCREASE"


def test_g001_a_strong_fraction_evidence_can_increase():
    record = run_adapt(SCENARIO_BY_ID["G-001-A"], phase2_pipeline())
    strategy = record["decision_trace"]["strategy_decision"]["decision"]
    evidence = record["evidence"]
    if evidence["reasoning_quality"] == "STRONG" and evidence["evidence_strength"] == "STRONG":
        assert strategy in {"INCREASE", "MAINTAIN"}


def test_g001_b_phase1f_failure_has_dedicated_hypothesis():
    record = run_adapt(SCENARIO_BY_ID["G-001-B"], phase2_pipeline())
    reason = record["decision_trace"]["strategy_decision"]["reason"]
    assert reason
    assert record["decision_trace"]["strategy_decision"]["evidence_ids"]


def test_algebra_and_fractions_recovery_use_same_rule():
    alg = decide(
        make_state(
            pattern="WWWCCC",
            concept_id="basic_algebra",
            misconceptions=(MisconceptionRecord("DIST_PROP", 3, "REPEATED"),),
            mastery=0.7,
        ),
        make_evidence(),
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    frac = decide(
        make_state(
            pattern="WWWCCC",
            concept_id="fractions",
            misconceptions=(MisconceptionRecord("ADD_DENOM", 3, "REPEATED"),),
            mastery=0.7,
        ),
        make_evidence(response_id="R-F"),
        strategy=StrategyState(current_strategy=StrategyName.REMEDIATE),
    )
    assert alg.decision == frac.decision
    assert alg.decision != StrategyName.REMEDIATE
