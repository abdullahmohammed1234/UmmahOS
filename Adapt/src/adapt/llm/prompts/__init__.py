"""Prompt loading and rendering. Learner text is interpolated as data, not as system instructions."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from adapt.llm.schemas import SCHEMA_PROMPT_BLOCK

PROMPT_DIR = Path(__file__).resolve().parent

PROMPT_IDS = ("evidence_v1", "evidence_v2", "evidence_v3", "baseline_v1")
EVIDENCE_PROMPT_IDS = ("evidence_v1", "evidence_v2", "evidence_v3")

PROMPT_EXPERIMENT = {
    "evidence_v1": "P-001",
    "evidence_v2": "P-002",
    "evidence_v3": "P-003",
    "baseline_v1": "BASELINE",
}


class UnknownPromptError(ValueError):
    pass


@lru_cache(maxsize=16)
def load_prompt(prompt_id: str) -> str:
    name = prompt_id if prompt_id.endswith(".txt") else f"{prompt_id}.txt"
    path = PROMPT_DIR / name
    if not path.is_file():
        raise UnknownPromptError(f"unknown prompt: {prompt_id}")
    return path.read_text(encoding="utf-8")


def prompt_version(prompt_id: str) -> str:
    return Path(prompt_id).stem


def render_prompt(
    prompt_id: str,
    *,
    learner: dict[str, Any],
    challenge: dict[str, Any] | None = None,
) -> str:
    template = load_prompt(prompt_id)
    learner_block = (
        "<<<LEARNER_INPUT_START>>>\n"
        f"{json.dumps(learner, ensure_ascii=True, indent=2)}\n"
        "<<<LEARNER_INPUT_END>>>"
    )
    challenge_block = (
        "Challenge (trusted system context):\n"
        f"{json.dumps(challenge or {}, ensure_ascii=True, indent=2)}"
    )
    return (
        template.replace("{{LEARNER_BLOCK}}", learner_block)
        .replace("{{CHALLENGE_BLOCK}}", challenge_block)
        .replace("{{SCHEMA_BLOCK}}", SCHEMA_PROMPT_BLOCK)
    )


def learner_payload(
    *,
    answer: str,
    confidence: str | None,
    approach: str | None,
    explanation: str | None,
    reasoning: str | None = None,
) -> dict[str, Any]:
    return {
        "answer": answer,
        "confidence": confidence,
        "approach": approach,
        "explanation": explanation,
        "reasoning": reasoning,
    }


def challenge_payload(challenge: Any) -> dict[str, Any]:
    if challenge is None:
        return {}
    if isinstance(challenge, dict):
        return {
            "challenge_id": challenge.get("challenge_id") or challenge.get("id"),
            "question": challenge.get("question") or challenge.get("prompt"),
            "expected_answer": challenge.get("expected_answer"),
            "concept_id": challenge.get("concept_id"),
        }
    return {
        "challenge_id": getattr(challenge, "challenge_id", None),
        "question": getattr(challenge, "question", None),
        "expected_answer": getattr(challenge, "expected_answer", None),
        "concept_id": getattr(challenge, "concept_id", None),
    }
