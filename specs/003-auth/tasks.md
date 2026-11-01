# Tasks: Módulo de autenticación

**Input**: `specs/003-auth/spec.md`, `plan.md`
**Estado**: [X] = encontrado en el repo; [ ] = pendiente o requiere verificación manual.

## Phase 1: Setup

- [X] T001 Fábrica de la app en `backend/app/__init__.py` y entrada `backend/run.py`
- [X] T002 [P] `backend/app/config.py` con `JWT_ACCESS_TOKEN_EXPIRES` de 12h e `INSTITUTIONAL_EMAIL_DOMAIN` (por defecto `unilibre.edu.co`)
- [X] T003 [P] `compose.yml` con servicio de app y MySQL, y `.env.example`

## Phase 2: Foundational

- [X] T004 Migración inicial MySQL `backend/migrations/versions/0001_initial_mysql_tables.py`
- [X] T005 [P] Modelos `users`, `faculties`, `programs` en `backend/app/models/`
- [X] T006 [P] Handlers JWT globales (expirado, inválido, no autorizado) en `app/__init__.py`
- [X] T007 [P] Seed de facultades y programas con el comando `flask seed-db`
- [X] T008 `backend/app/utils/errors.py` (`ServiceError`) y `controllers/http.py`

## Phase 3: US1 - Registro institucional (P1) 🎯 MVP

**Independent Test**: `POST /api/auth/register` con correo `@unilibre.edu.co` devuelve 201 y un token válido.

- [X] T009 [P] [US1] Schema de registro en `backend/app/schemas/auth.py` (contraseña mínima de 8)
- [X] T010 [US1] Servicio de registro en `backend/app/services/auth_service.py` (rol `researcher`, estado `active`)
- [X] T011 [US1] `register` en `controllers/auth_controller.py` y ruta en `routes/auth.py`
- [X] T012 [P] [US1] Test de schema para contraseña corta en `tests/test_schemas.py`

## Phase 4: US2 - Solicitud externa (P2)

- [X] T013 [P] [US2] Endpoint `request_account` (estado `pending`, sin token)
- [ ] T014 [US2] Confirmar que un correo institucional en la solicitud externa devuelve 400
- [ ] T015 [US2] Confirmar que un correo duplicado devuelve 409 por ambos caminos

## Phase 5: US3 - Login con JWT (P1)

- [X] T016 [US3] Endpoint `login` con claims `role` y `status`
- [ ] T017 [US3] Confirmar 403 con mensaje "Solicitud pendiente de aprobación" y el mensaje de cuenta rechazada
- [X] T018 [US3] Confirmado: `User.set_password` y `User.check_password` usan Flask-Bcrypt (constitución VII); spec actualizada

## Phase 6: US4 - Identidad protegida (P2)

- [X] T019 [US4] Endpoint `me` protegido con JWT
- [X] T020 [P] [US4] Endpoint `catalog` público para facultades y programas
- [ ] T021 [US4] Confirmar que un token inválido o expirado devuelve 401 y nunca 500

## Phase 7: Frontend y Polish

- [X] T022 [P] Páginas `login.html`, `register.html` y `static/js/auth.js` con token en `localStorage` (`riul_token`)
- [X] T023 [P] Tests en `backend/tests/test_auth.py`, con `conftest.py`
- [X] T024 Suite completa contra MySQL real (`riul_test`): 93 tests en verde
- [ ] T025 Verificar el flujo con `docker compose up` desde cero

## Dependencies

T001–T008 → fases 3 a 6. US1 y US3 comparten `auth_service.py`. La aprobación de cuentas pendientes queda fuera de esta spec (la cubre el panel de admin).
