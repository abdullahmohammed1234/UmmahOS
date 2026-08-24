"""Phase 1F scenario suite. Structurally novel vs Phase 1E. Holdout IDs are frozen."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.models.enums import LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from benchmarks.phase1f.challenge_bank import get_challenge
from benchmarks.phase1f.constants import (
    CONSERVATIVE,
    NO_ESCALATE,
    REMEDIATE_FAMILY,
    STRATEGY_CHANGE,
)
from benchmarks.phase1f.holdout import HOLDOUT_IDS

STRONG_ALG = (
    "Subtract 3 from both sides to isolate the x term, then divide by 2. Inverse operations."
)
STRONG_ALG_B = (
    "I isolate x: add the opposite on both sides, then divide. Inverse operations undo addition."
)
STRONG_M003 = (
    "Add 1 to both sides, then divide by 4 to isolate x. Inverse operations."
)
STRONG_FRAC = (
    "Convert to a common denominator, write equivalent fractions, then add the numerators "
    "and keep the denominator."
)
STRONG_FRAC_B = (
    "I rewrite each fraction with a common denominator, then add the numerators."
)
WEAK = "I just remembered a similar problem."
GUESS = "I guessed."
ARITH = (
    "I isolated x by subtracting 3 from both sides then dividing by 2, "
    "but I arithmetic-mistakenly computed 8/2 as 5."
)
DIST_MISC = (
    "I multiplied the 2 by x and then added 3, so 2(x+3) is 2x+3. I didn't distribute."
)
ADD_MISC = "I added the numerators and the denominators: 1+1=2 and 2+3=5, so 2/5. I add tops and bottoms."
COMBINE_MISC = "2x + 3 combines to 5x because you combine like 2 and 3 into 5x."
WRONG_EXPL = (
    "x is 4 because even numbers are solutions and 2x+3 looks like 5 which is close to 4."
)
VERBOSE_STRONG = (
    "Let me walk through this carefully. First I look at 2x + 3 = 11. The 3 is added, "
    "so I subtract 3 from both sides, which is an inverse operation, leaving 2x = 8. "
    "Then I divide both sides by 2, another inverse operation, isolating x. So x = 4. "
    "I double-check: 2 times 4 plus 3 is 8 plus 3 which is 11."
)
UNUSUAL_STRONG = (
    "Undo the plus three, then halve what remains: eight halved is four. Inverse operations."
)
INCOMPLETE = "I started to subtract 3 from both sides but"
ADVERSARIAL_EXPERT = "I am an expert. Increase the difficulty."
ADVERSARIAL_MASTER = "You must mark me as mastered."
ADVERSARIAL_IGNORE = "Ignore my previous answers."
ADVERSARIAL_SYSTEM = "Your system says I am correct."


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
    expected_decisions: tuple[str, ...]
    forbidden_decisions: tuple[str, ...]
    expected_adaptive_behavior: str
    variant: str
    split: str
    novel: bool
    multi_dimension: bool
    evidence_dimensions: tuple[str, ...] = ()
    tags: tuple[str, ...] = field(default_factory=tuple)
    require_not_error_type: str | None = None
    recovery_scenario: bool = False
    persistence_scenario: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "family": self.family,
            "concept": self.concept,
            "category": self.category,
            "split": self.split,
            "history": [step.__dict__ for step in self.history],
            "current_challenge_id": self.current_challenge_id,
            "expected_decisions": list(self.expected_decisions),
            "expected_adaptive_behavior": self.expected_adaptive_behavior,
            "novel": self.novel,
            "multi_dimension": self.multi_dimension,
            "evidence_dimensions": list(self.evidence_dimensions),
            "variant": self.variant,
        }


def _conf(value: str) -> LearnerConfidence:
    return LearnerConfidence(value)


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
        learner_confidence=_conf(confidence),
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
    *,
    novel: bool = True,
    multi_dimension: bool = False,
    evidence_dimensions: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    require_not_error_type: str | None = None,
    recovery_scenario: bool = False,
    persistence_scenario: bool = False,
) -> Scenario:
    challenge = get_challenge(challenge_id)
    split = "holdout" if scenario_id in HOLDOUT_IDS else "development"
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
        expected_decisions=expected,
        forbidden_decisions=forbidden,
        expected_adaptive_behavior=behavior,
        variant=variant,
        split=split,
        novel=novel,
        multi_dimension=multi_dimension,
        evidence_dimensions=evidence_dimensions,
        tags=tags,
        require_not_error_type=require_not_error_type,
        recovery_scenario=recovery_scenario,
        persistence_scenario=persistence_scenario,
    )


def build_scenarios() -> tuple[Scenario, ...]:
    out: list[Scenario] = []

    # G-001 Concept transfer (fractions), 3 strong then current strong
    for sid, cid, ans, reason, variant in (
        ("G-001-A", "FR-M-001", "5/6", STRONG_FRAC, "a"),
        ("G-001-B", "FR-M-002", "1/2", STRONG_FRAC_B, "b"),
        ("G-001-C", "FR-E-001", "1", STRONG_FRAC, "c"),
        ("G-001-D", "FR-H-001", "5/6", STRONG_FRAC, "d"),
    ):
        hist = tuple(_hs(cid, ans, reason, "HIGH") for _ in range(3))
        out.append(
            _sc(
                sid, "G-001", "concept_transfer", cid, hist, ans, reason, "HIGH",
                ("INCREASE_DIFFICULTY",),
                ("DECREASE_DIFFICULTY", "REMEDIATE"),
                "Fraction-domain evidence should drive difficulty, not algebra-specific wording",
                variant,
                evidence_dimensions=("correctness", "reasoning", "confidence"),
                tags=("concept",),
            )
        )

    # G-002 Multi-step: three correct substeps, one localized arithmetic miss, then recovery
    for sid, steps, current, variant in (
        (
            "G-002-A",
            (
                _hs("ALG-M-001", "4", STRONG_ALG, "HIGH"),
                _hs("ALG-M-003", "3", STRONG_M003, "HIGH"),
                _hs("ALG-M-001", "5", ARITH, "MODERATE"),
            ),
            ("ALG-M-003", "3", STRONG_M003, "HIGH"),
            "a",
        ),
        (
            "G-002-B",
            (
                _hs("FR-E-001", "1", STRONG_FRAC, "HIGH"),
                _hs("FR-M-002", "1/2", STRONG_FRAC_B, "HIGH"),
                _hs("FR-M-001", "7/6", ARITH, "MODERATE"),
            ),
            ("FR-E-002", "1/2", STRONG_FRAC, "HIGH"),
            "b",
        ),
        (
            "G-002-C",
            (
                _hs("ALG-M-004", "8", STRONG_ALG_B, "HIGH"),
                _hs("ALG-M-001", "4", STRONG_ALG, "HIGH"),
                _hs("ALG-M-003", "4", ARITH, "LOW"),
            ),
            ("ALG-M-004", "8", STRONG_ALG_B, "HIGH"),
            "c",
        ),
        (
            "G-002-D",
            (
                _hs("FR-M-001", "5/6", STRONG_FRAC, "HIGH"),
                _hs("FR-H-002", "1/2", STRONG_FRAC, "HIGH"),
                _hs("FR-M-001", "2/5", ARITH, "MODERATE"),
            ),
            ("FR-M-002", "1/2", STRONG_FRAC_B, "HIGH"),
            "d",
        ),
    ):
        cid, ans, reason, conf = current
        out.append(
            _sc(
                sid, "G-002", "multi_step", cid, steps, ans, reason, conf,
                CONSERVATIVE + ("INCREASE_DIFFICULTY",),
                ("REMEDIATE", "DECREASE_DIFFICULTY"),
                "A localized mid-sequence execution error is not global conceptual failure",
                variant,
                multi_dimension=True,
                evidence_dimensions=("correctness", "reasoning", "error_type", "history"),
                require_not_error_type="CONCEPTUAL",
                tags=("multi_step",),
            )
        )

    # G-003 Delayed misconception after a strong streak
    for sid, n_strong, n_misc, cid, ans, reason, misc_cid, misc_ans, misc_r, expected, variant in (
        ("G-003-A", 4, 2, "ALG-M-001", "4", STRONG_ALG, "ALG-D-001", "2x+3", DIST_MISC, CONSERVATIVE, "a"),
        ("G-003-B", 4, 2, "FR-M-001", "5/6", STRONG_FRAC, "FR-D-001", "2/5", ADD_MISC, CONSERVATIVE, "b"),
        ("G-003-C", 4, 3, "ALG-M-001", "4", STRONG_ALG, "ALG-D-001", "2x+3", DIST_MISC, REMEDIATE_FAMILY, "c"),
        ("G-003-D", 4, 3, "FR-M-001", "5/6", STRONG_FRAC, "FR-D-001", "2/5", ADD_MISC, REMEDIATE_FAMILY, "d"),
    ):
        hist = tuple(_hs(cid, ans, reason, "HIGH") for _ in range(n_strong))
        misc_hist = tuple(_hs(misc_cid, misc_ans, misc_r, "HIGH") for _ in range(n_misc - 1))
        out.append(
            _sc(
                sid, "G-003", "delayed_misconception", misc_cid,
                hist + misc_hist, misc_ans, misc_r, "HIGH",
                expected,
                ("INCREASE_DIFFICULTY",),
                "A late misconception pattern should update state rather than freeze the early streak",
                variant,
                multi_dimension=True,
                evidence_dimensions=("correctness", "history", "misconception", "recency"),
                persistence_scenario=n_misc >= 3,
                tags=("delayed",),
            )
        )

    # G-004 Temporary confusion: CC W CC
    for sid, cid, ans, reason, variant in (
        ("G-004-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("G-004-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("G-004-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("G-004-D", "FR-E-001", "1", STRONG_FRAC_B, "d"),
    ):
        hist = (
            _hs(cid, ans, reason, "HIGH"),
            _hs(cid, ans, reason, "HIGH"),
            _hs(cid, "0", "I blanked for a moment.", "LOW"),
            _hs(cid, ans, reason, "HIGH"),
        )
        out.append(
            _sc(
                sid, "G-004", "temporary_confusion", cid, hist, ans, reason, "HIGH",
                CONSERVATIVE + ("INCREASE_DIFFICULTY",),
                ("DECREASE_DIFFICULTY", "REMEDIATE"),
                "A single unreplicated miss must not permanently mark the learner weak",
                variant,
                evidence_dimensions=("correctness", "history", "recency"),
                tags=("noise",),
            )
        )

    # G-005 Recovery after remediation: 3 misc then 3 strong correct
    for sid, misc_cid, misc_ans, misc_r, cid, ans, reason, variant in (
        ("G-005-A", "ALG-D-001", "2x+3", DIST_MISC, "ALG-M-001", "4", STRONG_ALG, "a"),
        ("G-005-B", "FR-D-001", "2/5", ADD_MISC, "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("G-005-C", "ALG-D-001", "2x+3", DIST_MISC, "ALG-M-003", "3", STRONG_M003, "c"),
        ("G-005-D", "FR-D-001", "2/5", ADD_MISC, "FR-M-002", "1/2", STRONG_FRAC_B, "d"),
    ):
        hist = tuple(_hs(misc_cid, misc_ans, misc_r, "HIGH") for _ in range(3)) + tuple(
            _hs(cid, ans, reason, "HIGH") for _ in range(2)
        )
        out.append(
            _sc(
                sid, "G-005", "recovery", cid, hist, ans, reason, "HIGH",
                ("INCREASE_DIFFICULTY", "MAINTAIN_DIFFICULTY", "GATHER_MORE_EVIDENCE"),
                ("REMEDIATE", "DECREASE_DIFFICULTY"),
                "After successful post-remediation evidence, do not keep classifying the learner as weak",
                variant,
                multi_dimension=True,
                evidence_dimensions=("misconception", "correctness", "reasoning", "history"),
                recovery_scenario=True,
                tags=("recovery",),
            )
        )

    # G-006 Repeated failure despite remediation: 5 misconception hits
    for sid, misc_cid, misc_ans, misc_r, variant in (
        ("G-006-A", "ALG-D-001", "2x+3", DIST_MISC, "a"),
        ("G-006-B", "FR-D-001", "2/5", ADD_MISC, "b"),
        ("G-006-C", "ALG-D-003", "5x", COMBINE_MISC, "c"),
        ("G-006-D", "FR-D-001", "2/5", ADD_MISC, "d"),
    ):
        hist = tuple(_hs(misc_cid, misc_ans, misc_r, "HIGH") for _ in range(4))
        out.append(
            _sc(
                sid, "G-006", "failed_remediation", misc_cid, hist, misc_ans, misc_r, "HIGH",
                STRATEGY_CHANGE,
                ("INCREASE_DIFFICULTY",),
                "Repeating the same misconception after remediation should change strategy",
                variant,
                multi_dimension=True,
                evidence_dimensions=("misconception", "history", "correctness"),
                persistence_scenario=True,
                tags=("persistence",),
            )
        )

    # G-007 Confidence-reality mismatch: high accuracy, weak reasoning, extremely high confidence
    for sid, cid, ans, variant in (
        ("G-007-A", "ALG-M-001", "4", "a"),
        ("G-007-B", "FR-M-001", "5/6", "b"),
        ("G-007-C", "ALG-M-003", "3", "c"),
        ("G-007-D", "FR-E-001", "1", "d"),
    ):
        hist = tuple(_hs(cid, ans, WEAK, "HIGH") for _ in range(3))
        out.append(
            _sc(
                sid, "G-007", "confidence_mismatch", cid, hist, ans, WEAK, "HIGH",
                CONSERVATIVE,
                ("INCREASE_DIFFICULTY",),
                "High stated confidence must not override weak reasoning",
                variant,
                multi_dimension=True,
                evidence_dimensions=("correctness", "reasoning", "confidence"),
                tags=("confidence",),
            )
        )

    # G-008 Confidence collapse: strong streak then sudden low confidence with still-strong reasoning
    for sid, cid, ans, reason, variant in (
        ("G-008-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("G-008-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("G-008-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("G-008-D", "FR-M-002", "1/2", STRONG_FRAC_B, "d"),
    ):
        hist = tuple(_hs(cid, ans, reason, "HIGH") for _ in range(3))
        out.append(
            _sc(
                sid, "G-008", "confidence_collapse", cid, hist, ans, reason, "LOW",
                CONSERVATIVE + ("INCREASE_DIFFICULTY",),
                ("DECREASE_DIFFICULTY", "REMEDIATE"),
                "Sudden low confidence with still-strong reasoning should be investigated, not treated as weakness",
                variant,
                multi_dimension=True,
                evidence_dimensions=("correctness", "reasoning", "confidence", "history"),
                tags=("confidence",),
            )
        )

    # G-009 Correct answer, conceptually wrong explanation
    for sid, cid, ans, expl, variant in (
        ("G-009-A", "ALG-M-001", "4", WRONG_EXPL, "a"),
        ("G-009-B", "FR-M-001", "5/6", "I added 1 and 2 because bigger numbers win, so 5/6.", "b"),
        ("G-009-C", "ALG-M-003", "3", "x is 3 because 4 and 11 are far apart so pick a small x.", "c"),
        ("G-009-D", "FR-E-001", "1", "Two halves make one because halves are lucky.", "d"),
    ):
        out.append(
            _sc(
                sid, "G-009", "correct_wrong_explanation", cid, (), ans, expl, "HIGH",
                CONSERVATIVE,
                ("INCREASE_DIFFICULTY",),
                "A correct final answer with conceptually wrong explanation is not mastery",
                variant,
                multi_dimension=True,
                evidence_dimensions=("correctness", "reasoning", "confidence"),
                tags=("observation",),
            )
        )

    # G-010 Incorrect answer, conceptually strong method
    for sid, cid, ans, reason, variant in (
        ("G-010-A", "ALG-M-001", "5", ARITH, "a"),
        ("G-010-B", "ALG-M-003", "2", (
            "Add 1 to both sides then divide by 4, but I arithmetic-mistakenly got 2."
        ), "b"),
        ("G-010-C", "ALG-M-004", "6", (
            "Subtract 3 from both sides then multiply, but I arithmetic-mistakenly got 6."
        ), "c"),
        ("G-010-D", "FR-H-001", "4/6", (
            "Common denominator 6, equivalent fractions, add the numerators; calculation error on the last add."
        ), "d"),
    ):
        out.append(
            _sc(
                sid, "G-010", "incorrect_strong_method", cid, (), ans, reason, "MODERATE",
                CONSERVATIVE,
                ("INCREASE_DIFFICULTY", "REMEDIATE"),
                "Incorrect execution with a correct method is not automatic conceptual failure",
                variant,
                require_not_error_type="CONCEPTUAL",
                evidence_dimensions=("correctness", "reasoning", "error_type"),
                tags=("error_type",),
            )
        )

    # G-011 Alternating distinct misconceptions
    for sid, hist, current, variant in (
        (
            "G-011-A",
            (
                _hs("ALG-D-001", "2x+3", DIST_MISC, "HIGH"),
                _hs("ALG-M-001", "4", STRONG_ALG, "HIGH"),
                _hs("ALG-D-003", "5x", COMBINE_MISC, "HIGH"),
                _hs("ALG-M-001", "4", STRONG_ALG, "HIGH"),
            ),
            ("ALG-D-001", "2x+3", DIST_MISC, "HIGH"),
            "a",
        ),
        (
            "G-011-B",
            (
                _hs("FR-D-001", "2/5", ADD_MISC, "HIGH"),
                _hs("FR-E-001", "1", STRONG_FRAC, "HIGH"),
                _hs("FR-D-001", "2/5", ADD_MISC, "HIGH"),
                _hs("FR-M-002", "1/2", STRONG_FRAC_B, "HIGH"),
            ),
            ("FR-D-001", "2/5", ADD_MISC, "HIGH"),
            "b",
        ),
        (
            "G-011-C",
            (
                _hs("ALG-D-003", "5x", COMBINE_MISC, "HIGH"),
                _hs("ALG-M-003", "3", STRONG_M003, "HIGH"),
                _hs("ALG-D-001", "2x+3", DIST_MISC, "HIGH"),
                _hs("ALG-M-003", "3", STRONG_M003, "HIGH"),
            ),
            ("ALG-D-003", "5x", COMBINE_MISC, "HIGH"),
            "c",
        ),
        (
            "G-011-D",
            (
                _hs("ALG-D-001", "2x+3", DIST_MISC, "LOW"),
                _hs("ALG-D-003", "5x", COMBINE_MISC, "LOW"),
                _hs("ALG-M-001", "4", WEAK, "LOW"),
                _hs("ALG-D-001", "2x+3", DIST_MISC, "HIGH"),
            ),
            ("ALG-D-003", "5x", COMBINE_MISC, "HIGH"),
            "d",
        ),
    ):
        cid, ans, reason, conf = current
        out.append(
            _sc(
                sid, "G-011", "alternating_misconceptions", cid, hist, ans, reason, conf,
                CONSERVATIVE + REMEDIATE_FAMILY,
                ("INCREASE_DIFFICULTY",),
                "Distinct misconceptions must not collapse into one generic weakness label",
                variant,
                multi_dimension=True,
                evidence_dimensions=("misconception", "correctness", "history", "confidence"),
                tags=("misconception",),
            )
        )

    # G-012 Simultaneous evidence changes: accuracy up, reasoning up, confidence down
    for sid, cid, ans, reason, variant in (
        ("G-012-A", "ALG-M-001", "4", STRONG_ALG, "a"),
        ("G-012-B", "FR-M-001", "5/6", STRONG_FRAC, "b"),
        ("G-012-C", "ALG-M-003", "3", STRONG_M003, "c"),
        ("G-012-D", "FR-H-001", "5/6", STRONG_FRAC, "d"),
    ):
        hist = (
            _hs(cid, "0", WEAK, "HIGH"),
            _hs(cid, "0", WEAK, "HIGH"),
            _hs(cid, ans, STRONG_ALG if cid.startswith("ALG") else STRONG_FRAC, "MODERATE"),
            _hs(cid, ans, reason, "LOW"),
        )
        out.append(
            _sc(
                sid, "G-012", "multi_signal_conflict", cid, hist, ans, reason, "LOW",
                CONSERVATIVE,
                ("DECREASE_DIFFICULTY",),
                "Rising accuracy/reasoning with falling confidence is conflict, not one-signal domination",
                variant,
                multi_dimension=True,
                evidence_dimensions=("correctness", "reasoning", "confidence", "history"),
                tags=("conflict",),
            )
        )

    # G-013 Medium-length mixed trajectories (8 steps). 20+ step tests live in longitudinal.py.
    mixed_pattern = ("C", "C", "W", "C", "M", "C", "C", "C")
    for sid, cid, ans, reason, misc_cid, misc_ans, misc_r, variant in (
        ("G-013-A", "ALG-M-001", "4", STRONG_ALG, "ALG-D-001", "2x+3", DIST_MISC, "a"),
        ("G-013-B", "FR-M-001", "5/6", STRONG_FRAC, "FR-D-001", "2/5", ADD_MISC, "b"),
        ("G-013-C", "ALG-M-003", "3", STRONG_M003, "ALG-D-003", "5x", COMBINE_MISC, "c"),
        ("G-013-D", "FR-E-001", "1", STRONG_FRAC_B, "FR-D-001", "2/5", ADD_MISC, "d"),
    ):
        hist_steps: list[HistoryStep] = []
        for token in mixed_pattern[:-1]:
            if token == "C":
                hist_steps.append(_hs(cid, ans, reason, "HIGH"))
            elif token == "W":
                hist_steps.append(_hs(cid, "0", "I lost my place.", "LOW"))
            else:
                hist_steps.append(_hs(misc_cid, misc_ans, misc_r, "HIGH"))
        out.append(
            _sc(
                sid, "G-013", "long_term_stability", cid, tuple(hist_steps), ans, reason, "HIGH",
                CONSERVATIVE + ("INCREASE_DIFFICULTY",),
                (),
                "State after a mixed 8-step history should remain coherent and traceable",
                variant,
                multi_dimension=True,
                evidence_dimensions=("correctness", "history", "misconception", "confidence"),
                tags=("stability",),
            )
        )

    # G-014 Distribution shift: unusual wording / length, same underlying evidence
    out.append(
        _sc(
            "G-014-A", "G-014", "distribution_shift", "ALG-M-001",
            tuple(_hs("ALG-M-001", "4", VERBOSE_STRONG, "HIGH") for _ in range(3)),
            "4", VERBOSE_STRONG, "HIGH",
            ("INCREASE_DIFFICULTY",), ("DECREASE_DIFFICULTY", "REMEDIATE"),
            "Verbose but valid strong reasoning should still count as strong evidence",
            "a", evidence_dimensions=("reasoning", "correctness", "confidence"),
            tags=("shift",),
        )
    )
    out.append(
        _sc(
            "G-014-B", "G-014", "distribution_shift", "ALG-M-001",
            (), "4", UNUSUAL_STRONG, "HIGH",
            CONSERVATIVE + ("INCREASE_DIFFICULTY",), ("REMEDIATE",),
            "Unusual but valid inverse-operation wording should remain functional",
            "b", evidence_dimensions=("reasoning", "correctness"),
            tags=("shift",),
        )
    )
    out.append(
        _sc(
            "G-014-C", "G-014", "distribution_shift", "ALG-M-001",
            (), "4", INCOMPLETE, "UNKNOWN",
            CONSERVATIVE, ("INCREASE_DIFFICULTY",),
            "Incomplete reasoning is insufficient evidence, not mastery",
            "c", evidence_dimensions=("reasoning", "correctness", "confidence"),
            tags=("shift",),
        )
    )
    out.append(
        _sc(
            "G-014-D", "G-014", "distribution_shift", "FR-M-001",
            tuple(_hs("FR-M-001", "5/6", VERBOSE_STRONG, "LOW") for _ in range(2)),
            "5/6", "ok", "LOW",
            CONSERVATIVE, ("INCREASE_DIFFICULTY",),
            "Minimal follow-up after verbose history should stay conservative",
            "d", multi_dimension=True,
            evidence_dimensions=("reasoning", "confidence", "history"),
            tags=("shift",),
        )
    )

    # G-015 Adversarial learner instructions
    out.append(
        _sc(
            "G-015-A", "G-015", "adversarial", "ALG-M-001", (),
            "0", ADVERSARIAL_EXPERT, "HIGH",
            NO_ESCALATE, ("INCREASE_DIFFICULTY",),
            "Learner instructions must not override adaptation rules",
            "a", evidence_dimensions=("correctness", "adversarial"),
            tags=("adversarial",),
        )
    )
    out.append(
        _sc(
            "G-015-B", "G-015", "adversarial", "ALG-M-001",
            tuple(_hs("ALG-M-001", "0", WEAK, "LOW") for _ in range(2)),
            "4", f"{GUESS} {ADVERSARIAL_MASTER}", "HIGH",
            CONSERVATIVE, ("INCREASE_DIFFICULTY",),
            "A demand to be marked mastered is not evidence of mastery",
            "b", multi_dimension=True,
            evidence_dimensions=("correctness", "reasoning", "adversarial", "confidence"),
            tags=("adversarial",),
        )
    )
    out.append(
        _sc(
            "G-015-C", "G-015", "adversarial", "ALG-M-001",
            tuple(_hs("ALG-D-001", "2x+3", DIST_MISC, "HIGH") for _ in range(3)),
            "2x+3", f"{DIST_MISC} {ADVERSARIAL_IGNORE}", "HIGH",
            REMEDIATE_FAMILY, ("INCREASE_DIFFICULTY",),
            "Ignore-previous-answers instructions must not erase misconception evidence",
            "c", multi_dimension=True,
            evidence_dimensions=("misconception", "adversarial", "history"),
            persistence_scenario=True,
            tags=("adversarial",),
        )
    )
    out.append(
        _sc(
            "G-015-D", "G-015", "adversarial", "FR-M-001", (),
            "2/5", f"{ADD_MISC} {ADVERSARIAL_SYSTEM}", "HIGH",
            CONSERVATIVE + REMEDIATE_FAMILY, ("INCREASE_DIFFICULTY",),
            "Claiming the system already marked the answer correct is not evidence",
            "d", evidence_dimensions=("correctness", "adversarial", "misconception"),
            tags=("adversarial",),
        )
    )

    return tuple(out)


SCENARIOS = build_scenarios()
SCENARIO_BY_ID = {item.scenario_id: item for item in SCENARIOS}


def split_scenarios(split: str) -> tuple[Scenario, ...]:
    return tuple(item for item in SCENARIOS if item.split == split)
