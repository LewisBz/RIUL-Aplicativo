# Contracts: 006 Dashboard y Perfil

Esta feature no define endpoints nuevos. Consume contratos de 003-auth, cuya
fuente de verdad son los schemas Marshmallow de `backend/app/schemas/auth.py` y
`backend/app/static/openapi.yaml`.

## GET /api/auth/me

- Header: `Authorization: Bearer <access_token>`
- 200: perfil del usuario (`id`, `email`, `full_name`, `role`, `faculty_id`, `program_id`). Los nombres exactos de los campos se toman del schema de auth.
- 401: token ausente, inválido o expirado. El cliente limpia el token y redirige a `/login`.

## GET /api/auth/catalog

- Público.
- 200: listas de facultades y programas para mapear id → nombre.

## Rutas de página (servidas por Flask)

| Ruta | Respuesta | Guard |
| --- | --- | --- |
| `/dashboard` | 200, HTML shell | Cliente: sin sesión redirige a `/login` |
| `/profile` | 200, HTML shell | Cliente: sin sesión redirige a `/login` |

## Contrato de DOM

- `body[data-nav-active]` toma el valor `dashboard` o `profile`. La sidebar usa ese valor para marcar el ítem activo.

## Contratos adicionales usados hoy por el codigo

- `GET /api/dashboard`: datos del dashboard (usado por `dashboard.js`).
- `GET /api/profile` y `PUT` o `PATCH /api/profile`: lectura y edicion del perfil (usado por `profile.js`). Verificar metodo exacto en `routes/profile.py`.

