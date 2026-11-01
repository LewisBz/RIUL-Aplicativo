# RIUL — Red de Investigación Universidad Libre

Aplicativo tipo red social para la comunidad investigadora de la Universidad Libre
(Barranquilla, Atlántico). Conecta investigadores, docentes líderes y administradores
alrededor de **semilleros, proyectos, eventos, publicaciones y logros**.

## Objetivo

Centralizar la actividad de investigación universitaria en un solo lugar:

- **Visibilizar** semilleros de investigación, sus líneas, equipos, proyectos y publicaciones.
- **Conectar** a la comunidad mediante un feed de publicaciones con adjuntos y reacciones.
- **Gestionar** proyectos (estado, avance, hitos, productos) y la participación en eventos y convocatorias.
- **Reconocer** el esfuerzo con gamificación: XP validada por la administración, niveles, insignias y ranking.
- **Administrar** el acceso: registro institucional inmediato, solicitudes externas por aprobación y moderación.

## Roles

| Rol | Alcance |
|---|---|
| `researcher` | Investigador: se une a semilleros, crea proyectos, se inscribe en eventos, publica y registra logros. |
| `leader` | Docente líder: además crea semilleros y publica eventos/convocatorias. |
| `administrator` | Aprueba usuarios, valida logros, modera publicaciones y ve métricas globales. |

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, Flask 3, Flask-SQLAlchemy, Flask-Migrate (Alembic), Marshmallow |
| Seguridad | JWT (Flask-JWT-Extended), bcrypt, límite de intentos por IP, CORS configurable |
| Base de datos | MySQL 8.4 (PyMySQL) |
| Frontend | HTML (plantillas Jinja) + CSS (`design-system.css`) + JavaScript ES modules sin build |
| Contenedores | Docker Compose, Gunicorn |
| Calidad | pytest (MySQL real) |

## Estructura del repositorio

```
RIUL-Aplicativo/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Factory create_app, páginas, CORS, comandos CLI
│   │   ├── config.py            # dev / test / prod
│   │   ├── routes/              # Blueprints: URL -> controlador
│   │   ├── controllers/         # HTTP: valida entrada, llama servicios, serializa
│   │   ├── services/            # Reglas de negocio y permisos
│   │   ├── repositories/        # Acceso a datos (SQLAlchemy)
│   │   ├── models/              # Entidades ORM por dominio
│   │   ├── schemas/             # Marshmallow: entrada y serializadores de salida
│   │   ├── utils/               # Errores, slugs, rate limit
│   │   ├── templates/           # Páginas Jinja (una por pantalla)
│   │   ├── static/              # css, js (ES modules), openapi.yaml
│   │   └── seed_data.py         # Datos demo (fuente única)
│   ├── migrations/versions/     # 0001 base, 0002 dominio de investigación
│   ├── tests/                   # pytest por módulo
│   ├── api.http                 # Peticiones manuales (REST Client)
│   ├── dockerfile · pyproject.toml · run.py · wsgi.py
├── docs/                        # Modelo de datos, ER, datos sembrados
├── mockup/                      # Diseños de referencia (Stitch)
├── specs/                       # Especificaciones por funcionalidad
├── .specify/                    # Constitución y plantillas Spec Kit
├── compose.yml                  # MySQL + aplicación
└── .env.example                 # Variables de entorno
```

### Flujo de una petición

`routes` → `controllers` (guard de sesión + validación Marshmallow) → `services` (reglas, permisos, notificaciones) → `repositories` → `models`.
Los errores de negocio son `ServiceError(mensaje, estado)` y se responden como `{"message": "..."}`.

### Frontend

Cada pantalla es una plantilla en `templates/` más un módulo en `static/js/`. Piezas compartidas:
`session.js` (sesión JWT), `layout.js` (barra y menú), `api.js` (cliente REST), `adapters.js`
(API → modelos de vista), `forms.js` (diálogos de formulario).

## Módulos y API

Todas las rutas viven bajo `/api`, usan JSON, `snake_case` y exigen `Authorization: Bearer <token>`
salvo las de registro, login y catálogo. Documentación interactiva en **`/docs`** (OpenAPI en `/openapi.yaml`).

