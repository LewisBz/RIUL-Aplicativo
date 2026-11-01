# Implementation Plan: Feed de publicaciones

**Branch**: `004-feed-publicaciones` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

## Summary

Primer módulo autenticado: shell de app, caja de creación de posts, filtros por
categoría y grilla de tarjetas. Subida real de archivos (multipart), reacciones con
toggle y borrado por el autor. Los comentarios quedan fuera de alcance.

## Technical Context

**Language/Version**: Python 3.12 / Flask 3.x; JS ES2022 en `feed.js`

**Primary Dependencies**: Las de 003. Sin nuevas

**Storage**: MySQL (`posts`, `post_attachments`, `post_reactions`); archivos en volumen `uploads_data:/app/uploads`

**Testing**: pytest (`tests/test_posts.py`, `tests/test_schemas.py`)

**Target Platform**: Docker Compose

**Project Type**: web-service + frontend vanilla

**Constraints**: `MAX_CONTENT_LENGTH` de 10 MB. Extensiones permitidas. Nombres de archivo `<uuid>.<ext>`. Todo texto de usuario escapado en cliente

## Constitution Check

| Principio | Estado | Detalle |
| --- | --- | --- |
| I. MVC | PASS | `post.py` en models, schemas, repositories, services, controllers y routes |
| II. API-first | PASS | Contrato en la spec; handler 413 en JSON |
| III. Frontend vanilla | PASS | `feed.html` + `feed.js` + `design-system.css` |
| IV. MySQL | PASS | Tablas en `0001_initial_mysql_tables.py`; `UniqueConstraint(post_id, user_id)` |
| V. Docker | PASS | Volumen de uploads en `compose.yml` |
| VII. Seguridad | PASS | Chequeo de autor en servidor; 401 JSON global |

## Project Structure

```text
specs/004-feed-publicaciones/
├── plan.md
└── tasks.md

backend/app/
├── models/post.py
├── schemas/ (post schemas)
├── repositories/ · services/post_service.py
├── controllers/posts_controller.py
├── routes/posts.py
├── templates/feed.html
└── static/js/feed.js
```

## Complexity Tracking

Sin violaciones.
