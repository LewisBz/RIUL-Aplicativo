from marshmallow import Schema, fields, validate

from app.models import TICKET_CATEGORIES, TICKET_STATUSES
from app.schemas.projects import iso


class TicketCreateSchema(Schema):
    category = fields.Str(
        required=True,
        validate=validate.OneOf(TICKET_CATEGORIES, error="Categoría inválida."),
    )
    subject = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=160, error="El asunto debe tener entre 3 y 160 caracteres."),
    )
    message = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=4000, error="El mensaje debe tener entre 10 y 4000 caracteres."),
    )


class TicketReplySchema(Schema):
    status = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(TICKET_STATUSES, error="Estado inválido."),
    )
    reply = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(min=1, max=4000, error="La respuesta debe tener entre 1 y 4000 caracteres."),
    )


class TicketListQuerySchema(Schema):
    status = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(TICKET_STATUSES, error="Estado inválido."),
    )


def serialize_ticket(ticket, with_user: bool = False) -> dict:
    payload = {
        "id": ticket.id,
        "category": ticket.category,
        "subject": ticket.subject,
        "message": ticket.message,
        "status": ticket.status,
        "admin_reply": ticket.admin_reply,
        "replied_at": iso(ticket.replied_at),
        "created_at": iso(ticket.created_at),
    }
    if with_user:
        faculty = ticket.user.faculty.name if ticket.user.faculty else None
        payload["user"] = {
            "id": ticket.user.id,
            "full_name": ticket.user.full_name,
            "email": ticket.user.email,
            "faculty": faculty,
        }
    return payload
