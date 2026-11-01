# Implementation Plan: Dashboard y Perfil del Investigador

**Branch**: `006-dashboard-perfil` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-dashboard-perfil/spec.md`

## Summary

Dos pantallas autenticadas (`/dashboard`, `/profile`) con guard de sesión, navbar
de sesión (005) y sidebar compartida (`layout.js`). Identidad y contenido reales:
`dashboard.js` consume `/api/dashboard` y `profile.js` consume `/api/profile`
(lectura y edición). Feature de frontend sin modelo de datos propio; los endpoints
los aportan las features de dominio posteriores.

**Nota de estado**: implementada y alineada con la spec actualizada. El módulo demo
original (`demo-data.js`) fue reemplazado por la API; ver `research.md` (R3).

## Technical Context

**Language/Version**: JavaScript ES2022 (módulos nativos), HTML5, CSS3; backend Python 3.12 / Flask 3.x (endpoints de perfil y dashboard ya existentes)

**Primary Dependencies**: Ninguna nueva. `fetch` nativo, tokens CSS de `design-system.css`

**Storage**: N/A (token JWT en localStorage ya definido en 003; sin persistencia nueva)

**Testing**: pytest existente debe seguir verde (US6); verificación manual según `quickstart.md`

**Target Platform**: Navegadores modernos, servidos por Flask (Gunicorn en Docker Compose)

**Project Type**: web-service con frontend vanilla en `app/templates` + `app/static`

**Performance Goals**: Una llamada de datos por pantalla (`/api/dashboard` o `/api/profile`) con skeletons durante la carga

**Constraints**: Sin frameworks ni bundlers; tokens Stitch; contraste mínimo 4.5:1; contenedor máx. 1280px

**Scale/Scope**: 2 pantallas, 1 layout compartido (`layout.js`)

## Constitution Check

*GATE: debe pasar antes de Phase 0. Revalidado tras Phase 1.*

| Principio | Estado | Detalle |
| --- | --- | --- |
| I. Flask Layered MVC | PASS | Los endpoints siguen las capas (routes → controllers → services → repositories); los HTML viven en `app/templates`, assets en `app/static` |
| II. API-First | PASS | Solo consume contratos existentes (`/api/auth/me`, `/api/auth/catalog`); sin endpoints nuevos |
| III. Frontend vanilla, zero build | PASS | Módulos ES nativos; colores y espaciado desde variables CSS |
| IV. MySQL fuente única | PASS (N/A) | Sin entidades nuevas. Datos demo no se persisten |
| V. Docker reproducible | PASS | Se valida vía `compose.yml` |
| VI. Tested layers | PASS | Sin código backend nuevo; la suite actual no debe romperse |
| VII. Seguridad/JWT | PASS | Guard cliente es solo UX; el servidor revalida el token en `/me`. Token inválido se limpia |
| VIII. Git workflow | PASS | Rama `006-dashboard-perfil` creada desde `develop`; commits y push los hace un humano |

Sin violaciones: no se requiere Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/006-dashboard-perfil/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── consumed-api.md
└── tasks.md             # lo genera /speckit-tasks
```

### Source Code (repository root)

```text
backend/app/
├── templates/
│   ├── dashboard.html
│   └── profile.html
└── static/
    ├── css/design-system.css
    └── js/
        ├── session.js      # guard + initSessionUI (005)
        ├── layout.js       # navbar/sidebar compartidos
        ├── dashboard.js
        └── profile.js
```

**Structure Decision**: Se usa el layout Flask existente bajo `backend/app/`. No se
crean carpetas nuevas ni un árbol `frontend/` separado.

## Complexity Tracking

Sin violaciones; no aplica.

