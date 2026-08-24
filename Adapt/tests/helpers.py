"""Shared builders for Phase 1D tests."""

from __future__ import annotations

from adapt.adaptation.challenge_bank import CONCEPT_ID, get_challenge
from adapt.models.enums import LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from adapt.models.learner_state import initial_learner_state
from adapt.pipeline import AdaptPipeline

MEDIUM = get_challenge("ALG-M-001")
DIAGNOSTIC = get_challenge("ALG-D-001")
EASY = get_challenge("ALG-E-001")

STRONG_REASONING = (
    "To solve 2x + 3 = 11, subtract 3 from both sides to isolate the x term, "
    "getting 2x = 8, then divide both sides by 2. This uses inverse operations."
)
WEAK_REASONING = "I just remembered the answer."
GUESS_REASONING = "I guessed."
ARITHMETIC_REASONING = (
    "I isolated x by subtracting 3 from both sides then dividing by 2, "
    "but I arithmetic-mistakenly computed 8/2 as 5."
)
MISCONCEPTION_REASONING = (
    "I multiplied the 2 by x and then added 3, so 2(x+3) is 2x+3. "
    "I didn't distribute the 2 to both terms."
)


def new_state(learner_id: str = "L-001"):
    return initial_learner_state(learner_id, CONCEPT_ID)


def make_response(
    *,
    response_id: str,
    challenge_id: str,
    answer: str,
    reasoning: str | None,
    learner_confidence: LearnerConfidence,
    learner_id: str = "L-001",
) -> LearnerResponse:
    return LearnerResponse(
        response_id=response_id,
        learner_id=learner_id,
        concept_id=CONCEPT_ID,
        challenge_id=challenge_id,
        answer=answer,
        reasoning=reasoning,
        learner_confidence=learner_confidence,
    )


def run_one(state, challenge, response, pipeline=None):
    pipe = pipeline or AdaptPipeline()
    return pipe.run(learner_state=state, challenge=challenge, response=response)
