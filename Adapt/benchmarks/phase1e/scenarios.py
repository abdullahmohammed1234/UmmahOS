"""Frozen Phase 1E scenario suite.

Expected behavior is an evaluation reference. It is never passed to a system
under test. Surface wording varies across variants; the evidence pattern does not.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.adaptation.challenge_bank import CONCEPT_ID, get_challenge
from adapt.models.enums import LearnerConfidence
from adapt.models.learner_response import LearnerResponse

CONSERVATIVE = (
    "MAINTAIN_DIFFICULTY",
    "PROBE_UNCERTAINTY",
    "GATHER_MORE_EVIDENCE",
)
REMEDIATE_FAMILY = (
    "REMEDIATE",
    "CHANGE_REPRESENTATION",
    "GATHER_MORE_EVIDENCE",
)
NOISE_OK = (
    "MAINTAIN_DIFFICULTY",
    "INCREASE_DIFFICULTY",
    "PROBE_UNCERTAINTY",
    "GATHER_MORE_EVIDENCE",
)
REGRESSION_OK = (
    "DECREASE_DIFFICULTY",
    "PROBE_UNCERTAINTY",
    "GATHER_MORE_EVIDENCE",
    "MAINTAIN_DIFFICULTY",
)
CONFLICT_OK = (
    "PROBE_UNCERTAINTY",
    "GATHER_MORE_EVIDENCE",
    "MAINTAIN_DIFFICULTY",
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
    difficulty_context: str
    history: tuple[HistoryStep, ...]
    current_challenge_id: str
    current_answer: str
    current_reasoning: str | None
    current_confidence: str
    expected_decisions: tuple[str, ...]
    forbidden_decisions: tuple[str, ...]
    expected_adaptive_behavior: str
    variant: str
    counterfactual_pair_id: str | None = None
    counterfactual_role: str | None = None
    counterfactual_dimension: str | None = None
    forbid_next_difficulty: tuple[str, ...] = ()
    require_not_error_type: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "family": self.family,
            "concept": self.concept,
            "category": self.category,
            "difficulty_context": self.difficulty_context,
            "history": [step.__dict__ for step in self.history],
            "current_challenge_id": self.current_challenge_id,
            "current_answer": self.current_answer,
            "current_reasoning": self.current_reasoning,
            "current_confidence": self.current_confidence,
            "expected_decisions": list(self.expected_decisions),
            "forbidden_decisions": list(self.forbidden_decisions),
            "expected_adaptive_behavior": self.expected_adaptive_behavior,
            "variant": self.variant,
            "counterfactual_pair_id": self.counterfactual_pair_id,
            "counterfactual_role": self.counterfactual_role,
            "counterfactual_dimension": self.counterfactual_dimension,
            "forbid_next_difficulty": list(self.forbid_next_difficulty),
            "require_not_error_type": self.require_not_error_type,
            "tags": list(self.tags),
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
    return LearnerResponse(
        response_id=response_id,
        learner_id=learner_id,
        concept_id=CONCEPT_ID,
        challenge_id=challenge_id,
        answer=answer,
        reasoning=reasoning,
        learner_confidence=_conf(confidence),
    )


def scenario_steps(scenario: Scenario, learner_id: str) -> list[tuple[object, LearnerResponse]]:
    """History + current as (Challenge, LearnerResponse) pairs. No expected labels."""
    pairs: list[tuple[object, LearnerResponse]] = []
    for index, step in enumerate(scenario.history, start=1):
        challenge = get_challenge(step.challenge_id)
        response = make_response(
            response_id=f"{scenario.scenario_id}-H{index:02d}",
            learner_id=learner_id,
            challenge_id=step.challenge_id,
            answer=step.answer,
            reasoning=step.reasoning,
            confidence=step.learner_confidence,
        )
        pairs.append((challenge, response))
    current = get_challenge(scenario.current_challenge_id)
    current_response = make_response(
        response_id=f"{scenario.scenario_id}-CUR",
        learner_id=learner_id,
        challenge_id=scenario.current_challenge_id,
        answer=scenario.current_answer,
        reasoning=scenario.current_reasoning,
        confidence=scenario.current_confidence,
    )
    pairs.append((current, current_response))
    return pairs


STRONG_M001 = (
    "To solve 2x + 3 = 11, subtract 3 from both sides to isolate the x term, "
    "getting 2x = 8, then divide both sides by 2. This uses inverse operations."
)
STRONG_M001_B = (
    "Subtract 3 from both sides, then divide by 2. Inverse operations isolate x."
)
STRONG_M001_C = (
    "I isolate x: subtract 3 from both sides and divide. Inverse operations."
)
STRONG_M002 = (
    "Divide both sides by 3, then subtract 1. I could also distribute first."
)
STRONG_M002_B = (
    "Distribute, then subtract from both sides, then divide. Inverse operations."
)
STRONG_E001 = "I add 2 and 3. The sum is 5."
STRONG_E002 = "I subtract 4 from 7. The difference is 3."

GUESS_A = "I guessed."
GUESS_B = "Just a guess."
GUESS_C = "I was guessing."

WEAK_A = "I just remembered the answer."
WEAK_B = "I memorized this one."
WEAK_C = "I remembered the answer."

ARITH_M001_A = (
    "I isolated x by subtracting 3 from both sides then dividing by 2, "
    "but I arithmetic-mistakenly computed 8/2 as 5."
)
ARITH_M001_B = (
    "Subtract 3 from both sides then divide. Calculation error: I got 5."
)
ARITH_M002 = (
    "I divide both sides then subtract, but I added wrong at the last step."
)

MISC_A = (
    "I multiplied the 2 by x and then added 3, so 2(x+3) is 2x+3. "
    "I didn't distribute the 2 to both terms."
)
MISC_B = "2(x+3) is 2x+3 because I did not distribute to the 3."
MISC_C = "It's 2x+3. I didn't distribute."

WRONG = "0"
MISC_ANS = "2x+3"


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
    **kwargs: Any,
) -> Scenario:
    challenge = get_challenge(challenge_id)
    return Scenario(
        scenario_id=scenario_id,
        family=family,
        concept=CONCEPT_ID,
        category=category,
        difficulty_context=challenge.difficulty.value,
        history=history,
        current_challenge_id=challenge_id,
        current_answer=answer,
        current_reasoning=reasoning,
        current_confidence=confidence,
        expected_decisions=expected,
        forbidden_decisions=forbidden,
        expected_adaptive_behavior=behavior,
        variant=variant,
        **kwargs,
    )


def _strong_history(challenge_id: str, answer: str, reasoning: str, n: int) -> tuple[HistoryStep, ...]:
    return tuple(
        HistoryStep(challenge_id, answer, reasoning, "HIGH") for _ in range(n)
    )


def build_scenarios() -> tuple[Scenario, ...]:
    scenarios: list[Scenario] = []

    # S-001 Strong mastery evidence
    for sid, cid, ans, reason, variant in (
        ("S-001-A", "ALG-M-001", "4", STRONG_M001, "m001"),
        ("S-001-B", "ALG-M-002", "3", STRONG_M002, "m002"),
        ("S-001-C", "ALG-E-001", "5", STRONG_E001, "e001"),
    ):
        scenarios.append(
            _sc(
                sid, "S-001", "strong_mastery", cid,
                _strong_history(cid, ans, reason, 3),
                ans, reason, "HIGH",
                ("INCREASE_DIFFICULTY",),
                ("DECREASE_DIFFICULTY", "REMEDIATE"),
                "INCREASE_DIFFICULTY after repeated strong reliable success",
                variant,
                tags=("primary", "mastery"),
            )
        )

    # S-002 Lucky correct
    for sid, cid, ans, guess, variant in (
        ("S-002-A", "ALG-M-001", "4", GUESS_A, "guess-a"),
        ("S-002-B", "ALG-M-002", "3", GUESS_B, "guess-b"),
        ("S-002-C", "ALG-E-001", "5", GUESS_C, "guess-c"),
    ):
        scenarios.append(
            _sc(
                sid, "S-002", "lucky_guess", cid, (),
                ans, guess, "LOW",
                CONSERVATIVE,
                ("INCREASE_DIFFICULTY",),
                "Do not infer mastery from a lucky correct guess",
                variant,
                tags=("primary", "false_mastery"),
            )
        )

    # S-003 Correct / weak reasoning
    for sid, cid, ans, weak, variant in (
        ("S-003-A", "ALG-M-001", "4", WEAK_A, "weak-a"),
        ("S-003-B", "ALG-M-002", "3", WEAK_B, "weak-b"),
        ("S-003-C", "ALG-E-002", "3", WEAK_C, "weak-c"),
    ):
        scenarios.append(
            _sc(
                sid, "S-003", "weak_reasoning", cid, (),
                ans, weak, "LOW",
                CONSERVATIVE,
                ("INCREASE_DIFFICULTY",),
                "Correct + weak reasoning is not strong conceptual mastery",
                variant,
                tags=("primary", "reasoning"),
            )
        )

    # S-004 Incorrect / correct method
    for sid, cid, ans, reason, variant in (
        ("S-004-A", "ALG-M-001", "5", ARITH_M001_A, "arith-a"),
        ("S-004-B", "ALG-M-001", "7", ARITH_M001_B, "arith-b"),
        ("S-004-C", "ALG-M-002", "5", ARITH_M002, "arith-c"),
    ):
        scenarios.append(
            _sc(
                sid, "S-004", "arithmetic_error", cid, (),
                ans, reason, "MODERATE",
                CONSERVATIVE,
                ("INCREASE_DIFFICULTY", "REMEDIATE"),
                "Arithmetic/procedural error, not automatic conceptual misunderstanding",
                variant,
                require_not_error_type="CONCEPTUAL",
                tags=("primary", "error_type"),
            )
        )

    # S-005 Repeated misconception
    for sid, misc, variant in (
        ("S-005-A", MISC_A, "misc-a"),
        ("S-005-B", MISC_B, "misc-b"),
        ("S-005-C", MISC_C, "misc-c"),
    ):
        history = (
            HistoryStep("ALG-D-001", MISC_ANS, misc, "HIGH"),
            HistoryStep("ALG-D-001", MISC_ANS, misc, "HIGH"),
        )
        scenarios.append(
            _sc(
                sid, "S-005", "repeated_misconception", "ALG-D-001", history,
                MISC_ANS, misc, "HIGH",
                REMEDIATE_FAMILY,
                ("INCREASE_DIFFICULTY",),
                "Repeated misconception should change strategy, not increase difficulty",
                variant,
                tags=("primary", "misconception"),
            )
        )

    # S-006 Sparse evidence
    for sid, cid, ans, variant in (
        ("S-006-A", "ALG-M-001", "4", "sparse-m001"),
        ("S-006-B", "ALG-M-002", "3", "sparse-m002"),
        ("S-006-C", "ALG-E-001", "5", "sparse-e001"),
    ):
        scenarios.append(
            _sc(
                sid, "S-006", "sparse_evidence", cid, (),
                ans, None, "UNKNOWN",
                CONSERVATIVE,
                ("INCREASE_DIFFICULTY",),
                "Correct with no reasoning/confidence is insufficient evidence",
                variant,
                tags=("primary", "uncertainty"),
            )
        )

    # S-007 Ambiguous
    for sid, text, variant in (
        ("S-007-A", "Probably B. I'm not sure.", "ambig-b"),
        ("S-007-B", "Probably C. I'm not sure.", "ambig-c"),
        ("S-007-C", "Maybe D. No idea.", "ambig-d"),
    ):
        scenarios.append(
            _sc(
                sid, "S-007", "ambiguous_response", "ALG-M-001", (),
                text, None, "LOW",
                ("PROBE_UNCERTAINTY", "GATHER_MORE_EVIDENCE"),
                ("INCREASE_DIFFICULTY", "DECREASE_DIFFICULTY"),
                "Ambiguous response should probe or gather evidence",
                variant,
                tags=("primary", "uncertainty"),
            )
        )

    # S-008 Isolated noise CCCWCC
    for sid, cid, ans, reason, variant in (
        ("S-008-A", "ALG-M-001", "4", STRONG_M001, "noise-m001"),
        ("S-008-B", "ALG-M-002", "3", STRONG_M002, "noise-m002"),
        ("S-008-C", "ALG-E-001", "5", STRONG_E001, "noise-e001"),
    ):
        history = (
            HistoryStep(cid, ans, reason, "HIGH"),
            HistoryStep(cid, ans, reason, "HIGH"),
            HistoryStep(cid, ans, reason, "HIGH"),
            HistoryStep(cid, WRONG, "I mixed up a sign.", "MODERATE"),
            HistoryStep(cid, ans, reason, "HIGH"),
        )
        scenarios.append(
            _sc(
                sid, "S-008", "isolated_noise", cid, history,
                ans, reason, "HIGH",
                NOISE_OK,
                ("DECREASE_DIFFICULTY",),
                "One isolated error must not cause an extreme difficulty reduction",
                variant,
                forbid_next_difficulty=("EASY",) if cid != "ALG-E-001" else (),
                tags=("primary", "noise"),
            )
        )

    # S-009 Sudden improvement WWWCCC
    for sid, cid, ans, reason, variant in (
        ("S-009-A", "ALG-M-001", "4", STRONG_M001, "improve-m001"),
        ("S-009-B", "ALG-M-002", "3", STRONG_M002, "improve-m002"),
        ("S-009-C", "ALG-E-001", "5", STRONG_E001, "improve-e001"),
    ):
        history = tuple(
            HistoryStep(cid, WRONG, "I do not know how to isolate x.", "LOW")
            for _ in range(3)
        ) + tuple(HistoryStep(cid, ans, reason, "HIGH") for _ in range(2))
        forbid_diff = ("HARD",) if cid != "ALG-E-001" else ()
        scenarios.append(
            _sc(
                sid, "S-009", "sudden_improvement", cid, history,
                ans, reason, "HIGH",
                CONSERVATIVE,
                (),
                "Recognize improvement without jumping to maximum difficulty",
                variant,
                forbid_next_difficulty=forbid_diff,
                tags=("primary", "trajectory"),
            )
        )

    # S-010 Sudden regression CCCWW
    for sid, cid, ans, reason, variant in (
        ("S-010-A", "ALG-M-001", "4", STRONG_M001, "regress-m001"),
        ("S-010-B", "ALG-M-002", "3", STRONG_M002, "regress-m002"),
        ("S-010-C", "ALG-E-001", "5", STRONG_E001, "regress-e001"),
    ):
        history = tuple(HistoryStep(cid, ans, reason, "HIGH") for _ in range(3)) + (
            HistoryStep(cid, WRONG, "I subtracted 3 from both sides then got lost.", "LOW"),
        )
        scenarios.append(
            _sc(
                sid, "S-010", "sudden_regression", cid, history,
                WRONG, "I subtracted 3 from both sides then got lost.", "LOW",
                REGRESSION_OK,
                ("INCREASE_DIFFICULTY",),
                "Recognize regression or uncertainty; do not keep escalating",
                variant,
                tags=("primary", "trajectory"),
            )
        )

    # S-011 Conflicting evidence
    for sid, cid, ans, reason, variant in (
        ("S-011-A", "ALG-M-001", "4", STRONG_M001, "conflict-m001"),
        ("S-011-B", "ALG-M-002", "3", STRONG_M002, "conflict-m002"),
        ("S-011-C", "ALG-E-001", "5", STRONG_E001, "conflict-e001"),
    ):
        history = _strong_history(cid, ans, reason, 3)
        scenarios.append(
            _sc(
                sid, "S-011", "conflicting_evidence", cid, history,
                WRONG, GUESS_A, "LOW",
                CONFLICT_OK,
                ("INCREASE_DIFFICULTY",),
                "Weak contradictory evidence should raise uncertainty, not erase history",
                variant,
                tags=("primary", "conflict"),
            )
        )

    # S-012 / CF-P1 Strong vs weak reasoning, same 4/5 accuracy
    for variant, cid, ans, strong in (
        ("v1", "ALG-M-001", "4", STRONG_M001),
        ("v2", "ALG-M-001", "4", STRONG_M001_B),
        ("v3", "ALG-M-002", "3", STRONG_M002),
    ):
        acc_history_strong = (
            HistoryStep(cid, ans, strong, "HIGH"),
            HistoryStep(cid, WRONG, ARITH_M001_B if cid == "ALG-M-001" else ARITH_M002, "MODERATE"),
            HistoryStep(cid, ans, strong, "HIGH"),
            HistoryStep(cid, ans, strong, "HIGH"),
        )
        acc_history_weak = (
            HistoryStep(cid, ans, WEAK_A, "HIGH"),
            HistoryStep(cid, WRONG, WEAK_B, "HIGH"),
            HistoryStep(cid, ans, WEAK_A, "HIGH"),
            HistoryStep(cid, ans, WEAK_C, "HIGH"),
        )
        pair_id = f"CF-P1-{variant}"
        scenarios.append(
            _sc(
                f"{pair_id}-A", "S-012", "counterfactual_reasoning", cid,
                acc_history_strong, ans, strong, "HIGH",
                ("INCREASE_DIFFICULTY",),
                ("REMEDIATE",),
                "Strong reasoning + similar accuracy → increase difficulty",
                variant,
                counterfactual_pair_id=pair_id,
                counterfactual_role="A",
                counterfactual_dimension="reasoning_quality",
                tags=("counterfactual", "pair1"),
            )
        )
        scenarios.append(
            _sc(
                f"{pair_id}-B", "S-012", "counterfactual_reasoning", cid,
                acc_history_weak, ans, WEAK_A, "HIGH",
                CONSERVATIVE + ("REMEDIATE", "CHANGE_REPRESENTATION"),
                ("INCREASE_DIFFICULTY",),
                "Weak reasoning + similar accuracy → do not increase difficulty",
                variant,
                counterfactual_pair_id=pair_id,
                counterfactual_role="B",
                counterfactual_dimension="reasoning_quality",
                tags=("counterfactual", "pair1"),
            )
        )

    # CF-P2 No misconception vs repeated misconception
    # Interaction length matched. Accuracy is not identical because misconception
    # evidence in this implementation is carried by incorrect diagnostic answers.
    for variant, misc in (("v1", MISC_A), ("v2", MISC_B), ("v3", MISC_C)):
        pair_id = f"CF-P2-{variant}"
        a_history = _strong_history("ALG-M-001", "4", STRONG_M001, 4)
        b_history = (
            HistoryStep("ALG-D-001", MISC_ANS, misc, "HIGH"),
            HistoryStep("ALG-D-001", MISC_ANS, misc, "HIGH"),
            HistoryStep("ALG-M-001", "4", WEAK_A, "HIGH"),
            HistoryStep("ALG-M-001", "4", WEAK_A, "HIGH"),
        )
        scenarios.append(
            _sc(
                f"{pair_id}-A", "CF-P2", "counterfactual_misconception", "ALG-M-001",
                a_history, "4", STRONG_M001, "HIGH",
                ("INCREASE_DIFFICULTY",),
                ("REMEDIATE",),
                "No misconception + strong evidence → increase difficulty",
                variant,
                counterfactual_pair_id=pair_id,
                counterfactual_role="A",
                counterfactual_dimension="misconception",
                tags=("counterfactual", "pair2"),
            )
        )
        scenarios.append(
            _sc(
                f"{pair_id}-B", "CF-P2", "counterfactual_misconception", "ALG-D-001",
                b_history, MISC_ANS, misc, "HIGH",
                REMEDIATE_FAMILY,
                ("INCREASE_DIFFICULTY",),
                "Repeated misconception → remediate / change representation / gather",
                variant,
                counterfactual_pair_id=pair_id,
                counterfactual_role="B",
                counterfactual_dimension="misconception",
                tags=("counterfactual", "pair2"),
            )
        )

    # CF-P3 High vs low confidence, same strong reasoning, same 4/5 accuracy
    for variant, cid, ans, strong in (
        ("v1", "ALG-M-001", "4", STRONG_M001),
        ("v2", "ALG-M-001", "4", STRONG_M001_C),
        ("v3", "ALG-M-002", "3", STRONG_M002_B),
    ):
        pair_id = f"CF-P3-{variant}"
        hist_high = (
            HistoryStep(cid, ans, strong, "HIGH"),
            HistoryStep(cid, WRONG, ARITH_M001_B, "MODERATE"),
            HistoryStep(cid, ans, strong, "HIGH"),
            HistoryStep(cid, ans, strong, "HIGH"),
        )
        hist_low = (
            HistoryStep(cid, ans, strong, "LOW"),
            HistoryStep(cid, WRONG, ARITH_M001_B, "LOW"),
            HistoryStep(cid, ans, strong, "LOW"),
            HistoryStep(cid, ans, strong, "LOW"),
        )
        scenarios.append(
            _sc(
                f"{pair_id}-A", "CF-P3", "counterfactual_confidence", cid,
                hist_high, ans, strong, "HIGH",
                ("INCREASE_DIFFICULTY",),
                ("REMEDIATE",),
                "High-confidence strong evidence → increase difficulty",
                variant,
                counterfactual_pair_id=pair_id,
                counterfactual_role="A",
                counterfactual_dimension="learner_confidence",
                tags=("counterfactual", "pair3"),
            )
        )
        scenarios.append(
            _sc(
                f"{pair_id}-B", "CF-P3", "counterfactual_confidence", cid,
                hist_low, ans, strong, "LOW",
                CONSERVATIVE,
                ("INCREASE_DIFFICULTY",),
                "Low-confidence evidence should not be treated as strong mastery",
                variant,
                counterfactual_pair_id=pair_id,
                counterfactual_role="B",
                counterfactual_dimension="learner_confidence",
                tags=("counterfactual", "pair3"),
            )
        )

    return tuple(scenarios)


SCENARIOS = build_scenarios()
SCENARIO_BY_ID = {item.scenario_id: item for item in SCENARIOS}


def counterfactual_pairs() -> dict[str, dict[str, Scenario]]:
    pairs: dict[str, dict[str, Scenario]] = {}
    for scenario in SCENARIOS:
        if not scenario.counterfactual_pair_id:
            continue
        pairs.setdefault(scenario.counterfactual_pair_id, {})
        role = scenario.counterfactual_role or "?"
        pairs[scenario.counterfactual_pair_id][role] = scenario
    return pairs
