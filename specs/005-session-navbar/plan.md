# Implementation Plan: Navbar con sesión

**Branch**: `005-session-navbar` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

## Summary

Feature solo de frontend. El navbar muestra los CTAs de invitado sin sesión. Con
sesión muestra avatar, nombre, rol y un menú con "Cerrar sesión". Un token inválido
o expirado se limpia en silencio y se vuelve a la vista de invitado.

## Technical Context

**Language/Version**: JavaScript ES2022 (módulos), CSS3

**Primary Dependencies**: Ninguna. Consume `/api/auth/me`

**Storage**: `localStorage` clave `riul_token`

**Testing**: Prueba manual (sin cambios de backend)

**Target Platform**: Navegadores modernos

**Project Type**: web (frontend)

**Constraints**: Sin bucles de redirección ni rechazos de promesa sin manejar

## Constitution Check

| Principio | Estado | Detalle |
| --- | --- | --- |
| III. Frontend vanilla | PASS | Módulo ES nativo y clases con tokens |
| VII. Seguridad | PASS | El servidor valida el token en `/me` |
| Resto | N/A | Sin backend |

## Project Structure

```text
specs/005-session-navbar/
├── plan.md
└── tasks.md

backend/app/
├── templates/index.html      # data-auth="guest" | "user"
└── static/js/{session.js,main.js}
```

## Complexity Tracking

Sin violaciones.
