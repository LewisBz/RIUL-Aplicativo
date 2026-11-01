from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import User

NOTIFICATION_ACHIEVEMENT = "achievement"
NOTIFICATION_EVENT = "event"
NOTIFICATION_PROJECT = "project"
NOTIFICATION_SEMILLERO = "semillero"
NOTIFICATION_ACCOUNT = "account"

PRIORITY_HIGH = "high"
PRIORITY_NORMAL = "normal"
PRIORITY_LOW = "low"


class Notification(db.Model):
    """Notificación de usuario. Leída = `read_at` no nulo (NULL = no leída)."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_kind: Mapped[str | None] = mapped_column(String(30))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    priority: Mapped[str] = mapped_column(
        String(10), default=PRIORITY_NORMAL, server_default=PRIORITY_NORMAL
    )
    href: Mapped[str | None] = mapped_column(String(200))
    read_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship()

    @hybrid_property
    def is_read(self) -> bool:
        return self.read_at is not None

    @is_read.setter
    def is_read(self, value: bool) -> None:
        if value:
            if self.read_at is None:
                self.read_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            self.read_at = None

    @is_read.expression
    def is_read(cls):
        return cls.read_at.is_not(None)
