# RIUL — Modelo de datos y conjunto de datos sembrado

Referencia del esquema completo (34 tablas en 8 dominios, MySQL 8.4) y del paquete de datos de demostración
que carga `flask seed-demo`. Diagrama y restricciones: [`er-riul.md`](er-riul.md).

- Migraciones: `backend/migrations/versions/0001` … `0004_complete_data_model.py`
- Fuente única del seed: `backend/app/seed_data.py` (orquestación en `backend/app/services/seed_service.py`)
- Comandos: `flask seed-db` (catálogos y datos de referencia), `flask seed-demo` (dataset demo completo)

---

## 1. Esquema de la base de datos

### 1.1 Dominio 1 — Identidad y acceso

#### `users`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `full_name` | varchar(160) | NULL |
| `email` | varchar(255) | NOT NULL, UNIQUE |
| `password_hash` | varchar(255) | NOT NULL |
| `role` | varchar(20) | NOT NULL, default `researcher` |
| `status` | varchar(20) | NOT NULL, default `active` |
| `motivation` | varchar(500) | NULL |
| `faculty_id` | integer | NULL, FK → `faculties.id` |
| `program_id` | integer | NULL, FK → `programs.id` |
| `created_at` | datetime | NOT NULL, default `now()` |

#### `user_profiles`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, UNIQUE, FK → `users.id` ON DELETE CASCADE |
| `bio` | text | NULL |
| `photo` | varchar(255) | NULL |
| `orcid` | varchar(19) | NULL |

### 1.2 Dominio 2 — Catálogo académico

#### `faculties`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `name` | varchar(120) | NOT NULL, UNIQUE |

#### `programs`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `name` | varchar(120) | NOT NULL |
| `faculty_id` | integer | NOT NULL, FK → `faculties.id` |
| — | — | UNIQUE (`name`, `faculty_id`) |

### 1.3 Dominio 3 — Feed / publicaciones

#### `posts`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `category` | varchar(30) | NOT NULL, default `community` |
| `content` | text | NULL |
| `link_url` | varchar(500) | NULL |
| `created_at` | datetime | NOT NULL, default `now()` |

#### `post_attachments`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `post_id` | integer | NOT NULL, FK → `posts.id` |
| `kind` | varchar(10) | NOT NULL |
| `file_name` | varchar(255) | NOT NULL |
| `storage_name` | varchar(120) | NOT NULL, UNIQUE |
| `mime_type` | varchar(100) | NULL |
| `file_size` | integer | NULL |

#### `post_reactions`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `post_id` | integer | NOT NULL, FK → `posts.id` |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | UNIQUE (`post_id`, `user_id`) |

#### `comments`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `post_id` | integer | NOT NULL, FK → `posts.id` ON DELETE CASCADE |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `body` | text | NOT NULL |
| `created_at` | datetime | NOT NULL, default `now()` |

#### `post_shares`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `post_id` | integer | NOT NULL, FK → `posts.id` ON DELETE CASCADE |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | UNIQUE (`post_id`, `user_id`) |

### 1.4 Dominio 4 — Semilleros

#### `semilleros`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `slug` | varchar(80) | NOT NULL, UNIQUE |
| `name` | varchar(160) | NOT NULL |
| `area` | varchar(120) | NULL |
| `description` | text | NULL |
| `icon` | varchar(40) | NOT NULL, default `science` |
| `top_badge` | varchar(40) | NULL |
| `faculty_id` | integer | NOT NULL, FK → `faculties.id` |
| `program_id` | integer | NULL, FK → `programs.id` |
| `leader_id` | integer | NOT NULL, FK → `users.id` |
| `leader_title` | varchar(160) | NULL |
| `affiliation` | varchar(255) | NULL |
| `about` | text | NULL |
| `mission` | text | NULL |
| `vision` | text | NULL |
| `interest_areas` | json | NOT NULL |
| `created_at` | datetime | NOT NULL, default `now()` |

#### `semillero_members`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `semillero_id` | integer | NOT NULL, FK → `semilleros.id` |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `role` | varchar(20) | NOT NULL, default `member` |
| `status` | varchar(20) | NOT NULL, default `pending` |
| `approved_by` | integer | NULL, FK → `users.id` |
| `joined_at` | datetime | NOT NULL, default `now()` |
| — | — | UNIQUE (`semillero_id`, `user_id`) |
| — | — | CHECK `role IN ('leader','co_leader','member')` |
| — | — | CHECK `status IN ('pending','active','rejected')` |

