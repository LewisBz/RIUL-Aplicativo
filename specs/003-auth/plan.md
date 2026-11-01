# Implementation Plan: Módulo de autenticación

**Branch**: `003-auth` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

## Summary

Primera capacidad de backend: esqueleto Flask en capas, conexión a MySQL por Docker
Compose y flujo completo de autenticación: registro institucional (acceso
inmediato), solicitud de cuenta externa (pendiente de aprobación) y login con JWT.

**Reconciliación con la constitución v3.0.0**: la spec cita la constitución v1.1.0
(PostgreSQL implícito). Hoy rigen MySQL 8.4 + PyMySQL, Flask MVC en capas, Marshmallow
y Flask-Bcrypt. La spec dice `check_password_hash` (Werkzeug), pero la constitución
exige Flask-Bcrypt. Verificar en `/speckit-analyze`.

## Technical Context

**Language/Version**: Python 3.12, Flask 3.x

**Primary Dependencies**: Flask-SQLAlchemy, Flask-Migrate, Marshmallow, Flask-JWT-Extended, Flask-Bcrypt, PyMySQL, Gunicorn

**Storage**: MySQL 8.4 (`users`, `faculties`, `programs`), migraciones Alembic

**Testing**: pytest contra MySQL real (`riul_test`)

**Target Platform**: Docker Compose (app + db)

**Project Type**: web-service (API REST)

**Constraints**: Secretos solo por variables de entorno. Token de 12h con claims `role` y `status`. Dominio institucional configurable

## Constitution Check

| Principio | Estado | Detalle |
| --- | --- | --- |
| I. Flask MVC | PASS | Existen `models`, `schemas`, `controllers`, `routes`, `services`, `repositories` |
| II. API-first | PASS | Contrato en la spec; schemas Marshmallow en `schemas/auth.py` |
| IV. MySQL | PASS | Migración `0001_initial_mysql_tables.py` |
| V. Docker | PASS | `compose.yml` y `backend/dockerfile` |
| VI. Tests | PASS | `tests/test_auth.py` y `tests/test_schemas.py` |
| VII. Seguridad | PASS | `User.set_password`/`check_password` usan Flask-Bcrypt |

## Project Structure

```text
specs/003-auth/
├── plan.md
└── tasks.md

backend/
├── app/{models,schemas,controllers,routes,services,repositories,utils}/
├── migrations/versions/0001_initial_mysql_tables.py
└── tests/{test_auth.py,test_schemas.py,conftest.py}
```

## Complexity Tracking

Sin violaciones.
