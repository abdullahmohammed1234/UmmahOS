# ADAPT Phase 1E Benchmark Report

## 1. Executive summary

Hypothesis evaluation: **SUPPORTED**

ADAPT met the predefined strong-support pattern on this frozen benchmark.

Scenario executions: 51

## 2. Hypothesis

H1: ADAPT will make more evidence-appropriate instructional decisions than the baseline because it explicitly represents learner evidence, learner state, uncertainty, and adaptation decisions.

H0: ADAPT does not demonstrate a meaningful advantage over the baseline on the predefined evaluation criteria.

## 3. Systems compared

- BASELINE-001: simple deterministic heuristic tutor. Inspects response, reasoning, confidence, history, and challenge. Does not maintain ADAPT learner state.
- ADAPT-001: Phase 1D pipeline (Evidence Analyzer → State Updater → Adaptation Engine → Challenge Selector).

## 4. Benchmark methodology

Both systems received the same scenario, current challenge, learner response, and history. Expected labels were not provided to either system. The benchmark is deterministic.

## 5. Scenario suite

- Families: 12 required families plus two extra counterfactual pair families.
- Executions: 51
- Counterfactual pairs: 9

## 6. Metrics

### M-001 Decision appropriateness
- ADAPT: 51 / 51 = 100.0%
- BASELINE: 48 / 51 = 94.1%
- Difference: +5.9 pp
- Relative improvement: +6.3%

### M-002 Counterfactual differentiation
- ADAPT: 9 / 9 = 100.0%
- BASELINE: 6 / 9 = 66.7%
- Difference: +33.3 pp
- Relative improvement: +50.0%

### M-003 Evidence sensitivity
- ADAPT: 9 / 9 = 100.0%
- BASELINE: 6 / 9 = 66.7%
- Difference: +33.3 pp
- Relative improvement: +50.0%

### M-004 Misconception response
- ADAPT: 3 / 3 = 100.0%
- BASELINE: 3 / 3 = 100.0%
- Difference: +0.0 pp
- Relative improvement: +0.0%

### M-005 Uncertainty handling
- ADAPT: 9 / 9 = 100.0%
- BASELINE: 9 / 9 = 100.0%
- Difference: +0.0 pp
- Relative improvement: +0.0%

### M-006 Noise stability
- ADAPT: 3 / 3 = 100.0%
- BASELINE: 3 / 3 = 100.0%
- Difference: +0.0 pp
- Relative improvement: +0.0%

### M-007 Difficulty appropriateness
- ADAPT: 51 / 51 = 100.0%
- BASELINE: 51 / 51 = 100.0%
- Difference: +0.0 pp
- Relative improvement: +0.0%

### M-008 Decision traceability
- ADAPT: 51 / 51 = 100.0%
- BASELINE: 0 / 51 = 0.0%
- Difference: +100.0 pp
- Relative improvement: n/a

## 7. Statistical methodology

Binary rates use Wilson 95% confidence intervals. Paired appropriateness uses McNemar's test on discordant pairs. p-values are descriptive for this prototype sample.

McNemar n10 (ADAPT only appropriate) = 3, n01 (baseline only appropriate) = 0, statistic = 1.333, p = 0.2482. descriptive prototype p-value; do not treat as confirmatory

## 8. ADAPT results

- CF-P2: 6 / 6 = 100.0%
- CF-P3: 6 / 6 = 100.0%
- S-001: 3 / 3 = 100.0%
- S-002: 3 / 3 = 100.0%
- S-003: 3 / 3 = 100.0%
- S-004: 3 / 3 = 100.0%
- S-005: 3 / 3 = 100.0%
- S-006: 3 / 3 = 100.0%
- S-007: 3 / 3 = 100.0%
- S-008: 3 / 3 = 100.0%
- S-009: 3 / 3 = 100.0%
- S-010: 3 / 3 = 100.0%
- S-011: 3 / 3 = 100.0%
- S-012: 6 / 6 = 100.0%

## 9. Baseline results

