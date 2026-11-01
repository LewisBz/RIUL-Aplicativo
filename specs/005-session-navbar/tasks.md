# Tasks: Navbar con sesión

**Input**: `specs/005-session-navbar/spec.md`, `plan.md`
**Estado**: [X] = encontrado en el repo; [ ] = requiere prueba manual.

## Phase 1: Setup

- [X] T001 Crear `backend/app/static/js/session.js` con `getSessionUser()`, `logout()` y `API_BASE` (puerto ≠ 5000 → `http://localhost:5000`)
- [X] T002 [P] Marcar en `index.html` las acciones de invitado con `data-auth="guest"` y el bloque de usuario con `data-auth="user"`
- [X] T003 [P] Clases `.nav-user-btn`, `.nav-avatar`, `.nav-dropdown` en `design-system.css`

## Phase 2: US1 - Invitado ve los CTAs (P1)

- [X] T004 [US1] Sin `riul_token`, `session.js` deja visibles los elementos `guest` (alterna `.hidden` según `data-auth`)
- [ ] T005 [US1] Probar que el panel móvil conserva "Iniciar sesión"

## Phase 3: US2 - Identidad en el navbar (P1) 🎯 MVP

- [X] T006 [US2] Rellenar avatar, nombre y rol (`researcher` → Investigador, `administrator` → Administrador) con datos de `/api/auth/me`
- [X] T007 [US2] Dropdown que abre al hacer clic y cierra con Escape (clic fuera: verificar)
- [ ] T008 [US2] Probar que el escritorio y el panel móvil reflejan la sesión
- [X] T009 [US2] "Mi perfil" enlaza a `/profile`; spec actualizada

## Phase 4: US3 - Token inválido (P2)

- [X] T010 [US3] Limpiar el token cuando `/me` responde error de autenticación y volver a invitado (`session.js`)
- [ ] T011 [US3] Probar un token basura: vista de invitado, token borrado y sin errores en consola
- [X] T012 [US3] `getSessionUser()` borra el token solo con 401/403 (corregido en la feature 011); un 5xx lo conserva

## Phase 5: US4 - Cerrar sesión (P2)

- [X] T013 [US4] `logout()` borra el token. Hoy redirige a `/login`; la spec pide volver a la vista de invitado inmediatamente
- [X] T014 [US4] Spec alineada con el código: el logout redirige a `/login`

## Dependencies

T001 → T004–T013. Las desviaciones T009, T012 y T014 quedaron resueltas tras `/speckit-analyze`.
