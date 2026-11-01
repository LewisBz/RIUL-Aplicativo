from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import Event, EventRegistration


def slug_exists(slug: str) -> bool:
    return db.session.scalar(select(Event.id).where(Event.slug == slug)) is not None


def get_by_slug(slug: str) -> Event | None:
    return db.session.scalar(select(Event).where(Event.slug == slug))


def list_events(
    kind: str | None = None, status: str | None = None, q: str | None = None
) -> list[Event]:
    stmt = select(Event).order_by(Event.starts_at.desc(), Event.id.desc())
    if kind:
        stmt = stmt.where(Event.kind == kind)
    if status:
        stmt = stmt.where(Event.status == status)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Event.title.like(like), Event.description.like(like)))
    return list(db.session.scalars(stmt).all())


def add(event: Event) -> Event:
    db.session.add(event)
    return event


def get_registration(event_id: int, user_id: int) -> EventRegistration | None:
    return db.session.scalar(
        select(EventRegistration).where(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user_id,
        )
    )


def registered_event_ids(user_id: int) -> set[int]:
    rows = db.session.scalars(
        select(EventRegistration.event_id).where(EventRegistration.user_id == user_id)
    )
    return set(rows.all())


def count_registrations(event_id: int) -> int:
    return int(
        db.session.scalar(
            select(func.count())
            .select_from(EventRegistration)
            .where(EventRegistration.event_id == event_id)
        )
        or 0
    )


def add_registration(registration: EventRegistration) -> EventRegistration:
    db.session.add(registration)
    return registration


def delete_registration(registration: EventRegistration) -> None:
    db.session.delete(registration)


def count_events() -> int:
    return int(db.session.scalar(select(func.count()).select_from(Event)) or 0)


def commit() -> None:
    db.session.commit()
