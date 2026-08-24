# Phase 2 — Adaptive Strategy Layer Results

**Benchmark version:** `phase2-v1`
**Timestamp:** 2026-08-14T06:24:23Z
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

M2-008 recovery latency mean: 2.125 (n=8)

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

## Required answers

### Did Phase 2 fix G-003?

Yes, on the dedicated regression. Phase 1F G-003-A/B decided `DECREASE_DIFFICULTY`.
Phase 2 decides `PROBE` because a delayed misconception after a strong history is not
treated as global regression. Persistent misconception (three repeats) can still
`REMEDIATE`. Global regression scenarios still allow `DECREASE`.

### Did Phase 2 fix G-005?

Yes, on the dedicated holdout regression. Phase 1F G-005-D kept `REMEDIATE` after
mastery had already risen. Phase 2 recovers to `MAINTAIN` after sufficient recovery
evidence (repeated correct responses with reasoning quality, not correctness alone).
One isolated success during remediation is not enough.

### Did Phase 2 improve cross-concept behavior?

Yes, in the sense that strategy rules consume evidence/state and do not branch on
hardcoded concept names. Algebra 31/31 and fractions 29/29 were both appropriate
on the Phase 2 suite. G-001-B was **not** recoded to INCREASE; the subtraction item
uses addition-oriented reasoning, so MAINTAIN is the justified strategy.

### Did Phase 2 introduce new regressions?

No scored Phase 2 scenario failed. Phase 1D/1E tests still pass. Re-running frozen
Phase 1F without persistence reproduced development 39/42 = 92.9% and holdout
17/18 = 94.4% (gap −1.6 pp, ROBUST). Historical Phase 1F files were not rewritten.

### Did Phase 1 behavior remain intact?

Yes. `AdaptPipeline()` still uses the Phase 1 AdaptationEngine by default. The
strategy layer is opt-in via `strategy_engine=`. Phase 1E and Phase 1F scenarios,
labels, and historical result files were not modified.

## Comparison notes

Phase 1F remains the frozen generalization benchmark. Phase 2 uses a new scenario
suite and a new strategy layer. Overall M-001 vs M2-001 is not a valid head-to-head.
The valid before/after comparison is the dedicated G-001-B, G-003-A/B, and G-005-D
regressions above.

| Item | Phase 1F | Phase 2 | Valid comparison |
| --- | --- | --- | --- |
| G-003-A | DECREASE (fail) | PROBE | fixed |
| G-003-B | DECREASE (fail) | PROBE | fixed |
| G-005-D | REMEDIATE (fail) | MAINTAIN | fixed |
| G-001-B | MAINTAIN vs INCREASE label | MAINTAIN | label was too strong; not recoded |

