from sqlalchemy import func, select

from app.extensions import db
from app.modules.auth.models import Faculty, Program, User
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


def _count(model, *conditions) -> int:
    return int(db.session.scalar(select(func.count()).select_from(model).where(*conditions)) or 0)