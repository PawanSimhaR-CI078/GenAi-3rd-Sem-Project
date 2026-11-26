# Role Access Toggles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the editable permission checkboxes on `/admin/roles` look like brand-colored switches without changing native checkbox behavior or the saved permission payload.

**Architecture:** The existing permission matrix is built in JavaScript inside `roles.html`. Keep every editable cell as `<input type="checkbox">`, add `role="switch"` and an accessible name, and style it with one scoped CSS block. No API, backend, route or table changes.

**Tech Stack:** Flask, Jinja2, hand-written CSS3, vanilla JavaScript, pytest, browser verification.

**Spec:** `docs/superpowers/specs/2026-11-26-role-access-toggles-design.md`

## Global Constraints

- Exactly three application tables: `tolstoy_users`, `tolstoy_stories`, `tolstoy_system_settings`. Never add a table.
- No new dependency, npm, build step, framework, icon library or stylesheet.
- Keep Flask application factory, Jinja2 autoescaping, hand-written CSS3 and vanilla JavaScript.
- Keep the permission API, backend authorization, CSRF wrapper and session behavior unchanged.
- Use only existing design tokens. Primary `#5546E8`, hover `#4636D9`, border `#E4E7EF`, card `#FFFFFF`.
- Do not use copied orange or pink colors, Font Awesome or emoji icons.
- All new copy is plain and human, with no en dash or em dash.
- Native checkbox semantics stay: keyboard toggle, visible focus, disabled state and `.checked` as the source of truth.
- The save selector `#matrixBody input[type=checkbox]` and the payload keys `USER`, `ADMIN`, `SUPER_ADMIN` stay unchanged.
- SUPER_ADMIN cells stay as `✓ Full`; SUPER_ADMIN-only capabilities stay as `lock`. Neither becomes an interactive control.

## Review Focus

1. **Non-editable permissions:** a viewer without `roles_manage` must see disabled switches, not enabled ones. Test in Task 1: source assertion that `${editable?'':'disabled'}` remains on the input.
2. **Locked and Full cells:** these must remain plain text, with no switch markup. Test in Task 1: source assertions for `✓ Full`, `lock` and no switch class on those branches.
3. **Save payload:** a toggle must still send capability keys, not booleans or DOM nodes. Test in Task 1: source assertion for `#matrixBody input[type=checkbox]` and `el.checked`.
4. **Screen reader and keyboard:** each switch must have a spoken name and visible focus. Test in Task 1: source assertions for `role="switch"` and `aria-label`; Task 2 browser check with keyboard tab and toggle.
5. **Brand styling and motion:** no copied palette and no forced animation under reduced motion. Test in Task 1: CSS source assertions for the token and a scoped reduced-motion rule; Task 2 browser check.

## File Structure

- `app/templates/admin/roles.html`: switch markup in the matrix cell renderer only.
- `app/static/css/app.css`: one `/* Role access switches */` block beside the `.matrix` rules.
- `tests/test_role_access_switches.py`: source-level contract for markup, save behavior and CSS.

---

### Task 1: Switch markup and styles

**Files:**
- Modify: `app/templates/admin/roles.html:32`
- Modify: `app/static/css/app.css:217-219`
- Test: `tests/test_role_access_switches.py` (create)

**Interfaces:**
- Consumes: `esc()` from `app/templates/admin/base_admin.html:55`, `caps`, `matrix`, `roleKeys`, `locked` and `editable` already loaded by `loadMatrix()`.
- Produces: `.perm-switch` inputs with `role="switch"`, `aria-label="<capability> for <role>"`, unchanged `data-cap` and `data-role`, and CSS that styles checked and unchecked states.

- [ ] **Step 1: Write the failing test**

Create `tests/test_role_access_switches.py`:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _html():
    return (ROOT / "app/templates/admin/roles.html").read_text(encoding="utf-8")


