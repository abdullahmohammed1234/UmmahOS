"""Run a tiny live Gemini smoke test when credentials exist.

python scripts/run_gemini_smoke_test.py

Does not write historical benchmark artifacts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adapt.llm.config import load_settings
from adapt.llm.gemini import GeminiClient
from adapt.llm.prompts import render_prompt
from adapt.llm.validator import parse_and_validate


def main() -> int:
    settings = load_settings()
    if not settings.credentials_present:
        print("GEMINI_API_KEY is not configured. Skipping live smoke test.")
        print("Set GEMINI_API_KEY (and optionally GEMINI_MODEL) in the environment.")
        return 0
    client = GeminiClient(settings=settings)
    prompt = render_prompt(
        settings.prompt_id,
        learner={
            "answer": "8",
            "confidence": "LOW",
            "approach": "I guessed",
            "explanation": "I think I remembered it.",
            "reasoning": "I guessed. I think I remembered it.",
        },
        challenge={
            "challenge_id": "P12-SMOKE",
            "question": "Solve for x: 7x = 56",
            "expected_answer": "8",
            "concept_id": "basic_algebra",
        },
    )
    print(f"Calling Gemini model={settings.model} prompt={settings.prompt_id}")
    generation = client.generate(prompt, prompt_id=settings.prompt_id)
    print("Raw text:")
    print(generation.text)
    evidence = parse_and_validate(generation.text)
    print("Validated evidence:")
    print(json.dumps(evidence.to_dict(), indent=2))
    print("SMOKE TEST PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
