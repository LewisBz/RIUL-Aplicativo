from datetime import date

from sqlalchemy import func, select

from app.extensions import db
from app.models import (
    ACHIEVEMENT_VALIDATED,
    Achievement,
    Faculty,
    Project,
    Publication,
    Semillero,
    SemilleroMember,
    User,
)
from app.models.project import PROJECT_COMPLETED


def count_publications() -> int:
    return int(db.session.scalar(select(func.count()).select_from(Publication)) or 0)


def count_active_projects() -> int:
    return int(
        db.session.scalar(
            select(func.count()).select_from(Project).where(Project.status != PROJECT_COMPLETED)
        )
        or 0
    )


def total_validated_xp() -> int:
    return int(
        db.session.scalar(
            select(func.coalesce(func.sum(Achievement.xp), 0)).where(
                Achievement.status == ACHIEVEMENT_VALIDATED
            )
        )
        or 0
    )


def publication_dates() -> list[date]:
    """Fecha de producción: `published_on`, o la de registro si no existe."""
    rows = db.session.execute(select(Publication.published_on, Publication.created_at)).all()
    return [published or created.date() for published, created in rows]


def project_dates() -> list[date]:
    """Fecha de producción: `start_date`, o la de registro si no existe."""
    rows = db.session.execute(select(Project.start_date, Project.created_at)).all()
    return [started or created.date() for started, created in rows]


def semilleros_by_faculty() -> list[tuple[str, int]]:
    stmt = (
        select(func.coalesce(Faculty.name, "Sin facultad"), func.count(Semillero.id))
        .select_from(Semillero)
        .outerjoin(Faculty, Semillero.faculty_id == Faculty.id)
        .group_by(Faculty.name)
        .order_by(func.count(Semillero.id).desc())
    )
    return [(name, int(total)) for name, total in db.session.execute(stmt).all()]


def top_semilleros_by_xp(limit: int = 5) -> list[tuple[str, str | None, int]]:
    xp = func.coalesce(func.sum(Achievement.xp), 0)
    stmt = (
        select(Semillero.name, Faculty.name, xp)
        .select_from(Semillero)
        .outerjoin(Faculty, Semillero.faculty_id == Faculty.id)
        .join(SemilleroMember, SemilleroMember.semillero_id == Semillero.id)
        .join(
            Achievement,
            (Achievement.user_id == SemilleroMember.user_id)
            & (Achievement.status == ACHIEVEMENT_VALIDATED),
        )
        .group_by(Semillero.id, Semillero.name, Faculty.name)
        .order_by(xp.desc(), Semillero.name)
        .limit(limit)
    )
    return [(name, faculty, int(total)) for name, faculty, total in db.session.execute(stmt).all()]


def users_by_status() -> dict[str, int]:
    stmt = select(User.status, func.count(User.id)).group_by(User.status)
    return {status: int(total) for status, total in db.session.execute(stmt).all()}
