from app.models import (
    ACHIEVEMENT_IN_REVIEW,
    NOTIFICATION_ACCOUNT,
    PRIORITY_HIGH,
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    ROLE_RESEARCHER,
    STATUS_ACTIVE,
    STATUS_PENDING,
    STATUS_REJECTED,
    User,
)
from app.repositories import (
    engagement_repository,
    event_repository,
    post_repository,
    project_repository,
    semillero_repository,
    user_repository,
)
from app.services import notification_service


def overview() -> dict:
    return {
        "users": {
            "total": user_repository.count_users(),
            "active": user_repository.count_users(User.status == "active"),
            "pending": user_repository.count_users(User.status == "pending"),
        },
        "faculties": user_repository.count_faculties(),
        "programs": user_repository.count_programs(),
        "posts": post_repository.count_posts(),
        "semilleros": semillero_repository.count_semilleros(),
        "projects": project_repository.count_projects(),
        "events": event_repository.count_events(),
        "achievements": {
            "total": engagement_repository.count_achievements(),
            "pending": engagement_repository.count_achievements(ACHIEVEMENT_IN_REVIEW),
        },
        "unavailable": ["reports"],
    }


def list_users(
    status: str | None = None, role: str | None = None, q: str | None = None
) -> list[User]:
    valid_statuses = {STATUS_ACTIVE, STATUS_PENDING, STATUS_REJECTED}
    if status and status not in valid_statuses:
        raise ValueError("Estado de usuario inválido.")
    if role and role not in {ROLE_ADMINISTRATOR, ROLE_LEADER, ROLE_RESEARCHER}:
        raise ValueError("Rol de usuario inválido.")
    return user_repository.list_users(status=status, role=role, q=(q or "").strip() or None)


def update_user_status(actor_id: int, user_id: int, status: str) -> User:
    if status not in {STATUS_ACTIVE, STATUS_PENDING, STATUS_REJECTED}:
        raise ValueError("Estado de usuario inválido.")
    user = user_repository.get_user_by_id(user_id)
    if user is None:
        raise LookupError("Usuario no encontrado.")
    if user.id == actor_id and status != STATUS_ACTIVE:
        raise PermissionError("No puedes desactivar tu propia cuenta administrativa.")
    changed = user.status != status
    user.status = status
    if changed and status == STATUS_ACTIVE:
        notification_service.notify(
            user.id,
            NOTIFICATION_ACCOUNT,
            "Cuenta aprobada",
            "Tu solicitud fue aprobada. Ya puedes usar RIUL.",
            href="/dashboard",
            priority=PRIORITY_HIGH,
        )
    user_repository.commit()
    return user

