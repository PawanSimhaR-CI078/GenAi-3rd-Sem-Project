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

All require role ADMIN/SUPER_ADMIN.

### GET /api/v1/admin/users

- Query: `page`, `per_page`, `role`, `is_active`, `search`.

### GET /api/v1/admin/users/{user_id}

- Returns user without password_hash.

### PATCH /api/v1/admin/users/{user_id}

- Body: subset of profile fields (username edit pending confirmation).

### PATCH /api/v1/admin/users/{user_id}/tokens

- Body: `{"token_balance": 10}` or `{"adjustment": +5}` (exact contract pending). Admin only.

### GET /api/v1/admin/stories

- Query filters: user_id, story_status, generation_status.

### GET /api/v1/admin/analytics/summary

- Returns aggregate counts: total users, active users, total stories, editing/completed counts, tokens consumed, gemini usage totals.

### GET /api/v1/admin/analytics/charts

- Query: `chart` (key). Returns series for Chart.js.

### GET /api/v1/admin/database/{table_name}

- Allowed tables: the three approved only. Returns paginated rows with password_hash and secret columns stripped.

### GET /api/v1/admin/settings

### PATCH /api/v1/admin/settings

- Body: `{"setting_key": "...", "setting_value": "...", "value_type": "..."}`.

### PATCH /api/v1/admin/maintenance

- Body: `{"enabled": true, "password": "adminPassword"}`.
- Backend verifies password against the authenticated admin's hash. 401 on mismatch.

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