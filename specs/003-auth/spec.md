# Feature 003: User Authentication Module

**Branch**: `003-auth` | **Base**: `develop`
**Constitution**: v1.1.0 | **Priority**: P0 (blocks all authenticated modules)

## Purpose

First backend module of the modular monolith. Establishes the Flask application
skeleton, the PostgreSQL connection via Docker Compose, and the complete
authentication flow defined in mockups `riul_iniciar_sesión` and
`riul_registro_de_cuenta`: institutional registration (immediate access),
external account request (pending admin approval), and JWT-based login.

## API Contract (defined before implementation — Principle II)

| Method | Endpoint | Body | Success | Errors |
|---|---|---|---|---|
| POST | `/api/auth/register` | `email`, `password`, `full_name`, `faculty_id?`, `program_id?` | `201` `{access_token, user}` status=`active` | `409` duplicate email · `400` validation |
| POST | `/api/auth/request-account` | `email`, `full_name`, `motivation`, `faculty_id`, `program_id` | `202` `{message}` status=`pending` | `409` duplicate email · `400` validation |
| POST | `/api/auth/login` | `email`, `password` | `200` `{access_token, user}` | `401` bad credentials · `403` account pending/rejected |
| GET | `/api/auth/me` | Bearer token | `200` `{user}` from claims | `401` missing/expired/invalid token |

## User Stories

### US1: Institutional registration (direct)
**As a** university member **I want** to register with my institutional email
and **get immediate access**, matching the "Registro (Institucional)" tab.

- Email MUST end with configured institutional domain (`INSTITUTIONAL_EMAIL_DOMAIN`,
  default `unilibre.edu.co`)
- Password minimum 8 characters, validated server-side
- Account is created with role `researcher`, status `active`
- Response returns a valid JWT usable immediately

### US2: External account request (approval queue)
**As an** external researcher **I want** to request an account with my personal
email and motivation, matching the "Solicitud (No Institucional)" tab.

- Accepts any email that is NOT in the institutional domain
- Creates account with status `pending`; NO token is issued
- Login attempts return `403` until an administrator approves (admin portal,
  future feature)

### US3: Login with stateless JWT
**As a** registered active user **I want** to log in and receive a bearer token.

- Password verified with bcrypt (`check_password_hash`)
- Access token expires in 12h; custom claims include `role` and `status`
- Pending accounts receive `403` with message "Solicitud pendiente de aprobación"
  (mockup banner); rejected accounts receive `403` with rejection message

### US4: Protected identity endpoint
**As a** logged-in user **I want** `/api/auth/me` to return my identity so the
frontend can validate stored tokens.

- Requires `Authorization: Bearer <token>` via Flask-JWT-Extended
- Role claim re-validated server-side on protected routes (Principle VII)

## Data Model

- `users`: id PK, full_name, email UNIQUE NOT NULL, password_hash NOT NULL,
  role ENUM(`researcher`,`administrator`) default `researcher`,
  status ENUM(`active`,`pending`,`rejected`) default `active`,
  faculty_id FK nullable, program_id FK nullable, created_at
- `faculties`: id PK, name UNIQUE
- `programs`: id PK, name, faculty_id FK → faculties (1—N)

Seed (from mockup): Ingeniería → Ingeniería de Sistemas, Ingeniería Industrial;
Ciencias Básicas → (placeholder program).

## Non-Functional Requirements

- NFR1: Everything runs via `docker compose up` (app + postgres:16-alpine);
  no local Python required (Principle V)
- NFR2: Secrets only via env vars (`DATABASE_URL`, `JWT_SECRET_KEY`);
  `.env.example` committed, `.env` gitignored
- NFR3: Tests run against real PostgreSQL (database `riul_test` in same
  container, schema dropped/created per session); require `docker compose up -d db`
- NFR4: Frontend pages are standalone static HTML using only
  `css/design-system.css` + vanilla JS `fetch()`; token persisted in
  `localStorage` key `riul_token` (Principle III & VII tradeoff)

## Edge Cases

- Duplicate email across both registration paths → `409`
- Institutional email submitted via external-request form → `400` guiding user
  to institutional registration
- Malformed/expired token on `/me` → `401` (never 500)

## Out of Scope

Admin approval endpoints (admin portal feature), password recovery email flow,
refresh tokens, OAuth/social login.
