# Pre-existing materials

This document separates **pre-existing infrastructure** from **fresh UmmahOS work** created during the Harvest Anti-Muslim Hate Hackathon development window.

## 1. Repository

Pre-existing source repository:

https://github.com/abdullahmohammed1234/MSA-Platform.git

Cloned, unmodified, into:

`UmmahOS/MSA Platform/`

That directory is **pre-existing infrastructure only**. It is not the UmmahOS application root.

## 2. What existed before the Harvest fresh-work start

The SFU MSA Platform already existed as a production-oriented decoupled monolith:

- Laravel 12 API backend (`MSA Platform/backend`)
- Vue 3 + TypeScript + Vite + Pinia SPA (`MSA Platform/frontend`)
- MySQL in development/production, SQLite in-memory for PHPUnit
- Laravel Sanctum bearer-token authentication
- Custom RBAC (roles, permissions, role-user pivots, permission middleware, policies)
- Service / repository / policy architecture
- PHPUnit feature and unit tests
- CMS, Dawah Academy, Event Management System (EMS), analytics, and website modules
- SFU-specific authentication rules, branding, and deployment configuration

There was **no multi-organization / multi-MSA model**. Users were attached to one implicit organization: SFU MSA. "Member" was a global role, not an organization membership.

The original repository does not include a root `LICENSE` file. Its Laravel backend `composer.json` declares the MIT license. That attribution is preserved here and in the cloned repository.

## 3. Infrastructure used as reference / reusable material

Inspected and used as architectural reference only:

| Area | Pre-existing source | How it was used |
| --- | --- | --- |
| Backend framework | Laravel 12, PHP 8.2 | New UmmahOS backend created independently with the same family |
| API auth | Laravel Sanctum bearer tokens | Reused the pattern, not the SFU controllers |
| Auth HTTP shape | `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` | Adapted into UmmahOS `/api/v1/auth/*` |
| Custom RBAC models | `Role`, `Permission`, `permission_role` | Adapted into global role *templates* assigned through memberships |
| Permission middleware | pipe-separated permission checks | Adapted to organization context |
| Thin controllers + services | `AuthService`, authorization services | Same layering in `UmmahOS/backend` |
| JSON resources | `UserResource` | New UmmahOS resources include memberships |
| Testing | PHPUnit + `RefreshDatabase` + SQLite `:memory:` | Same test approach |
| Frontend stack | Vue 3, Vue Router, Pinia, Axios, Vite, TypeScript | New SPA created independently |
| API client pattern | Axios interceptor + stored bearer token | Adapted without SFU academy/EMS clients |

No MSA Platform PHP, Vue, or configuration files are imported at runtime.

## 4. Architecture patterns reused

- Decoupled API backend + SPA frontend
- Sanctum personal access tokens in `Authorization: Bearer`
- Custom RBAC rather than Spatie
- Form requests, API resources, and service classes
- Route middleware aliases for authorization
- Feature tests for auth, authorization, and isolation
- Frontend Pinia stores for session state
- Organization-aware frontend requests that never treat the client as the security boundary

The important **change** from the pre-existing pattern:

- MSA Platform evaluates roles and permissions **globally**
- UmmahOS evaluates roles and permissions **inside the current organization**

Admin in MSA Alpha is not admin in MSA Beta.

## 5. Components newly implemented in UmmahOS

Fresh work lives only in:

- `UmmahOS/backend/`
- `UmmahOS/frontend/`
- `UmmahOS/docs/`

Newly implemented:

- `Organization` model, migration, factory, and API
- `Membership` model and organization-scoped membership API
- Organization-aware `Role` / `Permission` assignment
- Active organization context (`/organizations/{organization}/context`)
- Tenant isolation middleware
- `BelongsToOrganization` foundation for later modules
- Phase 1 frontend: login, current organization, organization switching, members, settings
- Phase 1 backend and frontend tests
- This file and `PHASE_1.md`

## 6. SFU-specific functionality intentionally not carried forward

Do **not** treat the following as UmmahOS product behavior:

- Single implicit SFU MSA tenant
- `@sfu.ca` volunteer/login email enforcement
- Production hostnames `sfumsa.ca` / `api.sfumsa.ca`
- Mail identity "SFU MSA" / `no_reply@sfu.ca`
- Dawah Academy, CMS website, EMS, Square payments
- SFU student-number fields
- Campus prayer-time / SFU-branded content
- Global `super-admin` / `director` / `dawah-coordinator` / `mentor` / `volunteer` role set
- cPanel deployment paths for the SFU site
- Any production credentials, tokens, private member information, or live SFU data

UmmahOS development seed data is synthetic:

- Demo MSA Alpha
- Demo MSA Beta
- Example users at `@example.com`

No SFU production database was connected. No private SFU data was copied.

## Boundary reminder

**PRE-EXISTING:** `UmmahOS/MSA Platform/`

**FRESH:** `UmmahOS/backend/`, `UmmahOS/frontend/`, `UmmahOS/docs/`