#### `semillero_research_lines`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `semillero_id` | integer | NOT NULL, FK → `semilleros.id` |
| `name` | varchar(160) | NOT NULL |
| `icon` | varchar(40) | NOT NULL, default `science` |
| `coordinator` | varchar(160) | NULL |

#### `semillero_activities`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `semillero_id` | integer | NOT NULL, FK → `semilleros.id` |
| `title` | varchar(160) | NOT NULL |
| `place` | varchar(200) | NULL |
| `occurred_on` | date | NOT NULL |

#### `semillero_follows`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `semillero_id` | integer | NOT NULL, FK → `semilleros.id` |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | UNIQUE (`semillero_id`, `user_id`) |

#### `semillero_progress`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `semillero_id` | integer | NOT NULL, UNIQUE, FK → `semilleros.id` |
| `level_id` | integer | NOT NULL, FK → `levels.id` |
| `xp` | integer | NOT NULL, default `0` |

### 1.5 Dominio 5 — Proyectos y productos

#### `projects`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `slug` | varchar(100) | NOT NULL, UNIQUE |
| `title` | varchar(200) | NOT NULL |
| `type` | varchar(60) | NULL |
| `status` | varchar(20) | NOT NULL, default `planned` |
| `description` | text | NULL |
| `progress` | integer | NOT NULL, default `0` |
| `line` | varchar(120) | NULL |
| `role_required` | varchar(160) | NULL |
| `start_date` | date | NULL |
| `end_date` | date | NULL |
| `semillero_id` | integer | NULL, FK → `semilleros.id` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | CHECK `progress BETWEEN 0 AND 100` |
| — | — | CHECK `status IN ('planned','in_progress','review','closed')` |

#### `project_members`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `project_id` | integer | NOT NULL, FK → `projects.id` |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `role` | varchar(20) | NOT NULL, default `member` |
| — | — | UNIQUE (`project_id`, `user_id`) |
| — | — | CHECK `role IN ('principal','member')` |

#### `project_milestones`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `project_id` | integer | NOT NULL, FK → `projects.id` |
| `title` | varchar(200) | NOT NULL |
| `done` | boolean | NOT NULL, default `0` |
| `position` | integer | NOT NULL, default `0` |

#### `products`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `project_id` | integer | NULL, FK → `projects.id` |
| `semillero_id` | integer | NULL, FK → `semilleros.id` |
| `type` | varchar(20) | NOT NULL |
| `title` | varchar(250) | NOT NULL |
| `venue` | varchar(160) | NULL |
| `published_on` | date | NULL |
| `status` | varchar(20) | NOT NULL, default `in_review` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | CHECK `status IN ('in_review','approved')` |
| — | — | CHECK `type IN ('article','presentation','patent','report')` |

### 1.6 Dominio 6 — Eventos y convocatorias

#### `events`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `slug` | varchar(100) | NOT NULL, UNIQUE |
| `title` | varchar(200) | NOT NULL |
| `description` | text | NULL |
| `type` | varchar(60) | NULL |
| `status` | varchar(10) | NOT NULL, default `open` |
| `starts_at` | datetime | NOT NULL |
| `ends_at` | datetime | NOT NULL |
| `location` | varchar(160) | NULL |
| `capacity` | integer | NULL |
| `organizer` | varchar(160) | NULL |
| `requirements` | json | NOT NULL |
| `semillero_id` | integer | NULL, FK → `semilleros.id` |
| `created_by` | integer | NULL, FK → `users.id` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | CHECK `ends_at >= starts_at` |
| — | — | CHECK `status IN ('open','closed')` |

#### `event_participations`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `event_id` | integer | NOT NULL, FK → `events.id` |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `role` | varchar(20) | NOT NULL, default `attendee` |
| `status` | varchar(20) | NOT NULL, default `registered` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | UNIQUE (`event_id`, `user_id`) |
| — | — | CHECK `role IN ('attendee','speaker','organizer')` |
| — | — | CHECK `status IN ('available','registered','pending','closed')` |

