# TOLSTOY — Testing Strategy

## 1. Tools

- Automated: pytest.
- API: Postman (collection + environment).
- Manual: responsive/UI checks.

## 2. Test Categories

- Database integrity
- Authentication
- Authorization
- Token system
- Story functionality
- Gemini integration
- Admin features
- Frontend behavior

## 3. Database Tests

- Exactly three approved tables exist.
- All table names prefixed `tolstoy_`.
- Six metadata columns present in each.
- PKs, FKs, unique constraints, check constraints, indexes.
- Init idempotency.
- No password hashes exposed by DB viewer.

## 4. Authentication Tests

- Registration success/duplicate/invalid.
- Login success/invalid password/inactive account.
- Admin login requires admin role.
- Logout invalidates session.
- Session expiry.

## 5. Authorization Tests

- User accesses own stories (success).
- User accesses another user's story (403).
- User calls admin endpoint (403).
- Admin accesses admin endpoints (success).
- Maintenance mode blocks users, allows admins.

## 6. Token Tests

- New user gets 5 tokens.
- 48h refill adds 5 (additive, not reset).
- Repeated refill requests safe.
- Concurrent refill safe.
- Successful generation deducts cost.
- Insufficient balance → 402, no deduction.
- Failed generation → refund.
- Concurrent generation → no double spend.
- Admin balance update.

## 7. Story Tests

- Create/read/update.
- Generate/regenerate.
- Status change Editing↔Completed.
- Ownership protection.
- Delete/archive per policy.

## 8. Gemini Tests

- Valid structured response saved.
- Invalid JSON rejected.
- Empty response handled.
- Timeout → refund.
- Provider rate limit → 429 + refund.
- Provider error → 502 + refund.
- Usage extracted when available.

## 9. Admin Tests

- Dashboard metrics correct.
- User management CRUD.
- DB viewer masks secrets.
- Maintenance toggle requires password re-verify.
- Settings validation.

## 10. Frontend Tests (manual + automated where possible)

- Responsive layouts (mobile/tablet/desktop).
- Form validation.
- Loading/empty/error states.
- Navigation.
- Live clock/date.
- Token balance display.

## 11. Test Case Format

Each test case documents: objective, category, preconditions, steps, expected result, priority, automation suitability.

## 12. Completion Criteria

A phase is complete only when its tests pass and acceptance criteria are met. No claiming success without execution evidence.

## 13. Regression

Re-run full suite on any change to auth, tokens, DB, or Gemini.