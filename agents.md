# TOLSTOY — Agent Instructions

> This file is the highest-priority instruction source for any AI coding agent or developer working on TOLSTOY. Read it before reading any other file.

## 1. Project Identity

- **Name:** TOLSTOY
- **Type:** AI Story to Comic Script Generator
- **Output:** Written, structured comic scripts only. **No image generation of any kind.**
- **Repository root:** `TOLSTOY/` (currently flattened into this directory)

## 2. Authoritative Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 (target; current venv is 3.14 — recreate if the pin is required) |
| Backend | Flask (application factory pattern) |
| Database | SQLite at `database/tolstoy.db` |
| DB access | Python `sqlite3` / lightweight data-access layer |
| Templates | Jinja2 |
| Styling | CSS3 (ordinary, hand-written) |
| Optional utility CSS | Tailwind CSS via browser CDN only |
| Frontend scripting | Vanilla JavaScript |
| Charts | Chart.js via browser CDN |
| AI | Google Gemini API |
| Auth | Flask session-cookie authentication |
| CSRF | Flask-WTF / Flask CSRF |
| Testing | pytest + Postman |
| Env config | python-dotenv |
| VCS | Git + GitHub |

Forbidden: React, Vue, Angular, Vite, Webpack, Tailwind CLI, node_modules, npm, package.json, any frontend build step, Django, any additional framework. Do not add a dependency for a few lines of code.

## 3. Mandatory Reading Order

Before making any change, read in this order:

1. `agents.md` (this file)
2. `context.md`
3. `readme.md`
4. All relevant files in `markdown/` (`plan.md`, `architecture.md`, `database.markdown`, `api.md`, `ui_ux.md`, `security.md`, `testing.md`)
5. Inspect the existing code before modifying it.

## 4. Database Rules (Strict)

- Exactly **three** application tables: `tolstoy_users`, `tolstoy_stories`, `tolstoy_system_settings`.
- Every table name starts with `tolstoy_`. No exceptions.
- Never add a table without explicit owner approval.
- Every table must contain the six metadata columns: `created_by`, `created_at`, `updated_by`, `updated_at`, `reserved_slot_1`, `reserved_slot_2`.
- Database file lives only at `database/tolstoy.db`. Never in project root.
- Do not create, modify, or initialize the database during any task unless that task is the approved schema phase.
- Do not store secrets, API keys, or passwords in `tolstoy_system_settings`.

## 5. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Project directory | Uppercase | `TOLSTOY` |
| DB tables | lowercase, prefixed | `tolstoy_users` |
| Python modules | snake_case | `token_service.py` |
| Python functions/variables | snake_case | `generate_comic_script()` |
| Python classes | PascalCase | `StoryService` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_TOKEN_BALANCE` |
| API paths | lowercase | `/api/v1/stories` |
| JSON fields | snake_case | `story_title` |
| CSS classes | kebab-case | `story-card` |
| JS variables/functions | camelCase | `generateStory()` |
| Env vars | UPPER_SNAKE_CASE | `GEMINI_API_KEY` |

Use `tolstoy_` only for table names, not for Python identifiers.

## 6. Architecture Rules

- Use the Flask application factory (`create_app()`).
- Keep route handlers thin; put business logic in `app/services/`.
- Keep Gemini calls only in the dedicated AI service module.
- Keep DB access in model/data-access modules, not in routes.
- Use blueprints for API and page routes.
- Validate requests with `app/schemas/`.
- Enforce auth/authorization in `app/security/` and backend routes — never only in the UI.
- Centralize token calculation on the backend. Never in frontend JS.

## 7. Security Rules

- Hash passwords (never store plaintext). Use Werkzeug/argon2-compatible hashing.
- Flask session-cookie auth; secure cookies; session expiry; logout invalidates session.
- CSRF on every state-changing request.
- Parameterized SQLite queries only. No string-built SQL.
- Jinja2 autoescaping; never render untrusted content with `safe`/`innerHTML`.
- No secrets, keys, or hashes in logs, APIs, or templates.
- Gemini API key only in `.env`.
- Treat user story content as untrusted input. Validate Gemini output before saving.
- Never execute generated content as code.
- Maintenance-mode changes require re-verifying the admin's password on the backend.

## 8. Token Rules

- New users receive 5 application tokens.
- +5 tokens every 48 hours, additive (never reset to 5).
- Token cost calculated server-side from centralized config.
- No negative balances, no double-spend, no duplicate deductions.
- Refund tokens if generation fails after deduction.
- Application tokens ≠ Gemini provider tokens. Track provider usage separately where available.
- No transaction-history endpoint (no approved transaction table).

## 9. Story Rules

- Two lifecycle statuses: `EDITING`, `COMPLETED`. A completed story can return to editing.
- Generation state (pending/processing/succeeded/failed) is separate from lifecycle status.
- Store generated comic script as structured JSON text in one column of `tolstoy_stories`.
- Output is a written comic script (scenes/panels/dialogue/narration) — no images.

## 10. Frontend Rules

- HTML5 + Jinja2 + CSS3 + Vanilla JS only.
- No build step, no bundler, no framework.
- Tailwind and Chart.js only via browser CDN; pin verified versions before production.
- Prefer ordinary CSS for custom styling.

## 11. Testing Rules

- Every new non-trivial logic gets a small test or self-check.
- pytest for automated tests; Postman for API verification.
- Do not claim tests pass without running them.
- Do not mark a phase complete just because files exist.

## 12. How to Work

1. Inspect the code before editing.
2. Make the smallest complete change that fully solves the task.
3. Finish every part the change touches (callers, tests, fixtures).
4. Never add speculative features, options, or "for later" code.
5. Never rename, move, or delete user files without permission.
6. If a requirement is ambiguous, record it in the `Owner Confirmation Required` section rather than guessing.
7. Never silently add tables, dependencies, or files.
8. Update relevant Markdown docs when an approved implementation changes a contract.

## 13. Ambiguity Handling

If a task cannot be done within the approved constraints (e.g., needs a new table), document the limitation and ask for approval. Do not silently implement a workaround that violates the three-table rule.

## 14. Reporting

When finishing work, report: files changed, what was done, what was skipped, and any risk. Never claim success without evidence.<|end|><|start|>advisor to=bash<|channel|>analysis <|constrain|>xml<|message|><rfl:parameter name="command">
cat > context.md <<'EOF'
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
EOF
echo done