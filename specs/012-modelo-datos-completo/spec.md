# Especificación — Modelo de datos completo (diagrama ER)

**Estado**: implementado · **Migración**: `0004_complete_data_model.py` · **Esquema**: [`docs/er-riul.md`](../../docs/er-riul.md)

## Objetivo

Llevar a MySQL el modelo entidad-relación completo de RIUL (34 tablas en 8 dominios) y adaptar backend, frontend,
OpenAPI, documentación y Docker a ese modelo, sin perder los datos existentes.

## Historias de usuario

1. **Perfil**: como usuario quiero una biografía, foto y ORCID en mi perfil (`user_profiles`).
2. **Feed**: como miembro quiero comentar y compartir publicaciones (`comments`, `post_shares`).
3. **Semilleros**: como investigador quiero *solicitar* vincularme a un semillero y que su líder (o co-líder) apruebe o rechace la solicitud; también quiero seguir semilleros (`semillero_members.status`, `semillero_follows`).
4. **Proyectos**: como integrante quiero registrar productos de investigación tipados (`products`: artículo, ponencia, patente, informe).
5. **Convocatorias**: como administrador quiero publicar convocatorias (`calls`) que reciban postulaciones de personas o de semilleros (`call_applications`) y resolverlas.
6. **Gamificación**: como investigador quiero registrar logros con un origen verificable (evento, publicación, proyecto, producto o semillero) y adjuntar evidencias privadas; como administrador quiero aprobarlos y que el XP se acumule en un libro mayor (`xp_ledger`) del que salen nivel, insignias y progreso de semilleros.
7. **Reportes**: como administrador quiero generar reportes de un periodo y publicarlos (`report_snapshots`).

## Reglas

- Un logro tiene **exactamente un origen** (CHECK en base de datos); el tipo se deduce del origen.
- Solo los logros `approved` generan una fila en `xp_ledger` (única por logro).
- La facultad y el líder de un semillero son obligatorios; el líder es siempre miembro activo con rol `leader`.
- Las evidencias solo las descarga su dueño o un administrador.
- Los proyectos terminan en estado `closed` (antes `completed`).

## Migración de datos

- `publications` y `project_products` → `products`; `event_registrations` → `event_participations`; los eventos con `kind='call'` → `calls` (+ `call_applications`).
- `semilleros`: facultad y líder obligatorios; el líder pasa a figurar como miembro activo; `research_lines` → `semillero_research_lines`.
- `projects.leader_id` → integrante con rol `principal`; `completed` → `closed`; `notifications.is_read` → `read_at`.
- Logros antiguos nacidos de una inscripción a evento se conservan (mismo id) y se reconstruye el libro de XP; los demás no tienen origen verificable y se archivan en `achievements_legacy`.
- `downgrade` a 0003 restaura los datos originales (verificado en pruebas).

## Criterios de aceptación

- `test_migrations.py`: upgrade → modelos == migraciones → downgrade a 0003 → upgrade.
- `test_data_model.py`: contrato del esquema, CHECKs, comentarios/compartidos, convocatorias, pipeline de XP, privacidad de evidencias, reportes, perfil y coherencia del seed.
- `docker compose up --build` migra y siembra sin errores y el contenedor queda `healthy`.
