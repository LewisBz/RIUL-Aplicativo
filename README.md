# RIUL — Red de Investigación Universidad Libre

Aplicativo tipo red social para la comunidad investigadora de la Universidad Libre
(Barranquilla, Atlántico). Conecta investigadores, docentes líderes y administradores
alrededor de **semilleros, proyectos, eventos, publicaciones y logros**.

## Objetivo

Centralizar la actividad de investigación universitaria en un solo lugar:

- **Visibilizar** semilleros de investigación, sus líneas, equipos, proyectos y publicaciones.
- **Conectar** a la comunidad mediante un feed de publicaciones con adjuntos, reacciones, comentarios y compartidos.
- **Gestionar** proyectos (estado, avance, hitos, productos) y la participación en eventos y convocatorias.
- **Reconocer** el esfuerzo con gamificación: logros con origen verificable y evidencias, XP aprobada por la administración (libro mayor), niveles, insignias y ranking.
- **Reportar**: reportes institucionales (producción y ranking) generados y publicados por la administración.
- **Administrar** el acceso: registro institucional inmediato, solicitudes externas por aprobación y moderación.

## Roles

| Rol | Alcance |
|---|---|
| `researcher` | Investigador: solicita unirse a semilleros, crea proyectos, se inscribe en eventos, publica y registra logros. |
| `leader` | Docente líder: además crea semilleros, aprueba solicitudes de vinculación y publica eventos. |
| `administrator` | Aprueba usuarios, valida logros, publica convocatorias y resuelve postulaciones, genera reportes y ve métricas globales. |

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, Flask 3, Flask-SQLAlchemy, Flask-Migrate (Alembic), Marshmallow |
| Seguridad | JWT (Flask-JWT-Extended), bcrypt, límite de intentos por IP, CORS configurable |
| Base de datos | MySQL 8.4 (PyMySQL) |
| Frontend | HTML (plantillas Jinja) + CSS (`design-system.css`) + JavaScript ES modules sin build |
| Contenedores | Docker Compose, imagen multi-etapa (uv), Gunicorn |
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
│   ├── migrations/versions/     # 0001 base, 0002 dominio, 0003 soporte, 0004 modelo completo
│   ├── docker/entrypoint.sh     # migra, siembra y lanza Gunicorn
│   ├── tests/                   # pytest por módulo
│   ├── api.http                 # Peticiones manuales (REST Client)
│   ├── dockerfile · pyproject.toml · run.py · wsgi.py
├── docs/                        # Modelo de datos, ER, datos sembrados
├── mockup/                      # Diseños de referencia (Stitch)
├── specs/                       # Especificaciones por funcionalidad
├── .specify/                    # Constitución y plantillas Spec Kit
├── docker/mysql/riul.cnf        # utf8mb4 para MySQL
├── compose.yml                  # MySQL + aplicación (+ perfil de pruebas)
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
| Feed | `GET·POST /posts` · `DELETE /posts/{id}` · `POST /posts/{id}/reactions` · `GET·POST /posts/{id}/comments` · `DELETE /posts/{id}/comments/{cid}` · `POST /posts/{id}/shares` · `GET /posts/files/{name}` |
| Semilleros | `GET·POST /semilleros` · `GET /semilleros/{slug}` · `POST /semilleros/{slug}/members` · `PATCH /semilleros/{slug}/members/{user_id}` · `DELETE /semilleros/{slug}/members/me` · `POST·DELETE /semilleros/{slug}/follow` · `POST /semilleros/{slug}/activities` |
| Proyectos | `GET·POST /projects` · `GET·PATCH /projects/{slug}` · `POST /projects/{slug}/products` · `PATCH /projects/{slug}/milestones/{id}` |
| Eventos | `GET·POST /events` · `GET /events/{slug}` · `POST /events/{slug}/registrations` · `DELETE /events/{slug}/registrations/me` · `GET /events/{slug}/applications` · `PATCH /events/{slug}/applications/{id}` |
| Notificaciones | `GET /notifications` · `PATCH /notifications/{id}` · `POST /notifications/read-all` |
| Gamificación | `GET /gamification/me` · `GET /gamification/ranking` · `GET /gamification/types` · `POST /gamification/achievements` · `POST /gamification/achievements/{id}/evidences` · `GET /gamification/evidences/{name}` |
| Reportes | `GET /reports` · `GET /reports/{id}` (publicados) · `GET·POST /admin/reports` · `GET /admin/reports/{id}` · `POST /admin/reports/{id}/publication` |
| Admin | `GET /admin/overview` · `GET /admin/analytics` · `GET /admin/users` · `PATCH /admin/users/{id}` · `GET /admin/achievements` · `PATCH /admin/achievements/{id}` |
| Soporte | `GET·POST /support/tickets` · `GET /admin/support/tickets` · `PATCH /admin/support/tickets/{id}` |

