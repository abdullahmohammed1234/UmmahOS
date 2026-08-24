# Phase 11 metrics

All metrics below are based on executed checks. Nothing here is a usability score or a learning-gain claim.

| ID | Metric | Result |
| --- | --- | --- |
| M11-001 | Visual navigation integrity | **PASS** — landing, subjects, seven domains, design tokens present |
| M11-002 | Challenge interaction integrity | **PASS** — answer, confidence 1/3/5, approach chips, optional explanation; submit goes to API |
| M11-003 | Feedback/explanation integrity | **PASS** — noticed and why-this-question are `from_trace` |
| M11-004 | Adaptation visualization integrity | **PASS** — AdaptationMoment shows ADAPT ADAPTED + trace-backed copy |
| M11-005 | Counterfactual preservation | **PASS** — live AdaptiveTutor; Learner A INCREASE, Learner B PROBE |
| M11-006 | Research Mode preservation | **PASS** — header toggle, `/research`, in-lesson ResearchTrace |
| M11-007 | Responsive layout integrity | **PASS** — 1280×800 and 360×740 captured; stacked mobile landing |
| M11-008 | Accessibility-critical checks | **PASS** — skip link, focus rings, reduced motion, labeled controls, button contrast in CSS |
| M11-009 | Browser console/error integrity | **PASS** — no pageerror events during Playwright capture |
| M11-010 | Screenshot capture | **CAPTURED** — `results/phase11/screenshots/` |
| M11-011 | Deterministic demo | **PASS** — `python demo/run_phase11_demo.py` exit 0; seed 20260819 |
| M11-012 | Historical regression preservation | **PASS** — `python -m pytest` 540 passed; `python -m benchmarks.run_no_persist` reproduced Phase 1E–9 expected results |

## Bundle (production build)

Landing first-load JS: 151 kB (shared 102 kB + page). Learn route 156 kB first load. Three.js remains Quantum-only (lazy).

## Not measured

| Item | Status |
| --- | --- |
| Usability with consented learners | **PENDING (n = 0)** |
| Educational efficacy | **not claimed**; Phase 5 remains INCONCLUSIVE (n = 0) |
