from sqlalchemy import func, select

from app.extensions import db
from app.models import Faculty, Program, User


def get_user_by_email(email: str) -> User | None:
    return db.session.scalar(select(User).where(User.email == email))


def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def get_faculty(faculty_id: int) -> Faculty | None:
    return db.session.get(Faculty, faculty_id)


def get_program(program_id: int) -> Program | None:
    return db.session.get(Program, program_id)


def add_user(user: User) -> User:
    db.session.add(user)
    return user


def list_users(status: str | None = None, role: str | None = None) -> list[User]:
    stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
    if status:
        stmt = stmt.where(User.status == status)
    if role:
        stmt = stmt.where(User.role == role)
    return list(db.session.scalars(stmt).all())


def count_users(*conditions) -> int:
    return int(
        db.session.scalar(select(func.count()).select_from(User).where(*conditions))
        or 0
    )


def count_faculties() -> int:
    return int(db.session.scalar(select(func.count()).select_from(Faculty)) or 0)


def count_programs() -> int:
    return int(db.session.scalar(select(func.count()).select_from(Program)) or 0)


def commit() -> None:
    db.session.commit()


def flush() -> None:
    db.session.flush()
