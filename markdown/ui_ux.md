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

- **Dashboard:** summary cards + ~5–6 charts:
  1. Total registered users (doughnut: active vs inactive).
  2. Stories by status (bar: editing vs completed).
  3. Story creation trend (line: per day/week).
  4. Tokens consumed over time (line).
  5. Gemini input vs output tokens (bar).
  6. Top users by story count (bar).
- **User management:** table, search/filter, edit, activate/deactivate, adjust tokens.
- **Story management:** table with filters, view, delete/archive.
- **Database viewer:** paginated tables for the three approved tables; password hashes and secrets masked.
- **System settings:** edit key/value with type validation.
- **Maintenance mode:** toggle with password re-entry.

## 6. Responsive Behavior

- Mobile: collapsible sidebar (hamburger), stacked forms, horizontal-scroll tables, touch-friendly buttons (min 44px).
- Tablet: collapsible or persistent narrow sidebar.
- Desktop: persistent sidebar.
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