def _css():
    return (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")


def test_editable_cells_are_accessible_switches():
    html = _html()
    assert 'class="perm-switch" type="checkbox" role="switch"' in html
    assert 'aria-label="${esc(label)} for ${r}"' in html
    assert 'data-cap="${key}" data-role="${r}"' in html
    assert "${editable?'':'disabled'}" in html


def test_locked_and_full_cells_stay_text():
    html = _html()
    assert "✓ Full" in html
    assert "lock" in html
    assert "perm-switch" not in html.split("if(r==='SUPER_ADMIN')")[1].split("if(locked.includes(key))")[0]
    assert "perm-switch" not in html.split("if(locked.includes(key))")[1].split("const checked=")[0]


def test_save_payload_is_unchanged():
    html = _html()
    assert "document.querySelectorAll('#matrixBody input[type=checkbox]')" in html
    assert "el.checked" in html
    assert "out[el.dataset.role].push(el.dataset.cap)" in html
    assert "out={USER:[],ADMIN:[],SUPER_ADMIN:['*']}" in html


def test_switch_styles_use_brand_tokens_and_respect_reduced_motion():
    css = _css()
    block = css.split("/* Role access switches */")[-1]
    assert ".perm-switch" in block
    assert "appearance: none" in block
    assert "var(--color-primary)" in block
    assert "var(--color-border)" in block
    assert ":focus-visible" in block
    assert "@media (prefers-reduced-motion: reduce)" in block
    assert ".perm-switch { transition: none; }" in block
for color in ("FF4B2B", "FF416C", "Montserrat", "fa-"):
    assert color not in block
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_role_access_switches.py`
Expected: FAIL because the switch markup and CSS block do not exist.

- [ ] **Step 3: Add switch markup**

In `app/templates/admin/roles.html`, change only the editable cell template:

```javascript
return `<td class="text-center"><input class="perm-switch" type="checkbox" role="switch" aria-label="${esc(label)} for ${r}" data-cap="${key}" data-role="${r}" ${checked} ${editable?'':'disabled'}></td>`;
```

Do not change `loadMatrix()`, `saveMatrix()`, the role keys, the Full cell, the lock cell or `checked`.

- [ ] **Step 4: Add scoped CSS**

Append one `/* Role access switches */` block after the existing `.matrix` rules in `app/static/css/app.css`.

Style `.perm-switch` as a 40px by 22px track with `appearance: none`, `border-radius: 999px`, `background: var(--color-border)`, `position: relative`, `vertical-align: middle`, `cursor: pointer`, `margin: 0` and `transition: background var(--transition)`. Draw the 16px white knob with `.perm-switch::before` and move it with `transform: translateX(18px)` when checked. Set checked track to `var(--color-primary)`. Set `:disabled` to `opacity: .55` and `cursor: not-allowed`. Add `.perm-switch:focus-visible { outline: 2px solid var(--color-primary-hover); outline-offset: 2px; }`. Add `@media (prefers-reduced-motion: reduce) { .perm-switch { transition: none; } }` inside the block. Do not use `position: fixed`.

- [ ] **Step 5: Run the test to verify it passes**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -q tests/test_role_access_switches.py`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add app/templates/admin/roles.html app/static/css/app.css tests/test_role_access_switches.py
git commit -m "Style Role Access permission switches"
```

### Task 2: Full verification and push

**Files:**
- No source file changes expected. If `markdown/ui_ux.md` names the control type, update only that line; it currently does not.

**Interfaces:**
- Consumes: markup and styles from Task 1.
- Produces: verified result on `main`.

- [ ] **Step 1: Run automated checks**

Run each and record exact output:
- `.\\.venv\\Scripts\\python.exe -m pytest -q`
- `.\\.venv\\Scripts\\python.exe -m compileall -q app scripts tests`

- [ ] **Step 2: Browser verification**

Load the `browser` skill before the first browser tool call. Start the Flask server on port 5001 in the background and sign in at `/admin/login` as `Pawan Simha R` with the local demo password from `readme.md`.

Check that:
- `/admin/roles` shows switches for editable USER and ADMIN cells.
- SUPER_ADMIN cells still read `✓ Full` and locked cells still read `lock`.
- Tab reaches a switch, focus is visible, Space toggles it, and the Save permissions button appears.
- Toggling and saving keeps the same capability keys in the API request.
- A viewer without `roles_manage` sees disabled switches.
- No console errors.

Close every tab opened and stop the server.

- [ ] **Step 3: Commit and push**

If Step 2 required a source change, commit it with message `Verify Role Access switches`. Otherwise do not create an empty commit. Push with `git push origin main`. Also confirm the approved design doc `docs/superpowers/specs/2026-11-26-role-access-toggles-design.md` and this plan are included in a commit on `main`.

## Self-Review

- Spec goals 1 to 5 map to Task 1; browser and accessibility outcomes map to Task 2.
- All five Review Focus inputs have a source or browser test in an owning task.
- Save payload, locked cells, Full cells, CSRF and backend authorization are untouched.
- No new file besides one focused test; CSS stays in the existing stylesheet.
- The plan is shorter than the code it describes only in test code blocks, which pin exact strings the builder cannot guess.
