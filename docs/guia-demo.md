# Guía de demostración RIUL

RIUL (Red Institucional de Semilleros e Investigación) — aplicación web académica para explorar semilleros de investigación, administrar cuentas institucionales y compartir publicaciones.

## 1. Qué es RIUL (resumen)

- **Stack**: Python 3.12, Flask, SQLAlchemy 2, Flask-Migrate/Alembic, Marshmallow, PyMySQL; HTML/CSS/JS nativos; MySQL 8.4; Docker Compose.
- **Arquitectura**: `routes → controllers → services → repositories → models`. Capa persistencia centralizada en `repositories/`. Controladores no acceden directamente a BD, servicios no emiten SQL.
- **Módulos reales (persistidos)**: auth, feed/publicaciones, semilleros, admin de usuarios.
- **Módulos demo (no persistidos)**: proyectos, eventos, gamificación, logros, reportes (rotulados como "datos de demostración").

---

## 2. Explicación por rúbrica

### C1 — Diseño de base de datos (1.50)
- **Tablas**: `faculties`, `programs`, `users`, `posts`, `post_attachments`, `post_reactions`, `semilleros`, `semillero_members` (8).
- **Integridad**: PK/FK, unicidad (`email`, `slug`), `CHECK` en `roles/estado`, `categoría` de post y `kind` de adjunto.
- **ON DELETE**: `CASCADE` en dependientes; `SET NULL` en referencias opcionales (facultad/programa/líder).
- **Migraciones**: `0001`, `0002`, `0003` no destructivas.

### C2 — HTML/CSS (1.50)
- Design system con tokens en `design-system.css`, 17 plantillas, layout responsive.
- Vistas demo con banda "datos de demostración".

### C3 — Estructura (0.75)
- Capas obligatorias respetadas; un solo `alembic.ini` efectivo; contratos con Marshmallow.
- `admin_controller` no importa repositorios; `seed_service` usa repositorios.

### C4 — Docker (0.75)
- Compose: `app` + `db` (MySQL 8.4), healthcheck, volumen `mysql_data`, `restart: unless-stopped`.
- Migraciones + seed no destructivo al arrancar.

### C5 — Coherencia (0.50)
- OpenAPI `/docs` ↔ `/openapi.yaml` coherente con rutas reales.
- Navegación admin: "Semilleros" apunta a `#catalogs` (no `unavailable`).
- Módulos demo claramente diferenciados.

---

## 3. Levantar la app

```bash
docker compose up --build
```

Aplicación: **http://localhost:5000**  
MySQL: puerto **3307** (host) / **3306** interno.

### Credenciales de demostración

Contraseña común: **`RiulDemo2026*`**

| Rol | Correo | Estado | Notas |
|---|---|---|---|
| Administrador | `ana.restrepo@unilibre.edu.co` | activo | Usar para panel admin |
| Administrador | `leonardo.pardo@unilibre.edu.co` | activo | |
| Docente líder | `laura.mendoza@unilibre.edu.co` | activo | Líder DataLab |
| Docente líder | `maria.antonieta.perez@unilibre.edu.co` | activo | Líder ITA |
| Docente líder | `mateo.silva@unilibre.edu.co` | activo | Líder IoT-S |
| Docente líder | `javier.torres@unilibre.edu.co` | activo | Líder BioNeuro |
| Investigador | `camila.rojas@unilibre.edu.co` | activo | Usuario interno |
| Solicitud pendiente | `isabela.blanco@gmail.com` | pending | Login bloqueado |
| Cuenta rechazada | `tomas.restrepo@hotmail.com` | rejected | Login bloqueado |

---

## 4. Flujos a probar visualmente

### 4.1 Portada pública (sin sesión)

1. `/` → Ver hero RIUL + semilleros destacados.
2. Topnav: *Semilleros/Proyectos/Eventos*. Proyecto/Eventos abren; Semilleros redirige a `/login`.
3. Versión móvil: abrir menú ☰ (topnav).

**Espera:** página pública funcional, áreas protegidas exigen login.

### 4.2 Autenticación

