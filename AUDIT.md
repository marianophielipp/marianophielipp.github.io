# Professional Website Audit — Mariano Phielipp

**Audit date:** March 2026  
**Scope:** marianophielipp.github.io (HTML, CSS, JS, data)

---

## Executive Summary

The site is a clean, template-based professional site with solid SEO (Open Graph, Twitter Cards), responsive layout, and a data-driven publications page. The main issues are: **one JavaScript bug** (util.js early return), **missing accessibility/document standards** (no `lang`, `user-scalable=no`), **XSS risk** in publications rendering, **inconsistent UX** (breadcrumbs and return-to-top only on some pages), **fragile publications code** (no null checks, cache-busting in URL), and **duplicated HTML** across pages. Below are findings by category and recommended fixes.

---

## 1. Bugs & Broken Behavior

### 1.1 util.js — Panel early return (bug)

**Location:** `assets/js/util.js` lines 45–46 and 53–54.

**Problem:** When `this.length === 0` or `this.length > 1`, the function returns `$this` before `var $this = $(this)` is executed. Because of hoisting, `$this` is undefined at those points, so the plugin returns `undefined` instead of a jQuery object. This can break chaining and cause errors if callers assume a jQuery object.

**Fix:** Return `$(this)` in both early-exit cases:

```javascript
if (this.length == 0)
    return $(this);
// ...
return $(this);
```

### 1.2 publications.js — Possible runtime errors on malformed data

**Location:** `assets/js/publications.js` (e.g. `pub.authors.join`, `pub.authors.some`).

**Problem:** If `data.json` has an entry without `authors` (or with a non-array), `pub.authors.join(', ')` or `pub.authors.some(...)` will throw.

**Fix:** Use safe access and defaults, e.g. `(pub.authors || []).join(', ')`, and guard filters with `Array.isArray(pub.authors)` or a helper that returns an array.

### 1.3 Index page date typo

**Location:** `index.html` line 114.

**Problem:** Text says "As of January **2026**" but the visible datetime is "2025" (`datetime="2025-01-01"`). Inconsistent and confusing.

**Fix:** Align content and `<time datetime="...">` (e.g. both 2026 or both 2025) and use a single source of truth.

---

## 2. UX / UI Issues

### 2.1 Breadcrumbs only on inner pages

**Problem:** `index.html` has no breadcrumb; bio, research, contact, publications, and 404 do. Home feels inconsistent and users lose a clear “Home” anchor on the main landing.

**Fix:** Add a minimal breadcrumb on the homepage (e.g. “Home” only) so the pattern is consistent, or document that home intentionally has no breadcrumb and ensure the header “Mariano Phielipp” link to `index.html` is obvious.

### 2.2 Return-to-top and footer consistency

**Problem:** The floating “Return to Top” button exists on bio, research, contact, publications, and 404, but **not** on `index.html`. Long home content would benefit from the same behavior.

**Fix:** Add the same `#return-to-top` block and scripts on `index.html` so behavior is consistent.

### 2.3 Sidebar “Posts” thumb dimensions

**Location:** `index.html` line 244, `contact.html` line 265 (and similar elsewhere).

**Problem:** One sidebar post image uses `width="51" height="51"` (pic08) while others use `351×176`. That makes the thumbnail tiny and visually inconsistent.

**Fix:** Use the same aspect ratio/sizing as other sidebar thumbs (e.g. 351×176) or replace pic08 with an image that matches. If 51×51 is intentional, add a CSS class so the layout stays consistent (e.g. object-fit and fixed height).

### 2.4 Decorative links with `href="#"`

**Problem:** Many elements use `href="#"` (post titles, author links, logo, footer stats like “Collaboration”, “Contact”, “Error”, “404”). Clicking scrolls to top or does nothing. For screen readers and keyboard users, these are still links and can be confusing.

**Fix:** For non-navigational elements use `<span>` or `<button type="button">`, or add `aria-hidden="true"` and `tabindex="-1"` and keep `href="#"` only where necessary; ensure “Return to Top” is the only prominent `#` that intentionally scrolls.

### 2.5 Contact page footer “stats”

**Location:** `contact.html` footer `ul.stats`: “Collaboration” and “Contact” with `href="#"`.

**Problem:** They look like links but go nowhere and add no information.

**Fix:** Remove this block or replace with real links/actions (e.g. contact form, mailto, or remove for clarity).

### 2.6 user-scalable=no in viewport

