# Technical summary

ADAPT is a deterministic adaptive tutoring workflow.

Learner response → Evidence Analyzer → Learner State → Strategy Engine → Challenge Selector → next challenge.

The Phase 4/6 product is a thin UI over `AdaptiveTutor`. It does not reimplement adaptation.

## Frozen engine

Do not describe prompt-count as intelligence. The distinction is an explicit state transition that can be tested: changing evidence changes the decision.

No external LLM is required for the judge demo.

Seed: `20260814`.

## Engineering results

Transcribed from historical artifacts. Not recomputed as a new claim.

**Phase 1E**
- 51/51 appropriateness
- 9/9 counterfactual differentiation
- 51/51 traceability

**Phase 1F**
- 39/42 development
- 17/18 holdout
- ROBUST
- generalization gap −1.6 pp

**Phase 2**
- 60/60 strategy appropriateness

**Phase 3**
- 44/44 end-to-end adaptation
- 294/294 state-to-strategy causality
- 294/294 strategy-to-challenge consistency

**Phase 4**
- 20/20 task completion
- 119/119 engine preservation
- 119/119 trace visibility

**Phase 5**
- Human learning evaluation: INCONCLUSIVE
- n = 0

These numbers measure decision behavior. They do not measure learning gain.

## How guessing is handled

A correct answer with weak reasoning and low confidence is not treated as strong mastery evidence. The usual result is probe or gather-evidence rather than increase-difficulty. That difference is demonstrated in the counterfactual.

## How misconceptions are handled

A misconception signal can move the strategy to PROBE or REMEDIATE depending on persistence and the rest of the state. Repeated misconception evidence is required before remediation becomes sticky.

## Baseline

Phase 1E compared ADAPT to a correctness-oriented heuristic tutor that does not maintain ADAPT learner state.

Phase 5 defined a separate linear baseline tutor for a human study that was not executed (n = 0).
