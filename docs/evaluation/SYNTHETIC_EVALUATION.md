# Community Shield Synthetic Safety Evaluation

> **SYNTHETIC EVALUATION** — Not real incidents. Not a model-accuracy benchmark.

## Dataset design

- Dataset version: `1.0.0`
- Scenarios: 42
- Mode: `deterministic_fake_provider`
- All cases use fictional placeholders (`FictionalUserA`, `ExampleCommunity`, `https://example.invalid/...`).
- Harmful material is described abstractly; real slurs, victims, and accounts are never included.

## Why synthetic examples are used

The evaluation verifies **application safety properties** across the Community Shield chain.
It does not measure real-world hate-speech detection accuracy of any model.

## Categories tested

- **explicit**: PASS (6/6)
- **coded**: PASS (6/6)
- **visual**: PASS (6/6)
- **relational**: PASS (6/6)
- **misinformation**: PASS (6/6)
- **synthetic_ai**: PASS (6/6)
- **ambiguous**: PASS (6/6)

## Safety invariants

- context preservation: **PASS**
- uncertainty handling: **PASS**
- human routing: **PASS**
- privacy protection: **PASS**
- evidence reporting: **PASS**
- outcome tracking: **PASS**
- harmful claim avoidance: **PASS**

## Results

- Overall: **PASS**
- Critical safety failures: 0
- Finished at: 2026-08-23T23:31:57+00:00

## Failures

None.

## Limitations

- Deterministic mode uses `FakeAnalysisProvider`, not live Gemini.
- Synthetic scenarios cannot prove real-world classifier performance.
- Optional `--live-ai` mode is demo-only and still uses synthetic inputs only.

## What this evaluation does NOT prove

- It does **not** prove AI detects hate speech with any accuracy percentage.
- It does **not** prove humans will always reach the correct review decision.
- It does **not** authorize automatic enforcement or external platform submission.

This synthetic evaluation verifies application safety properties (context preservation, uncertainty representation, human authority, privacy isolation, and no automatic enforcement). It is NOT a claim of real-world hate-speech detection accuracy.
