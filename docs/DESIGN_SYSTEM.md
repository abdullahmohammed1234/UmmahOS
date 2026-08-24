# UmmahOS Design System

Phase 11 establishes a centralized visual identity for UmmahOS. Tokens live in `frontend/src/styles/tokens.css` and global component styles in `frontend/src/styles/components.css`.

## Brand

| Element | Value |
|---------|-------|
| Product name | **UmmahOS** |
| Positioning | Community infrastructure for Muslim student organizations |
| Community Shield tagline | Preserve context. Protect people. Respond responsibly. |
| Core principle | **AI assists. Humans decide.** |

## Color tokens

| Token | Purpose | Value |
|-------|---------|-------|
| `--primary` | Brand actions, active nav | `#1a6b4a` (deep emerald) |
| `--primary-hover` | Button hover | `#145a3d` |
| `--primary-soft` | Subtle backgrounds | `rgba(26, 107, 74, 0.1)` |
| `--secondary` | Secondary text emphasis | `#2d4a3e` |
| `--accent` | Restrained accent | `#c17f3a` |
| `--background` | Page background | `#f5f2eb` (warm neutral) |
| `--surface` | Cards, panels | `#fffdf9` |
| `--surface-elevated` | Inputs, elevated cards | `#ffffff` |
| `--border` | Borders, dividers | `#ddd6c8` |
| `--text-primary` | Headings, body | `#1a2420` (dark slate) |
| `--text-secondary` | Secondary copy | `#3d4f47` |
| `--text-muted` | Hints, metadata | `#6b7a72` |
| `--success` | Positive states | `#1a6b4a` |
| `--warning` | Uncertainty, caution | `#9a6b00` |
| `--danger` | Errors, destructive | `#9b2c2c` |
| `--info` | AI advisory contexts | `#2563a8` |

**Do not** hardcode semantic colors in individual components. Use tokens or semantic utility classes (`.badge.warning`, `.ai-block`, `.human-block`).

## Typography

- **Font:** Inter (Google Fonts) with system-ui fallback
- **Arabic/Unicode:** System font stack handles Arabic script; UI remains English-primary
- **Scale:** `--text-xs` through `--text-4xl`
- **Weights:** 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

## Spacing & layout

- Spacing scale: `--space-1` (4px) through `--space-16` (64px)
- Sidebar width: `--sidebar-width` (260px)
- Content max: `--content-max` (1120px), page max: `--page-max` (960px)

## Radius & shadows

- Radius: `--radius-sm` (8px) to `--radius-full` (pill)
- Shadows: `--shadow-sm`, `--shadow-md`, `--shadow-lg`

## Focus & motion

- Focus ring: `--focus-ring` (3px primary glow)
- Transitions: `--transition-fast/base/slow`
- Respects `prefers-reduced-motion: reduce`

## Global components

CSS classes in `components.css`:

| Class | Use |
|-------|------|
| `.button`, `.button.secondary`, `.button.danger` | Actions |
| `.badge`, `.badge.success/warning/danger/info` | Status labels |
| `.panel`, `.content`, `.card-link` | Cards |
| `.field` | Form fields |
| `.ai-advisory-banner`, `.ai-block` | AI analysis (advisory) |
| `.human-block` | Human review decisions |
| `.uncertainty-banner` | High uncertainty states |
| `.workflow`, `.workflow-step` | Process diagrams |
| `.timeline`, `.timeline-item` | Outcome tracking |
| `.before-after` | Landing page comparisons |
| `.stat-grid`, `.stat-card` | Dashboard metrics |
| `.skeleton` | Loading placeholders |

## Vue UI components

Reusable components in `frontend/src/components/ui/`:

- `PageHeader.vue` — Page titles with eyebrow and description
- `WorkflowSteps.vue` — Vertical/horizontal process steps
- `Timeline.vue` — Outcome and report progress
- `EmptyState.vue` — Empty list placeholders
- `LoadingState.vue` — Loading text and skeletons

Landing storytelling components live in `frontend/src/components/landing/`. Community Shield context visualization: `ContextRelationshipView.vue`.

## AI vs human visual distinction

| Context | Visual treatment |
|---------|------------------|
| AI analysis | Blue left border (`.ai-block`), info banner, "advisory" language |
| Human review | Green left border (`.human-block`), primary soft background |
| Uncertainty | Warning banner (`.uncertainty-banner`), never alarmist |

Never display AI output as "VERDICT" or "CONFIRMED HATE" unless it is an explicit human-authored decision.

## Changing the theme

Edit `frontend/src/styles/tokens.css`. Legacy aliases (`--bg`, `--panel`, `--ink`, `--muted`, `--line`, `--accent`) map to new tokens for backward compatibility with existing scoped styles.
