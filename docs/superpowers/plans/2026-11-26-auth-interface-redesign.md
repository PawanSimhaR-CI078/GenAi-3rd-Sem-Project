# Auth Interface Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plain user sign in and sign up cards with one shared, brand-colored sliding auth screen at `/login` and `/register`.

**Architecture:** Two thin Jinja wrappers set `auth_mode` and include one shared markup partial and one shared inline script partial. The existing route handlers, API endpoints, CSRF wrapper, session redirects and admin sign in page stay unchanged. New CSS is scoped to the split auth shell so the admin card and other pages are not restyled.

**Tech Stack:** Flask, Jinja2, hand-written CSS3, vanilla JS, Tailwind CDN already present in the public base, pytest, SIT script, Chrome browser checks.

**Spec:** `docs/superpowers/specs/2026-11-26-auth-interface-redesign-design.md`

## Global Constraints

- No new route, table, dependency, npm, build step, image generation or frontend framework.
- Keep Flask application factory, Jinja2 autoescaping, hand-written CSS3 and vanilla JavaScript.
- Keep `/admin/login`, maintenance, roles, sessions and backend auth behavior unchanged.
- Keep the shared public nav and footer on every public page.
- Use only existing design tokens. Primary is `#5546E8`, hover is `#4636D9`, subtle is `#F0EEFF`, card is `#FFFFFF`, page background is `#F7F8FC`, border is `#E4E7EF`, text is `#171A35`.
- Do not use the copied orange and pink colors, Font Awesome, Montserrat, social login buttons, a fake password reset link, a creator credit or a fixed footer.
- No `href="#"`, dead controls, placeholder-only inputs or icon-only buttons.
- All new copy is plain and human, with no en dash or em dash.
- CSRF comes only from the existing `getCsrf` and wrapped `fetch` in `app/static/js/app.js`.
- Redirects stay exact: admins and super admins to `/admin/home`, users to `/home`, registration to `/login`.
- Respect visible focus, announced errors, submit feedback, password visibility, 375px layout and reduced motion.

## Review Focus

1. **Admin sign in after the shared restyle:** it must keep its own page and exact redirect strings. Test: preserve `test_login_forms_redirect_to_welcome_page` admin assertions in Task 2 and browser check `/admin/login` in Task 4.
2. **Panel switching without reload:** overlay buttons must switch panels and update the URL to `/login` or `/register`. Test: source assertions in Task 2 and browser click checks in Task 4.
3. **Narrow screens:** at 375px the overlay hides, one form shows at a time and there is no horizontal scroll. Test: CSS source assertions in Task 3 and browser check in Task 4.
4. **Failed sign in or registration:** the error must be announced with `role="alert"` and receive focus. Test: markup assertions in Task 1 and browser error-state check in Task 4.
5. **Reduced motion and focus:** no slide animation under reduced motion, and focus stays visible on the primary overlay. Test: CSS source assertions in Task 3 and browser emulation in Task 4.

## File Structure

- `app/templates/public/_auth_shell.html`: both forms, overlay, mobile mode switch, panel state class.
- `app/templates/public/_auth_script.html`: panel switching, URL update, password toggles, submit handlers.
- `app/templates/public/login.html`: thin wrapper setting `auth_mode = 'login'`.
- `app/templates/public/register.html`: thin wrapper setting `auth_mode = 'register'`.
- `app/static/css/app.css`: one new `/* Auth interface */` block after the public landing block.
- `tests/test_auth_interface.py`: new focused pytest file.
- `tests/test_ui_navigation.py`: update only the inline redirect source assertions in `test_login_forms_redirect_to_welcome_page`.
- `scripts/sit_check.py`: add served HTML checks for `/login` and `/register`.
- `markdown/ui_ux.md`: update the user login and admin login contract lines.

---

### Task 1: Shared auth shell markup

**Files:**
- Create: `app/templates/public/_auth_shell.html`
- Modify: `app/templates/public/login.html`
- Modify: `app/templates/public/register.html`
- Test: `tests/test_auth_interface.py`

