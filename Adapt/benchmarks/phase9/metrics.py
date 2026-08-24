"""Phase 9 benchmark metrics."""

from __future__ import annotations

from typing import Any


def _ok(flag: bool) -> dict[str, Any]:
    return {"ok": flag, "pass": flag}


def compute_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    nav = raw["navigation"]
    domains = raw["domains"]
    variety = raw["variety"]
    diversity = raw["diversity"]
    light = raw["lightweight"]
    explain = raw["explanations"]
    preserve = raw["preservation"]
    cf = raw["counterfactual"]
    progress = raw["progress"]
    research = raw["research"]
    det = raw["determinism"]
    return {
        "M9-001_navigation": _ok(nav["ok"]),
        "M9-002_lightweight_evidence": _ok(light["ok"]),
        "M9-003_feedback_consistency": _ok(explain["ok"]),
        "M9-004_repetition_avoidance": _ok(diversity["ok"]),
        "M9-005_community_safety_subject": _ok(domains["subjects"] == 1),
        "M9-006_concept_coverage": _ok(domains["min_concepts"] >= 10),
        "M9-007_strategy_preservation": _ok(preserve["ok"]),
        "M9-008_counterfactual": _ok(cf["ok"]),
        "M9-009_research_trace": _ok(research["ok"]),
        "M9-010_progress": _ok(progress["ok"]),
        "M9-011_determinism": _ok(det["ok"]),
        "M9-012_challenge_variety": _ok(variety["types"] >= 4),
    }
