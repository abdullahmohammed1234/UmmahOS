# Phase 10 — Safety & Synthetic Evaluation

Phase 10 adds a **reproducible synthetic safety/evaluation layer** for Community Shield.

It does **not** redesign Phases 1–9, does **not** start Phase 11, and does **not** introduce automatic enforcement or live hate-speech accuracy claims.

## Objective

Answer, with synthetic data only:

1. Does UmmahOS preserve incident context?
2. Does AI identify uncertainty appropriately?
3. Are uncertain cases routed to human review?
4. Does the system protect private information?
5. Does the system produce an actionable evidence package?
6. Does the system preserve and track outcomes?
7. Does the system avoid automatically making harmful or unsupported claims?

## Central safety principle

```text
AI uncertainty → human review
evidence → human decision → outcome
```

**Not:**

```text
AI uncertainty → automatic accusation/action
AI → automatic enforcement
```

AI remains advisory. Human review remains authoritative.

## Synthetic dataset methodology

- Versioned dataset: `SyntheticDataset` (`v1.0.0`)
- Location: `backend/app/Evaluation/CommunityShield/SyntheticDataset.php`
- Fixture pointer: `backend/tests/Fixtures/CommunityShieldEvaluation/`
- Export artifacts: `docs/evaluation/synthetic_cases.json`

**Synthetic only:**

- Fictional authors (`FictionalUserA`, …)
- Fictional communities (`ExampleCommunity`)
- Placeholder URLs (`https://example.invalid/...`)
- Abstract harm descriptions (no real slurs, victims, accounts, or personal data)
- Privacy canaries (`PRIVATE_CANARY_001`, …) for leakage tests

## Seven scenario categories

| Category | Focus |
|----------|--------|
| Explicit | Abstract direct targeting patterns |
| Coded | Context-dependent / euphemistic signals |
| Visual | Image/video/meme **descriptions** (no harmful media bytes) |
| Relational / Reply Swarm | Meaning depends on ordered replies / related items |
| Misinformation | Unverified claims must not become “facts” |
| Synthetic AI Content | AI-generated / deepfake-style descriptions |
| Ambiguous / Uncertain | Correct behavior is uncertainty + human attention |

Coverage spans X, YouTube, TikTok, Reddit, Discord, Telegram, WhatsApp, and Other; public / group / private visibility.

## Evaluation architecture

```text
SyntheticDataset
      ↓
CommunityShieldEvaluationRunner
      ↓
materialize incident → FakeAnalysisProvider → human review
      → evidence package → outcome lifecycle → privacy checks
      ↓
CommunityShieldEvaluationResult (+ aggregate report)
      ↓
php artisan community-shield:evaluate
```

Contracts:

- `CommunityShieldEvaluationCase`
- `CommunityShieldEvaluationResult`

Deterministic mode uses the existing `FakeAnalysisProvider`.  
Optional `--live-ai` is demo-only, still synthetic-input-only, and is **not** the main safety benchmark.

> **The safety properties are enforced by the application architecture and regression tests, rather than depending on one particular LLM response.**

## Safety invariants

| Invariant | Pass condition |
|-----------|----------------|
| Context preservation | Platform, content type, visibility, original item, timestamps, context, ordered replies, related items, language, reporter notes survive pipeline + package |
| Uncertainty handling | Analysis includes signals, hypothesis classification, confidence, uncertainty, recommended action |
| Human routing | Uncertain/ambiguous cases enter human review; AI cannot confirm/resolve/escalate |
| Privacy protection | Cross-org isolation, canary scoping, private visibility representation |
| Evidence reporting | Package sections complete; `automatic_submission: false` |
| Outcome tracking | `reported → under_review → decision → outcome` + immutable history + unverified default |
| Harmful-claim avoidance | Observed evidence ≠ confirmed fact; AI ≠ human decision; outcome ≠ auto-verified |

## Privacy tests

Feature coverage in `CommunityShieldEvaluationPrivacyBoundaryTest`:

- Cross-org AI / evidence / outcome access blocked
- Member cannot access another user’s report
- Reviewer notes / AI metadata absent from member my-reports payload
- Evidence export keeps canaries out of reporting-route guidance
- Unauthorized appeals blocked

## AI uncertainty tests

- Ambiguous/misinformation fixtures expect high/moderate uncertainty
- High uncertainty must not present as confident established harmful fact
- AI analysis does not mutate incident status, escalation, classification, or review outcome
- Analysis package has no human-decision / final-outcome fields

## Human-review tests

Runner exercises:

`open → reviewing → uncertain | confirm | close` (+ optional `request context`)

Principle validated: **AI uncertainty → human attention**, not automatic accusation.

## Evidence / reporting tests

- JSON package structural completeness
- PDF render samples (including Arabic/Unicode synthetic text)
- Reporting guidance remains informational (`automatic_submission: false`)

## Outcome tests

Full synthetic lifecycle with:

- unverified default verification
- append-only status history
- decision separate from outcome
- appeal preserving original external report

## Academy / ADAPT safety tests

`CommunityShieldAdaptEducationSafetyTest` (uses `FakeAdaptClient`):

- Only confirmed incidents → LearningPattern
- Private incident fields not copied into learner content
- `source_incident_id` hidden from learner recommendation payloads
- ADAPT receives sanitized educational scenario content
- Adapt sessions remain owner-scoped

## Command

```bash
php artisan community-shield:evaluate
php artisan community-shield:evaluate --live-ai   # optional demo only
```

Exit non-zero on critical safety failures.

## Artifacts

- `docs/evaluation/SYNTHETIC_EVALUATION.md`
- `docs/evaluation/synthetic_cases.json`
- `docs/evaluation/evaluation-results.json`
- `backend/resources/evaluation/community_shield/synthetic_cases.json`

## Results

Deterministic evaluation (`php artisan community-shield:evaluate`):

- Scenarios: **42**
- Categories: all seven **PASS**
- Safety invariants: all seven **PASS**
- Critical safety failures: **0**
- RESULT: **PASS**

Artifacts are written to `docs/evaluation/` on each successful CLI run.

## Limitations

- This is a **synthetic safety evaluation**, not proof of real-world model accuracy.
- Deterministic mode does not call Gemini.
- Optional live AI mode still cannot justify accuracy percentage claims.
- Synthetic scenarios cannot prove every human reviewer will decide correctly.
- No automatic external platform reporting/enforcement is introduced or validated as desirable.

## What this evaluation does NOT prove

- It does **not** prove “AI detects hate speech with X% accuracy.”
- It does **not** replace human judgment.
- It does **not** authorize automated moderation.

Instead it verifies that the application preserves context, represents uncertainty, keeps AI advisory, routes decisions to humans, protects privacy/authorization boundaries, and avoids specified harmful-claim failure modes.

## Out of scope / not started

**Phase 11 was not started.**

MSA Platform/ remains untouched.
