import os

from sqlalchemy import text

from app.extensions import db
from app.models import (
    Achievement,
    Event,
    EventRegistration,
    Faculty,
    Notification,
    Post,
    PostReaction,
    Program,
    Project,
    ProjectMember,
    ProjectMilestone,
    ProjectProduct,
    Publication,
    ResearchLine,
    Semillero,
    SemilleroActivity,
    SemilleroMember,
    User,
)
from app.repositories import catalog_repository
from app.seed_data import (
    SEED_ACHIEVEMENTS,
    SEED_DEMO_POSTS,
    SEED_DEMO_REACTIONS,
    SEED_DEMO_USERS,
    SEED_EVENTS,
    SEED_FACULTIES,
    SEED_NOTIFICATIONS,
    SEED_PROJECTS,
    SEED_PUBLICATIONS,
    SEED_SEMILLEROS,
)
from app.utils.slug import unique_slug

SEED_USERS_PASSWORD_ENV = "DEMO_USERS_PASSWORD"
SEED_USERS_DEFAULT_PASSWORD = "RiulDemo2026*"

_DEMO_TABLES = (
    "notifications",
    "achievements",
    "event_registrations",
    "events",
    "publications",
    "project_milestones",
    "project_products",
    "project_members",
    "projects",
    "semillero_activities",
    "research_lines",
    "semillero_members",
    "semilleros",
    "post_reactions",
    "post_attachments",
    "posts",
    "users",
)


def _email(prefix: str) -> str:
    return f"{prefix}@unilibre.edu.co"


def _seed_research_domain(users_by_email, faculty_ids, program_ids) -> dict:
    def user(prefix):
        return users_by_email[_email(prefix)]

    semilleros = {}
    for spec in SEED_SEMILLEROS:
        leader = user(spec["leader"]) if spec["leader"] else None
        semillero = Semillero(
            slug=unique_slug(spec["name"], lambda s: any(x.slug == s for x in semilleros.values())),
            name=spec["name"],
            area=spec["area"],
            icon=spec["icon"],
            top_badge=spec.get("top_badge"),
            description=spec["description"],
            faculty_id=faculty_ids[spec["faculty"]],
            program_id=program_ids[(spec["faculty"], spec["program"])],
            leader_id=leader.id if leader else None,
            leader_name=leader.full_name if leader else spec.get("leader_name"),
            leader_title=spec["leader_title"],
            affiliation=spec["affiliation"],
            about=spec["about"],
            mission=spec["mission"],
            vision=spec["vision"],
            interest_areas=spec["interest_areas"],
        )
        for prefix, role in spec["members"]:
            semillero.members.append(SemilleroMember(user_id=user(prefix).id, role=role))
        for icon, name, coordinator in spec["lines"]:
            semillero.lines.append(ResearchLine(icon=icon, name=name, coordinator=coordinator))
        for occurred_on, title, place in spec["activities"]:
            semillero.activities.append(
                SemilleroActivity(occurred_on=occurred_on, title=title, place=place)
            )
        db.session.add(semillero)
        semilleros[spec["name"]] = semillero
    db.session.flush()

    projects = {}
    for spec in SEED_PROJECTS:
        project = Project(
            slug=unique_slug(spec["title"], lambda s: s in projects, 100),
            title=spec["title"],
            type=spec["type"],
            status=spec["status"],
            description=spec["description"],
            progress=spec["progress"],
            line=spec["line"],
            role_required=spec["role_required"],
            start_date=spec["start_date"],
            end_date=spec["end_date"],
            semillero_id=semilleros[spec["semillero"]].id,
            leader_id=user(spec["leader"]).id,
        )
        for prefix in [spec["leader"], *spec["members"]]:
            project.members.append(ProjectMember(user_id=user(prefix).id))
        for type_, name, status in spec["products"]:
            project.products.append(ProjectProduct(type=type_, name=name, status=status))
        for position, (text_, done) in enumerate(spec["milestones"]):
            project.milestones.append(
                ProjectMilestone(text=text_, done=done, position=position)
            )
        db.session.add(project)
        projects[project.slug] = project

    for spec in SEED_PUBLICATIONS:
        db.session.add(
            Publication(
                author_id=user(spec["author"]).id,
                semillero_id=semilleros[spec["semillero"]].id,
                title=spec["title"],
                venue=spec["venue"],
                published_on=spec["published_on"],
                status=spec["status"],
            )
        )

    registrations = 0
    for spec in SEED_EVENTS:
        event = Event(
            slug=unique_slug(spec["title"], lambda s: False, 100),
            kind=spec["kind"],
            title=spec["title"],
            description=spec["description"],
            type=spec["type"],
            status=spec["status"],
            starts_at=spec["starts_at"],
            ends_at=spec["ends_at"],
            location=spec["location"],
            capacity=spec["capacity"],
            organizer=spec["organizer"],
            requirements=spec["requirements"],
        )
        for prefix in spec["registered"]:
            event.registrations.append(EventRegistration(user_id=user(prefix).id))
            registrations += 1
        db.session.add(event)

    for prefix, icon, title, description, status, xp, achieved_on in SEED_ACHIEVEMENTS:
        db.session.add(
            Achievement(
                user_id=user(prefix).id,
                icon=icon,
                title=title,
                description=description,
                status=status,
                xp=xp,
                achieved_on=achieved_on,
            )
        )
    for prefix, type_, title, text_, priority, href, is_read, created_at in SEED_NOTIFICATIONS:
        db.session.add(
            Notification(
                user_id=user(prefix).id,
                type=type_,
                title=title,
                text=text_,
                priority=priority,
                href=href,
                is_read=is_read,
                created_at=created_at,
            )
        )
    return {
        "semilleros": len(semilleros),
        "proyectos": len(projects),
        "publicaciones": len(SEED_PUBLICATIONS),
        "eventos": len(SEED_EVENTS),
        "inscripciones": registrations,
        "logros": len(SEED_ACHIEVEMENTS),
        "notificaciones": len(SEED_NOTIFICATIONS),
    }


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

    research = _seed_research_domain(users_by_email, faculty_ids, program_ids)

    db.session.commit()
    return {
        **research,
        "facultades": len(SEED_FACULTIES),
        "programas": sum(len(p) for p in SEED_FACULTIES.values()),
        "usuarios": len(SEED_DEMO_USERS),
        "posts": len(SEED_DEMO_POSTS),
        "reacciones": reactions,
        "facultades_nuevas": created_faculties,
    }
