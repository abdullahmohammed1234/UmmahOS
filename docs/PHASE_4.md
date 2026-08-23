# Phase 4 — Community Shield Context Capture

## Objective

Transform Community Shield reports from simple structured incidents into **structured context records**.

Phase 1 multi-MSA foundation, Phase 2 community modules, and Phase 3 Community Shield reporting remain intact. Phase 4 deepens only context capture around the existing `Incident` entity.

The product principle:

> Do not preserve only the harmful item. Preserve the item + context + target + pattern.

The review principle:

> A report preserves enough surrounding context for an authorized reviewer to understand what happened without relying on a screenshot alone.

## Architecture

```
UmmahOS/
├── MSA Platform/     # reference only — untouched
├── backend/          # Laravel 12 API
├── frontend/         # Vue 3 SPA
└── docs/
```

Canonical entity remains `Incident` / `incidents`.

Child evidence entities:

* `incident_replies`
* `incident_related_items`

All endpoints remain organization-scoped:

```
/api/v1/organizations/{organization}/...
```

## Context-capture architecture

```
Community Shield Report (Incident)
        │
        ├── Incident metadata (platform, content type, visibility, status)
        ├── Original item
        ├── Source URL / reference
        ├── Timestamps (original posted / observed)
        ├── Surrounding context
        ├── Replies
        ├── Related copies
        ├── Language
        ├── Reporter notes
        └── Safety classification (human review)
```

Phase 4 captures structured evidence/context **manually**. It does not automatically scrape, classify, or retrieve external platform content.

## Report model additions

New fields on `incidents`:

| Field | Notes |
| --- | --- |
| `original_item_title` | Optional label |
| `original_item_content` | Optional long text of the reported item |
| `original_item_author` | Optional account / author reference |
| `original_item_posted_at` | When the original content was posted (if known) |
| `observed_at` | When the reporter observed/captured it |
| `surrounding_context` | What happened around the item |
| `language` | Stable language code (`en`, `ar`, …, `unknown`) |
| `reporter_notes` | Extra reviewer guidance from the reporter |
| `safety_classification` | Internal review classification |
| `classified_by` | Authenticated reviewer who classified |
| `classified_at` | When classification was set |

Phase 3 fields (`platform`, `content_type`, `visibility`, `source_url`, `description`, `status`) are preserved.

### Timestamps

* `original_item_posted_at` — when the content was posted
* `observed_at` — when the reporter observed it

If `observed_at` is omitted on create, the backend assigns submission time. Explicit values are not overwritten.

### Source URL

`source_url` remains the primary external reference when one exists. It is not fetched, crawled, or verified against the selected platform.

## Replies

Table: `incident_replies`

| Field | Notes |
| --- | --- |
| `incident_id` | Parent report |
| `author` | Optional account reference |
| `content` | Reply text |
| `posted_at` | Optional |
| `position` | Ordering |

Replies are evidence/context records, not a social-media conversation system. They are organization-scoped through the parent incident.

## Related copies

Table: `incident_related_items`

| Field | Notes |
| --- | --- |
| `incident_id` | Parent report |
| `platform` | Same platform catalog as incidents |
| `content_type` | Same content-type catalog |
| `reference_url` | Optional |
| `description` | What is related |
| `observed_at` | Optional |

Related copies preserve potential repetition or cross-platform spread. They are recorded manually — never discovered automatically.

## Language

Reporter-supplied language codes stored as strings. Expandable in application code without a database migration. Includes `unknown` / “Unknown / Not sure”.

No automated language detection in Phase 4.

## Reporter notes vs description

* **Description** — what happened / what is being reported
* **Reporter notes** — additional information reviewers should know

Reporter notes are not public and remain inside the organization review surface.

## Safety classification

Internal review values:

```
unclassified
harassment
hate
threat
targeted_abuse
discrimination
incitement
other
```

UI disclaimer:

> Internal review classification — not a legal determination.

Classification is reviewer-controlled (`incidents.manage`). Members cannot set it on create or update. Setting a non-`unclassified` value records `classified_by` and `classified_at`.

Severity scoring is deferred.

## Privacy model

Unchanged from Phase 3:

* Members can submit reports and receive confirmation
* Members cannot browse the organization report queue
* Members cannot view other reporters’ context
* Admins can review and classify within their organization only
* Organization A admins cannot see Organization B reports or child records

Reports remain immutable to members after submission.

## Member workflow

```
Platform
↓ Content type
↓ Visibility / context
↓ Original item (optional)
↓ Source / timestamp (optional)
↓ Surrounding context (optional)
↓ Replies (optional)
↓ Related copies (optional)
↓ Language / reporter notes (optional)
↓ Submit
```

Required fields remain:

* platform
* content type
* visibility
* description

A lightweight “Context captured” checklist shows completeness without blocking submission.

## Admin workflow

Admin detail is the main review surface:

1. Incident metadata
2. Original item
3. Surrounding context
4. Replies
5. Related copies
6. Language
7. Reporter notes
8. Safety classification
9. Status decision

Admins may also add/delete replies and related items after submission within their organization.

## API

```
GET    /organizations/{organization}/community-shield
POST   /organizations/{organization}/incidents
GET    /organizations/{organization}/incidents
GET    /organizations/{organization}/incidents/{incident}
PATCH  /organizations/{organization}/incidents/{incident}
POST   /organizations/{organization}/incidents/{incident}/replies
DELETE /organizations/{organization}/incidents/{incident}/replies/{reply}
POST   /organizations/{organization}/incidents/{incident}/related-items
DELETE /organizations/{organization}/incidents/{incident}/related-items/{relatedItem}
```

Create accepts nested `replies` and `related_items` inside a database transaction.

`organization_id`, `reported_by`, `status`, `safety_classification`, `classified_by`, and `classified_at` are prohibited on member create payloads.

Admin PATCH may update `status` and/or `safety_classification` only.

## Tenant isolation

Parent incidents are always resolved through the current organization before child access. Cross-organization attempts to read/write replies or related items return 404/403 as appropriate.

## Demo scenario

Use `multi.user@example.com` / `password`.

### Alpha (member)

Open Community Shield → Report a Concern and submit a context-rich report (original item, context, replies, related copy, language, notes).

### Beta (admin)

Switch to Beta → Community Shield → Review Reports. Open the seeded Discord group report to see structured context, related copies, language, notes, and classification controls.

Seeded examples include public, group, and private WhatsApp-style contexts with fictional content only.

## Tests

Backend coverage includes:

* original item persistence and long content
* timestamp behavior
* surrounding context / notes
* replies ordering and atomic create
* related copies across platforms
* language validation
* classification authorization
* child-record and incident IDOR isolation
* mass-assignment protection
* Phase 3 privacy regressions

Frontend coverage includes expanded form sections, context submission, confirmation, admin structured detail, classification, and member/admin control separation.

## Limitations

Phase 4 intentionally does **not** include:

* AI classification or embeddings
* automated hate-speech / language / pattern detection
* platform APIs or scraping
* screenshot / media upload subsystems
* browser extensions
* severity engines
* full audit-log subsystem
* member post-submit report history editing

Phase 4 creates the structured evidence substrate that later phases can interpret.

## Final product statement

Phase 3 established:

> A member can report harmful or concerning online content.

Phase 4 establishes:

> A report preserves enough surrounding context for an authorized reviewer to understand what happened without relying on a screenshot alone.

**Context is evidence.**
