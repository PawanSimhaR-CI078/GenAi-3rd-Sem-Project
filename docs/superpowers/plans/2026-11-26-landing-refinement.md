# Landing Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the measured mobile navigation, hierarchy and typography defects on the TOLSTOY landing page while leaving all behavior and backend contracts intact.

**Architecture:** Markup lives in `app/templates/public/base_public.html` and `app/templates/public/index.html`. Behavior is one small vanilla JS block in `app/static/js/app.js`. Styling stays in the existing `app/static/css/app.css` token system. Tests are source assertions in `tests/test_landing_page.py`.

**Tech Stack:** Flask, Jinja2, hand-written CSS3, vanilla JavaScript, pytest, browse browser verification.

**Spec:** `docs/superpowers/specs/2026-11-26-landing-refinement-design.md`

## Global Constraints

- Exactly three application tables; no schema or database change.
- No new dependency, npm, build step, framework, stylesheet or icon library.
- Keep Flask application factory, Jinja2 autoescaping, CSRF wrapper and session behavior unchanged.
- Keep all landing sections, IDs, links, copy and FAQ `<details>` elements.
- Use existing design tokens only. Primary `#5546E8`, hover `#4636D9`, border `#E4E7EF`, card `#FFFFFF`.
- No em dash or en dash in new copy.
- Desktop nav stays visible; the collapsible behavior applies only at `max-width: 768px`.

## Review Focus

1. **Phone navigation:** a 320px viewport must show one compact header row with a reachable Menu button, not six wrapped links. Test: source assertions for `data-nav-toggle`, `aria-controls="publicNav"`, `nav.is-open`, and browser check at 320px and 375px.
2. **Keyboard and screen reader:** the toggle must expose expanded state and Escape must close the menu and return focus. Test: source assertions for `aria-expanded`, `Escape`, and `toggle.focus()`.
3. **No hidden focus:** collapsed links use `display: none`, so Tab cannot enter them. Test: browser Tab check with the menu closed.
4. **Small text:** the script preview must not drop to 11px at 320px. Test: source assertion that the 11px override is gone and browser computed font size check.
5. **Duplicated font fetch:** CSS must not import the same font URL that the template links. Test: source assertion that `app.css` has no `@import url('https://fonts.googleapis.com`.

---

### Task 1: Mobile navigation

**Files:**
- Modify: `app/templates/public/base_public.html:14-24`
- Modify: `app/static/js/app.js:28`
- Modify: `app/static/css/app.css:346-355,450-464`
- Test: `tests/test_landing_page.py`

**Interfaces:**
- Consumes: existing `.public-nav`, `.btn`, design tokens and `app.js` loaded at `base_public.html:59`.
- Produces: `[data-nav-toggle]` button, `id="publicNav"` links container, `.is-open` class, `aria-expanded` state.

- [x] **Step 1: Write the failing test**

Add to `tests/test_landing_page.py`:

```python
def test_landing_has_accessible_mobile_navigation(client):
    from pathlib import Path

    html = client.get("/").get_data(as_text=True)
    assert 'data-nav-toggle' in html
    assert 'aria-controls="publicNav"' in html
    assert 'id="publicNav"' in html
    assert 'aria-expanded="false"' in html

    root = Path(__file__).resolve().parents[1]
    js = (root / "app/static/js/app.js").read_text(encoding="utf-8")
    assert "data-nav-toggle" in js
    assert "aria-expanded" in js
    assert "Escape" in js
    assert "toggle.focus()" in js

    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")
    assert ".nav-toggle" in css
    assert ".public-nav--landing nav.is-open" in css
```

- [x] **Step 2: Run the test to verify it fails**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_landing_page.py::test_landing_has_accessible_mobile_navigation`
Expected: FAIL.

- [x] **Step 3: Add the toggle markup**

In `app/templates/public/base_public.html`, keep the header class unchanged. Add before the existing `<nav>`:

```html
  <button class="nav-toggle" type="button" data-nav-toggle aria-controls="publicNav" aria-expanded="false" aria-label="Open navigation">
    <span class="nav-toggle__icon" aria-hidden="true"></span><span>Menu</span>
  </button>
