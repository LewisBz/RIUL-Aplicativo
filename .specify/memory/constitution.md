<!--
=== SYNC IMPACT REPORT ===
Version change: 2.0.0 -> 3.0.0
Modified principles:
  - IV. PostgreSQL Single Source of Truth -> IV. MySQL Single Source of Truth
    Engine is MySQL 8.4 with PyMySQL (mysql+pymysql). PostgreSQL/psycopg are
    forbidden. Alembic migrations remain mandatory (no db.create_all in
    production). Docker Compose pins mysql:8.4.
  - V. Reproducible Docker Environment: PostgreSQL service replaced by MySQL.
  - Fixed Technology Stack: Database/Driver rows updated; forbidden list no
    longer bans MySQL/PyMySQL and instead bans PostgreSQL/psycopg.
Added sections: none
Removed sections: none
Follow-up TODOs: none
=== END SYNC IMPACT REPORT ===

=== SYNC IMPACT REPORT (2.0.0) ===
Version change: 1.3.0 -> 2.0.0
Modified principles:
  - I. Modular Monolith -> I. Flask Layered MVC
    Domain packages under app/modules/<domain>/ are forbidden. The Flask app
    MUST follow the course layout (controllers, models, repositories, routes,
    schemas, services, static, templates, utils) with a factory in app/__init__.py.
  - II. API-First Backend: Marshmallow schemas are the JSON View; raw ORM
    objects MUST NOT be returned from controllers.
  - III. Pure JavaScript Frontend: HTML/CSS/JS live in app/templates and
    app/static (Flask folders), still zero-build vanilla JS + fetch.
  - VI. Tested Modules -> VI. Tested Layers (services, schemas, routes).
Added sections:
  - Fixed Technology Stack rows: Marshmallow, Flask-SQLAlchemy, WSGI (Gunicorn)
Removed sections:
  - Principle I modular-monolith rules (bounded domain modules, cross-module
    public service interfaces, new domains as new modules)
Follow-up TODOs: none
=== END SYNC IMPACT REPORT ===

=== SYNC IMPACT REPORT (1.3.0) ===
Version change: 1.2.0 -> 1.3.0
Modified principles:
  - VIII Git Workflow: expanded items 1 and 6.
Added sections: none
Removed sections: none
Follow-up TODOs: none
=== END SYNC IMPACT REPORT ===

=== SYNC IMPACT REPORT (1.2.0) ===
Version change: 1.1.0 -> 1.2.0 (MINOR: new principle VIII added)
Added: Principle VIII — Git Workflow for the three-person team
Unchanged: Principles I-VII and fixed stack table.
Follow-ups: set main as protected branch on GitHub enforcing the
  no-direct-push rule.
=== END SYNC IMPACT REPORT ===

=== SYNC IMPACT REPORT (1.1.0) ===
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

### I. Flask Layered MVC

The system is a single deployable Flask application organized by MVC layers, not
by domain modules. The application package MUST match the course Flask layout
(reference: `flask-Inventory`): factory in `app/__init__.py`, `run.py` as the
WSGI/CLI entry, plus these packages/folders inside `app/`:

- `models/` — SQLAlchemy entities (Model).
- `schemas/` — Marshmallow schemas: request validation and JSON serialization
  (View for the REST API).
- `controllers/` — HTTP orchestration: parse input, call services, return
  schema-dumped responses (Controller).
- `routes/` — Flask blueprints and URL registration only; no business logic.
- `services/` — use-case / business rules.
- `repositories/` — persistence access used by services; the only layer that
  queries the ORM session for domain reads/writes.
- `templates/` and `static/` — Flask HTML and static assets.
- `utils/` — cross-cutting helpers with no domain policy.
- `config.py` and `extensions.py` — configuration objects and extension
  instances (`db`, `jwt`, `migrate`, Marshmallow, bcrypt).

Dependency direction is mandatory and one-way: `routes` → `controllers` →
`services` → `repositories` → `models`. Schemas are used by controllers (and
tests) and MUST NOT contain business rules or database queries.

- Domain packages such as `app/modules/<domain>/` are forbidden. Features add
  files inside the existing layers (new model, schema, repository, service,
  controller, route), not a new bounded module.
- Controllers MUST NOT import repositories or issue queries. Services MUST NOT
  return Flask responses. Routes MUST NOT instantiate schemas for business
  decisions.
- The Flask project that hosts this package lives under `backend/` so Spec Kit
  artifacts (`specs/`, `.specify/`, `mockup/`) stay at the repository root.
  Rationale: the course requires Flask's layered MVC skeleton; RIUL keeps that
  skeleton and drops the modular monolith.

### II. API-First Backend

The backend exposes a REST JSON API that the frontend consumes exclusively.

- For every feature, the API contract (routes, methods, payloads, status codes,
  errors) is defined and reviewed before implementation begins.