| Paso | Acción | Resultado esperado |
|---|---|---|
| 2.1 | `/login` → `ana.restrepo@...` / `RiulDemo2026*` | Entra; aparece nombre/avatar en topnav. |
| 2.2 | Login con contraseña errada | Banner "Credenciales incorrectas." (401). |
| 2.3 | Login `isabela.blanco@gmail.com` + `RiulDemo2026*` | "Solicitud pendiente de aprobación." (403). |
| 2.4 | Login `tomas.restrepo@hotmail.com` | "Su cuenta no está autorizada para acceder." (403). |
| 2.5 | `/register` → pestaña "Registro (Institucional)", correo `@unilibre.edu.co` | Registro exitoso, redirige a app (activo). |
| 2.6 | Registro institucional con `@gmail.com` | Error: requiere correo `@unilibre.edu.co`. |
| 2.7 | Pestaña "Solicitud (No Institucional)" → `@gmail.com` + facultad/programa + motivo | "Solicitud enviada. Estado de validación: Solicitud pendiente de aprobación." (202). |
| 2.8 | Solicitud con `@unilibre.edu.co` | Error: usar registro institucional. |
| 2.9 | `/register` → elegir Facultad → selector de Programa se llena dinámicamente | Catálogo dependiente (`/api/auth/catalog`). |
| 2.10 | Menú usuario → *Cerrar sesión* | Vuelve a `/login`, token eliminado. |
| 2.11 | Borrar `riul_token` de localStorage → recargar `/feed` | Redirige a `/login`. |

### 4.3 Comunidad / Feed (persistido)

| Paso | Acción | Resultado esperado |
|---|---|---|
| 3.1 | `/feed` como usuario activo | 15 posts cargados. Filtro por defecto "Comunidad". |
| 3.2 | Chips: Artículo, Avance de Proyecto, Ponencia, Evento (activo/inhabilita) | Feed se filtra según categoría. |
| 3.3 | Publicar texto | Nueva publicación aparece primero, persiste al recargar. |
| 3.4 | Publicar con imagen | Aparece miniatura de imagen en tarjeta. |
| 3.5 | Publicar con PDF/DOC/PPT/XLS | Tarjeta muestra ícono, nombre y tamaño (enlace descargable). |
| 3.6 | Adjuntar >10MB | "El archivo supera el límite de 10 MB." (413). |
| 3.7 | Dar/quitar reacción | Contador sube/baja; ícono marcado/desmarcado. |
| 3.8 | Compartir | Copia permalink `#post-<id>`; al abrir ese enlace se hace scroll al post. |
| 3.9 | Eliminar propio → confirmar | Post desaparece. No aparece botón borrar en posts ajenos. |
| 3.10 | "Ver más (n)" | Carga más posts (paginación). |
| 3.11 | Permalink `#post-<id>` | Scroll automático al post correspondiente. |

### 4.4 Semilleros (persistido, solo lectura)

| Paso | Acción | Resultado esperado |
|---|---|---|
| 4.1 | `/semilleros` | 4 semilleros; "Mostrando 4 de 4". |
| 4.2 | Buscar: `neuro`, `datos`, `ita` | Filtrado in‑place (acentos/case‑insensitive). |
| 4.3 | Filtros: Facultad, Programa, Área (combinar) | Lista se reduce acorde a criterios. |
| 4.4 | *Limpiar filtros* / buscar inexistente | Vuelve al total; con término inexistente → estado vacío. |
| 4.5 | *Ver Detalle* o clic nombre | Abre detalle: misión, visión, líder, lista de integrantes, botón "Ver Todos (n)". |
| 4.6 | *Solicitar Vinculación* | Navega al detalle con ancla `#vinculacion`. |
| 4.7 | `/semillero-detalle?id=inexistente` | Mensaje "No fue posible cargar este semillero…" (no rompe la UI). |
| 4.8 | "Ver Todos" → "Ver Menos" | Alterna entre 4 y todos los miembros. |

### 4.5 Panel administrativo (solo admin)

| Paso | Acción | Resultado esperado |
|---|---|---|
| 5.1 | Investigador activo → `/admin` | "Acceso restringido. Esta ruta está reservada para administradores activos." (403). |
| 5.2 | Admin → `/admin` | Overview: totales, activos, pendientes, publicaciones, facultades, programas, semilleros. |
| 5.3 | Ver tabla usuarios | Nombre, correo, estado, acciones "Activar/Rechazar". |
| 5.4 | *Activar* usuario `isabela.blanco@gmail.com` | Estado pasa a `active`; botón "Activar" se deshabilita; contador "pendientes" disminuye. |
| 5.5 | *Rechazar* otro usuario | Estado pasa a `rejected`. |
| 5.6 | Sin token → recargar `/admin` | "Sesión requerida" → redirige a `/login`. |

