from sqlalchemy import func, select, update

from app.extensions import db
from app.models import Achievement, Notification, User
from app.models.gamification import ACHIEVEMENT_VALIDATED


# --- Notificaciones ---
def add_notification(notification: Notification) -> Notification:
    db.session.add(notification)
    return notification


def list_notifications(user_id: int, unread_only: bool = False, limit: int | None = None):
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    if limit:
        stmt = stmt.limit(limit)
    return list(db.session.scalars(stmt).all())


def count_unread(user_id: int) -> int:
    return int(
        db.session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        or 0
    )


def get_notification(notification_id: int, user_id: int) -> Notification | None:
    return db.session.scalar(
        select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
    )


def mark_all_read(user_id: int) -> None:
    db.session.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )


# --- Logros y ranking ---
def add_achievement(achievement: Achievement) -> Achievement:
    db.session.add(achievement)
    return achievement


def get_achievement(achievement_id: int) -> Achievement | None:
    return db.session.get(Achievement, achievement_id)


def achievement_exists(user_id: int, title: str) -> bool:
    return (
        db.session.scalar(
            select(Achievement.id).where(
                Achievement.user_id == user_id, Achievement.title == title
            )
        )
        is not None
    )


def list_achievements(user_id: int | None = None, status: str | None = None):
    stmt = select(Achievement).order_by(Achievement.achieved_on.desc(), Achievement.id.desc())
    if user_id:
        stmt = stmt.where(Achievement.user_id == user_id)
    if status:
        stmt = stmt.where(Achievement.status == status)
    return list(db.session.scalars(stmt).all())


def total_xp(user_id: int) -> int:
    return int(
        db.session.scalar(
            select(func.coalesce(func.sum(Achievement.xp), 0)).where(
                Achievement.user_id == user_id,
                Achievement.status == ACHIEVEMENT_VALIDATED,
            )
        )
        or 0
    )


def ranking(limit: int) -> list[tuple[User, int]]:
    xp = func.coalesce(func.sum(Achievement.xp), 0).label("xp")
    stmt = (
        select(User, xp)
        .outerjoin(
            Achievement,
            (Achievement.user_id == User.id)
            & (Achievement.status == ACHIEVEMENT_VALIDATED),
        )
        .where(User.status == "active", User.role != "administrator")
        .group_by(User.id)
        .order_by(xp.desc(), User.full_name)
        .limit(limit)
    )
    return [(row[0], int(row[1])) for row in db.session.execute(stmt).all()]


def count_achievements(status: str | None = None) -> int:
    stmt = select(func.count()).select_from(Achievement)
    if status:
        stmt = stmt.where(Achievement.status == status)
    return int(db.session.scalar(stmt) or 0)


def commit() -> None:
    db.session.commit()
