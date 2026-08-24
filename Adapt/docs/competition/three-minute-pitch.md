# 3-minute spoken pitch

See also `pitch.md` (30 seconds) and `demo-script.md` (click-through).

Target: about 180 seconds. Do not claim learning improvement.

## 0:00–0:30 — Problem

Most AI tutors adapt to the answer.

If you are right, they make the next item harder. If you are wrong, they make it easier.

That hides an important fact: a correct answer can be a guess, and an incorrect answer can be a small slip with a sound method.

ADAPT asks a different question: what does this answer tell us about the learner?

## 0:30–0:55 — ADAPT insight

ADAPT is not “we use more prompts.”

It has an explicit state transition:

Evidence updates a learner state.
That state determines instructional strategy.
That strategy determines the next challenge.

The product promise is: a tutor that adapts to how you learn, not just whether you are right.

## 0:55–1:45 — Live demo

Open the app. Start Learning. Choose Quantum or Mathematics.

Show the challenge: a short question, a quick confidence tap, optional approach. No essay required.

Submit a correct answer with high confidence.

Point to What ADAPT noticed and the adaptation moment: evidence detected, strategy from AdaptiveTutor, the next challenge changes.

Then submit uncertain or misconception evidence and show the strategy change to PROBE or REMEDIATE — whichever the frozen engine actually produces.

Open Research view. Walk the chain: Evidence → State → Strategy → Next Challenge.

## 1:45–2:15 — Counterfactual

Reset. Same starting challenge.

Learner A: strong reasoning, high confidence → INCREASE.

Learner B: weak reasoning, low confidence → a different decision from the same engine.

Say this sentence:

“Same starting point. Different evidence. Different decision.”

That is the core of ADAPT.

## 2:15–2:40 — Technical validation

This is engineering evidence, not a learning-gain study.

Phase 1E: 51/51 appropriateness, 9/9 counterfactual differentiation.

Phase 1F: 39/42 development, 17/18 holdout, ROBUST.

Phase 2: 60/60 strategy appropriateness.

Phase 3: 44/44 end-to-end adaptation; 294/294 causal links.

Phase 4: the product preserved every engine decision in the benchmark.

## 2:40–3:00 — Why it matters + limitations

If tutoring systems only look at correctness, they will treat a lucky guess like mastery and a near-miss like collapse.

ADAPT makes the reason for the next challenge visible.

We have not shown that this improves human learning. Phase 5 has a protocol, but n = 0, so the human result is INCONCLUSIVE.

What we have shown is that the decision changes with the evidence, survives adversarial tests, and leaves an auditable trace.