> **Nota**: `isabela.blanco@gmail.com` (solicitud externa) tiene contraseña aleatoria. **Activarla** cambia su estado en BD/UI, pero no podrá iniciar sesión hasta que se le asigne una contraseña (flujo admin no hace reset de password en esta demo).

### 4.6 Dashboard, Perfil y módulos demo

| Paso | Acción | Resultado esperado |
|---|---|---|
| 6.1 | `/dashboard` | Proyectos, publicaciones, notificaciones, estrellas. **Banda "datos de demostración"** visible. |
| 6.2 | `/profile` | Muestra facultad/programa/correo del usuario logueado + métricas demo (gamificación, insignias, logros). Banda demo visible. |
| 6.3 | `/projects` → detalle (`/project-detail?id=proyecto-analisis-datos`) | Listado y detalle demo con hitos/progreso. |
| 6.4 | `/events` → `/event-detail?id=evento-1` | Eventos demo. |
| 6.5 | `/gamification` | Niveles, estrellas, insignias demo. |
| 6.6 | `/notifications` | Notificaciones demo. |
| 6.7 | Navegación lateral | Los ítems demo son funcionales; varios botones con `disabled` son placeholders. |

### 4.7 Extras / API

| Paso | Acción | Resultado esperado |
|---|---|---|
| 7.1 | `/docs` y `/openapi.yaml` | Especificación OpenAPI visible (sirve desde `static/openapi.yaml`). |
| 7.2 | `/styleguide` | Componentes del design system. |
| 7.3 | Responsive: reducir a ~400–640px | Menú móvil, sidebar colapsa correctamente. |
| 7.4 | Red: cortar backend → páginas que hacen fetch | Muestran mensajes controlados (sin 500 crudos). |

---

## 5. Guion recomendado para demo (6–8 min)

1. **(10s)** `/` — introducción: landing público.
2. **(1m)** Login como `ana.restrepo@...` → **Panel admin**. Mostrar métricas reales + tabla.
3. **(30s)** **Aprobar** `isabela.blanco@gmail.com` → observar cambio de estado.
4. **(2m)** Logout → Login `laura.mendoza@...` → `/feed`. Crear publicación + imagen, filtrar chips, reaccionar, eliminar propia.
5. **(1m)** `/semilleros` → buscar "neuro", filtrar, abrir detalle + "Ver Todos", botón "Solicitar Vinculación".
6. **(30s)** `/profile` → mostrar datos reales + contenido demo y la banda "datos de demostración".
7. **(1m)** `/docs` → mostrar OpenAPI. Cerrar mencionando Docker Compose, capas Flask, MySQL y restricciones BD.

---

## 6. Matriz de cobertura por criterio

| Flujo | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| 4.1–4.2 | ● | ● | ● | | ● |
| 4.3 | ● | ● | ● | | ● |
| 4.4 | ● | ● | ● | | ● |
| 4.5 | ● | ● | ● | | ● |
| 4.6 | | ● | | | ● |
| 4.7 | | ● | | ● | ● |

---

## 7. Checklist para la demostración

- [ ] App levantada en Docker (`docker compose up --build`), puerto 5000 OK.
- [ ] `/admin` funciona con admin.
- [ ] aprobar `isabela.blanco@gmail.com` (estado cambia).
- [ ] `/feed`: publicar, adjuntar archivo, filtrar, reaccionar, eliminar.
- [ ] `/semilleros`: búsqueda, filtros, detalle, ancla vinculación.
- [ ] `/profile` muestra datos reales; banner demo presente.
- [ ] Páginas demo muestran "datos de demostración".
- [ ] `/docs` muestra OpenAPI.
- [ ] Insistir: módulos demo **no** persistidos (proyectos/eventos/gamificación/reportes).
- [ ] Mencionar: 8 tablas, CHECK + ON DELETE, capas, Docker reproducible.

---

## 8. Notas rápidas para exponer

- **Arquitectura**: "Backend en capas: routes→controllers→services→repositories→models. Controladores no hacen queries."
- **Integridad**: "Migración 0003 añade CHECK y ON DELETE sin borrar datos."
- **Seguridad/Auth**: "Pending/rejected bloqueados en login; guard de admin via `auth_service`; solo `@unilibre.edu.co` para registro institucional."
- **UX**: "Bandas demo para evitar confusión; mensajes controlados en toda la UI."
- **Reproducible**: "Docker + `flask db upgrade` + `flask seed-demo --if-empty`; `restart: unless-stopped` en app."
- **Honesto**: "Proyectos/Eventos/Gamificación/Reportes son demostrativos (JS + demo-data), no hay tablas aún."
