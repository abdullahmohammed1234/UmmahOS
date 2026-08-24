# Final submission checklist

Check items only after they are actually done. Do not fabricate.

---

## Competition files

- [ ] ML Workflow PNG (created from `workflow/WORKFLOW_SPEC.md`; not present in this package)
- [x] Samples document (`samples/ADAPT_SAMPLES_AND_COMPARISON.md` + `.pdf`; fulfills Samples without a video)
- [x] Documentation (`documentation/ADAPT_DOCUMENTATION.md` and supporting files)
- [ ] Final portal upload

---

## Workflow

- [ ] Human input shown
- [ ] Prompt shown (P-003 / evidence_v3)
- [ ] LLM shown
- [ ] Model identified (Gemini; default configurable; live 2.5/3.6 not combined)
- [ ] Evidence extraction shown
- [ ] Validation shown
- [ ] Fallback shown as failure path, not Gemini success
- [ ] AdaptiveTutor shown
- [ ] Strategy shown as an ADAPT decision
- [ ] Challenge selection shown

---

## Samples

- [x] Same cases used for baseline and workflow
- [x] Single-prompt baseline shown (`baseline_v1`)
- [x] ADAPT workflow shown
- [x] Correct-but-uncertain case (A-001 / lucky guess)
- [x] Counterfactual (product `/counterfactual` and/or F-001 vs F-002)
- [ ] Research Mode (optional for document; covered in documentation / demo)
- [x] Results accurately described (no significance claim; no live score)

---

## Documentation

- [x] P-001
- [x] P-002 (injection failure retained)
- [x] P-003
- [x] Evaluation
- [x] Limitations
- [x] Architecture
- [x] Reproducibility
- [x] Security

---

## Demo

- [ ] Gemini path tested **or** fallback path tested with correct label
- [ ] Fallback path tested
- [ ] Browser prepared (no secrets on screen)
- [ ] Sample learner responses prepared
- [ ] Counterfactual prepared
- [ ] Screen recording plan prepared (`samples/SAMPLE_VIDEO_SCRIPT.md`) — optional if Samples document is used
- [ ] No secrets visible

---

## Final verification

- [x] pytest passes — **598 passed** (2026-08-21 submission-prep run)
- [x] offline benchmark passes — 86.7% extraction; 100% validity/injection/traceability; 20/30 vs 11/30; p ≈ 0.137
- [ ] historical results unchanged (do not rewrite `results/phase12/` reports)
- [ ] AdaptiveTutor unchanged
- [ ] P-003 unchanged
- [ ] holdout unchanged
- [x] no API key tracked (`.env` gitignored; not in `git ls-files`)
- [ ] no unsupported claims in PNG, samples document, or pasted portal text

---

## After the PNG exists

- [ ] PNG matches `WORKFLOW_SPEC.md` node list
- [x] Samples document includes same-input single-prompt comparison
- [x] Closing line used: “Gemini interprets the evidence. AdaptiveTutor decides how to adapt.”