#### `calls`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `slug` | varchar(100) | NOT NULL, UNIQUE |
| `title` | varchar(200) | NOT NULL |
| `description` | text | NULL |
| `type` | varchar(60) | NULL |
| `status` | varchar(10) | NOT NULL, default `open` |
| `starts_at` | datetime | NOT NULL |
| `ends_at` | datetime | NOT NULL |
| `location` | varchar(160) | NULL |
| `organizer` | varchar(160) | NULL |
| `requirements` | json | NOT NULL |
| `published_by` | integer | NOT NULL, FK → `users.id` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | CHECK `status IN ('open','closed')` |
| — | — | CHECK `ends_at >= starts_at` |

#### `call_applications`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `call_id` | integer | NOT NULL, FK → `calls.id` |
| `user_id` | integer | NULL, FK → `users.id` |
| `semillero_id` | integer | NULL, FK → `semilleros.id` |
| `status` | varchar(20) | NOT NULL, default `pending` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | UNIQUE (`call_id`, `semillero_id`) |
| — | — | UNIQUE (`call_id`, `user_id`) |
| — | — | CHECK `status IN ('pending','accepted','rejected')` |
| — | — | CHECK `(user_id IS NOT NULL AND semillero_id IS NULL) OR (user_id IS NULL AND semillero_id IS NOT NULL)` |

### 1.7 Dominio 7 — Gamificación

#### `levels`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `level_number` | integer | NOT NULL, UNIQUE |
| `min_xp` | integer | NOT NULL |
| `stars` | integer | NOT NULL |
| — | — | CHECK `stars BETWEEN 1 AND 5` |

#### `badges`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `name` | varchar(120) | NOT NULL, UNIQUE |
| `description` | varchar(255) | NULL |
| `icon` | varchar(40) | NOT NULL, default `military_tech` |

#### `achievement_types`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `code` | varchar(20) | NOT NULL, UNIQUE |
| `name` | varchar(120) | NOT NULL |
| `icon` | varchar(40) | NOT NULL, default `military_tech` |
| `xp_value` | integer | NOT NULL, default `0` |
| `badge_id` | integer | NULL, FK → `badges.id` |
| — | — | CHECK `code IN ('event','post','project','article','presentation','patent','semillero')` |

#### `achievements`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `type_id` | integer | NOT NULL, FK → `achievement_types.id` |
| `status` | varchar(20) | NOT NULL, default `pending` |
| `validated_by` | integer | NULL, FK → `users.id` |
| `validated_at` | datetime | NULL |
| `event_id` | integer | NULL, FK → `events.id` |
| `post_id` | integer | NULL, FK → `posts.id` |
| `project_id` | integer | NULL, FK → `projects.id` |
| `product_id` | integer | NULL, FK → `products.id` |
| `semillero_id` | integer | NULL, FK → `semilleros.id` |
| `xp_semillero_id` | integer | NULL, FK → `semilleros.id` |
| `title` | varchar(160) | NULL |
| `description` | text | NULL |
| `achieved_on` | date | NOT NULL |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | CHECK `status IN ('pending','approved','rejected')` |
| — | — | CHECK `(event_id IS NOT NULL) + (post_id IS NOT NULL) + (project_id IS NOT NULL) + (product_id IS NOT NULL) + (semillero_id IS NOT NULL) = 1` |

#### `evidences`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `achievement_id` | integer | NOT NULL, FK → `achievements.id` ON DELETE CASCADE |
| `file_name` | varchar(255) | NOT NULL |
| `storage_name` | varchar(120) | NOT NULL, UNIQUE |
| `mime_type` | varchar(100) | NULL |
| `file_size` | integer | NULL |
| `created_at` | datetime | NOT NULL, default `now()` |

#### `xp_ledger`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `achievement_id` | integer | NOT NULL, UNIQUE, FK → `achievements.id` |
| `amount` | integer | NOT NULL |
| `created_at` | datetime | NOT NULL, default `now()` |

#### `user_progress`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, UNIQUE, FK → `users.id` |
| `xp` | integer | NOT NULL, default `0` |
| `level_id` | integer | NOT NULL, FK → `levels.id` |
| `stars` | integer | NOT NULL, default `1` |
| — | — | CHECK `stars BETWEEN 1 AND 5` |

