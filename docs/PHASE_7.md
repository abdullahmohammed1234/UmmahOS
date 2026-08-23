# Phase 7 — Incident Evidence Package & Export Report

## Objective

Turn a reviewed Community Shield incident into a complete, portable, structured **Incident Evidence Package** that preserves:

- incident metadata and source evidence
- AI analysis and uncertainty (advisory)
- human review and decision (authoritative)
- evidence references
- recommended reporting route
- safety / privacy notes

Then export that package as:

- structured **JSON**
- professional **PDF**

Phase 7 does **not** submit reports to external platforms. It prepares evidence and reporting guidance for human use.

AI analysis remains advisory and human review remains authoritative.

## Architecture

```
Controller
   ↓
Authorization (incidents.export | incidents.manage)
   ↓
IncidentEvidencePackageService
   ↓
IncidentEvidencePackage DTO
   ├── JSON serializer
   └── EvidencePackagePdfRenderer (mPDF)

ReportingRouteService  ← config/community_shield_reporting.php
SafetyPrivacyGuidanceService ← config/community_shield_safety.php
```

Packages are generated dynamically from source-of-truth records:

- `incidents`
- `incident_replies`
- `incident_related_items`
- `incident_ai_analyses`
- `incident_reviews`
- `incident_review_actions`
- `incident_context_requests`

No duplicated incident field store. Optional immutable export audit:

- `incident_evidence_exports` (`format`, `package_version`, `incident_reference`, `exported_by`, `created_at`)

Export generation is read-only and does not mutate incident status, review outcome, AI analysis, notes, or classification.

## Package schema (v1)

Stable contract fields:

- `package` — schema/package version, generated_at, generated_by, organization, source_incident_updated_at, hierarchy labels
- `incident` — reference, platform, content type, visibility, dates, status, review outcome, source URL
- `evidence` — original item, surrounding context, replies, related items, language, reporter notes, reported classification
- `ai_analysis` — current + previous summaries, uncertainty block, advisory disclaimer
- `human_review` — status/outcome/classification/notes/escalation/context requests/history/decision
- `references` — original / reply / related item references (captured data only)
- `reporting_route` — platform guidance (informational; `automatic_submission: false`)
- `safety_privacy_notes` — centralized operational guidance
- `disclaimers` — AI / human / reporting

Missing values are explicit (`null` or `"Not provided"`). The generator never invents URLs, timestamps, replies, related items, or human decisions.

## API

Organization-scoped endpoints:

| Method | Path | Permission |
| --- | --- | --- |
| GET | `/community-shield/reports/{report}/evidence-package` | `incidents.manage\|incidents.export` |
| GET | `/community-shield/reports/{report}/evidence-package.json` | export |
| GET | `/community-shield/reports/{report}/evidence-package.pdf` | export |

Filenames:

- `community-shield-incident-{reference}.json`
- `community-shield-incident-{reference}.pdf`

Nested report IDs are resolved through the organization. Cross-organization IDOR is blocked.

## Reporting routes

Maintainable configuration in `config/community_shield_reporting.php` for:

X, YouTube, TikTok, Reddit, Discord, Telegram, WhatsApp, Other

Guidance is generic and non-authoritative. Exact UI labels are avoided where workflows may change. `Other` receives generic guidance only.

## Safety / privacy

Centralized notes in `config/community_shield_safety.php`.

Exports deliberately omit:

- passwords / tokens / API keys
- unrelated memberships / organizations
- internal permission maps
- accidental Eloquent model dumps

Reviewer notes and review history are available only to authorized exporters (reviewers/admins). Members cannot export internal packages.

External references are treated as untrusted captured data:

- not fetched
- not scraped
- not embedded as remote content in PDFs

## PDF

Server-side rendering via `mpdf/mpdf` with Unicode/Arabic support (`dejavusans`, auto language/font).

PDF sections visually distinguish:

- SOURCE EVIDENCE
- AI CONTEXT ANALYSIS — ADVISORY
- HUMAN REVIEW — AUTHORITATIVE
- REPORTING GUIDANCE
- SAFETY & PRIVACY

HTML/markup in incident content is escaped. Remote images/scripts are not loaded.

## Permissions

New permission: `incidents.export`

Granted to:

- Community Safety Reviewer
- Organization Admin (via all-permissions sync)

Members do not receive export permission.

## Frontend

Review detail page includes an **Evidence Package** section for authorized users:

- View Evidence Package (structured preview)
- Export JSON
- Export PDF
- loading / ready / error feedback

No automatic “Submit to platform” actions.

## Demo

Phase 6 demos preserved. Phase 7 expands the resolved Alpha Reddit confirmed incident into a complete package demo with:

- original item + context + replies + related item
- AI analysis + uncertainty
- confirmed human review + multi-step history
- fulfilled context request
- reporting route for Reddit

Also retained:

- Alpha X flagship (unreviewed package path)
- Alpha Discord uncertain outcome
- Alpha Telegram escalated workflow
- Beta Arabic Discord content (Unicode/PDF coverage)

## Testing

Backend feature coverage includes package contents, AI/human separation, missing-data handling, org isolation/IDOR, read-only export, JSON safety, PDF content-type/non-empty output, reporting routes for all platforms, and packaging of stored Gemini analyses without new provider calls.

Frontend coverage includes export visibility, preview, JSON/PDF export, loading/error states, unreviewed and AI-unavailable displays.

## Limitations

- No automatic external reporting
- No platform API integrations or scraping
- No separate “redacted external” export mode beyond privacy notes (single internal package)
- Reporting guidance is informational and may lag platform UI changes
- Package version is derived from source timestamps (deterministic), not a full VCS history

## Future work (not Phase 7)

- Advanced pattern detection / cross-MSA intelligence
- Automated reporting integrations
- Public incident dashboards / org-wide safety analytics
- Optional redacted external export profiles

## Explicit non-goals

Phase 8 was not started. `MSA Platform/` was not modified.
