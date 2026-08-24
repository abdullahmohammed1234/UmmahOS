"""LLM-boundary errors. Invalid model output must not enter AdaptiveTutor."""

from __future__ import annotations

from adapt.errors import AdaptError


class LLMError(AdaptError):
    """Base error for the Gemini evidence-extraction boundary."""

    code = "LLM_ERROR"


class LLMUnavailableError(LLMError):
    code = "LLM_UNAVAILABLE"


class LLMTimeoutError(LLMError):
    code = "LLM_TIMEOUT"


class LLMRateLimitError(LLMError):
    code = "LLM_RATE_LIMIT"


class LLMAuthenticationError(LLMError):
    code = "LLM_AUTHENTICATION_FAILURE"


class LLMEmptyResponseError(LLMError):
    code = "LLM_EMPTY_RESPONSE"


class LLMValidationFailure(LLMError):
    """Malformed or contract-violating LLM output. Never fed to ADAPT as evidence."""

    code = "LLM_VALIDATION_FAILURE"
