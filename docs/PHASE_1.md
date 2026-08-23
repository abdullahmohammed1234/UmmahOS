# Phase 1 — Multi-MSA foundation

## Objective

Replace the old conceptual model:

`User → SFU MSA`

with:

`User → MSA Organization`

Phase 1 establishes the generalized UmmahOS platform foundation:

- Organization as a first-class entity
- Users belonging to many organizations
- Organization-scoped memberships, roles, and permissions
- Server-enforced tenant isolation
- A current-organization context the frontend can switch

Community Shield, incident capture, AI analysis, and report generation are **out of scope**.

## Architecture

```
UmmahOS/
├── MSA Platform/     # pre-existing SFU infrastructure (reference only)
├── backend/          # new Laravel 12 API
├── frontend/         # new Vue 3 SPA
└── docs/             # Phase 1 documentation
```

UmmahOS is a decoupled API + SPA. The frontend never talks to `MSA Platform/` at runtime.

```
User
 └── Membership (role)
      └── Organization
           ├── Members
           ├── Events      (future)
           ├── Courses     (future)
           ├── Content     (future)
           ├── Incidents   (future)
           └── Reports     (future)
```

## Pre-existing infrastructure

See `PRE_EXISTING_MATERIALS.md`.

The SFU MSA Platform provided proven Laravel / Vue / Sanctum / custom-RBAC patterns. Those patterns were adapted. The SFU application was not renamed, copied as the product UI, or used as the UmmahOS runtime.

## New UmmahOS architecture

### Backend

- Laravel 12, PHP 8.2, Sanctum bearer tokens
- Routes under `/api/v1`
- Thin controllers, form requests, JSON resources, services
- Organization-scoped middleware instead of global RBAC

### Frontend

- Vue 3, Vue Router, Pinia, Axios, TypeScript, Vite
- Distinct UmmahOS identity (not the SFU MSA visual system)
- Enough UI to prove authenticated user context, current organization, switching, and organization-aware requests

## Organization model

Table: `organizations`

| Field | Notes |
| --- | --- |
| `id` | Primary key |
| `name` | Display name |
| `slug` | Unique public identifier |
| `status` | `active`, `inactive`, or `suspended` |
| `created_at` / `updated_at` | Timestamps |

Route binding accepts either numeric `id` or `slug`.

Creating an organization makes the creator an **admin** member of that organization.

## Membership model

Table: `memberships`

| Field | Notes |
| --- | --- |
| `id` | Primary key |
| `user_id` | The person |
| `organization_id` | The MSA |
| `role_id` | Role **in that organization** |
| timestamps | |

Unique constraint: `(user_id, organization_id)`.

A user may have many memberships. Example:

```
multi.user@example.com
 ├── Demo MSA Alpha → member
 └── Demo MSA Beta  → admin
```

Membership is the organization boundary. There is no `User → one MSA` foreign key.

## Role model

Table: `roles`

Roles are **templates**, not global grants:

- `admin` — all permissions inside the assigned organization
- `member` — view permissions inside the assigned organization

The assignment lives on `memberships.role_id`. A role slug is never interpreted without an organization.

This is the adaptation of the MSA Platform RBAC tables. The old `role_user` global pivot is intentionally absent.

## Permission model

Table: `permissions` plus `permission_role`.

Foundational catalog only:

- `organization.view` / `organization.manage`
- `members.view` / `members.manage`
- `events.view` / `events.manage`
- `courses.view` / `courses.manage`
- `content.view` / `content.manage`
- `incidents.view` / `incidents.manage`
- `reports.view` / `reports.manage`

`admin` receives every slug. `member` receives `*.view` only.

Event, course, content, incident, and report **modules are not built** in Phase 1. Their permissions exist so later phases can authorize against a stable catalog.

There are no direct user-permission overrides and no global super-admin bypass. That MSA Platform behavior would break tenant isolation.

## Active organization strategy

**Chosen approach: organization-scoped routes.**

One implementation, not several:

```
/api/v1/organizations/{organization}/...
```

`{organization}` is resolved server-side (id or slug). Middleware then:

1. Requires a Sanctum-authenticated user
2. Loads that user's membership in the resolved organization
3. Rejects non-members with `403`
4. Binds `OrganizationContext` (organization + membership + role + permissions)

The frontend stores the current organization id in Pinia / `localStorage` and prefixes API calls with that id. The client-supplied id is a routing hint only. Membership is always re-checked on the server.

