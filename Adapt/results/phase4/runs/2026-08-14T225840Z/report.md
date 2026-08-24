# Phase 4 — Learner Experience & Demo Product Results

## 1. Question

Can a real learner experience ADAPT's adaptation clearly, naturally, and convincingly,
without the product layer inventing adaptive decisions?

**Benchmark version:** `phase4-v1`
**Timestamp:** 2026-08-14T225840Z
**Seed:** `20260814`
**Python:** 3.12.8

## 2. Coverage

- Sessions: 20 (minimum 20)
- Interaction steps: 119 (minimum 100)
- Counterfactual pairs: 5 (minimum 5)
- Recovery scenarios: 5 (minimum 5)
- Misconception scenarios: 5 (minimum 5)

## 3. Metrics

| Metric | Result | Target | Met |
| --- | --- | --- | --- |
| M4-001 Task completion | 20 / 20 = 100.0% | ≥ 95% | True |
| M4-002 Adaptive result preservation | 119 / 119 = 100.0% | 100% | True |
| M4-003 Trace visibility | 119 / 119 = 100.0% | 100% | True |
| M4-004 Counterfactual preservation | 5 / 5 = 100.0% | 100% | True |
| M4-005 Session recovery | 5 / 5 = 100.0% | 100% | True |

## 4. Counterfactuals

- `P4-CF-001` PASS: INCREASE vs PROBE (engine INCREASE vs PROBE)
- `P4-CF-002` PASS: INCREASE vs GATHER_EVIDENCE (engine INCREASE vs GATHER_EVIDENCE)
- `P4-CF-003` PASS: INCREASE vs PROBE (engine INCREASE vs PROBE)
- `P4-CF-004` PASS: INCREASE vs PROBE (engine INCREASE vs PROBE)
- `P4-CF-005` PASS: INCREASE vs GATHER_EVIDENCE (engine INCREASE vs GATHER_EVIDENCE)

## 5. Restorations

- `P4-RESTORE-001` PASS: ['GATHER_EVIDENCE', 'PROBE', 'INCREASE', 'MAINTAIN']
- `P4-RESTORE-002` PASS: ['GATHER_EVIDENCE', 'MAINTAIN', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE']
- `P4-RESTORE-003` PASS: ['GATHER_EVIDENCE', 'MAINTAIN', 'INCREASE', 'PROBE']
- `P4-RESTORE-004` PASS: ['GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN']
- `P4-RESTORE-005` PASS: ['GATHER_EVIDENCE', 'MAINTAIN', 'PROBE', 'INCREASE']

## 6. Failures

No application-level session failed completion or preservation.

## 7. Usability

PENDING — no formative human test was executed in this automated run.

## 8. Conclusion

See docs/phase-4/4.md for the phase transition decision.

