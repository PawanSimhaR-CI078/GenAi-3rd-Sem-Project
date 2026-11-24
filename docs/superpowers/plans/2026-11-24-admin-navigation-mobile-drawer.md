# Admin Navigation and Mobile Drawer Fix — Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make admin options discoverable from the public/user UI and make the sidebar usable on narrow screens.

**Architecture:** Small template + CSS/JS changes. No new dependencies, no backend contract changes.

**Tech Stack:** Jinja2, CSS3, vanilla JavaScript, pytest, browser smoke.

**Spec:** Approved in conversation on 2026-11-24.

## Global Constraints

- Keep the three-table database rule and existing auth/capability model.
- No new dependencies or frontend build step.
- Admin-only visibility uses `session.role`; backend authorization remains unchanged.
- Drawer must be closable and must not permanently cover page content.

## Review Focus

- A SUPER_ADMIN signing in through `/login` must land on `/admin`.
- A normal USER must not see the Admin Panel link.
- At ≤768px the menu must open and close without covering its own close control.
- At >768px the sidebar must remain sticky and the mobile controls hidden.

---

### Task 1: Add regression tests for navigation entry points

**Files:**
- Create: `tests/test_ui_navigation.py`

**Interfaces:**
- Consumes: `create_app("testing")`, `create_user(...)`.
- Produces: failing tests for public admin link, role-gated dashboard link, admin drawer markup.

- [ ] **Step 1: Write the failing tests**

```python
def test_public_pages_link_admin_signin(client):
    assert 'href="/admin/login"' in client.get("/").get_data(as_text=True)

def test_dashboard_shows_admin_panel_for_admins_only(client):
    # create SUPER_ADMIN and USER, log each in:
    # SUPER_ADMIN dashboard contains 'href="/admin"' and "Admin Panel"
    # USER dashboard contains neither

def test_admin_layout_has_mobile_drawer_controls(client):
    # log in SUPER_ADMIN, GET /admin:
    # assert data-sidebar-toggle, data-sidebar-close and data-sidebar-backdrop
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_ui_navigation.py -q`
Expected: FAIL on missing admin link / drawer markup.

### Task 2: Fix admin discoverability

**Files:**
- Modify: `app/templates/public/base_public.html`
- Modify: `app/templates/public/index.html`
- Modify: `app/templates/public/login.html`
- Modify: `app/templates/user/base_user.html`

- [ ] Add an Admin link to `/admin/login` in public nav and make the landing Admin card link there.
- [ ] After `/api/v1/auth/user/login`, redirect ADMIN/SUPER_ADMIN to `/admin`, others to `/dashboard`.
- [ ] Add an “Admin Panel” sidebar link for ADMIN/SUPER_ADMIN only.

### Task 3: Add shared mobile drawer behavior

**Files:**
- Modify: `app/templates/user/base_user.html`
- Modify: `app/templates/admin/base_admin.html`
- Modify: `app/static/css/app.css`
- Modify: `app/static/js/app.js`

- [ ] Add `data-sidebar-toggle`, `data-sidebar-close`, and `data-sidebar-backdrop` controls to both layouts.
- [ ] Add CSS for the backdrop, close button, mobile visibility, and body scroll lock.
- [ ] Add vanilla JS to toggle the drawer, close on backdrop/Escape, and keep `aria-expanded` in sync.

### Task 4: Verify and commit

- [ ] Run `pytest -q` and `scripts/sit_check.py`.
- [ ] Browser smoke at 646px and 1000px: open/close drawer, check admin link visibility, no console errors.
- [ ] Commit and push.