- That contract is implemented as Marshmallow schemas. Controllers MUST load
  inbound JSON through schemas and dump outbound bodies through schemas. Returning
  raw SQLAlchemy models, `dict`s built ad hoc from model attributes, or
  `jsonify(model)` is forbidden.
- Pages load data via `fetch()` against these endpoints; server-side rendering of
  business data inside Jinja templates is not used. Templates may exist only as
  document shells that load static JS/CSS.
- Contract changes require updating the feature specification first. Rationale:
  frontend and backend work happens in parallel; Marshmallow is the executable
  contract.

### III. Pure JavaScript Frontend (Zero Build)

The frontend is plain HTML, CSS, and native browser ES modules, served by Flask
from `app/templates` and `app/static`.

- No frameworks (React, Vue, Angular, Svelte), no jQuery, no bundlers, no
  transpilers, no lint/build toolchain, no npm build step. Files are served
  exactly as authored.
- UI MUST faithfully implement the Stitch design-system tokens defined in
  `mockup/stitch_riul_design_system_strategy/`: crimson primary (`#7b001f`), amber
  accent reserved for gamification only, Montserrat headlines + Inter body, 4px
  spacing rhythm, max container width 1280px, radii 8px (controls) / 16px (large
  containers), minimum 4.5:1 text contrast.
- Design tokens live in CSS custom properties; components reuse them instead of
  hard-coded values. A separate top-level `frontend/` tree MUST NOT be the
  serving source of truth once the Flask layout is in place. Rationale: zero-build
  keeps onboarding trivial and matches Flask's `static`/`templates` folders.

### IV. MySQL Single Source of Truth

MySQL is the only database engine for all persistent data.

- Data access goes through SQLAlchemy (via Flask-SQLAlchemy) plus Alembic
  migrations (via Flask-Migrate); schema changes always ship as versioned
  migrations, never manual edits or `create_all` in production paths.
- MySQL-specific features are allowed; compatibility with other engines is NOT a
  goal. The driver is PyMySQL (`mysql+pymysql://`). PostgreSQL and psycopg MUST
  NOT return. This matches the course inventory sample's engine while keeping
  Alembic instead of `create_all`.
- Every entity has explicit constraints (PKs, FKs, unique, check) at the database
  level, not only at the application level. Rationale: research records are
  academic evidence; integrity must be enforced where it cannot be bypassed.

### V. Reproducible Docker Environment

Every part of the system runs through Docker Compose.

- Compose defines at minimum the Flask app service (Gunicorn) and a MySQL
  service; versions are pinned (Python 3.12, MySQL 8.4).
- There is no supported "local-only" setup path; instructions that skip Compose
  are a violation. Rationale: students on different machines MUST get identical
  behavior; "works on my machine" bugs are unacceptable in a graded project.

### VI. Tested Layers (Flexible TDD)

Every backend layer that carries behavior ships with automated tests using pytest.

- Tests are required before merge, but strict test-first ordering is encouraged,
  not gated: writing tests after or alongside implementation is acceptable if
  coverage exists for services, Marshmallow schemas, and critical routes.
- Tests MUST cover each service's public interface, schema validation success and
  failure cases for the feature contract, and at least one end-to-end request
  through the registered blueprint routes.
- The full suite MUST pass before any merge; failing tests block integration.
  Rationale: flexible TDD matches a student team's reality while keeping
  regressions out of main.

### VII. Security and Role-Based Access

Authentication is stateless and enforced server-side on every request.

- Stateless JWT authentication via Flask-JWT-Extended: short-lived access tokens
  issued at login through the REST API and sent by the frontend as
  `Authorization: Bearer` headers. Roles (`researcher`, `administrator`) are
  encoded in token claims AND re-checked server-side on every request;
  authorization checks live in one place (decorators/guards on controllers or
  routes), not scattered in services or templates.
- Token storage: the frontend keeps tokens in localStorage and sends Bearer
  headers. This XSS tradeoff is explicitly accepted for this project; mitigations
  stay server-side (strict Marshmallow validation, no inline user HTML).
- Signing keys and secrets come from environment variables (never committed).
- All input is validated server-side with Marshmallow regardless of client-side
  validation.
- Passwords are hashed with bcrypt via Flask-Bcrypt; no plaintext, Werkzeug
  default hashes as the project standard, or fast hashes ever. Rationale: the
  platform stores personal academic data of real people.

## Fixed Technology Stack

The stack below is frozen for v1. Changes require a constitution amendment.

| Layer            | Technology                                   |
| ---------------- | -------------------------------------------- |
| Language         | Python 3.12 (pinned)                         |
| Web              | Flask 3.x                                    |
| App layout       | Flask layered MVC (`app/` course skeleton)   |
| ORM              | Flask-SQLAlchemy (SQLAlchemy 2.x)            |
| Serialization    | Marshmallow                                  |
| Migrations       | Alembic via Flask-Migrate                    |
| Database         | MySQL 8.4                                    |
| DB Driver        | PyMySQL                                      |
| Auth tokens      | Flask-JWT-Extended                           |
| Password hashing | Flask-Bcrypt (bcrypt)                        |
| WSGI             | Gunicorn (Docker app service)                |
| Runtime          | Docker Compose                               |
| Frontend         | Vanilla JS (ES2022 modules), HTML5, CSS3     |
| Styling          | CSS custom properties (Stitch design tokens) |
| Testing          | pytest                                       |

