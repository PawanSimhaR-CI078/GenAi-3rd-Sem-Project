# Marque Analytics Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add welcome links to both sidebars and apply Marque inspired polish to analytics KPI cards and bar charts.

**Architecture:** Keep the existing Flask templates and inline dashboard script. Add one sidebar link per role shell, extend the local `card()` helper with a tone argument, add CSS classes to the existing analytics block, and set Chart.js bar options only for bar datasets. No new backend code.

**Tech Stack:** Flask, Jinja2, CSS3, vanilla JS, Chart.js via CDN, Material Icons via Google Fonts, pytest, SIT script.

**Spec:** `docs/superpowers/specs/2026-11-25-marque-analytics-polish.md`

## Global Constraints

- Python 3.12 target. Keep current venv usage.
- Flask application factory and blueprints stay as they are.
- No new table, endpoint, dependency, build step or image generation.
- Exactly three tables remain: `tolstoy_users`, `tolstoy_stories`, `tolstoy_system_settings`.
- HTML5, Jinja2, CSS3 and vanilla JS only. Tailwind and Chart.js stay CDN only.
- Material Icons for sidebar icons. One small inline SVG is allowed for the Gemini mark inside `dashboard.html` only.
- Keep backend auth, CSRF, maintenance and RBAC behavior unchanged.
- Do not use en dashes or em dashes in new copy, comments or docs. Use commas or plain hyphens.
- New logic gets a small test or SIT check.

## Review Focus

1. Admin with revoked analytics can still land on `/admin/home`; Task 1 test checks the admin shell at that path.
2. Collapsed sidebar must keep the welcome icon usable without a label; Task 1 CSS assertion checks `.sidebar-collapsed .nav-link` still applies.
3. KPI tones must be static semantics, not derived from live values; Task 2 test asserts the exact tone classes in template source.
4. Gemini SVG must stay decorative while the text label remains present; Task 3 test asserts `aria-hidden="true"` and `Gemini tokens`.
5. Chart rounding must affect vertical bars only; Task 3 test asserts `borderRadius: 8` and `borderSkipped: 'bottom'`, and the browser pass checks line charts still render.

---

### Task 1: Welcome link in both sidebars

**Files:**
- Modify: `app/templates/user/base_user.html:23-33`
- Modify: `app/templates/admin/base_admin.html:24-33`
- Modify: `app/static/js/app.js:67-82`
- Test: `tests/test_ui_navigation.py`

**Interfaces:**
- Consumes: existing `nav-link`, `nav-icon`, `nav-label` classes and `sessionStorage.tolstoy_sidebar_collapsed`.
- Produces: `/home` link for users and `/admin/home` link for admins, both with Material icon `home` and label `Welcome`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_ui_navigation.py`:

```python
def test_welcome_link_in_both_sidebars(client, ctx):
    user = _make_user(ctx, "welcome_nav_user")
    admin = _make_user(ctx, "welcome_nav_super", "SUPER_ADMIN")

    _login(client, user, "USER")
    html = client.get("/home").get_data(as_text=True)
    assert 'href="/home"' in html
    assert '>home</i>' in html
    assert "Welcome</span>" in html

    _login(client, admin, "SUPER_ADMIN")
    html = client.get("/admin/home").get_data(as_text=True)
    assert 'href="/admin/home"' in html
    assert '>home</i>' in html
    assert "Welcome</span>" in html
```

Update `test_admin_sidebar_icons_are_valid_material_ligatures` so the allowed set includes `"home"`.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_ui_navigation.py::test_welcome_link_in_both_sidebars tests/test_ui_navigation.py::test_admin_sidebar_icons_are_valid_material_ligatures`
Expected: FAIL because the welcome links are missing.

- [ ] **Step 3: Implement the links**

In `app/templates/user/base_user.html`, add as the first item in the sidebar `nav`:

```html
<a href="/home" class="nav-link" data-nav="welcome" title="Welcome"><i class="material-icons nav-icon" aria-hidden="true">home</i><span class="nav-label">Welcome</span></a>
```

In `app/templates/admin/base_admin.html`, add as the first item in the sidebar `nav`, only guarded by existing auth and admin route context:

