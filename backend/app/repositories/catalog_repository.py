from sqlalchemy import func, select

from app.extensions import db
from app.models import Faculty, Program


def list_faculties() -> list[Faculty]:
    return list(db.session.scalars(select(Faculty).order_by(Faculty.name)).all())


def list_programs() -> list[Program]:
    return list(db.session.scalars(select(Program).order_by(Program.name)).all())


def get_faculty_by_name(name: str) -> Faculty | None:
    return db.session.scalar(select(Faculty).where(Faculty.name == name))


def get_program_by_name(name: str, faculty_id: int) -> Program | None:
    return db.session.scalar(
        select(Program).where(Program.name == name, Program.faculty_id == faculty_id)
    )


def add_faculty(faculty: Faculty) -> Faculty:
    db.session.add(faculty)
    return faculty


def add_program(program: Program) -> Program:
    db.session.add(program)
    return program


def count_faculties() -> int:
    return int(db.session.scalar(select(func.count()).select_from(Faculty)) or 0)


def count_programs() -> int:
    return int(db.session.scalar(select(func.count()).select_from(Program)) or 0)


def flush() -> None:
    db.session.flush()


def commit() -> None:
    db.session.commit()
