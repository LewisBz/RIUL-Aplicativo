from datetime import datetime, timezone

from sqlalchemy import func, select, update

from app.extensions import db
from app.models import Notification


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
        stmt = stmt.where(Notification.read_at.is_(None))
    if limit:
        stmt = stmt.limit(limit)
    return list(db.session.scalars(stmt).all())


def count_unread(user_id: int) -> int:
    return int(
        db.session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
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
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        .values(read_at=datetime.now(timezone.utc).replace(tzinfo=None))
    )


def commit() -> None:
    db.session.commit()
