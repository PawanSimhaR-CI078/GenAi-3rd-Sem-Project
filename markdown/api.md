# TOLSTOY — API Specification

## 1. Base

- Base URL: `/api/v1/`
- Content-Type: `application/json`
- Auth: Flask session cookie.
- CSRF: required on all state-changing requests (`POST`, `PATCH`, `PUT`, `DELETE`).
- Response envelope:

Success:
```json
{"success": true, "message": "OK", "data": {}}
```

Error:
```json
{"success": false, "message": "Human readable", "error": {"code": "ERROR_CODE"}}
```

## 2. Authentication

### POST /api/v1/auth/register

- Purpose: create a normal user account.
- Auth: none. CSRF: yes.
- Body:
```json
{"username": "alice", "password": "Str0ng!Pass", "display_name": "Alice", "phone_number": "+1..."}
```
- Validation: username unique, password min length + complexity, phone optional/unique.
- Success 201: `{"success": true, "message": "Registered", "data": {"user_id": 1}}`
- Errors: 400 validation, 409 duplicate username/phone.

### POST /api/v1/auth/user/login

- Body: `{"username": "alice", "password": "..."}` (provisional identifier).
- Success 200: sets session cookie; `data: {"user_id":1,"role":"USER"}`.
- Errors: 401 invalid credentials, 403 inactive account.

### POST /api/v1/auth/admin/login

- Same shape, requires role ADMIN/SUPER_ADMIN.
- Errors: 401, 403 (not an admin).

### POST /api/v1/auth/logout

- Auth: required. CSRF: yes.
- Success 200: clears session.

### GET /api/v1/auth/me

- Auth: required.
- Success 200: `{"user_id", "username", "display_name", "role", "token_balance", "is_active"}`. Never password_hash.

### GET /api/v1/auth/csrf

- Returns CSRF token for Postman/clients: `{"csrf_token": "..."}`.

## 3. Stories

### GET /api/v1/stories

- Auth: required (USER+).
- Query: `status` (EDITING/COMPLETED), `page`, `per_page`.
- Returns current user's stories only.

### POST /api/v1/stories

- Body:
```json
{"title": "My Story", "content": "...", "character_gender": "female", "target_audience": "children", "desired_length": "short", "language": "en"}
```
- Success 201: `{"story_id": 1}`.

### GET /api/v1/stories/{story_id}

- Owner or admin. 404 if not found, 403 if not owner.

### PATCH /api/v1/stories/{story_id}

- Owner only. Partial update of editable fields.
- Body subset of create fields + `generated_script` (admin/system only; users edit via editor fields).

### POST /api/v1/stories/{story_id}/generate

- Auth: owner. CSRF: yes.
- Flow: validate → check balance → deduct → call Gemini → save script + usage → return.
- Success 200: `{"story_id":1,"generated_script":{...},"tokens_consumed":N,"gemini_input_tokens":X,"gemini_output_tokens":Y}`.
- Errors: 402 insufficient tokens, 429 provider rate limit, 504 timeout, 502 provider error (tokens refunded).

### POST /api/v1/stories/{story_id}/regenerate

- Same as generate; replaces script. Token cost applies.

### PATCH /api/v1/stories/{story_id}/status

- Body: `{"story_status": "COMPLETED"}` (or EDITING).
- Owner only.

### DELETE /api/v1/stories/{story_id}

- Owner or admin. Policy (soft vs hard) pending owner confirmation. Default provisional: soft-delete (`is_deleted=1`).

## 4. Wallet

### GET /api/v1/wallet

- Auth: required.
- Returns: `{"token_balance": 5, "last_token_refill_at": "...", "next_refill_at": "...", "refill_amount": 5, "refill_interval_hours": 48}`.
- No transaction history (no approved transaction table).

## 5. Administrator

All require role ADMIN/SUPER_ADMIN. Each endpoint also requires the matching capability
(`analytics`, `users_view`, `users_edit`, `wallet_edit`, `roles_view`, `roles_manage`, `database`,
`stories_admin`, `settings`, `system`) from the `role_permissions` setting. `wallet_edit`,
`roles_view`, `roles_manage`, `settings` and `system` are SUPER_ADMIN-only and cannot be granted
to USER or ADMIN, including through the matrix API. Settings and system endpoints return 403
for ADMIN.

### GET /api/v1/admin/users

