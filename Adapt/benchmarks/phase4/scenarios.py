"""Phase 4 application-level scenarios.

Inputs are scripted learner evidence. Expected adaptive results are NOT hardcoded;
they are compared to the Phase 3 AdaptiveTutor running the same inputs.
"""

from __future__ import annotations

SCENARIOS = (
    {"id": "P4-S-001", "topic_id": "algebra", "initial_challenge": "ALG-D-001", "kinds": ("strong_correct",) * 6},
    {"id": "P4-S-002", "topic_id": "algebra", "initial_challenge": "ALG-M-001", "kinds": ("weak_correct",) * 6},
    {"id": "P4-S-003", "topic_id": "algebra", "initial_challenge": "ALG-M-001", "kinds": ("strong_correct", "strong_correct", "weak_correct", "strong_correct", "moderate_correct", "strong_correct")},
    {"id": "P4-S-004", "topic_id": "fractions", "initial_challenge": "FR-D-001", "kinds": ("strong_correct",) * 6},
    {"id": "P4-S-005", "topic_id": "fractions", "initial_challenge": "FR-D-001", "kinds": ("weak_correct",) * 6},
    {"id": "P4-S-006", "topic_id": "algebra", "initial_challenge": "ALG-M-002", "kinds": ("moderate_correct",) * 6},
    {"id": "P4-S-007", "topic_id": "algebra", "initial_challenge": "ALG-M-001", "kinds": ("guess_correct", "weak_correct", "strong_correct", "strong_correct", "strong_correct", "weak_correct")},
    {"id": "P4-S-008", "topic_id": "fractions", "initial_challenge": "FR-M-001", "kinds": ("strong_correct", "weak_correct", "strong_correct", "moderate_correct", "strong_correct", "strong_correct")},
    {"id": "P4-S-009", "topic_id": "algebra", "initial_challenge": "ALG-M-001", "kinds": ("correct_unknown", "strong_correct", "strong_correct", "weak_correct", "strong_correct", "strong_correct")},
    {"id": "P4-S-010", "topic_id": "algebra", "initial_challenge": "ALG-M-001", "kinds": ("adversarial_harder", "weak_correct", "strong_correct", "strong_correct", "strong_correct", "moderate_correct")},
    {
        "id": "P4-R-001",
        "topic_id": "algebra",
        "initial_challenge": "ALG-D-001",
        "recovery_scenario": True,
        "kinds": ("strong_correct", "strong_correct", "misconception", "misconception", "misconception", "strong_correct", "strong_correct", "strong_correct"),
    },
    {
        "id": "P4-R-002",
        "topic_id": "algebra",
        "initial_challenge": "ALG-M-002",
        "recovery_scenario": True,
        "kinds": ("strong_correct", "misconception", "misconception", "misconception", "strong_correct", "strong_correct", "strong_correct"),
    },
    {
        "id": "P4-R-003",
        "topic_id": "fractions",
        "initial_challenge": "FR-D-001",
        "recovery_scenario": True,
        "kinds": ("strong_correct", "misconception", "misconception", "misconception", "strong_correct", "strong_correct", "strong_correct"),
    },
    {
        "id": "P4-R-004",
        "topic_id": "algebra",
        "initial_challenge": "ALG-D-001",
        "recovery_scenario": True,
        "kinds": ("moderate_correct", "misconception", "misconception", "misconception", "strong_correct", "strong_correct"),
    },
    {
        "id": "P4-R-005",
        "topic_id": "algebra",
        "initial_challenge": "ALG-P-001",
        "recovery_scenario": True,
        "kinds": ("misconception", "misconception", "misconception", "strong_correct", "strong_correct", "strong_correct"),
    },
    {
        "id": "P4-M-001",
        "topic_id": "algebra",
        "initial_challenge": "ALG-M-002",
        "misconception_scenario": True,
        "kinds": ("strong_correct", "strong_correct", "misconception", "misconception", "strong_correct"),
    },
    {
        "id": "P4-M-002",
        "topic_id": "algebra",
        "initial_challenge": "ALG-D-001",
        "misconception_scenario": True,
        "kinds": ("strong_correct", "misconception", "misconception", "weak_correct", "strong_correct"),
    },
    {
        "id": "P4-M-003",
        "topic_id": "fractions",
        "initial_challenge": "FR-D-001",
        "misconception_scenario": True,
        "kinds": ("strong_correct", "misconception", "misconception", "strong_correct", "strong_correct"),
    },
    {
        "id": "P4-M-004",
        "topic_id": "algebra",
        "initial_challenge": "ALG-M-001",
        "misconception_scenario": True,
        "kinds": ("weak_correct", "misconception", "misconception", "misconception", "strong_correct"),
    },
    {
        "id": "P4-M-005",
        "topic_id": "fractions",
        "initial_challenge": "FR-P-001",
        "misconception_scenario": True,
        "kinds": ("misconception", "misconception", "strong_correct", "strong_correct", "moderate_correct"),
    },
)

COUNTERFACTUALS = (
    {
        "id": "P4-CF-001",
        "challenge_id": "ALG-M-001",
        "concept_id": "basic_algebra",
        "learner_a": {"label": "Learner A", "kinds": ["strong_correct", "strong_correct", "strong_correct"]},
        "learner_b": {"label": "Learner B", "kinds": ["weak_correct", "weak_correct", "weak_correct"]},
    },
    {
        "id": "P4-CF-002",
        "challenge_id": "ALG-D-001",
        "concept_id": "basic_algebra",
        "learner_a": {"label": "Learner A", "kinds": ["strong_correct"] * 4},
        "learner_b": {"label": "Learner B", "kinds": ["strong_correct", "strong_correct", "misconception"]},
    },
    {
        "id": "P4-CF-003",
        "challenge_id": "FR-D-001",
        "concept_id": "fractions",
        "learner_a": {"label": "Learner A", "kinds": ["strong_correct"] * 3},
        "learner_b": {"label": "Learner B", "kinds": ["weak_correct"] * 3},
    },
    {
        "id": "P4-CF-004",
        "challenge_id": "ALG-M-002",
        "concept_id": "basic_algebra",
        "learner_a": {"label": "Learner A", "kinds": ["strong_correct"] * 3},
        "learner_b": {"label": "Learner B", "kinds": ["guess_correct"] * 3},
    },
    {
        "id": "P4-CF-005",
        "challenge_id": "FR-M-001",
        "concept_id": "fractions",
        "learner_a": {"label": "Learner A", "kinds": ["strong_correct"] * 4},
        "learner_b": {"label": "Learner B", "kinds": ["correct_unknown"] * 4},
    },
)
