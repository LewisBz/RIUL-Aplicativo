# Tasks: Dashboard y Perfil del Investigador

**Input**: `specs/006-dashboard-perfil/spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`
**Estado**: [X] = encontrado en el repo; [ ] = pendiente o requiere verificación manual.

## Phase 1: Setup

- [X] T001 [P] Crear `backend/app/templates/dashboard.html` y `profile.html`
- [X] T002 [P] Crear `backend/app/static/js/dashboard.js` y `profile.js`
- [X] T003 [P] Estilos de sidebar y de ítem activo (`#9e1b32` / `#ffb0b3`) en `design-system.css`

## Phase 2: US1 - Guard de sesión (P1) 🎯 MVP

**Independent Test**: sin token, `/dashboard` y `/profile` redirigen a `/login`.

- [X] T004 [US1] `requireAuth()` en `session.js` que redirige a `/login` sin sesión válida
- [X] T005 [US1] Limpiar el token cuando `/api/auth/me` responde error
- [ ] T006 [US1] Probar token basura: se limpia, redirige y no hay bucle
- [X] T007 [US1] Decisión: `requireAuth` mantiene `location.href` (ver `research.md` R1); `/login` no redirige de vuelta sin sesión, así que no hay bucle

## Phase 3: US2 - Layout autenticado compartido (P1)

- [X] T008 [US2] Sidebar renderizada por `layout.js` desde `body[data-nav-active]` (la spec decía `sidebar.js`)
- [X] T009 [US2] Cerrar con Escape el menú desplegable en `layout.js`
- [ ] T010 [US2] Verificar que la sidebar se oculta en móvil y que el estilo del ítem activo coincide con el mockup

## Phase 4: US3 - Dashboard (P1)

- [X] T011 [US3] Dashboard consume `/api/dashboard` con adaptadores y skeletons (`adapters.js`, `skeleton.js`)
- [ ] T012 [US3] Verificar saludo con nombre real y las 5 tarjetas del bento (perfil, proyectos, publicaciones, semillero, notificaciones)
- [ ] T013 [US3] Verificar que "Ver Todo" lleva a `/profile` y que el bento colapsa a 1 columna en móvil

## Phase 5: US4 - Perfil (P1)

- [X] T014 [US4] Perfil consume `/api/profile` y `/api/auth/catalog` (facultad y programa por nombre)
- [X] T015 [US4] Edición del perfil (`PUT`/`PATCH /api/profile`) con el diálogo "Editar perfil". La spec la tenía deshabilitada: actualizar la spec
- [ ] T016 [US4] Verificar tarjeta de gamificación, tablas de publicaciones y productos, y línea de tiempo de logros según el mockup

## Phase 6: US5 y US6 - Datos y regresión

- [X] T017 [US5] Sin módulo demo: el contenido viene de API real (R3). Marcar US5 como superada en la spec
- [ ] T018 [US6] Ejecutar `pytest` y confirmar que pasa
- [ ] T019 [US6] Verificar homepage invitado y autenticado, `/login`, `/register` y `/docs`

## Phase 7: Alineación de la spec

- [X] T020 Actualizar `spec.md`: el backend aporta los endpoints, desaparecen `demo-data.js` y `sidebar.js`, la edición está activa
- [X] T021 Alinear el destino de logout (`/login`) en `spec.md`

## Dependencies

T001–T003 → US1 → US2 → US3/US4 → US5/US6 → Phase 7.
