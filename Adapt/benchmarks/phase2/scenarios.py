"""Phase 2 scenario suite. Does not modify Phase 1F scenarios."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.models.enums import LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from benchmarks.phase1f.challenge_bank import get_challenge
from benchmarks.phase1f.scenarios import (
    ADD_MISC,
    COMBINE_MISC,
    DIST_MISC,
    STRONG_ALG,
    STRONG_ALG_B,
    STRONG_FRAC,
    STRONG_FRAC_B,
    STRONG_M003,
    WEAK,
    GUESS,
    ARITH,
)
from benchmarks.phase2.constants import (
    CONSERVATIVE,
    DECREASE_FAMILY,
    NO_ESCALATE,
    PROBE_FAMILY,
    RECOVERY_FAMILY,
    REMEDIATE_FAMILY,
)


@dataclass(frozen=True)
class HistoryStep:
    challenge_id: str
    answer: str
    reasoning: str | None
    learner_confidence: str


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    family: str
    concept: str
    category: str
    history: tuple[HistoryStep, ...]
    current_challenge_id: str
    current_answer: str
    current_reasoning: str | None
    current_confidence: str
    expected_strategies: tuple[str, ...]
    forbidden_strategies: tuple[str, ...]
    expected_behavior: str
    variant: str
    evidence_dimensions: tuple[str, ...] = ()
    tags: tuple[str, ...] = field(default_factory=tuple)
    recovery_scenario: bool = False
    regression_scenario: bool = False
    misconception_scenario: bool = False
    stability_scenario: bool = False
    sparse_scenario: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "family": self.family,
            "concept": self.concept,
            "category": self.category,
            "expected_strategies": list(self.expected_strategies),
            "expected_behavior": self.expected_behavior,
            "variant": self.variant,
        }


def make_response(
    *,
    response_id: str,
    learner_id: str,
    challenge_id: str,
    answer: str,
    reasoning: str | None,
    confidence: str,
) -> LearnerResponse:
    challenge = get_challenge(challenge_id)
    return LearnerResponse(
        response_id=response_id,
        learner_id=learner_id,
        concept_id=challenge.concept_id,
        challenge_id=challenge_id,
        answer=answer,
        reasoning=reasoning,
        learner_confidence=LearnerConfidence(confidence),
    )


def scenario_steps(scenario: Scenario, learner_id: str):
    pairs = []
    for index, step in enumerate(scenario.history, start=1):
        pairs.append(
            (
                get_challenge(step.challenge_id),
                make_response(
                    response_id=f"{scenario.scenario_id}-H{index:02d}",
                    learner_id=learner_id,
                    challenge_id=step.challenge_id,
                    answer=step.answer,
                    reasoning=step.reasoning,
                    confidence=step.learner_confidence,
                ),
            )
        )
    pairs.append(
        (
            get_challenge(scenario.current_challenge_id),
            make_response(
                response_id=f"{scenario.scenario_id}-CUR",
                learner_id=learner_id,
                challenge_id=scenario.current_challenge_id,
                answer=scenario.current_answer,
                reasoning=scenario.current_reasoning,
                confidence=scenario.current_confidence,
            ),
        )
    )
    return pairs


def _hs(cid: str, answer: str, reasoning: str | None, conf: str) -> HistoryStep:
    return HistoryStep(cid, answer, reasoning, conf)


def _sc(
    scenario_id: str,
    family: str,
    category: str,
    challenge_id: str,
    history: tuple[HistoryStep, ...],
    answer: str,
    reasoning: str | None,
    confidence: str,
    expected: tuple[str, ...],
    forbidden: tuple[str, ...],
    behavior: str,
    variant: str,
    **flags,
) -> Scenario:
    challenge = get_challenge(challenge_id)
    return Scenario(
        scenario_id=scenario_id,
        family=family,
        concept=challenge.concept_id,
        category=category,
        history=history,
        current_challenge_id=challenge_id,
        current_answer=answer,
        current_reasoning=reasoning,
        current_confidence=confidence,
        expected_strategies=expected,
        forbidden_strategies=forbidden,
        expected_behavior=behavior,
        variant=variant,
        **flags,
    )


def build_scenarios() -> tuple[Scenario, ...]:
    out: list[Scenario] = []

    # P2-001 Delayed misconception after a strong streak
    for sid, n_strong, cid, ans, reason, misc_cid, misc_ans, misc_r, variant in (
        ("P2-001-A", 4, "ALG-M-001", "4", STRONG_ALG, "ALG-D-001", "2x+3", DIST_MISC, "a"),
        ("P2-001-B", 4, "FR-M-001", "5/6", STRONG_FRAC, "FR-D-001", "2/5", ADD_MISC, "b"),
        ("P2-001-C", 4, "ALG-M-003", "3", STRONG_M003, "ALG-D-001", "2x+3", DIST_MISC, "c"),
        ("P2-001-D", 4, "FR-E-001", "1", STRONG_FRAC, "FR-D-001", "2/5", ADD_MISC, "d"),
    ):
        hist = tuple(_hs(cid, ans, reason, "HIGH") for _ in range(n_strong)) + (
            _hs(misc_cid, misc_ans, misc_r, "HIGH"),
        )
        out.append(
            _sc(
                sid, "P2-001", "delayed_misconception", misc_cid, hist, misc_ans, misc_r, "HIGH",
                PROBE_FAMILY, ("DECREASE", "INCREASE"),
                "A delayed misconception after a strong history should be probed, not treated as global regression",
                variant, misconception_scenario=True,
                evidence_dimensions=("correctness", "history", "misconception"),
                tags=("g003",),
            )
        )

    # P2-002 Global regression
    for sid, cid, ans, reason, variant in (
        ("P2-002-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-002-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-002-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("P2-002-D", "FR-E-001", "1", STRONG_FRAC, "d"),
    ):
        hist = tuple(_hs(cid, ans, reason, "HIGH") for _ in range(3)) + tuple(
            _hs(cid, "0", GUESS, "LOW") for _ in range(2)
        )
        out.append(
            _sc(
                sid, "P2-002", "global_regression", cid, hist, "0", GUESS, "LOW",
                DECREASE_FAMILY, ("INCREASE",),
                "Repeated weak failures after a collapse should reduce difficulty or gather evidence",
                variant, regression_scenario=True,
                evidence_dimensions=("correctness", "reasoning", "confidence", "history"),
            )
        )

    # P2-003 Temporary error
    for sid, cid, ans, reason, variant in (
        ("P2-003-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-003-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-003-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("P2-003-D", "FR-E-001", "1", STRONG_FRAC, "d"),
    ):
        hist = (
            _hs(cid, ans, reason, "HIGH"),
            _hs(cid, ans, reason, "HIGH"),
            _hs(cid, "0", "I blanked for a moment.", "LOW"),
            _hs(cid, ans, reason, "HIGH"),
        )
        out.append(
            _sc(
                sid, "P2-003", "temporary_error", cid, hist, ans, reason, "HIGH",
                CONSERVATIVE + ("INCREASE",), ("DECREASE", "REMEDIATE"),
                "A single unreplicated miss must not force a strategy collapse",
                variant, stability_scenario=True,
                evidence_dimensions=("correctness", "history"),
            )
        )

    # P2-004 Misconception recovery
    for sid, misc_cid, misc_ans, misc_r, cid, ans, reason, variant in (
        ("P2-004-A", "ALG-D-001", "2x+3", DIST_MISC, "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-004-B", "FR-D-001", "2/5", ADD_MISC, "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-004-C", "ALG-D-001", "2x+3", DIST_MISC, "ALG-M-003", "3", STRONG_M003, "c"),
        ("P2-004-D", "FR-D-001", "2/5", ADD_MISC, "FR-M-002", "1/2", STRONG_FRAC_B, "d"),
    ):
        hist = tuple(_hs(misc_cid, misc_ans, misc_r, "HIGH") for _ in range(3)) + tuple(
            _hs(cid, ans, reason, "HIGH") for _ in range(2)
        )
        out.append(
            _sc(
                sid, "P2-004", "misconception_recovery", cid, hist, ans, reason, "HIGH",
                RECOVERY_FAMILY, ("REMEDIATE", "DECREASE"),
                "After sufficient recovery evidence, strategy should leave REMEDIATE",
                variant, recovery_scenario=True,
                evidence_dimensions=("misconception", "correctness", "reasoning"),
                tags=("g005",),
            )
        )

    # P2-005 Failed remediation
    for sid, misc_cid, misc_ans, misc_r, variant in (
        ("P2-005-A", "ALG-D-001", "2x+3", DIST_MISC, "a"),
        ("P2-005-B", "FR-D-001", "2/5", ADD_MISC, "b"),
        ("P2-005-C", "ALG-D-003", "5x", COMBINE_MISC, "c"),
        ("P2-005-D", "FR-D-001", "2/5", ADD_MISC, "d"),
    ):
        hist = tuple(_hs(misc_cid, misc_ans, misc_r, "HIGH") for _ in range(4))
        out.append(
            _sc(
                sid, "P2-005", "failed_remediation", misc_cid, hist, misc_ans, misc_r, "HIGH",
                REMEDIATE_FAMILY, ("INCREASE",),
                "Continuing misconception evidence should keep remediation",
                variant, misconception_scenario=True,
                evidence_dimensions=("misconception", "history"),
            )
        )

    # P2-006 Successful remediation
    for sid, misc_cid, misc_ans, misc_r, cid, ans, reason, variant in (
        ("P2-006-A", "ALG-D-001", "2x+3", DIST_MISC, "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-006-B", "FR-D-001", "2/5", ADD_MISC, "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-006-C", "ALG-D-003", "5x", COMBINE_MISC, "ALG-M-003", "3", STRONG_M003, "c"),
        ("P2-006-D", "FR-D-001", "2/5", ADD_MISC, "FR-E-001", "1", STRONG_FRAC, "d"),
    ):
        hist = tuple(_hs(misc_cid, misc_ans, misc_r, "HIGH") for _ in range(3)) + tuple(
            _hs(cid, ans, reason, "HIGH") for _ in range(2)
        )
        out.append(
            _sc(
                sid, "P2-006", "successful_remediation", cid, hist, ans, reason, "HIGH",
                RECOVERY_FAMILY, ("REMEDIATE",),
                "Successful remediation must permit strategy recovery",
                variant, recovery_scenario=True,
                evidence_dimensions=("misconception", "correctness", "reasoning", "confidence"),
            )
        )

    # P2-007 Strategy oscillation
    for sid, cid, ans, reason, variant in (
        ("P2-007-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-007-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-007-C", "ALG-M-004", "8", STRONG_ALG_B, "c"),
        ("P2-007-D", "FR-E-002", "1/2", STRONG_FRAC, "d"),
    ):
        hist = tuple(_hs(cid, ans, reason, "HIGH") for _ in range(3)) + (
            _hs(cid, "0", "typo slip", "MODERATE"),
        )
        out.append(
            _sc(
                sid, "P2-007", "strategy_oscillation", cid, hist, ans, reason, "HIGH",
                CONSERVATIVE + ("INCREASE",), ("DECREASE",),
                "One miss after strong work must not reverse into DECREASE then back to INCREASE",
                variant, stability_scenario=True,
                evidence_dimensions=("correctness", "history"),
            )
        )

    # P2-008 Confidence/mastery conflict
    for sid, cid, ans, variant in (
        ("P2-008-A", "ALG-M-001", "4", "a"),
        ("P2-008-B", "FR-M-001", "5/6", "b"),
        ("P2-008-C", "ALG-M-003", "3", "c"),
        ("P2-008-D", "FR-E-001", "1", "d"),
    ):
        hist = tuple(_hs(cid, ans, WEAK, "HIGH") for _ in range(3))
        out.append(
            _sc(
                sid, "P2-008", "confidence_mastery_conflict", cid, hist, ans, WEAK, "HIGH",
                CONSERVATIVE, ("INCREASE",),
                "High stated confidence cannot override weak reasoning",
                variant,
                evidence_dimensions=("correctness", "reasoning", "confidence"),
            )
        )

    # P2-009 Evidence conflict
    for sid, cid, ans, reason, variant in (
        ("P2-009-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-009-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-009-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("P2-009-D", "FR-H-001", "5/6", STRONG_FRAC, "d"),
    ):
        hist = (
            _hs(cid, "0", WEAK, "HIGH"),
            _hs(cid, "0", WEAK, "HIGH"),
            _hs(cid, ans, reason, "MODERATE"),
            _hs(cid, ans, reason, "LOW"),
        )
        out.append(
            _sc(
                sid, "P2-009", "evidence_conflict", cid, hist, ans, reason, "LOW",
                CONSERVATIVE, ("DECREASE",),
                "Conflicting accuracy, reasoning, and confidence should gather or probe",
                variant,
                evidence_dimensions=("correctness", "reasoning", "confidence", "history"),
            )
        )

    # P2-010 Cross-concept transfer
    out.append(
        _sc(
            "P2-010-A", "P2-010", "cross_concept", "ALG-M-001",
            tuple(_hs("ALG-M-001", "4", STRONG_ALG, "HIGH") for _ in range(3)),
            "4", STRONG_ALG, "HIGH",
            ("INCREASE", "MAINTAIN"), ("DECREASE", "REMEDIATE"),
            "Strong algebra evidence can support increasing difficulty",
            "a", evidence_dimensions=("correctness", "reasoning", "confidence"),
        )
    )
    out.append(
        _sc(
            "P2-010-B", "P2-010", "cross_concept", "FR-M-001",
            tuple(_hs("FR-M-001", "5/6", STRONG_FRAC, "HIGH") for _ in range(3)),
            "5/6", STRONG_FRAC, "HIGH",
            ("INCREASE", "MAINTAIN"), ("DECREASE", "REMEDIATE"),
            "Strong fraction evidence can support increasing difficulty without algebra-specific rules",
            "b", evidence_dimensions=("correctness", "reasoning", "confidence"), tags=("g001",),
        )
    )
    out.append(
        _sc(
            "P2-010-C", "P2-010", "cross_concept", "FR-M-002",
            tuple(_hs("FR-M-002", "1/2", STRONG_FRAC_B, "HIGH") for _ in range(3)),
            "1/2", STRONG_FRAC_B, "HIGH",
            CONSERVATIVE, ("DECREASE", "REMEDIATE"),
            "Subtraction item with addition-oriented reasoning is not automatically INCREASE",
            "c", evidence_dimensions=("correctness", "reasoning"), tags=("g001",),
        )
    )
    out.append(
        _sc(
            "P2-010-D", "P2-010", "cross_concept", "ALG-M-003",
            tuple(_hs("ALG-M-003", "3", STRONG_M003, "HIGH") for _ in range(3)),
            "3", STRONG_M003, "HIGH",
            ("INCREASE", "MAINTAIN"), ("DECREASE", "REMEDIATE"),
            "A second algebra item should use the same evidence rules as fractions",
            "d", evidence_dimensions=("correctness", "reasoning", "confidence"),
        )
    )

    # P2-011 Strong learner recovery
    for sid, cid, ans, reason, variant in (
        ("P2-011-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-011-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-011-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("P2-011-D", "FR-E-001", "1", STRONG_FRAC, "d"),
    ):
        hist = tuple(_hs(cid, "0", GUESS, "LOW") for _ in range(3)) + tuple(
            _hs(cid, ans, reason, "HIGH") for _ in range(3)
        )
        out.append(
            _sc(
                sid, "P2-011", "strong_learner_recovery", cid, hist, ans, reason, "HIGH",
                CONSERVATIVE + ("INCREASE",), ("REMEDIATE",),
                "A learner who recovers with strong evidence should leave a weak-learner strategy",
                variant, recovery_scenario=False,
                evidence_dimensions=("correctness", "reasoning", "history"),
            )
        )

    # P2-012 Persistent misconception
    for sid, n, cid, ans, reason, variant in (
        ("P2-012-A", 3, "ALG-D-001", "2x+3", DIST_MISC, "a"),
        ("P2-012-B", 3, "FR-D-001", "2/5", ADD_MISC, "b"),
        ("P2-012-C", 4, "ALG-D-001", "2x+3", DIST_MISC, "c"),
        ("P2-012-D", 4, "FR-D-001", "2/5", ADD_MISC, "d"),
    ):
        hist = tuple(_hs(cid, ans, reason, "HIGH") for _ in range(n - 1))
        out.append(
            _sc(
                sid, "P2-012", "persistent_misconception", cid, hist, ans, reason, "HIGH",
                REMEDIATE_FAMILY, ("INCREASE", "MAINTAIN"),
                "Repeated misconception evidence can trigger remediation",
                variant, misconception_scenario=True,
                evidence_dimensions=("misconception", "history"),
            )
        )

    # P2-013 Sparse evidence
    for sid, cid, ans, reason, conf, variant in (
        ("P2-013-A", "ALG-M-001", "4", None, "UNKNOWN", "a"),
        ("P2-013-B", "FR-M-001", "5/6", None, "UNKNOWN", "b"),
        ("P2-013-C", "ALG-M-001", "", "maybe", "LOW", "c"),
        ("P2-013-D", "FR-E-001", "1", GUESS, "UNKNOWN", "d"),
    ):
        out.append(
            _sc(
                sid, "P2-013", "sparse_evidence", cid, (), ans, reason, conf,
                CONSERVATIVE, ("INCREASE", "DECREASE"),
                "Sparse evidence should assess or gather rather than commit",
                variant, sparse_scenario=True,
                evidence_dimensions=("correctness", "reasoning", "confidence"),
            )
        )

    # P2-014 Noisy evidence
    for sid, cid, ans, reason, variant in (
        ("P2-014-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-014-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-014-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("P2-014-D", "ALG-M-001", "4", STRONG_ALG, "d"),
    ):
        hist = (
            _hs(cid, ans, reason, "HIGH"),
            _hs(cid, ans, reason, "HIGH"),
            _hs(cid, "5" if cid.startswith("ALG") else "7/6", ARITH, "MODERATE"),
        )
        out.append(
            _sc(
                sid, "P2-014", "noisy_evidence", cid, hist, ans, reason, "HIGH",
                CONSERVATIVE + ("INCREASE",), ("DECREASE", "REMEDIATE"),
                "An arithmetic miss is noise, not a strategy collapse",
                variant, stability_scenario=True,
                evidence_dimensions=("correctness", "error_type", "history"),
            )
        )

    # P2-015 Longitudinal strategy evolution
    mixed = ("C", "C", "W", "C", "C", "C", "C")
    for sid, cid, ans, reason, variant in (
        ("P2-015-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("P2-015-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("P2-015-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("P2-015-D", "FR-E-001", "1", STRONG_FRAC, "d"),
    ):
        hist_steps = []
        for token in mixed:
            if token == "C":
                hist_steps.append(_hs(cid, ans, reason, "HIGH"))
            else:
                hist_steps.append(_hs(cid, "0", "I lost my place.", "LOW"))
        out.append(
            _sc(
                sid, "P2-015", "longitudinal_strategy", cid, tuple(hist_steps), ans, reason, "HIGH",
                CONSERVATIVE + ("INCREASE",), (),
                "A mixed longitudinal history should remain coherent and traceable",
                variant, stability_scenario=True,
                evidence_dimensions=("correctness", "history", "confidence"),
            )
        )

    return tuple(out)


SCENARIOS = build_scenarios()
SCENARIO_BY_ID = {item.scenario_id: item for item in SCENARIOS}
