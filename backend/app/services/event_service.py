"""Eventos y convocatorias.

En la base son dos agregados distintos (`events` + `event_participations` y
`calls` + `call_applications`), pero comparten URL y pantalla, así que este
servicio los expone como una sola "actividad" identificada por `slug`.
"""
from datetime import datetime

from app.models import (
    APPLICATION_ACCEPTED,
    APPLICATION_PENDING,
    APPLICATION_REJECTED,
    EVENT_CLOSED,
    EVENT_KIND_CALL,
    EVENT_KIND_EVENT,
    EVENT_KINDS,
    EVENT_OPEN,
    MEMBERSHIP_ACTIVE,
    NOTIFICATION_EVENT,
    PARTICIPATION_ATTENDEE,
    PARTICIPATION_REGISTERED,
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    SEMILLERO_ROLE_CO_LEADER,
    SEMILLERO_ROLE_LEADER,
    Call,
    CallApplication,
    Event,
    EventParticipation,
    User,
)
from app.repositories import event_repository, semillero_repository
from app.services import gamification_service, notification_service
from app.utils.errors import ServiceError
from app.utils.slug import unique_slug

PARTICIPATION_AVAILABLE = "available"
PARTICIPATION_FULL = "full"
PARTICIPATION_CLOSED = "closed"
PARTICIPATION_REGISTERED_VIEW = "registered"


def _clean(value) -> str:
    return (value or "").strip()


def _naive(value: datetime) -> datetime:
    return value.replace(tzinfo=None)


def activity_key(activity) -> tuple[str, int]:
    return activity.kind, activity.id


def is_closed(activity, now: datetime | None = None) -> bool:
    return activity.status == EVENT_CLOSED or activity.ends_at < (now or datetime.now())


def effective_status(activity) -> str:
    return EVENT_CLOSED if is_closed(activity) else EVENT_OPEN


def is_full(activity) -> bool:
    return activity.capacity is not None and activity.participant_count >= activity.capacity


def participation(activity, registered: bool) -> str:
    if registered:
        return PARTICIPATION_REGISTERED_VIEW
    if is_closed(activity):
        return PARTICIPATION_CLOSED
    if is_full(activity):
        return PARTICIPATION_FULL
    return PARTICIPATION_AVAILABLE


def list_events(kind=None, status=None, q=None) -> list:
    if kind and kind not in EVENT_KINDS:
        raise ServiceError("Tipo de actividad inválido.", 400)
    if status and status not in (EVENT_OPEN, EVENT_CLOSED):
        raise ServiceError("Estado de actividad inválido.", 400)
    query = _clean(q) or None
    activities: list = []
    if kind in (None, EVENT_KIND_EVENT):
        activities += event_repository.list_events(query)
    if kind in (None, EVENT_KIND_CALL):
        activities += event_repository.list_calls(query)
    if status:
        activities = [a for a in activities if effective_status(a) == status]
    return sorted(activities, key=lambda a: (a.starts_at, a.id), reverse=True)


def get_or_404(slug: str):
    activity = event_repository.get_event_by_slug(slug) or event_repository.get_call_by_slug(slug)
    if activity is None:
        raise ServiceError("Actividad no encontrada.", 404)
    return activity


def registered_keys(user_id: int) -> set[tuple[str, int]]:
    keys = {(EVENT_KIND_EVENT, i) for i in event_repository.participating_event_ids(user_id)}
    keys |= {(EVENT_KIND_CALL, i) for i in event_repository.applied_call_ids(user_id)}
    return keys


def is_registered(activity, keys: set[tuple[str, int]]) -> bool:
    return activity_key(activity) in keys


def create(user: User, data: dict):
    kind = data.get("kind") or EVENT_KIND_EVENT
    if kind == EVENT_KIND_CALL:
        if user.role != ROLE_ADMINISTRATOR:
            raise ServiceError("Solo la administración publica convocatorias.", 403)
    elif user.role not in (ROLE_LEADER, ROLE_ADMINISTRATOR):
        raise ServiceError("Solo docentes líderes o administradores publican actividades.", 403)

    title = _clean(data.get("title"))
    if not title:
        raise ServiceError("El título es obligatorio.", 400)
    starts_at, ends_at = _naive(data["starts_at"]), _naive(data["ends_at"])
    if ends_at < starts_at:
        raise ServiceError("La fecha de cierre no puede ser anterior al inicio.", 400)

    common = dict(
        slug=unique_slug(title, event_repository.slug_exists, 100),
        title=title,
        description=_clean(data.get("description")) or None,
        type=_clean(data.get("type")) or None,
        starts_at=starts_at,
        ends_at=ends_at,
        location=_clean(data.get("location")) or None,
        organizer=_clean(data.get("organizer")) or user.full_name,
        requirements=data.get("requirements") or [],
    )
    if kind == EVENT_KIND_CALL:
        activity = Call(published_by=user.id, **common)
    else:
        semillero_id = None
        if data.get("semillero"):
            semillero = semillero_repository.get_by_slug(data["semillero"])
            if semillero is None:
                raise ServiceError("Semillero no encontrado.", 404)
            semillero_id = semillero.id
        activity = Event(
            capacity=data.get("capacity"),
            semillero_id=semillero_id,
            created_by=user.id,
            **common,
        )
    event_repository.add(activity)
    event_repository.commit()
    return activity


