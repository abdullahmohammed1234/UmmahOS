# Phase 3 — Community Shield

## Objective

Turn the Phase 2 Community Shield foundation into a meaningful, organization-scoped reporting system for harmful or concerning online content.

Phase 1 multi-MSA architecture and Phase 2 community modules remain intact. Phase 3 deepens only Community Shield.

The product insight:

> Community Shield captures not only what harmful content was reported, but the platform, content type, and social context in which it occurred.

## Architecture

UmmahOS remains a decoupled Laravel 12 API + Vue 3 SPA.

```
UmmahOS/
├── MSA Platform/     # reference only — untouched
├── backend/          # Laravel 12 API
├── frontend/         # Vue 3 SPA
└── docs/
```

Community Shield reports continue to use the Phase 2 `Incident` model / `incidents` table as the canonical report entity. No duplicate `reports` / `community_reports` domain was introduced.

Every report belongs to exactly one organization through `organization_id`.

Every endpoint remains under:

```
/api/v1/organizations/{organization}/...
```

## Report data model

Table: `incidents`

| Field | Notes |
| --- | --- |
| `id` | Primary key |
| `organization_id` | Owning MSA |
| `reported_by` | Submitting user |
| `platform` | Required enum |
| `content_type` | Required enum |
| `visibility` | Required context enum |
| `source_url` | Optional URL reference |
| `description` | Required free-text concern |
| `status` | `open` \| `reviewing` \| `resolved` |
| timestamps | |

Phase 2 `category` was replaced by structured platform / content type / visibility fields.

## Supported platforms

Internal values:

```
x
youtube
tiktok
reddit
discord
telegram
whatsapp
other
```

UI labels: X, YouTube, TikTok, Reddit, Discord, Telegram, WhatsApp, Other.

## Content types

```
post
comment
video
image
message
profile
thread
```

## Visibility / context

```
public
group
private
unknown
```

UI labels:

- Public
- Group / Community
- Private / Direct
- Unknown

Visibility is required because platform + content type alone is not enough context. Examples:

- `x` + `post` + `public`
- `discord` + `message` + `group`
- `whatsapp` + `message` + `private`

## Member workflow

1. Open Community Shield
2. Choose **Report a Concern**
3. Select platform
4. Select content type
5. Select visibility / context
6. Optionally provide source URL
7. Describe what happened
8. Submit
9. Receive confirmation with report ID and status `Open`

Members do not browse the organization report queue.

Members do not view other members' reports.

Members do not change status.

For Phase 3, the member experience after submit is confirmation only.

## Admin workflow

Organization admins with `incidents.manage` can:

- open the Community Shield review queue
- see organization-scoped counts: open / reviewing / resolved
- filter by status
- open a report detail
- update status (`open` → `reviewing` → `resolved`)

Admins cannot access reports from another organization.

## Privacy model

Community Shield reports may contain sensitive community information.

Protections:

- authentication required
- organization membership required
- queue/list/show/update require `incidents.manage`
- nested reports are loaded through `$organization->incidents()`
- description is rendered as plain text (no HTML)
- no public report URLs
- no unauthenticated report endpoints
- member dashboards do not expose organization-wide report counts
- request payload cannot set `organization_id`, `reported_by`, or initial `status`

## Authorization

Phase 1 RBAC is reused. No separate Community Shield permission framework.

| Action | Who | Permission / gate |
| --- | --- | --- |
| Submit report | Any current-org member | Membership only |
| Community Shield overview | Any current-org member | Membership only; counts only for admins |
| List / view / update reports | Current-org admin | `incidents.manage` |
| Admin dashboard shield counts | Current-org admin | `organization.manage` |

A user who is a member in Alpha and an admin in Beta has member Community Shield capabilities in Alpha and admin review capabilities in Beta.

## Tenant isolation

1. `EnsureOrganizationMembership` on every organization-scoped route
2. `EnsureOrganizationPermission` for review endpoints
3. Nested record lookup through the current organization relation
4. Cross-org IDOR attempts return `403` (not a member) or `404` (wrong org id)

## Validation

Backend validation:

- `platform` required, enum
- `content_type` required, enum
- `visibility` required, enum
- `source_url` optional; if present must be a valid URL
- `description` required, max 8000 characters
- `organization_id`, `reported_by`, and `status` prohibited on create
- only `status` allowed on update; other report fields prohibited

No scraping. No platform ownership checks on URLs. No external fetches.

## API

```
GET    /api/v1/organizations/{organization}/community-shield
POST   /api/v1/organizations/{organization}/incidents
GET    /api/v1/organizations/{organization}/incidents
GET    /api/v1/organizations/{organization}/incidents/{incident}
PATCH  /api/v1/organizations/{organization}/incidents/{incident}
```

Route naming kept `incidents` for continuity with Phase 1/2. The product name remains Community Shield.

## Dashboard integration

Member dashboard:

- Community Shield entry point only
- no organization-wide report counts

Admin dashboard:

- open / reviewing / resolved counts for the current organization
- link into the Community Shield review queue

## Demo data

Both demo organizations contain distinct Community Shield reports.

Alpha examples:

- X / Post / Public / open
- Discord / Message / Group / reviewing
- Reddit / Thread / Public / resolved

Beta examples:

- TikTok / Video / Public / reviewing
- WhatsApp / Message / Private / open
- YouTube / Comment / Public / resolved

## Critical demo flow

Login:

```
multi.user@example.com
password
```

1. Enter **Demo MSA Alpha** as member → Community Shield → Report a Concern → submit structured report under Alpha.
2. Switch to **Demo MSA Beta** as admin → Community Shield review queue shows Beta reports only.
3. Switch back to Alpha → member cannot access the admin review queue.

This proves:

```
same user
+ same application
+ different organization
+ different role
= different authorized experience
```

## Tests

Backend Phase 3 coverage includes:

- authenticated creation
- unauthenticated rejection
- platform / content type / visibility / description / source URL validation
- representative platform-context combinations
- organization_id payload rejection
- member privacy (no list/view/status change)
- admin list/filter/view/status lifecycle
- cross-organization IDOR protections
- overview count privacy

Frontend tests cover:

- Community Shield page render
- platform / content type / visibility selection
- validation error display
- successful submission confirmation
- member does not see admin review controls
- admin sees organization report queue
- switching organization changes Community Shield authorization/data

## Limitations

- No evidence file storage yet
- No AI classification or recommendations
- No external platform APIs or scraping
- No automated moderation, bans, escalation, or law-enforcement notifications
- No assignment system or priority scoring
- Members cannot later retrieve their own report history (confirmation only)
- Source URL is stored as supplied text; not verified against the selected platform

## Intentionally deferred

- AI-assisted analysis
- Platform integrations (X, YouTube, TikTok, Reddit, Discord, Telegram, WhatsApp)
- Automated moderation / toxicity classifiers
- Evidence attachment uploads
- Notification / email workflows
- Analytics and trend charts
- Cross-organization pattern detection

Phase 3 establishes the structured reporting and human review foundation only.
