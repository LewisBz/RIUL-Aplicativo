# Tareas — Modelo de datos completo

## Backend
- [x] Modelos por dominio (`app/models/`), incluidos perfil, comentarios, compartidos, seguidores, productos, convocatorias, libro de XP, evidencias y reportes.
- [x] Migración `0004_complete_data_model.py` con migración de datos y `downgrade` verificado.
- [x] Repositorios, servicios (`gamification_service.apply_approval`, `report_service`, vinculación con aprobación) y esquemas Marshmallow.
- [x] Rutas y controladores: comentarios, compartidos, aprobación de miembros, seguimiento, postulaciones, tipos de logro, evidencias, reportes.
- [x] Seed coherente (`seed_service`, `seed_data`) a través del libro de XP.
- [x] Pruebas: `test_data_model.py`, `test_migrations.py`, suites existentes adaptadas.

## Frontend
- [x] `adapters.js`: estados `closed`/`approved`/`pending`, tipos de producto, membresía y progreso de semilleros.
- [x] Semillero: solicitud pendiente/rechazada, seguir, aprobación del líder.
- [x] Gamificación: registro por origen con evidencia (`api.js` admite `FormData`), adjuntar evidencias.
- [x] Feed: comentarios y compartidos. Perfil: biografía y ORCID. Proyectos: tipo de producto y estado `closed`.
- [x] Administración: logros `pending`/`approved`, reportes (generar y publicar). Convocatorias: revisión de postulaciones.

## Documentación y Docker
- [x] `openapi.yaml` 2.0.0, `api.http`, `docs/er-riul.md`, `docs/er-riul.drawio`, `docs/tablas-y-datos.md`, README.
- [x] Docker: imagen multi-etapa con usuario sin privilegios, `entrypoint.sh` (migra, siembra según `SEED_DEMO`), healthchecks, perfil `tests`, `.dockerignore`, `.gitattributes`, `docker/mysql/riul.cnf`.
