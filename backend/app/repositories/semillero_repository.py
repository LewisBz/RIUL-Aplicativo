from sqlalchemy import func, select

from app.extensions import db
from app.models import (
    Faculty,
    Program,
    ResearchLine,
    Semillero,
    SemilleroActivity,
    SemilleroMember,
    User,
)


def slug_exists(slug: str) -> bool:
    return db.session.scalar(select(Semillero.id).where(Semillero.slug == slug)) is not None


def get_by_slug(slug: str) -> Semillero | None:
    return db.session.scalar(select(Semillero).where(Semillero.slug == slug))


def list_semilleros(
    q: str | None = None, faculty_id: int | None = None, area: str | None = None
) -> list[Semillero]:
    stmt = select(Semillero).order_by(Semillero.name)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            Semillero.name.like(like)
            | Semillero.description.like(like)
            | Semillero.area.like(like)
        )
    if faculty_id:
        stmt = stmt.where(Semillero.faculty_id == faculty_id)
    if area:
        stmt = stmt.where(Semillero.area == area)
    return list(db.session.scalars(stmt).all())


def add(semillero: Semillero) -> Semillero:
    db.session.add(semillero)
    return semillero


def get_member(semillero_id: int, user_id: int) -> SemilleroMember | None:
    return db.session.scalar(
        select(SemilleroMember).where(
            SemilleroMember.semillero_id == semillero_id,
            SemilleroMember.user_id == user_id,
        )
    )


def add_member(member: SemilleroMember) -> SemilleroMember:
    db.session.add(member)
    return member


def delete_member(member: SemilleroMember) -> None:
    db.session.delete(member)


def memberships_for_user(user_id: int) -> list[SemilleroMember]:
    stmt = (
        select(SemilleroMember)
        .where(SemilleroMember.user_id == user_id)
        .order_by(SemilleroMember.joined_at)
    )
    return list(db.session.scalars(stmt).all())


def count_activities_since(semillero_id: int, since) -> int:
    return int(
        db.session.scalar(
            select(func.count())
            .select_from(SemilleroActivity)
            .where(
                SemilleroActivity.semillero_id == semillero_id,
                SemilleroActivity.occurred_on >= since,
            )
        )
        or 0
    )


def count_semilleros() -> int:
    return int(db.session.scalar(select(func.count()).select_from(Semillero)) or 0)


def list_areas() -> list[str]:
    rows = db.session.scalars(
        select(Semillero.area).where(Semillero.area.is_not(None)).distinct().order_by(Semillero.area)
    )
    return list(rows.all())


def commit() -> None:
    db.session.commit()


def flush() -> None:
    db.session.flush()
