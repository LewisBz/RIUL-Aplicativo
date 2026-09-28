import os

from sqlalchemy import text

from app.extensions import db
from app.models import Faculty, Post, PostReaction, Program, User
from app.repositories import catalog_repository
from app.seed_data import (
    SEED_DEMO_POSTS,
    SEED_DEMO_REACTIONS,
    SEED_DEMO_USERS,
    SEED_FACULTIES,
)

SEED_USERS_PASSWORD_ENV = "DEMO_USERS_PASSWORD"
SEED_USERS_DEFAULT_PASSWORD = "RiulDemo2026*"

_DEMO_TABLES = ("post_reactions", "post_attachments", "posts", "users")


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
    user.role = "administrator"
    user.status = "active"
    user.set_password(password)
    db.session.commit()
    return email


def seed_demo() -> dict:
    """Purge users/posts and rebuild the demo dataset from seed_data.py."""
    db.session.expunge_all()
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    for table in _DEMO_TABLES:
        db.session.execute(text(f"TRUNCATE TABLE `{table}`"))
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    db.session.commit()
    db.session.expunge_all()

    created_faculties = 0
    faculty_ids = {}
    program_ids = {}
    for faculty_name, program_names in SEED_FACULTIES.items():
        faculty = Faculty.query.filter_by(name=faculty_name).first()
        if faculty is None:
            faculty = Faculty(name=faculty_name)
            db.session.add(faculty)
            db.session.flush()
            created_faculties += 1
        faculty_ids[faculty_name] = faculty.id
        for program_name in program_names:
            program = Program.query.filter_by(
                name=program_name, faculty_id=faculty.id
            ).first()
            if program is None:
                program = Program(name=program_name, faculty_id=faculty.id)
                db.session.add(program)
                db.session.flush()
            program_ids[(faculty_name, program_name)] = program.id

    password = os.environ.get(SEED_USERS_PASSWORD_ENV, SEED_USERS_DEFAULT_PASSWORD)

    users_by_email = {}
    for spec in SEED_DEMO_USERS:
        user = User(
            full_name=spec["full_name"],
            email=spec["email"],
            role=spec["role"],
            status=spec["status"],
            motivation=spec["motivation"],
            faculty_id=faculty_ids[spec["faculty"]] if spec["faculty"] else None,
            program_id=(
                program_ids[(spec["faculty"], spec["program"])]
                if spec["program"]
                else None
            ),
        )
        user.set_password(password)
        db.session.add(user)
        users_by_email[spec["email"]] = user
    db.session.flush()

    posts = []
    for spec in SEED_DEMO_POSTS:
        post = Post(
            author_id=users_by_email[spec["author"]].id,
            category=spec["category"],
            content=spec["content"],
            link_url=spec["link_url"],
            created_at=spec["created_at"],
        )
        db.session.add(post)
        posts.append(post)
    db.session.flush()

    reactions = 0
    for post, reactors in zip(posts, SEED_DEMO_REACTIONS):
        for email in reactors:
            db.session.add(
                PostReaction(post_id=post.id, user_id=users_by_email[email].id)
            )
            reactions += 1

    db.session.commit()
    return {
        "facultades": len(SEED_FACULTIES),
        "programas": sum(len(p) for p in SEED_FACULTIES.values()),
        "usuarios": len(SEED_DEMO_USERS),
        "posts": len(SEED_DEMO_POSTS),
        "reacciones": reactions,
        "facultades_nuevas": created_faculties,
    }
