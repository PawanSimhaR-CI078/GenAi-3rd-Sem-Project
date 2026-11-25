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

When finishing work, report: files changed, what was done, what was skipped, and any risk. Never claim success without evidence.
