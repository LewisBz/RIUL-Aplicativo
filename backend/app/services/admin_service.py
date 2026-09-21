from app.models import (
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    ROLE_RESEARCHER,
    STATUS_ACTIVE,
    STATUS_PENDING,
    STATUS_REJECTED,
    User,
)
from app.repositories import post_repository, user_repository


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
        "unavailable": ["semilleros", "projects", "events", "achievements", "reports"],
    }


def list_users(status: str | None = None, role: str | None = None) -> list[User]:
    valid_statuses = {STATUS_ACTIVE, STATUS_PENDING, STATUS_REJECTED}
    if status and status not in valid_statuses:
        raise ValueError("Estado de usuario inválido.")
    if role and role not in {ROLE_ADMINISTRATOR, ROLE_LEADER, ROLE_RESEARCHER}:
        raise ValueError("Rol de usuario inválido.")
    return user_repository.list_users(status=status, role=role)


def update_user_status(actor_id: int, user_id: int, status: str) -> User:
    if status not in {STATUS_ACTIVE, STATUS_PENDING, STATUS_REJECTED}:
        raise ValueError("Estado de usuario inválido.")
    user = user_repository.get_user_by_id(user_id)
    if user is None:
        raise LookupError("Usuario no encontrado.")
    if user.id == actor_id and status != STATUS_ACTIVE:
        raise PermissionError("No puedes desactivar tu propia cuenta administrativa.")
    user.status = status
    user_repository.commit()
    return user
