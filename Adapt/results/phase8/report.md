# Phase 8 report

**Executed:** 2026-08-15T20:18:43Z  
**Seed:** 20260814  
**Benchmark:** phase8-v1  

This phase is a product UX and explanation layer. AdaptiveTutor, Evidence Analyzer, State Updater, Strategy Engine, Adaptation Engine, and Phase 1E–7 benchmark logic were not modified. Historical result files were not rewritten.

No educational-efficacy claim is made. Phase 5 remains INCONCLUSIVE (n = 0).

---

## Metrics

All values are from real execution (`python -m benchmarks.phase8.runner`).

| ID | Metric | Result | Status |
| --- | --- | --- | --- |
| M8-001 | Navigation completion | complete | PASS |
| M8-002 | Concept accessibility | 50/50 reachable | PASS |
| M8-003 | Challenge completion | 1/1 | PASS |
| M8-004 | Lightweight evidence completion | optional reasoning | PASS |
| M8-005 | Explanation coverage | 4/4 fields | PASS |
| M8-006 | Trace-explanation consistency | consistent with engine | PASS |
| M8-007 | Progress correctness | honest empty/recorded states | PASS |
| M8-008 | Repetition avoidance | 100.0% | PASS |
| M8-009 | Counterfactual preservation | Learner A INCREASE vs Learner B PROBE | PASS |
| M8-010 | Research trace visibility | complete chain | PASS |
| M8-011 | Engine preservation | product GATHER_EVIDENCE → PROBE equals direct AdaptiveTutor | PASS |
| M8-012 | Determinism | identical across two ProductService runs | PASS |

Failures: none.

---

## Tests

```text
python -m pytest
472 passed, 0 failed, 0 skipped
```

Including `tests/phase8/` (22 tests) plus historical Phase 1–7 suites.

---

## Regression (`python -m benchmarks.run_no_persist`)

Historical artifacts were not rewritten (`persist=False`).

| Phase | Result |
| --- | --- |
| 1E | 51/51 appropriateness; 9/9 counterfactual; 51/51 traceability |
| 1F | 39/42 development; 17/18 holdout; ROBUST; −1.6 pp |
| 2 | 60/60 strategy appropriateness |
| 3 | 44/44; 294/294; 294/294 |
| 4 | 20/20; 119/119; 119/119 |
| 5 | human n=0; H1 INCONCLUSIVE; failures [] |
| 7 | M7-001–M7-008 PASS |
| 8 | M8-001–M8-012 PASS |

---

## Counterfactual

Live `AdaptiveTutor` runs, same start:

- Learner A → INCREASE
- Learner B → PROBE

Displayed decisions equal engine decisions.

---

## Usability

**PENDING.** Participants: 0 / 5. See `results/phase8/usability.md`.

Not converted into a fake PASS.

---

## Screenshots

**NOT CAPTURED.** See `results/phase8/screenshots/README.md`.

Visual browser/layout inspection: **NOT EXECUTED**.

---

## Honesty

Phase 5 human learning evaluation remains INCONCLUSIVE (n = 0).

Progress in the product is visit memory while ADAPT is running. It is not a long-term saved learning record and is not evidence that ADAPT improves learning.
