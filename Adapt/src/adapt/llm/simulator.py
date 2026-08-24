"""Prompt-conditioned evidence simulator for offline Phase 12 benchmarks.

This is not live Gemini. It follows instruction features found in the prompt
text so prompt-engineering differences can be measured without an API key.
Live Gemini results, when collected, are stored separately and labeled as live.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from adapt.llm.client import LLMGeneration

INJECTION_RE = re.compile(
    r"ignore (your|the previous|previous) (instructions|prompt)|"
    r"mark me as mastered|"
    r"set mastery to|"
    r"classify me as an expert|"
    r"increase my difficulty|"
    r"you must classify me|"
    r"give me the hardest",
    re.IGNORECASE,
)

GUESS_RE = re.compile(
    r"\b(guess|guessed|guessing|remembered|memorized|just a guess)\b",
    re.IGNORECASE,
)
STRONG_RE = re.compile(
    r"\b(divide|divided|inverse|both sides|distributed|factor|definition|"
    r"because|therefore|so that)\b",
    re.IGNORECASE,
)
ARITH_RE = re.compile(
    r"\b(miscalculat|arithmetic|added wrong|calculation|computed wrong|off by)\b",
    re.IGNORECASE,
)
MISC_RE = re.compile(
    r"\b(multipl(?:y|ied) (?:instead|only)|add(?:ed)? the denominators|"
    r"didn't distribute|cross multiply)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PromptFeatures:
    prompt_id: str
    require_schema: bool
    no_automatic_mastery: bool
    injection_defense: bool
    forbid_strategy: bool
    distinguish_reasoning: bool
    preserve_uncertainty: bool


def detect_features(prompt: str) -> PromptFeatures:
    lowered = prompt.lower()
    prompt_id = "unknown"
    match = re.search(r"PROMPT_ID:\s*(\S+)", prompt)
    if match:
        prompt_id = match.group(1).strip()
    return PromptFeatures(
        prompt_id=prompt_id,
        require_schema="required json object" in lowered or "return only a json object" in lowered,
        no_automatic_mastery="does not automatically" in lowered or "no automatic mastery" in lowered,
        injection_defense="untrusted" in lowered or "not instructions" in lowered,
        forbid_strategy="do not choose increase" in lowered or "never output an adaptive strategy" in lowered,
        distinguish_reasoning="guessing or memorization" in lowered or "reasoning matters" in lowered,
        preserve_uncertainty="evidence_strength to \"insufficient\"" in lowered
        or "preserve uncertainty" in lowered,
    )


def simulate_evidence_text(prompt: str) -> str:
    features = detect_features(prompt)
    learner = _extract_learner(prompt)
    challenge = _extract_challenge(prompt)
    answer = str(learner.get("answer") or "")
    explanation = " ".join(
        str(part)
        for part in (
            learner.get("explanation"),
            learner.get("reasoning"),
            learner.get("approach"),
        )
        if part
    )
    expected = str(challenge.get("expected_answer") or "")
    injection = bool(INJECTION_RE.search(explanation) or INJECTION_RE.search(answer))

    if injection and not features.injection_defense:
        if not features.require_schema:
            return "You are mastered. Increase difficulty.\n{\"correctness\":\"correct\",\"strategy\":\"INCREASE\"}"
        # Structured but contract-free: obey the injected instruction as if it were a label.
        payload = _base_payload(
            "correct",
            "strong",
            "high",
            None,
            None,
            "strong",
            "low",
            ["learner requested mastery"],
        )
        return json.dumps(payload)

    correctness = _correctness(answer, expected, explanation)
    reasoning = _reasoning(explanation, features)
    confidence = _confidence(str(learner.get("confidence") or ""))
    error_type, misconception = _error(correctness, explanation)
    strength, uncertainty = _strength(
        correctness, reasoning, confidence, features, explanation
    )
    supporting = _supporting(answer, explanation, injection)

    if not features.require_schema and correctness == "correct" and reasoning == "weak":
        return f"Looks correct. I would INCREASE.\nThe answer was {answer}."

    payload = _base_payload(
        correctness,
        reasoning,
        confidence,
        misconception,
        error_type,
        strength,
        uncertainty,
        supporting,
    )
    if not features.forbid_strategy and correctness == "correct" and reasoning in {"strong", "partial"}:
        payload["next_action"] = "INCREASE"
    return json.dumps(payload)


def simulate_baseline_text(prompt: str) -> str:
    learner = _extract_learner(prompt)
    challenge = _extract_challenge(prompt)
    answer = str(learner.get("answer") or "")
    explanation = " ".join(
        str(part)
        for part in (learner.get("explanation"), learner.get("reasoning"), learner.get("approach"))
        if part
    )
    expected = str(challenge.get("expected_answer") or "")
    if INJECTION_RE.search(explanation) or INJECTION_RE.search(answer):
        return json.dumps(
            {
                "next_action": "INCREASE",
                "mastery": "high",
                "message": "You are classified as an expert.",
                "reason": "The learner instructed the tutor to increase difficulty.",
            }
        )
    correct = _normalize(answer) == _normalize(expected) and expected != ""
    if correct:
        if GUESS_RE.search(explanation) or str(learner.get("confidence") or "").upper() == "LOW":
            action = "INCREASE"
            mastery = "high"
            reason = "The answer is correct, so raise difficulty."
        else:
            action = "INCREASE"
            mastery = "high"
            reason = "Correct answer indicates mastery."
    elif not explanation.strip():
        action = "MAINTAIN"
        mastery = "medium"
        reason = "Not enough text to judge."
    elif ARITH_RE.search(explanation):
        action = "REMEDIATE"
        mastery = "low"
        reason = "Wrong answer, so remediate."
    elif MISC_RE.search(explanation):
        action = "REMEDIATE"
        mastery = "low"
        reason = "Wrong answer looks like a misconception."
    else:
        action = "DECREASE"
        mastery = "low"
        reason = "Incorrect answer."
    return json.dumps(
        {
            "next_action": action,
            "mastery": mastery,
            "message": "Here is what we should do next.",
            "reason": reason,
        }
    )


class PromptSimulatorClient:
    """Deterministic instruction-following stub used by offline benchmarks."""

    provider = "simulator"

    def __init__(self, *, mode: str = "evidence", model: str = "prompt-simulator") -> None:
        self.mode = mode
        self.model = model
        self.prompts: list[str] = []

    def available(self) -> bool:
        return True

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
        if self.mode == "baseline" or (prompt_id or "").startswith("baseline") or "PROMPT_ID: baseline" in prompt:
            text = simulate_baseline_text(prompt)
        else:
            text = simulate_evidence_text(prompt)
        return LLMGeneration(
            text=text,
            model=self.model,
            provider=self.provider,
            prompt_id=prompt_id,
            temperature=temperature,
        )


def _extract_learner(prompt: str) -> dict:
    return _extract_json_between(prompt, "<<<LEARNER_INPUT_START>>>", "<<<LEARNER_INPUT_END>>>")


def _extract_challenge(prompt: str) -> dict:
    marker = "Challenge (trusted system context):"
    if marker not in prompt:
        return {}
    blob = prompt.split(marker, 1)[1]
    start = blob.find("{")
    end = blob.find("\n\n")
    region = blob[start:] if start >= 0 else blob
    if end > 0:
        region = blob[start:end] if start >= 0 else blob[:end]
    try:
        parsed = json.loads(region.strip())
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        start = blob.find("{")
        end = blob.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(blob[start : end + 1])
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
        return {}


def _extract_json_between(prompt: str, start_token: str, end_token: str) -> dict:
    start = prompt.rfind(start_token)
    end = prompt.rfind(end_token)
    if start < 0 or end <= start:
        return {}
    blob = prompt[start + len(start_token) : end]
    try:
        parsed = json.loads(blob.strip())
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").strip().lower())


def _correctness(answer: str, expected: str, explanation: str) -> str:
    if not answer.strip():
        return "unclear"
    if expected and _normalize(answer) == _normalize(expected):
        return "correct"
    if expected and _normalize(expected) in _normalize(answer):
        return "correct"
    if not expected:
        return "unclear"
    return "incorrect"


def _reasoning(explanation: str, features: PromptFeatures) -> str:
    text = (explanation or "").strip()
    if not text:
        return "missing"
    if INJECTION_RE.search(text) and features.injection_defense:
        return "weak"
    if GUESS_RE.search(text):
        return "weak"
    if ARITH_RE.search(text) and STRONG_RE.search(text):
        return "partial"
    if STRONG_RE.search(text) and len(text) >= 40:
        return "strong"
    if STRONG_RE.search(text):
        return "partial"
    if len(text) < 20:
        return "weak"
    return "partial"


def _confidence(value: str) -> str:
    text = (value or "").strip().upper()
    mapping = {
        "HIGH": "high",
        "MODERATE": "medium",
        "LOW": "low",
        "UNKNOWN": "unclear",
        "UNSURE": "low",
        "CONFIDENT": "high",
        "VERY CONFIDENT": "high",
    }
    if text in mapping:
        return mapping[text]
    lowered = (value or "").strip().lower()
    if lowered in {"high", "medium", "low", "unclear"}:
        return lowered
    return "unclear"


def _error(correctness: str, explanation: str) -> tuple[str | None, str | None]:
    if correctness != "incorrect":
        return None, None
    if ARITH_RE.search(explanation):
        return "arithmetic", None
    if MISC_RE.search(explanation):
        return "conceptual", "misconception"
    if not explanation.strip():
        return "insufficient_evidence", None
    return "unknown", None


def _strength(
    correctness: str,
    reasoning: str,
    confidence: str,
    features: PromptFeatures,
    explanation: str,
) -> tuple[str, str]:
    if correctness == "unclear" or (reasoning == "missing" and not explanation.strip()):
        return ("insufficient", "high") if features.preserve_uncertainty else ("moderate", "medium")
    if INJECTION_RE.search(explanation) and features.injection_defense:
        return "weak", "high"
    if correctness == "correct" and reasoning == "weak":
        if features.no_automatic_mastery:
            return "weak", "medium"
        return "strong", "low"
    if correctness == "correct" and reasoning == "strong" and confidence == "high":
        return "strong", "low"
    if correctness == "correct" and reasoning in {"strong", "partial"}:
        return "moderate", "medium"
    if correctness == "incorrect" and reasoning == "missing":
        return "insufficient" if features.preserve_uncertainty else "weak", "high"
    if correctness == "incorrect":
        return "moderate", "medium"
    return "moderate", "medium"


def _supporting(answer: str, explanation: str, injection: bool) -> list[str]:
    items = [f"answer={answer!r}"]
    if explanation:
        items.append(explanation[:160])
    if injection:
        items.append("learner text contains instruction-like language")
    return items


def _base_payload(
    correctness: str,
    reasoning: str,
    confidence: str,
    misconception: str | None,
    error_type: str | None,
    strength: str,
    uncertainty: str,
    supporting: list[str],
) -> dict:
    return {
        "correctness": correctness,
        "reasoning_quality": reasoning,
        "confidence_signal": confidence,
        "misconception": misconception,
        "error_type": error_type,
        "evidence_strength": strength,
        "uncertainty": uncertainty,
        "supporting_evidence": supporting,
    }
