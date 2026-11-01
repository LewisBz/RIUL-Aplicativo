from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.semillero import Semillero
from app.models.user import User

PUBLICATION_PUBLISHED = "published"
PUBLICATION_IN_REVIEW = "in_review"
PUBLICATION_STATUSES = (PUBLICATION_PUBLISHED, PUBLICATION_IN_REVIEW)
class Publication(db.Model):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(160))
    published_on: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20), default=PUBLICATION_IN_REVIEW, server_default=PUBLICATION_IN_REVIEW
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    author: Mapped["User"] = relationship()
    semillero: Mapped["Semillero | None"] = relationship()

