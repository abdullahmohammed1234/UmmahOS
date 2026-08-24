"""Provider-agnostic LLM client boundary.

The rest of ADAPT talks to LLMClient, not to Gemini specifically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class LLMGeneration:
    text: str
    model: str
    provider: str
    prompt_id: str | None = None
    temperature: float | None = None
    raw: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMClient(Protocol):
    """Minimal generation interface. Implementations must not decide tutoring strategy."""

    provider: str

    def available(self) -> bool:
        ...

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        prompt_id: str | None = None,
    ) -> LLMGeneration:
        ...
