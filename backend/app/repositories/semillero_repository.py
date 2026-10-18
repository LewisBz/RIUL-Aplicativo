from sqlalchemy import func, or_, select

from app.extensions import db
from app.models.semillero import Semillero, SemilleroMember


def get_by_id(semillero_id: int) -> Semillero | None:
    return db.session.get(Semillero, semillero_id)


def get_by_slug(slug: str) -> Semillero | None:
    return db.session.scalar(select(Semillero).where(Semillero.slug == slug))


def list_semilleros(
    faculty_id: int | None = None,
    program_id: int | None = None,
    area: str | None = None,
    query: str | None = None,
) -> list[Semillero]:
    stmt = select(Semillero).order_by(Semillero.name.asc())
    if faculty_id:
        stmt = stmt.where(Semillero.faculty_id == faculty_id)
    if program_id:
        stmt = stmt.where(Semillero.program_id == program_id)
    if area and area.lower() != "all":
        stmt = stmt.where(Semillero.area == area)
    if query:
        pattern = f"%{query}%"
        stmt = stmt.where(
            or_(
                Semillero.name.ilike(pattern),
                Semillero.description.ilike(pattern),
                Semillero.area.ilike(pattern),
            )
        )
    return list(db.session.scalars(stmt).all())


def add_semillero(semillero: Semillero) -> Semillero:
    db.session.add(semillero)
    return semillero


def add_member(member: SemilleroMember) -> SemilleroMember:
    db.session.add(member)
    return member


def get_member(semillero_id: int, user_id: int) -> SemilleroMember | None:
    return db.session.scalar(
        select(SemilleroMember).where(
            SemilleroMember.semillero_id == semillero_id,
            SemilleroMember.user_id == user_id,
        )
    )


def count_semilleros() -> int:
    return int(
        db.session.scalar(select(func.count()).select_from(Semillero)) or 0
    )


def flush() -> None:
    db.session.flush()


def commit() -> None:
    db.session.commit()
