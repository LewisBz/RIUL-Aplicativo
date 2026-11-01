# Implementation Plan: Fix de arranque y servicio del frontend

**Branch**: `004-fix-auth-serving` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

## Summary

Bugfix de 003: el contenedor no arrancaba por falta de `migrations/alembic.ini`.
Además, Flask sirve ahora el frontend en un único origen (`:5000`), con URLs limpias
y documentación Swagger en `/docs`.

## Technical Context

**Language/Version**: Python 3.12 / Flask 3.x

**Primary Dependencies**: Flask-Migrate (Alembic). Swagger UI por CDN (solo desarrollo)

**Storage**: N/A (sin cambios de esquema)

**Testing**: pytest sigue en verde; verificación con `curl`

**Target Platform**: Docker Compose

**Project Type**: web-service

**Constraints**: Las rutas `/api/*` mantienen precedencia sobre el catch-all del frontend

## Constitution Check

| Principio | Estado | Detalle |
| --- | --- | --- |
| I. Flask MVC | PASS | Rutas de página en `create_app`, assets en `app/static` |
| III. Frontend vanilla | PASS | Sin build |
| V. Docker | PASS | Es el objetivo del fix |
| VIII. Git | PASS | Rama de bugfix `NNN-fix-*` |

## Project Structure

```text
specs/004-fix-auth-serving/
├── plan.md
└── tasks.md

backend/
├── migrations/alembic.ini
├── api.http
└── app/
    ├── __init__.py            # "/", "/openapi.yaml", "/<path:path>"
    ├── static/openapi.yaml
    └── templates/docs.html
```

## Complexity Tracking

Sin violaciones.
