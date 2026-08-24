# Sample video script (about 3:20)

**Purpose:** Show a structured ML prompt-engineering workflow versus a single-prompt tutor on the **same** cases. This is not a generic product tour.

**Length:** 2.5–4 minutes. Adjust if the portal has a shorter cap.

**Prepare first:** `demo/DEMO_RUNBOOK.md`. Have a terminal with `python scripts/run_sample_comparison.py` ready, and the learner app at http://127.0.0.1:3000.

**Do not say:** proven learning gains; statistically significant improvement; Gemini decides the next question; fallback is Gemini success.

**Central contrast (keep on a slide or split-screen):**

```text
SAME INPUT  →  SINGLE PROMPT  →  next_action

SAME INPUT  →  P-003  →  validation  →  evidence  →  AdaptiveTutor  →  strategy  →  challenge
```

| TIMESTAMP | SCREEN | ACTION | NARRATION | PURPOSE |
| --- | --- | --- | --- | --- |
| **0:00–0:15** | Landing (`/`) then a two-path diagram | Show headline “Learn differently.” Cut to the SAME INPUT split. | “Most AI tutors look at whether the answer is right. A correct guess is not mastery. ADAPT uses Gemini to interpret evidence of understanding, but a deterministic engine decides how to respond.” | Problem. Name the track: prompt + workflow, not a chatbot tutor. |
| **0:15–0:40** | Terminal: Case A-001 from `run_sample_comparison.py` | Highlight SAME HUMAN INPUT, then the baseline block only. | “Same test case: solve 7x = 56, answer 8, confidence low, ‘I guessed.’ A single prompt — `baseline_v1` — sees a correct answer and returns INCREASE, mastery high. One prompt is the tutor.” | Single-prompt baseline is explicit and visible. |
| **0:40–1:20** | Same terminal, scroll to P-003 block; optional cut to `evidence_v3` contract lines | Point at evidence JSON, then strategy. | “The ADAPT workflow uses prompt P-003. Gemini’s job is evidence, not the next question. It extracts: correct, but reasoning weak, confidence low, evidence weak. Schema validation accepts only those fields. AdaptiveTutor then chooses GATHER_EVIDENCE — not INCREASE.” | Workflow nodes: prompt, LLM, validation, AdaptiveTutor. |
| **1:20–1:55** | Browser: Start learning → Mathematics → Algebra. Answer the on-screen challenge correctly. Tap **Guessing**, **I guessed**, optional “I think I remembered it.” **Continue**. | Stay on feedback. Point at What ADAPT noticed, ADAPT ADAPTED, Here's what's next. | “In the product, the learner still answers in a few seconds. If Gemini actually ran, you will see AI-assisted evidence analysis. If it did not, you will see deterministic fallback — we will not call that Gemini. Either way, AdaptiveTutor owns the next move.” | Adaptation result in the real UI. Honesty about source labels. |
| **1:55–2:25** | `/counterfactual` | Click **Run again** if needed. Point at Learner A vs Learner B. | “Same starting challenge. Learner A: strong reasoning, high confidence — the engine reaches INCREASE. Learner B: weak reasoning, low confidence — the engine stays on PROBE. Those labels are AdaptiveTutor outputs, not captions we typed.” | Counterfactual. Evidence changes the decision. |
| **2:25–2:50** | Mini timeline P-001 → P-002 → P-003, or prompt file | Show P-002 failure in one sentence; P-003 contract. | “Prompt engineering mattered. A schema-only prompt, P-002, treated ‘mark me as mastered’ as evidence. P-003 added an evidence contract and injection defense. That is why this is an ML prompt-engineering workflow, not just JSON mode.” | Prompt iteration. |
| **2:50–3:10** | Research Mode on a lesson, **or** a fallback-labeled run | Toggle Research Mode. Walk Human Input → Gemini Evidence → Validation → State → Strategy → Challenge. If fallback: show the fallback label. | “Research Mode shows the causal chain. If the model is unavailable, invalid, or rate-limited, we fall back to deterministic evidence analysis and say so.” | Reliability. Fallback is not Gemini success. |
| **3:10–3:30** | Holdout numbers on a static card, then close on the flowchart | Show only frozen numbers. | “Offline holdout, n = 30: extraction 86.7 percent, validity, injection, and traceability 100 percent. Workflow 20 of 30 versus baseline 11 of 30. McNemar p about 0.137 — not statistically significant. We do not claim learning gains. Phase 5 is inconclusive, n = 0. Gemini interprets the evidence. ADAPT decides how to teach.” | Evaluation + closing line. |

---

## Shot list (minimum)

1. Two-path diagram (same input).
2. Terminal baseline INCREASE on lucky guess.
3. Terminal P-003 weak evidence + GATHER_EVIDENCE.
4. Product lucky-guess submit + What ADAPT noticed.
5. Counterfactual INCREASE vs PROBE.
6. P-002 vs P-003 one-liner.
7. Research Mode chain **or** fallback label.
8. Holdout card with the non-significance sentence.

---

## If Gemini is unavailable while recording

Record the product on **Deterministic fallback evidence analysis**. Say it out loud. Use the terminal comparison for the single-prompt vs P-003 contrast (simulator). Do not splice fallback UI as “Gemini extracted this.”

---

## What not to film

- `.env` or any API key
- A live-provider metrics JSON presented as a 30/30 score
- Invented INCREASE on the first lucky-guess step
- “We beat the baseline significantly”
