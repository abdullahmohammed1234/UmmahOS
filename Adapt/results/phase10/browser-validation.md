# Phase 10 browser validation

Status: **EXECUTED**

Date: 2026-08-16  
Frontend: `http://127.0.0.1:3000` (Next.js 15.5.12 production)  
API: `http://127.0.0.1:8765`  
Tool: Playwright Chromium, 1280×800 and 360×740

## Routes visited

- `/`
- `/subjects`
- `/subjects/quantum`
- `/learn?session=…` (from Superposition)
- `/how-it-works`
- `/research`
- `/counterfactual`
- `/progress`

## Results

| Check | Result |
| --- | --- |
| Page JavaScript exceptions | none |
| Failed API requests | none observed |
| Broken navigation | none |
| Missing assets | none |
| Landing / subjects / challenge / feedback / counterfactual / quantum | rendered |
| Narrow viewport (360×740) landing | rendered |

## Console

No `pageerror` events.

Warnings (not treated as application failures):

- `THREE.Clock: This module has been deprecated` on the Quantum page (dependency warning from Three.js / Drei).
- WebGL `GPU stall due to ReadPixels` while capturing the Quantum canvas (driver/performance notice during screenshot).

Request aborts of the form `/subjects/…?_rsc=…` `net::ERR_ABORTED` occurred during fast navigation. These are cancelled Next.js RSC prefetches, not missing pages.

## Conclusion

**PASS** for executed visual/browser inspection. Screenshots stored in `results/phase10/screenshots/`.
