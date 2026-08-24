"""Test/benchmark LLM clients. Never used as a stand-in for live Gemini in reports."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from adapt.llm.client import LLMGeneration
from adapt.llm.errors import LLMError, LLMTimeoutError, LLMUnavailableError


class MockLLMClient:
    """Returns scripted generations. Used by automated tests."""

    provider = "mock"

    def __init__(
        self,
        text: str | Sequence[str] | Callable[[str], str] | None = None,
        *,
        error: LLMError | None = None,
        model: str = "mock-gemini",
        available: bool = True,
    ) -> None:
        self._text = text if text is not None else "{}"
        self._error = error
        self.model = model
        self._available = available
        self.prompts: list[str] = []

    def available(self) -> bool:
        return self._available

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        prompt_id: str | None = None,
    ) -> LLMGeneration:
        self.prompts.append(prompt)
        _ = (temperature, max_output_tokens)
        if self._error is not None:
            raise self._error
        if callable(self._text):
            body = self._text(prompt)
        elif isinstance(self._text, str):
            body = self._text
        else:
            index = min(len(self.prompts) - 1, len(self._text) - 1)
            body = self._text[index]
        return LLMGeneration(
            text=body,
            model=self.model,
            provider=self.provider,
            prompt_id=prompt_id,
            temperature=temperature,
        )


class UnavailableLLMClient:
    provider = "mock"

    def available(self) -> bool:
        return False

    def generate(self, prompt: str, **kwargs) -> LLMGeneration:
        _ = (prompt, kwargs)
        raise LLMUnavailableError("mock client unavailable")


class TimeoutLLMClient:
    provider = "mock"

    def available(self) -> bool:
        return True

    def generate(self, prompt: str, **kwargs) -> LLMGeneration:
        _ = (prompt, kwargs)
        raise LLMTimeoutError("mock timeout")
