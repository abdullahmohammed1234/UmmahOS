"""Google Gemini client using the public REST API.

No third-party SDK dependency. API keys are read from the environment only.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlencode

from adapt.llm.client import LLMGeneration
from adapt.llm.config import (
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MODEL,
    GeminiSettings,
    load_settings,
)
from adapt.llm.errors import (
    LLMAuthenticationError,
    LLMEmptyResponseError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUnavailableError,
)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiClient:
    provider = "gemini"

    def __init__(
        self,
        *,
        settings: GeminiSettings | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        loaded = settings or load_settings()
        self.settings = loaded
        self.api_key = api_key if api_key is not None else loaded.api_key
        self.model = model or loaded.model or DEFAULT_MODEL
        self.timeout_seconds = (
            loaded.timeout_seconds if timeout_seconds is None else float(timeout_seconds)
        )
        self.max_retries = 3 if max_retries is None else max(1, int(max_retries))

    def available(self) -> bool:
        return bool(self.api_key)

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        prompt_id: str | None = None,
    ) -> LLMGeneration:
        if not self.api_key:
            raise LLMAuthenticationError("GEMINI_API_KEY is not configured")
        resolved_temp = self.settings.temperature if temperature is None else float(temperature)
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": resolved_temp,
                "maxOutputTokens": int(max_output_tokens or DEFAULT_MAX_OUTPUT_TOKENS),
                "responseMimeType": "application/json",
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        url = GEMINI_ENDPOINT.format(model=self.model) + "?" + urlencode({"key": self.api_key})
        body, status = self._post_with_retry(url, payload)
        if status >= 400:
            raise LLMUnavailableError(f"Gemini API returned HTTP {status}")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise LLMEmptyResponseError("Gemini returned a non-JSON envelope") from exc
        text = _extract_text(parsed)
        if not text.strip():
            raise LLMEmptyResponseError("Gemini returned an empty response")
        return LLMGeneration(
            text=text,
            model=self.model,
            provider=self.provider,
            prompt_id=prompt_id,
            temperature=resolved_temp,
            raw=parsed,
        )

    def _post_with_retry(self, url: str, payload: dict[str, Any]) -> tuple[str, int]:
        last_error: urllib.error.HTTPError | None = None
        for attempt in range(self.max_retries):
            try:
                return self._post(url, payload)
            except LLMTimeoutError:
                if attempt < self.max_retries - 1:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                raise
            except urllib.error.HTTPError as exc:
                last_error = exc
                status = int(exc.code or 0)
                if status == 400 and "thinkingConfig" in payload.get("generationConfig", {}):
                    payload["generationConfig"].pop("thinkingConfig", None)
                    try:
                        return self._post(url, payload)
                    except urllib.error.HTTPError as retry_exc:
                        last_error = retry_exc
                        status = int(retry_exc.code or 0)
                        exc = retry_exc
                if status in {429, 503} and attempt < self.max_retries - 1:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                raise self._from_http(exc) from exc
        assert last_error is not None
        raise self._from_http(last_error) from last_error

    def _post(self, url: str, payload: dict[str, Any]) -> tuple[str, int]:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return response.read().decode("utf-8"), int(getattr(response, "status", 200))
        except urllib.error.HTTPError:
            raise
        except TimeoutError as exc:
            raise LLMTimeoutError("Gemini request timed out") from exc
        except urllib.error.URLError as exc:
            reason = str(getattr(exc, "reason", exc))
            lowered = reason.lower()
            if "timed out" in lowered or "timeout" in lowered:
                raise LLMTimeoutError("Gemini request timed out") from exc
            raise LLMUnavailableError(f"Gemini API unavailable: {reason}") from exc
        except OSError as exc:
            raise LLMUnavailableError(f"Gemini API unavailable: {exc}") from exc

    def _from_http(self, exc: urllib.error.HTTPError) -> LLMErrorLike:
        status = int(exc.code or 0)
        detail = _http_detail(exc)
        if status in {401, 403}:
            return LLMAuthenticationError(detail or "Gemini authentication failed")
        if status == 429:
            return LLMRateLimitError(detail or "Gemini rate limit exceeded")
        if status >= 500:
            return LLMUnavailableError(detail or f"Gemini server error HTTP {status}")
        if status == 408:
            return LLMTimeoutError(detail or "Gemini request timed out")
        return LLMUnavailableError(detail or f"Gemini HTTP {status}")


LLMErrorLike = (
    LLMAuthenticationError
    | LLMRateLimitError
    | LLMTimeoutError
    | LLMUnavailableError
    | LLMEmptyResponseError
)


def _http_detail(exc: urllib.error.HTTPError) -> str:
    try:
        raw = exc.read().decode("utf-8")
    except Exception:
        return str(exc)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw[:300] or str(exc)
    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        return str(error.get("message") or raw[:300])
    return raw[:300]


def _extract_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates") or []
    parts: list[str] = []
    for candidate in candidates:
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if text:
                parts.append(str(text))
    return "\n".join(parts)