#### `user_badges`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `badge_id` | integer | NOT NULL, FK → `badges.id` |
| `achievement_id` | integer | NOT NULL, FK → `achievements.id` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | UNIQUE (`user_id`, `badge_id`) |

### 1.8 Dominio 8 — Notificaciones, soporte y reportes

#### `notifications`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `type` | varchar(20) | NOT NULL |
| `entity_kind` | varchar(30) | NULL |
| `entity_id` | integer | NULL |
| `title` | varchar(160) | NOT NULL |
| `text` | varchar(500) | NOT NULL |
| `priority` | varchar(10) | NOT NULL, default `normal` |
| `href` | varchar(200) | NULL |
| `read_at` | datetime | NULL |
| `created_at` | datetime | NOT NULL, default `now()` |

#### `support_tickets`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `category` | varchar(30) | NOT NULL |
| `subject` | varchar(160) | NOT NULL |
| `message` | text | NOT NULL |
| `status` | varchar(20) | NOT NULL, default `open` |
| `admin_reply` | text | NULL |
| `replied_at` | datetime | NULL |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | CHECK `status IN ('open','in_progress','resolved')` |

#### `report_snapshots`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `generated_by` | integer | NOT NULL, FK → `users.id` |
| `kind` | varchar(10) | NOT NULL |
| `period_start` | date | NOT NULL |
| `period_end` | date | NOT NULL |
| `published_at` | datetime | NULL |
| `metrics_json` | json | NOT NULL |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | CHECK `period_end >= period_start` |
| — | — | CHECK `kind IN ('report','ranking')` |

### 1.9 Enumeraciones de aplicación

| Campo | Valores |
|-------|---------|
| `users.role` | `researcher`, `leader`, `administrator` |
| `users.status` | `active`, `pending`, `rejected` |
| `posts.category` | `community`, `article`, `project_advance`, `presentation`, `event` |
| `post_attachments.kind` | `image`, `file` |
| `semillero_members.role` | `leader`, `co_leader`, `member` |
| `semillero_members.status` | `pending`, `active`, `rejected` |
| `projects.status` | `planned`, `in_progress`, `review`, `closed` |
| `project_members.role` | `principal`, `member` (la API expone al principal como `leader`) |
| `events.status` / `calls.status` | `open`, `closed` (el estado efectivo pasa a `closed` al vencer `ends_at`) |
| `event_participations.role` | `attendee`, `speaker`, `organizer` |
| `event_participations.status` | `available`, `registered`, `pending`, `closed` |
| `products.type` | `article`, `presentation`, `patent`, `report` |
| `products.status` | `in_review`, `approved` |
| `call_applications.status` | `pending`, `accepted`, `rejected` |
| `achievements.status` | `pending`, `approved`, `rejected` |
| `achievement_types.code` | `event`, `post`, `project`, `article`, `presentation`, `patent`, `semillero` |
| `report_snapshots.kind` | `report`, `ranking` |

### 1.10 Pipeline de XP

```
achievement (origen único) --aprobación--> xp_ledger --> user_progress (nivel)
                                                     \-> user_badges (insignias por umbral)
                                                     \-> semillero_progress (vía xp_semillero_id / origen)
```

Solo los logros `approved` suman XP; el XP base viene de `achievement_types` y administración puede sobrescribirlo
al aprobar. Las evidencias (`evidences`) son archivos privados: solo las ve su dueño o un administrador.

---

## 2. Conjunto de datos sembrado (`flask seed-demo`)

El comando **purga** los datos de negocio (todas las tablas salvo los catálogos `faculties`, `programs`, `levels`,
`badges` y `achievement_types`, que se upsertan) y reconstruye el paquete completo. Es idempotente.
Resultado verificado: **15 usuarios, 15 publicaciones, 47 reacciones, 7 comentarios, 6 compartidos, 6 semilleros
(8 seguidores), 7 proyectos, 11 productos, 3 eventos (7 participaciones), 1 convocatoria (3 postulaciones),
10 logros, 6 notificaciones y 2 reportes.** El XP de los logros aprobados pasa por el libro mayor, de modo que
niveles, insignias y progreso de semilleros son coherentes con el ledger.

### 2.1 Facultades y programas