| Recurso | Endpoints |
|---|---|
| Auth | `POST /auth/register` · `POST /auth/request-account` · `POST /auth/login` · `GET /auth/me` · `GET /auth/catalog` |
| Perfil | `GET·PATCH /profile` · `POST /profile/password` · `POST /publications` · `GET /dashboard` |
| Feed | `GET·POST /posts` · `DELETE /posts/{id}` · `POST /posts/{id}/reactions` · `GET /posts/files/{name}` |
| Semilleros | `GET·POST /semilleros` · `GET /semilleros/{slug}` · `POST /semilleros/{slug}/members` · `DELETE /semilleros/{slug}/members/me` · `POST /semilleros/{slug}/activities` |
| Proyectos | `GET·POST /projects` · `GET·PATCH /projects/{slug}` · `POST /projects/{slug}/products` · `PATCH /projects/{slug}/milestones/{id}` |
| Eventos | `GET·POST /events` · `GET /events/{slug}` · `POST /events/{slug}/registrations` · `DELETE /events/{slug}/registrations/me` |
| Notificaciones | `GET /notifications` · `PATCH /notifications/{id}` · `POST /notifications/read-all` |
| Gamificación | `GET /gamification/me` · `GET /gamification/ranking` · `POST /gamification/achievements` |
| Admin | `GET /admin/overview` · `GET /admin/users` · `PATCH /admin/users/{id}` · `GET /admin/achievements` · `PATCH /admin/achievements/{id}` |

Convenciones: colecciones devuelven `{items, total}`; recursos devuelven un objeto con el nombre del
recurso (`{"project": {...}}`); semilleros, proyectos y eventos se direccionan por `slug`.

### Páginas

`/` · `/login` · `/register` · `/dashboard` · `/profile` · `/feed` · `/semilleros` · `/semillero-detalle?id=` ·
`/projects` · `/project-detail?id=` · `/events` · `/event-detail?id=` · `/gamification` · `/notifications` ·
`/admin` · `/docs` · `/privacidad` · `/terminos` · `/contacto`

### Flujos principales

- **Cuenta externa**: solicitud → `pending` → el administrador la aprueba → el usuario recibe una notificación.
- **Evento**: inscripción (valida cupo y cierre) → notificación → logro de participación `in_review` → el administrador lo valida y asigna XP.
- **Gamificación**: 200 XP por nivel; solo los logros `validated` suman al nivel y al ranking.
- **Semillero**: un investigador se vincula y el líder recibe una notificación.

## Puesta en marcha