**Interfaces:**
- Consumes: `public/base_public.html` blocks `title`, `content`, `scripts`; Jinja variable `auth_mode` from the wrapper templates.
- Produces: classes `auth-wrapper--split`, `auth-shell`, `auth-form-panel`, `auth-form-panel--signin`, `auth-form-panel--signup`, `auth-overlay-container`, `auth-overlay`, `auth-overlay-panel`, `auth-mode-switch`; ids `authContainer`, `loginForm`, `registerForm`, `loginMsg`, `registerMsg`, `authSignInBtn`, `authSignUpBtn`, `authMobileSignIn`, `authMobileSignUp`, `loginSubmitBtn`, `registerSubmitBtn`; `data-auth-mode` on `authContainer`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_auth_interface.py` with:

```python
def test_login_and_register_share_auth_shell(client):
    login = client.get("/login").get_data(as_text=True)
    register = client.get("/register").get_data(as_text=True)
    for html in (login, register):
        assert "auth-wrapper--split" in html
        assert "auth-form-panel--signin" in html
        assert "auth-form-panel--signup" in html
        assert "auth-overlay-container" in html
        assert "auth-mode-switch" in html
        for required in ("loginForm", "registerForm", "loginMsg", "registerMsg",
                         "loginUsername", "loginPassword", "registerUsername",
                         "registerDisplayName", "registerPassword"):
            assert required in html
        assert 'role="alert"' in html
        assert 'href="#"' not in html
        assert "fa-" not in html
        assert "Montserrat" not in html
        assert "FF4B2B" not in html and "FF416C" not in html

    assert 'data-auth-mode="login"' in login
    assert 'data-auth-mode="register"' in register
    assert "right-panel-active" not in login
    assert "right-panel-active" in register
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_auth_interface.py`
Expected: FAIL because the shared shell does not exist.

- [ ] **Step 3: Build the shared shell and thin wrappers**

Create `_auth_shell.html`. Use a wrapper `<div class="auth-wrapper auth-wrapper--split">` and a container `<div id="authContainer" class="auth-shell{% if auth_mode == 'register' %} right-panel-active{% endif %}" data-auth-mode="{{ auth_mode }}">`.

Include both forms in the DOM. Sign in fields: `loginUsername`, `loginPassword`, a `type="button"` show/hide control, submit button `loginSubmitBtn`, and error element `loginMsg` with `role="alert"` and `aria-live="polite"`. Register fields: `registerUsername`, `registerDisplayName`, `registerPassword`, a `type="button"` show/hide control, the existing username and password hints, submit button `registerSubmitBtn`, and error element `registerMsg` with the same accessibility attributes. Use visible `<label for="...">` elements. Keep the existing cross-links: `No account? Create one` linking to `/register` and `Already have an account? Sign in` linking to `/login`.

Include the overlay with two panels and two `type="button"` controls `authSignInBtn` and `authSignUpBtn`. The left panel says `Welcome back` and explains that sign in is for existing accounts. The right panel says `New to TOLSTOY` and mentions 5 starting tokens. Do not add social buttons, a reset link or a creator footer. Include a mobile-only `auth-mode-switch` with buttons `authMobileSignIn` and `authMobileSignUp`.

Make `login.html` and `register.html` thin wrappers. Each extends `public/base_public.html`, sets `auth_mode` to `login` or `register`, keeps its own `title` block, includes `_auth_shell.html` in the `content` block, and leaves the `scripts` block empty for Task 2.

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_auth_interface.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/public/_auth_shell.html app/templates/public/login.html app/templates/public/register.html tests/test_auth_interface.py
git commit -m "Add shared sliding auth shell"
```

### Task 2: Shared auth behavior

**Files:**
- Create: `app/templates/public/_auth_script.html`
- Modify: `app/templates/public/login.html`
- Modify: `app/templates/public/register.html`
- Modify: `tests/test_ui_navigation.py`
- Test: `tests/test_auth_interface.py`

