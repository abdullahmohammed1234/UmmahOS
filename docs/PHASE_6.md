# Phase 6 — Human Review Workflow for Community Shield

## Objective

Introduce the formal **Community Safety Review** workflow.

Phase 1–5 remain intact. Phase 6 does **not** make AI authoritative and does **not** add automated enforcement.

The product principle:

> AI-assisted triage is advisory. Human reviewers remain authoritative for Community Shield decisions.

Canonical flow:

```
Submitted
    ↓
AI-assisted triage
    ↓
Human review
    ↓
┌──────────────┬──────────────┬───────────┐
│ Confirm      │ Uncertain    │ Close     │
│      ↓       │      ↓       │           │
│ Escalate     │ Request      │           │
│              │ context      │           │
└──────────────┴──────────────┴───────────┘
```

## Architecture

```
Incident
   ↓
Structured Evidence (Phase 4)
   ↓
AI Context Analysis (Phase 5, advisory)
   ↓
Human Reviewer (organization-scoped)
   ↓
Human Decision + Review / Audit History
```

Canonical application paths:

* `UmmahOS/backend/`
* `UmmahOS/frontend/`
* `UmmahOS/docs/`

`MSA Platform/` remains untouched reference material.

## Community Safety Reviewer role

Slug: `community_safety_reviewer`  
Display name: **Community Safety Reviewer**

This role is assigned through the existing:

```
User ↔ Membership ↔ Organization ↔ Role ↔ Permissions
```

It is organization-scoped. A user can be a reviewer in Demo MSA Alpha and a member in Demo MSA Beta without gaining Beta review access.

There is **no** global reviewer role.

### Reviewer permissions

| Permission | Purpose |
| --- | --- |
| `organization.view` | Basic app access inside the assigned organization |
| `incidents.view` | View Community Shield incident metadata |
| `incidents.review` | Access review queue / start / uncertain / close |
| `incidents.request_context` | Create and resolve context requests |
| `incidents.escalate` | Record internal escalations |
| `incidents.classify` | Confirm with human classification |

The reviewer role does **not** receive unrestricted `*` access and does **not** receive `organization.manage` or general content administration.

Organization admins continue to receive all permissions inside their organization, including review access. Admin ≠ Reviewer as roles, but admins retain review capability through permissions.

## Review lifecycle

Existing Phase 3/4 workflow status is preserved and extended:

| Field | Values | Meaning |
| --- | --- | --- |
| `status` | `open`, `reviewing`, `resolved` | Where the incident is in the workflow |
| `review_outcome` | `confirmed`, `uncertain`, `closed`, or null | What the reviewer concluded |

Additional incident fields:

* `current_reviewer_id`, `review_started_at`
* `review_notes`
* `escalated`, `escalation_reason`, `escalated_by`, `escalated_at`
* `review_lock_version` (optimistic concurrency)

### Outcomes

* **Confirm** — reviewer determines the evidence supports a safety concern/classification. Requires notes + human classification. Resolves the incident.
* **Uncertain** — evidence is insufficient or ambiguous. Valid outcome. Incident remains under review.
* **Close** — no further review action is required. Optional reason. Does **not** automatically mean “false report.”
* **Escalate** — internal higher-level human review. Requires reason. No external reporting.
* **Request More Context** — structured request record. Incident remains unresolved.

## Data model

### `incident_reviews`

Durable review session records (`reviewer_id`, `outcome`, `notes`, `safety_classification`, `escalation_reason`, `is_current`).

### `incident_review_actions`

Immutable audit history (`actor_id`, `action`, `notes`, `payload`, `created_at`).

Normal reviewers cannot edit historical actions.

### `incident_context_requests`

Structured requests (`reason`, `requested_by`, `requested_at`, `status`: `open` / `fulfilled` / `cancelled`).

## API

Organization-scoped endpoints under `/api/v1/organizations/{organization}/...`:

