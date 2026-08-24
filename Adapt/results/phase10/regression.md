# Phase 10 regression

Historical engine benchmarks were re-run with `python -m benchmarks.run_no_persist`.

Artifacts under `results/phase1`–`results/phase9` were not rewritten.

| Phase | Result |
| --- | --- |
| 1E | 51/51 appropriateness; 9/9 counterfactual; 51/51 traceability |
| 1F | 39/42 development; 17/18 holdout; ROBUST; gap −1.6 pp |
| 2 | 60/60 strategy appropriateness |
| 3 | 44/44 end-to-end; 294/294 causality; 294/294 consistency |
| 4 | 20/20 task completion; 119/119 engine preservation; 119/119 trace visibility |
| 5 | INCONCLUSIVE; n = 0 |
| 7 | 7 domains; 81 concepts; 21 types; counterfactual preserved |
| 8 | product UX layer; engine preserved |
| 9 | product polish; engine preserved |

Full pytest after Phase 10:

```text
514 passed, 0 failed, 0 skipped
```

Baseline before Phase 10: **492 passed**.
