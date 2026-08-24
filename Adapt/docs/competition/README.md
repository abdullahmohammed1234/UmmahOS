# Competition documentation

Track: **ML Prompt Engineering**

The final repository-side submission package is:

**[`docs/competition/submission/final/`](submission/final/README.md)**

Use that folder for PNG creation, sample-video recording, judge demonstration, and portal upload.

## What belongs where

| Location | Role |
| --- | --- |
| `docs/competition/submission/final/` | **Final** judge-facing submission package |
| `docs/competition/submission/` | Prior Phase 12 drafts (workflow notes, recorded samples, prompts, limitations) |
| `docs/competition/*.md` | Earlier product-demo notes (pitch, Phase 6 checklist, screenshot guide) |
| `docs/phase-12/` | Internal Phase 12 technical reports and freeze audit |
| `results/phase12/` | Historical benchmark artifacts — do not rewrite |

Do not treat prior drafts as the upload package. If two documents disagree, prefer `submission/final/` plus `docs/phase-12/12-freeze-audit.md`.

## Known portal artifacts

The competition requires:

1. ML workflow PNG
2. Samples (video/document comparing the workflow with a single-prompt approach)
3. Documentation

A fourth portal field, if any, is **not specified** in this repository. Do not invent one. Confirm on the competition portal before upload.

## Manual artifacts still required

1. ML workflow PNG — create from `submission/final/workflow/WORKFLOW_SPEC.md`
2. Samples / demo video — record from `submission/final/samples/SAMPLE_VIDEO_SCRIPT.md`
