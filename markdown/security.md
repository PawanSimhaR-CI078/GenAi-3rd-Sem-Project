# TOLSTOY — Security Specification

## 1. Authentication

- Passwords hashed with strong algorithm (Werkzeug `generate_password_hash` or argon2); never plaintext.
- Login verifies hash; constant-time comparison.
- Session created on success; session cookie `HttpOnly`, `Secure` (prod), `SameSite=Lax` (or Strict).
- Session expiry configured; logout clears server-side session and cookie.
- Inactive accounts cannot log in.

## 2. Authorization

- Roles: `USER`, `ADMIN`, `SUPER_ADMIN`.
- Backend decorators enforce role on every protected route.
- Ownership check: user may only access/modify own stories (by `user_id`); changing URL ID must not bypass.
- Admin endpoints require ADMIN+.
- Maintenance mode: user routes blocked; admin routes remain accessible.

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
- Cannot be bypassed by frontend.
- Prevents permanent lockout: at least one admin path remains to disable.

## 10. Database Security

- DB file not in project root; backups/exports gitignored.
- DB viewer strips password_hash and secret columns.
- No direct SQL from user input.

## 11. Logging

- Log auth events, balance changes, maintenance toggles with actor + timestamp.
- Never log secrets, hashes, or full content.<|end|><|start|>write to=assistant<|channel|>analysis<|message|>Wrote file successfully: markdown/security.md