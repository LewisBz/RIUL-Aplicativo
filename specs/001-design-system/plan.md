# Implementation Plan: Sistema de diseño centralizado

**Branch**: `001-design-system` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

## Summary

Una sola hoja de estilos (`design-system.css`) con tokens Material 3 como variables
CSS, clases de componentes extraídas de los mockups y una página `styleguide.html`
de validación visual. CSS plano, sin build.

**Reconciliación con la constitución v3.0.0**: la spec ubica los archivos en
`frontend/`. Hoy viven en `backend/app/static/css/design-system.css` y
`backend/app/templates/styleguide.html` (constitución III: no existe un árbol
`frontend/` separado). Las tareas usan las rutas actuales.

## Technical Context

**Language/Version**: CSS3 plano + HTML5. Sin JS en esta feature.

**Primary Dependencies**: Google Fonts (Montserrat, Inter) y Material Symbols por `<link>` CDN

**Storage**: N/A

**Testing**: Validación visual contra `mockup/.../DESIGN.md` y la página styleguide

**Target Platform**: Navegadores modernos, servido por Flask

**Project Type**: web (hoja de estilos compartida)

**Constraints**: Un solo archivo CSS. Sin frameworks, preprocesadores ni bundlers. Solo tema claro.

**Scale/Scope**: ~40 tokens de color, escala tipográfica, ~25 familias de componentes

## Constitution Check

| Principio | Estado | Detalle |
| --- | --- | --- |
| III. Zero build, tokens CSS | PASS | Es el origen de los tokens |
| I. Layout Flask | PASS | CSS en `app/static/css`, HTML en `app/templates` |
| Resto | N/A | Sin backend ni datos |

## Project Structure

```text
specs/001-design-system/
├── plan.md
└── tasks.md

backend/app/
├── static/css/design-system.css
└── templates/styleguide.html
```

**Structure Decision**: Se mantiene un solo CSS dividido en secciones numeradas con comentarios. Las secciones posteriores (feed, session navbar, etc.) se agregan al mismo archivo.

## Complexity Tracking

Sin violaciones.
