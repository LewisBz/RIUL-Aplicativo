# Tasks: Sistema de diseño centralizado

**Input**: `specs/001-design-system/spec.md`, `plan.md`
**Estado**: [X] = verificado en el repo; [ ] = pendiente o requiere validación manual.
**Tests**: Sin tests automatizados (CSS). Validación visual.

## Phase 1: Setup

- [X] T001 Crear `backend/app/static/css/design-system.css` como único archivo de estilos
- [X] T002 [P] Crear `backend/app/templates/styleguide.html` enlazando solo el CSS central

## Phase 2: US1 - Hoja única con tokens y componentes (P1) 🎯 MVP

**Goal**: Cualquier vista consume tokens y componentes con un solo `<link>`.
**Independent Test**: Una página que solo enlaza `design-system.css` renderiza tokens y componentes sin Tailwind.

- [X] T003 [US1] Definir los tokens de color Material 3 y `--accent-gold: #ffb800` en `:root` de `design-system.css`
- [X] T004 [P] [US1] Definir tipografía (Montserrat 600/700, Inter 400/600/700) y las clases de escala
- [X] T005 [P] [US1] Definir espaciado de 4px, gutter 24px, contenedor 1280px, margen móvil 16px
- [X] T006 [P] [US1] Definir radios (sm 4, md 8, lg 16, pill) y sombras (ambient, gamified, glow de XP)
- [X] T007 [US1] Implementar botones: primary, secondary, gold y tertiary
- [X] T008 [P] [US1] Implementar inputs y selects con radio 8px y foco crimson de 2px
- [X] T009 [P] [US1] Implementar `.glass-card`, research card y achievement card con borde ámbar
- [X] T010 [P] [US1] Implementar pills de estado, chips de filtro, tabs, tabla zebra y timeline vertical
- [X] T011 [P] [US1] Implementar dropzone, barra de XP con glow y app shell (topnav 64px, sidebar 256px)
- [X] T012 [P] [US1] Implementar footer institucional y scrollbar personalizado
- [X] T013 [US1] Implementar el grid de 12 columnas y el stack responsive a 1 columna en ≤768px
- [X] T014 [US1] Agregar guardas `overflow-wrap` y `max-width` en chips y pills

## Phase 3: US2 - Página styleguide (P2)

**Goal**: Mostrar todos los tokens y componentes con etiquetas.
**Independent Test**: Abrir `/styleguide` y ver cada grupo de tokens y componentes.

- [X] T015 [US2] Mostrar swatches de color, escala tipográfica y escala de espaciado en `styleguide.html`
- [X] T016 [US2] Mostrar cada componente (botones, inputs, pills, cards, XP, tablas, timeline, shell)

## Phase 4: Polish y validación

- [ ] T017 Comparar primary, fuentes y ritmo de espaciado con `mockup/stitch_riul_design_system_strategy/riul_academic_evolution/DESIGN.md`
- [ ] T018 Confirmar que el CSS no tiene referencias a frameworks y que carga fuera de línea con fallbacks de fuentes
- [ ] T019 Confirmar que `/styleguide` responde 200 en el entorno Docker

## Dependencies

T001 → T003–T014 → T015–T016 → T017–T019. Las tareas [P] de la fase 2 no comparten secciones del archivo, pero sí el mismo archivo: aplicarlas en secuencia o resolver conflictos de merge.
