"""Gemini evidence-extraction workflow (Nodes 1–3).

Nodes 4–6 remain AdaptiveTutor: state update, strategy, challenge selection.
Gemini interprets evidence. ADAPT decides how to adapt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from adapt.llm.client import LLMClient, LLMGeneration
from adapt.llm.config import DEFAULT_PROMPT_ID, WORKFLOW_VERSION, load_settings
from adapt.llm.errors import LLMError, LLMValidationFailure
from adapt.llm.fallback import SOURCE_FALLBACK, SOURCE_GEMINI, SOURCE_NVIDIA, DeterministicFallback
from adapt.llm.gemini import GeminiClient
from adapt.llm.prompts import challenge_payload, learner_payload, prompt_version, render_prompt
from adapt.llm.schemas import LLMEvidence
from adapt.llm.validator import parse_and_validate
from adapt.models.challenge import Challenge
from adapt.models.evidence import Evidence
from adapt.models.learner_response import LearnerResponse

NODE_HUMAN_INPUT = "human_input"
NODE_GEMINI_EXTRACTION = "gemini_extraction"
NODE_VALIDATION = "evidence_validation"
NODE_STATE_UPDATE = "adapt_state_update"
NODE_STRATEGY = "adapt_strategy"
NODE_CHALLENGE = "challenge_selection"
NODE_FEEDBACK = "human_feedback"


@dataclass
class WorkflowNode:
    id: str
    name: str
    actor: str
    purpose: str
    status: str
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "actor": self.actor,
            "purpose": self.purpose,
            "status": self.status,
            "detail": dict(self.detail),
        }


@dataclass
class WorkflowResult:
    source: str
    prompt_id: str
    prompt_version: str
    workflow_version: str
    model: str | None
    temperature: float | None
    raw_text: str | None
    parsed: dict[str, Any] | None
    llm_evidence: LLMEvidence | None
    evidence: Evidence
    validation_ok: bool
    failure_code: str | None
    failure_message: str | None
    nodes: list[WorkflowNode]
    human_input: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "workflow_version": self.workflow_version,
            "model": self.model,
            "temperature": self.temperature,
            "raw_text": self.raw_text,
            "parsed": self.parsed,
            "llm_evidence": None if self.llm_evidence is None else self.llm_evidence.to_dict(),
            "evidence": self.evidence.to_dict(),
            "validation_ok": self.validation_ok,
            "failure_code": self.failure_code,
            "failure_message": self.failure_message,
            "nodes": [node.to_dict() for node in self.nodes],
            "human_input": dict(self.human_input),
        }


class EvidenceExtractionWorkflow:
    """Node 2 calls the LLM. Node 3 validates. Invalid output never enters ADAPT."""

    def __init__(
        self,
        *,
        client: LLMClient | None = None,
        prompt_id: str | None = None,
        fallback: DeterministicFallback | None = None,
        require_llm: bool = False,
    ) -> None:
        settings = load_settings()
        self.settings = settings
        self.prompt_id = prompt_id or settings.prompt_id or DEFAULT_PROMPT_ID
        self.fallback = fallback or DeterministicFallback()
        self.require_llm = require_llm
        if client is not None:
            self.client = client
        elif settings.credentials_present:
            self.client = GeminiClient(settings=settings)
        else:
            self.client = None

    def extract(
        self,
        response: LearnerResponse,
        challenge: Challenge | None,
        history: list[LearnerResponse] | None = None,
    ) -> WorkflowResult:
        human = _human_input(response)
        nodes = [
            WorkflowNode(
                id="1",
                name=NODE_HUMAN_INPUT,
                actor="human",
                purpose="Collect answer, confidence, approach, and optional explanation.",
                status="complete",
                detail=human,
            )
        ]
        if self.client is None or not _client_available(self.client):
            if self.require_llm:
                raise LLMError("LLM client is not available")
            evidence = self.fallback.analyze(response, challenge, history)
            nodes.append(
                WorkflowNode(
                    id="2",
                    name=NODE_GEMINI_EXTRACTION,
                    actor="gemini",
                    purpose="Extract structured learner evidence. Does not choose strategy.",
                    status="skipped",
                    detail={"reason": "credentials_unavailable"},
                )
            )
            nodes.append(
                WorkflowNode(
                    id="3",
                    name=NODE_VALIDATION,
                    actor="validator",
                    purpose="Reject malformed LLM output so it cannot corrupt learner state.",
                    status="skipped",
                    detail={"fallback": SOURCE_FALLBACK},
                )
            )
            return WorkflowResult(
                source=SOURCE_FALLBACK,
                prompt_id=self.prompt_id,
                prompt_version=prompt_version(self.prompt_id),
                workflow_version=WORKFLOW_VERSION,
                model=None,
                temperature=None,
                raw_text=None,
                parsed=None,
                llm_evidence=None,
                evidence=evidence,
                validation_ok=False,
                failure_code="LLM_UNAVAILABLE",
                failure_message="LLM credentials are unavailable; using deterministic fallback.",
                nodes=nodes,
                human_input=human,
            )

        prompt = render_prompt(
            self.prompt_id,
            learner=human,
            challenge=challenge_payload(challenge),
        )
        try:
            generation = self.client.generate(prompt, prompt_id=self.prompt_id)
        except LLMError as exc:
            return self._fallback_result(
                response,
                challenge,
                history,
                human,
                nodes,
                failure_code=getattr(exc, "code", "LLM_UNAVAILABLE"),
                failure_message=str(exc),
                raw_text=None,
            )
        nodes.append(
            WorkflowNode(
                id="2",
                name=NODE_GEMINI_EXTRACTION,
                actor="gemini",
                purpose="Extract structured learner evidence. Does not choose strategy.",
                status="complete",
                detail={
                    "model": generation.model,
                    "provider": generation.provider,
                    "prompt_id": self.prompt_id,
                    "prompt_version": prompt_version(self.prompt_id),
                },
            )
        )
        try:
            llm_evidence = parse_and_validate(generation.text)
        except LLMValidationFailure as exc:
            return self._fallback_result(
                response,
                challenge,
                history,
                human,
                nodes,
                failure_code=exc.code,
                failure_message=str(exc),
                raw_text=generation.text,
                model=generation.model,
                temperature=generation.temperature,
            )
        nodes.append(
            WorkflowNode(
                id="3",
                name=NODE_VALIDATION,
                actor="validator",
                purpose="Reject malformed LLM output so it cannot corrupt learner state.",
                status="complete",
                detail={"ok": True},
            )
        )
        evidence = llm_evidence.to_adapt_evidence(response.response_id)
        return WorkflowResult(
            source=_live_source(generation),
            prompt_id=self.prompt_id,
            prompt_version=prompt_version(self.prompt_id),
            workflow_version=WORKFLOW_VERSION,
            model=generation.model,
            temperature=generation.temperature,
            raw_text=generation.text,
            parsed=llm_evidence.to_dict(),
            llm_evidence=llm_evidence,
            evidence=evidence,
            validation_ok=True,
            failure_code=None,
            failure_message=None,
            nodes=nodes,
            human_input=human,
        )

    def _fallback_result(
        self,
        response: LearnerResponse,
        challenge: Challenge | None,
        history: list[LearnerResponse] | None,
        human: dict[str, Any],
        nodes: list[WorkflowNode],
        *,
        failure_code: str,
        failure_message: str,
        raw_text: str | None,
        model: str | None = None,
        temperature: float | None = None,
    ) -> WorkflowResult:
        if not any(node.name == NODE_GEMINI_EXTRACTION for node in nodes):
            nodes.append(
                WorkflowNode(
                    id="2",
                    name=NODE_GEMINI_EXTRACTION,
                    actor="gemini",
                    purpose="Extract structured learner evidence. Does not choose strategy.",
                    status="failed",
                    detail={"code": failure_code},
                )
            )
        nodes.append(
            WorkflowNode(
                id="3",
                name=NODE_VALIDATION,
                actor="validator",
                purpose="Reject malformed LLM output so it cannot corrupt learner state.",
                status="failed",
                detail={"code": failure_code, "message": failure_message},
            )
        )
        evidence = self.fallback.analyze(response, challenge, history)
        return WorkflowResult(
            source=SOURCE_FALLBACK,
            prompt_id=self.prompt_id,
            prompt_version=prompt_version(self.prompt_id),
            workflow_version=WORKFLOW_VERSION,
            model=model,
            temperature=temperature,
            raw_text=raw_text,
            parsed=None,
            llm_evidence=None,
            evidence=evidence,
            validation_ok=False,
            failure_code=failure_code,
            failure_message=failure_message,
            nodes=nodes,
            human_input=human,
        )


def attach_adapt_nodes(
    result: WorkflowResult,
    *,
    state: dict[str, Any],
    strategy: dict[str, Any],
    challenge: dict[str, Any],
    feedback: dict[str, Any] | None = None,
) -> WorkflowResult:
    """Record Nodes 4–7 from AdaptiveTutor. Does not change the engine decision."""
    extra = [
        WorkflowNode(
            id="4",
            name=NODE_STATE_UPDATE,
            actor="adapt",
            purpose="Deterministic learner-state update from validated evidence.",
            status="complete",
            detail=state,
        ),
        WorkflowNode(
            id="5",
            name=NODE_STRATEGY,
            actor="adapt",
            purpose="Deterministic instructional strategy. Gemini cannot override this.",
            status="complete",
            detail=strategy,
        ),
        WorkflowNode(
            id="6",
            name=NODE_CHALLENGE,
            actor="adapt",
            purpose="Select the next challenge from strategy. Gemini cannot choose it.",
            status="complete",
            detail=challenge,
        ),
        WorkflowNode(
            id="7",
            name=NODE_FEEDBACK,
            actor="human",
            purpose="Show a short, trace-backed explanation to the learner.",
            status="complete",
            detail=feedback or {},
        ),
    ]
    result.nodes = [node for node in result.nodes if node.id in {"1", "2", "3"}] + extra
    return result


def _human_input(response: LearnerResponse) -> dict[str, Any]:
    metadata = response.metadata or {}
    return learner_payload(
        answer=response.answer,
        confidence=response.learner_confidence.value,
        approach=metadata.get("approach"),
        explanation=metadata.get("explanation"),
        reasoning=response.reasoning,
    )


def _client_available(client: LLMClient) -> bool:
    available = getattr(client, "available", None)
    if callable(available):
        return bool(available())
    return True


def _live_source(generation: LLMGeneration) -> str:
    provider = (generation.provider or "").strip().lower()
    if provider == "nvidia":
        return SOURCE_NVIDIA
    return SOURCE_GEMINI