**Location:** All HTML files: `content="width=device-width, initial-scale=1, user-scalable=no"`.

**Problem:** Disabling zoom harms accessibility (WCAG) and is discouraged for most sites.

**Fix:** Remove `user-scalable=no` so users can zoom. Use `content="width=device-width, initial-scale=1"`.

---

## 3. Code Quality & Maintainability

### 3.1 Duplication across HTML pages

**Problem:** Header, menu, sidebar (intro, mini-posts, posts list, blurb, footer), and script tags are copy-pasted across 6 HTML files. Any change (e.g. nav item, link, script) must be done in multiple places, which is error-prone.

**Fix:** Introduce a simple static build step (e.g. a small Node or Python script, or Jekyll/GitHub Pages) that uses includes/layouts so header, nav, sidebar, and scripts live in one place. Alternatively, keep static HTML but add a checklist in README for “change in all pages” when updating nav/footer.

### 3.2 publications.js — Global state and cache-busting

**Problem:** `loadPublications()` uses `fetch('data.json?v=' + Date.now())`, so every load bypasses cache. That increases latency and server load with no benefit for static JSON.

**Fix:** Use `data.json` without a query string so the browser can cache. If you need updates, rely on cache headers or a versioned path (e.g. `data.20260316.json`).

### 3.3 publications.js — No escaping (XSS)

**Problem:** `displayPublications()` builds HTML with template literals and assigns to `innerHTML` using `pub.title`, `pub.authors`, `pub.venue`, `pub.snippet` without escaping. If the JSON were ever edited or sourced from elsewhere and contained `<script>` or `onerror=`, it could execute in the page.

**Fix:** Use a small escape function for text content and use it for every dynamic string:

```javascript
function escapeHtml(str) {
    if (str == null) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
```

Use it for title, venue, snippet, and each author when building the HTML. For arrays (e.g. authors), `pub.authors.map(escapeHtml).join(', ')` after ensuring `pub.authors` is an array.

### 3.4 main.css — Conflicting footer rules

**Location:** `assets/css/main.css` (e.g. `.footer-research-block`, `article > footer`, `article.post > footer`).

**Problem:** Multiple `!important` rules and repeated selectors (e.g. `.footer-research-block` defined several times) suggest overrides fighting the template. Hard to maintain and reason about.

**Fix:** Consolidate footer and research-block styles into one section, use specificity instead of `!important` where possible, and remove duplicate selectors.

### 3.5 Naming and structure

**Problem:** `_data/publications_cleaned.json` and `_data/publications.json` exist but the site uses root `data.json`. Scripts in `scripts/` (e.g. `clean_publications.py`) suggest a pipeline; the relationship is not documented.

**Fix:** In README, briefly document: source of publications data, how `data.json` is generated, and that the live site reads only `data.json`.

---

## 4. Consistency

### 4.1 Sidebar content per page

**Problem:** Mini-posts and “Posts list” differ by page (different images, order, links). That’s acceptable for variety but can feel inconsistent (e.g. “Professional Background” vs “Publications & Impact” ordering and targets).

**Recommendation:** Either standardize one canonical sidebar (same items and order, only “current” page highlighted) or document that sidebars are page-specific by design.

### 4.2 Image dimensions and loading

**Problem:** Most images have explicit `width`, `height`, and `loading="lazy"`. 404 and a few others omit dimensions or loading. Pic08 uses 51×51.

**Fix:** Use consistent dimensions for the same “type” of image (e.g. all sidebar thumbs same size), and add `loading="lazy"` and dimensions to any remaining images so layout is stable and lazy-loading is consistent.

### 4.3 LinkedIn URL

**Problem:** README says `mariano-phielipp-941624`; HTML uses `mariano-phielipp/`. Both may resolve, but the canonical URL should be one.

**Fix:** Pick one URL and use it in README and all HTML (and any configs). Prefer the full vanity path if it’s the canonical profile.

---

## 5. Performance & Technical Debt

### 5.1 Font loading

**Problem:** `main.css` imports Google Fonts (Source Sans Pro, Raleway) without `display=swap` or preconnect. Can cause FOIT and layout shift.

**Fix:** Add `&display=swap` to the Google Fonts URL and consider `<link rel="preconnect" href="https://fonts.googleapis.com">` (and fonts.gstatic.com) in the HTML head.

### 5.2 Scripts loading

