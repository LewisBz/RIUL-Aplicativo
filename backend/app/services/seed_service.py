import os

from app.extensions import db
from app.models import (
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    ROLE_RESEARCHER,
    STATUS_ACTIVE,
    Faculty,
    Program,
    User,
)
from app.repositories import catalog_repository

SEED_FACULTIES = {
    "Ingeniería": ["Ingeniería de Sistemas", "Ingeniería Industrial"],
    "Ciencias Básicas": [],
}

SEED_USERS_PASSWORD_ENV = "DEMO_USERS_PASSWORD"
SEED_USERS_DEFAULT_PASSWORD = "RiulDemo2026*"


def seed_db() -> int:
    created = 0
    for faculty_name, program_names in SEED_FACULTIES.items():
        faculty = catalog_repository.get_faculty_by_name(faculty_name)
        if faculty is None:
            faculty = Faculty(name=faculty_name)
            catalog_repository.add_faculty(faculty)
            db.session.flush()
            created += 1
        for program_name in program_names:
            exists = catalog_repository.get_program_by_name(program_name, faculty.id)
            if exists is None:
                catalog_repository.add_program(
                    Program(name=program_name, faculty_id=faculty.id)
                )
                created += 1
    db.session.commit()
    return created


def seed_admin(email: str, password: str, name: str) -> str:
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email)
        db.session.add(user)
    user.full_name = name or "Administrador Demo"
    user.role = ROLE_ADMINISTRATOR
    user.status = STATUS_ACTIVE
    user.set_password(password)
    db.session.commit()
    return email


def seed_users() -> tuple[int, int]:
    password = os.environ.get(SEED_USERS_PASSWORD_ENV, SEED_USERS_DEFAULT_PASSWORD)
    db.session.expunge_all()
    faculty = catalog_repository.get_faculty_by_name("Ingeniería")
    program = (
        catalog_repository.get_program_by_name("Ingeniería de Sistemas", faculty.id)
        if faculty
        else None
    )
    specs = [
        ("estudiante.demo@unilibre.edu.co", "Estudiante Demo", ROLE_RESEARCHER),
        ("docente.demo@unilibre.edu.co", "Docente Demo", ROLE_LEADER),
        ("admin.demo@unilibre.edu.co", "Administrador Demo", ROLE_ADMINISTRATOR),
    ]
    created = 0
    updated = 0
    for email, name, role in specs:
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email)
            db.session.add(user)
            created += 1
        else:
            updated += 1
        user.full_name = name
        user.role = role
        user.status = STATUS_ACTIVE
        user.motivation = None
        if role != ROLE_ADMINISTRATOR and faculty is not None:
            user.faculty_id = faculty.id
            user.program_id = program.id if program else None
        user.set_password(password)
    db.session.commit()
    return created, updated
