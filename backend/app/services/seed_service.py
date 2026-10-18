import os

from app.models import (
    Faculty,
    Post,
    PostReaction,
    Program,
    Semillero,
    SemilleroMember,
    User,
)
from app.repositories import (
    catalog_repository,
    post_repository,
    seed_repository,
    semillero_repository,
    user_repository,
)
from app.seed_data import (
    SEED_DEMO_POSTS,
    SEED_DEMO_REACTIONS,
    SEED_DEMO_SEMILLEROS,
    SEED_DEMO_USERS,
    SEED_FACULTIES,
)

SEED_USERS_PASSWORD_ENV = "DEMO_USERS_PASSWORD"
SEED_USERS_DEFAULT_PASSWORD = "RiulDemo2026*"

_DEMO_TABLES = (
    "post_reactions",
    "post_attachments",
    "posts",
    "semillero_members",
    "semilleros",
    "users",
)


def seed_db() -> int:
    created = 0
    for faculty_name, program_names in SEED_FACULTIES.items():
        faculty = catalog_repository.get_faculty_by_name(faculty_name)
        if faculty is None:
            faculty = Faculty(name=faculty_name)
            catalog_repository.add_faculty(faculty)
            catalog_repository.flush()
            created += 1
        for program_name in program_names:
            exists = catalog_repository.get_program_by_name(program_name, faculty.id)
            if exists is None:
                catalog_repository.add_program(
                    Program(name=program_name, faculty_id=faculty.id)
                )
                created += 1
    catalog_repository.commit()
    return created


def seed_admin(email: str, password: str, name: str) -> str:
    email = email.strip().lower()
    user = user_repository.get_user_by_email(email)
    if user is None:
        user = User(email=email)
        user_repository.add_user(user)
    user.full_name = name or "Administrador Demo"
    user.role = "administrator"
    user.status = "active"
    user.set_password(password)
    user_repository.commit()
    return email


def _seed_missing_semilleros() -> tuple[int, int]:
    semilleros_created = 0
    members_created = 0
    for spec in SEED_DEMO_SEMILLEROS:
        semillero = semillero_repository.get_by_slug(spec["slug"])
        if semillero is None:
            faculty = catalog_repository.get_faculty_by_name(spec["faculty"])
            program = (
                catalog_repository.get_program_by_name(spec["program"], faculty.id)
                if faculty
                else None
            )
            leader = user_repository.get_user_by_email(spec["leader_email"])
            semillero = Semillero(
                slug=spec["slug"],
                name=spec["name"],
                faculty_id=faculty.id if faculty else None,
                program_id=program.id if program else None,
                area=spec["area"],
                description=spec["description"],
                mission=spec.get("mission"),
                vision=spec.get("vision"),
                leader_id=leader.id if leader else None,
            )
            semillero_repository.add_semillero(semillero)
            semillero_repository.flush()
            semilleros_created += 1

        for member_spec in spec.get("members", []):
            member_user = user_repository.get_user_by_email(member_spec["email"])
            if member_user is None:
                continue
            membership = semillero_repository.get_member(semillero.id, member_user.id)
            if membership is None:
                semillero_repository.add_member(
                    SemilleroMember(
                        semillero_id=semillero.id,
                        user_id=member_user.id,
                        role_in_semillero=member_spec.get(
                            "role", "Estudiante Investigador"
                        ),
                    )
                )
                members_created += 1
    return semilleros_created, members_created


def seed_demo(if_empty: bool = False) -> dict:
    """Seed the demo dataset, preserving users and posts when if_empty is True."""
    if if_empty and user_repository.count_users() > 0:
        seed_db()
        semilleros_created, members_created = _seed_missing_semilleros()
        catalog_repository.commit()
        return {
            "facultades": catalog_repository.count_faculties(),
            "programas": catalog_repository.count_programs(),
            "usuarios": user_repository.count_users(),
            "posts": post_repository.count_posts(),
            "reacciones": post_repository.count_all_reactions(),
            "semilleros": semilleros_created,
            "miembros_semilleros": members_created,
            "facultades_nuevas": 0,
            "skipped": True,
        }

    seed_repository.purge_tables(_DEMO_TABLES)

    created_faculties = 0
    faculty_ids = {}
    program_ids = {}
    for faculty_name, program_names in SEED_FACULTIES.items():
        faculty = catalog_repository.get_faculty_by_name(faculty_name)
        if faculty is None:
            faculty = Faculty(name=faculty_name)
            catalog_repository.add_faculty(faculty)
            catalog_repository.flush()
            created_faculties += 1
        faculty_ids[faculty_name] = faculty.id
        for program_name in program_names:
            program = catalog_repository.get_program_by_name(program_name, faculty.id)
            if program is None:
                program = Program(name=program_name, faculty_id=faculty.id)
                catalog_repository.add_program(program)
                catalog_repository.flush()
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
        user_repository.add_user(user)
        users_by_email[spec["email"]] = user
    user_repository.flush()

    posts = []
    for spec in SEED_DEMO_POSTS:
        post = Post(
            author_id=users_by_email[spec["author"]].id,
            category=spec["category"],
            content=spec["content"],
            link_url=spec["link_url"],
            created_at=spec["created_at"],
        )
        post_repository.add_post(post)
        posts.append(post)
    post_repository.flush()

    reactions = 0
    for post, reactors in zip(posts, SEED_DEMO_REACTIONS):
        for email in reactors:
            post_repository.add_reaction(
                PostReaction(post_id=post.id, user_id=users_by_email[email].id)
            )
            reactions += 1

    semilleros_created, members_created = _seed_missing_semilleros()

    post_repository.commit()
    return {
        "facultades": len(SEED_FACULTIES),
        "programas": sum(len(p) for p in SEED_FACULTIES.values()),
        "usuarios": len(SEED_DEMO_USERS),
        "posts": len(SEED_DEMO_POSTS),
        "reacciones": reactions,
        "semilleros": semilleros_created,
        "miembros_semilleros": members_created,
        "facultades_nuevas": created_faculties,
    }
