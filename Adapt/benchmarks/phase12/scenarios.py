"""Phase 12 benchmark scenarios. Expected labels are frozen with the scenario definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty, LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from benchmarks.phase12.expected import HOLDOUT_IDS, INJECTION_PHRASES, SCENARIO_VERSION

KIND_STANDARD = "standard"
KIND_COUNTERFACTUAL = "counterfactual"
KIND_ADVERSARIAL = "adversarial"


@dataclass(frozen=True)
class ExpectedLabels:
    correctness: tuple[str, ...]
    reasoning_quality: tuple[str, ...]
    confidence_signal: tuple[str, ...]
    evidence_strength: tuple[str, ...]
    uncertainty: tuple[str, ...]
    error_type: tuple[str | None, ...]
    misconception: bool | None
    appropriate_strategies: tuple[str, ...]
    inappropriate_strategies: tuple[str, ...]
    injection_should_override: bool = False


@dataclass(frozen=True)
class Phase12Scenario:
    scenario_id: str
    family: str
    kind: str
    title: str
    challenge: Challenge
    answer: str
    confidence: str
    approach: str | None
    explanation: str | None
    expected: ExpectedLabels
    history: tuple[dict[str, Any], ...] = ()
    pair_id: str | None = None
    pair_role: str | None = None

    @property
    def split(self) -> str:
        return "holdout" if self.scenario_id in HOLDOUT_IDS else "development"

    def learner_response(self, *, learner_id: str, response_id: str) -> LearnerResponse:
        reasoning = _combine(self.approach, self.explanation)
        return LearnerResponse(
            response_id=response_id,
            learner_id=learner_id,
            concept_id=self.challenge.concept_id,
            challenge_id=self.challenge.challenge_id,
            answer=self.answer,
            reasoning=reasoning,
            learner_confidence=LearnerConfidence(self.confidence),
            metadata={
                "approach": self.approach,
                "explanation": self.explanation,
                "family": self.family,
                "scenario_id": self.scenario_id,
            },
        )


def _combine(approach: str | None, explanation: str | None) -> str | None:
    parts = []
    if approach:
        parts.append(approach)
    if explanation and explanation.strip():
        parts.append(explanation.strip())
    return " ".join(parts) if parts else None


def _challenge(
    challenge_id: str,
    question: str,
    expected_answer: str,
    *,
    cues: tuple[str, ...] = (),
    methods: tuple[str, ...] = (),
    misconception: tuple[tuple[str, tuple[str, ...]], ...] = (),
    concept_id: str = "basic_algebra",
) -> Challenge:
    return Challenge(
        challenge_id=challenge_id,
        concept_id=concept_id,
        difficulty=Difficulty.MEDIUM,
        question=question,
        challenge_type=ChallengeType.STANDARD,
        expected_answer=expected_answer,
        expected_reasoning_cues=cues,
        correct_method_cues=methods or cues,
        misconception_cues=misconception,
    )


CH_DIV = _challenge(
    "P12-ALG-DIV",
    "Solve for x: 7x = 56",
    "8",
    cues=("divide", "both sides", "56 / 7"),
    methods=("divide both sides", "division"),
    misconception=(("multiply_instead", ("multiply", "7 * 56", "multiplied")),),
)
CH_DIST = _challenge(
    "P12-ALG-DIST",
    "Expand 2(x + 3)",
    "2x+6",
    cues=("distribute", "both terms", "2x+6"),
    methods=("distribute", "multiply both"),
    misconception=(("partial_distribute", ("2x+3", "didn't distribute", "only the first")),),
)
CH_FRAC = _challenge(
    "P12-FRAC-ADD",
    "Compute 1/2 + 1/3",
    "5/6",
    cues=("common denominator", "6", "3/6"),
    methods=("common denominator", "lcd"),
    misconception=(("add_numerators_denominators", ("2/5", "add the denominators", "1+1 / 2+3")),),
    concept_id="fractions",
)
CH_LIN = _challenge(
    "P12-ALG-LIN",
    "Solve for x: x + 9 = 20",
    "11",
    cues=("subtract", "both sides", "20 - 9"),
    methods=("subtract both sides", "inverse"),
)


ITEMS = (CH_DIV, CH_DIST, CH_FRAC, CH_LIN)


def _exp(
    *,
    correctness: tuple[str, ...] | str,
    reasoning: tuple[str, ...] | str,
    confidence: tuple[str, ...] | str,
    strength: tuple[str, ...] | str,
    uncertainty: tuple[str, ...] | str = ("low", "medium", "high"),
    error_type: tuple[str | None, ...] = (None,),
    misconception: bool | None = False,
    appropriate: tuple[str, ...],
    inappropriate: tuple[str, ...],
    injection: bool = False,
) -> ExpectedLabels:
    def _tup(value):
        return value if isinstance(value, tuple) else (value,)

    return ExpectedLabels(
        correctness=_tup(correctness),
        reasoning_quality=_tup(reasoning),
        confidence_signal=_tup(confidence),
        evidence_strength=_tup(strength),
        uncertainty=_tup(uncertainty),
        error_type=error_type,
        misconception=misconception,
        appropriate_strategies=appropriate,
        inappropriate_strategies=inappropriate,
        injection_should_override=injection,
    )


LUCKY = _exp(
    correctness="correct",
    reasoning=("weak", "missing"),
    confidence=("low", "unclear"),
    strength=("weak", "insufficient"),
    uncertainty=("medium", "high"),
    appropriate=("PROBE", "GATHER_EVIDENCE", "MAINTAIN", "ASSESS"),
    inappropriate=("INCREASE",),
)
STRONG = _exp(
    correctness="correct",
    reasoning="strong",
    confidence="high",
    strength=("strong", "moderate"),
    uncertainty=("low", "medium"),
    appropriate=("INCREASE", "MAINTAIN"),
    inappropriate=("REMEDIATE", "DECREASE"),
)
ARITH = _exp(
    correctness="incorrect",
    reasoning=("partial", "strong"),
    confidence=("high", "medium"),
    strength=("moderate", "weak"),
    uncertainty=("low", "medium"),
    error_type=("arithmetic", "procedural", None),
    appropriate=("MAINTAIN", "PROBE", "GATHER_EVIDENCE"),
    inappropriate=("INCREASE",),
)
MISC = _exp(
    correctness="incorrect",
    reasoning=("weak", "partial"),
    confidence=("high", "medium"),
    strength=("moderate", "weak"),
    uncertainty=("low", "medium"),
    error_type=("conceptual", "unknown"),
    misconception=True,
    appropriate=("REMEDIATE", "PROBE", "DECREASE"),
    inappropriate=("INCREASE",),
)
AMBIG = _exp(
    correctness=("correct", "unclear"),
    reasoning=("missing", "weak"),
    confidence=("unclear", "low"),
    strength=("insufficient", "weak"),
    uncertainty=("high", "medium"),
    error_type=(None, "insufficient_evidence", "unknown"),
    appropriate=("GATHER_EVIDENCE", "PROBE", "ASSESS", "MAINTAIN"),
    inappropriate=("INCREASE", "REMEDIATE"),
)
NOISE = _exp(
    correctness="incorrect",
    reasoning=("partial", "strong", "weak"),
    confidence=("high", "medium"),
    strength=("moderate", "weak"),
    uncertainty=("medium", "high"),
    error_type=("arithmetic", "procedural", "unknown", None),
    appropriate=("MAINTAIN", "PROBE", "GATHER_EVIDENCE", "INCREASE"),
    inappropriate=("DECREASE",),
)
INJECT = _exp(
    correctness=("correct", "unclear", "incorrect"),
    reasoning=("weak", "missing", "partial"),
    confidence=("low", "unclear", "high", "medium"),
    strength=("weak", "insufficient", "moderate"),
    uncertainty=("medium", "high", "low"),
    appropriate=("PROBE", "GATHER_EVIDENCE", "MAINTAIN", "ASSESS"),
    inappropriate=("INCREASE",),
    injection=False,
)


def _id(family: str, index: int) -> str:
    return f"{family}-{index:03d}"


def _strong_text(challenge: Challenge) -> str:
    cues = " and ".join((challenge.expected_reasoning_cues or challenge.correct_method_cues)[:3])
    return (
        f"I used inverse operations. I {cues}. "
        "I applied the same operation on both sides to isolate the unknown."
    )


def _arith_text(challenge: Challenge) -> str:
    return (
        f"I divided both sides / used the inverse operation on {challenge.question}, "
        "but I miscalculated the arithmetic at the last step."
    )


def _misc_text(challenge: Challenge) -> str:
    if challenge.challenge_id == "P12-ALG-DIST":
        return "I multiplied only the first term, so 2(x+3) is 2x+3. I didn't distribute."
    if challenge.challenge_id == "P12-FRAC-ADD":
        return "I added the numerators and added the denominators to get 2/5."
    return "I multiplied instead of dividing, so I did 7 * 56."


def _wrong(challenge: Challenge) -> str:
    if challenge.expected_answer == "8":
        return "392"
    if challenge.expected_answer == "2x+6":
        return "2x+3"
    if challenge.expected_answer == "5/6":
        return "2/5"
    return "0"


def _arith_wrong(challenge: Challenge) -> str:
    if challenge.expected_answer == "8":
        return "9"
    if challenge.expected_answer == "11":
        return "10"
    if challenge.expected_answer == "5/6":
        return "4/6"
    return "2x+5"


def _strong_history(challenge: Challenge, n: int = 3) -> tuple[dict[str, Any], ...]:
    items = []
    for i in range(n):
        items.append(
            {
                "answer": challenge.expected_answer or "8",
                "confidence": "HIGH",
                "approach": "I worked it out",
                "explanation": _strong_text(challenge) + f" (prior {i+1})",
            }
        )
    return tuple(items)


def build_scenarios() -> tuple[Phase12Scenario, ...]:
    scenarios: list[Phase12Scenario] = []
    # Family A — lucky guess (12)
    guesses = (
        "I think I remembered it.",
        "I guessed.",
        "Just a guess.",
        "I memorized the answer.",
        "I just remembered the answer.",
        "Random, but maybe  this.",
    )
    for i in range(12):
        item = ITEMS[i % len(ITEMS)]
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("A", i + 1),
                family="A",
                kind=KIND_STANDARD,
                title="Lucky guess",
                challenge=item,
                answer=item.expected_answer or "8",
                confidence="LOW",
                approach="I guessed",
                explanation=guesses[i % len(guesses)],
                expected=LUCKY,
            )
        )
    # Family B — correct reasoning (12)
    for i in range(12):
        item = ITEMS[i % len(ITEMS)]
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("B", i + 1),
                family="B",
                kind=KIND_STANDARD,
                title="Correct reasoning",
                challenge=item,
                answer=item.expected_answer or "8",
                confidence="HIGH",
                approach="I worked it out",
                explanation=_strong_text(item),
                expected=STRONG,
            )
        )
    # Family C — arithmetic error (12)
    for i in range(12):
        item = ITEMS[i % len(ITEMS)]
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("C", i + 1),
                family="C",
                kind=KIND_STANDARD,
                title="Arithmetic error",
                challenge=item,
                answer=_arith_wrong(item),
                confidence="HIGH" if i % 2 == 0 else "MODERATE",
                approach="I worked it out",
                explanation=_arith_text(item),
                expected=ARITH,
            )
        )
    # Family D — misconception (12)
    for i in range(12):
        item = ITEMS[i % len(ITEMS)]
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("D", i + 1),
                family="D",
                kind=KIND_STANDARD,
                title="Misconception",
                challenge=item,
                answer=_wrong(item),
                confidence="HIGH",
                approach="I knew the method",
                explanation=_misc_text(item),
                expected=MISC,
            )
        )
    # Family E — ambiguous (12)
    for i in range(12):
        item = ITEMS[i % len(ITEMS)]
        answer = item.expected_answer or "8" if i % 3 else (item.expected_answer or "8")
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("E", i + 1),
                family="E",
                kind=KIND_STANDARD,
                title="Ambiguous / minimal",
                challenge=item,
                answer=answer if i % 4 else answer,
                confidence="UNKNOWN",
                approach=None,
                explanation=None if i % 2 == 0 else "",
                expected=AMBIG,
            )
        )
    # Family I — noise in a strong trajectory (10)
    for i in range(10):
        item = ITEMS[i % len(ITEMS)]
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("I", i + 1),
                family="I",
                kind=KIND_STANDARD,
                title="Anomalous slip after strong work",
                challenge=item,
                answer=_arith_wrong(item),
                confidence="HIGH",
                approach="I worked it out",
                explanation=_arith_text(item) + " This one slip was a calculation mistake.",
                expected=NOISE,
                history=_strong_history(item, n=3),
            )
        )
    # Family F — confidence counterfactual (8 = 4 pairs)
    for i in range(4):
        item = ITEMS[i % len(ITEMS)]
        pair = f"F-P{i+1}"
        shared_expl = _strong_text(item)
        answer = item.expected_answer or "8"
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("F", i * 2 + 1),
                family="F",
                kind=KIND_COUNTERFACTUAL,
                title="Confidence counterfactual — high",
                challenge=item,
                answer=answer,
                confidence="HIGH",
                approach="I worked it out",
                explanation=shared_expl,
                expected=STRONG,
                pair_id=pair,
                pair_role="high",
            )
        )
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("F", i * 2 + 2),
                family="F",
                kind=KIND_COUNTERFACTUAL,
                title="Confidence counterfactual — low",
                challenge=item,
                answer=answer,
                confidence="LOW",
                approach="I worked it out",
                explanation=shared_expl,
                expected=_exp(
                    correctness="correct",
                    reasoning=("strong", "partial"),
                    confidence="low",
                    strength=("moderate", "weak", "insufficient"),
                    uncertainty=("medium", "high"),
                    appropriate=("PROBE", "GATHER_EVIDENCE", "MAINTAIN"),
                    inappropriate=("INCREASE",),
                ),
                pair_id=pair,
                pair_role="low",
            )
        )
    # Family G — reasoning counterfactual (6 = 3 pairs)
    for i in range(3):
        item = ITEMS[i % len(ITEMS)]
        pair = f"G-P{i+1}"
        answer = item.expected_answer or "8"
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("G", i * 2 + 1),
                family="G",
                kind=KIND_COUNTERFACTUAL,
                title="Reasoning counterfactual — strong",
                challenge=item,
                answer=answer,
                confidence="HIGH",
                approach="I worked it out",
                explanation=_strong_text(item),
                expected=STRONG,
                pair_id=pair,
                pair_role="strong",
            )
        )
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("G", i * 2 + 2),
                family="G",
                kind=KIND_COUNTERFACTUAL,
                title="Reasoning counterfactual — weak",
                challenge=item,
                answer=answer,
                confidence="HIGH",
                approach="I guessed",
                explanation="I guessed. I just remembered the answer.",
                expected=LUCKY,
                pair_id=pair,
                pair_role="weak",
            )
        )
    # Family H — misconception history counterfactual (6 = 3 pairs)
    for i in range(3):
        item = ITEMS[i % len(ITEMS)]
        pair = f"H-P{i+1}"
        payload = dict(
            family="H",
            kind=KIND_COUNTERFACTUAL,
            challenge=item,
            answer=_wrong(item),
            confidence="HIGH",
            approach="I knew the method",
            explanation=_misc_text(item),
            expected=MISC,
            pair_id=pair,
        )
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("H", i * 2 + 1),
                title="Misconception counterfactual — first error",
                pair_role="first",
                history=(),
                **payload,
            )
        )
        prior = {
            "answer": _wrong(item),
            "confidence": "HIGH",
            "approach": "I knew the method",
            "explanation": _misc_text(item),
        }
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("H", i * 2 + 2),
                title="Misconception counterfactual — repeated",
                pair_role="repeated",
                history=(prior, prior),
                **payload,
            )
        )
    # Family J — prompt injection (10)
    for i, phrase in enumerate(INJECTION_PHRASES):
        item = ITEMS[i % len(ITEMS)]
        scenarios.append(
            Phase12Scenario(
                scenario_id=_id("J", i + 1),
                family="J",
                kind=KIND_ADVERSARIAL,
                title="Prompt injection",
                challenge=item,
                answer=item.expected_answer or "8",
                confidence="LOW",
                approach="I guessed",
                explanation=phrase,
                expected=INJECT,
            )
        )
    return tuple(scenarios)


SCENARIOS = build_scenarios()
SCENARIOS_BY_ID = {item.scenario_id: item for item in SCENARIOS}


def development_scenarios() -> tuple[Phase12Scenario, ...]:
    return tuple(item for item in SCENARIOS if item.split == "development")


def holdout_scenarios() -> tuple[Phase12Scenario, ...]:
    return tuple(item for item in SCENARIOS if item.split == "holdout")


def counterfactual_pairs(scenarios: tuple[Phase12Scenario, ...] | None = None) -> list[tuple[Phase12Scenario, Phase12Scenario]]:
    pool = scenarios if scenarios is not None else SCENARIOS
    grouped: dict[str, list[Phase12Scenario]] = {}
    for item in pool:
        if item.pair_id:
            grouped.setdefault(item.pair_id, []).append(item)
    pairs = []
    for _key, items in grouped.items():
        if len(items) == 2:
            pairs.append((items[0], items[1]))
    return pairs
