<!--
=== SYNC IMPACT REPORT ===
Version change: 1.0.0 -> 1.1.0
Modified principles:
  - VII Security and Role-Based Access: session-based auth replaced by stateless
    JWT via Flask-JWT-Extended; bcrypt fixed as mandatory hash via Flask-Bcrypt;
    token storage policy added (Authorization Bearer + localStorage, accepted XSS
    tradeoff documented).
Added sections:
  - Fixed Technology Stack rows: "Auth tokens" and "Password hashing"
Removed sections: none
Follow-up TODOs: none
=== END SYNC IMPACT REPORT ===

=== SYNC IMPACT REPORT (1.0.0) ===
Version change: (none) -> 1.0.0
Modified principles: N/A (initial ratification)
Added sections:
  - Core Principles I-VII
  - Fixed Technology Stack
  - Development Workflow
  - Governance
Removed sections: none
Follow-up TODOs: none
=== END SYNC IMPACT REPORT ===
-->

# RIUL-Aplicativo Constitution

A spec-driven constitution for RIUL ("Red de Investigación Universidad Libre"), a
research-network social platform for university researchers, faculty, and students.

## Core Principles

### I. Modular Monolith

The system is a single deployable Flask application composed of strictly bounded domain
modules (e.g., auth, researcher profiles, seedbeds/semilleros, posts & feed, events &
calls, projects & outputs, gamification/ranking, admin dashboards & analytics, support).

- Each module owns its blueprints, SQLAlchemy models, services, and templates/assets.
- Cross-module access MUST go through each module's explicit public service interface;
  importing another module's internal models or helpers is forbidden.
- Shared infrastructure (database session, auth primitives, config) lives in a common
  core package; domain logic never leaks into it.
- New domains are added as new modules; existing modules are never merged into a
  tangle. Rationale: module boundaries are this project's critical architectural
  decision; they enable parallel student-team work without merge chaos.

### II. API-First Backend

The backend exposes a REST JSON API that the frontend consumes exclusively.

- For every feature, the API contract (routes, methods, payloads, status codes,
  errors) is defined and reviewed before implementation begins.
- Pages load data via `fetch()` against these endpoints; server-side rendering of
  business data inside templates is not used.
- Contract changes require updating the feature specification first. Rationale:
  frontend and backend work happens in parallel across team members; the contract is
  their shared agreement.

### III. Pure JavaScript Frontend (Zero Build)

The frontend is plain HTML, CSS, and native browser ES modules served as static files.

- No frameworks (React, Vue, Angular, Svelte), no jQuery, no bundlers, no transpilers,
  no lint/build toolchain, no npm build step. Files are served exactly as authored.
- UI MUST faithfully implement the Stitch design-system tokens defined in
  `mockup/stitch_riul_design_system_strategy/`: crimson primary (`#7b001f`), amber
  accent reserved for gamification only, Montserrat headlines + Inter body, 4px
  spacing rhythm, max container width 1280px, radii 8px (controls) / 16px (large
  containers), minimum 4.5:1 text contrast.
- Design tokens live in CSS custom properties; components reuse them instead of
  hard-coded values. Rationale: zero-build keeps onboarding trivial for a student
  team and makes every mockup directly comparable to production.

### IV. PostgreSQL Single Source of Truth

PostgreSQL is the only database engine for all persistent data.

- Data access goes through SQLAlchemy ORM plus Alembic migrations (via Flask-Migrate);
  schema changes always ship as versioned migrations, never manual edits.
- PostgreSQL-specific features are allowed; compatibility with other engines is NOT a
  goal. The driver is psycopg. MySQL-era artifacts (e.g., PyMySQL) MUST NOT return.
- Every entity has explicit constraints (PKs, FKs, unique, check) at the database
  level, not only at the application level. Rationale: research records are academic
  evidence; integrity must be enforced where it cannot be bypassed.

### V. Reproducible Docker Environment

Every part of the system runs through Docker Compose.

- Compose defines at minimum the Flask app service and a PostgreSQL service; versions
  are pinned (Python 3.12, PostgreSQL 16+).
- There is no supported "local-only" setup path; instructions that skip Compose are a
  violation. Rationale: five students on five machines must get identical behavior;
  "works on my machine" bugs are unacceptable in a graded project.

### VI. Tested Modules (Flexible TDD)

Every backend module ships with automated tests using pytest.

- Tests are required before merge, but strict test-first ordering is encouraged, not
  gated: writing tests after or alongside implementation is acceptable if coverage
  exists for the module's service interfaces and critical paths.
- A module's tests MUST cover its public service interface and at least one
  end-to-end request through its blueprint routes.
