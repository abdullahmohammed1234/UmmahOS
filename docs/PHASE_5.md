# Phase 5 — AI Context Analysis for Community Shield

## Objective

Add an **AI-assisted context analysis layer** to Community Shield.

Phase 1–4 remain intact. Phase 5 does **not** replace human review.

The product principle:

> AI analyzes the structured incident and context. A trained human reviews the analysis and makes the decision.

AI uncertainty is an intentional product feature. Ambiguous evidence should surface uncertainty rather than manufactured confidence.

> AI analysis is advisory and does not constitute a final safety, legal, or policy determination.

## Architecture

```
Community Shield Incident (Phase 4 structured context)
        │
        ▼
AI Analysis Service
        │
        ▼
Provider Interface (AIAnalysisProvider)
        │
        ├── GeminiAnalysisProvider
        ├── FakeAnalysisProvider (tests)
        └── UnavailableAnalysisProvider (no credentials)
        │
        ▼
incident_ai_analyses (persisted analysis packages)
        │
        ▼
Human reviewer (authoritative classification + status)
```

Canonical application paths:

* `UmmahOS/backend/`
* `UmmahOS/frontend/`
* `UmmahOS/docs/`

`MSA Platform/` remains untouched reference material.

## AI analysis data model

Table: `incident_ai_analyses`

| Field | Notes |
| --- | --- |
| `incident_id` | Parent organization-scoped incident |
| `provider` | e.g. `gemini`, `fake`, `unavailable` |
| `model` | Configured model name |
| `prompt_version` | e.g. `community_shield_context_v1` |
| `status` | `queued` → `running` → `completed` / `failed` |
| `analysis` | Structured JSON package (nullable on failure) |
| `error_message` | Safe failure message for reviewers |
| `requested_by` | Admin who triggered analysis |

Each request creates a **new** analysis record. Previous analyses are never overwritten.

## Structured analysis package

```json
{
  "signals": [
    {
      "name": "religious_identity_targeting",
      "description": "...",
      "evidence": ["..."],
      "confidence": "moderate"
    }
  ],
  "classification": {
    "label": "potential_coded_visual_hate",
    "confidence": "moderate"
  },
  "uncertainty": {
    "level": "moderate",
    "explanation": "..."
  },
  "alternative_interpretation": "... or null",
  "recommended_action": {
    "type": "human_review",
    "reason": "..."
  }
}
```

### Confidence / uncertainty

Qualitative only:

* `low`
* `moderate`
* `high`

No fake numeric probabilities.

### Recommended actions

Review actions only:

* `human_review`
* `request_more_context`
* `no_immediate_action`

Never bans, deletions, police reports, or other enforcement.

## Provider abstraction

Interface: `App\Contracts\AI\AIAnalysisProvider`

Implementations:

* `GeminiAnalysisProvider` — live Gemini generateContent API via Laravel HTTP
* `FakeAnalysisProvider` — deterministic test double
* `UnavailableAnalysisProvider` — honest failure when credentials are missing

Binding lives in `AppServiceProvider`. In `testing`, the fake provider is used automatically so CI never depends on live Gemini calls.

## Gemini configuration

Environment variables (see `backend/.env.example`):

```
AI_ANALYSIS_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
```

Optional:

```
GEMINI_API_ENDPOINT=
GEMINI_TIMEOUT=45
```

Credentials are never hard-coded.

If `GEMINI_API_KEY` is empty:

* report submission still works
* admin review still works
* AI analysis returns a failed / unavailable state honestly

No fabricated “successful” analysis is inserted.

## Prompt architecture

Versioned prompt class:

`App\Prompts\CommunityShieldContextAnalysisV1`

Prompt version identifier:

`community_shield_context_v1`

The prompt:

* tells the model it is an assistant to a human reviewer
* forbids enforcement actions and legal determinations
* forbids fabricating missing evidence
* requires explicit uncertainty when evidence is ambiguous
* separates **system/analysis instructions** from **untrusted incident content**

Incident content is wrapped as:

