# Feature 005: Session-Aware Navbar

**Branch:** `005-session-navbar` (from `develop`)
**Type:** Frontend-only feature
**Depends on:** 003-auth (backend `/api/auth/me`), 004-fix-auth-serving (static serving, clean URLs)
**Backend changes:** NONE

## Problem

After login/register, the user is redirected to the homepage but the navbar is
static: it always shows "Iniciar sesión" / "Registrarse" CTAs regardless of
session state. The logged-in user gets no visual confirmation of who they are.

## User Stories

### US1 — Guest sees public CTAs

As a visitor without a session, the homepage navbar shows the current
"Iniciar sesión" (outline) and "Registrarse" (primary) buttons exactly as
today.

**Acceptance**
- No `riul_token` in localStorage → guest view unchanged.
- Mobile menu panel keeps its "Iniciar sesión" entry.

### US2 — Authenticated user sees identity in navbar

As a logged-in user visiting any page with `js/session.js` loaded, the navbar
replaces the guest CTAs with an identity block:

- Circular avatar showing the first letter of my name.
- My full name (fallback: email) and role caption
  (`researcher → Investigador`, `administrator → Administrador`, external roles shown raw).
- Clicking it opens a dropdown with:
  - **Mi perfil** — placeholder, disabled with "Próximamente" tooltip.
  - **Cerrar sesión** — removes the token and returns to guest view.

**Acceptance**
- Register or login → redirect to homepage → identity block visible with correct data from `/api/auth/me`.
- Desktop AND mobile menu panel both reflect session state.
- Dropdown closes when clicking outside or pressing Escape.

### US3 — Invalid/expired token degrades gracefully

If `riul_token` exists but `/api/auth/me` answers 401/403 (expired, tampered),
or fetch fails (backend down):

- Token is removed from localStorage silently (on auth errors only).
- Navbar falls back to guest view.
- No console crashes; no redirect loops.

**Acceptance**
- Setting garbage into `riul_token` then reloading → guest view, token cleared, zero unhandled promise rejections.

### US4 — Logout restores guest state

Clicking "Cerrar sesión" (desktop dropdown or mobile panel) clears the token,
closes any open menus, and re-renders the navbar as guest immediately.

## Implementation Notes

- New shared module `frontend/js/session.js`: `getSessionUser()` + `logout()`.
  API base logic mirrors `auth.js` (`port !== '5000' → http://localhost:5000`).
- `index.html` marks guest actions with `data-auth="guest"` and adds a hidden
  block `data-auth="user"`; CSS toggles visibility via `.hidden`.
- CSS section 16: `.nav-user-btn`, `.nav-avatar` (36px circle,
  `--primary-fixed` bg, `--primary` text), `.nav-user-meta`, `.nav-dropdown`
  (absolute card, reuses design tokens).
- `main.js` becomes an ES module that initializes session rendering after DOM
  load (top-level await allowed in modules).
- "Mi perfil" stays disabled until the future researcher-profile feature.
