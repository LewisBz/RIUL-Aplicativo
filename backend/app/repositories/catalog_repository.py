from sqlalchemy import select

from app.extensions import db
from app.models import Faculty, Program


def list_faculties() -> list[Faculty]:
    return list(db.session.scalars(select(Faculty).order_by(Faculty.name)).all())


def list_programs() -> list[Program]:
    return list(db.session.scalars(select(Program).order_by(Program.name)).all())


def get_faculty_by_name(name: str) -> Faculty | None:
    return Faculty.query.filter_by(name=name).first()


def get_program_by_name(name: str, faculty_id: int) -> Program | None:
    return Program.query.filter_by(name=name, faculty_id=faculty_id).first()


def add_faculty(faculty: Faculty) -> Faculty:
    db.session.add(faculty)
    return faculty


def add_program(program: Program) -> Program:
    db.session.add(program)
    return program
