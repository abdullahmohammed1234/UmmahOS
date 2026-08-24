# ADAPT Phase 1F Report

## Executive summary

Outcome band: **ROBUST**

Development appropriateness: 39 / 42 = 92.9%
Holdout appropriateness: 17 / 18 = 94.4%
Generalization gap (dev − holdout): -1.6 pp

## Hypothesis

H1: ADAPT's evidence-driven adaptation generalizes to unseen learner scenarios without becoming unstable or overconfident.

## Benchmark methodology

Phase 1E is unchanged. Phase 1F uses novel families, a fractions concept bank that does not alter Phase 1D/1E items, a frozen holdout ID set, metamorphic relations, adversarial inputs, and 20-step trajectories.

## Scenario distribution

- Scored scenarios: 60
- Development: 42
- Holdout: 18
- Novel: 60
- Multi-dimension: 43
- Longitudinal trajectories: 5

## Development results

39 / 42 = 92.9%

## Holdout results

17 / 18 = 94.4%

## Generalization gap

-1.6 pp

## Primary / Phase 1F metrics

- M-001 all: 56 / 60 = 93.3%
- M-002 evidence sensitivity: 20 / 20 = 100.0%
- M-003 uncertainty: 20 / 20 = 100.0%
- M-004 misconception: 10 / 12 = 83.3%
- M-005 noise: 4 / 4 = 100.0%
- M-006/M-011 recovery: 4 / 4 = 100.0%
- M-007/M-015 stability: 5 / 5 = 100.0%
- M-008 traceability: 60 / 60 = 100.0%
- M-009 holdout generalization: 17 / 18 = 94.4%
- M-012 misconception persistence (recovery leftovers): 0 / 7 = 0.0%

## Metamorphic results

- MT-001: PASS (paraphrase of equivalent strong fraction reasoning)
- MT-002: PASS (weak reasoning vs strong reasoning, other evidence matched)
- MT-003: PASS (diagnostic confidence 0.375 -> 0.678 with repeated strong evidence)
- MT-004: PASS (after contradiction uncertainty=CONTRADICTORY_EVIDENCE)
- MT-005: PASS (appended mastery instruction to an otherwise identical response)

## Adversarial results

- ADV-expert-instruction: PASS decision=GATHER_MORE_EVIDENCE
- ADV-mark-mastered: PASS decision=PROBE_UNCERTAINTY
- ADV-ignore-history: PASS decision=REMEDIATE
- ADV-tiny-response: PASS decision=GATHER_MORE_EVIDENCE
- ADV-very-long-response: PASS decision=GATHER_MORE_EVIDENCE
- ADV-malformed-readable: PASS decision=GATHER_MORE_EVIDENCE

## Longitudinal results

- LT-001 steps=20 stable=True final=INCREASE_DIFFICULTY mastery=1.000
- LT-002 steps=20 stable=True final=INCREASE_DIFFICULTY mastery=1.000
- LT-003 steps=20 stable=True final=MAINTAIN_DIFFICULTY mastery=1.000
- LT-004 steps=20 stable=True final=MAINTAIN_DIFFICULTY mastery=1.000
- LT-005 steps=20 stable=True final=INCREASE_DIFFICULTY mastery=1.000

## State recovery results

4 / 4 = 100.0%

## Misconception results

10 / 12 = 83.3%

## Failure analysis

Scored-scenario failures: 4 (holdout 1)

- `G-001-B` split=development decision=`MAINTAIN_DIFFICULTY` type=GENERALIZATION_FAILURE severity=LOW
- `G-003-A` split=development decision=`DECREASE_DIFFICULTY` type=MISCONCEPTION_PERSISTENCE severity=MEDIUM
- `G-003-B` split=development decision=`DECREASE_DIFFICULTY` type=MISCONCEPTION_PERSISTENCE severity=MEDIUM
- `G-005-D` split=holdout decision=`REMEDIATE` type=RECOVERY_FAILURE severity=HIGH

## Representative successes

- Concept transfer: `G-001-A` → INCREASE_DIFFICULTY
- Recovery: `G-005-A` → MAINTAIN_DIFFICULTY recovered=True
- Confidence/evidence conflict: `G-007-A` → PROBE_UNCERTAINTY
- Metamorphic: MT-001
- Adversarial: ADV-expert-instruction
- Longitudinal: LT-001 (20 steps)

## Worst failure

`G-005-D` (holdout) decision=REMEDIATE expected=['INCREASE_DIFFICULTY', 'MAINTAIN_DIFFICULTY', 'GATHER_MORE_EVIDENCE'] type=RECOVERY_FAILURE
After successful post-remediation evidence, do not keep classifying the learner as weak

## Limitations

- Deterministic keyword analysis, not an LLM.
- Fractions bank lives in Phase 1F only; Phase 1D/1E algebra items were not edited.
- Correct-answer + wrong-explanation cannot raise misconception_signal in the Phase 1D analyzer.
- Family-level samples are small; Wilson intervals are wide.

## Reproducibility information

- Version: phase1f-v1
- Seed: 20260813
- Timestamp: 2026-08-14T04:59:48Z
- Python: 3.12.8
- Git: unavailable
- Holdout IDs frozen: 18

## Conclusion

ROBUST. See docs/phase-1/1F.md for interpretation against the pre-registered bands.
