# Research: 006 Dashboard y Perfil

## R1 — Guard de sesión

- **Decision**: Al cargar, la página llama a `/api/auth/me` con el Bearer token (`requireAuth()` en `session.js`). Si no hay sesión válida redirige a `/login` (`location.href`). El token se limpia solo con 401 o 403.
- **Rationale**: El servidor es la autoridad (constitución VII). Limpiar el token en 401/403 evita ciclos login ↔ página; un 5xx no debe cerrar la sesión. `location.href` es lo implementado y es aceptable porque `/login` no redirige de vuelta sin sesión.
- **Alternatives**: Validar solo la presencia del token (rechazado: tokens expirados causarían pantallas rotas).

## R2 — Resolución de facultad y programa

- **Decision original**: mapear IDs a nombres en el cliente con `/api/auth/catalog`.
- **Estado actual**: `GET /api/profile` devuelve `faculty` y `program` con id y nombre. `/api/auth/catalog` se usa solo para poblar los selects del formulario de edición.
- **Rationale**: Menos lógica en el cliente y una sola llamada para el perfil.

## R3 - Datos demo (superado por APIs reales)

- **Decision original**: contenido no modelado desde un unico modulo demo.
- **Estado actual**: `dashboard.js` consume `/api/dashboard` y `profile.js` consume `/api/profile`. No existe `demo-data.js`. Las features 007 a 010 aportaron las APIs reales.
- **Accion**: hecha. La spec se actualizó (US3, US4, US5 y el encabezado de backend).

## R4 — Sidebar compartida

- **Decision**: La sidebar se renderiza por JS y toma el ítem activo de `body[data-nav-active]`. Se oculta bajo el breakpoint móvil.
- **Rationale**: Evita duplicar HTML en cada página. Es compatible con zero-build.
- **Alternatives**: Include de Jinja (rechazado: la constitución limita las plantillas a shells de documento).

## R5 — Estilos del ítem activo

- **Decision**: Usar los valores del mockup (`#9e1b32` de fondo, `#ffb0b3` de texto) como variables CSS, no como literales sueltos.
- **Rationale**: La constitución III exige tokens. Se conserva la fidelidad al mockup.

Todos los NEEDS CLARIFICATION están resueltos.

