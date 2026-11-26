# TOLSTOY landing refinement design

**Status:** Approved by the owner's 2026-11-26 implementation brief. Scope for this pass is the public landing page and its shared public shell.

**Intent:** The landing page already has the required sections, brand colors and native FAQ accordion. The remaining friction is a six-link navigation bar that wraps into three rows on phones, a plain three-step row with no visual connection, a secondary token CTA, an 11px script preview at 320px, and a duplicate Google Fonts request. Fix those without touching backend rules, token pricing, authentication or API contracts.

**Approaches considered:**
1. Full application-wide redesign in one pass. Rejected for this pass because the owner's final instruction was to update the landing page; the other pages are already aligned with the same tokens.
2. Landing-only refinement using existing CSS tokens and vanilla JS. Chosen. It keeps the current structure and fixes measured defects.
3. Introduce a component framework or build step. Rejected by AGENTS.md.

**What changes:**
- Collapsible mobile navigation using a button with `aria-expanded` and `aria-controls`; the same shared public header is used on login and register, so the control must not depend on the page path.
- Desktop connector line behind the three step cards, with the badges above it.
- Token section CTA becomes the primary button.
- Remove the 11px override at 320px so the script preview stays at 12px.
- Remove the CSS `@import` for Google Fonts because all three base templates already load the same fonts.
- FAQ hover and focus polish, with no JS accordion rewrite.

**Non-goals:** no backend, database, session, CSRF, token or Gemini changes; no new dependency, icon library or build step; no new decorative graphics; no removal of sections or links; no em dashes or en dashes in new copy.

**Left to the builder:** exact CSS values that match the existing token scale and breakpoint boundaries.
