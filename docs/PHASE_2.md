# Phase 2 — Community Foundation

## Objective

Prove that UmmahOS is a genuine multi-MSA community platform, not merely a multi-tenant database.

A member should be able to enter their MSA and see that organization's community. An administrator should be able to manage only that organization's basic community content.

Phase 1 remains the architectural foundation:

```
User
 └── Membership (role)
      └── Organization
           └── Organization-scoped modules
```

Phase 2 adds thin vertical slices on top of that model. It does not replace authentication, membership, roles, permissions, organization-scoped routes, or tenant isolation.

## Architecture

UmmahOS remains a decoupled Laravel 12 API + Vue 3 SPA.

```
UmmahOS/
├── MSA Platform/     # pre-existing SFU infrastructure (reference only, untouched)
├── backend/          # Laravel 12 API
├── frontend/         # Vue 3 SPA
└── docs/
```

Every Phase 2 record belongs to exactly one organization. Every Phase 2 endpoint lives under:

```
/api/v1/organizations/{organization}/...
```

`EnsureOrganizationMembership` remains the security boundary. The client-supplied organization id is a routing hint only. Nested records are loaded through the current organization (`$organization->announcements()`, `events()`, and so on). A record id from Organization B requested through Organization A returns `404`.

## Modules implemented

Thin vertical slices only.

| Area | Member | Admin |
| --- | --- | --- |
| Member dashboard | Organization overview aggregating Phase 2 data | — |
| Admin dashboard | — | Counts + navigation |
| Announcements | List and view published notices | Create, edit, publish/unpublish, delete |
| Resources | Browse and open external links | CRUD |
| Events | View community events | CRUD |
| Academy | View published courses | CRUD + publish/unpublish |
| Community Shield | Submit a private concern | List, view, update status |

Intentionally not built: EMS/ticketing/payments, LMS lessons/quizzes/progress, CMS/file storage, AI moderation, notifications, analytics.

## Database changes

New organization-owned tables, each with `organization_id` → `organizations.id` and indexes:

### `announcements`

`id`, `organization_id`, `title`, `body`, `published_at` (nullable), `created_by`, timestamps

Members only see rows where `published_at` is set and `<= now()`.

### `resources`

`id`, `organization_id`, `title`, `description`, `url`, `category`, `created_by`, timestamps

URL references only. No file storage.

### `events`

`id`, `organization_id`, `title`, `description`, `location`, `starts_at`, `ends_at`, `registration_url`, `created_by`, timestamps

Community calendar only. No tickets, payments, QR, waitlists, or check-in.

### `courses`

`id`, `organization_id`, `title`, `description`, `status` (`draft` \| `published`), `created_by`, timestamps

Foundation/entry point only. No lessons, quizzes, grading, or enrollment.

### `incidents`

`id`, `organization_id`, `reported_by`, `category`, `description`, `status` (`open` \| `reviewing` \| `resolved`), timestamps

Categories: `safety`, `harassment`, `hate`, `community_concern`, `other`.

Shared patterns reused from Phase 1:

- `BelongsToOrganization` + `scopeForOrganization()`
- `HasCreator` for `created_by`
- Query through the current organization, never a client-supplied org id alone

## API routes

All of the following require Sanctum authentication and organization membership.

```
GET    /api/v1/organizations/{organization}/dashboard
GET    /api/v1/organizations/{organization}/admin/dashboard

GET    /api/v1/organizations/{organization}/announcements
POST   /api/v1/organizations/{organization}/announcements
GET    /api/v1/organizations/{organization}/announcements/{announcement}
PATCH  /api/v1/organizations/{organization}/announcements/{announcement}
DELETE /api/v1/organizations/{organization}/announcements/{announcement}

GET    /api/v1/organizations/{organization}/resources
POST   /api/v1/organizations/{organization}/resources
GET    /api/v1/organizations/{organization}/resources/{resource}
PATCH  /api/v1/organizations/{organization}/resources/{resource}
DELETE /api/v1/organizations/{organization}/resources/{resource}

GET    /api/v1/organizations/{organization}/events
POST   /api/v1/organizations/{organization}/events
GET    /api/v1/organizations/{organization}/events/{event}
PATCH  /api/v1/organizations/{organization}/events/{event}
DELETE /api/v1/organizations/{organization}/events/{event}

GET    /api/v1/organizations/{organization}/courses
POST   /api/v1/organizations/{organization}/courses
GET    /api/v1/organizations/{organization}/courses/{course}
PATCH  /api/v1/organizations/{organization}/courses/{course}
DELETE /api/v1/organizations/{organization}/courses/{course}

POST   /api/v1/organizations/{organization}/incidents
GET    /api/v1/organizations/{organization}/incidents
GET    /api/v1/organizations/{organization}/incidents/{incident}
PATCH  /api/v1/organizations/{organization}/incidents/{incident}
```