`GET /api/v1/organizations/{organization}/context` is the switch/reload endpoint. Switching organizations is "call context on a different organization the user already belongs to."

Not implemented (intentionally):

- Session-stored current org on the server
- Trusting an `X-Organization-Id` header without a route-bound organization
- Cookie-based tenant selection

## Tenant isolation strategy

Security is enforced on the backend.

1. **Membership gate.** `EnsureOrganizationMembership` runs on every organization-scoped route.
2. **Permission gate.** `EnsureOrganizationPermission` evaluates the membership role in *that* organization only.
3. **Explicit query scoping.** Memberships and future records are loaded through `$organization->memberships()` or `scopeForOrganization()`. Direct IDs from another tenant 404 inside the current org.
4. **No global admin bypass.** Admin is an organization role, not a platform-wide override.
5. **Future module lock.** `/organizations/{organization}/{events|courses|content|incidents|reports}/{id}` requires membership now, even though those modules are unimplemented. Cross-org IDOR attempts return `403`.

Frontend filtering is convenience only.

## Database decisions

- Independent UmmahOS schema. Not the SFU production database.
- Local default: SQLite (`backend/database/database.sqlite`)
- Tests: SQLite `:memory:`
- No imported SFU member rows, emails, or secrets

Seeded development organizations:

- Demo MSA Alpha (`demo-msa-alpha`)
- Demo MSA Beta (`demo-msa-beta`)

Seeded users (password `password`):

| Email | Memberships |
| --- | --- |
| `alpha.admin@example.com` | Alpha admin |
| `alpha.member@example.com` | Alpha member |
| `beta.admin@example.com` | Beta admin |
| `multi.user@example.com` | Alpha member + Beta admin |
| `outsider@example.com` | none |

## API decisions

Public auth:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Authenticated, unscoped:

- `GET /api/v1/organizations` — only orgs the user belongs to
- `POST /api/v1/organizations` — create org; creator becomes admin

Authenticated + member:

- `GET /api/v1/organizations/{organization}`
- `GET /api/v1/organizations/{organization}/context`
- `PATCH|DELETE /api/v1/organizations/{organization}` — `organization.manage`
- `GET /api/v1/organizations/{organization}/members` — `members.view`
- `POST|PATCH|DELETE .../members` — `members.manage`

## Frontend decisions

Phase 1 UI proves context, not a design system.

- Login establishes authenticated user context
- App shell shows the current organization
- Switcher lists only memberships and reloads `/context`
- Navigation is organization-aware (members/settings depend on current permissions)
- Axios sends the Sanctum bearer token; all tenant calls use `/organizations/{id}/...`

The visual language is a temporary functional shell. It is not the SFU MSA UI and not the final UmmahOS design system.

## Testing

Backend (PHPUnit):

1. Organization creation
2. Multi-organization membership
3. Membership add/update/remove
4. Different roles per organization
5. Organization-scoped permissions
6. Cross-organization read denied
7. Cross-organization update denied
8. Cross-organization delete denied
9. Non-member access denied
10. Invalid organization context rejected
11. IDOR against org, membership, and `/incidents/{id}` URLs
12. Authentication (login, me, logout)
13. Organization switching via context
14. Default Laravel example test

Frontend (Vitest):

- Organization path helper
- Multi-membership switching updates current org, role, and permissions

## Security testing

Covered on the backend:

- Read / update / delete isolation
- Role isolation (admin in A is member in B)
- API isolation (list endpoint does not leak other orgs)
- Direct-ID access
- Invalid slugs and missing ids
- IDOR: `/organizations/B`, `/organizations/A/members/{B-membership}`, `/organizations/B/incidents/123`

## Limitations

- No invitation / join-request workflow; admins add members by user id
- No organization-level settings beyond name, slug, and status
- Future modules are isolation stubs, not product features
- No email verification, password reset, or file uploads
- No production deployment configuration
- Frontend has no visual polish and no final design system
- Local development uses SQLite; production database choice is still open
- Creating an organization is available to any authenticated user

## Future work

Later phases, not this one:

- Deeper Events, Academy, content, incidents, and reports product features
- AI hate analysis
- Evidence packaging and report generation
- Cross-platform pattern detection
- ADAPT integration
- Final UmmahOS design system
- Richer membership lifecycle (invites, ownership transfer)

Organization-scoped announcements, resources, events, Academy, and Community Shield foundations were added in Phase 2. See `PHASE_2.md`.
