# Judge demo script (2–3 minutes)

**Superseded for the ML Prompt Engineering video:** `docs/competition/submission/final/demo/JUDGE_DEMO.md` and `docs/competition/submission/final/samples/SAMPLE_VIDEO_SCRIPT.md`.

Deterministic. Uses `AdaptiveTutor`. No API key.

```bash
python -m app
cd frontend
npm run dev
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000). The Python server on port 8765 is the API. Next.js proxies `/api` to it.

Optional CLI: `python demo/run_competition_demo.py`, `python demo/run_phase9_demo.py`, or `python demo/run_phase11_demo.py`.

These are demonstrations of system behavior, not human study results.

Central sentence:

> ADAPT doesn't just look at whether the answer was right. It looks at the evidence behind the answer and changes what comes next.

## 0:00–0:20 — Landing

Show:

- **ADAPT**
- **Learn differently.**
- “An AI tutor that adapts to how you learn, not just whether you are right.”
- Start learning / See how ADAPT adapts
- Answer → ADAPT notices → ADAPT adapts

Say: ADAPT doesn't just look at whether the answer was right. It looks at the evidence behind the answer and changes what comes next.

## 0:20–0:45 — Choose

Click **Start learning**. Show the seven subjects. Open **Quantum** (or Mathematics). Choose a concept.

## 0:45–1:20 — Answer

Answer the challenge. Tap **Guessing / Unsure / Confident**. Optionally tap an approach chip. Long typing is optional.

Click **Continue**.

## 1:20–1:50 — ADAPT noticed

Stay on feedback.

Walk:

1. Concise result
2. What ADAPT noticed
3. The adaptation moment (**ADAPT ADAPTED**, then the trace-backed next move)
4. Why this question?
5. Here’s what’s next

Do not invent the strategy. Read what the product shows from the engine.

## 1:50–2:10 — Second challenge

Continue. Show that the next question changed. If ADAPT revisits an idea, say: “That's intentional — let's try this idea from another angle.”

## 2:10–2:30 — Research Mode

Turn on **Research Mode** in the header, or open `/research`.

Walk the real trace:

Evidence → Learner State → Strategy → Next Challenge

## 2:30–3:00 — Counterfactual

Open **Counterfactual**.

Same start. Different evidence.

- Learner A: strong reasoning, high confidence → whatever `AdaptiveTutor` returns (typically INCREASE)
- Learner B: weak reasoning, low confidence → a different engine decision (typically PROBE)

Say: “Same starting point. Different evidence. Different decision.”

Final line:

“ADAPT doesn't just look at whether the answer was right. It looks at the evidence behind the answer and changes what comes next.”

If asked about learning improvement: Phase 5 is INCONCLUSIVE, n = 0.