- CF-P2: 6 / 6 = 100.0%
- CF-P3: 3 / 6 = 50.0%
- S-001: 3 / 3 = 100.0%
- S-002: 3 / 3 = 100.0%
- S-003: 3 / 3 = 100.0%
- S-004: 3 / 3 = 100.0%
- S-005: 3 / 3 = 100.0%
- S-006: 3 / 3 = 100.0%
- S-007: 3 / 3 = 100.0%
- S-008: 3 / 3 = 100.0%
- S-009: 3 / 3 = 100.0%
- S-010: 3 / 3 = 100.0%
- S-011: 3 / 3 = 100.0%
- S-012: 6 / 6 = 100.0%

## 10. Paired comparison

- ADAPT: 51 / 51 = 100.0%
- BASELINE: 48 / 51 = 94.1%
- Difference: +5.9 pp
- Relative improvement: +6.3%

## 11. Counterfactual results

ADAPT pairs:
- CF-P1-v1 (reasoning_quality): INCREASE_DIFFICULTY vs PROBE_UNCERTAINTY differentiated=True sensitive=True
- CF-P1-v2 (reasoning_quality): INCREASE_DIFFICULTY vs PROBE_UNCERTAINTY differentiated=True sensitive=True
- CF-P1-v3 (reasoning_quality): INCREASE_DIFFICULTY vs PROBE_UNCERTAINTY differentiated=True sensitive=True
- CF-P2-v1 (misconception): INCREASE_DIFFICULTY vs REMEDIATE differentiated=True sensitive=True
- CF-P2-v2 (misconception): INCREASE_DIFFICULTY vs REMEDIATE differentiated=True sensitive=True
- CF-P2-v3 (misconception): INCREASE_DIFFICULTY vs REMEDIATE differentiated=True sensitive=True
- CF-P3-v1 (learner_confidence): INCREASE_DIFFICULTY vs MAINTAIN_DIFFICULTY differentiated=True sensitive=True
- CF-P3-v2 (learner_confidence): INCREASE_DIFFICULTY vs MAINTAIN_DIFFICULTY differentiated=True sensitive=True
- CF-P3-v3 (learner_confidence): INCREASE_DIFFICULTY vs MAINTAIN_DIFFICULTY differentiated=True sensitive=True

Baseline pairs:
- CF-P1-v1 (reasoning_quality): INCREASE_DIFFICULTY vs MAINTAIN_DIFFICULTY differentiated=True sensitive=True
- CF-P1-v2 (reasoning_quality): INCREASE_DIFFICULTY vs MAINTAIN_DIFFICULTY differentiated=True sensitive=True
- CF-P1-v3 (reasoning_quality): INCREASE_DIFFICULTY vs MAINTAIN_DIFFICULTY differentiated=True sensitive=True
- CF-P2-v1 (misconception): INCREASE_DIFFICULTY vs REMEDIATE differentiated=True sensitive=True
- CF-P2-v2 (misconception): INCREASE_DIFFICULTY vs REMEDIATE differentiated=True sensitive=True
- CF-P2-v3 (misconception): INCREASE_DIFFICULTY vs REMEDIATE differentiated=True sensitive=True
- CF-P3-v1 (learner_confidence): INCREASE_DIFFICULTY vs INCREASE_DIFFICULTY differentiated=False sensitive=False
- CF-P3-v2 (learner_confidence): INCREASE_DIFFICULTY vs INCREASE_DIFFICULTY differentiated=False sensitive=False
- CF-P3-v3 (learner_confidence): INCREASE_DIFFICULTY vs INCREASE_DIFFICULTY differentiated=False sensitive=False

## 12. Failure analysis

ADAPT inappropriate decisions: 0


Baseline inappropriate decisions: 3

- `CF-P3-v1-B` decision=`INCREASE_DIFFICULTY` error=`OTHER`
- `CF-P3-v2-B` decision=`INCREASE_DIFFICULTY` error=`OTHER`
- `CF-P3-v3-B` decision=`INCREASE_DIFFICULTY` error=`OTHER`

## 13. Representative examples

### ADAPT strong mastery

