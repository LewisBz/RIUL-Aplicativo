import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.extensions import db
from app.models import (
    ACHIEVEMENT_APPROVED,
    ACHIEVEMENT_REJECTED,
    MEMBER_MEMBER,
    MEMBER_PRINCIPAL,
    MEMBERSHIP_ACTIVE,
    MEMBERSHIP_PENDING,
    PARTICIPATION_ATTENDEE,
    PARTICIPATION_REGISTERED,
    SEMILLERO_ROLE_LEADER,
    TYPE_ARTICLE,
    TYPE_EVENT,
    TYPE_PATENT,
    TYPE_POST,
    TYPE_PRESENTATION,
    TYPE_PROJECT,
    TYPE_SEMILLERO,
    Achievement,
    Call,
    CallApplication,
    Comment,
    Event,
    EventParticipation,
    Faculty,
    Notification,
    Post,
    PostReaction,
    PostShare,
    Product,
    Program,
    Project,
    ProjectMember,
    ProjectMilestone,
    ResearchLine,
    Semillero,
    SemilleroActivity,
    SemilleroFollow,
    SemilleroMember,
    User,
    UserProfile,
)
from app.repositories import catalog_repository, gamification_repository
from app.seed_data import (
    SEED_ACHIEVEMENTS,
    SEED_CALLS,
    SEED_DEMO_COMMENTS,
    SEED_DEMO_POSTS,
    SEED_DEMO_REACTIONS,
    SEED_DEMO_SHARES,
    SEED_DEMO_USERS,
    SEED_EVENTS,
    SEED_FACULTIES,
    SEED_NOTIFICATIONS,
    SEED_PRODUCTS,
    SEED_PROJECTS,
    SEED_REPORTS,
    SEED_SEMILLERO_FOLLOWS,
    SEED_SEMILLEROS,
    SEED_USER_PROFILES,
)
from app.services import gamification_service, reference_service, report_service
from app.utils.slug import unique_slug

SEED_USERS_PASSWORD_ENV = "DEMO_USERS_PASSWORD"
SEED_USERS_DEFAULT_PASSWORD = "RiulDemo2026*"

# Tablas de catálogo: el seed demo no las vacía (se upsertan).
_CATALOG_TABLES = {"faculties", "programs", "levels", "badges", "achievement_types"}

_PRODUCT_TYPE_TO_ACHIEVEMENT = {
    "article": TYPE_ARTICLE,
    "presentation": TYPE_PRESENTATION,
    "patent": TYPE_PATENT,
}


def _demo_tables() -> list[str]:
    """Todas las tablas salvo catálogos, de hijas a padres."""
    return [
        table.name
        for table in reversed(db.metadata.sorted_tables)
        if table.name not in _CATALOG_TABLES
    ]


def _email(prefix: str) -> str:
    return f"{prefix}@unilibre.edu.co"


def _seed_semilleros(user, faculty_ids, program_ids) -> dict:
    semilleros = {}
    for spec in SEED_SEMILLEROS:
        leader = user(spec["leader"])
        semillero = Semillero(
            slug=unique_slug(spec["name"], lambda s: any(x.slug == s for x in semilleros.values())),
            name=spec["name"],
            area=spec["area"],
            icon=spec["icon"],
            top_badge=spec.get("top_badge"),
            description=spec["description"],
            faculty_id=faculty_ids[spec["faculty"]],
            program_id=program_ids[(spec["faculty"], spec["program"])],
            leader_id=leader.id,
            leader_title=spec["leader_title"],
            affiliation=spec["affiliation"],
            about=spec["about"],
            mission=spec["mission"],
            vision=spec["vision"],
            interest_areas=spec["interest_areas"],
        )
        semillero.members.append(
            SemilleroMember(
                user_id=leader.id,
                role=SEMILLERO_ROLE_LEADER,
                status=MEMBERSHIP_ACTIVE,
                approved_by=leader.id,
            )
        )
        for prefix, role, *rest in spec["members"]:
            status = rest[0] if rest else MEMBERSHIP_ACTIVE
            semillero.members.append(
                SemilleroMember(
                    user_id=user(prefix).id,
                    role=role,
                    status=status,
                    approved_by=None if status == MEMBERSHIP_PENDING else leader.id,
                )
            )
        for icon, name, coordinator in spec["lines"]:
            semillero.lines.append(ResearchLine(icon=icon, name=name, coordinator=coordinator))
        for occurred_on, title, place in spec["activities"]:
            semillero.activities.append(
                SemilleroActivity(occurred_on=occurred_on, title=title, place=place)
            )
        db.session.add(semillero)
        semilleros[spec["name"]] = semillero
    db.session.flush()
    for semillero in semilleros.values():
        gamification_service.ensure_semillero_progress(semillero.id)
    for prefix, name in SEED_SEMILLERO_FOLLOWS:
        db.session.add(SemilleroFollow(semillero_id=semilleros[name].id, user_id=user(prefix).id))
    return semilleros


