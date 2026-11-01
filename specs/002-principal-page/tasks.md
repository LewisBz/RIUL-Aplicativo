# Tasks: Landing pública

**Input**: `specs/002-principal-page/spec.md`, `plan.md`
**Estado**: [X] = verificado en el repo; [ ] = pendiente o requiere validación manual.

## Phase 1: Setup

- [X] T001 Crear `backend/app/templates/index.html` enlazando solo `design-system.css`
- [X] T002 [P] Crear `backend/app/static/js/main.js` como módulo ES

## Phase 2: US1 - Landing fiel al mockup (P1) 🎯 MVP

**Independent Test**: Abrir `/` y comparar cada sección con el mockup.

- [X] T003 [US1] Agregar a `design-system.css` las clases `.topnav-brand`, `.nav-link`, `.btn-outline`, `.hero`, `.hero-bg`, `.hero-content`, `.card-hover`, `.line-clamp-3`, `.section-header`, `.list-row`, `.carousel-track`, `.carousel-card`, `.carousel-arrow`, `.hide-scrollbar`, `.progress-mini`, `.check-list`, `.media-overlay` (verificadas parcialmente con `rg`: hay coincidencias de `carousel-track` y `progress-mini`)
- [X] T004 [US1] Construir topnav con marca, enlaces y acciones hacia `/login` y `/register`
- [X] T005 [US1] Construir hero con fondo abstracto al 20% de opacidad
- [X] T006 [US1] Construir el bento (semilleros span-8, proyectos recientes span-4)
- [X] T007 [US1] Construir carrusel de eventos, sección "Descubrir Más" y footer institucional
- [X] T008 [US1] Confirmar que `index.html` no contiene referencias a Tailwind (verificado con `rg`: sin coincidencias en `templates/`)
- [ ] T009 [US1] Comparar visualmente cada sección con el mockup
- [ ] T010 [US1] Verificar que el bento apila a 1 columna bajo 768px

## Phase 3: US2 - Interacciones básicas (P2)

- [X] T011 [US2] Hamburguesa móvil que muestra y oculta el menú en `main.js`
- [X] T012 [US2] Chevrons del carrusel con `scrollBy` suave en `main.js`
- [X] T013 [US2] Cerrar el menú con Escape (en `main.js`)
- [ ] T014 [US2] Probar manualmente hamburguesa bajo 768px y chevrons a cualquier ancho

## Phase 4: Polish

- [X] T015 Verificado: `index.html` y `main.js` no consumen la API; los datos de la landing siguen hardcodeados, como dice la spec. Consumir `/api/semilleros`, `/api/projects` y `/api/events` queda como mejora futura (principio II)
- [ ] T016 Verificar el comportamiento sin JS y fuera de línea (fallbacks de fuentes)

## Dependencies

Depende de 001. T003 → T004–T007 → T009/T010. T011 y T012 son independientes entre sí.
