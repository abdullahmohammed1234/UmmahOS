"""LLM boundary around ADAPT. The LLM interprets evidence; ADAPT decides."""

from adapt.llm.analyzer import LLMEvidenceAnalyzer
from adapt.llm.baseline import SinglePromptBaseline
from adapt.llm.client import LLMClient, LLMGeneration
from adapt.llm.fallback import SOURCE_FALLBACK, SOURCE_GEMINI, SOURCE_NVIDIA, DeterministicFallback
from adapt.llm.gemini import GeminiClient
from adapt.llm.nvidia import NvidiaClient
from adapt.llm.workflow import EvidenceExtractionWorkflow, WorkflowResult

__all__ = [
    "DeterministicFallback",
    "EvidenceExtractionWorkflow",
    "GeminiClient",
    "LLMClient",
    "LLMEvidenceAnalyzer",
    "LLMGeneration",
    "NvidiaClient",
    "SOURCE_FALLBACK",
    "SOURCE_GEMINI",
    "SOURCE_NVIDIA",
    "SinglePromptBaseline",
    "WorkflowResult",
]
