"""Longitudinal Phase 3 trajectories (20+ steps)."""

from __future__ import annotations

from dataclasses import dataclass

from benchmarks.phase3.expected import HOLDOUT_IDS


@dataclass(frozen=True)
class TrajectorySpec:
    trajectory_id: str
    label: str
    concept: str
    kinds: tuple[str, ...]
    expected_path: tuple[str, ...]
    expected_behavior: str
    forbidden: tuple[str, ...] = ()
    initial_challenge_id: str | None = None
    recovery_scenario: bool = False
    misconception_scenario: bool = False

    @property
    def split(self) -> str:
        return "holdout" if self.trajectory_id in HOLDOUT_IDS else "development"

    @property
    def n_steps(self) -> int:
        return len(self.kinds)


def _repeat(kind: str, n: int) -> tuple[str, ...]:
    return tuple(kind for _ in range(n))


def _t001() -> tuple[str, ...]:
    return _repeat("strong_correct", 20)


def _t002() -> tuple[str, ...]:
    return ("wrong_weak", "misconception") * 10


def _t003() -> tuple[str, ...]:
    return (
        _repeat("wrong_weak", 4)
        + _repeat("moderate_correct", 4)
        + _repeat("strong_correct", 12)
    )


def _t004() -> tuple[str, ...]:
    return ("strong_correct", "wrong_weak") * 10


def _t005() -> tuple[str, ...]:
    return (
        _repeat("strong_correct", 6)
        + _repeat("misconception", 4)
        + _repeat("strong_correct", 10)
    )


def _t006() -> tuple[str, ...]:
    pattern = (
        "strong_correct",
        "guess_correct",
        "arithmetic",
        "moderate_correct",
        "wrong_weak",
        "strong_correct",
        "correct_high_weak",
        "ambiguous",
        "strong_correct",
        "misconception",
    )
    return pattern + pattern


def build_trajectories() -> tuple[TrajectorySpec, ...]:
    return (
        TrajectorySpec(
            trajectory_id="T-001",
            label="Strong learner",
            concept="basic_algebra",
            kinds=_t001(),
            expected_path=("ASSESS", "MAINTAIN", "INCREASE", "INCREASE"),
            expected_behavior="ASSESS/GATHER then MAINTAIN/INCREASE; no remediation.",
            forbidden=("REMEDIATE", "DECREASE"),
            initial_challenge_id="ALG-M-001",
        ),
        TrajectorySpec(
            trajectory_id="T-002",
            label="Struggling learner",
            concept="basic_algebra",
            kinds=_t002(),
            expected_path=("ASSESS", "PROBE", "REMEDIATE", "REMEDIATE"),
            expected_behavior="ASSESS then PROBE/REMEDIATE; gather rather than increase.",
            forbidden=("INCREASE",),
            misconception_scenario=True,
            initial_challenge_id="ALG-M-002",
        ),
        TrajectorySpec(
            trajectory_id="T-003",
            label="Improving learner",
            concept="basic_algebra",
            kinds=_t003(),
            expected_path=("GATHER_EVIDENCE", "MAINTAIN", "RECOVER", "INCREASE"),
            expected_behavior="Early gathering, later maintain/recovery/increase.",
            initial_challenge_id="ALG-E-001",
            recovery_scenario=True,
        ),
        TrajectorySpec(
            trajectory_id="T-004",
            label="Oscillating learner",
            concept="basic_algebra",
            kinds=_t004(),
            expected_path=("ASSESS", "PROBE", "GATHER_EVIDENCE", "MAINTAIN"),
            expected_behavior="No extreme INCREASE↔DECREASE oscillation.",
            initial_challenge_id="ALG-M-001",
        ),
        TrajectorySpec(
            trajectory_id="T-005",
            label="Misconception/recovery learner",
            concept="basic_algebra",
            kinds=_t005(),
            expected_path=("MAINTAIN", "PROBE", "REMEDIATE", "RECOVER", "MAINTAIN"),
            expected_behavior="Probe then remediate, then recover; not global regression.",
            misconception_scenario=True,
            recovery_scenario=True,
            forbidden=("DECREASE",),
            initial_challenge_id="ALG-M-002",
        ),
        TrajectorySpec(
            trajectory_id="T-006",
            label="Mixed/noisy learner",
            concept="basic_algebra",
            kinds=_t006(),
            expected_path=("ASSESS", "GATHER_EVIDENCE", "PROBE", "MAINTAIN"),
            expected_behavior="Noisy mixed evidence stays conservative.",
            initial_challenge_id="ALG-M-001",
        ),
        TrajectorySpec(
            trajectory_id="T-H-001",
            label="Holdout strong fractions",
            concept="fractions",
            kinds=_repeat("strong_correct", 20),
            expected_path=("ASSESS", "MAINTAIN", "INCREASE"),
            expected_behavior="Holdout strong fractions longitudinal.",
            forbidden=("REMEDIATE",),
            initial_challenge_id="FR-M-001",
        ),
        TrajectorySpec(
            trajectory_id="T-H-002",
            label="Holdout oscillating fractions",
            concept="fractions",
            kinds=("strong_correct", "wrong_weak") * 10,
            expected_path=("ASSESS", "PROBE", "GATHER_EVIDENCE"),
            expected_behavior="Holdout oscillation should not thrash INCREASE/DECREASE.",
            initial_challenge_id="FR-E-001",
        ),
    )


TRAJECTORIES = build_trajectories()
TRAJECTORY_BY_ID = {item.trajectory_id: item for item in TRAJECTORIES}
