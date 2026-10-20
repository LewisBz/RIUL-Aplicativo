# RIUL — requerimientos del workflow

RIUL (Red Institucional de Semilleros e Investigación) concentra el ingreso, la publicación y la gestión de la investigación de la Universidad Libre. Este documento es la lista verificable del workflow general: inicio, autenticación, validación, dashboard, interacción, logros y visibilidad.

Roles del sistema (no se crea un rol extra de “estudiante”):

| En el workflow | En la base |
| --- | --- |
| Visitante | Sin sesión |
| Estudiante investigador | `researcher` |
| Docente líder | `leader` |
| Administrador | `administrator` |

## 1. Requerimientos funcionales

Cada ítem se comprueba en la aplicación con un resultado observable.

### Usuarios y acceso

- RF-01. El visitante abre la portada y puede ir a semilleros, proyectos y eventos.
- RF-02. El registro institucional exige correo `@unilibre.edu.co`, crea la cuenta `active` y entrega token.
- RF-03. Quien no es institucional envía solicitud (`pending`) con facultad, programa y motivación, sin token.
- RF-04. Login correcto de una cuenta `active` entrega token. Contraseña incorrecta responde 401.
- RF-05. Una cuenta `pending` no entra (403, solicitud pendiente). Una `rejected` no entra (403, no autorizada).
- RF-06. El administrador lista usuarios y cambia el estado a `active` o `rejected`. Un investigador que abre `/admin` recibe 403.

### Investigación

- RF-07. Semilleros, proyectos y eventos se listan y se abren en detalle desde la base de datos.
- RF-08. Un investigador solicita vinculación a un semillero y queda `pending`. El docente líder de ese semillero la aprueba o la rechaza.
- RF-09. Un usuario autenticado puede seguir un semillero sin ser integrante.
- RF-10. Un líder registra un proyecto con estado, avance e hitos. El detalle muestra equipo e hitos.
- RF-11. Un usuario se inscribe a un evento abierto (`registered`) o se postula a una convocatoria (`pending`).

### Comunidad

- RF-12. Un usuario autenticado publica en el feed (texto, enlace o archivo), filtra por categoría, reacciona una vez y borra solo lo suyo.
- RF-13. Un usuario comenta una publicación y el comentario queda guardado.
- RF-14. El perfil muestra correo, facultad y programa reales, semilleros, proyectos y logros de esa cuenta. La bio se puede editar.

### Logros, gamificación y visibilidad

- RF-15. Registrar un logro, publicar, crear un proyecto o inscribirse a un evento deja el logro en `pending`. No suma XP.
- RF-16. Solo el administrador aprueba o rechaza un logro. Al aprobar: suma XP, recalcula nivel (`xp // 100 + 1`) y estrellas (`mínimo entre 5 y el nivel`), otorga insignia y avisa al usuario.
- RF-17. Gamificación muestra XP, nivel, estrellas, insignias, ranking por XP y los logros del usuario.
- RF-18. Notificaciones listan avisos de la cuenta (logro validado, vinculación, evento).
- RF-19. El panel admin muestra indicadores en vivo: usuarios, publicaciones, semilleros, proyectos, eventos, logros y el ranking.

### Por rol (workflow)

- Estudiante: entrar, buscar semillero, solicitar vinculación, participar, registrar logro, ver hoja de vida.
- Docente líder: administrar integrantes del semillero, registrar proyecto, publicar avances en el feed.
- Administrador: validar cuentas, validar logros, ver indicadores y ranking.
- Visitante: consultar información pública de la portada. El detalle de investigación exige sesión.

## 2. Requerimientos no funcionales

- RNF-01 Seguridad. Contraseña con bcrypt. Sesión JWT en `Authorization: Bearer`. Rutas de admin y de aprobación de logros exigen rol `administrator`. La aprobación de integrantes exige ser el `leader_id` del semillero.
- RNF-02 Rendimiento. Listados paginados en el feed y respuestas JSON acotadas (sin archivos embebidos). El ranking se calcula con el XP ya guardado, no recorriendo el historial en cada tarjeta.
- RNF-03 Usabilidad. Errores de login, permiso y validación en español, en la misma pantalla. Estados vacíos cuando un filtro no devuelve filas.
- RNF-04 Accesibilidad. Botones con texto o `aria-label`. Contraste del design system (tokens de color, no gris sobre gris). El foco sigue el orden del formulario de login y de vinculación.
- RNF-05 Disponibilidad. `docker compose up` levanta MySQL y la app, aplica migraciones y siembra datos si la base está vacía. `restart: unless-stopped` en ambos servicios.
- RNF-06 Compatibilidad. HTML/CSS/JS sin bundler. Misma UI en escritorio y en ancho móvil (menú de la barra superior).
- RNF-07 Escalabilidad. Cada proceso nuevo entra como tabla + endpoint bajo `/api`, sin cambiar el login ni el feed ya publicados.

## 3. Pantallas que cubren el workflow

Portada, login, registro, feed, semilleros y detalle, proyectos y detalle, eventos y detalle, dashboard, perfil, gamificación, notificaciones, admin. Esas pantallas son el boceto de alta fidelidad y el prototipo: la navegación es la del workflow (explorar, autenticar, validar, gestionar, registrar logro, ver ranking).
