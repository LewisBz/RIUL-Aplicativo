from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import Call, CallApplication, Event, EventParticipation


def slug_exists(slug: str) -> bool:
    """Los slugs son únicos entre eventos y convocatorias (comparten URL)."""
    in_events = db.session.scalar(select(Event.id).where(Event.slug == slug)) is not None
    in_calls = db.session.scalar(select(Call.id).where(Call.slug == slug)) is not None
    return in_events or in_calls


def get_event_by_slug(slug: str) -> Event | None:
    return db.session.scalar(select(Event).where(Event.slug == slug))


def get_call_by_slug(slug: str) -> Call | None:
    return db.session.scalar(select(Call).where(Call.slug == slug))


def list_events(q: str | None = None) -> list[Event]:
    stmt = select(Event).order_by(Event.starts_at.desc(), Event.id.desc())
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Event.title.like(like), Event.description.like(like)))
    return list(db.session.scalars(stmt).all())


def list_calls(q: str | None = None) -> list[Call]:
    stmt = select(Call).order_by(Call.starts_at.desc(), Call.id.desc())
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Call.title.like(like), Call.description.like(like)))
    return list(db.session.scalars(stmt).all())


def add(entity):
    db.session.add(entity)
    return entity


# --- Participación en eventos ---
def get_participation(event_id: int, user_id: int) -> EventParticipation | None:
    return db.session.scalar(
        select(EventParticipation).where(
            EventParticipation.event_id == event_id,
            EventParticipation.user_id == user_id,
        )
    )


def participating_event_ids(user_id: int) -> set[int]:
    rows = db.session.scalars(
        select(EventParticipation.event_id).where(EventParticipation.user_id == user_id)
    )
    return set(rows.all())


def delete_participation(participation: EventParticipation) -> None:
    db.session.delete(participation)


# --- Postulaciones a convocatorias ---
def get_user_application(call_id: int, user_id: int) -> CallApplication | None:
    return db.session.scalar(
        select(CallApplication).where(
            CallApplication.call_id == call_id, CallApplication.user_id == user_id
        )
    )


def get_semillero_application(call_id: int, semillero_id: int) -> CallApplication | None:
    return db.session.scalar(
        select(CallApplication).where(
            CallApplication.call_id == call_id, CallApplication.semillero_id == semillero_id
        )
    )


def get_application(application_id: int) -> CallApplication | None:
    return db.session.get(CallApplication, application_id)


def applied_call_ids(user_id: int) -> set[int]:
    rows = db.session.scalars(
        select(CallApplication.call_id).where(CallApplication.user_id == user_id)
    )
    return set(rows.all())


def list_applications(call_id: int) -> list[CallApplication]:
    stmt = (
        select(CallApplication)
        .where(CallApplication.call_id == call_id)
        .order_by(CallApplication.created_at, CallApplication.id)
    )
    return list(db.session.scalars(stmt).all())


def delete_application(application: CallApplication) -> None:
    db.session.delete(application)


def count_events() -> int:
    events = int(db.session.scalar(select(func.count()).select_from(Event)) or 0)
    calls = int(db.session.scalar(select(func.count()).select_from(Call)) or 0)
    return events + calls


def commit() -> None:
    db.session.commit()


def flush() -> None:
    db.session.flush()
