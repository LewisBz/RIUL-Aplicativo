from marshmallow import Schema, fields, validate

from app.models import APPLICATION_STATUSES, EVENT_KINDS, EVENT_STATUSES
from app.schemas.projects import iso
from app.services import event_service


class EventCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200, error="El título debe tener entre 3 y 200 caracteres."))
    kind = fields.Str(load_default="event", validate=validate.OneOf(EVENT_KINDS, error="Tipo de actividad inválido."))
    description = fields.Str(load_default="")
    type = fields.Str(load_default="")
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
    location = fields.Str(load_default="")
    capacity = fields.Int(load_default=None, allow_none=True, validate=validate.Range(min=1, error="El cupo debe ser mayor a cero."))
    organizer = fields.Str(load_default="")
    requirements = fields.List(fields.Str(), load_default=list)
    semillero = fields.Str(load_default=None, allow_none=True)


class EventListQuerySchema(Schema):
    kind = fields.Str(load_default=None, allow_none=True)
    status = fields.Str(load_default=None, allow_none=True, validate=validate.OneOf(EVENT_STATUSES, error="Estado de actividad inválido."))
    q = fields.Str(load_default=None, allow_none=True)


class RegistrationSchema(Schema):
    """Cuerpo opcional: una convocatoria puede postular a un semillero."""

    semillero = fields.Str(load_default=None, allow_none=True)


class ApplicationReviewSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            [s for s in APPLICATION_STATUSES if s != "pending"],
            error="Estado de postulación inválido.",
        ),
    )


def serialize_event(event, registered: bool = False) -> dict:
    semillero = getattr(event, "semillero", None)
    return {
        "id": event.id,
        "slug": event.slug,
        "kind": event.kind,
        "title": event.title,
        "description": event.description,
        "type": event.type,
        "status": event_service.effective_status(event),
        "starts_at": iso(event.starts_at),
        "ends_at": iso(event.ends_at),
        "location": event.location,
        "capacity": event.capacity,
        "registered_count": event.participant_count,
        "organizer": event.organizer,
        "requirements": event.requirements or [],
        "semillero": {"slug": semillero.slug, "name": semillero.name} if semillero else None,
        "participation": event_service.participation(event, registered),
    }


def serialize_application(application) -> dict:
    applicant = (
        {
            "kind": "user",
            "id": application.user.id,
            "name": application.user.full_name,
        }
        if application.user
        else {
            "kind": "semillero",
            "id": application.semillero.id,
            "name": application.semillero.name,
            "slug": application.semillero.slug,
        }
    )
    return {
        "id": application.id,
        "status": application.status,
        "applicant": applicant,
        "created_at": iso(application.created_at),
    }
