import os

from app.models import (
    Achievement,
    Badge,
    Call,
    Comment,
    Event,
    EventParticipation,
    Faculty,
    Notification,
    Post,
    PostReaction,
    Program,
    Project,
    ProjectMember,
    ProjectMilestone,
    Semillero,
    SemilleroMember,
    User,
    UserBadge,
    UserProfile,
    UserProgress,
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
    "notifications",
    "user_badges",
    "user_progress",
    "achievements",
    "badges",
    "user_profiles",
    "call_applications",
    "calls",
    "event_participations",
    "events",
    "project_milestones",
    "project_members",
    "projects",
    "comments",
    "semillero_follows",
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


def _seed_workflow() -> None:
    from datetime import datetime

    from app.services.workflow_service import ensure_badges

    if Project.query.first() is not None:
        return
    ensure_badges()

    def user(email):
        return user_repository.get_user_by_email(email)

    laura = user("laura.mendoza@unilibre.edu.co")
    camila = user("camila.rojas@unilibre.edu.co")
    javier = user("javier.torres@unilibre.edu.co")
    mateo = user("mateo.silva@unilibre.edu.co")
    if laura is None:
        return

    specs = [
        {
            "slug": "proyecto-analisis-datos",
            "title": "Análisis predictivo del rendimiento académico",
            "type": "Investigación aplicada",
            "status": "En curso",
            "faculty": "Ingeniería",
            "seedbed": "DataLab - RIUL",
            "leader": laura,
            "description": "Modelo para identificar factores del rendimiento académico.",
            "progress": 68,
            "line": "Ciencia de datos",
            "start": "2025-02-10",
            "end": "2026-11-30",
            "members": ["Laura Mendoza", "Camila Rojas", "Andrés Pérez"],
            "milestones": [("Definición de variables", True), ("Validación con la comunidad", False)],
        },
        {
            "slug": "proyecto-redes-neuronales",
            "title": "Redes neuronales aplicadas a la educación",
            "type": "Desarrollo tecnológico",
            "status": "Revisión",
            "faculty": "Ciencias Básicas",
            "seedbed": "Biomodelos y Neurocomputación (BioNeuro)",
            "leader": javier,
            "description": "Modelos interpretables para retroalimentación en cursos.",
            "progress": 42,
            "line": "Inteligencia artificial",
            "start": "2025-08-01",
            "end": "2027-03-15",
            "members": ["Javier Torres", "Sofía Díaz"],
            "milestones": [("Revisión bibliográfica", True), ("Prototipo inicial", False)],
        },
        {
            "slug": "proyecto-sensores-campus",
            "title": "Sensores IoT para campus sostenible",
            "type": "Innovación",
            "status": "Planeado",
            "faculty": "Ingeniería",
            "seedbed": "Internet de las Cosas y Sostenibilidad (IoT-S)",
            "leader": mateo,
            "description": "Red de sensores de consumo energético en el campus.",
            "progress": 12,
            "line": "Internet de las cosas",
            "start": "2026-09-01",
            "end": "2027-12-20",
            "members": ["Mateo Silva"],
            "milestones": [("Diseño de arquitectura", False)],
        },
    ]
    for spec in specs:
        leader = spec["leader"] or laura
        project = Project(
            slug=spec["slug"],
            title=spec["title"],
            type=spec["type"],
            status=spec["status"],
            description=spec["description"],
            faculty=spec["faculty"],
            seedbed=spec["seedbed"],
            leader_name=leader.full_name,
            leader_id=leader.id,
            progress=spec["progress"],
            line=spec["line"],
            start_date=spec["start"],
            end_date=spec["end"],
        )
        db_add = project
        from app.extensions import db

        db.session.add(db_add)
        db.session.flush()
        for name in spec["members"]:
            db.session.add(ProjectMember(project_id=project.id, name=name))
        for text, done in spec["milestones"]:
            db.session.add(ProjectMilestone(project_id=project.id, text=text, done=done))

    from app.extensions import db

    events = [
        ("simposio-investigacion-2026", "V Simposio Internacional de Investigación", "Simposio", "Abierto", "Auditorio A", 180, datetime(2026, 11, 13, 18, 0), datetime(2026, 11, 14, 18, 0), "Dirección de Investigación"),
        ("taller-datos-abiertos", "Taller de datos abiertos para investigadores", "Taller", "Abierto", "Sala B", 40, datetime(2026, 12, 4, 9, 0), datetime(2026, 12, 4, 12, 0), "DataLab - RIUL"),
        ("encuentro-innovacion-2025", "Encuentro de innovación y transferencia", "Encuentro", "Cerrado", "Auditorio A", 100, datetime(2025, 10, 18, 8, 0), datetime(2025, 10, 18, 17, 0), "Centro de Innovación"),
    ]
    for slug, title, kind, status, location, capacity, start, end, organizer in events:
        db.session.add(
            Event(
                slug=slug,
                title=title,
                description=title,
                type=kind,
                status=status,
                location=location,
                capacity=capacity,
                organizer=organizer,
                starts_at=start,
                ends_at=end,
            )
        )
    db.session.add(
        Call(
            slug="convocatoria-semilleros-2027",
            title="Convocatoria de fortalecimiento a semilleros 2027",
            description="Presenta una propuesta para fortalecer tu semillero.",
            status="Abierta",
            location="Virtual",
            organizer="Vicerrectoría de Investigación",
            starts_at=datetime(2026, 11, 1),
            ends_at=datetime(2027, 1, 30),
            published_by=user("ana.restrepo@unilibre.edu.co").id
            if user("ana.restrepo@unilibre.edu.co")
            else None,
        )
    )
    db.session.flush()
    taller = Event.query.filter_by(slug="taller-datos-abiertos").first()
    if taller and camila:
        db.session.add(EventParticipation(event_id=taller.id, user_id=camila.id, status="registered"))

    approved = Achievement(
        user_id=camila.id if camila else laura.id,
        kind="event",
        title="Participante destacado",
        description="Participación en el V Simposio Internacional",
        status="approved",
        xp_amount=50,
        validated_by=user("ana.restrepo@unilibre.edu.co").id
        if user("ana.restrepo@unilibre.edu.co")
        else None,
    )
    pending = Achievement(
        user_id=camila.id if camila else laura.id,
        kind="article",
        title="Publicador académico",
        description="Artículo en revista indexada, pendiente de validación",
        status="pending",
        xp_amount=120,
    )
    laura_log = Achievement(
        user_id=laura.id,
        kind="semillero",
        title="Líder de semillero",
        description="Acompañamiento a DataLab",
        status="approved",
        xp_amount=2140,
        validated_by=user("ana.restrepo@unilibre.edu.co").id
        if user("ana.restrepo@unilibre.edu.co")
        else None,
    )
    db.session.add_all([approved, pending, laura_log])
    db.session.flush()
    for person, xp in ((laura, 2140), (camila, 50) if camila else (laura, 2140)):
        if person is None:
            continue
        level = xp // 100 + 1
        db.session.add(
            UserProgress(user_id=person.id, xp=xp, level=level, stars=min(5, level))
        )
    badge = Badge.query.filter_by(code="leader").first()
    if badge:
        db.session.add(UserBadge(user_id=laura.id, badge_id=badge.id, achievement_id=laura_log.id))
    if camila:
        db.session.add(
            Notification(
                user_id=camila.id,
                type="achievement",
                title="Logro en revisión",
                message="Tu artículo está pendiente de validación del administrador.",
                href="/gamification",
            )
        )
    db.session.flush()


def _seed_surface() -> None:
    """Bios, un comentario y avisos. No pisa filas que ya existan."""
    from app.extensions import db

    laura = user_repository.get_user_by_email("laura.mendoza@unilibre.edu.co")
    camila = user_repository.get_user_by_email("camila.rojas@unilibre.edu.co")
    if laura and db.session.get(UserProfile, laura.id) is None:
        db.session.add(
            UserProfile(
                user_id=laura.id,
                bio="Docente líder de DataLab. Acompaña proyectos de analítica del rendimiento académico.",
            )
        )
    if camila and db.session.get(UserProfile, camila.id) is None:
        db.session.add(
            UserProfile(
                user_id=camila.id,
                bio="Estudiante investigadora. Trabaja en modelos predictivos y datos abiertos.",
            )
        )
    if Comment.query.first() is None and camila is not None:
        post = Post.query.order_by(Post.id.asc()).first()
        if post is not None:
            db.session.add(
                Comment(
                    post_id=post.id,
                    user_id=camila.id,
                    body="Me sumo a esta línea. Puedo apoyar con la validación de los datos.",
                )
            )
    notices = (
        (
            "laura.mendoza@unilibre.edu.co",
            "Solicitudes del semillero",
            "Revisa las vinculaciones de DataLab desde el panel del semillero.",
            "/semilleros?id=datalab",
            "member",
        ),
        (
            "ana.restrepo@unilibre.edu.co",
            "Logro por validar",
            "Hay un artículo pendiente de aprobación en el panel administrativo.",
            "/admin",
            "achievement",
        ),
        (
            "javier.torres@unilibre.edu.co",
            "Proyecto en revisión",
            "Redes neuronales aplicadas a la educación sigue en revisión.",
            "/projects",
            "project",
        ),
    )
    for email, title, message, href, kind in notices:
        person = user_repository.get_user_by_email(email)
        if person is None or Notification.query.filter_by(user_id=person.id, title=title).first():
            continue
        db.session.add(
            Notification(
                user_id=person.id,
                type=kind,
                title=title,
                message=message,
                href=href,
            )
        )
    db.session.flush()


def seed_demo(if_empty: bool = False) -> dict:
    """Seed the demo dataset, preserving users and posts when if_empty is True."""
    if if_empty and user_repository.count_users() > 0:
        seed_db()
        semilleros_created, members_created = _seed_missing_semilleros()
        _seed_workflow()
        _seed_surface()
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
    _seed_workflow()
    _seed_surface()

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
