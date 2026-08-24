# Phase 2 — Adaptive Strategy Layer Results

**Benchmark version:** `phase2-v1`
**Timestamp:** 2026-08-14T06:22:13Z
**Scenarios:** 60

## Metrics

| Metric | Result | Wilson 95% |
| --- | --- | --- |
| M2-001 Strategy appropriateness | 60 / 60 = 100.0% | 94.0–100.0% |
| M2-002 Strategy recovery | 8 / 8 = 100.0% | 67.6–100.0% |
| M2-003 Misconception/regression separation | 8 / 8 = 100.0% | 67.6–100.0% |
| M2-004 Unnecessary transitions (lower better) | 0 / 60 = 0.0% | 0.0–6.0% |
| M2-005 Evidence sensitivity | 4 / 4 = 100.0% | 51.0–100.0% |
| M2-006 Traceability | 60 / 60 = 100.0% | 94.0–100.0% |
| M2-007 Cross-concept generalization | 60 / 60 = 100.0% | 94.0–100.0% |

M2-008 recovery latency mean: 1.125 (n=8)

## Cross-concept breakdown

- `basic_algebra`: 31 / 31 = 100.0%
- `fractions`: 29 / 29 = 100.0%

## Counterfactual strategy tests

- `P2-CF-001` PASS: PROBE vs REMEDIATE (PROBE/GATHER vs REMEDIATE)
- `P2-CF-002` PASS: REMEDIATE vs MAINTAIN (one success stays REMEDIATE; three strong successes recover)
- `P2-CF-003` PASS: PROBE vs DECREASE (localized error vs global weakness yield different strategies)
- `P2-CF-004` PASS: REMEDIATE vs ASSESS (same mastery, different strategy history, different transition)

## Phase 1F failure regressions (Phase 2 pipeline)

- `G-001-B` Phase 1F=`MAINTAIN_DIFFICULTY` Phase 2=`MAINTAIN` target=justified strategy; do not force INCREASE verdict=DOCUMENTED
  - FR-M-002 is subtraction; the supplied reasoning talks about adding numerators. Evidence is not strong enough to justify INCREASE. Phase 1F's INCREASE label was overly optimistic for this item.
- `G-003-A` Phase 1F=`DECREASE_DIFFICULTY` Phase 2=`PROBE` target=PROBE / GATHER_EVIDENCE verdict=FIXED
- `G-003-B` Phase 1F=`DECREASE_DIFFICULTY` Phase 2=`PROBE` target=PROBE / GATHER_EVIDENCE verdict=FIXED
- `G-005-D` Phase 1F=`REMEDIATE` Phase 2=`MAINTAIN` target=strategy recovery away from REMEDIATE verdict=FIXED

## Invariants

- invariant_1_weak_evidence_not_high_mastery: PASS
- invariant_8_traceable: PASS
- invariant_9_no_simple_oscillation: PASS
- invariant_6_counterfactuals_differ: PASS

## Failures

No scored Phase 2 scenario failures.

## Comparison notes

Phase 1F remains the frozen generalization benchmark. Phase 2 uses a new scenario
suite and a new strategy layer. Overall M-001 vs M2-001 is not a valid head-to-head
unless the same items are compared. The valid before/after comparison is the dedicated
G-001-B, G-003-A/B, and G-005-D regressions above.