def _seed_projects(user, semilleros) -> tuple[dict, dict]:
    projects, products = {}, {}
    for spec in SEED_PROJECTS:
        leader = user(spec["leader"])
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
        )
        project.members.append(ProjectMember(user_id=leader.id, role=MEMBER_PRINCIPAL))
        for prefix in spec["members"]:
            if prefix != spec["leader"]:
                project.members.append(ProjectMember(user_id=user(prefix).id, role=MEMBER_MEMBER))
        for type_, title, status in spec["products"]:
            product = Product(
                user_id=leader.id,
                semillero_id=project.semillero_id,
                type=type_,
                title=title,
                status=status,
            )
            project.products.append(product)
            products[(spec["leader"], title)] = product
        for position, (text_, done) in enumerate(spec["milestones"]):
            project.milestones.append(
                ProjectMilestone(text=text_, done=done, position=position)
            )
        db.session.add(project)
        projects[spec["title"]] = project
    db.session.flush()
    return projects, products


def _seed_products(user, semilleros, products) -> None:
    for spec in SEED_PRODUCTS:
        product = Product(
            user_id=user(spec["author"]).id,
            semillero_id=semilleros[spec["semillero"]].id,
            type=spec["type"],
            title=spec["title"],
            venue=spec["venue"],
            published_on=spec["published_on"],
            status=spec["status"],
        )
        db.session.add(product)
        products[(spec["author"], spec["title"])] = product


def _seed_events(user, semilleros) -> tuple[dict, int, int]:
    events, participations = {}, 0
    for spec in SEED_EVENTS:
        event = Event(
            slug=unique_slug(spec["title"], lambda s: any(e.slug == s for e in events.values()), 100),
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
            semillero_id=semilleros[spec["semillero"]].id if spec.get("semillero") else None,
            created_by=user(spec["created_by"]).id,
        )
        for entry in spec["registered"]:
            prefix, role = (entry, PARTICIPATION_ATTENDEE) if isinstance(entry, str) else entry
            event.participations.append(
                EventParticipation(
                    user_id=user(prefix).id, role=role, status=PARTICIPATION_REGISTERED
                )
            )
            participations += 1
        db.session.add(event)
        events[spec["title"]] = event

    applications = 0
    for spec in SEED_CALLS:
        call = Call(
            slug=unique_slug(
                spec["title"],
                lambda s: any(e.slug == s for e in events.values()),
                100,
            ),
            title=spec["title"],
            description=spec["description"],
            type=spec["type"],
            status=spec["status"],
            starts_at=spec["starts_at"],
            ends_at=spec["ends_at"],
            location=spec["location"],
            organizer=spec["organizer"],
            requirements=spec["requirements"],
            published_by=user(spec["published_by"]).id,
        )
        for kind, ref, status in spec["applications"]:
            if kind == "user":
                call.applications.append(CallApplication(user_id=user(ref).id, status=status))
            else:
                call.applications.append(
                    CallApplication(semillero_id=semilleros[ref].id, status=status)
                )
            applications += 1
        db.session.add(call)
    db.session.flush()
    return events, participations, applications


