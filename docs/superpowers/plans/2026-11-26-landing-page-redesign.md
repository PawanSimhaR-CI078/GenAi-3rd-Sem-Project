# Landing Page Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the public landing page as a complete ten-section page with a CSS-only product preview and a shared four-column footer.

**Architecture:** Keep Flask, Jinja2 and hand-written CSS. The page markup goes in `public/index.html`, shared nav and footer go in `public/base_public.html`, and new styles go in one marked block at the end of `app/static/css/app.css`. No routes, backend logic, dependencies or build step.

**Tech Stack:** Flask, Jinja2, CSS3, vanilla JS, Tailwind CDN already present in the public base, pytest, SIT script, Chrome browser checks.

**Spec:** `docs/superpowers/specs/2026-11-26-landing-page-redesign-design.md`

## Global Constraints

- Exactly three tables: `tolstoy_users`, `tolstoy_stories`, `tolstoy_system_settings`. No schema work.
- No new dependency, npm, build step, image generation or new route.
- Keep the existing `#5546E8` palette and Plus Jakarta Sans, Inter and JetBrains Mono fonts.
- No Material Icons font on public pages. Use CSS shapes and text labels.
- No emoji as icons. No invented customers, logos, testimonials, counts, pricing or uptime claims.
- No en dash or em dash in new copy. Use commas or plain hyphens.
- Jinja autoescaping stays on. Every link resolves to one of `/`, `/login`, `/register`, `/admin/login`, `/maintenance` or an in-page anchor.
- Respect `prefers-reduced-motion`, visible focus and 375px layout.

## Review Focus

1. Logged out visitor at 375px: no horizontal scroll and every section stays in reading order. Test: browser width check at 375px plus `document.documentElement.scrollWidth <= innerWidth`.
2. Keyboard user on FAQ: `<details>` and `<summary>` work without custom JS. Test: browser tab and Enter check plus a source assertion that FAQ uses those tags.
3. Footer on `/login` and `/maintenance`: links stay valid and the page still renders. Test: pytest check on all five public routes plus SIT public loop.
4. Product preview with images forbidden: hero uses CSS markup only, no `<img>` and no background image URL. Test: source assertion in the landing test.
5. Reduced motion: decorative transitions stop. Test: existing global `prefers-reduced-motion` rule plus browser emulated reduced motion check.

## File Structure

- `app/templates/public/index.html`: ten sections, real copy, in-page ids.
- `app/templates/public/base_public.html`: shared nav anchors and four-column footer.
- `app/static/css/app.css`: one new landing block after the welcome block.
- `tests/test_landing_page.py`: new focused pytest file.
- `scripts/sit_check.py`: one new served HTML check.
- `markdown/ui_ux.md`: update the landing contract line.

---

### Task 1: Landing page structure and copy

**Files:**
- Modify: `app/templates/public/index.html`
- Test: `tests/test_landing_page.py`

**Interfaces:**
- Consumes: existing `btn`, `card`, `badge`, `feature-grid` classes and `{% extends "public/base_public.html" %}`.
- Produces: section ids `proof`, `problem`, `how`, `features`, `tokens`, `faq`, `start`; classes `lp-hero`, `lp-script`, `lp-proof`, `lp-problem`, `lp-steps`, `lp-benefits`, `lp-tokens`, `lp-faq`, `lp-final`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_landing_page.py` with:

```python
def test_landing_sections_and_copy(client):
    html = client.get("/").get_data(as_text=True)
    for section_id in ("proof", "problem", "how", "features", "tokens", "faq", "start"):
        assert f'id="{section_id}"' in html
    for class_name in ("lp-hero", "lp-script", "lp-proof", "lp-problem", "lp-steps", "lp-benefits", "lp-tokens", "lp-faq", "lp-final"):
        assert class_name in html
    assert "<details>" in html and "<summary>" in html
    assert "5 tokens" in html and "48 hours" in html
    assert "no images" in html.lower()
    assert "<img" not in html.lower()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_landing_page.py`
Expected: FAIL because the sections are absent.

- [ ] **Step 3: Replace `index.html` content with the ten sections**

Keep the `{% extends %}` and title blocks. Build, in order: hero with `lp-script` CSS preview, `lp-proof` fact strip, `lp-problem`, `lp-steps`, `lp-benefits`, `lp-tokens`, `lp-faq`, `lp-final`. Use the exact ids and classes from Interfaces. Write original plain copy about the real product. The hero preview uses nested `div` and `span` elements with `aria-hidden="true"` and no image. FAQ uses native details and summary. All CTAs point to `/register` or `/login`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_landing_page.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/public/index.html tests/test_landing_page.py
git commit -m "Rebuild landing page sections and copy"
```

### Task 2: Shared nav and four-column footer

**Files:**
- Modify: `app/templates/public/base_public.html:14-24`
- Test: `tests/test_landing_page.py`

