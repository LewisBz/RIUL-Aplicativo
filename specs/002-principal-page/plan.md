# Implementation Plan: Landing pública desde el mockup principal

**Branch**: `002-principal-page` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

## Summary

Landing pública fiel al mockup `riul_p_gina_principal`: navegación, hero, bento de
semilleros y proyectos, carrusel de eventos, "Descubrir Más" y footer. Usa solo
`design-system.css`. Interacciones mínimas en JS vanilla.

**Reconciliación con la constitución v3.0.0**: la spec usa `frontend/index.html` y
`frontend/js/main.js`. Hoy son `backend/app/templates/index.html` y
`backend/app/static/js/main.js`, servidos por Flask en `/`. Los datos hardcodeados
pueden haberse reemplazado por consumo de API en features posteriores (principio II).

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript ES2022 (módulo `main.js`)

**Primary Dependencies**: Ninguna. Depende de 001 (`design-system.css`)

**Storage**: N/A

**Testing**: Comparación visual con el mockup y prueba manual de interacciones

**Target Platform**: Navegadores modernos, servido por Flask

**Project Type**: web (página pública)

**Constraints**: Sin Tailwind ni frameworks. Máximo un archivo JS para el módulo. Contenedor 1280px

## Constitution Check

| Principio | Estado | Detalle |
| --- | --- | --- |
| III. Frontend vanilla | PASS | Sin frameworks; clases nuevas como tokens en el CSS central |
| I. Layout Flask | PASS | Archivos en `app/templates` y `app/static` |
| II. API-first | OBSERVACIÓN | La spec original deja los datos hardcodeados «por ahora». Verificar en tareas si ya consume API |

## Project Structure

```text
specs/002-principal-page/
├── plan.md
└── tasks.md

backend/app/
├── templates/index.html
└── static/
    ├── css/design-system.css
    └── js/main.js
```

## Complexity Tracking

Sin violaciones.