- Scenario: `S-001-A`
- Expected: INCREASE_DIFFICULTY after repeated strong reliable success
- ADAPT decision: `INCREASE_DIFFICULTY` (appropriate)
- Baseline decision: `INCREASE_DIFFICULTY` (appropriate)
- ADAPT evidence: `{'response_id': 'S-001-A-CUR', 'answer_status': 'CORRECT', 'reasoning_quality': 'STRONG', 'error_type': 'NONE', 'misconception_signal': None, 'confidence_signal': 'HIGH', 'evidence_strength': 'STRONG', 'diagnostic_confidence': 'HIGH', 'evidence_reliability': 'HIGH', 'polarity': 'POSITIVE'}`
- Baseline diagnosis: Baseline used correctness=CORRECT with heuristic reasons: correct_strong_reasoning_repeated_success

### ADAPT lucky guess

- Scenario: `S-002-A`
- Expected: Do not infer mastery from a lucky correct guess
- ADAPT decision: `GATHER_MORE_EVIDENCE` (appropriate)
- Baseline decision: `GATHER_MORE_EVIDENCE` (appropriate)
- ADAPT evidence: `{'response_id': 'S-002-A-CUR', 'answer_status': 'CORRECT', 'reasoning_quality': 'WEAK', 'error_type': 'NONE', 'misconception_signal': None, 'confidence_signal': 'LOW', 'evidence_strength': 'WEAK', 'diagnostic_confidence': 'LOW', 'evidence_reliability': 'LOW', 'polarity': 'POSITIVE'}`
- Baseline diagnosis: Baseline used correctness=CORRECT with heuristic reasons: guess_language

### ADAPT repeated misconception

- Scenario: `S-005-A`
- Expected: Repeated misconception should change strategy, not increase difficulty
- ADAPT decision: `REMEDIATE` (appropriate)
- Baseline decision: `REMEDIATE` (appropriate)
- ADAPT evidence: `{'response_id': 'S-005-A-CUR', 'answer_status': 'INCORRECT', 'reasoning_quality': 'STRONG', 'error_type': 'CONCEPTUAL', 'misconception_signal': 'DIST_PROP', 'confidence_signal': 'HIGH', 'evidence_strength': 'MODERATE', 'diagnostic_confidence': 'MODERATE', 'evidence_reliability': 'MODERATE', 'polarity': 'NEGATIVE'}`
- Baseline diagnosis: Baseline used correctness=INCORRECT with heuristic reasons: repeated_misconception_keywords

### Counterfactual pair

- Scenario: `CF-P1-v1-A`
- Expected: Strong reasoning + similar accuracy → increase difficulty
- ADAPT decision: `INCREASE_DIFFICULTY` (appropriate)
- Baseline decision: `INCREASE_DIFFICULTY` (appropriate)
- ADAPT evidence: `{'response_id': 'CF-P1-v1-A-CUR', 'answer_status': 'CORRECT', 'reasoning_quality': 'STRONG', 'error_type': 'NONE', 'misconception_signal': None, 'confidence_signal': 'HIGH', 'evidence_strength': 'STRONG', 'diagnostic_confidence': 'HIGH', 'evidence_reliability': 'HIGH', 'polarity': 'POSITIVE'}`
- Baseline diagnosis: Baseline used correctness=CORRECT with heuristic reasons: correct_strong_reasoning_repeated_success

### ADAPT failure (if any)

No matching executed example was found.

## 14. Limitations

- Deterministic keyword analysis, not an LLM tutor.
- One concept (`basic_algebra`) and a small challenge bank.
- CF-P2 cannot match raw accuracy exactly because misconception evidence is expressed as incorrect diagnostic answers.
- Secondary error labels are heuristic.
- This is not a human learning-gain study.

## 15. Conclusion

SUPPORTED: ADAPT met the predefined strong-support pattern on this frozen benchmark.

## 16. Reproducibility information

- Benchmark version: phase1e-v1
- Random seed: 20260813
- Timestamp: 2026-08-14T04:50:42Z
- Python: 3.12.8
- Git commit: unavailable
- Scenario count: 51
