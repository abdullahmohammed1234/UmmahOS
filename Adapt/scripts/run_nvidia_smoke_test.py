"""Run a tiny live NVIDIA smoke test when credentials exist.

python scripts/run_nvidia_smoke_test.py

Does not write historical benchmark artifacts.
Does not call Gemini.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adapt.llm.analyzer import LLMEvidenceAnalyzer
from adapt.llm.config import load_nvidia_settings
from adapt.llm.errors import LLMError
from adapt.llm.fallback import SOURCE_FALLBACK, SOURCE_NVIDIA
from adapt.llm.nvidia import NvidiaClient, select_available_model
from adapt.models.challenge import Challenge
from adapt.models.enums import ChallengeType, Difficulty, LearnerConfidence
from adapt.models.learner_response import LearnerResponse
from adapt.tutor.tutor import AdaptiveTutor


def main() -> int:
    settings = load_nvidia_settings()
    key_present = settings.credentials_present
    print(f"NVIDIA key detected: {'YES' if key_present else 'NO'}")
    if not key_present:
        print("NVIDIA_API_KEY is not configured. Skipping live NVIDIA smoke test.")
        return 2

    catalog_client = NvidiaClient(settings=settings)
    selected = settings.model
    catalog_ok = False
    try:
        available = catalog_client.list_models()
        catalog_ok = True
        print(f"NVIDIA model catalog: {len(available)} model(s) visible")
        chosen = select_available_model(available, preferred=settings.model)
        if chosen:
            selected = chosen
        elif settings.model not in available:
            print("Configured model was not in the catalog; will still probe it directly.")
    except LLMError as exc:
        print(f"NVIDIA model catalog unavailable ({exc.code}); probing configured model directly.")

    print(f"provider: NVIDIA")
    print(f"model: {selected}")
    print(f"prompt: {settings.prompt_id}")
    client = NvidiaClient(settings=settings, model=selected, max_retries=1)
    try:
        ping = client.generate("Reply with the single word pong.")
        ping_ok = bool(ping.text.strip())
    except LLMError as exc:
        print(f"live request succeeded: NO")
        print(f"model ping failed: {exc.code}")
        print("SMOKE TEST FAIL")
        return 1
    print(f"live request succeeded: {'YES' if ping_ok else 'NO'}")
    if not ping_ok:
        print("SMOKE TEST FAIL")
        return 1
    print(f"model catalog used: {'YES' if catalog_ok else 'NO'}")

    challenge = Challenge(
        challenge_id="P12-NVIDIA-SMOKE",
        concept_id="basic_algebra",
        difficulty=Difficulty.EASY,
        question="Solve for x: 7x = 56",
        challenge_type=ChallengeType.STANDARD,
        expected_answer="8",
        expected_reasoning_cues=("divide", "both sides"),
        correct_method_cues=("divide",),
    )
    analyzer = LLMEvidenceAnalyzer(client=client, prompt_id=settings.prompt_id)
    tutor = AdaptiveTutor(bank=(challenge,), analyzer=analyzer, seed=20260819)
    tutor.start_session(
        learner_id="nvidia-smoke",
        concept_id="basic_algebra",
        session_id="P12-NVIDIA-SMOKE",
        initial_challenge=challenge,
    )
    step = tutor.submit_response(
        "P12-NVIDIA-SMOKE",
        LearnerResponse(
            response_id="nvidia-smoke-r1",
            learner_id="nvidia-smoke",
            concept_id="basic_algebra",
            challenge_id=challenge.challenge_id,
            answer="8",
            reasoning="I guessed. I think I remembered it.",
            learner_confidence=LearnerConfidence.LOW,
            metadata={
                "approach": "I guessed",
                "explanation": "I think I remembered it.",
            },
        ),
    )
    result = analyzer.last_result
    source = None if result is None else result.source
    valid = bool(result and result.validation_ok)
    fallback = source == SOURCE_FALLBACK
    print(f"schema valid: {'YES' if valid else 'NO'}")
    print(f"source: {source}")
    print(f"fallback used: {'YES' if fallback else 'NO'}")
    if result is not None and result.llm_evidence is not None:
        print("evidence extracted:")
        print(json.dumps(result.llm_evidence.to_dict(), indent=2))
    elif result is not None:
        print(f"extraction failed: {result.failure_code}")
        if result.failure_message:
            print(result.failure_message)
    print(f"AdaptiveTutor decision: {step.decision.value}")
    print(f"mastery estimate: {step.state_after.mastery_estimate}")
    print(f"reason: {step.reason}")
    if source == SOURCE_NVIDIA and valid and step.decision.value != "INCREASE":
        print("SMOKE TEST PASS")
        return 0
    if source == SOURCE_NVIDIA and valid:
        print("SMOKE TEST PASS (NVIDIA evidence accepted; AdaptiveTutor still owns the decision)")
        return 0
    print("SMOKE TEST FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
