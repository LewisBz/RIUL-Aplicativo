from datetime import date, datetime, time

from sqlalchemy import func, select

from app.extensions import db
from app.models import (
    ACHIEVEMENT_APPROVED,
    PRODUCT_ARTICLE,
    Achievement,
    Event,
    Faculty,
    Product,
    Project,
    Semillero,
    SemilleroProgress,
    User,
    UserProgress,
    XpLedger,
)
from app.models.project import PROJECT_CLOSED


def count_publications() -> int:
    """Producción académica: productos registrados."""
    return int(db.session.scalar(select(func.count()).select_from(Product)) or 0)


def count_active_projects() -> int:
    return int(
        db.session.scalar(
            select(func.count()).select_from(Project).where(Project.status != PROJECT_CLOSED)
        )
        or 0
    )


def total_validated_xp() -> int:
    return int(db.session.scalar(select(func.coalesce(func.sum(XpLedger.amount), 0))) or 0)


def publication_dates() -> list[date]:
    """Fecha de producción: `published_on`, o la de registro si no existe."""
    rows = db.session.execute(select(Product.published_on, Product.created_at)).all()
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
    stmt = (
        select(Semillero.name, Faculty.name, func.coalesce(SemilleroProgress.xp, 0))
        .select_from(Semillero)
        .outerjoin(Faculty, Semillero.faculty_id == Faculty.id)
        .outerjoin(SemilleroProgress, SemilleroProgress.semillero_id == Semillero.id)
        .order_by(func.coalesce(SemilleroProgress.xp, 0).desc(), Semillero.name)
        .limit(limit)
    )
    return [(name, faculty, int(total)) for name, faculty, total in db.session.execute(stmt).all()]


def top_users_by_xp(limit: int = 10) -> list[tuple[str | None, int]]:
    xp = func.coalesce(UserProgress.xp, 0)
    stmt = (
        select(User.full_name, xp)
        .select_from(User)
        .outerjoin(UserProgress, UserProgress.user_id == User.id)
        .where(User.status == "active", User.role != "administrator")
        .order_by(xp.desc(), User.full_name)
        .limit(limit)
    )
    return [(name, int(total)) for name, total in db.session.execute(stmt).all()]


def users_by_status() -> dict[str, int]:
    stmt = select(User.status, func.count(User.id)).group_by(User.status)
    return {status: int(total) for status, total in db.session.execute(stmt).all()}


# --- Métricas por periodo (instantáneas de reportes) ---
def _bounds(start: date, end: date) -> tuple[datetime, datetime]:
    return datetime.combine(start, time.min), datetime.combine(end, time.max)


def period_counts(start: date, end: date) -> dict[str, int]:
    low, high = _bounds(start, end)

    def count(model, column):
        return int(
            db.session.scalar(
                select(func.count()).select_from(model).where(column.between(low, high))
            )
            or 0
        )

    approved_in_period = int(
        db.session.scalar(
            select(func.count())
            .select_from(Achievement)
            .where(
                Achievement.status == ACHIEVEMENT_APPROVED,
                Achievement.validated_at.between(low, high),
            )
        )
        or 0
    )
    xp_in_period = int(
        db.session.scalar(
            select(func.coalesce(func.sum(XpLedger.amount), 0)).where(
                XpLedger.created_at.between(low, high)
            )
        )
        or 0
    )
    return {
        "new_users": count(User, User.created_at),
        "new_projects": count(Project, Project.created_at),
        "new_products": count(Product, Product.created_at),
        "new_events": count(Event, Event.created_at),
        "achievements_approved": approved_in_period,
        "xp_awarded": xp_in_period,
    }
