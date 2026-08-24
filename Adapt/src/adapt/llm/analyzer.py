"""Evidence analyzer adapter: Gemini extraction with deterministic fallback.

Implements the same analyze() contract as EvidenceAnalyzer so AdaptiveTutor
can use it without engine changes. Gemini cannot update state or pick challenges.
"""

from __future__ import annotations

from adapt.analysis.evidence_analyzer import EvidenceAnalyzer
from adapt.llm.client import LLMClient
from adapt.llm.fallback import DeterministicFallback
from adapt.llm.workflow import EvidenceExtractionWorkflow, WorkflowResult
from adapt.models.challenge import Challenge
from adapt.models.evidence import Evidence
from adapt.models.learner_response import LearnerResponse


class LLMEvidenceAnalyzer(EvidenceAnalyzer):
    """Drop-in analyzer. AdaptiveTutor still owns state, strategy, and selection."""

    def __init__(
        self,
        *,
        client: LLMClient | None = None,
        prompt_id: str | None = None,
        workflow: EvidenceExtractionWorkflow | None = None,
    ) -> None:
        self.workflow = workflow or EvidenceExtractionWorkflow(
            client=client,
            prompt_id=prompt_id,
            fallback=DeterministicFallback(),
        )
        self.last_result: WorkflowResult | None = None

    def analyze(
        self,
        response: LearnerResponse,
        challenge: Challenge | None,
        history: list[LearnerResponse] | None = None,
    ) -> Evidence:
        result = self.workflow.extract(response, challenge, history)
        self.last_result = result
        return result.evidence
