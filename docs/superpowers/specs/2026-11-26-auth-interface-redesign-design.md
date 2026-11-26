# Auth interface redesign design

**Goal:** Give TOLSTOY the split sign in and sign up feel from the copied example, using TOLSTOY's own colors, real form fields and real auth endpoints.

**Status:** Proposed on 2026-11-26, awaiting owner approval. Approach: one shared sliding auth screen rendered by `/login` and `/register`. Admin sign in stays separate.

## Intent

The copied example has a split card, a sliding overlay and two forms in one view. TOLSTOY already has working auth pages, but they are plain cards and sit side by side as separate URLs. This change keeps the useful interaction and drops everything that would mislead a user: social buttons, a password reset link with no destination, a creator credit, fake `action="#"` forms and the orange and pink palette.

## Goals

1. `/login` and `/register` render the same shared auth shell with the correct side open on first load.
2. The overlay buttons switch between sign in and sign up without a full reload and update the visible URL to `/login` or `/register` with `history.replaceState`.
3. Keep the real fields and behavior already in TOLSTOY:
   - Sign in: username, password, show/hide toggle, sign in button.
   - Register: username, display name, password, length hints, create account button.
4. Use the existing endpoints and the shared fetch wrapper so CSRF stays attached.
5. Use TOLSTOY tokens only, especially `#5546E8`, `#4636D9`, `#F0EEFF`, `#FFFFFF`, `#F7F8FC`, `#E4E7EF` and the existing text colors. Keep the existing Plus Jakarta Sans, Inter and JetBrains Mono fonts.
6. Work at 375px with no horizontal scroll. On small screens, hide the sliding overlay and show one form at a time through two labelled buttons.
7. Keep labels visible, errors announced with `role="alert"`, submit buttons showing loading text, password visibility toggles and visible keyboard focus.
8. Leave `/admin/login`, maintenance, roles, sessions and all backend auth behavior unchanged.

## Non-goals

- No new route, table, dependency, npm, build step, image generation or frontend framework.
- No social login, OAuth, password reset or contact flow.
- No Font Awesome CDN or Font Awesome classes.
- No changes to the admin sign in page.
- No changes to the public nav or footer contract.
- No changes to the API or schema.

## Anti-goals

- A copy of the example's orange and pink look.
- Dead `href="#"` links or buttons that do nothing.
- Placeholder-only inputs, invisible focus rings or motion that ignores reduced motion.
- A second auth implementation that drifts from the shared CSRF wrapper.

## Constraints

- Flask application factory, Jinja2, hand-written CSS3 and vanilla JavaScript only.
- Jinja autoescaping stays on. Never render untrusted content with `safe` or `innerHTML`.
- CSRF token comes from the existing `getCsrf` and wrapped `fetch` in `app/static/js/app.js`.
- All new copy is plain and human, with no en dash or em dash.
- Existing tests that assert inline redirect strings must be updated to read the shared partial instead of expecting those strings in `login.html`.
- `modern-web-guidance` cannot run in this environment because npm and npx are unavailable. Local UI guidance was used for form labels, announced errors, submit feedback and password visibility.

## Approaches

1. **One sliding auth screen, chosen.** Both URLs render one shell. This matches the request, keeps two working entry points and avoids duplicate form code. It needs a small amount of JS for the panel switch and URL update.
2. **Two matching split pages.** Simpler, but loses the sliding interaction the user asked for.
3. **Restyled cards only.** Cheapest, but still feels like the current plain pages.

## Builder decisions

- `app/templates/public/_auth_shell.html` holds both forms, the overlay and the panel state class.
- `app/templates/public/_auth_script.html` holds the panel switch, URL update, show/hide toggle and submit handlers.
- `app/templates/public/login.html` and `register.html` become thin wrappers that set `auth_mode` to `login` or `register` and include the shared partials. Route handlers stay unchanged.
- The page keeps the shared public nav and footer because `tests/test_landing_page.py` asserts that contract on every public page.
- Sign in is the initial panel for `/login`. Sign up is the initial panel for `/register`.
- The overlay buttons are `type="button"` and use real labels. No icon-only buttons.
- On desktop, the overlay slides with a CSS transform. On screens up to 768px, the overlay is hidden, a small mode switch is shown, and one form is visible at a time. The hidden form uses the `hidden` attribute.
- Each form gets its own error element with `role="alert"` and `aria-live="polite"`. On failed submit, focus moves to that element.
- On submit, the active button is disabled and shows `Signing in...` or `Creating...`, then returns to its normal label.
- The success redirects stay exactly as they are today: admins and super admins go to `/admin/home`, users go to `/home`, registration goes to `/login`.
- New CSS goes in one marked `/* Auth interface */` block in `app/static/css/app.css`. No new stylesheet.
- The admin page is not touched, even visually, so its existing test keeps its exact strings.

## What the builder should settle

- Exact spacing, border radius and transition timing, using existing tokens.
- Whether the register password toggle sits inside the input like the current sign in page, as long as it stays keyboard accessible.
- Exact overlay copy, provided it stays factual and dash free.
- Test names and the smallest set of assertions that prove the structure, initial state, real endpoints and absence of the copied palette and dead links.

## Verification

- Add a focused pytest file for the shared shell on both URLs.
- Update `tests/test_ui_navigation.py::test_login_forms_redirect_to_welcome_page` to assert the shared script file while leaving admin assertions on `admin_login.html`.
- Add SIT checks that `/login` and `/register` both render the shell.
- Run pytest, compileall, SIT and browser checks at 1440px, 768px and 375px. Browser checks cover panel switching, URL updates, submit feedback, error announcement, password toggles, focus visibility, reduced motion and no console errors.
