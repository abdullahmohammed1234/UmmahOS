# Security boundaries

This is a lightweight audit note for judges and maintainers. It does not claim a formal penetration test.

## Organization isolation

- Community records are organization-scoped.
- API routes take the current organization and authorize against membership.
- Cross-organization IDs are rejected in feature tests (incidents, reviews, academy, ADAPT sessions).

## Authentication and RBAC

- Sanctum token auth for the SPA.
- Permissions are organization-scoped (review, export, outcomes, education patterns, admin content).
- The sidebar only shows tools the current membership can use.

## Privacy

- Members see reporter-visible outcome summaries, not internal reviewer notes.
- Learning recommendations must not expose `source_incident_id` to learners (`LearningRecommendationResource`).
- Reporter notes are part of the review package for authorized reviewers, not a public feed.

## AI handling

- AI output is labeled advisory in the reviewer UI.
- Analysis failures stay failed; they are not treated as confirmations.
- HTML is not rendered from model output via `v-html` in the Vue app.

## Evidence and outcomes

- Evidence export requires incident export permission.
- Outcome management requires outcome permissions.
- Export is a file download — not an automated report to a platform.

## Secrets and debug

- Use `backend/.env` locally; do not commit secrets. `GEMINI_API_KEY` is empty in `.env.example`.
- Demo accounts (`password`) exist only in seeders for evaluation.
- `MSA Platform/` is reference material and is not part of the runtime trust boundary for this app.

## IDOR and unscoped access

Reviewers should continue to treat numeric IDs as untrusted. Existing tests cover denied access when the incident belongs to another organization or the role lacks permission.

## What we did not change in this pass

Security architecture (policies, tenant scoping, AI advisory boundary) was not rewritten. This pass focused on presentation and documentation of existing boundaries.