```

Give the existing `<nav>` `id="publicNav"`. Keep every link and class as is.

- [x] **Step 4: Add the behavior**

Append one IIFE to `app/static/js/app.js`. Use `document.querySelector('[data-nav-toggle]')`, find the controlled element by `getAttribute('aria-controls')`, return early if either is missing, toggle `.is-open`, update `aria-expanded` and `aria-label`, close on link click, close and focus the toggle on Escape, and close when `window.innerWidth > 768`.

- [x] **Step 5: Add the CSS**

In `app/static/css/app.css`, add base `.nav-toggle` styles with `display: none`, `min-height: 44px`, visible `:focus-visible` outline and a two-bar icon made from pseudo elements. In the existing `@media (max-width: 768px)` block, show the toggle, make `.public-nav--landing` `position: relative` and `flex-wrap: nowrap`, position the nav absolutely below the header with `display: none`, and show it as a full-width column under `.public-nav--landing nav.is-open`. Keep all other rules in that media block.

- [x] **Step 6: Run the test to verify it passes**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_landing_page.py`
Expected: PASS.

- [x] **Step 7: Commit**

```bash
git add app/templates/public/base_public.html app/static/js/app.js app/static/css/app.css tests/test_landing_page.py
git commit -m "Add accessible mobile navigation to public pages"
```

### Task 2: Landing visual refinement

**Files:**
- Modify: `app/static/css/app.css:1-2,378-399,466-474`
- Modify: `app/templates/public/index.html:95`
- Test: `tests/test_landing_page.py`

**Interfaces:**
- Consumes: tokens from `:root`, `.card`, `.badge` and `.btn` classes.
- Produces: connected step cards, primary token CTA, 12px minimum script preview, single font request.

- [x] **Step 1: Write the failing test**

Add to `tests/test_landing_page.py`:

```python
def test_landing_refinements(client):
    from pathlib import Path

    html = client.get("/").get_data(as_text=True)
    assert 'class="btn btn-primary">Create an account</a>' in html
    assert 'id="tokens"' in html and 'id="faq"' in html
    assert html.count("<details>") == 5

    root = Path(__file__).resolve().parents[1]
    css = (root / "app/static/css/app.css").read_text(encoding="utf-8")
    assert "@import url('https://fonts.googleapis.com" not in css
    assert ".lp-script-name, .lp-script-line { font-size: 11px; }" not in css
    assert ".lp-steps .feature-grid::before" in css
    assert ".lp-faq summary:hover" in css
```

- [x] **Step 2: Run the test to verify it fails**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_landing_page.py::test_landing_refinements`
Expected: FAIL.

- [x] **Step 3: Apply the markup and CSS changes**

Change the token section CTA class to `btn btn-primary`. Remove the CSS `@import` line. Delete the 11px preview override in the 375px media block. Add a `@media (min-width: 769px)` block with a dashed connector line on `.lp-steps .feature-grid::before` and `z-index: 1` on `.lp-steps .card .badge`. Add `.lp-faq summary:hover` with a subtle background and the existing transition.

- [x] **Step 4: Run the test to verify it passes**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_landing_page.py`
Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add app/templates/public/index.html app/static/css/app.css tests/test_landing_page.py
git commit -m "Refine landing hierarchy and typography"
```

### Task 3: Full verification and push

**Files:**
- No source changes expected. Update `markdown/ui_ux.md` only if it describes the public navigation.

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: verified result on `main`.

- [x] **Step 1: Run automated checks**

Run and record: `.\\.venv\\Scripts\\python.exe -m pytest -q`, `.\\.venv\\Scripts\\python.exe -m compileall -q app scripts tests`, and the SIT check against the running server on port 5001.

- [x] **Step 2: Browser verification**

Use the `browse` tools through code mode. Check `/`, `/login`, `/register`, `/admin/login` and `/maintenance` at 320, 375, 430, 768, 1024, 1280, 1440 and 1920px. Verify no horizontal overflow, compact mobile menu with working keyboard control, all nav and footer links, FAQ toggling, visible focus, reduced motion, console errors and network failures. Capture screenshots at desktop, tablet and mobile widths.

- [x] **Step 3: Commit and push**

Commit any needed source or doc fix, then push `origin main`.

## Self-Review

- Spec changes map to Task 1 or Task 2; browser and backend preservation map to Task 3.
- All five Review Focus lines have a source or browser test.
- No backend, schema, auth, CSRF, token or Gemini file is touched.
- The plan uses only existing files and tokens, with no new dependency or build step.

## Verification Evidence

- `pytest -q`: 76 passed.
- `compileall -q app scripts tests`: exit 0.
- `scripts/sit_check.py`: 77 / 77 passed.
- Browser matrix at 320, 375, 430, 768, 1024, 1280, 1440 and 1920px: no horizontal overflow, nav collapses below 769px, script preview stays at 12px, connector aligns with badge centers on desktop.
- Browser checks on `/`, `/login`, `/register`, `/admin/login` and `/maintenance`: no console errors, 0 network failures, focus outlines visible, FAQ keyboard toggle works, reduced motion sets scroll behavior to auto.
- Code review: two Important findings fixed and rechecked. No Critical or Important issues remain.