**Problem:** jQuery, browser.min, breakpoints, util, main (and on publications, publications.js) are all render-blocking. No `defer` or `async`.

**Fix:** Add `defer` to all script tags so parsing isn’t blocked. Ensure inline or DOMContentLoaded logic still runs after scripts load (defer preserves order).

### 5.3 main.css size

**Problem:** main.css is large (~2500+ lines) with repeated breakpoint blocks (e.g. row/column grid repeated at xlarge, large, medium, small, xsmall). Template-original, but heavy.

**Fix:** Lower priority for a static site. If you optimize later, consider purging unused rules or splitting “above-the-fold” vs “rest” and loading the rest lazily. Not critical for current scale.

---

## 6. Accessibility & Standards

### 6.1 Missing `lang` on `<html>`

**Problem:** No `lang` attribute on any page (e.g. `<html lang="en">`). Bad for screen readers and SEO.

**Fix:** Add `lang="en"` (or the correct language) to `<html>` on every page.

### 6.2 “Return to Top” focus and semantics

**Problem:** The button is an `<a href="#">`. For keyboard/screen reader users, it should be clear it’s a “scroll to top” action.

**Fix:** Use `<a href="#top" id="return-to-top">` and add `<span id="top"></span>` or use `id="wrapper"` at the top as the target; or use `<button type="button">` and scroll via JS, with `aria-label="Return to top"`.

### 6.3 Menu trigger

**Problem:** The hamburger is `<a class="fa-bars" href="#menu">`. If #menu is off-screen or hidden, focus and semantics may be unclear.

**Fix:** Ensure the menu has `id="menu"` and consider `aria-expanded` and `aria-controls="menu"` on the trigger so assistive tech knows the relationship. The existing panel JS may already handle visibility; verify with a quick test.

---

## 7. Implemented Fixes (Refactor Round)

- **Avatar/face images:** Removed inline `width="389" height="389"` from all author and logo avatar images so CSS controls size. Template uses `.author img { width: 4em; border-radius: 100% }` for circles and `#intro .logo` + `:before` SVG for the hexagonal sidebar logo. Added `height: 4em; object-fit: cover` for author avatars and `height: auto; object-fit: cover` for the logo image so they are no longer elongated.
- **Footer CSS:** Consolidated duplicate `.footer-research-block` and article footer overrides into a single block in `main.css` and removed `!important` where possible.
- **Jekyll refactor:** Not applied. The site remains static HTML so it works without a build step. A future move to Jekyll (or another SSG) with `_includes` for header, menu, sidebar, and footer would reduce duplication; see "Larger refactors" below.

---

## 8. Prioritized Fix List

### High priority (do first)

1. **util.js:** Fix panel early return to use `$(this)` instead of `$this`.
2. **publications.js:** Escape all dynamic content before `innerHTML` and add null/array checks for `pub.authors` (and other fields) to avoid runtime errors.
3. **All HTML:** Add `lang="en"` to `<html>` and remove `user-scalable=no` from the viewport meta tag.
4. **index.html:** Align “January 2026” text with the visible date (or vice versa) and add the return-to-top block so behavior matches other pages.

### Quick wins

5. Add breadcrumb to index (e.g. “Home” only).
6. Fix pic08 dimensions (use 351×176 or a dedicated small-thumb class).
7. Remove cache-busting from `data.json` fetch (`?v=Date.now()`).
8. Add `defer` to script tags.
9. Add `&display=swap` and optional preconnect for Google Fonts.
10. Unify LinkedIn URL in README and HTML.

### Larger refactors (next)

11. Introduce a build step or SSG (e.g. Jekyll) with includes so header, nav, sidebar, and scripts are not duplicated.
12. Consolidate main.css footer/research-block rules and reduce `!important`.
13. Document the publications pipeline (scripts, _data, data.json) in README.
14. Replace decorative `href="#"` with semantic elements or proper ARIA where appropriate.

---

## Summary Table

| Category        | Count | Severity |
|----------------|-------|----------|
| Bugs           | 3     | High (1), Medium (2) |
| UX/UI          | 6     | Medium   |
| Code quality   | 5     | Medium   |
| Consistency    | 3     | Low      |
| Performance    | 3     | Low      |
| A11y/standards| 3     | Medium   |

Implementing the high-priority and quick-win items will materially improve correctness, security, accessibility, and consistency without large structural changes. The refactors are recommended when you are ready to reduce duplication and streamline maintenance.
