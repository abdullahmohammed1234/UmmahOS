# Judge demonstration

One page. Read this before a live judging session.

---

## 10-second pitch

ADAPT uses Gemini to interpret evidence of learner understanding, but a deterministic adaptive engine decides how to respond.

---

## 30-second explanation

The learner submits an answer, confidence, and optional reasoning. Prompt P-003 asks Gemini for evidence — not for the next question. Schema validation rejects tutoring decisions leaked in JSON. AdaptiveTutor updates learner state, chooses a strategy, and picks the next catalog challenge. If Gemini fails, we fall back to deterministic evidence analysis and say so. We have not shown learning gains. Phase 5 is inconclusive, n = 0.

---

## 2-minute demo

1. Open http://127.0.0.1:3000.
2. **Start learning** → Mathematics → Algebra.
3. Submit a **correct** answer with **Guessing** and **I guessed**.
4. Point to **What ADAPT noticed** (not treated as mastery).
5. Point to **ADAPT ADAPTED** and the next challenge.
6. Toggle **Research Mode** — walk evidence → state → strategy → challenge.
7. Open **Counterfactual** — Learner A INCREASE vs Learner B PROBE (read the on-screen engine labels).
8. If asked about single-prompt: show Case A from `python scripts/run_sample_comparison.py` (baseline INCREASE vs workflow GATHER_EVIDENCE).

---

## Strongest scenario

Correct answer + “I guessed.”

Correctness-only tutors raise difficulty. ADAPT should gather or probe, not INCREASE, on that evidence.

---

## Strongest counterfactual

Same start. Strong reasoning / high confidence vs weak reasoning / low confidence.

Recorded product trajectory: INCREASE vs PROBE after three steps. Say: “Same starting point. Different evidence. Different decision.”

---

## Three numbers to mention

Use only:

1. **86.7%** extraction (offline holdout, n = 30)
2. **100%** validity, injection resistance, and traceability
3. Optionally: **20/30** vs **11/30**, McNemar **p ≈ 0.137** — **not statistically significant**

Do not mention a live Gemini percentage.

---

## One limitation to volunteer

Live provider holdouts were incomplete due to provider constraints. Offline simulator results are the reproducible quantitative evidence.

---

## Closing line

Gemini interprets the evidence. ADAPT decides how to teach.
