"""Phase 3 end-to-end sessions and counterfactual pairs."""

from __future__ import annotations

from dataclasses import dataclass

from benchmarks.phase3.constants import ADVANCED, CONSERVATIVE, NO_ESCALATE, PROBE_FAMILY, REMEDIATE_FAMILY, RECOVERY_FAMILY
from benchmarks.phase3.expected import HOLDOUT_IDS


@dataclass(frozen=True)
class Phase3Scenario:
    scenario_id: str
    family: str
    concept: str
    category: str
    kinds: tuple[str, ...]
    expected_final: tuple[str, ...]
    expected_behavior: str
    forbidden: tuple[str, ...] = ()
    initial_challenge_id: str | None = None
    start_remediate: bool = False
    pair_id: str | None = None
    pair_role: str | None = None
    recovery_scenario: bool = False
    misconception_scenario: bool = False
    meaningful_evidence: bool = True

    @property
    def split(self) -> str:
        return "holdout" if self.scenario_id in HOLDOUT_IDS else "development"

    @property
    def n_steps(self) -> int:
        return len(self.kinds)


def _s(
    scenario_id: str,
    family: str,
    concept: str,
    category: str,
    kinds: tuple[str, ...],
    expected_final: tuple[str, ...],
    expected_behavior: str,
    **kwargs,
) -> Phase3Scenario:
    return Phase3Scenario(
        scenario_id=scenario_id,
        family=family,
        concept=concept,
        category=category,
        kinds=kinds,
        expected_final=expected_final,
        expected_behavior=expected_behavior,
        **kwargs,
    )


STRONG4 = ("strong_correct", "strong_correct", "strong_correct", "strong_correct")
WEAK4 = ("weak_correct", "weak_correct", "weak_correct", "weak_correct")
WRONG4 = ("wrong_weak", "wrong_weak", "wrong_weak", "wrong_weak")