There are no global `/api/v1/events`, `/announcements`, or `/incidents` endpoints.

Phase 1 isolation stubs remain only for unimplemented namespaces: `content` and `reports`.

## Authorization model

Phase 1 RBAC is reused. No second permission system.

Roles are still organization-scoped templates:

- `member` — `*.view` in that organization
- `admin` — all permissions in that organization

Module mapping:

| Module | View | Manage |
| --- | --- | --- |
| Announcements | `content.view` | `content.manage` |
| Resources | `content.view` | `content.manage` |
| Events | `events.view` | `events.manage` |
| Academy | `courses.view` | `courses.manage` |
| Community Shield review | — | `incidents.manage` |
| Member dashboard | `organization.view` | — |
| Admin dashboard | — | `organization.manage` |

Community Shield submit is a membership action, not `incidents.manage`. Any member of the current organization can `POST /incidents`. They cannot list or view incidents, including their own after submission (confirmation is in the create response). Admins list, view, and update status only inside their organization.

Unpublished announcements and draft courses are hidden from members (`404` on direct id access).

A user who is a member in Alpha and an admin in Beta has member capabilities in Alpha and admin capabilities in Beta. That Phase 1 behavior is unchanged.

## Tenant isolation

1. Membership gate on every organization-scoped route.
2. Permission gate for manage vs view.
3. Nested records loaded through `$organization->{relation}()->whereKey($id)`.
4. No global admin bypass.
5. Dashboards aggregate only the current organization's rows.

Cross-organization reads, updates, and deletes return `403` (not a member of that org) or `404` (id does not belong to the current org).

## Demo data

Existing Phase 1 users and organizations are unchanged.

| Email | Memberships |
| --- | --- |
| `alpha.admin@example.com` | Alpha admin |
| `alpha.member@example.com` | Alpha member |
| `beta.admin@example.com` | Beta admin |
| `multi.user@example.com` | Alpha member + Beta admin |
| `outsider@example.com` | none |

Password: `password`.

Alpha and Beta now have intentionally different community content:

- **Alpha:** Friday gathering notice, welcome notice, unpublished officer memo, prayer timetable, new-student guide, community iftar, brothers hike, published Qur'an foundations course, draft leadership course, open Community Shield report from `alpha.member@example.com`
- **Beta:** elections notice, sisters study circle, housing list, masjid map, sports day, published seerah circle, draft fiqh workshop, reviewing Community Shield report from `multi.user@example.com`

Switching `multi.user@example.com` from Alpha to Beta changes both the visible community and the available admin navigation.

## Frontend

Vue 3, TypeScript, Vite, Pinia, Axios. Phase 1 auth store, organization store, organization switcher, and application shell are reused.

Member navigation:

```
Home · Announcements · Resources · Events · Academy · Community Shield
```

Admin navigation (only when the current organization role includes `organization.manage`):

```
Organization
 ├── Dashboard
 ├── Members
 ├── Announcements
 ├── Events
 ├── Resources
 ├── Academy
 └── Community Shield
```

There are no global admin pages and no super-admin.

## Tests

Backend PHPUnit: **73 passed / 282 assertions** (Phase 1 suite still included).

Phase 2 coverage:

- Announcements: member view, unpublished hidden, cross-org blocked, admin CRUD, member cannot manage
- Resources: member view, cross-org blocked, admin CRUD, member cannot manage
- Events: member view, cross-org blocked, admin CRUD, member cannot manage
- Academy: published visible, drafts hidden from members, cross-org blocked, admin publish/unpublish/CRUD
- Community Shield: member submit, member cannot browse reports, cross-org blocked, admin review/status update
- Dashboards: member and admin aggregates are current-organization only; members cannot open the admin dashboard
- Critical multi-org proof: `multi.user` as Alpha member sees only Alpha data and cannot manage; as Beta admin sees only Beta data and can manage

Frontend Vitest: **3 passed**. Production frontend build succeeded.

## Known limitations

- Resources are external URLs only; there is no upload/storage system
- Events have no registration, ticketing, or attendance
- Academy has no lessons, progress, or certificates
- Community Shield has no workflows, email, escalation, or AI
- Members cannot later retrieve their own submitted incidents (confirmation only)
- Announcements and resources share the Phase 1 `content.*` permission pair
- UI is functional product UI, not the final UmmahOS design system

## What was intentionally deferred

- Complete EMS (Square, payments, QR tickets, waitlists, check-in, refunds)
- Complete LMS (lessons, quizzes, grading, assignments, certificates)
- Complete CMS and file storage
- Automated moderation / AI hate analysis
- Notifications and email workflows
- Analytics
- Invitations and richer membership lifecycle
- Production infrastructure

Later phases can deepen individual modules. Phase 2 only establishes the community foundation inside the Phase 1 multi-MSA boundary.
