# Tasks: Fix de arranque y servicio del frontend

**Input**: `specs/004-fix-auth-serving/spec.md`, `plan.md`
**Estado**: [X] = encontrado en el repo; [ ] = requiere ejecución manual.

## Phase 1: US1 - El contenedor arranca (P1) 🎯 MVP

- [X] T001 [US1] Crear `backend/migrations/alembic.ini`
- [ ] T002 [US1] Validar `docker compose up -d --build app`: sin bucle de reinicio, con migración, seed y Gunicorn escuchando
- [ ] T003 [US1] Validar que `GET /api/auth/catalog` lista facultades y programas sembrados

## Phase 2: US2 - Flask sirve el frontend (P1)

- [X] T004 [US2] Ruta `/` en `backend/app/__init__.py`
- [X] T005 [US2] Ruta catch-all `/<path:path>` para páginas y estáticos, con `/api/*` con precedencia
- [X] T006 [P] [US2] Ruta `/openapi.yaml` y archivo `static/openapi.yaml`
- [X] T007 [P] [US2] Página `templates/docs.html` (Swagger UI) y archivo `backend/api.http` (US2.1)
- [ ] T008 [US2] Validar 200 en `/login`, `/register`, `/docs` y `/openapi.yaml`

## Phase 3: US3 - Base de API correcta (P2)

- [X] T009 [US3] En `static/js/auth.js`, base same-origin en el puerto 5000 y `http://localhost:5000` en otro origen
- [ ] T010 [US3] Validar el flujo registro → login → me con `curl`

## Phase 4: Polish

- [X] T011 Suite pytest en verde (la spec exigía 14 tests; hoy son 93)
- [X] T012 Criterios de aceptación de la spec actualizados: las páginas se sirven como plantillas

## Dependencies

T001 → T002/T003. T004 → T005 → T008.
