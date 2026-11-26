# Role Access permission switches design

**Status:** Proposed on 2026-11-26, awaiting owner approval.

**Intent:** The Role Access matrix at `/admin/roles` uses plain checkboxes for editable permissions. Replace their look with brand-colored switches so the page reads more clearly, without changing how permissions are stored or saved.

## What is there now

`app/templates/admin/roles.html` builds the matrix in JavaScript from `/api/v1/admin/roles/permissions`. Each editable cell is an `<input type="checkbox" data-cap="..." data-role="..." checked?>`. `saveMatrix()` collects checked boxes with `document.querySelectorAll('#matrixBody input[type=checkbox]')` and sends `{USER: [...], ADMIN: [...], SUPER_ADMIN: ['*']}` through a PUT with the shared CSRF-aware fetch. SUPER_ADMIN cells render as `✓ Full`. SUPER_ADMIN-only capabilities render as `lock`. Neither is an editable checkbox.

## Goals

1. Editable permission cells look and behave like on/off switches.
2. The switch uses TOLSTOY tokens only: primary `#5546E8`, hover `#4636D9`, border `#E4E7EF`, card `#FFFFFF` and muted text.
3. Native checkbox semantics stay: keyboard toggle, visible focus, disabled state, `.checked` and the existing `input[type=checkbox]` save selector.
4. Each switch has a spoken name that says the capability and role.
5. Reduced motion is respected. No new dependency, framework, route, table or API change.

## Non-goals

- No change to the permission API, backend authorization, locked cells or the "Full" cells.
- No change to user or admin login, the public pages, or other admin pages.
- No new stylesheet, npm package, build step or icon library.

## Approaches

1. **Styled native checkbox, chosen.** Add `role="switch"` and `aria-label` to the existing checkbox and draw the track and knob in CSS. Save logic and keyboard behavior stay intact. Smallest change.
2. **`<button aria-pressed>` toggles.** Needs manual state, disabled handling and a new save extraction path. More JS and more failure modes.
3. **`<input type="checkbox" switch>`.** Not supported in Chrome, Edge or Firefox without a polyfill. A new dependency is forbidden here, so this is ruled out.

## Builder decisions

- Add class `perm-switch`, `role="switch"` and `aria-label="<capability> for <role>"` to each editable checkbox. Use the existing `esc()` helper for the label.
- Add one scoped `/* Role access switches */` block in `app/static/css/app.css` beside the `.matrix` rules. Style the checked track with `var(--color-primary)`, the unchecked track with `var(--color-border)`, and the knob with `#fff`. Use `appearance: none` and a short transform transition. Keep the existing global `:focus-visible` rule and add a switch-specific focus ring if needed.
- Keep `input[type=checkbox]` in the DOM and in `saveMatrix()`. Do not rename the data attributes or change the payload.
- Leave `✓ Full` and `lock` cells as text.
- Add focused tests that read `roles.html` and `app.css`, asserting the switch class, `role="switch"`, the accessible name pattern, the unchanged save selector, the brand tokens and no new dependency.
- Update `markdown/ui_ux.md` only if its Role Access contract mentions the control type.

## Verification

- Run pytest and compileall.
- Browser check `/admin/roles` as a SUPER_ADMIN: switches render, keyboard toggles them, focus is visible, locked and Full cells remain text, and saving a toggle sends the same capability keys as before.
- Disclose that `modern-web-guidance` was consulted locally through its `forms/switch.md` guide because npm and npx are unavailable in this environment; the native `switch` attribute path was rejected because its fallback needs a forbidden dependency.
