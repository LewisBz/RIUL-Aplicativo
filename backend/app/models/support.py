from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import User

TICKET_OPEN = "open"
TICKET_IN_PROGRESS = "in_progress"
TICKET_RESOLVED = "resolved"
TICKET_STATUSES = (TICKET_OPEN, TICKET_IN_PROGRESS, TICKET_RESOLVED)

TICKET_CATEGORIES = ("technical_bug", "feature_request", "account_issue", "other")


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('open','in_progress','resolved')", name="ck_support_tickets_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    subject: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=TICKET_OPEN, server_default=TICKET_OPEN, nullable=False
    )
    admin_reply: Mapped[str | None] = mapped_column(Text)
    replied_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship()