# --- Inscripción / postulación ---
def _manages_semillero(user: User, semillero) -> bool:
    if user.role == ROLE_ADMINISTRATOR or semillero.leader_id == user.id:
        return True
    member = semillero_repository.get_member(semillero.id, user.id)
    return (
        member is not None
        and member.status == MEMBERSHIP_ACTIVE
        and member.role in (SEMILLERO_ROLE_LEADER, SEMILLERO_ROLE_CO_LEADER)
    )


def register(user: User, slug: str, data: dict | None = None):
    activity = get_or_404(slug)
    if is_closed(activity):
        raise ServiceError("Esta actividad ya está cerrada.", 409)
    if isinstance(activity, Call):
        _apply_to_call(user, activity, (data or {}).get("semillero"))
    else:
        _join_event(user, activity)
    event_repository.commit()
    return activity


def _join_event(user: User, event: Event) -> None:
    if event_repository.get_participation(event.id, user.id) is not None:
        raise ServiceError("Ya estás inscrito en esta actividad.", 409)
    if is_full(event):
        raise ServiceError("No quedan cupos disponibles.", 409)
    event_repository.add(
        EventParticipation(
            event_id=event.id,
            user_id=user.id,
            role=PARTICIPATION_ATTENDEE,
            status=PARTICIPATION_REGISTERED,
        )
    )
    notification_service.notify(
        user.id,
        NOTIFICATION_EVENT,
        "Inscripción confirmada",
        f"Quedaste inscrito en «{event.title}».",
        href=f"/event-detail?id={event.slug}",
        entity=("event", event.id),
    )
    gamification_service.award_event_participation(user.id, event)


def _apply_to_call(user: User, call: Call, semillero_slug: str | None) -> None:
    if semillero_slug:
        semillero = semillero_repository.get_by_slug(semillero_slug)
        if semillero is None:
            raise ServiceError("Semillero no encontrado.", 404)
        if not _manages_semillero(user, semillero):
            raise ServiceError("Solo el líder del semillero puede postularlo.", 403)
        if event_repository.get_semillero_application(call.id, semillero.id) is not None:
            raise ServiceError("Este semillero ya está postulado.", 409)
        application = CallApplication(call_id=call.id, semillero_id=semillero.id)
        subject = f"El semillero {semillero.name} quedó postulado a «{call.title}»."
    else:
        if event_repository.get_user_application(call.id, user.id) is not None:
            raise ServiceError("Ya estás postulado a esta convocatoria.", 409)
        application = CallApplication(call_id=call.id, user_id=user.id)
        subject = f"Te postulaste a «{call.title}»."
    event_repository.add(application)
    notification_service.notify(
        user.id,
        NOTIFICATION_EVENT,
        "Postulación registrada",
        subject,
        href=f"/event-detail?id={call.slug}",
        entity=("call", call.id),
    )


def unregister(user: User, slug: str):
    activity = get_or_404(slug)
    if isinstance(activity, Call):
        application = event_repository.get_user_application(activity.id, user.id)
        if application is None:
            raise ServiceError("No estás postulado a esta convocatoria.", 404)
        if is_closed(activity):
            raise ServiceError("Esta actividad ya está cerrada.", 409)
        if application.status != APPLICATION_PENDING:
            raise ServiceError("La postulación ya fue resuelta y no puede retirarse.", 409)
        event_repository.delete_application(application)
    else:
        registration = event_repository.get_participation(activity.id, user.id)
        if registration is None:
            raise ServiceError("No estás inscrito en esta actividad.", 404)
        if is_closed(activity):
            raise ServiceError("Esta actividad ya está cerrada.", 409)
        event_repository.delete_participation(registration)
    event_repository.commit()
    return activity


# --- Revisión de postulaciones (administración) ---
def list_applications(actor: User, slug: str) -> list[CallApplication]:
    if actor.role != ROLE_ADMINISTRATOR:
        raise ServiceError("Se requieren permisos de administrador.", 403)
    activity = get_or_404(slug)
    if not isinstance(activity, Call):
        raise ServiceError("Solo las convocatorias reciben postulaciones.", 400)
    return event_repository.list_applications(activity.id)


def review_application(actor: User, slug: str, application_id: int, status: str) -> CallApplication:
    if actor.role != ROLE_ADMINISTRATOR:
        raise ServiceError("Se requieren permisos de administrador.", 403)
    if status not in (APPLICATION_ACCEPTED, APPLICATION_REJECTED):
        raise ServiceError("Estado de postulación inválido.", 400)
    call = get_or_404(slug)
    application = event_repository.get_application(application_id)
    if not isinstance(call, Call) or application is None or application.call_id != call.id:
        raise ServiceError("Postulación no encontrada.", 404)
    application.status = status
    verdict = "aceptada" if status == APPLICATION_ACCEPTED else "rechazada"
    recipient = application.user_id or (
        application.semillero.leader_id if application.semillero else None
    )
    if recipient:
        notification_service.notify(
            recipient,
            NOTIFICATION_EVENT,
            f"Postulación {verdict}",
            f"Tu postulación a «{call.title}» fue {verdict}.",
            href=f"/event-detail?id={call.slug}",
            entity=("call", call.id),
        )
    event_repository.commit()
    return application
