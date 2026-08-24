"""Gemini / mock client failure modes."""

from __future__ import annotations

import pytest

from adapt.llm.errors import (
    LLMAuthenticationError,
    LLMEmptyResponseError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from adapt.llm.gemini import GeminiClient
from adapt.llm.testing import MockLLMClient, TimeoutLLMClient, UnavailableLLMClient


def test_mock_returns_text():
    client = MockLLMClient(text='{"ok": true}')
    result = client.generate("hello")
    assert result.text == '{"ok": true}'
    assert client.prompts == ["hello"]


def test_timeout_client():
    client = TimeoutLLMClient()
    with pytest.raises(LLMTimeoutError):
        client.generate("x")


def test_unavailable_client():
    client = UnavailableLLMClient()
    with pytest.raises(LLMUnavailableError):
        client.generate("x")


def test_gemini_without_key_is_unavailable():
    client = GeminiClient(api_key="", model="gemini-2.0-flash")
    assert client.available() is False
    with pytest.raises(LLMAuthenticationError):
        client.generate("hello")


def test_mock_error_is_raised():
    client = MockLLMClient(error=LLMRateLimitError("slow down"))
    with pytest.raises(LLMRateLimitError):
        client.generate("x")


def test_empty_generation_type_exists():
    assert LLMEmptyResponseError.code == "LLM_EMPTY_RESPONSE"
