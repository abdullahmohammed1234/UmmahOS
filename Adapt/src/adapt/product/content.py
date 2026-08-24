"""Judge-facing product copy. Historical numbers are transcribed, not recomputed."""

from __future__ import annotations

from typing import Any

from adapt.product.labels import CTA_PRIMARY, CTA_SECONDARY, HERO, PROMISE, PROMISE_SHORT, SUPPORTING, TAGLINE

ARCHITECTURE = (
    {
        "id": "learner",
        "name": "Learner",
        "summary": "A person answering a challenge with an answer, confidence, and optional reasoning.",
    },
    {
        "id": "response",
        "name": "Response",
        "summary": "The only inputs the tutor uses: answer, confidence, and reasoning.",
    },
    {
        "id": "analyzer",
        "name": "Evidence Analyzer",
        "summary": "Extracts signals about understanding, confidence, reasoning, and misconceptions. When Gemini is enabled, this step is an LLM evidence workflow plus schema validation; otherwise it is the deterministic analyzer.",
    },
    {
        "id": "state",
        "name": "Learner State",
        "summary": "Maintains the system's current belief about the learner.",
    },
    {
        "id": "strategy",
        "name": "Strategy Engine",
        "summary": "Chooses how the tutor should respond.",
    },
    {
        "id": "selector",
        "name": "Challenge Selector",
        "summary": "Turns the instructional strategy into the next task.",
    },
    {
        "id": "challenge",
        "name": "Next Challenge",
        "summary": "The next problem the learner sees, selected from the frozen challenge bank.",
    },
)

CHAIN = ("Answer", "Evidence", "Learner State", "Strategy", "Next Challenge")

TECHNICAL_EVIDENCE = {
    "disclaimer": (
        "These are engineering benchmarks of adaptive decision behavior. "
        "They are not proof that ADAPT improves human learning."
    ),
    "phases": [
        {
            "id": "1e",
            "title": "Phase 1E — Benchmark against baseline",
            "items": [
                "51/51 appropriateness",
                "9/9 counterfactual differentiation",
                "51/51 traceability",
            ],
        },
        {
            "id": "1f",
            "title": "Phase 1F — Generalization stress testing",
            "items": [
                "39/42 development",
                "17/18 holdout",
                "ROBUST",
                "generalization gap −1.6 pp",
            ],
        },
        {
            "id": "2",
            "title": "Phase 2 — Adaptive Strategy Layer",
            "items": ["60/60 strategy appropriateness"],
        },
        {
            "id": "3",
            "title": "Phase 3 — Integrated AdaptiveTutor",
            "items": [
                "44/44 end-to-end adaptation",
                "294/294 state-to-strategy causality",
                "294/294 strategy-to-challenge consistency",
            ],
        },
        {
            "id": "4",
            "title": "Phase 4 — Learner-facing product",
            "items": [
                "20/20 task completion",
                "119/119 engine preservation",
                "119/119 trace visibility",
            ],
        },
        {
            "id": "5",
            "title": "Phase 5 — Human learning evaluation",
            "items": [
                "Human learning evaluation: INCONCLUSIVE",
                "n = 0",
            ],
        },
        {
            "id": "12",
            "title": "Phase 12 — Gemini evidence workflow",
            "items": [
                "Gemini interprets learner evidence; ADAPT decides how to adapt",
                "Structured output is schema-validated before it can enter the engine",
                "Phase 5 remains INCONCLUSIVE (n = 0)",
            ],
        },
    ],
}

LIMITATIONS = [
    {
        "id": "g001b",
        "title": "Phase 1F: fraction subtraction boundary",
        "detail": (
            "G-001-B did not accumulate to INCREASE after three successes on a "
            "fraction-subtraction item. The supplied reasoning discussed adding "
            "numerators, so the evidence was not strong enough for INCREASE. "
            "This remains a documented generalization boundary, not a hidden failure."
        ),
    },
    {
        "id": "g003",
        "title": "Phase 1F: delayed misconception vs regression",
        "detail": (
            "On G-003-A/B, delayed misconception evidence historically triggered "
            "DECREASE (regression) instead of diagnostic probing. Phase 2 later "
            "separated that case in the strategy layer; the Phase 1F result is "
            "kept as historical evidence."
        ),
    },
    {
        "id": "phase5",
        "title": "Phase 5: human participants = 0",
        "detail": (
            "No consented learners were available. H1 is INCONCLUSIVE. "
            "This is not a positive learning result."
        ),
    },
    {
        "id": "usability",
        "title": "Phase 4: formative usability study incomplete",
        "detail": "The planned 5-learner usability protocol remains PENDING (0 / 5).",
    },
    {
        "id": "efficacy",
        "title": "No claim of educational efficacy",
        "detail": (
            "ADAPT has not been shown to improve learning. Engineering evidence "
            "shows that decisions change with learner evidence. That is not the "
            "same as a learning-gain result."
        ),
    },
    {
        "id": "heuristic",
        "title": "Heuristic evidence analysis, with optional Gemini interpretation",
        "detail": (
            "The frozen Evidence Analyzer is deterministic and cue-based. Phase 12 can wrap it "
            "with a Gemini evidence-extraction workflow. Gemini does not choose strategy or the "
            "next challenge. Offline benchmarks use a prompt-conditioned simulator unless a live "
            "Gemini key is explicitly requested."
        ),
    },
    {
        "id": "concepts",
        "title": "Curated, not complete, curriculum",
        "detail": (
            "Phase 7 adds multiple domains with a curated challenge catalog. "
            "This is not a complete course in any subject."
        ),
    },
    {
        "id": "bank",
        "title": "Finite challenge catalog",
        "detail": (
            "Questions are authored in advance. ADAPT does not generate an unlimited "
            "curriculum at runtime. Unavailable items are surfaced rather than invented."
        ),
    },
]


def product_content() -> dict[str, Any]:
    return {
        "promise": PROMISE,
        "promise_short": PROMISE_SHORT,
        "hero": HERO,
        "supporting": SUPPORTING,
        "cta_primary": CTA_PRIMARY,
        "cta_secondary": CTA_SECONDARY,
        "tagline": TAGLINE,
        "learner_chain": [
            "I answer",
            "ADAPT observes",
            "ADAPT understands",
            "ADAPT decides",
            "ADAPT changes",
            "I learn",
        ],
        "product_loop": [
            "Choose",
            "Learn",
            "Answer",
            "ADAPT notices",
            "Adaptation",
            "Improve",
        ],
        "chain": list(CHAIN),
        "architecture": [dict(item) for item in ARCHITECTURE],
        "technical_evidence": TECHNICAL_EVIDENCE,
        "limitations": [dict(item) for item in LIMITATIONS],
        "phase5": {
            "status": "INCONCLUSIVE",
            "n": 0,
            "statement": "Phase 5 human learning evaluation: INCONCLUSIVE (n=0)",
        },
    }
