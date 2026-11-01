from datetime import datetime

from app.models import (
    ACHIEVEMENT_IN_REVIEW,
    EVENT_CLOSED,
    EVENT_KIND_CALL,
    EVENT_KIND_EVENT,
    EVENT_KINDS,
    EVENT_OPEN,
    NOTIFICATION_EVENT,
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    Event,
    EventRegistration,
    User,
)
from app.repositories import engagement_repository, event_repository
from app.services import gamification_service, notification_service
from app.utils.errors import ServiceError
from app.utils.slug import unique_slug

PARTICIPATION_REGISTERED = "registered"
PARTICIPATION_AVAILABLE = "available"
PARTICIPATION_FULL = "full"
PARTICIPATION_CLOSED = "closed"


def _clean(value) -> str:
    return (value or "").strip()


def _naive(value: datetime) -> datetime:
    return value.replace(tzinfo=None)


def is_closed(event: Event, now: datetime | None = None) -> bool:
    return event.status == EVENT_CLOSED or event.ends_at < (now or datetime.now())


def effective_status(event: Event) -> str:
    return EVENT_CLOSED if is_closed(event) else EVENT_OPEN


def is_full(event: Event) -> bool:
    return event.capacity is not None and len(event.registrations) >= event.capacity


def participation(event: Event, registered: bool) -> str:
    if registered:
        return PARTICIPATION_REGISTERED
    if is_closed(event):
        return PARTICIPATION_CLOSED
    if is_full(event):
        return PARTICIPATION_FULL
    return PARTICIPATION_AVAILABLE


def list_events(kind=None, status=None, q=None) -> list[Event]:
    if kind and kind not in EVENT_KINDS:
        raise ServiceError("Tipo de actividad inválido.", 400)
    if status and status not in (EVENT_OPEN, EVENT_CLOSED):
        raise ServiceError("Estado de actividad inválido.", 400)
    events = event_repository.list_events(kind, None, _clean(q) or None)
    if status:
        events = [e for e in events if effective_status(e) == status]
    return events


def get_or_404(slug: str) -> Event:
    event = event_repository.get_by_slug(slug)
    if event is None:
        raise ServiceError("Actividad no encontrada.", 404)
    return event


def registered_ids(user_id: int) -> set[int]:
    return event_repository.registered_event_ids(user_id)


def create(user: User, data: dict) -> Event:
    if user.role not in (ROLE_LEADER, ROLE_ADMINISTRATOR):
        raise ServiceError("Solo docentes líderes o administradores publican actividades.", 403)
    title = _clean(data.get("title"))
    if not title:
        raise ServiceError("El título es obligatorio.", 400)
    starts_at, ends_at = _naive(data["starts_at"]), _naive(data["ends_at"])
    if ends_at < starts_at:
        raise ServiceError("La fecha de cierre no puede ser anterior al inicio.", 400)
    event = Event(
        slug=unique_slug(title, event_repository.slug_exists, 100),
        kind=data.get("kind") or EVENT_KIND_EVENT,
        title=title,
        description=_clean(data.get("description")) or None,
        type=_clean(data.get("type")) or None,
        starts_at=starts_at,
        ends_at=ends_at,
        location=_clean(data.get("location")) or None,
        capacity=data.get("capacity"),
        organizer=_clean(data.get("organizer")) or user.full_name,
        requirements=data.get("requirements") or [],
        created_by=user.id,
    )
    event_repository.add(event)
    event_repository.commit()
    return event


def register(user: User, slug: str) -> Event:
    event = get_or_404(slug)
    if event_repository.get_registration(event.id, user.id) is not None:
        raise ServiceError("Ya estás inscrito en esta actividad.", 409)
    if is_closed(event):
        raise ServiceError("Esta actividad ya está cerrada.", 409)
    if is_full(event):
        raise ServiceError("No quedan cupos disponibles.", 409)
    event_repository.add_registration(EventRegistration(event_id=event.id, user_id=user.id))
    is_call = event.kind == EVENT_KIND_CALL
    notification_service.notify(
        user.id,
        NOTIFICATION_EVENT,
        "Postulación registrada" if is_call else "Inscripción confirmada",
        f"{'Te postulaste a' if is_call else 'Quedaste inscrito en'} «{event.title}».",
        href=f"/event-detail?id={event.slug}",
    )
    title = f"Participación en {event.title}"
    if not is_call and not engagement_repository.achievement_exists(
        user.id, title
    ):
        gamification_service.award(
            user.id,
            title=title,
            description="Pendiente de validación por la Dirección de Investigación.",
            xp=gamification_service.EVENT_PARTICIPATION_XP,
            icon="event",
            status=ACHIEVEMENT_IN_REVIEW,
        )
    event_repository.commit()
    return event


def unregister(user: User, slug: str) -> Event:
    event = get_or_404(slug)
    registration = event_repository.get_registration(event.id, user.id)
    if registration is None:
        raise ServiceError("No estás inscrito en esta actividad.", 404)
    if is_closed(event):
        raise ServiceError("Esta actividad ya está cerrada.", 409)
    event_repository.delete_registration(registration)
    event_repository.commit()
    return event

