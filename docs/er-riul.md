# RIUL — esquema entidad-relación por dominio

Fuente de verdad de las tablas **implementadas**: [`backend/migrations/versions/`](../backend/migrations/versions/) (revisiones `0001`, `0002` y `0003`). Motor: MySQL 8.4.

`semilleros` y `semillero_members` están implementadas en MySQL mediante la revisión `0002` y se consultan por la API. Las entidades aún planificadas salen de `unavailable` en el overview de admin (`projects`, `events`, `achievements`, `reports`); no existen en MySQL.

Diagrama principal en Draw.io: [`docs/er-riul.drawio`](er-riul.drawio). Abrir en [app.diagrams.net](https://app.diagrams.net/) o en VS Code / Cursor con la extensión Draw.io. Cada dominio es un recuadro **transparente** con título (`Dominio 1 — Identidad y acceso (auth)`, etc.); el color de dominio va en el encabezado de cada tabla.

Copia Lucidchart (se parte al agrupar): [editar](https://lucid.app/lucidchart/7cb95ea3-6ab7-4ddb-8d58-2dca05520ea0/edit) · [ver](https://lucid.app/lucidchart/7cb95ea3-6ab7-4ddb-8d58-2dca05520ea0/view).

Este archivo también sirve para dbdiagram.io (pegar DBML más abajo).

## Leyenda de color

Relaciones **cruzadas** (autor, reacciones, FKs académicas) se dibujan en gris `#94A3B8`; no usan el color del dominio destino. Recuadros punteados = dominio aún no migrado a MySQL.

| Dominio | Color | Estado | Tablas |
| --- | --- | --- | --- |
| 1 Identidad y acceso (auth) | carmesí RIUL `#7B001F` | implementado | `users` |
| 2 Catálogo académico | azul `#2563EB` | implementado | `faculties`, `programs` |
| 3 Feed / publicaciones | verde azulado `#0F766E` | implementado | `posts`, `post_attachments`, `post_reactions` |
| 4 Semilleros | morado `#7C3AED` | implementado | `semilleros`, `semillero_members` |
| 5 Proyectos | verde `#15803D` | planificado | `projects` (stub) |
| 6 Eventos | ámbar `#D97706` | planificado | `events` (stub) |
| 7 Gamificación | naranja `#EA580C` | planificado | `achievements` (stub) |
| 8 Reportes | gris `#64748B` | planificado | `reports` (stub) |

## Diagrama Mermaid

El `.drawio` ya trae color de tabla + ventana de dominio. Stubs: borde y recuadro punteados. Enlaces `users` → stubs: línea punteada gris (aún no hay FK).

```mermaid
erDiagram
  faculties ||--o{ programs : tiene
  faculties ||--o{ users : opcional
  programs ||--o{ users : opcional
  users ||--o{ posts : escribe
  users ||--o{ post_reactions : reacciona
  posts ||--o{ post_attachments : tiene
  posts ||--o{ post_reactions : recibe
  faculties ||--o{ semilleros : "adscribe"
  programs ||--o{ semilleros : "adscribe"
  users o|--o{ semilleros : "lidera"
  semilleros ||--o{ semillero_members : "tiene"
  users ||--o{ semillero_members : "participa"
  users }o..o{ projects : "planificado participa"
  users }o..o{ events : "planificado asiste"
  users }o..o{ achievements : "planificado obtiene"
  users }o..o{ reports : "planificado genera"

  faculties {
    int id PK
    string name UK
  }
  programs {
    int id PK
    string name
    int faculty_id FK
  }
  users {
    int id PK
    string full_name
    string email UK
    string password_hash
    string role
    string status
    string motivation
    int faculty_id FK
    int program_id FK
    datetime created_at
  }
  posts {
    int id PK
    int author_id FK
    string category
    text content
    string link_url
    datetime created_at
  }
  post_attachments {
    int id PK
    int post_id FK
    string kind
    string file_name
    string storage_name UK
    string mime_type
    int file_size
  }
  post_reactions {
    int id PK
    int post_id FK
    int user_id FK
    datetime created_at
  }
  semilleros {
    int id PK
    string slug UK
    string name
    text description
    string area
    text mission
    text vision
    int faculty_id FK
    int program_id FK
    int leader_id FK
    datetime created_at
  }
  semillero_members {
    int id PK
    int semillero_id FK
    int user_id FK
    string role_in_semillero
    datetime joined_at
  }
  projects {
    int id PK
    string nombre
  }
  events {
    int id PK
    string nombre
  }
  achievements {
    int id PK
    string nombre
  }
  reports {
    int id PK
    string nombre
  }
```

## Restricciones y enumeraciones (implementado)

Copiado de la migración y de los modelos SQLAlchemy.

### Claves foráneas

Reglas de borrado a nivel de base de datos (migración `0003`).

| Tabla | Columna | Referencia | ON DELETE |
| --- | --- | --- | --- |
| `programs` | `faculty_id` NOT NULL | `faculties.id` | CASCADE |
| `users` | `faculty_id` NULL | `faculties.id` | SET NULL |
| `users` | `program_id` NULL | `programs.id` | SET NULL |
| `posts` | `author_id` NOT NULL | `users.id` | CASCADE |
| `post_attachments` | `post_id` NOT NULL | `posts.id` | CASCADE |
| `post_reactions` | `post_id` NOT NULL | `posts.id` | CASCADE |
| `post_reactions` | `user_id` NOT NULL | `users.id` | CASCADE |
| `semilleros` | `faculty_id` NULL | `faculties.id` | SET NULL |
| `semilleros` | `program_id` NULL | `programs.id` | SET NULL |
| `semilleros` | `leader_id` NULL | `users.id` | SET NULL |
| `semillero_members` | `semillero_id` NOT NULL | `semilleros.id` | CASCADE |
| `semillero_members` | `user_id` NOT NULL | `users.id` | CASCADE |

### Uniques e índices

| Tabla | Restricción |
| --- | --- |
| `faculties` | UNIQUE `name` |
| `programs` | UNIQUE `(name, faculty_id)` |
| `users` | UNIQUE INDEX `ix_users_email` (`email`) |
| `post_attachments` | UNIQUE `storage_name` |
| `post_reactions` | UNIQUE `(post_id, user_id)` |
| `semilleros` | UNIQUE INDEX `ix_semilleros_slug` (`slug`) |
| `semillero_members` | UNIQUE `(semillero_id, user_id)` |

### Valores de enumeración (validados con CHECK en MySQL, migración `0003`)

| Columna | Valores | CHECK |
| --- | --- | --- |
| `users.role` | `researcher` \| `leader` \| `administrator` (default `researcher`) | `ck_users_role` |
| `users.status` | `active` \| `pending` \| `rejected` (default `active`) | `ck_users_status` |
| `posts.category` | `article` \| `project_advance` \| `presentation` \| `event` \| `community` (default `community`) | `ck_posts_category` |
| `post_attachments.kind` | `image` \| `file` | `ck_post_attachments_kind` |

`created_at` en `users`, `posts`, `post_reactions` y `semilleros`, y `joined_at` en `semillero_members`: `DATETIME` con `DEFAULT CURRENT_TIMESTAMP`.

## DBML

Importable en [dbdiagram.io](https://dbdiagram.io). Los `Note` marcan color y estado. Stubs sin `Ref` hacia `users`.

```dbml
Project riul {
  database_type: 'MySQL'
  Note: 'Implementado = migraciones 0001, 0002 y 0003. Stubs = overview admin unavailable.'
}

TableGroup catalogo_academico [color: #2563EB] {
  faculties
  programs
}

TableGroup identidad_acceso [color: #7B001F] {
  users
}

TableGroup feed_publicaciones [color: #0F766E] {
  posts
  post_attachments
  post_reactions
}

TableGroup semilleros [color: #7C3AED] {
  semilleros
  semillero_members
}

TableGroup proyectos_planificado [color: #15803D] {
  projects
}

TableGroup eventos_planificado [color: #D97706] {
  events
}

TableGroup gamificacion_planificado [color: #EA580C] {
  achievements
}

TableGroup reportes_planificado [color: #64748B] {
  reports
}

Table faculties {
  id int [pk, increment]
  name varchar(120) [unique, not null]

  Note: 'Dominio catálogo #2563EB — implementado'
}

Table programs {
  id int [pk, increment]
  name varchar(120) [not null]
  faculty_id int [not null]

  indexes {
    (name, faculty_id) [unique]
  }

  Note: 'Dominio catálogo #2563EB — implementado'
}

Table users {
  id int [pk, increment]
  full_name varchar(160)
  email varchar(255) [unique, not null]
  password_hash varchar(255) [not null]
  role varchar(20) [not null, default: 'researcher', note: 'researcher | leader | administrator']
  status varchar(20) [not null, default: 'active', note: 'active | pending | rejected']
  motivation varchar(500)
  faculty_id int
  program_id int
  created_at datetime [not null, default: `CURRENT_TIMESTAMP`]

  Note: 'Dominio identidad #7B001F — implementado'
}

Table posts {
  id int [pk, increment]
  author_id int [not null]
  category varchar(30) [not null, default: 'community', note: 'article | project_advance | presentation | event | community']
  content text
  link_url varchar(500)
  created_at datetime [not null, default: `CURRENT_TIMESTAMP`]

  Note: 'Dominio feed #0F766E — implementado'
}

Table post_attachments {
  id int [pk, increment]
  post_id int [not null]
  kind varchar(10) [not null, note: 'image | file']
  file_name varchar(255) [not null]
  storage_name varchar(120) [unique, not null]
  mime_type varchar(100)
  file_size int

  Note: 'Dominio feed #0F766E — implementado'
}

Table post_reactions {
  id int [pk, increment]
  post_id int [not null]
  user_id int [not null]
  created_at datetime [not null, default: `CURRENT_TIMESTAMP`]

  indexes {
    (post_id, user_id) [unique]
  }

  Note: 'Dominio feed #0F766E — implementado'
}

Table semilleros {
  id int [pk, increment]
  slug varchar(50) [unique, not null]
  name varchar(200) [not null]
  description text
  area varchar(100)
  mission text
  vision text
  faculty_id int
  program_id int
  leader_id int
  created_at datetime [not null, default: `CURRENT_TIMESTAMP`]

  Note: 'Dominio semilleros #7C3AED — implementado'
}

Table semillero_members {
  id int [pk, increment]
  semillero_id int [not null]
  user_id int [not null]
  role_in_semillero varchar(50) [not null, default: 'Estudiante Investigador']
  joined_at datetime [not null, default: `CURRENT_TIMESTAMP`]

  indexes {
    (semillero_id, user_id) [unique]
  }

  Note: 'Dominio semilleros #7C3AED — implementado'
}

Table projects {
  id int [pk]
  nombre varchar [note: 'stub']

  Note: 'Planificado #15803D — no hay tabla en MySQL'
}

Table events {
  id int [pk]
  nombre varchar [note: 'stub']

  Note: 'Planificado #D97706 — no hay tabla en MySQL'
}

Table achievements {
  id int [pk]
  nombre varchar [note: 'stub']

  Note: 'Planificado #EA580C — no hay tabla en MySQL'
}

Table reports {
  id int [pk]
  nombre varchar [note: 'stub']

  Note: 'Planificado #64748B — no hay tabla en MySQL'
}

Ref: programs.faculty_id > faculties.id [delete: cascade]
Ref: users.faculty_id > faculties.id [delete: set null]
Ref: users.program_id > programs.id [delete: set null]
Ref: posts.author_id > users.id [delete: cascade]
Ref: post_attachments.post_id > posts.id [delete: cascade]
Ref: post_reactions.post_id > posts.id [delete: cascade]
Ref: post_reactions.user_id > users.id [delete: cascade]
Ref: semilleros.faculty_id > faculties.id [delete: set null]
Ref: semilleros.program_id > programs.id [delete: set null]
Ref: semilleros.leader_id > users.id [delete: set null]
Ref: semillero_members.semillero_id > semilleros.id [delete: cascade]
Ref: semillero_members.user_id > users.id [delete: cascade]
```

## Cómo usarlo después

1. **Draw.io**: Arrange → Insert → Advanced → Mermaid, pegar el bloque `erDiagram`. Colorear grupos a mano con los hex.
2. **dbdiagram.io**: New diagram → pegar el DBML. Los `TableGroup` ya llevan color.
3. **Lucidchart**: el documento ya existe (enlace al inicio de este archivo). Stubs van con borde punteado; FKs reales en gris `#94A3B8`.