```
=== BEGIN UNTRUSTED INCIDENT CONTENT ===
...
=== END UNTRUSTED INCIDENT CONTENT ===
```

Reported text is treated as evidence, never as instructions (prompt-injection awareness).

## Context payload

`CommunityShieldContextBuilder` sends only analysis-relevant fields:

* platform, content type, visibility
* original item
* source URL
* timestamps
* surrounding context
* replies
* related copies
* language
* reporter notes

It does **not** send:

* auth tokens
* organization IDs
* membership IDs
* reporter identity
* permissions
* unrelated user data

## Human review separation

Phase 4 human fields remain authoritative:

* `safety_classification`
* `classified_by`
* `classified_at`
* `status`

AI analysis:

* does not overwrite human classification
* does not change incident status
* does not resolve, close, enforce, notify, or contact anyone

Admin UI labels:

* **AI Context Analysis** (advisory)
* **Human classification** (authoritative)

## API

Organization-scoped only:

```
POST /api/v1/organizations/{organization}/incidents/{incident}/ai-analysis
GET  /api/v1/organizations/{organization}/incidents/{incident}/ai-analyses
GET  /api/v1/organizations/{organization}/incidents/{incident}/ai-analyses/{analysis}
```

Authorization: `incidents.manage`

Members cannot trigger or view reviewer AI analysis.

Cross-organization access is blocked through the existing organization + incident resolution path.

AI analysis is **not** run automatically on report creation. Admins must click **Analyze with AI**.

## Frontend workflow

Admin report detail:

1. Review structured Phase 4 context
2. Read privacy note / advisory disclaimer
3. Click **Analyze with AI** (or **Run New Analysis**)
4. Review potential signals, classification, confidence, uncertainty, alternative interpretation, recommended action
5. Set human classification
6. Update status if appropriate

Uncertainty is displayed prominently — not hidden.

## Failure handling

Provider/network/validation failures store:

```
status = failed
```

UI shows:

```
AI analysis unavailable
```

Never:

```
No harmful content detected
```

Malformed model JSON is rejected by `AnalysisResultValidator` before persistence as a trusted package.

## Evaluation fixtures

Deterministic fictional fixtures live in:

`backend/tests/Fixtures/AI/EvaluationFixtures.php`

| Case | Intent |
| --- | --- |
| A | Clear potential religious identity targeting |
| B | Ambiguous quote / incomplete context |
| C | Repeated / cross-platform pattern |
| D | Insufficient evidence |

These evaluate pipeline behavior with the fake provider. They are not live Gemini outputs.

## Testing strategy

Backend:

* authorization (member denied, cross-org denied)
* fake provider success / failure / malformed output
* persistence + non-overwrite of prior analyses
* human classification/status unchanged
* tenant isolation
* prompt untrusted-content separation
* schema validation

Frontend:

* Analyze with AI visible for admins only
* loading / completed / failed states
* signals, confidence, uncertainty, alternative interpretation, recommended action
* disclaimer
* rerun creates an additional analysis
* org switching isolates AI UI

Live Gemini calls are not required for automated tests.

## Demo workflow

With credentials configured:

```
Open admin report
→ Analyze with AI
→ Gemini structured package
→ Human reviews uncertainty + signals
→ Human classification
→ Status update
```

Without credentials:

```
Reporting + review works
AI analysis unavailable
```

Do not present fixture/demo packages as live model results unless clearly labeled.

## Limitations

* Sync request-time analysis (no elaborate queue worker required for Phase 5)
* Qualitative confidence only
* Single Gemini provider integration (swappable via interface)
* No dashboard AI scores
* No training, RAG, embeddings, or automated enforcement

## Future work

Possible later phases (out of scope here):

* async job queue for long analyses
* analysis comparison UI across prompt versions
* reviewer feedback on analysis usefulness
* additional providers

## Preserve previous phases

`docs/PHASE_1.md` through `docs/PHASE_4.md` are unchanged.

Phase 5 establishes:

> AI can help an authorized human reviewer understand structured context without pretending to be the final authority.
