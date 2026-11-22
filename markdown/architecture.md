# TOLSTOY — Architecture

## 1. Overview

Flask application using the application-factory pattern, modular blueprints, a service layer, and SQLite. No frontend build step.

## 2. Application Factory

`app/__init__.py` exposes `create_app(config_name=None)`:

- Load config from `app/config.py`.
- Initialize extensions (`app/extensions.py`).
- Register blueprints (API + pages).
- Register error handlers.
- Set up logging.
- Return the app.

`run.py` calls `create_app()` and runs the dev server (planned, not yet implemented).

## 3. Configuration (`app/config.py`)

Classes: `BaseConfig`, `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`.

- Read secrets from environment via `python-dotenv`.
- `SECRET_KEY`, `DATABASE_PATH`, `GEMINI_API_KEY`, `GEMINI_MODEL`, mail settings, `ADMIN_EMAIL`.
- Session cookie settings (`SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_SAMESITE`).
- CSRF settings.
- Never hardcode secrets.

## 4. Extensions (`app/extensions.py`)

Shared instances created without an app: CSRF protection, (optionally) login manager. Initialized in the factory via `init_app`. Keeps circular-import risk low.

## 5. Directory Responsibilities

| Path | Responsibility |
|---|---|
| `app/models/` | DB models/data-access: `user.py`, `story.py`, `system_settings.py` only |
| `app/routes/api/` | JSON API blueprints |
| `app/routes/pages/` | HTML page-rendering blueprints |
| `app/services/` | Business logic: auth, story, token, gemini, email, analytics, maintenance, db viewer |
| `app/security/` | Decorators, role policies, security helpers |
| `app/schemas/` | Request/response validation and serialization |
| `app/templates/` | Jinja2 templates: `public/`, `user/`, `admin/`, `errors/` |
| `app/static/` | `css/`, `js/`, `images/` |
| `database/` | SQLite file, migrations, backups, exports |
| `tests/` | pytest suite |

## 6. Data Flow

Browser → Flask route → schema validation → security (auth/role/CSRF) → service → model/DB → service → schema → JSON/HTML response.

Gemini calls happen only inside the AI service, never in routes or browser JS.

## 7. Blueprints

- `auth_bp` (API + pages)
- `stories_bp`
- `wallet_bp`
- `admin_bp`
- `system_bp` (settings, maintenance)
- `contact_bp`
- `pages_bp` (public/user/admin page rendering)

Each blueprint has a clear prefix and responsibility. Avoid giant files; split by resource when a module exceeds ~300 lines.

## 8. Dependency Boundaries

- Routes depend on services, schemas, security.
- Services depend on models and external clients (Gemini, mail).
- Models depend only on DB access.
- No circular imports: use extension instances + factory init.

## 9. Error Handling

- Centralized error handlers for 400/401/403/404/429/500.
- JSON errors for `/api/` paths; HTML error pages for browser paths.
- Never leak stack traces or secrets in production.
- Log errors server-side with request context (no secrets).

## 10. Logging

- Structured, level-based logging.
- Never log passwords, tokens, API keys, or full story content in production (log IDs/lengths instead).
- Separate audit-relevant events (login, maintenance toggle, balance change) are logged with actor + timestamp.

## 11. Database Connection Lifecycle

- Open connection per request or use a managed connection helper.
- Ensure connections are closed (context manager / teardown).
- Enable foreign keys (`PRAGMA foreign_keys = ON`).
- Use parameterized queries only.

## 12. Adding Features

1. Check `agents.md` and relevant docs.
2. Add schema → service → route → template → test.
3. Do not create new tables.
4. Do not add dependencies without approval.
5. Update docs if contracts change.

## 13. Naming Conventions

See `agents.md` §5. Mandatory across all modules.

## 14. Frontend Architecture

- Jinja2 base templates per area (`base_public.html`, `base_user.html`, `base_admin.html`).
- Reusable macros for buttons, forms, cards, modals, tables, notifications.
- Vanilla JS modules in `app/static/js/` (e.g., `dashboard.js`, `story-editor.js`).
- Central CSS `app/static/css/app.css`.
- Tailwind/Chart.js via CDN in base templates (pin versions before production).

## 15. Security Architecture

See `markdown/security.md`. Auth, CSRF, role policies, ownership checks, input validation, rate limiting, headers. All enforced server-side.

## 16. Token Architecture

See `markdown/database.markdown` and `markdown/api.md`. Atomic balance updates with concurrency control; refill based on stored timestamp; refund on failure.

## 17. Gemini Architecture

Isolated `gemini_service.py`. Configurable model. Structured JSON output with schema validation. Timeout, retry, rate-limit handling. Usage extracted and stored per story.

## 18. Maintenance Mode

Controlled by `tolstoy_system_settings`. Middleware/check on user routes. Admin routes remain accessible. Requires password re-verification to toggle. Existing sessions: block new user actions; document in-progress generation behavior.<|end|><|start|>write to=assistant<|channel|>analysis<|message|>Wrote file successfully: markdown/architecture.md