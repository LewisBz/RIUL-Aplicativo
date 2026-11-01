# Feature 011: Analítica administrativa, soporte y editor de publicaciones

**Branch**: `011-analitica-soporte-editor` (desde `develop`)
**Mockups**: `riul_anal_tica_administrativa`, `riul_soporte_administrativo`, `riul_crear_publicaci_n`
**Constitución**: v3.0.0

## Propósito

Completar las pantallas del mockup que aún no existían: analítica administrativa, centro de soporte y editor de contenido. Se usan solo datos reales. Las métricas del mockup sin fuente de datos (H-index, financiación externa) y los campos sin modelo (visibilidad, destino, borrador) no se incluyen.

## Contrato de API (definido antes de implementar — Principio II)

| Método | Endpoint | Acceso | Éxito | Errores |
|---|---|---|---|---|
| GET | `/api/admin/analytics` | administrador | `200` `{totals, production[12], semilleros_by_faculty, top_semilleros, account_status}` | `401`, `403` |
| POST | `/api/support/tickets` | usuario activo | `201` `{ticket}` | `400`, `401` |
| GET | `/api/support/tickets` | usuario activo | `200` `{items, total}` (solo propios) | `401` |
| GET | `/api/admin/support/tickets?status=` | administrador | `200` `{items, total}` con datos del usuario | `400`, `401`, `403` |
| PATCH | `/api/admin/support/tickets/<id>` | administrador | `200` `{ticket}`; `reply` y/o `status` | `400`, `401`, `403`, `404` |

`category`: `technical_bug`, `feature_request`, `account_issue`, `other`. `status`: `open`, `in_progress`, `resolved`. Responder sin indicar estado pasa el ticket a `in_progress` y notifica al autor.

## Modelo de datos

`support_tickets`: id, user_id FK, category, subject (160), message, status (CHECK), admin_reply, replied_at, created_at. Migración `0003`.

## Historias

- **US1 Analítica (`/admin-analytics`)**: tarjetas de totales, línea de producción mensual (publicaciones por `published_on` y proyectos por `start_date`, con la fecha de registro como respaldo), barras de semilleros por facultad, top de semilleros por XP validado, dona de estado de cuentas y exportación CSV.
- **US2 Soporte admin (`/support`)**: acciones rápidas, búsqueda de ayuda, tabla de tickets con filtro por estado y diálogo de respuesta, documentación y contacto escalado.
- **US3 Ayuda de usuario (`/help`)**: crear tickets y ver respuestas. Enlace "Ayuda" en el footer.
- **US4 Editor (`/crear-publicacion`)**: título, contenido, enlace, archivo con arrastrar y soltar, y categoría. Publica con `POST /api/posts`; el título se antepone al contenido. Acceso desde "Editor completo" en el feed.

## Fuera de alcance

Visibilidad y destino de publicaciones, borradores, H-index y financiación, y editor de texto enriquecido.
