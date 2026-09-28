# Feature 006: Dashboard y Perfil del Investigador

**Branch:** `006-dashboard-perfil` (from `develop`)
**Type:** Frontend-only feature (mockup-faithful UI + demo data)
**Depends on:** 003-auth (`/api/auth/me`, `/api/auth/catalog`), 004 (static serving, clean URLs), 005 (session navbar)
**Backend changes:** NONE

## Problem

The researcher has no home inside the platform. The two most important
authenticated screens — the researcher dashboard and the profile / research
CV — do not exist yet. Mockups `riul_dashboard_del_investigador` and
`riul_perfil_del_investigador` define their anatomy.

## Scope decision

Identity data is REAL (from `/api/auth/me`; faculty/program names resolved
client-side by mapping `/catalog`). Everything not yet modeled in the backend
(semilleros, projects, publications, products, achievements, notifications,
XP/level/stars/badges) renders from a clearly-marked DEMO module
(`js/demo-data.js`) that future backend features will replace as data source.

## User Stories

### US1 — Session guard

Visiting `/dashboard` or `/profile` without a valid session redirects to
`/login`. With an expired/garbage token: token cleared, redirect to `/login`
(no crash, no loop).

### US2 — Shared authenticated layout

Both pages reuse the session navbar (avatar + name + role + dropdown with
logout) from 005 via `initSessionUI()`, plus a new left sidebar rendered by
`js/sidebar.js` reading `body[data-nav-active]`. Sidebar hidden on mobile.
Active item styled literally per mockup (`bg #9e1b32`, text `#ffb0b3`).

### US3 — Dashboard

- Greeting "Hola, {full_name|email}" (real).
- Bento grid faithful to mockup:
  - Profile snippet (col-4): real avatar initial/name/role; demo level +
    star rating (amber `#ffb800`); "Ver Todo" → `/profile`.
  - Projects summary (col-8): demo rows with status + arrow buttons;
    footer actions Ver Todos / Crear (placeholders).
  - Publications list (col-6) demo; "Registrar" placeholder.
  - My semillero card (amber left border + decorative corner) demo.
  - Recent notifications card demo.

### US4 — Profile page

- Banner: square avatar with real initial, real full_name/email, role label;
  disabled "Editar Perfil" button.
- Left column (1/3): Información personal REAL (email, faculty, program
  resolved via `/catalog`); Mis semilleros & Proyectos demo lists.
- Right column (2/3):
  - Gamification hero card (amber left border + soft amber shadow):
    "Nivel {n}" + "{xp} / {next} XP" progress bar (74%), Estrellas obtenidas,
    Últimas insignias horizontal scroll row.
  - Publicaciones table (demo).
  - Productos table with status badges (Aprobado teal / En revisión gray)
    + Logros timeline (filled nodes done, hollow pending).

### US5 — Demo data isolation

All non-identity content comes exclusively from `js/demo-data.js` constants;
no hardcoded strings scattered in pages for swappable content.

### US6 — Regression safety

Existing pages unaffected: homepage guest/auth views, login/register flows,
docs page. pytest suite stays green (no backend change).

## Acceptance

- `/dashboard` and `/profile` served clean (200) by Flask catch-all.
- Guard works both directions; logout from either page returns to guest state.
- Layout responsive: bento collapses to single column on mobile; sidebar hidden.