- Query: `page`, `role`, `is_active`, `search`.
- Returns `users`, `total`, `page`. Never includes password_hash.

### GET /api/v1/admin/users/{user_id}

- Returns user without password_hash.

### PATCH /api/v1/admin/users/{user_id}

- Body: subset of `username`, `display_name`, `phone_number`, `is_active`.
- Duplicate username/phone returns 409. Self-deactivation and deactivating the last active SUPER_ADMIN return 403.

### PATCH /api/v1/admin/users/{user_id}/tokens

- Requires `wallet_edit` (SUPER_ADMIN only).
- Body: `{"increase": 5}` (positive integer only).
- Setting `token_balance`, negative `adjustment`, zero or non-integer returns 400.
- Tokens can only be increased.

### PATCH /api/v1/admin/users/{user_id}/role

- Body: `{"role": "ADMIN", "password": "adminPassword"}`.
- Requires `roles_manage`, password re-entry, and role guardrails. Self-role-change is blocked.

### GET /api/v1/admin/roles/permissions

- Returns `permissions` (role → capability list), `capabilities`, `locked` (SUPER_ADMIN-only keys), `editable`.

### PUT /api/v1/admin/roles/permissions

- Body: `{"permissions": {"USER": [], "ADMIN": [...], "SUPER_ADMIN": ["*"]}}`.
- SUPER_ADMIN is always full. A role cannot revoke its own `roles_manage`.
- Returning any locked capability for USER/ADMIN is rejected with 403 `FORBIDDEN`; locked keys in
  stored settings are ignored when computing effective permissions.

### GET /api/v1/admin/stories

- Query filters: user_id, story_status, generation_status.

### GET /api/v1/admin/analytics/summary

- Query: `range` (7, 30, 90, 36500 = all).
- Returns grouped objects: `users`, `stories`, `tokens`, `system`.

### GET /api/v1/admin/analytics/charts

- Query: `chart` (`users_growth`, `users_role`, `token_distribution`, `stories_status`,
  `generation_status`, `stories_per_day`, `tokens_per_day`, `gemini_usage`, `top_users`), `range`.

### GET /api/v1/admin/analytics/db-health

- Row counts and last write per table, plus database size in bytes.

### GET /api/v1/admin/analytics/integrity

- On-demand `PRAGMA integrity_check` and foreign-key violation count.

### GET /api/v1/admin/analytics/recent

- Recent users and recent stories (5 each).

### GET /api/v1/admin/database/meta

- Table names, row counts and database size.

### GET /api/v1/admin/database/{table_name}

- Allowed tables: the three approved only.
- Query: `page`, `per_page` (max 100), `q` (search).
- Returns paginated rows with `columns`, `total`, `page`, `pages`. password_hash is omitted;
  secret settings are masked. Read-only.

### GET /api/v1/admin/settings

- Requires `settings` (SUPER_ADMIN only).
- Returns key/value settings. Internal structured settings such as `role_permissions` are excluded;
  those are managed through Role Access.

### PATCH /api/v1/admin/settings

- Requires `settings` (SUPER_ADMIN only).

- Body: `{"setting_key": "...", "setting_value": "...", "value_type": "..."}`.

### GET /api/v1/admin/system/status

- Requires `system` (SUPER_ADMIN only).
- Returns `enabled`, `updated_at`, `updated_by`, `affected_users`.

### PATCH /api/v1/admin/maintenance

- Requires `system` (SUPER_ADMIN only).
- Body: `{"enabled": true, "password": "adminPassword"}`.
- Backend verifies password against the authenticated admin's hash. 401 on mismatch.
- While enabled, user pages redirect to `/maintenance` and user APIs return 503 `MAINTENANCE`.
  Admin login, admin pages and admin APIs remain available. The flag persists across restarts.

## 6. Contact

### POST /api/v1/contact

- Auth: required (or public with rate limit; provisional: authenticated users).
- Body: `{"subject": "...", "message": "..."}`.
- Sends email to configured admin email.
- Rate-limited; validates against header injection.

## 7. Status Codes

200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Validation Error, 429 Too Many Requests, 500 Server Error, 502 Bad Gateway (provider), 504 Gateway Timeout.

## 8. Postman

- Use cookie jar for session persistence.
- Fetch CSRF via `GET /api/v1/auth/csrf` and send as `X-CSRFToken` header (or form field) on state-changing requests.
- Environment variables: `base_url`, `csrf_token`.