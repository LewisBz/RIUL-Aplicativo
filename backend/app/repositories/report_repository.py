from sqlalchemy import select

from app.extensions import db
from app.models import ReportSnapshot


def add(report: ReportSnapshot) -> ReportSnapshot:
    db.session.add(report)
    return report


def get(report_id: int) -> ReportSnapshot | None:
    return db.session.get(ReportSnapshot, report_id)


def list_reports(kind: str | None = None, published_only: bool = False) -> list[ReportSnapshot]:
    stmt = select(ReportSnapshot).order_by(ReportSnapshot.created_at.desc(), ReportSnapshot.id.desc())
    if kind:
        stmt = stmt.where(ReportSnapshot.kind == kind)
    if published_only:
        stmt = stmt.where(ReportSnapshot.published_at.is_not(None))
    return list(db.session.scalars(stmt).all())


def commit() -> None:
    db.session.commit()