| Facultad | Programas |
|----------|-----------|
| Ingeniería | Ingeniería de Sistemas, Ingeniería Industrial, Ingeniería Estadística, Ingeniería Mecánica |
| Ciencias Básicas | Biología |
| Ciencias Sociales | Comunicación Social |

### 2.2 Usuarios (15)

Contraseña común: valor de `DEMO_USERS_PASSWORD` (default `RiulDemo2026*`).
Los pendientes/rechazados usan correos externos y su login queda bloqueado.

| # | Nombre | Email | Rol | Estado | Facultad / Programa | Relación |
|---|--------|-------|-----|--------|----------------------|----------|
| 1 | Ana Sofía Restrepo | ana.restrepo@unilibre.edu.co | administrator | active | — | — |
| 2 | Leonardo Pardo Roa | leonardo.pardo@unilibre.edu.co | administrator | active | — | — |
| 3 | Laura Mendoza | laura.mendoza@unilibre.edu.co | leader | active | Ingeniería / Sistemas | Guía a Camila, Andrés |
| 4 | María Antonieta Pérez | maria.antonieta.perez@unilibre.edu.co | leader | active | Ingeniería / Sistemas | Guía a Luis, Carolina |
| 5 | Mateo Silva | mateo.silva@unilibre.edu.co | leader | active | Ingeniería / Industrial | Guía a Diego, Paula |
| 6 | Javier Torres | javier.torres@unilibre.edu.co | leader | active | Ciencias Básicas / Biología | Guía a Sofía |
| 7 | Camila Rojas | camila.rojas@unilibre.edu.co | researcher | active | Ingeniería / Sistemas | Equipo de Laura M. |
| 8 | Andrés Pérez | andres.perez@unilibre.edu.co | researcher | active | Ingeniería / Sistemas | Equipo de Laura M. |
| 9 | Luis Grandett | luis.grandett@unilibre.edu.co | researcher | active | Ingeniería / Sistemas | Equipo de M. Antonieta |
| 10 | Carolina Martínez | carolina.martinez@unilibre.edu.co | researcher | active | Ingeniería / Sistemas | Equipo de M. Antonieta |
| 11 | Diego Gutiérrez | diego.gutierrez@unilibre.edu.co | researcher | active | Ingeniería / Industrial | Equipo de Mateo |
| 12 | Paula Fernández | paula.fernandez@unilibre.edu.co | researcher | active | Ingeniería / Industrial | Equipo de Mateo |
| 13 | Sofía Díaz | sofia.diaz@unilibre.edu.co | researcher | active | Ciencias Básicas / Biología | Equipo de Javier |
| 14 | Isabela Blanco | isabela.blanco@gmail.com | researcher | **pending** | Ciencias Básicas / Biología | Solicitud externa |
| 15 | Tomás Restrepo | tomas.restrepo@hotmail.com | researcher | **rejected** | Ingeniería / Sistemas | Solicitud externa |

Distribución: *role* → administrator 2, leader 4, researcher 9. *status* → active 13, pending 1, rejected 1.

### 2.3 Publicaciones (15)

| # | Autor | Categoría | Resumen | Enlace |
|---|-------|-----------|---------|--------|
| 1 | Laura Mendoza | `event` | V Simposio Internacional de Investigación — inscripciones | sí |
| 2 | Laura Mendoza | `project_advance` | Modelo predictivo de rendimiento académico: 87% precisión | — |
| 3 | Camila Rojas | `event` | Taller de datos abiertos para investigadores (4 dic) | — |
| 4 | Camila Rojas | `article` | Publicación "Optimización de Modelos Predictivos" | sí |
| 5 | Andrés Pérez | `community` | Convocatoria para validar el modelo con la comunidad | — |
| 6 | María Antonieta Pérez | `community` | Bienvenida al Semillero ITA — cupos abiertos | — |
| 7 | María Antonieta Pérez | `article` | "Low-cost IoT Sensors for Tomato Crops" (IEEE) | sí |
| 8 | Luis Grandett | `project_advance` | Ciberseguridad en redes académicas: detección de anomalías | — |
| 9 | Carolina Martínez | `community` | Memoria del taller práctico de sensores ESP32 | — |
| 10 | Mateo Silva | `project_advance` | Sensores IoT campus: arquitectura de red aprobada | — |
| 11 | Diego Gutiérrez | `presentation` | Ponencia del Proyecto C en Encuentro de Innovación | sí |
| 12 | Paula Fernández | `community` | Bitácora del muestreo energético del campus | — |
| 13 | Javier Torres | `presentation` | Ponencia "Redes interpretables en educación" (CCC) | sí |
| 14 | Sofía Díaz | `project_advance` | Prototipo inicial del modelo de redes neuronales | — |
| 15 | Ana Sofía Restrepo | `community` | Lineamientos de publicación en la comunidad RIUL | — |