**Interfaces:**
- Consumes: all ids produced by Task 1 and the wrapped `fetch` in `app/static/js/app.js`.
- Produces: `window.TOLSTOY.authReady = true`; overlay and mobile mode switches toggle `right-panel-active` and call `history.replaceState`; both submit handlers use the existing API endpoints and redirects.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_auth_interface.py`:

```python
def test_shared_auth_script_uses_real_endpoints(client):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    script = (root / "app/templates/public/_auth_script.html").read_text(encoding="utf-8")
    html = client.get("/login").get_data(as_text=True)

    assert "history.replaceState" in script
    assert "'/login'" in script and "'/register'" in script
    assert "/api/v1/auth/user/login" in script
    assert "/api/v1/auth/register" in script
    assert "sessionStorage.setItem('tolstoy_tab','1')" in script
    assert "'/admin/home'" in script and "'/home'" in script
    assert ".focus()" in script
    assert "authReady" in script
    assert "_auth_script.html" not in html
    assert "loginForm" in html
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_auth_interface.py::test_shared_auth_script_uses_real_endpoints`
Expected: FAIL because the script partial does not exist.

- [ ] **Step 3: Implement the shared script**

Create `_auth_script.html` as a `<script>` partial. Do not add a new static file. Use only vanilla JS.

Implement:
- A `setMode(mode)` function that toggles `right-panel-active` on `#authContainer`, updates `data-auth-mode`, calls `history.replaceState(null, '', mode === 'register' ? '/register' : '/login')`, toggles the `hidden` attribute on the two form panels for mobile, and updates `aria-pressed` on the two mobile switch buttons.
- Click handlers for the overlay controls `authSignInBtn`, `authSignUpBtn` and the mobile controls `authMobileSignIn`, `authMobileSignUp` that call `setMode` with the matching mode. The form submit buttons are `loginSubmitBtn` and `registerSubmitBtn`.
- A password toggle for both password fields that flips `type` between `password` and `text` and updates its button text between `show` and `hide`.
- Submit handlers for `loginForm` and `registerForm` that prevent default, disable the active button, show `Signing in...` or `Creating...`, post to `/api/v1/auth/user/login` and `/api/v1/auth/register` with `credentials: 'same-origin'`, restore the button label, announce failures through `loginMsg` or `registerMsg` with `textContent`, focus the message element, and keep the existing success redirects.
- Set `window.TOLSTOY.authReady = true` at the end. Initialize the page from `data-auth-mode` on load.

In `login.html` and `register.html`, include `_auth_script.html` in the `scripts` block.

Update `tests/test_ui_navigation.py::test_login_forms_redirect_to_welcome_page` so the user login assertions read `app/templates/public/_auth_script.html` instead of `login.html`. Keep all admin assertions on `admin_login.html` exactly as they are.

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_auth_interface.py tests/test_ui_navigation.py::test_login_forms_redirect_to_welcome_page`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/public/_auth_script.html app/templates/public/login.html app/templates/public/register.html tests/test_auth_interface.py tests/test_ui_navigation.py
git commit -m "Add shared auth panel behavior"
```

### Task 3: Auth interface styles

**Files:**
- Modify: `app/static/css/app.css`
- Test: `tests/test_auth_interface.py`

**Interfaces:**
- Consumes: classes from Task 1 and existing `:root` tokens.
- Produces: scoped CSS for `.auth-wrapper--split`, `.auth-shell`, `.auth-form-panel`, `.auth-overlay-container`, `.auth-overlay`, `.auth-overlay-panel`, `.auth-mode-switch`, `.auth-error`, `.right-panel-active`, plus responsive and reduced-motion rules.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_auth_interface.py`:

```python
def test_auth_interface_styles(client):
    from pathlib import Path

    css = (Path(__file__).resolve().parents[1] / "app/static/css/app.css").read_text(encoding="utf-8")
    for selector in (".auth-wrapper--split", ".auth-shell", ".auth-form-panel",
                     ".auth-overlay-container", ".auth-overlay-panel", ".auth-mode-switch",
                     ".auth-error", ".right-panel-active"):
        assert selector in css
    assert "#5546E8" not in css.split("/* Auth interface */")[-1].replace("--color-primary: #5546E8;", "")
    assert "FF4B2B" not in css and "FF416C" not in css
    assert "@media (max-width: 768px)" in css.split("/* Auth interface */")[-1]
    assert "@media (prefers-reduced-motion: reduce)" in css.split("/* Auth interface */")[-1]
    assert ".auth-shell :focus-visible" in css
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_auth_interface.py::test_auth_interface_styles`
Expected: FAIL because the auth block does not exist.

- [ ] **Step 3: Add one scoped CSS block**

Append to `app/static/css/app.css` under `/* Auth interface */`, after the public landing block. Do not edit the existing `.auth-wrapper`, `.auth-card` or `.auth-logo` rules, because the admin page uses them.

Use only existing tokens. Give `.auth-wrapper--split` a centered flex layout with enough top and bottom space for the shared nav and footer. Give `.auth-shell` a white card, soft shadow, rounded corners, hidden overflow, `768px` max width and `480px` min height. Place `.auth-form-panel` panels absolutely at 50% width. Style `.auth-overlay` with a `linear-gradient(135deg, var(--color-primary), var(--color-primary-hover))`, not the copied orange and pink. Style the overlay buttons with transparent backgrounds and white borders. Style `.auth-error` with `var(--color-error)`.

Add `.auth-shell :focus-visible { outline-color: var(--color-primary-hover); outline-offset: 3px; }`. Add `.auth-form-panel[hidden] { display: none; }` so the `hidden` attribute wins over the panel's `display: flex`. Add a scoped `@media (max-width: 768px)` block that hides `.auth-overlay-container`, shows `.auth-mode-switch`, stacks the shell, shows one form at a time and gives buttons full width. Add a scoped `@media (prefers-reduced-motion: reduce)` block that removes transform transitions on `.auth-shell`, `.auth-form-panel` and `.auth-overlay-container`. Do not use `position: fixed`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest -q tests/test_auth_interface.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/static/css/app.css tests/test_auth_interface.py
git commit -m "Style the shared auth interface"
```

