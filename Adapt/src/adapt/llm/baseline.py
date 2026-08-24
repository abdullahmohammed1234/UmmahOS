"""Single-prompt Gemini baseline.

One prompt produces a tutoring action. This path does not use AdaptiveTutor.
It exists only for fair comparison against the structured evidence workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from adapt.llm.client import LLMClient
from adapt.llm.config import load_settings
from adapt.llm.errors import LLMError, LLMValidationFailure
from adapt.llm.gemini import GeminiClient
from adapt.llm.prompts import challenge_payload, learner_payload, prompt_version, render_prompt
from adapt.llm.validator import extract_json_object
from adapt.models.challenge import Challenge
from adapt.models.learner_response import LearnerResponse

BASELINE_PROMPT_ID = "baseline_v1"
BASELINE_ACTIONS = ("INCREASE", "DECREASE", "PROBE", "REMEDIATE", "MAINTAIN")


@dataclass(frozen=True)
class BaselineResult:
    next_action: str | None
    mastery: str | None
    message: str | None
    reason: str | None
    raw_text: str | None
    parsed: dict[str, Any] | None
    prompt_id: str
    prompt_version: str
    model: str | None
    valid: bool
    failure_code: str | None
    failure_message: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "next_action": self.next_action,
            "mastery": self.mastery,
            "message": self.message,
            "reason": self.reason,
            "raw_text": self.raw_text,
            "parsed": self.parsed,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "model": self.model,
            "valid": self.valid,
            "failure_code": self.failure_code,
            "failure_message": self.failure_message,
            "architecture": "single_prompt",
        }


class SinglePromptBaseline:
    def __init__(self, *, client: LLMClient | None = None, prompt_id: str = BASELINE_PROMPT_ID) -> None:
        settings = load_settings()
        self.prompt_id = prompt_id
        if client is not None:
            self.client = client
        elif settings.credentials_present:
            self.client = GeminiClient(settings=settings)
        else:
            self.client = None

    def run(
        self,
        response: LearnerResponse,
        challenge: Challenge | None,
    ) -> BaselineResult:
        if self.client is None or not getattr(self.client, "available", lambda: False)():
            return BaselineResult(
                next_action=None,
                mastery=None,
                message=None,
                reason=None,
                raw_text=None,
                parsed=None,
                prompt_id=self.prompt_id,
                prompt_version=prompt_version(self.prompt_id),
                model=None,
                valid=False,
                failure_code="LLM_UNAVAILABLE",
                failure_message="Baseline Gemini client is unavailable.",
            )
        metadata = response.metadata or {}
        prompt = render_prompt(
            self.prompt_id,
            learner=learner_payload(
                answer=response.answer,
                confidence=response.learner_confidence.value,
                approach=metadata.get("approach"),
                explanation=metadata.get("explanation"),
                reasoning=response.reasoning,
            ),
            challenge=challenge_payload(challenge),
        )
        try:
            generation = self.client.generate(prompt, prompt_id=self.prompt_id)
        except LLMError as exc:
            return BaselineResult(
                next_action=None,
                mastery=None,
                message=None,
                reason=None,
                raw_text=None,
                parsed=None,
                prompt_id=self.prompt_id,
                prompt_version=prompt_version(self.prompt_id),
                model=None,
                valid=False,
                failure_code=getattr(exc, "code", "LLM_UNAVAILABLE"),
                failure_message=str(exc),
            )
        try:
            parsed = extract_json_object(generation.text)
        except LLMValidationFailure as exc:
            return BaselineResult(
                next_action=None,
                mastery=None,
                message=None,
                reason=None,
                raw_text=generation.text,
                parsed=None,
                prompt_id=self.prompt_id,
                prompt_version=prompt_version(self.prompt_id),
                model=generation.model,
                valid=False,
                failure_code=exc.code,
                failure_message=str(exc),
            )
        action = parsed.get("next_action") or parsed.get("action") or parsed.get("strategy")
        action_text = str(action).strip().upper() if action is not None else None
        valid = action_text in BASELINE_ACTIONS
        return BaselineResult(
            next_action=action_text if valid else action_text,
            mastery=None if parsed.get("mastery") is None else str(parsed.get("mastery")).strip().lower(),
            message=None if parsed.get("message") is None else str(parsed.get("message")),
            reason=None if parsed.get("reason") is None else str(parsed.get("reason")),
            raw_text=generation.text,
            parsed=parsed,
            prompt_id=self.prompt_id,
            prompt_version=prompt_version(self.prompt_id),
            model=generation.model,
            valid=valid,
            failure_code=None if valid else "LLM_VALIDATION_FAILURE",
            failure_message=None if valid else f"unsupported next_action={action!r}",
        )
