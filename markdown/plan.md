# TOLSTOY — Implementation Plan

## 1. Objective

Deliver TOLSTOY as a clean, secure, three-table Flask application that converts story input into structured comic scripts via Gemini, with token management, user/admin interfaces, analytics, and tests.

## 2. Phases

### Phase 0 — Project Foundation (done)

- Repository, venv, config files, folder structure.
- **Acceptance:** all required dirs/files exist; `.gitignore` excludes secrets/DB.

### Phase 1 — Documentation and Architecture Approval

- Review all Markdown docs; resolve open decisions.
- **Deliverables:** approved schema, API contracts, security design.
- **Acceptance:** owner signs off on `Owner Confirmation Required` items (or marks provisional).

### Phase 2 — Database Foundation

- SQLite init at `database/tolstoy.db`.
- Create exactly three tables with six metadata columns each.
- Constraints, indexes, DB access layer, tests.
- **Acceptance:** `SELECT name FROM sqlite_master` returns exactly the three tables; metadata columns present; tests green.

### Phase 3 — Authentication and Authorization

- Registration, user/admin login, password hashing, sessions, CSRF, role enforcement.
- **Acceptance:** auth tests pass; unauthorized access blocked.

### Phase 4 — Token Management

- Initial 5 tokens, 48h refill, atomic deduction, refunds, concurrency tests.
- **Acceptance:** token tests pass including concurrent requests.

### Phase 5 — Story Management

- CRUD, status changes, ownership enforcement.
- **Acceptance:** story tests pass; cross-user access blocked.

### Phase 6 — Gemini Integration

- Service module, prompt, structured JSON, validation, usage tracking, error handling, refund.
- **Acceptance:** valid/invalid/timeout cases handled; tokens refunded on failure.

### Phase 7 — User Frontend

- Landing, auth pages, dashboard, create story, editor, My Stories, wallet, contact admin.
- **Acceptance:** responsive; forms validated; loading/empty/error states.

### Phase 8 — Administrator Frontend

- Analytics (~5–6 charts), user/story management, DB viewer, settings, maintenance mode.
- **Acceptance:** charts render from real data; secrets never shown.

### Phase 9 — API and Postman Verification

- Postman collection + environment; all endpoints tested.
- **Acceptance:** every documented endpoint returns expected status/body.

### Phase 10 — Security and QA

- Full pytest suite, security checks, responsive testing, concurrency, Gemini failure, DB integrity.
- **Acceptance:** all tests green; no critical findings.

### Phase 11 — Deployment Readiness

- Production config, secret management, backup strategy, logging, deployment docs, final acceptance.
- **Acceptance:** deployment checklist complete.

## 3. Phase Rules

- A phase is not complete until its tests pass and acceptance criteria are met.
- Do not start a later phase while an earlier phase has failing tests.
- Each phase must update relevant Markdown docs if contracts change (with approval).

## 4. Dependencies

- Phase 2 depends on Phase 1 (schema approval).
- Phase 3 depends on Phase 2.
- Phase 4 depends on Phase 3.
- Phase 5 depends on Phase 3.
- Phase 6 depends on Phase 4 and 5.
- Phase 7 depends on Phase 5 and 6.
- Phase 8 depends on Phase 3 and 7.
- Phase 9 depends on Phases 3–8.
- Phase 10 depends on Phase 9.
- Phase 11 depends on Phase 10.

## 5. Unresolved Decisions (Owner Confirmation Required)

See `context.md` §14 and the `Owner Confirmation Required` section below. These do not block documentation but block implementation of dependent features.

## 6. Owner Confirmation Required

1. **Auth identifier** — username vs display name vs phone. Matters for registration/login/API/DB. Provisional: store `username` (unique) + optional `display_name`; phone optional. Depends: Phase 3.
2. **Admin role assignment** — two initial admins: one `ADMIN` + one `SUPER_ADMIN`, or both `ADMIN`? Depends: Phase 3, 8.
3. **SUPER_ADMIN distinction** — whether `SUPER_ADMIN` has extra privileges (e.g., maintenance mode, settings) vs `ADMIN`. Depends: Phase 8.
4. **Admin email + provider** — recipient address and SMTP config. Depends: Phase 7 (contact admin).
5. **Gemini model** — exact model name, quota, limits. Depends: Phase 6.
6. **Token cost per generation/regeneration** — how many application tokens a generation costs. Depends: Phase 4, 6.
7. **Refill accumulation** — if inactive for multiple 48h periods, do refills stack or only one? Depends: Phase 4.
8. **Deletion policy** — soft-delete vs permanent delete. Depends: Phase 5.
9. **Editing after completion** — allowed (status returns to Editing) — confirm whether content edits require re-generation. Depends: Phase 5.
10. **Dynamic page permissions** — required despite three-table limit? Likely no; fixed role-based policy. Depends: Phase 8.
11. **Story JSON output schema** — exact fields for scenes/panels/dialogue/narration. Depends: Phase 6, 7.
12. **Editable user fields by admin** — username editable or only profile info? Depends: Phase 8.