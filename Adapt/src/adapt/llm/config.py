"""Environment-based Gemini configuration. No secrets in code."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

WORKFLOW_VERSION = "phase12-v1"
DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_OUTPUT_TOKENS = 8192
DEFAULT_TIMEOUT_SECONDS = 45.0
DEFAULT_PROMPT_ID = "evidence_v3"

ENV_API_KEY = "GEMINI_API_KEY"
ENV_MODEL = "GEMINI_MODEL"
ENV_TEMPERATURE = "GEMINI_TEMPERATURE"
ENV_TIMEOUT = "GEMINI_TIMEOUT_SECONDS"
ENV_PROMPT = "ADAPT_GEMINI_PROMPT"
ENV_USE_GEMINI = "ADAPT_USE_GEMINI"

DEFAULT_NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"
DEFAULT_NVIDIA_MAX_OUTPUT_TOKENS = 1024
ENV_NVIDIA_API_KEY = "NVIDIA_API_KEY"
ENV_NVIDIA_MODEL = "NVIDIA_MODEL"
ENV_NVIDIA_TEMPERATURE = "NVIDIA_TEMPERATURE"
ENV_NVIDIA_TIMEOUT = "NVIDIA_TIMEOUT_SECONDS"

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_dotenv(*, override: bool = False) -> Path | None:
    """Load `.env` from the working directory or project root.

    Existing process environment variables win unless override=True.
    The file is never logged.
    """
    seen: set[Path] = set()
    loaded: Path | None = None
    for candidate in (Path.cwd() / ".env", PROJECT_ROOT / ".env"):
        path = candidate.resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        _apply_dotenv(path, override=override)
        loaded = loaded or path
    return loaded


def _apply_dotenv(path: Path, *, override: bool) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        if not override and key in os.environ:
            continue
        os.environ[key] = _strip_quotes(value.strip())


@dataclass(frozen=True)
class GeminiSettings:
    api_key: str | None
    model: str
    temperature: float
    timeout_seconds: float
    prompt_id: str
    use_gemini: bool

    @property
    def credentials_present(self) -> bool:
        return bool(self.api_key)

    @property
    def enabled(self) -> bool:
        return self.use_gemini and self.credentials_present


def load_settings() -> GeminiSettings:
    load_dotenv()
    raw_temp = _env(ENV_TEMPERATURE)
    raw_timeout = _env(ENV_TIMEOUT)
    raw_use = (_env(ENV_USE_GEMINI) or "").lower()
    explicit_off = raw_use in {"0", "false", "no", "off"}
    explicit_on = raw_use in {"1", "true", "yes", "on"}
    api_key = _env(ENV_API_KEY)
    use_gemini = False if explicit_off else (explicit_on or bool(api_key))
    try:
        temperature = float(raw_temp) if raw_temp is not None else DEFAULT_TEMPERATURE
    except ValueError:
        temperature = DEFAULT_TEMPERATURE
    try:
        timeout = float(raw_timeout) if raw_timeout is not None else DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        timeout = DEFAULT_TIMEOUT_SECONDS
    return GeminiSettings(
        api_key=api_key,
        model=_env(ENV_MODEL) or DEFAULT_MODEL,
        temperature=temperature,
        timeout_seconds=timeout,
        prompt_id=_env(ENV_PROMPT) or DEFAULT_PROMPT_ID,
        use_gemini=use_gemini,
    )


@dataclass(frozen=True)
class NvidiaSettings:
    api_key: str | None
    model: str
    temperature: float
    timeout_seconds: float
    prompt_id: str

    @property
    def credentials_present(self) -> bool:
        return bool(self.api_key)


def load_nvidia_settings() -> NvidiaSettings:
    load_dotenv()
    raw_temp = _env(ENV_NVIDIA_TEMPERATURE)
    raw_timeout = _env(ENV_NVIDIA_TIMEOUT)
    try:
        temperature = float(raw_temp) if raw_temp is not None else DEFAULT_TEMPERATURE
    except ValueError:
        temperature = DEFAULT_TEMPERATURE
    try:
        timeout = float(raw_timeout) if raw_timeout is not None else DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        timeout = DEFAULT_TIMEOUT_SECONDS
    return NvidiaSettings(
        api_key=_env(ENV_NVIDIA_API_KEY),
        model=_env(ENV_NVIDIA_MODEL) or DEFAULT_NVIDIA_MODEL,
        temperature=temperature,
        timeout_seconds=timeout,
        prompt_id=_env(ENV_PROMPT) or DEFAULT_PROMPT_ID,
    )
