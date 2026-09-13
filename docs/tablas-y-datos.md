# RIUL — Modelo de Datos y Conjunto de Datos Sembrado

Documento de referencia del esquema (6 tablas) y del paquete de datos de
demostración que carga el comando `flask seed-demo`.

- Fuente única de verdad del seed: `backend/app/seed_data.py`
- Comando: `flask seed-demo` (reemplaza `seed-db` y `seed-users`)

---

## 1. Esquema de la base de datos (PostgreSQL)

Migraciones: `0001_auth_module_initial_tables` y `0002_posts_module_tables`.

### 1.1 `faculties`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `name` | varchar(120) | NOT NULL, UNIQUE |

### 1.2 `programs`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `name` | varchar(120) | NOT NULL |
| `faculty_id` | integer | NOT NULL, FOREIGN KEY → `faculties.id` |
| — | — | UNIQUE (`name`, `faculty_id`) |

### 1.3 `users`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `full_name` | varchar(160) | NULL |
| `email` | varchar(255) | NOT NULL, UNIQUE, INDEX |
| `password_hash` | varchar(255) | NOT NULL |
| `role` | varchar(20) | NOT NULL, default `researcher` |
| `status` | varchar(20) | NOT NULL, default `active` |
| `motivation` | varchar(500) | NULL |
| `faculty_id` | integer | FK → `faculties.id`, NULL |
| `program_id` | integer | FK → `programs.id`, NULL |
| `created_at` | datetime | NOT NULL, default `now()` |

### 1.4 `posts`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `author_id` | integer | NOT NULL, FK → `users.id` |
| `category` | varchar(30) | NOT NULL, default `community` |
| `content` | text | NULL |
| `link_url` | varchar(500) | NULL |
| `created_at` | datetime | NOT NULL, default `now()` |

### 1.5 `post_attachments`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `post_id` | integer | NOT NULL, FK → `posts.id` |
| `kind` | varchar(10) | NOT NULL (`image` \| `file`) |
| `file_name` | varchar(255) | NOT NULL |
| `storage_name` | varchar(120) | NOT NULL, UNIQUE |
| `mime_type` | varchar(100) | NULL |
| `file_size` | integer | NULL |

### 1.6 `post_reactions`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | integer | PRIMARY KEY |
| `post_id` | integer | NOT NULL, FK → `posts.id` |
| `user_id` | integer | NOT NULL, FK → `users.id` |
| `created_at` | datetime | NOT NULL, default `now()` |
| — | — | UNIQUE (`post_id`, `user_id`) |

### 1.7 Relaciones

- `faculties` 1:N → `programs`
- `users` N:1 → `faculties` (opcional) y N:1 → `programs` (opcional)
- `users` 1:N → `posts` (autor)
- `posts` 1:N → `post_attachments` (borrado en cascada)
- `posts` N:N → `users` a través de `post_reactions` (reacción única por par)

> No existe tabla de relación explícita usuario↔usuario. Las relaciones entre
> usuarios se expresan por **facultad/programa compartidos** (líder que guía a
> investigadores) y por **autoría/reacciones** de publicaciones.

### 1.8 Valores permitidos (enum)

| Campo | Valores |
|-------|---------|
| `users.role` | `researcher`, `leader`, `administrator` |
| `users.status` | `active`, `pending`, `rejected` |
| `posts.category` | `community`, `article`, `project_advance`, `presentation`, `event` |
| `post_attachments.kind` | `image`, `file` |

---

## 2. Conjunto de datos sembrado (`flask seed-demo`)

El comando **purga** `post_reactions`, `post_attachments`, `posts` y `users`
(no toca facultades/programas: los upserta) y reconstruye el paquete completo.
Totales: **2 facultades, 3 programas, 15 usuarios, 15 posts y 47 reacciones.**

### 2.1 Facultades y programas

| Facultad | Programas |
|----------|-----------|
| Ingeniería | Ingeniería de Sistemas, Ingeniería Industrial |
| Ciencias Básicas | Biología |

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

### 2.4 Reacciones (47)

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
# (Al iniciar el contenedor ya se ejecuta: flask db upgrade && flask seed-demo)

# Verificación rápida en consola psql / docker exec
SELECT role, status, count(*) FROM users GROUP BY role, status;
SELECT count(*) FROM posts;          -- 15
SELECT category, count(*) FROM posts GROUP BY category;
SELECT count(*) FROM post_reactions; -- 47
```

Cuentas de prueba:

| Email | Contraseña | Resultado de login |
|-------|-----------|--------------------|
| laura.mendoza@unilibre.edu.co | RiulDemo2026* | 200 (leader) |
| camila.rojas@unilibre.edu.co | RiulDemo2026* | 200 (researcher) |
| ana.restrepo@unilibre.edu.co | RiulDemo2026* | 200 (administrator) |
| isabela.blanco@gmail.com | RiulDemo2026* | 403 "Solicitud pendiente de aprobación" |
| tomas.restrepo@hotmail.com | RiulDemo2026* | 403 "Cuenta no autorizada" |