### Task 4: SIT, docs and full verification

**Files:**
- Modify: `scripts/sit_check.py`
- Modify: `markdown/ui_ux.md`
- Test: full suite

**Interfaces:**
- Consumes: served HTML from Tasks 1 to 3.
- Produces: SIT checks named `GET /login auth shell 200` and `GET /register auth shell 200`.

- [ ] **Step 1: Write the failing SIT checks**

Add after the public pages loop in `scripts/sit_check.py`:

```python
for path in ("/login", "/register"):
    r = requests.get(BASE + path)
    mode = "login" if path == "/login" else "register"
    rec(f"GET {path} auth shell 200", r.status_code == 200 and all(x in r.text for x in ("auth-wrapper--split", "auth-form-panel--signin", "auth-form-panel--signup", f'data-auth-mode="{mode}"')), r.status_code)
```

- [ ] **Step 2: Run SIT to verify it fails**

Start the server if needed, then run `.\.venv\Scripts\python.exe scripts/sit_check.py`.
Expected: FAIL on the new checks before the implementation is present. If the checks already pass because earlier tasks landed, record that plainly and continue.

- [ ] **Step 3: Update the UI contract**

In `markdown/ui_ux.md`, change the user login and admin login lines to say that user login and registration share one sliding screen at `/login` and `/register`, while admin login remains a separate route and page. Do not change any other section.

- [ ] **Step 4: Run full verification**

Run each and report exact results:
- `.\.venv\Scripts\python.exe -m pytest -q`
- `.\.venv\Scripts\python.exe -m compileall -q app scripts tests`
- `.\.venv\Scripts\python.exe scripts/sit_check.py` against `http://127.0.0.1:5001`

- [ ] **Step 5: Browser verification**

Load the `browser` skill before the first browser tool call. Open `/login`, `/register` and `/admin/login`.

At 1440px, 768px and 375px, check:
- `/login` opens on sign in and `/register` opens on sign up.
- Overlay buttons switch panels without a full reload and update the URL.
- Mobile mode switch shows one form at a time with no horizontal scroll.
- Password toggles work on both forms.
- Submit feedback appears while a form is pending.
- Both error elements expose `role="alert"` and `aria-live`; their focus behavior is covered by the shared script assertions.
- Focus is visible on the primary overlay.
- Reduced motion removes the slide transition.
- `/admin/login` still renders its own card and its existing script, with no shared auth classes present.
- No console errors.
Close every tab opened.

- [ ] **Step 6: Commit and push**

```bash
git add -A
git commit -m "Verify auth interface redesign and update UI contract"
git push origin main
```

## Self-Review

- Spec goals 1 to 8 map to Tasks 1 to 4.
- All five Review Focus items have a source or browser test in the owning task.
- File ownership is disjoint after each commit, so sequential subagents can work safely.
- Admin page, backend, CSRF, routes, database and dependencies are untouched.
- Test assertions pin real endpoint strings, initial panel state, responsive rules and absence of the copied assets.
- Plan decisions are pinned where a wrong guess would matter; spacing and exact overlay wording stay with the builder as the spec allows.
