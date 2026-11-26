# Marque Analytics Polish Spec

> **For agentic workers:** This is the approved design doc for `docs/superpowers/plans/2026-11-25-marque-analytics-polish.md`.

**Goal:** Add a welcome entry to both sidebars and polish the analytics KPI cards and bar charts using inspiration from the Marque UI kit.

**Approved:** 2026-11-25. Scope: Marque polish. Color mapping: green for good, red for bad.

## Requirements

1. Users see a `Welcome` link to `/home` in the user sidebar. Admins see a `Welcome` link to `/admin/home` in the admin sidebar. Both use the Material Icons `home` ligature. The link gets the existing active state on its own path.
2. The 12 analytics KPI cards keep their current labels and values. They gain standardized tones:
   - `good`: Generation success, Completed, New users
   - `bad`: Inactive users, Soft-deleted stories
   - `neutral`: Total users, Total stories, Tokens in circulation, Editing, Avg tokens per user, Tokens consumed
   - `gemini`: Gemini tokens
3. Gemini tokens get a small inline Gemini spark mark next to the label. The mark is decorative and the text label remains readable.
4. KPI cards borrow three Marque details only: hairline border, 14px radius, soft violet shadow, hover lift, mono uppercase label and a thin striped accent. The 12-card grid stays in place. No full palette rewrite.
5. Chart.js bar datasets round only the top corners with `borderRadius: 8` and `borderSkipped: 'bottom'`. Line datasets stay unchanged.
6. Existing tests and SIT checks gain coverage for the sidebar link, tone classes, Gemini mark and chart rounding. Pytest, compileall, SIT and browser checks at desktop and mobile widths must pass.

## Files in scope

- `app/templates/user/base_user.html`
- `app/templates/admin/base_admin.html`
- `app/static/js/app.js`
- `app/templates/admin/dashboard.html`
- `app/static/css/app.css`
- `tests/test_ui_navigation.py`
- `scripts/sit_check.py`

## Out of scope

- New tables, endpoints, dependencies, build steps or generated images.
- Full editorial restyle of the analytics grid or panels.
- Changes to story, token, auth, maintenance or RBAC rules.
- New page copy beyond the `Welcome` sidebar label.