```html
<a href="/admin/home" class="nav-link {{ 'active' if request.path == '/admin/home' }}" title="Welcome"><i class="material-icons">home</i><span class="nav-label">Welcome</span></a>
```

In `app/static/js/app.js`, add one branch before the dashboard branch:

```js
if (path === '/home') active = '/home';
```

Keep the `else if` chain intact. Do not add a separate `active` assignment later.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_ui_navigation.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/user/base_user.html app/templates/admin/base_admin.html app/static/js/app.js tests/test_ui_navigation.py
git commit -m "Add welcome links to user and admin sidebars"
```

### Task 2: Standardized KPI tones and Marque card polish

**Files:**
- Modify: `app/templates/admin/dashboard.html:89-113`
- Modify: `app/static/css/app.css:122-124,225-229`
- Test: `tests/test_ui_navigation.py`
- Test: `scripts/sit_check.py`

**Interfaces:**
- Consumes: `card(label, value, sub)` inline helper in `app/templates/admin/dashboard.html`.
- Produces: `card(label, value, sub, tone)` returning a `.stat-card.kpi-tone--<tone>` element. Allowed tones are `neutral`, `good`, `bad` and `gemini`. Task 3 adds the Gemini mark inside this helper.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_ui_navigation.py`:

```python
def test_analytics_kpi_tones_and_marque_polish(client, ctx):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    html = (root / "app/templates/admin/dashboard.html").read_text(encoding="utf-8")
    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")

    assert "card('Generation success'" in html
    assert "'good'" in html
    assert "'bad'" in html
    assert "kpi-tone--" in html
    assert ".kpi-grid > .stat-card.kpi-tone--good" in css
    assert ".kpi-grid > .stat-card.kpi-tone--bad" in css
    assert "repeating-linear-gradient" in css
    assert "translateY(-3px)" in css
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_ui_navigation.py::test_analytics_kpi_tones_and_marque_polish`
Expected: FAIL because tone classes and CSS are absent.

- [ ] **Step 3: Extend the helper and map the tones**

Change the helper signature to `function card(label, value, sub, tone)`. Add `kpi-tone--${tone}` to the returned `stat-card` class list. Keep `esc()` on label, value and sub.

Pass these exact fourth arguments for the 12 cards in this order: `neutral`, `neutral`, `neutral`, `good`, `good`, `neutral`, `good`, `neutral`, `bad`, `bad`, `neutral`, `gemini`.

- [ ] **Step 4: Add CSS polish**

Append to the analytics block in `app/static/css/app.css`, after `.kpi-grid > .stat-card`:

```css
.kpi-grid > .stat-card { position: relative; overflow: hidden; border-color: var(--color-border); border-radius: 14px; box-shadow: 0 18px 36px -24px rgba(85,70,232,.45); transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition); }
.kpi-grid > .stat-card::before { content: ""; position: absolute; inset: 0 0 auto; height: 3px; background: repeating-linear-gradient(90deg, var(--color-primary) 0 8px, transparent 8px 14px); opacity: .55; }
.kpi-grid > .stat-card:hover { transform: translateY(-3px); box-shadow: 0 28px 48px -28px rgba(85,70,232,.55); }
.kpi-grid > .stat-card .stat-label { font-family: var(--font-mono); font-size: 11px; font-weight: 500; letter-spacing: .12em; text-transform: uppercase; }
.kpi-grid > .stat-card.kpi-tone--good .stat-value { color: var(--color-success); }
.kpi-grid > .stat-card.kpi-tone--bad .stat-value { color: var(--color-error); }
.kpi-grid > .stat-card.kpi-tone--gemini .stat-value { color: var(--color-primary); }
```

Do not change `.kpi-grid` columns or the `@media` rules.

- [ ] **Step 5: Add the SIT check**

Add to `scripts/sit_check.py` after the existing admin analytics page check:

```python
r = s.get(BASE + "/admin")
rec("GET /admin KPI tones 200", r.status_code == 200 and "kpi-tone--good" in r.text and "kpi-tone--bad" in r.text, r.status_code)
```

