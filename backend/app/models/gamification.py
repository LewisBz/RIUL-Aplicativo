from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import User

ACHIEVEMENT_VALIDATED = "validated"
ACHIEVEMENT_IN_REVIEW = "in_review"
ACHIEVEMENT_REJECTED = "rejected"
ACHIEVEMENT_STATUSES = (ACHIEVEMENT_VALIDATED, ACHIEVEMENT_IN_REVIEW, ACHIEVEMENT_REJECTED)


class Achievement(db.Model):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    icon: Mapped[str] = mapped_column(String(40), default="military_tech", server_default="military_tech")
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default=ACHIEVEMENT_IN_REVIEW, server_default=ACHIEVEMENT_IN_REVIEW
    )
    xp: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    achieved_on: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship()


