# TOLSTOY — Security Specification

## 1. Authentication

- Passwords hashed with strong algorithm (Werkzeug `generate_password_hash` or argon2); never plaintext.
- Login verifies hash; constant-time comparison.
- Session created on success; session cookie `HttpOnly`, `Secure` (prod), `SameSite=Lax` (or Strict).
- Session expiry configured; logout clears server-side session and cookie.
- Inactive accounts cannot log in.

## 2. Authorization

- Roles: `USER`, `ADMIN`, `SUPER_ADMIN`.
- Backend decorators enforce both role and capability on every protected route.
- Capabilities are stored as JSON in `tolstoy_system_settings` (`role_permissions`); no fourth table.
- SUPER_ADMIN always holds every capability. Only a role with `roles_manage` can edit the matrix,
  and it cannot revoke its own management access.
- Session role and active status are re-read from the database on every request, so role changes take effect immediately.
- Ownership check: user may only access/modify own stories (by `user_id`); changing URL ID must not bypass.
- Admin endpoints require ADMIN+.
- Admin token adjustments are increases only; the API rejects sets and negative deltas.
- Role changes and maintenance toggles require password re-entry.
- At least one active SUPER_ADMIN must always remain; self-demotion and self-deactivation are blocked.

## 3. CSRF

- CSRF protection on all state-changing requests.
- Token available via `GET /api/v1/auth/csrf` for Postman/JS.
- Frontend forms include CSRF token.
- Validate on server; reject missing/invalid with 403.

## 4. Input Validation

- Validate all JSON bodies against schemas (`app/schemas/`).
- Validate query params and path params (types, ranges).
- Parameterized SQLite queries only; no string interpolation.
- Validate story content length and JSON output schema.
- Sanitize email inputs; prevent header injection.

## 5. XSS and Browser Security

- Jinja2 autoescaping enabled (default).
- Never use `|safe` on untrusted content.
- Avoid `innerHTML` with untrusted data; use `textContent` or sanitize.
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, CSP (define during implementation).
- Rate limiting on auth, contact, generation endpoints.

## 6. Secrets

- `.env` holds all secrets; `.env` gitignored; `.env.example` has placeholders only.
- Never commit keys, passwords, DB files, backups, exports.
- Never log secrets or password hashes.

## 7. API Security

- Request size limits.
- Consistent error responses without internal details.
- No password hashes or secrets in any response.
- Rate limiting where appropriate (auth, contact, generate).

## 8. AI-Specific Security

- User story content is untrusted input; do not let it override system prompt/output requirements.
- Gemini API key only server-side.
- Validate Gemini output (JSON schema) before saving.
- Do not execute generated content.
- Timeouts and resource limits on provider calls.
- Do not log full story content or API keys.

## 9. Maintenance Mode

- Toggle requires re-entering admin password; backend verifies against hash.
- A single global request guard blocks all user pages and APIs, not only story routes.
- Cannot be bypassed by frontend.
- Prevents permanent lockout: admin login, admin pages and admin APIs remain reachable.
- Bootstrap seeds settings only when absent so a restart cannot silently bring the system online.

## 10. Database Security

- DB file not in project root; backups/exports gitignored.
- DB viewer omits password_hash entirely, masks secret settings, and is read-only.
- Table names are whitelisted; search columns are fixed per table and parameterized.
- No direct SQL from user input.

## 11. Logging

- Log auth events, balance changes, maintenance toggles with actor + timestamp.
- Never log secrets, hashes, or full content.<|end|><|start|>write to=assistant<|channel|>analysis<|message|>Wrote file successfully: markdown/security.md