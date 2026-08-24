# Single-prompt baseline

The competition requires comparison against a **single-prompt** approach on the **same** learner test cases.

This baseline already exists in the repository. It is not a hidden second copy of ADAPT.

---

## What the baseline is

```text
Human learner input
+
single prompt (baseline_v1)
    ↓
LLM
    ↓
direct assessment / recommendation
    { next_action, mastery, message, reason }
```

**Code:** `src/adapt/llm/baseline.py` (`SinglePromptBaseline`)  
**Prompt:** `src/adapt/llm/prompts/baseline_v1.txt`  
**Prompt ID:** `baseline_v1`  
**Architecture flag:** `single_prompt`

It does **not** use:

- P-003 / `evidence_v3`
- AdaptiveTutor
- schema validation of evidence fields
- learner-state update
- strategy engine
- challenge selector
- additional hidden prompts

That is the fair “one prompt tutors” control.

---

## Exact baseline prompt

From `src/adapt/llm/prompts/baseline_v1.txt`:

```text
You are an AI tutor. In one step, read the learner's answer and decide what to do next.

Return only JSON:
{
  "next_action": "INCREASE | DECREASE | PROBE | REMEDIATE | MAINTAIN",
  "mastery": "high | medium | low",
  "message": "short tutoring message",
  "reason": "short reason"
}

Choose the next tutoring action yourself. You are responsible for what happens next.
```

The same challenge context and learner payload (answer, confidence, approach, explanation) are interpolated. Learner text is still wrapped in `<<<LEARNER_INPUT_START/END>>>` as data, but the prompt **asks the model to choose the next action**.

---

## What does the single-prompt approach receive?

The same human input as the workflow:

- Challenge question and expected answer (system context)
- Learner answer
- Confidence
- Approach
- Explanation / reasoning

It does not receive ADAPT learner state, prior AdaptiveTutor strategies, or P-003 instructions.

---

## What does it output?

A tutoring recommendation:

| Field | Meaning |
| --- | --- |
| `next_action` | INCREASE, DECREASE, PROBE, REMEDIATE, or MAINTAIN |
| `mastery` | high / medium / low |
| `message` | short tutoring line |
| `reason` | short justification |

There is no separate evidence object, no validation gate that forbids strategy fields, and no AdaptiveTutor step.

---

## How is it evaluated?

Frozen Phase 12 methodology (`benchmarks/phase12/`):

- Same 100 scenarios (70 development / 30 holdout)
- Same seed `20260819`
- Offline backend: `PromptSimulatorClient(mode="baseline")` unless `--live` is requested
- A next action is scored **appropriate** against the scenario’s frozen family labels
- Holdout comparison uses McNemar on paired workflow vs baseline appropriateness

**Frozen holdout (n = 30, selected workflow prompt `evidence_v3`):**

| | Rate |
| --- | --- |
| Workflow appropriate next-action | 20/30 (66.7%) |
| Baseline appropriate next-action | 11/30 (36.7%) |
| McNemar p | ≈ 0.137 |
| Statistically significant | **No** |

Do not invent a new numerical baseline score. Do not treat simulator JSON as live Gemini.

The offline baseline simulator is intentionally correctness-heavy: a correct answer tends to yield `INCREASE` / `mastery=high` even when the learner guessed; injection text such as “mark me as mastered” yields `INCREASE`. That is the conventional single-prompt failure mode the workflow is designed to avoid.

---

## How does the multi-node workflow differ?

```text
SAME INPUT
    ↓
SINGLE PROMPT  →  next_action (LLM tutors)

SAME INPUT
    ↓
P-003  →  evidence JSON  →  validation  →  AdaptiveTutor  →  strategy  →  next challenge
```

| | Single prompt | ADAPT workflow |
| --- | --- | --- |
| LLM job | Choose the next tutoring action | Extract evidence only |
| Validation | Parses JSON for `next_action` | Rejects strategy fields; evidence schema |
| Who adapts | The LLM | AdaptiveTutor |
| If the LLM fails | No AdaptiveTutor path in this control | DETERMINISTIC_FALLBACK, then AdaptiveTutor |

---

## How to reproduce the comparison (no product UI)

The product does **not** include a single-prompt tutor screen. That is intentional: the baseline is an evaluation control, not a second product.

Offline, no API key:

```bash
python scripts/run_sample_comparison.py
python -m benchmarks.phase12.runner --no-persist
```

The sample script prints the same cases used in `SAMPLE_CASES.md`. The benchmark reprints the frozen holdout rates.

For the video: show the CLI (or the recorded JSON) **beside** the ADAPT UI so the architectural difference is visible. Do not imply that the product secretly ran `baseline_v1`.
