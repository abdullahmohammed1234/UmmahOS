# Phase 12 benchmark report

Status: executed (prompt-simulator)
Scenario version: phase12-scenarios-v1
Workflow version: phase12-v1
Seed: 20260819
Model / backend: prompt-simulator / prompt-simulator
Selected prompt: evidence_v3
n scenarios: 100 (development 70, holdout 30)

## Honesty

- This file records a workflow-vs-baseline comparison of evidence extraction and adaptive decisions.
- It is not a learning-gain result. Phase 5 remains INCONCLUSIVE (n = 0).
- Live Gemini is used only when `backend = gemini`. Simulator runs are labeled as such.

## Prompt selection (development)

- evidence_v1 (P-001): score=0.623 validity=0.429 accuracy=0.314 injection=1.000
- evidence_v2 (P-002): score=0.500 validity=0.686 accuracy=0.314 injection=0.000
- evidence_v3 (P-003): score=0.970 validity=1.000 accuracy=0.900 injection=1.000

Selected by frozen criteria phase12-criteria-v1: **evidence_v3**.

## Holdout (single evaluation of the selected prompt)

- Evidence extraction accuracy: 0.8666666666666667
- Structured output validity: 1.0
- Counterfactual sensitivity: 1.0
- ADAPT decision differentiation: 1.0
- Prompt injection robustness: 1.0
- Traceability: 1.0

## Baseline comparison (holdout)

- n: 30
- ADAPT workflow score: 0.6666666666666666
- Single-prompt baseline score: 0.36666666666666664
- Absolute difference: 0.3
- Relative difference: 0.8181818181818182
- McNemar p-value: 0.13739482585580087
- Statistically significant: False
- Note: McNemar p-value is descriptive. n=30 paired scenarios. Difference is not claimed as statistically significant.