Convenciones: colecciones devuelven `{items, total}`; recursos devuelven un objeto con el nombre del
recurso (`{"project": {...}}`); semilleros, proyectos y eventos se direccionan por `slug`.

### Páginas

`/` · `/login` · `/register` · `/dashboard` · `/profile` · `/feed` · `/semilleros` · `/semillero-detalle?id=` ·
`/projects` · `/project-detail?id=` · `/events` · `/event-detail?id=` · `/gamification` · `/notifications` ·
`/crear-publicacion` · `/help` · `/admin` · `/admin-analytics` · `/support` · `/docs` · `/privacidad` · `/terminos` · `/contacto`

### Flujos principales

- **Cuenta externa**: solicitud → `pending` → el administrador la aprueba → el usuario recibe una notificación.
- **Evento**: inscripción (valida cupo y cierre) → notificación → logro de participación `pending` → el administrador lo aprueba y asigna XP.
- **Convocatoria**: una persona o el líder de un semillero se postula → el administrador acepta o rechaza → el postulante recibe una notificación.
- **Gamificación**: cada logro tiene exactamente un origen (evento, publicación, proyecto, producto o semillero) y puede llevar evidencias privadas. Al aprobarse se escribe en el libro mayor `xp_ledger`, del que salen el nivel, las insignias y el progreso del semillero; solo los logros `approved` suman.
- **Semillero**: el investigador solicita vincularse (`pending`) y el líder o co-líder la aprueba o rechaza; también se puede seguir un semillero sin pertenecer a él.
- **Reportes**: el administrador genera un reporte (borrador) de un periodo y lo publica para todos.

## Puesta en marcha

Requisitos: Docker Desktop. Para desarrollo local sin contenedor de aplicación, Python 3.12 y [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env          # ajusta secretos y contraseñas
docker compose up --build     # MySQL + app en http://localhost:5000
```

El contenedor (`backend/docker/entrypoint.sh`) ejecuta `flask db upgrade`, luego `flask seed-demo` y por último Gunicorn, que corre con un usuario sin privilegios.
**`seed-demo` reemplaza usuarios, publicaciones y todo el dominio de investigación**: úsalo solo en desarrollo. Con `SEED_DEMO=0` en el entorno solo se siembran los catálogos (`flask seed-db`) y se conservan los datos.
Los servicios `db` y `app` tienen healthcheck; el esquema completo (34 tablas) lo crean las migraciones 0001–0004.

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
| `flask seed-db` | Catálogos: facultades, programas, niveles, insignias y tipos de logro (idempotente) |
| `flask seed-admin` | Administrador de desarrollo (`ADMIN_DEMO_*`) |
| `flask seed-demo` | Reconstruye el conjunto de datos demo completo (usuarios, semilleros, proyectos, productos, eventos, convocatoria, logros con XP, reportes, comentarios, etc.) |

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

Sin `uv` instalado, corre la suite con Docker (la imagen de la app no incluye pytest):

```bash
docker compose --profile test run --rm tests            # toda la suite (~4 min)
docker compose --profile test run --rm tests uv run pytest -q tests/test_data_model.py
```

El servicio `tests` monta `./backend`, guarda el entorno virtual en el volumen `riul_venv` y usa la base `riul_test` del contenedor `db`.

Las pruebas usan la base `riul_test` (se crea sola) y cubren auth, feed, administración,
semilleros, proyectos, eventos y convocatorias, notificaciones, gamificación, perfil, reportes, esquemas,
el contrato del modelo de datos (`test_data_model.py`: CHECKs, pipeline de XP, privacidad de evidencias) y
las migraciones (`test_migrations.py`: upgrade → comparación con los modelos → downgrade → upgrade).

## Configuración

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Conexión SQLAlchemy a MySQL |
| `SECRET_KEY` · `JWT_SECRET_KEY` | Secretos (obligatorios y distintos del valor de desarrollo en `prod`) |
| `INSTITUTIONAL_EMAIL_DOMAIN` | Dominio con registro inmediato (`unilibre.edu.co`) |
| `CORS_ORIGINS` | Orígenes permitidos separados por coma; `*` solo en desarrollo |
| `UPLOAD_FOLDER` | Carpeta de adjuntos del feed y evidencias (volumen `uploads_data` en Docker) |
| `SEED_DEMO` | `1` (defecto) siembra el dataset demo al arrancar el contenedor; `0` solo catálogos |
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
