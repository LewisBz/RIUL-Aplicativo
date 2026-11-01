from datetime import date, datetime

from sqlalchemy import JSON, Date, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import User

REPORT_KIND_REPORT = "report"
REPORT_KIND_RANKING = "ranking"
REPORT_KINDS = (REPORT_KIND_REPORT, REPORT_KIND_RANKING)


class ReportSnapshot(db.Model):
    """Instantánea de analítica generada por un administrador.

    `published_at` nulo = borrador. Los rankings en vivo no se almacenan: se
    calculan con ``ORDER BY user_progress.xp``.
    """

    __tablename__ = "report_snapshots"
    __table_args__ = (
        db.CheckConstraint("kind IN ('report','ranking')", name="ck_report_snapshots_kind"),
        db.CheckConstraint("period_end >= period_start", name="ck_report_snapshots_period"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    generated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column()
    metrics_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    author: Mapped["User"] = relationship()

    @property
    def is_published(self) -> bool:
        return self.published_at is not None
