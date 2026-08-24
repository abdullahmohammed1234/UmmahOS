# Phase 5 methodology (frozen before human analysis)

## Design
Within-subject: pre-test → condition A → post-test A → condition B → post-test B.
Condition order is randomized by participant id and seed 20260814.
Group 1: ADAPT then BASELINE. Group 2: BASELINE then ADAPT.

## Conditions
- ADAPT: Phase 4 ProductService wrapping AdaptiveTutor. 4 algebra + 4 fractions steps.
- BASELINE: LinearTutor, frozen 8-item sequence, feedback after each item, no learner-state strategy.

## Scoring
Normalized exact match or listed alias. Missing answers score 0 with status MISSING.
gain = post_test_score - pre_test_score
delta = gain_ADAPT - gain_BASELINE

## Statistics
n < 1: INCONCLUSIVE.
1 ≤ n < 6: exploratory descriptive statistics only.
n ≥ 6: Wilcoxon signed-rank plus bootstrap 95% CI on mean delta; Cohen dz if sd > 0.

## Delayed retention
Optional. If not run: NOT COLLECTED.

## Synthetic data
SYN-A/B/C validate arithmetic of deltas. They are not human results.