Fechas escalonadas entre 2026-08-29 y 2026-09-12 (orden de feed realista).

### 2.4 Dominio de investigación

6 semilleros (con líneas, actividades, miembros activos y pendientes, seguidores y progreso), 7 proyectos con
integrantes, hitos y productos, 11 productos (artículos, ponencias y patentes) y 3 eventos con participaciones.

### 2.5 Gamificación, convocatorias y reportes

- 10 logros (aprobados, pendientes y rechazados), cada uno con un único origen; los aprobados generan filas en `xp_ledger`.
- 1 convocatoria (*Convocatoria de fortalecimiento a semilleros 2027*) con 3 postulaciones: dos de semilleros (una aceptada, una pendiente) y una de persona.
- 2 reportes (`report`, `ranking`) generados con `report_service`; uno publicado.

### 2.6 Reacciones (47)

Solo reaccionan usuarios **relacionados** con el autor (equipo, líder y admins).

| Post | Quién reacciona |
|------|-----------------|
| 1 (Laura, simposio) | Camila, Andrés, Luis, Carolina |
| 2 (Laura, avance) | Camila, Andrés, Javier |
| 3 (Camila, taller) | Laura, Andrés, Sofía |
| 4 (Camila, artículo) | Laura, Andrés, Luis, Ana Restrepo |
| 5 (Andrés, convocatoria) | Camila, Laura, Sofía |
| 6 (M. Antonieta, ITA) | Luis, Carolina, Ana Restrepo |
| 7 (M. Antonieta, artículo) | Luis, Carolina, Mateo |
| 8 (Luis, ciberseguridad) | Carolina, M. Antonieta, Laura |
| 9 (Carolina, ESP32) | Luis, M. Antonieta, Diego |
| 10 (Mateo, arquitectura) | Diego, Paula, Laura |
| 11 (Diego, ponencia) | Paula, Mateo, Luis |
| 12 (Paula, bitácora) | Diego, Mateo, Carolina |
| 13 (Javier, ponencia) | Sofía, Camila, Laura |
| 14 (Sofía, prototipo) | Javier, Camila, Andrés |
| 15 (Ana, lineamientos) | Laura, Leonardo, M. Antonieta |

Nota: Isabela (pending) y Tomás (rejected) no reaccionan ni publican.

---

## 3. Cómo sembrar y verificar

```bash
# Reset y carga completa del paquete demo
docker compose exec app flask seed-demo
# Al iniciar el contenedor se ejecuta: flask db upgrade && flask seed-demo
# (SEED_DEMO=0 en el entorno conserva los datos y solo siembra catálogos con flask seed-db)

# Verificación rápida en MySQL
SELECT role, status, count(*) FROM users GROUP BY role, status;
SELECT count(*) FROM posts;          -- 15
SELECT count(*) FROM post_reactions; -- 47
SELECT status, count(*) FROM achievements GROUP BY status;
SELECT COUNT(*) FROM xp_ledger;      -- uno por logro aprobado
```

Cuentas de prueba:

| Email | Contraseña | Resultado de login |
|-------|-----------|--------------------|
| laura.mendoza@unilibre.edu.co | RiulDemo2026* | 200 (leader) |
| camila.rojas@unilibre.edu.co | RiulDemo2026* | 200 (researcher) |
| ana.restrepo@unilibre.edu.co | RiulDemo2026* | 200 (administrator) |
| isabela.blanco@gmail.com | RiulDemo2026* | 403 "Solicitud pendiente de aprobación" |
| tomas.restrepo@hotmail.com | RiulDemo2026* | 403 "Cuenta no autorizada" |
