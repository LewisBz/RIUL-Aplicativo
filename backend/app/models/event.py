from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import User

EVENT_KIND_EVENT = "event"
EVENT_KIND_CALL = "call"
EVENT_KINDS = (EVENT_KIND_EVENT, EVENT_KIND_CALL)

EVENT_OPEN = "open"
EVENT_CLOSED = "closed"
EVENT_STATUSES = (EVENT_OPEN, EVENT_CLOSED)


class Event(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(10), default=EVENT_KIND_EVENT, server_default=EVENT_KIND_EVENT)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(10), default=EVENT_OPEN, server_default=EVENT_OPEN)
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime] = mapped_column(nullable=False)
    location: Mapped[str | None] = mapped_column(String(160))
    capacity: Mapped[int | None] = mapped_column(Integer)
    organizer: Mapped[str | None] = mapped_column(String(160))
    requirements: Mapped[list] = mapped_column(JSON, default=list)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    registrations: Mapped[list["EventRegistration"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class EventRegistration(db.Model):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("event_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    event: Mapped["Event"] = relationship(back_populates="registrations")
    user: Mapped["User"] = relationship()

