# Feature 006: Dashboard y Perfil del Investigador

**Branch:** `006-dashboard-perfil` (from `develop`)
**Type:** Frontend (mockup-faithful UI) con contenido real servido por la API
**Status:** Implementado y actualizado (la versión original usaba datos demo y no tocaba el backend)
**Depends on:** 003-auth (`/api/auth/me`, `/api/auth/catalog`), 004 (serving, clean URLs), 005 (session navbar)
**Backend:** `GET /api/dashboard`, `GET /api/profile`, `PATCH /api/profile`, `POST /api/profile/password` y `POST /api/publications` (agregados por las features posteriores de dominio; ver `backend/app/routes/profile.py`)

## Problem

The researcher has no home inside the platform. The two most important
authenticated screens — the researcher dashboard and the profile / research
CV — need to exist. Mockups `riul_dashboard_del_investigador` and
`riul_perfil_del_investigador` define their anatomy.

## Scope decision

La primera versión mostraba identidad real y contenido demo (`js/demo-data.js`).
Hoy todo el contenido es real: `dashboard.js` consume `/api/dashboard` y
`profile.js` consume `/api/profile`; la facultad y el programa llegan resueltos
por la API y `/api/auth/catalog` se usa solo para el formulario de edición. Ya no
existe el módulo demo. El layout compartido (navbar, sidebar, footer) lo renderiza
`js/layout.js` a partir de `body[data-nav-active]`; no existe `sidebar.js`.

## User Stories

### US1 — Session guard

Visiting `/dashboard` or `/profile` without a valid session redirects to
`/login`. With an expired/garbage token (401/403): token cleared, redirect to `/login`
(no crash, no loop). A 5xx or network failure does not clear the token.

### US2 — Shared authenticated layout

Both pages reuse the session navbar (avatar + name + role + dropdown with
logout) from 005 via `initSessionUI()`, plus the left sidebar rendered by
`js/layout.js` reading `body[data-nav-active]`. Sidebar hidden on mobile; the
mobile menu panel carries the same navigation. Active item styled per mockup
(`bg #9e1b32`, text `#ffb0b3`, through CSS in `design-system.css`).

### US3 — Dashboard

- Greeting with the real user name.
- Bento grid faithful to mockup, fed by `/api/dashboard`:
  - Profile snippet: avatar initial/name/role, level and stars (amber `#ffb800`);
    "Ver Todo" → `/profile`.
  - Projects summary with status and arrow buttons; footer actions.
  - Publications list; "Registrar" opens a form (`POST /api/publications`).
  - My semillero card (amber left border) with activities this month.
  - Recent notifications card with unread count.
- Skeleton placeholders while loading.

### US4 — Profile page

- Banner: avatar initial, full name, email, role label; **"Editar Perfil" enabled**
  (dialog → `PATCH /api/profile`; change password → `POST /api/profile/password`).
- Left column: personal information (email, faculty, program); real semilleros and projects.
- Right column:
  - Gamification hero card (amber left border + soft amber shadow): "Nivel {n}",
    XP progress bar, stars, latest badges.
  - Publications table.
  - Products table with status badges (Aprobado teal / En revisión gray) and the achievements timeline.

### US5 — Data source isolation

All content comes from the API through adapters (`js/adapters.js`); there are no
hardcoded swappable strings in pages. (Replaces the original "demo data isolation".)

### US6 — Regression safety

Existing pages unaffected: homepage guest/auth views, login/register flows,
docs page. The pytest suite stays green.

## Acceptance

- `/dashboard` and `/profile` served clean (200) by the Flask catch-all.
- Guard works both directions; logout from either page redirects to `/login`.
- Layout responsive: bento collapses to a single column on mobile; sidebar hidden.
- Editing the profile persists after reload.
