# ADAPT

Judge-facing documentation for the ML Prompt Engineering track.

**One line:** Gemini interprets evidence. AdaptiveTutor decides how to adapt.

---

## Executive Summary

ADAPT is an evidence-driven adaptive tutor. A learner submits an answer, a confidence rating, and optional reasoning. An LLM workflow (prompt P-003 / `evidence_v3`) interprets that input as structured evidence. Schema validation accepts or rejects the model output. A frozen deterministic engine, AdaptiveTutor, then updates learner state, chooses an instructional strategy, and selects the next challenge from a finite catalog.

The LLM does not choose INCREASE, PROBE, or REMEDIATE. If the model is unavailable, invalid, or times out, ADAPT uses labeled `DETERMINISTIC_FALLBACK` and continues.

This is a prompt-engineering and systems result. It is not a learning-gain study.

---

## Problem

Most AI tutors adapt to correctness. Right → harder. Wrong → easier.

That policy cannot see:

- a correct answer that was guessed
- an incorrect answer that used a sound method with an arithmetic slip
- a conceptual mix-up that looks like a random error
- learner-directed text that tries to force “mark me as mastered”

ADAPT asks: **what does this response provide evidence of?**

---

## Why Correctness Is Not Enough

Correctness is one field. Mastery is not that field.

Case A in the sample set is a correct lucky guess. A single-prompt tutor records `INCREASE`. The P-003 workflow records weak evidence; AdaptiveTutor gathers more evidence instead of raising difficulty.

That distinction is the product promise and the competition comparison.

---

## The ML Prompt Engineering Workflow

```text
Human input → P-003 → Gemini (evidence) → validation
        → AdaptiveTutor → state → strategy → next challenge → explanation
```

Failure path: LLM error → `DETERMINISTIC_FALLBACK` → deterministic analyzer → AdaptiveTutor.

Full node specification: `../workflow/WORKFLOW_SPEC.md`.

---

## Human Input

Required in the learner UI:

- Answer
- Confidence: **Guessing / Unsure / Confident**

Optional:

- Approach chips (I guessed, I worked it out, …)
- “Want to explain? Optional”

Human involvement is necessary because those signals are not implied by the answer string.

---

## Prompt P-003 / evidence_v3

File: `src/adapt/llm/prompts/evidence_v3.txt`.

The prompt states that the model is an **evidence extractor**. It must not tutor and must not choose a strategy. Learner text is untrusted data. A correct answer is not automatic mastery. Errors are classified. Ambiguity may be `insufficient` evidence. `supporting_evidence` must be grounded in the input.

Selected on a frozen development set (n = 70) before holdout. Holdout was not used to rewrite the prompt.

---

## Gemini Evidence Interpretation

Primary competition LLM: **Google Gemini**.

Repository default model: `gemini-2.0-flash` via `GEMINI_MODEL`. Live integration was exercised on Gemini 2.5 Flash and Gemini 3.6 Flash; those attempts must not be combined into one live score. Offline quantitative evaluation used a prompt-conditioned simulator.

Gemini’s job: fill the evidence schema.  
Gemini’s non-job: pick the next question.

---

## Schema Validation

The validator requires the evidence fields and legal enums. It rejects adaptive-decision keys and strategy tokens. Failure code: `LLM_VALIDATION_FAILURE`. Invalid JSON never becomes learner state.

---

## Deterministic Fallback

Timeouts, missing keys, rate limits, and invalid output use the existing deterministic `EvidenceAnalyzer`. The product labels this **Deterministic fallback evidence analysis**. It is not presented as Gemini success.

---

## AdaptiveTutor

AdaptiveTutor receives validated (or fallback) evidence and remains responsible for:

- learner-state update
- strategy
- challenge selection

It is deterministic given seed and evidence. Phase 12 injected an optional LLM analyzer; it did not replace the engine.

---

## Strategy Selection

Strategies such as INCREASE, PROBE, REMEDIATE, MAINTAIN, and GATHER_EVIDENCE are AdaptiveTutor decisions. The first step often gathers evidence before committing to INCREASE or REMEDIATE. That is frozen policy, not an LLM choice.

---

## Challenge Selection

Next items come from a finite catalog through the existing selector. Gemini cannot emit `next_challenge`. Questions are not generated at runtime.

---

## Research Mode

Header toggle or `/research`. Shows the live causal chain: evidence → state → strategy → next challenge, including workflow nodes and evidence source when the LLM path ran. It does not change decisions and does not expose secrets.

---

## Counterfactual Demonstration

`/counterfactual` — “Same question. Different learner.”

Same start. Strong/high-confidence evidence versus weak/low-confidence evidence. Recorded three-step engine outcomes: INCREASE versus PROBE. Strategies are live AdaptiveTutor outputs.

---

## Prompt Engineering Iteration

### P-001

Minimal instruction (`evidence_v1`). Development: validity 42.9%, extraction 31.4%, injection 100%. Weighted score 0.623.

### P-002

Schema-only JSON (`evidence_v2`). Validity rose (68.6%). Injection robustness **0/7**. Learner-directed content could be treated as evidence. Structured output without a contract is not automatically safe.

### P-003

Contract + schema + injection defense + no strategy (`evidence_v3`). Development score 0.970. Selected. Holdout evaluated once.

---

## Evaluation

See `EVALUATION.md` for the full table.

Offline holdout n = 30, selected prompt P-003:

- Extraction 86.7%
- Validity / injection / traceability 100%
- Workflow 20/30 vs baseline 11/30
- McNemar p ≈ 0.137 — **not statistically significant**

---

## Offline Holdout

Primary reproducible quantitative evaluation. Backend `prompt-simulator`, seed `20260819`. Command: `python -m benchmarks.phase12.runner --no-persist`.

---

## Live Provider Testing

Live Gemini integration was successfully exercised, but complete live holdout evaluation was blocked by provider quota/rate limits. No full live Gemini score is claimed. Gemini 2.5 and 3.6 attempts are not combined.

Live NVIDIA validation was incomplete because representative inference requests timed out (`meta/llama-3.3-70b-instruct`). That is not an extraction accuracy of 0%. NVIDIA and Gemini data are not combined.

---

## Limitations

Phase 5 remains INCONCLUSIVE (n = 0). No learning-gain claim. See `LIMITATIONS.md`.

---

## Reproducibility

```bash
python -m pytest
python -m benchmarks.phase12.runner --no-persist
python scripts/run_sample_comparison.py
```

Live API reproducibility is not claimed: provider quotas and timeouts blocked complete live holdouts.

---

## Security

`.env` is gitignored. Keys are not in source. Research Mode does not display secrets. Do not film API keys.

---

## Conclusion

ADAPT is a constrained LLM workflow around a tested adaptive engine. Prompt P-003 extracts evidence; validation enforces the contract; AdaptiveTutor still teaches.

Gemini interprets the evidence. ADAPT decides how to teach.
