# Feature 004: Fix Auth Serving (alembic.ini + static frontend via Flask)

**Branch**: `004-fix-auth-serving` | **Base**: `develop`
**Type**: Bugfix of 003-auth | **Constitution**: v1.2.0

## Problem

1. The `app` container crashes on boot: Flask-Migrate expects
   `backend/migrations/alembic.ini`, which was never created (the hand-written
   initial migration shipped only the root `backend/alembic.ini`). Result:
   migrations and seed never run, `faculties` stays empty, `/api/auth/catalog`
   is unreachable, and the faculty/program selects render empty.
2. When the frontend is opened with any static server other than the API
   origin (Five Server, Live Server), `js/auth.js` resolves `API=''` and calls
   its own origin instead of `http://localhost:5000`.
3. The team decided Flask must serve the frontend directly so development
   needs a single origin (`http://localhost:5000`) — no external static server.

## User Stories

### US1: Container boots end-to-end
Adding `migrations/alembic.ini` makes `flask db upgrade && flask seed-db &&
gunicorn` succeed. Logs show migration applied + "Seed completo" + gunicorn
listening.

### US2: Frontend served by Flask
`GET /` returns `frontend/index.html`; `GET /login.html`, `/register.html`,
`css/*`, `js/*` return static files. Clean extension-less URLs resolve to
their `.html` file (`/login`, `/register`, `/docs`); all `/api/*` routes keep
precedence.

### US2.1: Manual testing tools (dev-only)
- `backend/api.http` provides ready-to-send requests for the VS Code REST
  Client extension, including automatic token capture from the login response.
- `frontend/docs.html` + `frontend/openapi.yaml` expose interactive Swagger UI
  at `/docs` (CDN-loaded, dev documentation only — not part of the product
  runtime).

### US3: Correct API base resolution
`auth.js` uses same-origin requests when served from port 5000, and falls back
to `http://localhost:5000` for any other origin (CORS already enabled).

## Acceptance Criteria

- [ ] `docker compose up -d --build app` → healthy, no restart loop
- [ ] `curl localhost:5000/api/auth/catalog` lists seeded faculties+programs
- [ ] Full flow via curl works: register → login → me (Bearer)
- [ ] `curl localhost:5000/login.html` returns 200 HTML
- [ ] Clean URLs return 200: `/login`, `/register`, `/docs`
- [ ] `/openapi.yaml` served; Swagger UI renders it at `/docs`
- [ ] pytest suite remains 14/14 green

## Out of Scope

Admin approval endpoints, password recovery, refresh tokens.
