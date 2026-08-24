"""Phase 5 evaluation constants. Frozen before participant analysis."""

from __future__ import annotations

BENCHMARK_VERSION = "phase5-v1"
RANDOM_SEED = 20260814
PLANNED_PARTICIPANTS = 10
TRAINING_STEPS_PER_TOPIC = 4
TRAINING_STEPS_PER_CONDITION = 8
PRETEST_ITEM_COUNT = 8
POSTTEST_ITEM_COUNT = 8

CONDITIONS = ("ADAPT", "BASELINE")
TOPICS = ("algebra", "fractions")

ADAPT_START = {
    "algebra": "ALG-D-001",
    "fractions": "FR-D-001",
}

# Frozen linear baseline sequence. Order does not depend on learner performance.
BASELINE_SEQUENCE = (
    "ALG-E-001",
    "ALG-M-001",
    "ALG-D-001",
    "ALG-M-002",
    "FR-E-001",
    "FR-M-001",
    "FR-D-001",
    "FR-P-001",
)

DIST_PROP = "DIST_PROP"
ADD_DENOM = "ADD_DENOM"

DIST_PROP_TRAINING_IDS = frozenset({"ALG-D-001", "ALG-M-002", "ALG-P-001", "ALG-P-002", "ALG-P-003", "ALG-R-001"})
ADD_DENOM_TRAINING_IDS = frozenset({"FR-M-001", "FR-D-001", "FR-P-001", "FR-P-002", "FR-R-001"})

DIST_PROP_POST_IDS = frozenset({"POST-A-003", "POST-B-003"})
ADD_DENOM_POST_IDS = frozenset({"POST-A-006", "POST-B-006"})

CONCEPTUAL_CUES = {
    DIST_PROP: ("distribute", "both terms", "both", "two groups"),
    ADD_DENOM: ("common denominator", "equivalent", "numerators", "same denominator", "sixths"),
}

HUMAN_SOURCE = "human"
SYNTHETIC_SOURCE = "synthetic"

DELAYED_RETENTION_STATUS = "NOT COLLECTED"

# Frozen interpretation rule (set before inspecting human outcomes).
MIN_N_FOR_INFERENCE = 6
MIN_N_FOR_EXPLORATORY_DIRECTION = 1
SMALL_SAMPLE_NOTE = "Exploratory evidence only."
