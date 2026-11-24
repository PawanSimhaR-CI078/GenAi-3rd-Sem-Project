# TOLSTOY — UI/UX Specification

## 1. Stack

HTML5, Jinja2, CSS3, Vanilla JS. Tailwind and Chart.js via CDN (pin versions before production). No build step.

## 2. Base Templates

- `base_public.html` — landing, auth, maintenance, errors.
- `base_user.html` — authenticated user area (top nav + sidebar).
- `base_admin.html` — admin area.
- Reusable Jinja macros: button, form field, card, modal, table, notification, empty state, spinner.

## 3. Public Pages

- **Landing:** hero, features, CTA (login/register).
- **Register:** username, password, display name, phone (optional), validation.
- **User login:** username + password.
- **Admin login:** separate route/page.
- **Maintenance:** shown to users when maintenance mode active.
- **Errors:** 404, 403, 500 pages.

## 4. User Area

### Top Navigation Bar

- Logo/name, user info, token balance (live), live clock, current date, logout.

### Sidebar

Dashboard, Create Story, My Stories, Editing, Completed, Token Wallet, Contact Admin, Profile/Settings.

### Dashboard

- Welcome message with display name.
- Token balance card.
- Total stories, Editing count, Completed count.
- Recent stories list.
- "Create New Story" CTA.

### Create Story

Form: title, story content/idea, character gender, target audience, desired length, language. Validation + helper text.

### Story Editor

- Editable metadata.
- Generated script rendered as structured scenes/panels (read-only view + raw JSON toggle).
- Save changes, Regenerate (if permitted), status toggle (Editing/Completed).

### My Stories

Tabs/sections: Editing, Completed. Move between statuses. Empty states.

### Token Wallet

- Current balance, next refill time, refill rules (+5 every 48h), tokens consumed (from stories where available).
- No transaction history (not available).

### Contact Admin

Form: subject, message. Success/error feedback. Rate-limited.

### Profile/Settings

Display name, password change (future). Keep minimal.

## 5. Admin Area

Sidebar sections: Analytics, User Editing, Role Access, Live Database, Stories, Settings, System Control.
Links are hidden when the role lacks the capability.

- **Analytics:** grouped KPI cards (users, stories, tokens), 9 charts (user growth, users by role,
  token balance distribution, stories by status, generation outcomes, stories per day, tokens per day,
  top users, Gemini usage), complete database overview (table counts, size, on-demand integrity check),
  recent signups and recent stories. Range selector: 7 / 30 / 90 / all.
- **User Editing:** searchable/filterable table with a side drawer for username, display name, phone
  and active state (ADMIN+). The “Add tokens” control appears only for SUPER_ADMIN, is increase-only,
  and shows a live preview of the new balance.
- **Role Access:** SUPER_ADMIN only. Permission matrix (capabilities × roles, SUPER_ADMIN locked)
  plus user role assignment with password re-entry and guardrails. Locked capabilities render as
  🔒 and cannot be granted to USER/ADMIN.
- **Live Database:** table switcher, row search, pagination, optional 5-second auto-refresh, row detail,
  hidden password hashes and masked secrets. Read-only.
- **Story management:** table with filters, view, delete/archive.
- **System settings:** SUPER_ADMIN only; key/value list. Internal structured settings such as
  `role_permissions` are hidden and linked to Role Access; maintenance toggle moved to System Control.
- **System Control:** SUPER_ADMIN only. ONLINE/OFFLINE status card, affected-user count, password
  re-entry, typed confirmation, persistent offline badge in the topbar.
- **Admin entry points:** public nav and landing Admin card link to `/admin/login`; an ADMIN/SUPER_ADMIN
  signing in through `/login` lands on `/admin`. Their user sidebar also shows an Admin Panel link.

## 6. Responsive Behavior

- Mobile: collapsible sidebar drawer (hamburger), backdrop, close button, Escape/outside-click close,
  body scroll lock; stacked forms, horizontal-scroll tables, touch-friendly buttons (min 44px).
  The same drawer pattern applies to user and admin layouts.
- Tablet: collapsible or persistent narrow sidebar.
- Desktop: persistent sidebar; mobile controls hidden.
- Charts resize via Chart.js responsive option.

## 7. Consistency

- Shared CSS variables for colors, spacing, typography.
- Consistent button styles (primary/secondary/danger).
- Form validation messages inline.
- Loading spinners on async actions.
- Empty states with CTA.
- Confirmation dialogs for destructive actions.
- Toast/notification system for success/error.

## 8. Accessibility

- Semantic HTML, labels, ARIA where needed, keyboard navigation, focus states, sufficient contrast.<|end|><|start|>write to=assistant<|channel|>analysis<|message|>Wrote file successfully: markdown/ui_ux.md