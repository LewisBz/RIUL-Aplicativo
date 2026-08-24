from sqlalchemy import func, select

from app.extensions import db
from app.modules.auth.models import (
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    ROLE_RESEARCHER,
    STATUS_ACTIVE,
    STATUS_PENDING,
    STATUS_REJECTED,
    Faculty,
    Program,
    User,
)
from app.modules.posts.models import Post


def overview() -> dict:
    return {
        "users": {
            "total": _count(User),
            "active": _count(User, User.status == "active"),
            "pending": _count(User, User.status == "pending"),
        },
        "faculties": _count(Faculty),
        "programs": _count(Program),
        "posts": _count(Post),
        "unavailable": ["semilleros", "projects", "events", "achievements", "reports"],
    }


def list_users(status: str | None = None, role: str | None = None) -> list[dict]:
    valid_statuses = {STATUS_ACTIVE, STATUS_PENDING, STATUS_REJECTED}
    if status and status not in valid_statuses:
        raise ValueError("Estado de usuario inválido.")
    if role and role not in {ROLE_ADMINISTRATOR, ROLE_LEADER, ROLE_RESEARCHER}:
        raise ValueError("Rol de usuario inválido.")

    stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
    if status:
        stmt = stmt.where(User.status == status)
    if role:
        stmt = stmt.where(User.role == role)
    return [user.to_dict() for user in db.session.scalars(stmt).all()]


def update_user_status(actor_id: int, user_id: int, status: str) -> dict:
    if status not in {STATUS_ACTIVE, STATUS_PENDING, STATUS_REJECTED}:
        raise ValueError("Estado de usuario inválido.")
    user = db.session.get(User, user_id)
    if user is None:
        raise LookupError("Usuario no encontrado.")
    if user.id == actor_id and status != STATUS_ACTIVE:
        raise PermissionError("No puedes desactivar tu propia cuenta administrativa.")
    user.status = status
    db.session.commit()
    return user.to_dict()


def _count(model, *conditions) -> int:
    return int(db.session.scalar(select(func.count()).select_from(model).where(*conditions)) or 0)