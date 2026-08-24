# Phase 12 video script (~3:00)

**Superseded by** `docs/competition/submission/final/samples/SAMPLE_VIDEO_SCRIPT.md` (explicit same-input single-prompt comparison).

Purpose: show a structured ML/LLM workflow, not “we called Gemini.”

---

## 0:00–0:20 — Introduce

On screen: ADAPT landing, then the learner chain.

> ADAPT doesn't just ask whether you were right. It tries to understand how you arrived there.

> Gemini interprets the learner. ADAPT decides how to teach.

Do not say ADAPT has been proven to improve learning.

---

## 0:20–0:50 — Learner input

Open a lesson. Show a short challenge.

Submit quickly:

- Answer
- Confidence chip
- Approach chip
- Optional one-line note

> The learner can answer in a few seconds. We do not force a long essay.

Point at the four fields. This is **human input**.

---

## 0:50–1:20 — Gemini evidence extraction

Enable Research Mode.

Show:

- Human Input node
- Gemini Evidence node
- Prompt version (`evidence_v3`)
- Structured JSON fields: correctness, reasoning quality, confidence, evidence strength

> This model is Google Gemini. Its job is evidence extraction — not choosing the next question.

If the run used fallback, say so. Do not label fallback as Gemini.

---

## 1:20–1:50 — Evidence → State → Strategy → Challenge

Stay in Research Mode. Walk the rest of the chain:

- Validation
- Learner state (mastery / uncertainty)
- Strategy from AdaptiveTutor
- Next challenge id

> Validation rejects malformed output. The frozen engine still owns state, strategy, and selection.

---

## 1:50–2:20 — Counterfactual

Open **Same question. Different learner.**

Learner A: correct, strong reasoning, high confidence → engine **INCREASE** (after the live trajectory).  
Learner B: correct, weak reasoning, low confidence → engine **PROBE**.

> Same starting challenge. Different evidence. Different adaptation. Those strategies are AdaptiveTutor outputs, not captions we typed.

---

## 2:20–2:50 — Baseline comparison

Show one paired sample (lucky guess or injection) from `samples.md`:

- Baseline: one prompt says INCREASE
- Workflow: weak/insufficient evidence, ADAPT gathers or probes

> A conventional single prompt tries to tutor in one shot. Our workflow extracts evidence, validates it, then lets a tested adaptive engine decide.

Mention honestly: the frozen holdout difference is **not statistically significant** (n = 30). Do not oversell.

---

## 2:50–3:00 — Close

Return to the flowchart.

> The LLM interprets the learner. ADAPT decides how to teach.

Cut.
