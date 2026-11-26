# Landing Page Redesign Design

**Goal:** Replace the thin public landing page with a complete, credible page that explains the product and ends in a working sign up path.

**Approved:** 2026-11-26. Approach: editorial indigo, keep the existing `#5546E8` tokens and Plus Jakarta Sans / Inter / JetBrains Mono fonts.

## Intent

The current `/` page has a hero, three "how it works" cards, four feature cards, a closing CTA and a one-line footer in `base_public.html`. It says what the tool is but not why a writer should trust it or what happens after sign up. The new page covers the full decision path in one scroll, using only real product facts.

## Goals

1. Ten distinct sections in a persuasive order: nav, hero with product view, proof strip, problem, how it works, benefits, token model, FAQ, final CTA, footer.
2. The hero shows a CSS-only comic script preview, because image generation is forbidden.
3. The footer becomes a four-column block with Product, Resources, Company and Legal areas, shared by every public page through `base_public.html`.
4. Copy is plain and honest, with no invented customers, logos, testimonials, counts, pricing or uptime claims.
5. Responsive down to 375px, keyboard accessible, respects reduced motion, uses no new dependency and no build step.

## Non-goals

- No new routes, database changes, settings or backend logic.
- No images, icons from new libraries, animations beyond CSS transitions, or client-side frameworks.
- No changes to login, registration, maintenance or the authenticated shells.

## Anti-goals

- A page that looks like a different product from the app behind it.
- Fake social proof. Proof comes from real product behavior: 5 starting tokens, +5 every 48 hours, structured JSON output, Editing and Completed states, session auth and CSRF.
- A footer that repeats dead links. Every link must resolve to an existing public route.

## Constraints

- Flask application factory, Jinja2 templates, hand-written CSS3, vanilla JS, Tailwind via browser CDN and existing Material Icons via Google Fonts.
- Existing `app.css` tokens stay authoritative. No new palette.
- No emoji as icons. Use Material Icons already loaded in the page, or CSS shapes.
- All new copy passes through `@beinghuman`. No em dash or en dash in new copy.
- Tests live in `tests/`, SIT checks in `scripts/sit_check.py`.

## Approaches

1. **Editorial indigo, chosen.** Build on the current tokens, add ten sections and a real footer. Keeps visual continuity with the app and needs no new assets.
2. **Brutalist pink.** The design system search suggested pink and cyan with sharp corners. It breaks continuity with the authenticated app and was rejected.
3. **Minimal extension.** Two extra sections and a nicer footer. Cheaper, but fails the "filled" requirement.

## Builder decisions

- `app/templates/public/index.html` holds the ten sections. `app/templates/public/base_public.html` holds only the shared footer and nav changes.
- New CSS goes in a clearly marked public landing block in `app/static/css/app.css`; no new stylesheet.
- FAQ uses native `<details>` and `<summary>`, so no JS accordion is needed.
- The hero preview uses nested `div` and `span` elements styled as a script card. It is decorative with `aria-hidden="true"` and the real explanation stays in text.
- Section ids are `proof`, `problem`, `how`, `features`, `tokens`, `faq` and `start`, and the nav points at them.
- Tests assert section ids, FAQ presence, hero preview, footer columns and real-route links. SIT checks the served HTML for those ids. Browser check covers 375px, 768px, 1024px and 1440px with zero console errors.

## Builder decisions

- Product and Resources footer links use real in-page anchors and the five existing public routes. Company and Legal are plain text with no links, so no fake or broken destinations are introduced.
- The shared footer and nav in `base_public.html` render on all public pages. "No changes to login, registration, maintenance" means no edits to those page templates.
- The public base does not load Material Icons, so the landing page uses CSS shapes instead of adding a new font asset.

## Left to the builder

- Exact wording, spacing and minor layout choices, within the constraints above.
- Which of the existing `btn` and `card` classes to reuse, provided the result is distinct per section.
