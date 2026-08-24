"""Longitudinal 20+ step trajectories."""

from __future__ import annotations

from adapt.models.learner_state import initial_learner_state
from adapt.pipeline import AdaptPipeline
from benchmarks.phase1f.challenge_bank import get_challenge
from benchmarks.phase1f.evaluator import make_pipeline
from benchmarks.phase1f.scenarios import HistoryStep, make_response

STRONG = (
    "Subtract 3 from both sides to isolate the x term, then divide by 2. Inverse operations."
)
STRONG_F = (
    "Convert to a common denominator, write equivalent fractions, then add the numerators."
)
MISC = "I multiplied the 2 by x and then added 3, so 2(x+3) is 2x+3. I didn't distribute."
ADD_MISC = "I added the numerators and the denominators so 2/5. I add tops and bottoms."
ARITH = (
    "I isolated x by subtracting 3 from both sides then dividing by 2, "
    "but I arithmetic-mistakenly computed 8/2 as 5."
)


def _expand(tokens: str, cid: str, ans: str, reason: str, misc_cid: str, misc_ans: str, misc_r: str) -> list[HistoryStep]:
    steps: list[HistoryStep] = []
    for token in tokens.split():
        if token == "C":
            steps.append(HistoryStep(cid, ans, reason, "HIGH"))
        elif token == "W":
            steps.append(HistoryStep(cid, "0", ARITH, "LOW"))
        elif token == "M":
            steps.append(HistoryStep(misc_cid, misc_ans, misc_r, "HIGH"))
        elif token == "G":
            steps.append(HistoryStep(cid, ans, "I guessed.", "LOW"))
        elif token == "S":
            steps.append(HistoryStep(cid, ans, reason, "LOW"))
        else:
            raise ValueError(token)
    return steps


TRAJECTORIES = (
    {
        "trajectory_id": "LT-001",
        "concept": "basic_algebra",
        "description": "success, isolated miss, delayed misconception, remediation window, recovery",
        "cid": "ALG-M-001",
        "ans": "4",
        "reason": STRONG,
        "misc_cid": "ALG-D-001",
        "misc_ans": "2x+3",
        "misc_r": MISC,
        "tokens": "C C W C C M M M C C C W C C G C C C C C",
    },
    {
        "trajectory_id": "LT-002",
        "concept": "fractions",
        "description": "fraction transfer with add-denominator misconception then recovery",
        "cid": "FR-M-001",
        "ans": "5/6",
        "reason": STRONG_F,
        "misc_cid": "FR-D-001",
        "misc_ans": "2/5",
        "misc_r": ADD_MISC,
        "tokens": "C C C M M M C C C W C C C S C C G C C C",
    },
    {
        "trajectory_id": "LT-003",
        "concept": "basic_algebra",
        "description": "oscillating correctness without a stable misconception",
        "cid": "ALG-M-003",
        "ans": "3",
        "reason": "Add 1 to both sides, then divide by 4 to isolate x. Inverse operations.",
        "misc_cid": "ALG-D-001",
        "misc_ans": "2x+3",
        "misc_r": MISC,
        "tokens": "C W C W C W C C W C C C W C C G C C W C",
    },
    {
        "trajectory_id": "LT-004",
        "concept": "basic_algebra",
        "description": "strong start, regression cluster, then slow recovery",
        "cid": "ALG-M-001",
        "ans": "4",
        "reason": STRONG,
        "misc_cid": "ALG-D-003",
        "misc_ans": "5x",
        "misc_r": "2x + 3 combines to 5x because you combine like 2 and 3 into 5x.",
        "tokens": "C C C C W W W C C M C C C C W C C C C C",
    },
    {
        "trajectory_id": "LT-005",
        "concept": "fractions",
        "description": "uncertain sparse start, then consistent strong evidence",
        "cid": "FR-E-001",
        "ans": "1",
        "reason": STRONG_F,
        "misc_cid": "FR-D-001",
        "misc_ans": "2/5",
        "misc_r": ADD_MISC,
        "tokens": "G G C G C C C C C W C C C C C C C C C C",
    },
)


def _coherent(states: list[dict]) -> bool:
    for item in states:
        mastery = item["mastery_estimate"]
        if not 0.0 <= mastery <= 1.0:
            return False
        if item["uncertainty"] == "LOW_UNCERTAINTY" and item["evidence_strength"] == "INSUFFICIENT":
            return False
    deltas = [
        states[i]["mastery_estimate"] - states[i - 1]["mastery_estimate"]
        for i in range(1, len(states))
    ]
    return all(abs(delta) <= 0.20 for delta in deltas)


def run_longitudinal(pipeline: AdaptPipeline | None = None) -> list[dict]:
    pipe = pipeline or make_pipeline()
    results = []
    for spec in TRAJECTORIES:
        tokens = spec["tokens"]
        assert len(tokens.split()) >= 20
        steps_spec = _expand(
            tokens,
            spec["cid"],
            spec["ans"],
            spec["reason"],
            spec["misc_cid"],
            spec["misc_ans"],
            spec["misc_r"],
        )
        pairs = []
        learner_id = spec["trajectory_id"]
        for index, step in enumerate(steps_spec, start=1):
            pairs.append(
                (
                    get_challenge(step.challenge_id),
                    make_response(
                        response_id=f"{learner_id}-S{index:02d}",
                        learner_id=learner_id,
                        challenge_id=step.challenge_id,
                        answer=step.answer,
                        reasoning=step.reasoning,
                        confidence=step.learner_confidence,
                    ),
                )
            )
        traces = pipe.run_sequence(
            learner_state=initial_learner_state(learner_id, spec["concept"]),
            steps=pairs,
        )
        states = [item.learner_state_after.to_dict() for item in traces]
        decisions = [item.adaptation_decision.decision.value for item in traces]
        stable = len(traces) >= 20 and _coherent(states)
        results.append(
            {
                "trajectory_id": spec["trajectory_id"],
                "description": spec["description"],
                "concept": spec["concept"],
                "steps": len(traces),
                "stable": stable,
                "passed": stable,
                "final_decision": decisions[-1],
                "final_mastery": states[-1]["mastery_estimate"],
                "final_uncertainty": states[-1]["uncertainty"],
                "mastery_path": [round(item["mastery_estimate"], 4) for item in states],
                "decisions": decisions,
                "traceable": all(
                    item.adaptation_decision.reason and item.adaptation_decision.evidence_used
                    for item in traces
                ),
            }
        )
    return results
