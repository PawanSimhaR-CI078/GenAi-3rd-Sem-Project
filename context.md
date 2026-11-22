# TOLSTOY — Project Context

## 1. Identity

- **Name:** TOLSTOY
- **Type:** AI Story to Comic Script Generator
- **Output:** Written, structured comic scripts only. No image generation.

## 2. Purpose

Users submit a story idea or story content. TOLSTOY uses Google's Gemini API to transform that input into a structured comic script (scenes, panels, dialogue, narration). Administrators manage users, content, settings, and system health.

## 3. Users

- **Normal users:** register, log in, create/edit stories, generate scripts, manage token balance, contact admin.
- **Administrators:** two initial accounts (role assignment pending owner confirmation) with analytics, user/story management, database viewer, settings, maintenance mode.

## 4. Core Functionality

1. Authentication (register, login, logout, sessions).
2. Story management (create, read, update, delete/archive, status changes).
3. Comic script generation via Gemini (structured JSON output).
4. Application token system (initial 5, +5 every 48h, deduction per generation, refund on failure).
5. Administrator dashboard with ~5–6 charts.
6. Email contact to admin.
7. Maintenance mode.

## 5. Token System

- Initial allocation: 5 tokens per new user.
- Refill: +5 every 48 hours, additive, based on stored timestamp.
- Deduction: server-side, atomic, before generation.
- Refund on failed generation.
- Application tokens are internal credits; Gemini tokens are provider-reported usage. They are not interchangeable.

## 6. Story Lifecycle

- Statuses: `EDITING`, `COMPLETED`. Completed can return to Editing.
- Generation state (pending/processing/succeeded/failed) is distinct from lifecycle status.
- Generated script stored as structured JSON text in `tolstoy_stories`.

## 7. Database (Strict)

Exactly three tables, all prefixed `tolstoy_`:

1. `tolstoy_users` — accounts (users + admins), token balance, refill timestamp.
2. `tolstoy_stories` — one row per story + generated script + usage.
3. `tolstoy_system_settings` — global config (key/value, no secrets).

Every table has six metadata columns: `created_by`, `created_at`, `updated_by`, `updated_at`, `reserved_slot_1`, `reserved_slot_2`.

DB file: `database/tolstoy.db`. No tables created yet.

## 8. Technology Stack

See `agents.md` §2. Python 3.12 target, Flask, SQLite, Jinja2, CSS3, Vanilla JS, Gemini, pytest, Postman. No Node/npm/build step.

## 9. Frontend

HTML5 + Jinja2 + CSS3 + Vanilla JS. Tailwind and Chart.js via CDN only. Assets in `app/static/`. No bundler.

## 10. Security Expectations

Session-cookie auth, CSRF on state changes, hashed passwords, parameterized SQL, Jinja autoescaping, secrets in `.env`, backend-enforced authorization, no password hashes exposed.

## 11. API

REST under `/api/v1/`. Consistent JSON envelope `{success, message, data}` / `{success, message, error:{code}}`. Session cookies + CSRF.

## 12. Key Design Decisions

- Flask application factory + blueprints.
- Service layer for business logic; Gemini isolated in one service.
- Three-table DB limit; limitations documented rather than worked around.
- No transaction-history endpoint (no approved transaction table).
- Dynamic page-permission toggles limited by three-table constraint; fixed role-based policy instead.

## 13. Known Limitations

- No image generation.
- No complete provider billing history (only per-story usage stored).
- No transaction ledger.
- Dynamic page-permission management requires a permissions table (not approved).
- Current venv is Python 3.14.10, not 3.12.
- Node.js/npm not installed (intentionally not required).

## 14. Unresolved Owner Decisions

See `Owner Confirmation Required` sections in the Markdown docs. Includes auth identifier, admin role assignment, email config, Gemini model, token cost, refill accumulation, deletion policy, editing-after-completion, dynamic page permissions, JSON output schema, editable user fields.

## 14b. Owner Confirmation Required

1. Auth identifier (username/display name/phone).
2. Admin role assignment (ADMIN vs SUPER_ADMIN) for two initial admins.
3. Whether SUPER_ADMIN has extra privileges.
4. Admin email address and SMTP provider.
5. Exact Gemini model.
6. Application token cost per generation/regeneration.
7. Refill accumulation across missed periods.
8. Deletion policy (soft vs hard).
9. Editing after completion rules.
10. Dynamic page permissions need.
11. Exact story JSON output schema.
12. Admin-editable user fields.

Each: question, why it matters, options, recommended approach, dependent implementation work. See `markdown/plan.md` §6.

## 15. Documentation Map

- `agents.md` — agent rules (read first)
- `context.md` — this file
- `readme.md` — setup guide
- `markdown/plan.md` — roadmap
- `markdown/architecture.md` — technical architecture
- `markdown/database.markdown` — DB schema
- `markdown/api.md` — API spec
- `markdown/ui_ux.md` — frontend spec
- `markdown/security.md` — security spec
- `markdown/testing.md` — testing strategy