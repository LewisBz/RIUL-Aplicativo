# Quickstart: validar 006 Dashboard y Perfil

## Prerrequisitos

- Docker Compose levantado: `docker compose up --build` (app Flask + MySQL 8.4).
- Un usuario registrado, o uno de los usuarios seed.

## Escenarios

1. **Guard sin sesión (US1)**: en una ventana sin token abre `/dashboard` y luego `/profile`. Esperado: redirige a `/login` en ambos casos.
2. **Token inválido (US1)**: guarda `"garbage"` como token en localStorage y abre `/dashboard`. Esperado: el token se borra, redirige a `/login` y no hay bucle.
3. **Layout compartido (US2)**: con sesión, ambas páginas muestran el navbar de sesión (avatar, nombre, rol, menú con salir) y la sidebar con el ítem activo correcto. En móvil la sidebar está oculta.
4. **Dashboard (US3)**: el saludo usa el nombre real. Se ven las tarjetas de perfil, proyectos, publicaciones, semillero y notificaciones. "Ver Todo" va a `/profile`.
5. **Perfil (US4)**: el banner y la información personal muestran datos reales, con facultad y programa por nombre, resueltos por `/api/profile`. Se ven la tarjeta de gamificación, las tablas y la línea de tiempo.
6. **Edición (US4)**: con "Editar Perfil" cambia el nombre, recarga y comprueba que persiste.
7. **Logout**: salir desde cualquiera de las dos páginas lleva a `/login`.
8. **Regresión (US6)**: la home en modo invitado y autenticado, `/login`, `/register` y `/docs` siguen funcionando. Corre la suite de pytest contra el servicio `db` (ver el README del backend); debe pasar completa.
9. **Responsive**: el bento pasa a una columna en móvil.

## Resultado esperado

Todos los escenarios pasan sin nuevas dependencias.
