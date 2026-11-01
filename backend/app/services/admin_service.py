from datetime import datetime, timezone

from app.models import (
    ACHIEVEMENT_PENDING,
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
    analytics_repository,
    event_repository,
    gamification_repository,
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
            "total": gamification_repository.count_achievements(),
            "pending": gamification_repository.count_achievements(ACHIEVEMENT_PENDING),
        },
        "unavailable": [],
    }


def _month_keys(count: int = 12) -> list[str]:
    today = datetime.now(timezone.utc).replace(tzinfo=None)
    year, month = today.year, today.month
    keys = []
    for _ in range(count):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return list(reversed(keys))


def analytics() -> dict:
    keys = _month_keys(12)
    production = {key: {"month": key, "publications": 0, "projects": 0} for key in keys}
    for produced_on in analytics_repository.publication_dates():
        entry = production.get(produced_on.strftime("%Y-%m"))
        if entry:
            entry["publications"] += 1
    for produced_on in analytics_repository.project_dates():
        entry = production.get(produced_on.strftime("%Y-%m"))
        if entry:
            entry["projects"] += 1
    by_status = analytics_repository.users_by_status()
    return {
        "totals": {
            "publications": analytics_repository.count_publications(),
            "active_projects": analytics_repository.count_active_projects(),
            "semilleros": semillero_repository.count_semilleros(),
            "validated_xp": analytics_repository.total_validated_xp(),
        },
        "production": [production[key] for key in keys],
        "semilleros_by_faculty": [
            {"faculty": name, "count": total}
            for name, total in analytics_repository.semilleros_by_faculty()
        ],
        "top_semilleros": [
            {"name": name, "faculty": faculty, "xp": xp}
            for name, faculty, xp in analytics_repository.top_semilleros_by_xp()
        ],
        "account_status": {
            "active": by_status.get(STATUS_ACTIVE, 0),
            "pending": by_status.get(STATUS_PENDING, 0),
            "rejected": by_status.get(STATUS_REJECTED, 0),
            "total": sum(by_status.values()),
        },
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

