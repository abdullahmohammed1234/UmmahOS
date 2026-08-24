"""NVIDIA NIM client using the public OpenAI-compatible REST API.

No third-party SDK dependency. API keys are read from the environment only.
The key is never placed in URLs, logs, or exception messages.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any

from adapt.llm.client import LLMGeneration
from adapt.llm.config import (
    DEFAULT_NVIDIA_MAX_OUTPUT_TOKENS,
    DEFAULT_NVIDIA_MODEL,
    NvidiaSettings,
    load_nvidia_settings,
)
from adapt.llm.errors import (
    LLMAuthenticationError,
    LLMEmptyResponseError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMUnavailableError,
)

NVIDIA_CHAT_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODELS_ENDPOINT = "https://integrate.api.nvidia.com/v1/models"
PREFERRED_NVIDIA_MODELS = (
    "meta/llama-3.3-70b-instruct",
    "meta/llama-3.1-70b-instruct",
    "nvidia/llama-3.1-nemotron-70b-instruct",
    "meta/llama-3.1-405b-instruct",
)
_SECRET_RE = re.compile(r"nvapi-[A-Za-z0-9_-]+")


class NvidiaClient:
    provider = "nvidia"

    def __init__(
        self,
        *,
        settings: NvidiaSettings | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        loaded = settings or load_nvidia_settings()
        self.settings = loaded
        self.api_key = api_key if api_key is not None else loaded.api_key
        self.model = model or loaded.model or DEFAULT_NVIDIA_MODEL
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
            raise LLMAuthenticationError("NVIDIA_API_KEY is not configured")
        resolved_temp = self.settings.temperature if temperature is None else float(temperature)
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": resolved_temp,
            "max_tokens": int(max_output_tokens or DEFAULT_NVIDIA_MAX_OUTPUT_TOKENS),
            "stream": False,
        }
        body, status = self._post_with_retry(NVIDIA_CHAT_ENDPOINT, payload)
        if status >= 400:
            raise LLMUnavailableError(f"NVIDIA API returned HTTP {status}")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise LLMEmptyResponseError("NVIDIA returned a non-JSON envelope") from exc
        text = _extract_text(parsed)
        if not text.strip():
            raise LLMEmptyResponseError("NVIDIA returned an empty response")
        return LLMGeneration(
            text=text,
            model=self.model,
            provider=self.provider,
            prompt_id=prompt_id,
            temperature=resolved_temp,
        )

    def list_models(self) -> list[str]:
        if not self.api_key:
            raise LLMAuthenticationError("NVIDIA_API_KEY is not configured")
        request = urllib.request.Request(
            NVIDIA_MODELS_ENDPOINT,
            headers=self._headers(),
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise self._from_http(exc) from exc
        except TimeoutError as exc:
            raise LLMTimeoutError("NVIDIA models request timed out") from exc
        except urllib.error.URLError as exc:
            reason = _redact(str(getattr(exc, "reason", exc)), self.api_key)
            raise LLMUnavailableError(f"NVIDIA API unavailable: {reason}") from exc
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise LLMEmptyResponseError("NVIDIA models endpoint returned non-JSON") from exc
        data = parsed.get("data") if isinstance(parsed, dict) else None
        if not isinstance(data, list):
            return []
        names: list[str] = []
        for item in data:
            if isinstance(item, str) and item:
                names.append(item)
            elif isinstance(item, dict):
                ident = item.get("id") or item.get("model")
                if ident:
                    names.append(str(ident))
        return names

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

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
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return response.read().decode("utf-8"), int(getattr(response, "status", 200))
        except urllib.error.HTTPError:
            raise
        except TimeoutError as exc:
            raise LLMTimeoutError("NVIDIA request timed out") from exc
        except urllib.error.URLError as exc:
            reason = _redact(str(getattr(exc, "reason", exc)), self.api_key)
            lowered = reason.lower()
            if "timed out" in lowered or "timeout" in lowered:
                raise LLMTimeoutError("NVIDIA request timed out") from exc
            raise LLMUnavailableError(f"NVIDIA API unavailable: {reason}") from exc
        except OSError as exc:
            raise LLMUnavailableError(
                f"NVIDIA API unavailable: {_redact(str(exc), self.api_key)}"
            ) from exc

    def _from_http(self, exc: urllib.error.HTTPError) -> LLMErrorLike:
        status = int(exc.code or 0)
        detail = _redact(_http_detail(exc), self.api_key)
        if status in {401, 403}:
            return LLMAuthenticationError(detail or "NVIDIA authentication failed")
        if status == 429:
            return LLMRateLimitError(detail or "NVIDIA rate limit exceeded")
        if status >= 500:
            return LLMUnavailableError(detail or f"NVIDIA server error HTTP {status}")
        if status == 408:
            return LLMTimeoutError(detail or "NVIDIA request timed out")
        return LLMUnavailableError(detail or f"NVIDIA HTTP {status}")


LLMErrorLike = (
    LLMAuthenticationError
    | LLMRateLimitError
    | LLMTimeoutError
    | LLMUnavailableError
    | LLMEmptyResponseError
)


def select_available_model(available: list[str], *, preferred: str | None = None) -> str | None:
    """Pick a configured/preferred instruct model that the account actually exposes."""
    names = [item.strip() for item in available if item and item.strip()]
    if not names:
        return None
    if preferred and preferred in names:
        return preferred
    for candidate in PREFERRED_NVIDIA_MODELS:
        if candidate in names:
            return candidate
    lowered = [item.lower() for item in names]
    for needle in ("llama-3.3-70b-instruct", "llama-3.1-70b-instruct", "nemotron-70b", "instruct"):
        for name, low in zip(names, lowered):
            if needle in low:
                return name
    return names[0]


def _redact(text: str, secret: str | None) -> str:
    cleaned = _SECRET_RE.sub("[REDACTED]", text or "")
    if secret:
        cleaned = cleaned.replace(secret, "[REDACTED]")
    return cleaned


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
    if isinstance(error, str):
        return error[:300]
    return raw[:300]


def _extract_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    parts: list[str] = []
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        message = choice.get("message") or {}
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str) and content:
            parts.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, str) and item:
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if text:
                        parts.append(str(text))
        text = choice.get("text")
        if isinstance(text, str) and text:
            parts.append(text)
    return "\n".join(parts)
