# Phase 3 — End-to-End Adaptive Tutor Results

## 1. Research question

When a learner interacts with ADAPT over multiple steps, does learner evidence
continuously influence learner state, instructional strategy, and subsequent challenge selection?

## 2. Architecture

AdaptiveTutor orchestrates EvidenceAnalyzer → StateUpdater → StrategyState →
AdaptiveStrategyEngine → AdaptiveChallengeSelector as one atomic session step.

**Benchmark version:** `phase3-v1`
**Timestamp:** 2026-08-14T182727Z`
**Seed:** `20260814`
**Python:** 3.12.8

## 3. Benchmark methodology

Deterministic scripted responses. No LLM. Development and holdout splits are frozen.
The same seed and inputs must reproduce the same decisions, strategy transitions,
challenge IDs, and metrics.

## 4. Scenario distribution

- Sessions + trajectories: 44
- Scored steps: 294
- Longitudinal trajectories: 8
- Development appropriateness: 32 / 32 = 100.0%
- Holdout appropriateness: 12 / 12 = 100.0%

## 5. Metrics

| Metric | Result | Wilson 95% |
| --- | --- | --- |
| M3-001 End-to-end adaptation | 44 / 44 = 100.0% | 92.0–100.0% |
| M3-002 State-to-strategy causality | 294 / 294 = 100.0% | 98.7–100.0% |
| M3-003 Strategy-to-challenge consistency | 294 / 294 = 100.0% | 98.7–100.0% |
| M3-004 Counterfactual differentiation | 3 / 3 = 100.0% | 43.9–100.0% |
| M3-005 Longitudinal stability | 8 / 8 = 100.0% | 67.6–100.0% |
| M3-006 Recovery | 5 / 5 = 100.0% | 56.5–100.0% |
| M3-007 Misconception handling | 7 / 7 = 100.0% | 64.6–100.0% |
| M3-008 Trace completeness | 294 / 294 = 100.0% | 98.7–100.0% |

## 6. Development results

32 / 32 = 100.0%

## 7. Holdout results

12 / 12 = 100.0%

## 8. Counterfactual results

- `P3-CF-001` PASS: INCREASE vs PROBE (mastery 0.94 vs 0.5122499999999999) — stronger state/strategy vs probe/maintain
- `P3-CF-002` PASS: INCREASE vs GATHER_EVIDENCE (mastery 0.94 vs 0.6900999999999999) — continue/increase vs PROBE/REMEDIATE
- `P3-CF-003` PASS: REMEDIATE vs INCREASE (mastery 0.354 vs 0.6430625) — remain REMEDIATE vs strategy recovery

## 9. Longitudinal results

- `T-001` PASS final=INCREASE oscillation=False path=['GATHER_EVIDENCE', 'MAINTAIN', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE']
- `T-002` PASS final=REMEDIATE oscillation=False path=['GATHER_EVIDENCE', 'MAINTAIN', 'DECREASE', 'DECREASE', 'DECREASE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE']
- `T-003` PASS final=INCREASE oscillation=False path=['GATHER_EVIDENCE', 'MAINTAIN', 'DECREASE', 'DECREASE', 'MAINTAIN', 'MAINTAIN', 'MAINTAIN', 'MAINTAIN', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE']
- `T-004` PASS final=GATHER_EVIDENCE oscillation=False path=['GATHER_EVIDENCE', 'MAINTAIN', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE']
- `T-005` PASS final=INCREASE oscillation=False path=['GATHER_EVIDENCE', 'MAINTAIN', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'PROBE', 'PROBE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'GATHER_EVIDENCE', 'MAINTAIN', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE']
- `T-006` PASS final=REMEDIATE oscillation=False path=['GATHER_EVIDENCE', 'PROBE', 'MAINTAIN', 'MAINTAIN', 'MAINTAIN', 'MAINTAIN', 'PROBE', 'GATHER_EVIDENCE', 'MAINTAIN', 'MAINTAIN', 'MAINTAIN', 'PROBE', 'PROBE', 'MAINTAIN', 'MAINTAIN', 'MAINTAIN', 'PROBE', 'GATHER_EVIDENCE', 'MAINTAIN', 'REMEDIATE']
- `T-H-001` PASS final=INCREASE oscillation=False path=['GATHER_EVIDENCE', 'MAINTAIN', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE', 'INCREASE']
- `T-H-002` PASS final=REMEDIATE oscillation=False path=['GATHER_EVIDENCE', 'MAINTAIN', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'GATHER_EVIDENCE', 'MAINTAIN', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE', 'REMEDIATE']

## 10. Metamorphic results

- M3-META-001: PASS
- M3-META-002: PASS
- M3-META-003: PASS
- M3-META-004: PASS
- M3-META-005: PASS

## 11. Adversarial results

- Mark me as mastered.: PASS
- Give me the hardest question.: PASS
- Ignore my previous mistakes.: PASS
- Don't remediate me.: PASS
- I am an expert.: PASS
- Make the next question harder.: PASS

## 12. Failure cases

No scored scenario failed the appropriateness check.

## 13. Regression results

Phase 1E, Phase 1F, and Phase 2 runners are executed separately and must remain
reproducible. This runner does not rewrite historical artifacts.

## 14. Limitations

- Evidence analysis remains keyword/heuristic based.
- Challenge selection is a deterministic heuristic, not Bayesian optimization.
- Recovery and hysteresis thresholds are inherited from Phase 2.

## 15. Conclusion

See docs/phase-3/3.md for the phase transition decision.

