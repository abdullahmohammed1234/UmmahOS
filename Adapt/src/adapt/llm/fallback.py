"""Deterministic evidence fallback used when a live LLM is unavailable or invalid.

This path is the existing EvidenceAnalyzer. It is never labeled as Gemini or NVIDIA output.
"""

from __future__ import annotations

from adapt.analysis.evidence_analyzer import EvidenceAnalyzer
from adapt.models.challenge import Challenge
from adapt.models.evidence import Evidence
from adapt.models.learner_response import LearnerResponse

SOURCE_GEMINI = "GEMINI"
SOURCE_NVIDIA = "NVIDIA"
SOURCE_FALLBACK = "DETERMINISTIC_FALLBACK"
SOURCE_DETERMINISTIC = "DETERMINISTIC"
LIVE_EVIDENCE_SOURCES = frozenset({SOURCE_GEMINI, SOURCE_NVIDIA})


class DeterministicFallback:
    source = SOURCE_FALLBACK

    def __init__(self, analyzer: EvidenceAnalyzer | None = None) -> None:
        self.analyzer = analyzer or EvidenceAnalyzer()

    def analyze(
        self,
        response: LearnerResponse,
        challenge: Challenge | None,
        history: list[LearnerResponse] | None = None,
    ) -> Evidence:
        return self.analyzer.analyze(response, challenge, history)
