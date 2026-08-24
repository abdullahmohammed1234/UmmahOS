# ADAPT — ML Prompt Engineering submission package

**Project:** ADAPT  
**Track:** ML Prompt Engineering  
**One-sentence description:** ADAPT uses an LLM to interpret learner evidence, while ADAPT's deterministic AdaptiveTutor remains responsible for deciding how to adapt.

**Core innovation:** Prompt-engineered evidence extraction (P-003 / `evidence_v3`) sits in front of a frozen adaptive engine. Gemini interprets evidence. AdaptiveTutor decides how to adapt.

This folder is the repository-side submission package. It is the source of truth for PNG creation, sample comparison, judge demonstration, and written documentation.

---

## Required competition artifacts

The competition requires three artifacts. A fourth portal field, if present, is **not specified** in this repository — confirm on the portal before upload. Do not invent a fourth artifact.

| # | Portal artifact | Repository location | Status |
| --- | --- | --- | --- |
| 1 | ML workflow PNG | Specified by `workflow/WORKFLOW_SPEC.md` | **MANUAL — PNG not created here** |
| 2 | Samples (video / document) | `samples/ADAPT_SAMPLES_AND_COMPARISON.md` (+ PDF) | **Document ready** (fulfills Samples; no video required) |
| 3 | Documentation | `documentation/` | Ready |
| 4 | Unspecified portal field | — | Verify on the competition portal |

A prior workflow image exists at `docs/competition/submission/ml-workflow.png`. Treat it as a draft. The final PNG should be generated from `workflow/WORKFLOW_SPEC.md`.

---

## Samples requirement — document (not video)

The competition accepts:

> Samples: Prepare a video/**document** that shows the use of workflow for sample test cases as compared to using a single prompt approach with the same test cases.

This package fulfills Samples with a **document**, not a video:

| File | Role |
| --- | --- |
| `samples/ADAPT_SAMPLES_AND_COMPARISON.md` | Source of truth (judge-facing) |
| `samples/ADAPT_SAMPLES_AND_COMPARISON.pdf` | Upload-ready PDF rendered from the Markdown |

Supporting detail (optional reading; not the portal Samples artifact):

- `samples/SAMPLE_CASES.md`
- `samples/SINGLE_PROMPT_BASELINE.md`
- `samples/SAMPLE_VIDEO_SCRIPT.md` (legacy recording plan; unused if submitting the document)

Reproduce recorded sample blocks:

```bash
python scripts/run_sample_comparison.py
```

Regenerate the PDF after editing the Markdown:

```bash
python scripts/render_samples_pdf.py
```

---

## MANUAL ARTIFACTS

These files are **not** in the repository and must be created by hand:

1. **ML workflow PNG** — flowchart of human input, P-003, Gemini, validation, fallback, AdaptiveTutor, strategy, next challenge, and explanation.

The Samples artifact is the document above. Do **not** require a video for portal upload when the document is used.

---

## Repository-side artifacts

```text
docs/competition/submission/final/
├── README.md                          ← this index
├── SUBMISSION_CHECKLIST.md
├── workflow/
│   └── WORKFLOW_SPEC.md               ← source of truth for the PNG
├── samples/
│   ├── ADAPT_SAMPLES_AND_COMPARISON.md  ← Samples artifact (source)
│   ├── ADAPT_SAMPLES_AND_COMPARISON.pdf ← Samples artifact (PDF)
│   ├── SAMPLE_VIDEO_SCRIPT.md         ← optional / legacy
│   ├── SAMPLE_CASES.md
│   └── SINGLE_PROMPT_BASELINE.md
├── documentation/
│   ├── ADAPT_DOCUMENTATION.md         ← primary written documentation
│   ├── EVALUATION.md
│   ├── ARCHITECTURE.md
│   └── LIMITATIONS.md
└── demo/
    ├── DEMO_RUNBOOK.md
    ├── JUDGE_DEMO.md
    └── QA.md
```

Related (not the upload package):

- Offline comparison helper: `scripts/run_sample_comparison.py`
- Samples PDF renderer: `scripts/render_samples_pdf.py`
- Frozen Phase 12 report: `docs/phase-12/12.md`
- Freeze audit: `docs/phase-12/12-freeze-audit.md`
- Recorded sample JSON: `docs/competition/submission/samples.md`
- Prompt files: `src/adapt/llm/prompts/`

---

## Core message (use this wording)

> Gemini interprets evidence. AdaptiveTutor decides how to adapt.

Do **not** say:

- “Gemini decides what the learner should do next.”
- “Gemini makes ADAPT smarter.”
- “ADAPT has proven learning gains.”

If the LLM is unavailable, invalid, or times out, the path is `DETERMINISTIC_FALLBACK`. That is not a successful LLM result.

---

## Recommended submission order

1. Read `documentation/LIMITATIONS.md` so claims stay inside the evidence.
2. Generate the ML workflow PNG from `workflow/WORKFLOW_SPEC.md`.
3. Confirm Samples document/PDF: `samples/ADAPT_SAMPLES_AND_COMPARISON.md` / `.pdf`.
4. Run `demo/DEMO_RUNBOOK.md` and confirm Gemini **or** fallback labeling (for live judging).
5. Upload PNG, Samples document/PDF, and `documentation/ADAPT_DOCUMENTATION.md` (plus EVALUATION / ARCHITECTURE / LIMITATIONS as supporting text).
6. Use `demo/JUDGE_DEMO.md` and `demo/QA.md` for live judging.
7. Complete `SUBMISSION_CHECKLIST.md` before sending.

---

## Frozen evaluation snapshot

Offline holdout (prompt-simulator, n = 30, selected prompt P-003 / `evidence_v3`):

- Extraction 86.7% (26/30)
- Validity 100%
- Injection resistance 100%
- Traceability 100%
- Workflow 20/30 vs single-prompt baseline 11/30
- McNemar p ≈ 0.137 — **not statistically significant**

Phase 5 remains **INCONCLUSIVE (n = 0)**. No learning-gain claim. No full live Gemini or NVIDIA holdout score is claimed.