Requisitos: Docker Desktop. Para desarrollo local sin contenedor de aplicación, Python 3.12 y [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env          # ajusta secretos y contraseñas
docker compose up --build     # MySQL + app en http://localhost:5000
```

El contenedor ejecuta `flask db upgrade && flask seed-demo` y luego Gunicorn.
**`seed-demo` reemplaza usuarios, publicaciones y todo el dominio de investigación**: úsalo solo en desarrollo.

Desarrollo local:

```bash
docker compose up -d db                 # MySQL en localhost:3307
cd backend
uv sync
uv run flask --app run.py db upgrade
uv run flask --app run.py seed-demo
uv run flask --app run.py run --port 5000
```

> El puerto del host para MySQL es **3307** (`DATABASE_URL`/`TEST_DATABASE_URL` en `.env.example`).

### Comandos CLI

| Comando | Efecto |
|---|---|
| `flask seed-db` | Facultades y programas (idempotente) |
| `flask seed-admin` | Administrador de desarrollo (`ADMIN_DEMO_*`) |
| `flask seed-demo` | Reconstruye el conjunto de datos demo completo |

### Usuarios demo

`flask seed-demo` crea 15 usuarios. Todos comparten la misma contraseña: el valor de
`DEMO_USERS_PASSWORD` (por defecto **`RiulDemo2026*`**).

| Nombre | Correo | Rol | Estado | Facultad / Programa |
|---|---|---|---|---|
| Ana Sofía Restrepo | `ana.restrepo@unilibre.edu.co` | administrator | active | — |
| Leonardo Pardo Roa | `leonardo.pardo@unilibre.edu.co` | administrator | active | — |
| Laura Mendoza | `laura.mendoza@unilibre.edu.co` | leader | active | Ingeniería / Ing. de Sistemas |
| María Antonieta Pérez | `maria.antonieta.perez@unilibre.edu.co` | leader | active | Ingeniería / Ing. de Sistemas |
| Mateo Silva | `mateo.silva@unilibre.edu.co` | leader | active | Ingeniería / Ing. Industrial |
| Javier Torres | `javier.torres@unilibre.edu.co` | leader | active | Ciencias Básicas / Biología |
| Camila Rojas | `camila.rojas@unilibre.edu.co` | researcher | active | Ingeniería / Ing. de Sistemas |
| Andrés Pérez | `andres.perez@unilibre.edu.co` | researcher | active | Ingeniería / Ing. de Sistemas |
| Luis Grandett | `luis.grandett@unilibre.edu.co` | researcher | active | Ingeniería / Ing. de Sistemas |
| Carolina Martínez | `carolina.martinez@unilibre.edu.co` | researcher | active | Ingeniería / Ing. de Sistemas |
| Diego Gutiérrez | `diego.gutierrez@unilibre.edu.co` | researcher | active | Ingeniería / Ing. Industrial |
| Paula Fernández | `paula.fernandez@unilibre.edu.co` | researcher | active | Ingeniería / Ing. Industrial |
| Sofía Díaz | `sofia.diaz@unilibre.edu.co` | researcher | active | Ciencias Básicas / Biología |
| Isabela Blanco | `isabela.blanco@gmail.com` | researcher | pending | Ciencias Básicas / Biología |
| Tomás Restrepo | `tomas.restrepo@hotmail.com` | researcher | rejected | Ingeniería / Ing. de Sistemas |

- Para probar el flujo completo, entra como `camila.rojas` (investigadora con semillero, proyectos y logros), `laura.mendoza` (líder) o `ana.restrepo` (administradora, accede a `/admin`).
- Isabela (`pending`) y Tomás (`rejected`) no pueden iniciar sesión: sirven para probar los mensajes de "Solicitud pendiente de aprobación" y "Cuenta no autorizada".
- Detalle del conjunto de datos: [`docs/tablas-y-datos.md`](docs/tablas-y-datos.md).

## Pruebas

```bash
docker compose up -d db
cd backend && uv run pytest
```

Las pruebas usan la base `riul_test` (se crea sola) y cubren auth, feed, administración,
semilleros, proyectos, eventos, notificaciones, gamificación, perfil y esquemas.

## Configuración

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Conexión SQLAlchemy a MySQL |
| `SECRET_KEY` · `JWT_SECRET_KEY` | Secretos (obligatorios y distintos del valor de desarrollo en `prod`) |
| `INSTITUTIONAL_EMAIL_DOMAIN` | Dominio con registro inmediato (`unilibre.edu.co`) |
| `CORS_ORIGINS` | Orígenes permitidos separados por coma; `*` solo en desarrollo |
| `UPLOAD_FOLDER` | Carpeta de adjuntos del feed |
| `DEMO_USERS_PASSWORD` · `ADMIN_DEMO_*` | Semillas de desarrollo |

Para producción usa la configuración `prod` (`create_app("prod")`), que se niega a arrancar con secretos por defecto o CORS abierto.

## Seguridad

- Contraseñas con bcrypt y JWT de 12 h; las rutas de escritura exigen cuenta `active`.
- Límite de intentos por IP en login, registro, solicitud de cuenta y cambio de contraseña.
- Los adjuntos requieren sesión (cabecera o `?token=` para `<img>`/enlaces).
- `/styleguide` solo existe en desarrollo y pruebas.

## Documentación adicional

- [`docs/tablas-y-datos.md`](docs/tablas-y-datos.md) — esquema y datos sembrados
- [`docs/er-riul.md`](docs/er-riul.md) y [`docs/er-riul.drawio`](docs/er-riul.drawio) — entidad-relación
- [`specs/`](specs/) — especificaciones por funcionalidad
- [`.specify/memory/constitution.md`](.specify/memory/constitution.md) — principios de arquitectura

## Equipo

Luis, Hector, Javier — Universidad Libre, Barranquilla.

## Licencia

Ver [`LICENSE`](LICENSE).
