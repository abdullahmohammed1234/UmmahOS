# Judge questions

Answers are honest and technically precise. Do not upgrade Phase 5.

## 1. Why is this actually adaptive?

Because the next challenge is not a fixed sequence. Learner evidence updates a learner state. That state selects an instructional strategy. That strategy selects the next challenge. Changing the evidence, holding the start fixed, changes the decision. That is the counterfactual.

## 2. Why not just use one LLM prompt?

The important distinction isn't the number of prompts.
ADAPT has an explicit state transition.

Learner evidence updates a learner state.
That state determines instructional strategy.
That strategy determines the next challenge.

We then test whether changing the evidence changes
the resulting decision.

## 3. How do you know the learner state is correct?

We don't claim it is a true model of the person. It is the system's current belief, updated from heuristic evidence. We test whether that belief changes coherently with evidence, not whether it matches a hidden mental state.

## 4. How do you handle guessing?

A correct answer with weak reasoning and low confidence is weak evidence of mastery. The engine typically probes or gathers more evidence instead of increasing difficulty. The counterfactual shows this against a strong-reasoning path.

## 5. How do you handle contradictory evidence?

Contradiction raises uncertainty. The strategy layer prefers gathering evidence or probing over a confident INCREASE. Phase 1F included a contradiction metamorphic test.

## 6. What happens with misconceptions?

A misconception signal can move the tutor to PROBE. Repeated misconception evidence can move it to REMEDIATE. Recovery evidence can move it off remediation. The guided demo shows that sequence through the real engine.

## 7. What happens when evidence is insufficient?

The initial strategy is ASSESS / gather evidence. Mastery is not assumed. Sparse or missing reasoning does not get treated as strong understanding.

## 8. How is this different from adaptive testing?

Adaptive testing usually selects the next item to estimate ability from correctness. ADAPT selects an instructional strategy — increase, probe, remediate, maintain — using answer, reasoning, confidence, and misconception signals, then picks a challenge that serves that strategy.

## 9. What does the baseline do?

Phase 1E used a deterministic heuristic tutor that inspects the response but does not maintain ADAPT learner state. Phase 5 defined a linear tutor with a fixed item order for a human comparison that was not run.

## 10. What evidence do you have that it works?

Engineering evidence: appropriateness, counterfactual differentiation, generalization, strategy consistency, and product preservation of engine decisions. See the Technical Evidence page.

We do not have evidence that it improves human learning.

## 11. Did real learners test it?

No consented learners completed Phase 5. Phase 4 usability is also PENDING (0 / 5). Demo scenarios are labeled DEMO SCENARIO and are not human study results.

## 12. Why is Phase 5 inconclusive?

We have not established that yet.

Phase 5 contains a controlled evaluation protocol,
but no consented participants were available,
so the human-learning result is inconclusive.

What we have demonstrated so far is engineering evidence:
the system changes decisions based on learner evidence,
survives adversarial testing, generalizes across a novel
scenario suite, and maintains an auditable causal trace.

## 13. What would you do with more time?

Run Phase 5 with real consented learners. Finish the usability protocol. Expand the challenge bank. Keep the engine frozen until a new research phase is declared, then revisit the documented 1F boundaries with better items rather than recoding old failures.