| Method | Path | Permission |
| --- | --- | --- |
| GET | `/community-shield/review-queue` | `incidents.manage\|incidents.review` |
| GET | `/community-shield/reports/{report}/review` | review |
| POST | `.../review/start` | review |
| POST | `.../review/confirm` | `incidents.manage\|incidents.classify` |
| POST | `.../review/uncertain` | review |
| POST | `.../review/close` | review |
| POST | `.../review/escalate` | `incidents.manage\|incidents.escalate` |
| POST | `.../context-requests` | `incidents.manage\|incidents.request_context` |
| PATCH | `.../context-requests/{id}` | request_context |

Queue filters: `status`, `platform`, `confidence`, `uncertainty`, `classification`, `escalated`.

Every action validates state-machine transitions on the backend. Stale `review_lock_version` values return **409**.

Nested report IDs are always resolved through the organization. Cross-organization access returns 403/404 as appropriate.

## AI / human separation

* AI analysis packages remain unchanged by human review actions.
* Human classification (`safety_classification`) remains authoritative and distinct from AI labels.
* AI cannot change incident status, create review decisions, escalate, or resolve incidents.
* Queue and review UI label AI as **AI-assisted triage** / **AI Context Analysis**, never “AI Verdict.”

## Frontend

* **Review Queue** — `/community-shield/review-queue`
* **Review Detail** — `/community-shield/review-queue/:id`

Navigation (current organization membership):

```
Community Shield Review
  ├── Reports
  └── Review Queue
```

Ordinary members do not see the review queue, reviewer notes, escalation records, or internal audit history.

Review detail presents evidence first, then AI Context Analysis, then Human Review controls and history.

## Security model

Preserved from Phases 1–5:

* Sanctum authentication
* organization-scoped routes
* membership middleware
* permission middleware
* organization context
* IDOR protection
* nested resource validation

Phase 6 additions:

* reviewer notes are internal-only
* review endpoints require review/classify/escalate/request_context (or manage)
* no global reviewer bypass
* optimistic concurrency on review mutations

## Demo workflow

Seeded credentials (password for all): `password`

| User | Memberships |
| --- | --- |
| `multi.user@example.com` | Alpha **Community Safety Reviewer** + Beta admin |
| `alpha.reviewer@example.com` | Alpha reviewer |
| `beta.reviewer@example.com` | Beta reviewer |
| `alpha.admin@example.com` | Alpha admin (retains review access) |
| `alpha.member@example.com` | Alpha member (no review access) |

Suggested demo:

1. Sign in as `multi.user@example.com`.
2. Stay in Demo MSA Alpha.
3. Open **Community Shield → Review Queue**.
4. Open the high-uncertainty Discord report.
5. Review original item, context, replies, related items, AI Context Analysis.
6. Use **Request More Context**.
7. Open another report and **Confirm** with human rationale.
8. Open the Telegram report and inspect **Escalate**.
9. Switch to Demo MSA Beta — Alpha review queue is no longer available; Beta admin review remains organization-local.

## Testing

Backend Feature coverage includes:

* reviewer role/permissions and org scoping
* queue isolation
* start / confirm / uncertain / close / escalate / request context
* invalid transitions and required fields
* audit history preservation
* AI package immutability under human review
* concurrency conflicts
* member denial / admin retention

Frontend Vitest coverage includes:

* nav gating for reviewers vs members
* queue + detail evidence package
* uncertainty prominence
* review action flows
* org-switch isolation
* safe failed-action display

## Known limitations

* No external platform integrations, scraping, or automated reporting.
* No enterprise case-assignment system beyond reviewer-of-record + lock version.
* Context requests are workflow records only; fulfillment is manual evidence capture.
* Escalation is internal only.
* No advanced analytics, pattern detection, or cross-MSA intelligence.

## Future work (not Phase 6)

* Advanced analytics / pattern detection
* Cross-MSA intelligence
* Automated moderation / enforcement
* External platform reporting
* Public reporting dashboards

Phase 7 is not started.
