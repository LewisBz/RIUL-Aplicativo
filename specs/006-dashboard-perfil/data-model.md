# Data Model: 006 Dashboard y Perfil

No hay entidades persistentes nuevas, ni migraciones ni tablas. Solo hay modelos de vista en el cliente.

## Identidad (real, de `/api/auth/me`; facultad y programa llegan resueltos en `/api/profile`)

| Campo | Origen | Uso |
| --- | --- | --- |
| `full_name` | me | Saludo, banner de perfil (si falta, se usa `email`) |
| `email` | me | Información personal |
| `role` | me | Etiqueta de rol (`researcher` o `administrator`) |
| `faculty`, `program` | profile | Objeto `{id, name}` o `null` |
| `faculties[]`, `programs[]` | catalog | Opciones del formulario de edición |

Inicial del avatar: primera letra de `full_name`, o de `email` si no hay nombre.

## Contenido (hoy servido por /api/dashboard y /api/profile; originalmente demo)

| Entidad | Campos | Pantalla |
| --- | --- | --- |
| Gamificación | `level`, `xp`, `nextXp`, `stars`, `badges[]` | Dashboard, Perfil |
| Proyecto | `title`, `status` | Dashboard, Perfil |
| Publicación | `title`, `venue`, `year` | Dashboard, Perfil |
| Producto | `title`, `status` (`Aprobado` o `En revisión`) | Perfil |
| Logro | `title`, `done` (booleano) | Perfil (línea de tiempo) |
| Semillero | `name`, `members` | Dashboard, Perfil |
| Notificación | `text`, `time` | Dashboard |

Reglas:
- La barra de XP muestra `xp / nextXp` (74% en el mockup).
- El estado `Aprobado` usa el color teal. `En revisión` usa gris.
- Las entidades viven en las tablas de las features de dominio (proyectos, publicaciones, logros, notificaciones, semilleros); esta feature no agrega tablas.