Use the existing admin session variable from that section. Do not create a second login.

- [ ] **Step 6: Run the tests and SIT**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_ui_navigation.py`
Expected: PASS.

Run: `.\\.venv\\Scripts\\python.exe scripts/sit_check.py`
Expected: all checks PASS against `http://127.0.0.1:5001`.

- [ ] **Step 7: Commit**

```bash
git add app/templates/admin/dashboard.html app/static/css/app.css tests/test_ui_navigation.py scripts/sit_check.py
git commit -m "Add standardized KPI tones and Marque card polish"
```

### Task 3: Gemini mark and rounded bar tops

**Files:**
- Modify: `app/templates/admin/dashboard.html:89,131-137`
- Test: `tests/test_ui_navigation.py`
- Test: `scripts/sit_check.py`

**Interfaces:**
- Consumes: `card(label, value, sub, tone)` from Task 2.
- Produces: inline `GEMINI_MARK` constant used when `tone === 'gemini'`, and bar dataset options with rounded top corners.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_ui_navigation.py`:

```python
def test_gemini_mark_and_rounded_bar_tops(client, ctx):
    from pathlib import Path

    html = (Path(__file__).resolve().parents[1] / "app/templates/admin/dashboard.html").read_text(encoding="utf-8")
    assert "GEMINI_MARK" in html
    assert 'aria-hidden="true"' in html
    assert "Gemini tokens" in html
    assert "borderRadius: 8" in html
    assert "borderSkipped: 'bottom'" in html
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_ui_navigation.py::test_gemini_mark_and_rounded_bar_tops`
Expected: FAIL because the mark and chart options are absent.

- [ ] **Step 3: Add the inline Gemini mark**

Define one `const GEMINI_MARK` in the dashboard script containing a 16px inline SVG with a linear gradient from `#4285F4` to `#9B72CB` to `#D96570`, a four point spark path, `class="kpi-gemini-mark"`, `aria-hidden="true"` and `focusable="false"`.

Inside `card()`, when `tone === 'gemini'`, prepend the mark to the label markup. Keep the label text escaped and visible.

Add one CSS rule in `app/static/css/app.css` after the KPI tone rules:

```css
.kpi-gemini-mark { width: 16px; height: 16px; margin-right: 6px; vertical-align: -2px; }
```

- [ ] **Step 4: Round bar tops only**

In the chart creation call, change the dataset object so `type === 'bar'` adds `borderRadius: 8` and `borderSkipped: 'bottom'`. Keep line datasets with their current `backgroundColor`, `borderColor`, `fill` and `tension` values.

- [ ] **Step 5: Add the SIT check**

Extend the admin analytics SIT check from Task 2 to also assert `GEMINI_MARK` and `borderSkipped: 'bottom'` appear in the page source.

- [ ] **Step 6: Run the full verification set**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q`
Expected: all tests PASS.

Run: `.\\.venv\\Scripts\\python.exe -m compileall -q app scripts tests`
Expected: no output, exit 0.

Run: `.\\.venv\\Scripts\\python.exe scripts/sit_check.py`
Expected: all checks PASS against `http://127.0.0.1:5001`.

- [ ] **Step 7: Browser verification**

In the connected browser, sign in as super admin, open `/admin/home`, confirm the new `Welcome` link is present, open `/admin`, confirm the 12 KPI cards render with green and red values, confirm the Gemini mark is visible on the Gemini card, confirm bar charts have rounded tops and line charts still render. Check the console for errors. Emulate `375x812` and confirm the KPI grid is one column and the sidebar link remains reachable through the menu.

- [ ] **Step 8: Commit and push**

```bash
git add -A
git commit -m "Add Gemini mark and rounded analytics bars"
git push origin main
```

## Self-Review

- Spec requirements 1 through 6 map to Tasks 1 through 3.
- Step scan: each step writes one test, one exact markup block or one exact config value.
- Type consistency: `card(label, value, sub, tone)` is introduced in Task 2 and consumed in Task 3.
- Review Focus: all five conditions have a test or browser check.
- Proportion: the plan is shorter than the code it describes and contains no full function bodies.
