from sqlalchemy import select

from app.extensions import db
from app.models import SupportTicket


def add_ticket(ticket: SupportTicket) -> SupportTicket:
    db.session.add(ticket)
    return ticket


def get_ticket(ticket_id: int) -> SupportTicket | None:
    return db.session.get(SupportTicket, ticket_id)


def list_tickets(user_id: int | None = None, status: str | None = None, limit: int | None = None):
    stmt = select(SupportTicket).order_by(SupportTicket.created_at.desc(), SupportTicket.id.desc())
    if user_id is not None:
        stmt = stmt.where(SupportTicket.user_id == user_id)
    if status:
        stmt = stmt.where(SupportTicket.status == status)
    if limit:
        stmt = stmt.limit(limit)
    return list(db.session.scalars(stmt).all())


def commit() -> None:
    db.session.commit()
