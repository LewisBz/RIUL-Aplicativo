# Tasks: Feed de publicaciones

**Input**: `specs/004-feed-publicaciones/spec.md`, `plan.md`
**Estado**: [X] = encontrado en el repo; [ ] = pendiente o requiere verificación manual.

## Phase 1: Foundational

- [X] T001 [P] Modelos `Post`, `PostAttachment`, `PostReaction` en `backend/app/models/post.py` (`UniqueConstraint(post_id, user_id)`)
- [X] T002 [P] Migración de las tablas de posts en `0001_initial_mysql_tables.py`
- [X] T003 [P] `UPLOAD_FOLDER` y `MAX_CONTENT_LENGTH` de 10 MB en `config.py`
- [X] T004 [P] Volumen `uploads_data` en `compose.yml`
- [X] T005 Registro del blueprint de posts en `create_app` y handler 413 en `routes/posts.py`

## Phase 2: US1 - Crear post (P1) 🎯 MVP

**Independent Test**: `POST /api/posts` multipart devuelve 201 con el post serializado.

- [X] T006 [P] [US1] Schemas de creación con categorías válidas (`article`, `project_advance`, `presentation`, `event`, `community`)
- [X] T007 [US1] `post_service.py`: regla de al menos uno entre content, link y file; extensiones y nombre `<uuid>.<ext>`
- [X] T008 [US1] `posts_controller.py`: `POST /api/posts` y respuesta 413 en JSON
- [X] T009 [P] [US1] Test de categoría desconocida en `tests/test_schemas.py`
- [X] T010 [P] [US1] Tests de la API en `tests/test_posts.py`
- [ ] T011 [US1] Confirmar que un POST sin content, link ni file devuelve 400

## Phase 3: US2 - Explorar el feed con filtros (P1)

- [X] T012 [US2] `GET /api/posts` con `category` y `page`, orden `created_at DESC`
- [X] T013 [P] [US2] `static/js/feed.js` y `templates/feed.html` con chips de filtro
- [ ] T014 [US2] Confirmar paginación de 10 por página y respuesta 400 para categoría inválida
- [ ] T015 [US2] Confirmar escape de HTML en todo texto de usuario y estado vacío amigable

## Phase 4: US3 - Reacciones (P2)

- [X] T016 [US3] `POST /api/posts/<id>/reactions` con toggle (`reaction_count`, `reacted_by_me`)
- [ ] T017 [US3] Confirmar 404 para un post inexistente

## Phase 5: US4 - Borrar post propio (P3)

- [X] T018 [US4] `DELETE /api/posts/<id>` solo para el autor, con borrado físico del adjunto
- [ ] T019 [US4] Confirmar 403 para no autor, 404 para inexistente, y que el menú solo aparece en posts propios
- [X] T020 [P] Endpoint público `GET /api/posts/files/<name>`

## Phase 6: Polish

- [ ] T021 Comparar `feed.html` con el mockup `riul_feed_de_publicaciones`
- [ ] T022 Ejecutar `pytest` con MySQL real y confirmar que la suite pasa
- [ ] T023 Verificar que el volumen persiste archivos tras reiniciar el contenedor

## Dependencies

Fase 1 → US1 → US2/US3/US4. Los comentarios y la edición quedan fuera de alcance.
