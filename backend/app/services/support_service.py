from datetime import datetime, timezone

from app.models import (
    NOTIFICATION_ACCOUNT,
    TICKET_IN_PROGRESS,
    TICKET_RESOLVED,
    SupportTicket,
    User,
)
from app.repositories import support_repository
from app.services import notification_service
from app.utils.errors import ServiceError


def create_ticket(user: User, data: dict) -> SupportTicket:
    ticket = support_repository.add_ticket(
        SupportTicket(
            user_id=user.id,
            category=data["category"],
            subject=data["subject"].strip(),
            message=data["message"].strip(),
        )
    )
    support_repository.commit()
    return ticket


def list_my_tickets(user: User) -> list[SupportTicket]:
    return support_repository.list_tickets(user_id=user.id)


def list_all_tickets(status: str | None = None, limit: int | None = None) -> list[SupportTicket]:
    return support_repository.list_tickets(status=status, limit=limit)


def reply_ticket(ticket_id: int, data: dict) -> SupportTicket:
    ticket = support_repository.get_ticket(ticket_id)
    if ticket is None:
        raise ServiceError("Ticket no encontrado.", 404)
    reply = (data.get("reply") or "").strip()
    status = data.get("status")
    if not reply and not status:
        raise ServiceError("Indica una respuesta o un estado.", 400)
    if reply:
        ticket.admin_reply = reply
        ticket.replied_at = datetime.now(timezone.utc).replace(tzinfo=None)
        if not status and ticket.status != TICKET_RESOLVED:
            status = TICKET_IN_PROGRESS
        notification_service.notify(
            ticket.user_id,
            NOTIFICATION_ACCOUNT,
            "Respuesta de soporte",
            f"Soporte respondió tu ticket «{ticket.subject}».",
            href="/help",
        )
    if status:
        ticket.status = status
    support_repository.commit()
    return ticket