- The full suite MUST pass before any merge; failing tests block integration.
  Rationale: flexible TDD matches a student team's reality while keeping regressions
  out of main.

### VII. Security and Role-Based Access

Authentication is stateless and enforced server-side on every request.

- Stateless JWT authentication via Flask-JWT-Extended: short-lived access tokens
  issued at login through the REST API and sent by the frontend as
  `Authorization: Bearer` headers. Roles (`researcher`, `administrator`) are encoded
  in token claims AND re-checked server-side on every request; authorization checks
  live in one place per module (decorators/guards), not scattered in views.
- Token storage: the frontend keeps tokens in localStorage and sends Bearer headers.
  This XSS tradeoff is explicitly accepted for this project; mitigations stay
  server-side (strict input validation, no inline user HTML).
- Signing keys and secrets come from environment variables (never committed).
- All input validated server-side regardless of client-side validation.
- Passwords are hashed with bcrypt via Flask-Bcrypt; no plaintext or fast hashes
  ever. Rationale: the platform stores personal academic data of real people.

## Fixed Technology Stack

The stack below is frozen for v1. Changes require a constitution amendment.

| Layer      | Technology                                        |
| ---------- | ------------------------------------------------- |
| Language   | Python 3.12 (pinned)                              |
| Web        | Flask 3.x                                         |
| ORM        | SQLAlchemy 2.x                                    |
| Migrations | Alembic via Flask-Migrate                         |
| Database   | PostgreSQL 16+                                    |
| DB Driver  | psycopg                                           |
| Auth tokens | Flask-JWT-Extended                               |
| Password hashing | Flask-Bcrypt (bcrypt)                       |
| Runtime    | Docker Compose                                    |
| Frontend   | Vanilla JS (ES2022 modules), HTML5, CSS3          |
| Styling    | CSS custom properties (Stitch design tokens)      |
| Testing    | pytest                                            |

Forbidden by this constitution: ORMs other than SQLAlchemy, client frameworks or
bundlers, alternative databases, unpinned runtimes, session-based authentication,
plaintext or fast-hash password storage.

## Principle VIII: Git Workflow (Team of Three — Luis, Héctor, Javier)

The repository follows a fixed branch model so the three-person team can
collaborate without stepping on each other.

1. **Branches**: `main` is production-ready and protected; `develop` is the
   team integration branch; every Spec Kit feature gets one branch named after
   its spec folder (`NNN-feature-name`), created ALWAYS from `develop`.
2. **Integration**: features enter `develop` exclusively through GitHub Pull
   Requests. Every PR requires approval from at least 1 of the other 2 team
   members before merging.
3. **Releases**: `develop` reaches `main` via PR only when a module is stable
   and its tests pass; release commits are tagged `vX.Y`.
4. **Forbidden**: direct pushes to `main`; deleting another member's branches;
   commits without a descriptive message referencing the feature/spec number.
5. Constitution amendments may be committed directly on `develop` as small
   governance-only changes; they follow the amendment process above.

## Development Workflow

Every feature follows the Spec Kit pipeline; no feature starts with code.

- Pipeline: `/speckit.specify` -> `/speckit.clarify` (if ambiguity) ->
  `/speckit.plan` -> `/speckit.tasks` -> `/speckit.analyze` -> `/speckit.implement`.
- One git branch per feature, named after its spec folder; commits reference the
  feature/spec being implemented.
- The constitution is checked during `/speckit.analyze`; violations found there block
  `/speckit.implement`.
- Mockups in `mockup/` are the visual source of truth referenced by specifications.

## Governance

This constitution supersedes all other practices, conventions, and ad-hoc decisions.

- Amendments: proposed in a spec folder, documented in this file with a semantic
  version bump (MAJOR: principle removal/redefinition; MINOR: new principle or
  material expansion; PATCH: wording), plus updated amendment date and Sync Impact
  Report entry.
- Compliance: every plan review and pull request verifies adherence; complexity or
  exceptions MUST be justified in writing within the relevant spec or PR.
- Any conflict between documentation, habit, or convenience and this document is
  resolved in favor of this document.

**Version**: 1.2.0 | **Ratified**: 2026-08-22 | **Last Amended**: 2026-08-22

## Sync Impact Report
- Version change: 1.1.0 → 1.2.0 (MINOR: new principle VIII added)
- Added: Principle VIII — Git Workflow for the three-person team
  (branch model feature → PR(1 reviewer) → develop; releases develop → main
  via tagged PR; direct pushes to main forbidden).
- Unchanged: Principles I–VII and fixed stack table.
- Follow-ups: team members must set `main` as protected branch on GitHub
  (Settings → Branches) enforcing the no-direct-push rule.