def build_scenarios() -> tuple[Phase3Scenario, ...]:
    return (
        _s("S-001", "strong", "basic_algebra", "strong_learner", STRONG4, ADVANCED,
           "Strong correct evidence should advance strategy/challenge.",
           initial_challenge_id="ALG-M-001"),
        _s("S-002", "weak", "basic_algebra", "weak_learner", WEAK4, CONSERVATIVE,
           "Correct but weak evidence should not escalate difficulty.",
           initial_challenge_id="ALG-M-001", forbidden=("INCREASE",)),
        _s("S-003", "uncertain", "basic_algebra", "uncertain_learner",
           ("correct_unknown", "correct_unknown", "correct_unknown", "ambiguous"),
           CONSERVATIVE, "Missing reasoning keeps the tutor in evidence gathering.",
           forbidden=("INCREASE",)),
        _s("S-004", "strong", "fractions", "strong_learner", STRONG4, ADVANCED + PROBE_FAMILY,
           "Holdout strong fractions learner.", initial_challenge_id="FR-M-001"),
        _s("S-005", "misconception", "basic_algebra", "isolated_misconception",
           ("strong_correct", "strong_correct", "strong_correct", "misconception"),
           PROBE_FAMILY, "Isolated misconception after strong history should probe, not globally regress.",
           forbidden=("DECREASE",), misconception_scenario=True, initial_challenge_id="ALG-M-002"),
        _s("S-006", "misconception", "basic_algebra", "repeated_misconception",
           ("misconception", "misconception", "misconception", "misconception"),
           REMEDIATE_FAMILY + PROBE_FAMILY,
           "Repeated misconception should remediate or probe.",
           misconception_scenario=True, forbidden=("INCREASE",), initial_challenge_id="ALG-M-002"),
        _s("S-007", "recovery", "basic_algebra", "recovery",
           ("strong_correct", "strong_correct", "strong_correct"),
           RECOVERY_FAMILY, "Quality successes during remediation should recover strategy.",
           start_remediate=True, recovery_scenario=True, initial_challenge_id="ALG-R-001"),
        _s("S-008", "recovery", "fractions", "recovery",
           ("strong_correct", "strong_correct", "strong_correct"),
           RECOVERY_FAMILY + REMEDIATE_FAMILY,
           "Holdout recovery on fractions.",
           start_remediate=True, recovery_scenario=True, initial_challenge_id="FR-R-001"),
        _s("S-009", "noise", "basic_algebra", "noise",
           ("strong_correct", "strong_correct", "arithmetic", "strong_correct"),
           CONSERVATIVE + ("INCREASE",),
           "An isolated arithmetic slip should not cause extreme decrease."),
        _s("S-010", "oscillation", "basic_algebra", "oscillation",
           ("strong_correct", "wrong_weak", "strong_correct", "wrong_weak"),
           CONSERVATIVE, "Oscillating evidence should gather rather than INCREASE↔DECREASE.",
           forbidden=()),
        _s("S-011", "confidence_conflict", "basic_algebra", "confidence_conflict",
           ("correct_high_weak", "correct_high_weak", "correct_high_weak", "correct_high_weak"),
           PROBE_FAMILY + ("MAINTAIN",),
           "Correct + weak reasoning + high confidence is a conflict; do not increase.",
           forbidden=("INCREASE",)),
        _s("S-012", "sparse", "fractions", "sparse_evidence",
           ("correct_unknown", "ambiguous"),
           CONSERVATIVE, "Holdout sparse evidence.", forbidden=("INCREASE", "DECREASE")),
        _s("S-013", "sparse", "basic_algebra", "sparse_evidence",
           ("empty", "correct_unknown", "ambiguous"),
           CONSERVATIVE, "Sparse/empty evidence stays conservative.", forbidden=("INCREASE",)),
        _s("S-014", "cross_concept", "fractions", "strong_learner", STRONG4, ADVANCED + PROBE_FAMILY,
           "Cross-concept strong fractions path.", initial_challenge_id="FR-E-001"),
        _s("S-015", "adversarial", "basic_algebra", "adversarial",
           ("adversarial_harder", "adversarial_harder", "weak_correct", "adversarial_mastered"),
           CONSERVATIVE, "Learner instructions must not override adaptive decisions.",
           forbidden=("INCREASE",)),
        _s("S-016", "failure", "basic_algebra", "missing_confidence",
           ("correct_unknown", "weak_correct", "correct_unknown", "moderate_correct"),
           CONSERVATIVE, "Missing confidence is unknown, not mastery.", forbidden=("INCREASE",)),
        _s("S-017", "failure", "basic_algebra", "contradictory",
           ("strong_correct", "strong_correct", "strong_correct", "wrong_weak"),
           CONSERVATIVE + PROBE_FAMILY, "A sudden miss after strength should probe, not blindly decrease."),
        _s("S-018", "mixed", "basic_algebra", "mixed_noisy",
           ("strong_correct", "guess_correct", "arithmetic", "moderate_correct"),
           CONSERVATIVE + ADVANCED, "Holdout mixed signals."),
        _s("S-019", "misconception", "fractions", "isolated_misconception",
           ("strong_correct", "strong_correct", "strong_correct", "misconception"),
           PROBE_FAMILY + REMEDIATE_FAMILY,
           "Holdout isolated fraction misconception.",
           misconception_scenario=True, forbidden=("DECREASE",), initial_challenge_id="FR-M-001"),
        _s("S-020", "oscillation", "fractions", "oscillation",
           ("strong_correct", "wrong_weak", "strong_correct", "wrong_weak"),
           CONSERVATIVE, "Holdout oscillating fractions."),
        _s("S-021", "weak", "fractions", "weak_learner", WEAK4, CONSERVATIVE,
           "Holdout weak fractions.", forbidden=("INCREASE",), initial_challenge_id="FR-M-001"),
        _s("S-022", "confidence_conflict", "fractions", "confidence_conflict",
           ("correct_high_weak", "correct_high_weak", "correct_high_weak"),
           PROBE_FAMILY + ("MAINTAIN",),
           "Holdout confidence conflict.", forbidden=("INCREASE",)),
        _s("S-023", "failure", "basic_algebra", "unexpected_correct",
           ("wrong_weak", "wrong_weak", "wrong_weak", "strong_correct"),
           CONSERVATIVE + REMEDIATE_FAMILY,
           "Holdout unexpected correct after failures is not automatic mastery.",
           forbidden=("INCREASE",)),
        _s("S-024", "transfer", "basic_algebra", "transfer",
           STRONG4, ADVANCED + PROBE_FAMILY,
           "Holdout transfer-capable strong sequence.", initial_challenge_id="ALG-T-001"),
        _s("S-025", "noise", "basic_algebra", "guess_noise",
           ("guess_correct", "guess_correct", "arithmetic", "wrong_weak"),
           CONSERVATIVE + ("DECREASE",),
           "Guessing and noise must not create mastery.", forbidden=("INCREASE",)),
        _s("S-026", "improving", "basic_algebra", "improving_learner",
           ("wrong_weak", "wrong_weak", "moderate_correct", "strong_correct"),
           CONSERVATIVE + RECOVERY_FAMILY,
           "Improving evidence should not stay in unjustified decrease."),
        _s("S-027", "struggling", "basic_algebra", "struggling_learner",
           ("misconception", "wrong_weak", "misconception", "misconception"),
           REMEDIATE_FAMILY + PROBE_FAMILY + ("GATHER_EVIDENCE", "DECREASE", "ASSESS"),
           "Struggling misconception path.", misconception_scenario=True,
           forbidden=("INCREASE",), initial_challenge_id="ALG-M-002"),
        _s("S-028", "strong", "basic_algebra", "strong_then_probe",
           ("strong_correct", "strong_correct", "strong_correct", "ambiguous"),
           CONSERVATIVE + ADVANCED, "Ambiguity after strength should not erase prior evidence blindly."),
        _s("S-029", "maintain", "basic_algebra", "maintain_variation",
           ("moderate_correct", "moderate_correct", "moderate_correct", "moderate_correct"),
           CONSERVATIVE + ("INCREASE",),
           "Moderate evidence prefers maintain/variation over extremes."),
        _s("S-030", "gather", "basic_algebra", "gather_then_decide",
           ("correct_unknown", "moderate_correct", "strong_correct", "strong_correct"),
           CONSERVATIVE + ADVANCED,
           "Evidence gathering then stronger work may advance."),
        _s("P3-CF-001A", "counterfactual", "basic_algebra", "cf_quality_strong",
           STRONG4, ADVANCED,
           "Counterfactual A: strong reasoning and high confidence.",
           initial_challenge_id="ALG-M-001", pair_id="P3-CF-001", pair_role="A"),
        _s("P3-CF-001B", "counterfactual", "basic_algebra", "cf_quality_weak",
           WEAK4, CONSERVATIVE,
           "Counterfactual B: weak reasoning and low confidence.",
           initial_challenge_id="ALG-M-001", pair_id="P3-CF-001", pair_role="B",
           forbidden=("INCREASE",)),
        _s("P3-CF-002A", "counterfactual", "basic_algebra", "cf_misc_strong",
           STRONG4, ADVANCED,
           "Counterfactual A: four strong corrects.",
           initial_challenge_id="ALG-M-002", pair_id="P3-CF-002", pair_role="A"),
        _s("P3-CF-002B", "counterfactual", "basic_algebra", "cf_misc_misconception",
           ("strong_correct", "strong_correct", "misconception"),
           PROBE_FAMILY + REMEDIATE_FAMILY,
           "Counterfactual B: misconception after two corrects; not global regression.",
           initial_challenge_id="ALG-M-002", pair_id="P3-CF-002", pair_role="B",
           misconception_scenario=True, forbidden=("DECREASE",)),
        _s("P3-CF-003A", "counterfactual", "basic_algebra", "cf_remediate_fail",
           ("wrong_weak", "wrong_weak"),
           REMEDIATE_FAMILY + ("GATHER_EVIDENCE", "PROBE"),
           "Counterfactual A: continued remediation failures.",
           start_remediate=True, pair_id="P3-CF-003", pair_role="A",
           initial_challenge_id="ALG-R-001", forbidden=("INCREASE",)),
        _s("P3-CF-003B", "counterfactual", "basic_algebra", "cf_remediate_recover",
           ("weak_correct", "strong_correct", "strong_correct"),
           RECOVERY_FAMILY + REMEDIATE_FAMILY,
           "Counterfactual B: quality recovery from remediation.",
           start_remediate=True, recovery_scenario=True, pair_id="P3-CF-003",
           pair_role="B", initial_challenge_id="ALG-R-001"),
    )


SCENARIOS = build_scenarios()
SCENARIO_BY_ID = {item.scenario_id: item for item in SCENARIOS}


def development_scenarios() -> tuple[Phase3Scenario, ...]:
    return tuple(item for item in SCENARIOS if item.split == "development")


def holdout_scenarios() -> tuple[Phase3Scenario, ...]:
    return tuple(item for item in SCENARIOS if item.split == "holdout")