def _seed_achievements(user, admin, semilleros, projects, products, events, posts) -> int:
    for spec in SEED_ACHIEVEMENTS:
        kind, ref = spec["origin"]
        if kind == "event":
            column, origin_id, type_code = "event_id", events[ref].id, TYPE_EVENT
        elif kind == "semillero":
            column, origin_id, type_code = "semillero_id", semilleros[ref].id, TYPE_SEMILLERO
        elif kind == "project":
            column, origin_id, type_code = "project_id", projects[ref].id, TYPE_PROJECT
        elif kind == "post":
            column, origin_id, type_code = "post_id", posts[ref].id, TYPE_POST
        else:
            product = products[ref]
            column, origin_id = "product_id", product.id
            type_code = _PRODUCT_TYPE_TO_ACHIEVEMENT[product.type]
        achievement_type = gamification_repository.get_type_by_code(type_code)
        reviewed = spec["status"] in (ACHIEVEMENT_APPROVED, ACHIEVEMENT_REJECTED)
        achievement = Achievement(
            user_id=user(spec["user"]).id,
            type_id=achievement_type.id,
            status=spec["status"],
            title=spec["title"],
            description=spec["description"],
            achieved_on=spec["achieved_on"],
            validated_by=admin.id if reviewed else None,
            validated_at=datetime.now(timezone.utc).replace(tzinfo=None) if reviewed else None,
            **{column: origin_id},
        )
        db.session.add(achievement)
        db.session.flush()
        if spec["status"] == ACHIEVEMENT_APPROVED:
            amount = spec["xp"] if spec["xp"] is not None else achievement_type.xp_value
            gamification_service.apply_approval(achievement, amount)
    return len(SEED_ACHIEVEMENTS)


def _seed_research_domain(users_by_email, faculty_ids, program_ids, posts) -> dict:
    def user(prefix):
        return users_by_email[_email(prefix)]

    admin = users_by_email["ana.restrepo@unilibre.edu.co"]

    semilleros = _seed_semilleros(user, faculty_ids, program_ids)
    projects, products = _seed_projects(user, semilleros)
    _seed_products(user, semilleros, products)
    events, participations, applications = _seed_events(user, semilleros)
    db.session.flush()
    achievements = _seed_achievements(
        user, admin, semilleros, projects, products, events, posts
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
                read_at=created_at + timedelta(hours=1) if is_read else None,
                created_at=created_at,
            )
        )
    return {
        "semilleros": len(semilleros),
        "seguidores": len(SEED_SEMILLERO_FOLLOWS),
        "proyectos": len(projects),
        "productos": len(products),
        "eventos": len(events),
        "participaciones": participations,
        "convocatorias": len(SEED_CALLS),
        "postulaciones": applications,
        "logros": achievements,
        "notificaciones": len(SEED_NOTIFICATIONS),
    }


def _seed_reports(admin: User) -> int:
    for kind, start, end, published in SEED_REPORTS:
        report = report_service.generate(admin, kind, start, end)
        if published:
            report_service.publish(admin, report.id)
    return len(SEED_REPORTS)


def seed_db() -> int:
    """Catálogos: facultades, programas, niveles, insignias y tipos de logro."""
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
    created += reference_service.seed_reference_data()
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
    """Purge demo data and rebuild the complete demo dataset from seed_data.py."""
    db.session.expunge_all()
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    for table in _demo_tables():
        db.session.execute(text(f"TRUNCATE TABLE `{table}`"))
    db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    db.session.commit()
    db.session.expunge_all()

    reference_service.seed_reference_data()

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

    profiles = 0
    for prefix, (bio, orcid, photo) in SEED_USER_PROFILES.items():
        db.session.add(
            UserProfile(
                user_id=users_by_email[_email(prefix)].id, bio=bio, orcid=orcid, photo=photo
            )
        )
        profiles += 1

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

    for index, email, body, created_at in SEED_DEMO_COMMENTS:
        db.session.add(
            Comment(
                post_id=posts[index].id,
                user_id=users_by_email[email].id,
                body=body,
                created_at=created_at,
            )
        )
    shares = 0
    for index, emails in SEED_DEMO_SHARES.items():
        for email in emails:
            db.session.add(PostShare(post_id=posts[index].id, user_id=users_by_email[email].id))
            shares += 1

    research = _seed_research_domain(users_by_email, faculty_ids, program_ids, posts)
    db.session.commit()

    reports = _seed_reports(users_by_email["ana.restrepo@unilibre.edu.co"])
    return {
        **research,
        "facultades": len(SEED_FACULTIES),
        "programas": sum(len(p) for p in SEED_FACULTIES.values()),
        "usuarios": len(SEED_DEMO_USERS),
        "perfiles": profiles,
        "posts": len(SEED_DEMO_POSTS),
        "reacciones": reactions,
        "comentarios": len(SEED_DEMO_COMMENTS),
        "compartidos": shares,
        "reportes": reports,
        "facultades_nuevas": created_faculties,
    }
