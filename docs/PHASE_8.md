# Phase 8 — Community Shield Outcome Tracking

Phase 8 closes the reporting feedback loop by tracking **externally reported outcomes** as user/reviewer-provided records. UmmahOS does **not** automatically submit reports, query external platforms, or verify platform decisions unless a human explicitly records verification.

## Objective

After Phases 1–7, Community Shield could capture incidents, preserve evidence, analyze with AI, conduct human review, generate evidence packages, and provide reporting guidance. Phase 8 answers:

> **What happened next?**

## Core Product Principle

| Internal UmmahOS review | External platform outcome |
|-------------------------|---------------------------|
| UmmahOS controls workflow | UmmahOS only **records** information |
| Human review is authoritative | "Reported" = submission was **recorded**, not auto-submitted |
| | Outcomes include **source** and **verification state** |

## Architecture

```
Incident
   │
   └── incident_external_reports (multiple per incident)
            │
            ├── incident_external_report_status_history (append-only)
            │
            └── incident_report_appeals
```

### Services

- `IncidentOutcomeService` — create reports, transitions, appeals, history, serialization
- `OutcomeStateMachine` — validates status transitions
- `IncidentEvidencePackageService` — includes `outcome_tracking.reports[]` in JSON/PDF exports

### API Routes (organization-scoped)

| Method | Path | Permission |
|--------|------|------------|
| GET | `/community-shield/reports/{report}/external-reports` | outcomes.view \| manage \| admin |
| POST | `/community-shield/reports/{report}/external-reports` | outcomes.manage \| admin |
| PATCH | `/community-shield/reports/{report}/external-reports/{id}` | outcomes.manage \| admin |
| GET | `.../external-reports/{id}/history` | outcomes.view \| manage \| admin |
| POST | `.../external-reports/{id}/appeals` | outcomes.appeal \| manage \| admin |
| PATCH | `.../external-reports/{id}/appeals/{appeal}` | outcomes.manage \| admin |
| GET | `/community-shield/my-reports` | membership (ownership filter) |
| GET | `/community-shield/my-reports/{report}` | membership (ownership filter) |
| POST | `/community-shield/my-reports/{report}/external-reports/{id}/appeals` | outcomes.appeal |

## External Report Model

Fields: `platform`, `reporting_channel`, `external_reference`, `reported_at`, `status`, `decision`, `outcome`, `outcome_source`, `verification_status`, `internal_notes`, `reporter_visible_summary`, `decision_note`, `outcome_summary`.

Platforms include incident platforms plus: `campus_administration`, `university_office`, `community_organization`.

## Status Workflow

```
reported → under_review → decision → outcome
                ↘ decision (skip allowed)
outcome → outcome (updates within final stage)
```

- **reported** — A user/reviewer recorded external submission
- **under_review** — External destination acknowledged or reporter recorded review
- **decision** — Decision value required (`action_taken`, `no_action`, etc.)
- **outcome** — Outcome value required (`content_removed`, `no_action`, etc.)

## Source & Verification

| Outcome source | Meaning |
|----------------|---------|
| `platform_response` | Information from platform response |
| `reporter_observation` | Reporter observed result |
| `reviewer_observation` | Reviewer observed result |
| `other` | Other source |

| Verification | Meaning |
|--------------|---------|
| `unverified` | Default — not independently verified |
| `reported_by_user` | User-reported, not verified |
| `verified_by_reviewer` | Human reviewer explicitly verified |

Never auto-set `verified_by_reviewer` from URLs, report IDs, AI, or time elapsed.

## Appeals

Separate `incident_report_appeals` records preserve original decisions. Statuses: `submitted`, `under_review`, `accepted`, `rejected`, `withdrawn`, `resolved`.

Appeal submission records **"Appeal Submitted"** — not automatic external submission.

## Immutable History

`incident_external_report_status_history` is append-only. Each transition records `previous_status`, `new_status`, `decision`, `outcome`, `changed_by`, `changed_at`, `note`.

## RBAC

| Permission | Admin | Reviewer | Member |
|------------|-------|----------|--------|
| `incidents.outcomes.view` | ✓ | ✓ | ✓ (view slug) |
| `incidents.outcomes.manage` | ✓ | ✓ | ✗ |
| `incidents.outcomes.appeal` | ✓ | ✓ | ✓ |

Member access is **ownership-scoped** via `reported_by == current_user`, not org-wide.

## Member Experience

- **My Reports** list at `/community-shield/my-reports`
- **What happened next?** section on report detail
- Timeline from history (no internal notes)
- Appeal submission for own reports

## Reviewer Experience

- **Outcome Tracking** section on review detail page
- Record external report, update status, record decision/outcome
- View history and manage appeals

## Evidence Package Integration

JSON/PDF exports include:

```json
{
  "outcome_tracking": {
    "label": "OUTCOME TRACKING",
    "disclaimer": "...",
    "reports": [ ... ]
  }
}
```

Empty state: `"reports": []`. Phase 7 fields unchanged. PDF section 8: OUTCOME TRACKING.

## Demo Data

`DemoCommunitySeeder` seeds four Phase 8 scenarios (clearly demo/seed, not real platform reports):

- **Demo A** — Reddit completed outcome (verified by reviewer)
- **Demo B** — Discord under review
- **Demo C** — X no action + member appeal
- **Demo D** — Other platform, unverified reporter observation

## Demo Workflow

1. Login as `alpha.reviewer@example.com`
2. Community Shield → Review Queue → confirmed Reddit incident
3. Outcome Tracking → record/update external report lifecycle
4. Export evidence package — includes outcome tracking
5. Login as `alpha.member@example.com`
6. My Reports → view outcome timeline and submit appeal

## Tests

### Backend (148 tests, 823 assertions)

- `IncidentOutcomeTest` — CRUD, transitions, appeals, member access, tenant isolation, history
- `IncidentEvidencePackageTest` — outcome_tracking in JSON/PDF

### Frontend (32 tests)

- `outcomeTracking.spec.ts` — reviewer panel, member view, forms, verification display

## Limitations (Phase 8)

- No automatic platform submission or API integration
- No scraping or automated outcome detection
- No AI outcome prediction
- No notification/email infrastructure
- No cross-org analytics (Phase 9+)

## What Phase 8 Does NOT Include

Phase 9 was **not started**: advanced analytics, cross-MSA intelligence, automated integrations, predictive models, public dashboards.

`MSA Platform/` was **not modified**.