**Interfaces:**
- Consumes: section ids from Task 1.
- Produces: classes `public-nav--landing`, `site-footer`, `site-footer__grid`, `site-footer__col`; footer headings Product, Resources, Company, Legal.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_landing_page.py`:

```python
def test_public_nav_and_shared_footer(client):
    html = client.get("/").get_data(as_text=True)
    assert 'class="public-nav public-nav--landing"' in html
    assert 'href="/#how"' in html and 'href="/#faq"' in html
    for heading in ("Product", "Resources", "Company", "Legal"):
        assert heading in html
    assert 'href="/maintenance"' in html
    for path in ("/login", "/register", "/admin/login", "/maintenance"):
        page = client.get(path).get_data(as_text=True)
        assert "site-footer__grid" in page, path
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_landing_page.py::test_public_nav_and_shared_footer`
Expected: FAIL because the footer is still one line.

- [ ] **Step 3: Implement nav anchors and footer**

In `base_public.html`, add `public-nav--landing` to the header class, and change Home to `href="/#how"` with label "How it works", add `href="/#features"`, `href="/#tokens"`, `href="/#faq"` links, then sign in, admin and get started. Keep at most five links before the primary CTA. Replace the one-line footer with `site-footer` containing `site-footer__grid` and four `site-footer__col` blocks. Product and Resources use `/#...` anchors plus `/login`, `/register`, `/admin/login`, `/maintenance`. Company and Legal are plain text with no anchors. Copyright stays plain text with a comma instead of an em dash.

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_landing_page.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/public/base_public.html tests/test_landing_page.py
git commit -m "Add shared public nav anchors and four-column footer"
```

### Task 3: Landing styles

**Files:**
- Modify: `app/static/css/app.css` after the welcome block
- Test: `tests/test_landing_page.py`

**Interfaces:**
- Consumes: classes from Tasks 1 and 2 and existing `:root` tokens.
- Produces: CSS rules for `.lp-*`, `.public-nav--landing`, `.site-footer*`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_landing_page.py`:

```python
def test_landing_styles(client):
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "app/static/css/app.css").read_text(encoding="utf-8")
    for selector in (".lp-hero", ".lp-script", ".lp-proof", ".lp-steps", ".lp-benefits", ".lp-tokens", ".lp-faq", ".lp-final", ".site-footer__grid"):
        assert selector in css
    assert "@media (max-width: 768px)" in css
    assert "prefers-reduced-motion" in css
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_landing_page.py::test_landing_styles`
Expected: FAIL because the styles are absent.

- [ ] **Step 3: Add one landing CSS block**

Append to `app/static/css/app.css` under `/* Public landing */`. Use existing tokens only. Give the hero a two-column layout with the script preview on the right, the proof strip a four-column grid, the steps three columns, benefits a three-column grid, tokens a two-column split, FAQ full width with native details styling, and the final CTA a contrasting `var(--color-primary)` panel. Add `.site-footer` with a dark `var(--color-text)` background, light text and a four-column `site-footer__grid`. Add `768px` and `375px` media rules collapsing every grid to one column and making CTAs full width. No `position: fixed` on mobile. Do not remove or edit the existing global reduced-motion rule.

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_landing_page.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/static/css/app.css tests/test_landing_page.py
git commit -m "Style the new landing page and footer"
```

### Task 4: SIT, docs and full verification

**Files:**
- Modify: `scripts/sit_check.py`
- Modify: `markdown/ui_ux.md`
- Test: full suite

**Interfaces:**
- Consumes: served HTML from all three tasks.
- Produces: one SIT check named `GET / landing sections 200`.

- [ ] **Step 1: Write the failing SIT check**

Add after the public pages loop in `scripts/sit_check.py`:

```python
r = requests.get(BASE + "/")
rec("GET / landing sections 200", r.status_code == 200 and all(x in r.text for x in ('id="proof"', 'id="faq"', 'site-footer__grid', 'lp-script')), r.status_code)
```

- [ ] **Step 2: Run SIT to verify it fails**

Run: `.\.venv\Scripts\python.exe scripts/sit_check.py`
Expected: FAIL on the new check while the rest pass.

- [ ] **Step 3: Update the UI contract**

Change the landing line in `markdown/ui_ux.md` to list the ten sections and the shared footer. No other doc section changes.

- [ ] **Step 4: Run the full verification set**

Run: `.\.venv\Scripts\python.exe -m pytest -q`
Expected: all tests PASS.

Run: `.\.venv\Scripts\python.exe -m compileall -q app scripts tests`
Expected: no output, exit 0.

Run: `.\.venv\Scripts\python.exe scripts/sit_check.py`
Expected: all checks PASS against `http://127.0.0.1:5001`.

- [ ] **Step 5: Browser verification**

Open `/` in the connected browser. Check at 1440px, 1024px, 768px and 375px: all ten sections render in order, the hero preview is visible except where intentionally hidden, the footer has four columns collapsing to one, no horizontal scroll, no console errors, FAQ opens on click, and every nav anchor lands on its section. Check reduced motion with the browser emulation. Close the tab when done.

- [ ] **Step 6: Commit and push**

```bash
git add -A
git commit -m "Verify landing redesign and update UI contract"
git push origin main
```

## Self-Review

- Spec goals 1 to 5 map to Tasks 1 to 4.
- Builder answers are pinned in the spec and enforced by Task 2 tests.
- Review Focus items each have a test or browser check in the owning task.
- No task edits another task's file after its commit, so sequential subagents can work safely.
- Plan length stays close to the spec length and contains no full implementation bodies.
