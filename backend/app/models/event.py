from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.semillero import Semillero
from app.models.user import User

EVENT_KIND_EVENT = "event"
EVENT_KIND_CALL = "call"
EVENT_KINDS = (EVENT_KIND_EVENT, EVENT_KIND_CALL)

EVENT_OPEN = "open"
EVENT_CLOSED = "closed"
EVENT_STATUSES = (EVENT_OPEN, EVENT_CLOSED)

PARTICIPATION_ATTENDEE = "attendee"
PARTICIPATION_SPEAKER = "speaker"
PARTICIPATION_ORGANIZER = "organizer"
PARTICIPATION_ROLES = (PARTICIPATION_ATTENDEE, PARTICIPATION_SPEAKER, PARTICIPATION_ORGANIZER)

PARTICIPATION_AVAILABLE = "available"
PARTICIPATION_REGISTERED = "registered"
PARTICIPATION_PENDING = "pending"
PARTICIPATION_CLOSED = "closed"
PARTICIPATION_STATUSES = (
    PARTICIPATION_AVAILABLE,
    PARTICIPATION_REGISTERED,
    PARTICIPATION_PENDING,
    PARTICIPATION_CLOSED,
)

APPLICATION_PENDING = "pending"
APPLICATION_ACCEPTED = "accepted"
APPLICATION_REJECTED = "rejected"
APPLICATION_STATUSES = (APPLICATION_PENDING, APPLICATION_ACCEPTED, APPLICATION_REJECTED)


class Event(db.Model):
    __tablename__ = "events"
    __table_args__ = (
        db.CheckConstraint("status IN ('open','closed')", name="ck_events_status"),
        db.CheckConstraint("ends_at >= starts_at", name="ck_events_dates"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default=EVENT_OPEN, server_default=EVENT_OPEN
    )
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime] = mapped_column(nullable=False)
    location: Mapped[str | None] = mapped_column(String(160))
    capacity: Mapped[int | None] = mapped_column(Integer)
    organizer: Mapped[str | None] = mapped_column(String(160))
    requirements: Mapped[list] = mapped_column(JSON, default=list)
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    semillero: Mapped["Semillero | None"] = relationship()
    participations: Mapped[list["EventParticipation"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )

    kind = EVENT_KIND_EVENT  # atributo de lectura: la API unifica eventos y convocatorias

    @property
    def participant_count(self) -> int:
        return len(self.participations)


class EventParticipation(db.Model):
    """Participación de un usuario en un evento (asistente, ponente u organizador)."""

    __tablename__ = "event_participations"
    __table_args__ = (
        UniqueConstraint("event_id", "user_id"),
        db.CheckConstraint(
            "role IN ('attendee','speaker','organizer')", name="ck_event_participations_role"
        ),
        db.CheckConstraint(
            "status IN ('available','registered','pending','closed')",
            name="ck_event_participations_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PARTICIPATION_ATTENDEE, server_default=PARTICIPATION_ATTENDEE
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PARTICIPATION_REGISTERED, server_default=PARTICIPATION_REGISTERED
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    event: Mapped["Event"] = relationship(back_populates="participations")
    user: Mapped["User"] = relationship()


class Call(db.Model):
    """Convocatoria publicada por la administración."""

    __tablename__ = "calls"
    __table_args__ = (
        db.CheckConstraint("status IN ('open','closed')", name="ck_calls_status"),
        db.CheckConstraint("ends_at >= starts_at", name="ck_calls_dates"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default=EVENT_OPEN, server_default=EVENT_OPEN
    )
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime] = mapped_column(nullable=False)
    location: Mapped[str | None] = mapped_column(String(160))
    organizer: Mapped[str | None] = mapped_column(String(160))
    requirements: Mapped[list] = mapped_column(JSON, default=list)
    published_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    publisher: Mapped["User"] = relationship()
    applications: Mapped[list["CallApplication"]] = relationship(
        back_populates="call", cascade="all, delete-orphan"
    )

    kind = EVENT_KIND_CALL
    capacity = None  # las convocatorias no tienen cupo

    @property
    def participant_count(self) -> int:
        return len(self.applications)


class CallApplication(db.Model):
    """Postulación a una convocatoria: de un usuario o de un semillero (exclusivo)."""

    __tablename__ = "call_applications"
    __table_args__ = (
        UniqueConstraint("call_id", "user_id"),
        UniqueConstraint("call_id", "semillero_id"),
        db.CheckConstraint(
            "(user_id IS NOT NULL AND semillero_id IS NULL) OR "
            "(user_id IS NULL AND semillero_id IS NOT NULL)",
            name="ck_call_applications_applicant",
        ),
        db.CheckConstraint(
            "status IN ('pending','accepted','rejected')", name="ck_call_applications_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=APPLICATION_PENDING, server_default=APPLICATION_PENDING
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    call: Mapped["Call"] = relationship(back_populates="applications")
    user: Mapped["User | None"] = relationship()
    semillero: Mapped["Semillero | None"] = relationship()