Forbidden by this constitution: modular monolith domain packages
(`app/modules/...`), ORMs other than SQLAlchemy, returning ORM objects as JSON,
client frameworks or bundlers, PostgreSQL/psycopg, alternative databases, unpinned
runtimes, session-based authentication, plaintext or fast-hash password storage.

## Principle VIII: Git Workflow (Team of Three — Luis, Héctor, Javier)

The repository follows a fixed branch model so the three-person team can
collaborate without stepping on each other.

1. **Branches**: `main` is production-ready and protected; `develop` is the
   team integration branch; every Spec Kit feature gets one branch named after
   its spec folder (`NNN-feature-name`), created ALWAYS from `develop`. Every
   change tied to a spec — feature, bugfix, hotfix, or adjustment — MUST happen
   on its own branch (`NNN-feature-name`, `NNN-fix-*`) created from `develop`
   BEFORE any file is modified. Working directly on `develop` or `main` is
   forbidden; the only exception is governance-only constitution amendments
   (item 5).
2. **Integration**: features enter `develop` exclusively through GitHub Pull
   Requests. Every PR requires approval from at least 1 of the other 2 team
   members before merging.
3. **Releases**: `develop` reaches `main` via PR only when a feature is stable
   and its tests pass; release commits are tagged `vX.Y`.
4. **Forbidden**: direct pushes to `main`; deleting another member's branches;
   commits without a descriptive message referencing the feature/spec number.
5. Constitution amendments may be committed directly on `develop` as small
   governance-only changes; they follow the amendment process above.
6. **AI agent boundaries**: AI agents may autonomously create branches for
   features, bugfixes, hotfixes, and similar work following the established
   naming style (e.g., `NNN-feature-name`, `NNN-fix-*`). Every other git
   operation — `commit`, `push`, `pull`, `merge`, `rebase`, PR merges, and any
   history-modifying or destructive operation (`reset --hard`, force push,
   branch deletion) — is executed exclusively by human team members. When work
   is complete, AI agents stop with changes in place and hand off the suggested
   commands for a team member to review and run. Before starting any work, an AI
   agent MUST verify it is on the correct spec branch; if it does not exist, the
   agent creates it first from `develop`. If a session starts on `develop`, the
   agent stops and asks before touching files; leaving spec-related work on
   `develop` is forbidden.

## Development Workflow

Every feature follows the Spec Kit pipeline; no feature starts with code.

- Pipeline: `/speckit-specify` -> `/speckit-clarify` (if ambiguity) ->
  `/speckit-plan` -> `/speckit-tasks` -> `/speckit-analyze` ->
  `/speckit-implement`.
- OpenCode keeps the dotted form (`/speckit.specify`, …); Cursor uses hyphens.
- One git branch per feature, named after its spec folder; commits reference the
  feature/spec being implemented.
- The constitution is checked during `/speckit-analyze`; violations found there
  block `/speckit-implement`.
- Mockups in `mockup/` are the visual source of truth referenced by
  specifications.

## Governance

This constitution supersedes all other practices, conventions, and ad-hoc
decisions.

- Amendments: proposed in a spec folder, documented in this file with a semantic
  version bump (MAJOR: principle removal/redefinition; MINOR: new principle or
  material expansion; PATCH: wording), plus updated amendment date and Sync
  Impact Report entry.
- Compliance: every plan review and pull request verifies adherence; complexity
  or exceptions MUST be justified in writing within the relevant spec or PR.
- Any conflict between documentation, habit, or convenience and this document is
  resolved in favor of this document.
- Existing code and specs written under the modular monolith (v1.x) are
  superseded by this document. Migrating `app/modules/` into layered MVC is a
  spec-driven change, not a silent refactor on `develop`.

**Version**: 3.0.0 | **Ratified**: 2026-08-22 | **Last Amended**: 2026-09-20

## Sync Impact Report

- Version change: 2.0.0 → 3.0.0 (MAJOR: Principle IV redefined; PostgreSQL
  removed)
- Replaced: IV. PostgreSQL → IV. MySQL 8.4 + PyMySQL
- Modified: V Docker (mysql:8.4), Fixed Technology Stack, forbidden list
- Unchanged in intent: I Flask layered MVC, II API-first + Marshmallow, III
  vanilla frontend in templates/static, VI tested layers, VII JWT/bcrypt, VIII Git
- Explicit non-adoptions from the inventory sample: Werkzeug as the password
  standard, `db.create_all` instead of Alembic
- Follow-ups: none
