"""Operaciones del workflow (proyectos, eventos, logros, notificaciones)."""
from datetime import datetime, timezone

from app.extensions import db
from app.models import (
    Achievement,
    Badge,
    Call,
    CallApplication,
    Comment,
    Event,
    EventParticipation,
    Notification,
    Project,
    Semillero,
    SemilleroFollow,
    SemilleroMember,
    User,
    UserBadge,
    UserProfile,
    UserProgress,
)
from app.utils.errors import ServiceError

XP_BY_KIND = {
    "event": 50,
    "post": 20,
    "project": 40,
    "article": 120,
    "presentation": 80,
    "patent": 100,
    "semillero": 80,
}
BADGE_BY_KIND = {
    "event": "event",
    "post": "publisher",
    "project": "project",
    "article": "publisher",
    "presentation": "event",
    "patent": "project",
    "semillero": "leader",
}
ICONS = {
    "event": "event",
    "post": "forum",
    "project": "folder",
    "article": "article",
    "presentation": "co_present",
    "patent": "workspace_premium",
    "semillero": "groups",
    "achievement": "military_tech",
    "message": "mail",
}


def _progress(user_id: int) -> UserProgress:
    row = db.session.get(UserProgress, user_id)
    if row is None:
        row = UserProgress(user_id=user_id, xp=0, level=1, stars=1)
        db.session.add(row)
        db.session.flush()
    return row


def _apply_xp(progress: UserProgress) -> None:
    progress.level = progress.xp // 100 + 1
    progress.stars = min(5, progress.level)


def _notify(user_id: int, type_: str, title: str, message: str, href: str | None) -> None:
    db.session.add(
        Notification(
            user_id=user_id,
            type=type_,
            title=title,
            message=message,
            href=href,
        )
    )


def record_pending(
    user_id: int,
    kind: str,
    title: str,
    description: str | None = None,
    source_kind: str | None = None,
    source_id: int | None = None,
    evidence: str | None = None,
    commit: bool = True,
) -> Achievement:
    if kind not in XP_BY_KIND:
        raise ServiceError("Tipo de logro no válido.", 400)
    row = Achievement(
        user_id=user_id,
        kind=kind,
        title=title[:200],
        description=description,
        status="pending",
        xp_amount=XP_BY_KIND[kind],
        evidence=evidence,
        source_kind=source_kind,
        source_id=source_id,
    )
    db.session.add(row)
    if commit:
        db.session.commit()
    return row


def ensure_badges() -> None:
    catalog = [
        ("publisher", "Publicador destacado", "workspace_premium"),
        ("event", "Participante de evento", "military_tech"),
        ("leader", "Líder de semillero", "groups"),
        ("project", "Gestor de proyecto", "folder"),
    ]
    for code, title, icon in catalog:
        if Badge.query.filter_by(code=code).first() is None:
            db.session.add(Badge(code=code, title=title, icon=icon))
    db.session.flush()


def list_comments(post_id: int) -> list[dict]:
    rows = (
        Comment.query.filter_by(post_id=post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [
        {
            "id": row.id,
            "body": row.body,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "author": row.author.full_name if row.author else "Investigador",
        }
        for row in rows
    ]


def add_comment(user_id: int, post_id: int, body: str) -> dict:
    text = (body or "").strip()
    if not text:
        raise ServiceError("El comentario no puede estar vacío.", 400)
    from app.models import Post

    if db.session.get(Post, post_id) is None:
        raise ServiceError("Publicación no encontrada.", 404)
    row = Comment(post_id=post_id, user_id=user_id, body=text)
    db.session.add(row)
    db.session.commit()
    return list_comments(post_id)[-1]


def join_semillero(user_id: int, semillero_id: int, motivation: str | None) -> dict:
    semillero = db.session.get(Semillero, semillero_id)
    if semillero is None:
        raise ServiceError("Semillero no encontrado.", 404)
    member = SemilleroMember.query.filter_by(
        semillero_id=semillero.id, user_id=user_id
    ).first()
    if member and member.status == "active":
        raise ServiceError("Ya perteneces a este semillero.", 409)
    if member and member.status == "pending":
        raise ServiceError("Ya tienes una solicitud pendiente.", 409)
    if member is None:
        member = SemilleroMember(
            semillero_id=semillero.id,
            user_id=user_id,
            role_in_semillero="Estudiante Investigador",
            status="pending",
        )
        db.session.add(member)
    else:
        member.status = "pending"
    if semillero.leader_id:
        user = db.session.get(User, user_id)
        _notify(
            semillero.leader_id,
            "member",
            "Solicitud de vinculación",
            f"{user.full_name if user else 'Un investigador'} quiere unirse a {semillero.name}.",
            f"/semillero-detalle?id={semillero.slug}",
        )
    db.session.commit()
    return {"status": "pending", "motivation": motivation or ""}


def follow_semillero(user_id: int, semillero_id: int) -> dict:
    semillero = db.session.get(Semillero, semillero_id)
    if semillero is None:
        raise ServiceError("Semillero no encontrado.", 404)
    existing = SemilleroFollow.query.filter_by(
        semillero_id=semillero.id, user_id=user_id
    ).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return {"following": False}
    db.session.add(SemilleroFollow(semillero_id=semillero.id, user_id=user_id))
    db.session.commit()
    return {"following": True}


def review_member(actor_id: int, semillero_id: int, member_user_id: int, status: str) -> dict:
    if status not in {"active", "rejected"}:
        raise ServiceError("Estado de vinculación no válido.", 400)
    semillero = db.session.get(Semillero, semillero_id)
    if semillero is None or semillero.leader_id != actor_id:
        raise ServiceError("Solo el líder del semillero puede resolver la solicitud.", 403)
    member = SemilleroMember.query.filter_by(
        semillero_id=semillero.id, user_id=member_user_id
    ).first()
    if member is None:
        raise ServiceError("Solicitud no encontrada.", 404)
    member.status = status
    _notify(
        member_user_id,
        "member",
        "Vinculación actualizada",
        f"Tu solicitud a {semillero.name} fue {'aprobada' if status == 'active' else 'rechazada'}.",
        f"/semillero-detalle?id={semillero.slug}",
    )
    db.session.commit()
    return {"status": status}


def _project_card(project: Project) -> dict:
    return {
        "id": project.slug,
        "title": project.title,
        "type": project.type,
        "status": project.status,
        "description": project.description or "",
        "faculty": project.faculty or "",
        "seedbed": project.seedbed or "",
        "leader": project.leader_name or "",
        "progress": project.progress,
        "line": project.line or "",
        "startDate": project.start_date or "",
        "endDate": project.end_date or "",
        "products": [],
        "members": [member.name for member in project.members],
        "milestones": [
            {"text": item.text, "done": bool(item.done)} for item in project.milestones
        ],
    }


def list_projects() -> list[dict]:
    return [_project_card(row) for row in Project.query.order_by(Project.id.asc()).all()]


def get_project(slug: str) -> dict:
    row = Project.query.filter_by(slug=slug).first()
    if row is None:
        raise ServiceError("Proyecto no encontrado.", 404)
    return _project_card(row)


def create_project(user_id: int, data: dict) -> dict:
    title = (data.get("title") or "").strip()
    if not title:
        raise ServiceError("El proyecto necesita un título.", 400)
    user = db.session.get(User, user_id)
    slug = f"proyecto-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    project = Project(
        slug=slug,
        title=title,
        type=data.get("type") or "Investigación aplicada",
        status="En curso",
        description=data.get("description") or "",
        faculty=data.get("faculty") or "",
        seedbed=data.get("seedbed") or "",
        leader_name=user.full_name if user else "",
        leader_id=user_id,
        progress=int(data.get("progress") or 0),
        line=data.get("line") or "",
    )
    db.session.add(project)
    db.session.flush()
    record_pending(
        user_id,
        "project",
        f"Proyecto: {title}",
        project.description,
        source_kind="project",
        source_id=project.id,
        commit=False,
    )
    db.session.commit()
    return _project_card(project)


def _iso(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def _event_card(event: Event, user_id: int | None) -> dict:
    mine = None
    if user_id:
        mine = next((p for p in event.participations if p.user_id == user_id), None)
    registered = len(event.participations)
    status = "Cerrado" if event.status == "Cerrado" else "Abierto"
    participation = "available"
    if mine:
        participation = mine.status
    elif status == "Cerrado":
        participation = "closed"
    return {
        "id": event.slug,
        "kind": "event",
        "title": event.title,
        "description": event.description or "",
        "type": event.type,
        "status": status,
        "startDate": _iso(event.starts_at),
        "endDate": _iso(event.ends_at or event.starts_at),
        "location": event.location or "",
        "capacity": event.capacity,
        "registered": registered,
        "organizer": event.organizer or "",
        "requirements": [],
        "participationStatus": participation,
        "members": [event.organizer] if event.organizer else [],
        "timeline": [{"text": "Inscripciones", "done": status != "Cerrado"}],
    }


def _call_card(call: Call, user_id: int | None) -> dict:
    mine = None
    if user_id:
        mine = next((p for p in call.applications if p.user_id == user_id), None)
    status = "Cerrado" if call.status == "Cerrada" else "Abierta"
    participation = "available"
    if mine:
        participation = "pending" if mine.status == "pending" else mine.status
    elif status == "Cerrado":
        participation = "closed"
    return {
        "id": call.slug,
        "kind": "call",
        "title": call.title,
        "description": call.description or "",
        "type": "Convocatoria",
        "status": status,
        "startDate": _iso(call.starts_at),
        "endDate": _iso(call.ends_at or call.starts_at),
        "location": call.location or "Virtual",
        "capacity": None,
        "registered": len(call.applications),
        "organizer": call.organizer or "",
        "requirements": ["Propuesta de trabajo", "Aval del semillero"],
        "participationStatus": participation,
        "members": [call.organizer] if call.organizer else [],
        "timeline": [{"text": "Convocatoria publicada", "done": True}],
    }


def list_activities(user_id: int | None) -> list[dict]:
    events = [_event_card(row, user_id) for row in Event.query.order_by(Event.starts_at.asc())]
    calls = [_call_card(row, user_id) for row in Call.query.order_by(Call.starts_at.asc())]
    return events + calls


def get_activity(slug: str, user_id: int | None) -> dict:
    event = Event.query.filter_by(slug=slug).first()
    if event:
        return _event_card(event, user_id)
    call = Call.query.filter_by(slug=slug).first()
    if call:
        return _call_card(call, user_id)
    raise ServiceError("Actividad no encontrada.", 404)


def join_activity(user_id: int, slug: str) -> dict:
    event = Event.query.filter_by(slug=slug).first()
    if event:
        if event.status == "Cerrado":
            raise ServiceError("El evento está cerrado.", 409)
        existing = EventParticipation.query.filter_by(event_id=event.id, user_id=user_id).first()
        if existing:
            raise ServiceError("Ya estás inscrito.", 409)
        db.session.add(EventParticipation(event_id=event.id, user_id=user_id, status="registered"))
        record_pending(
            user_id,
            "event",
            f"Participación: {event.title}",
            event.description,
            source_kind="event",
            source_id=event.id,
            commit=False,
        )
        db.session.commit()
        return _event_card(event, user_id)
    call = Call.query.filter_by(slug=slug).first()
    if call is None:
        raise ServiceError("Actividad no encontrada.", 404)
    if call.status == "Cerrada":
        raise ServiceError("La convocatoria está cerrada.", 409)
    existing = CallApplication.query.filter_by(call_id=call.id, user_id=user_id).first()
    if existing:
        raise ServiceError("Ya enviaste una postulación.", 409)
    db.session.add(CallApplication(call_id=call.id, user_id=user_id, status="pending"))
    db.session.commit()
    return _call_card(call, user_id)


def profile_payload(user: User) -> dict:
    progress = _progress(user.id)
    _apply_xp(progress)
    memberships = (
        SemilleroMember.query.filter_by(user_id=user.id, status="active").all()
    )
    projects = Project.query.filter_by(leader_id=user.id).all()
    achievements = (
        Achievement.query.filter_by(user_id=user.id).order_by(Achievement.id.desc()).all()
    )
    badges = UserBadge.query.filter_by(user_id=user.id).all()
    profile = db.session.get(UserProfile, user.id)
    return {
        "bio": profile.bio if profile else "",
        "gamification": {
            "level": progress.level,
            "xp": progress.xp,
            "nextLevelXp": progress.level * 100,
            "stars": progress.stars,
            "totalStars": 5,
        },
        "badges": [
            {"icon": row.badge.icon, "title": row.badge.title, "highlighted": True}
            for row in badges
            if row.badge
        ],
        "semilleros": [
            {"name": row.semillero.name, "role": f"Rol: {row.role_in_semillero}"}
            for row in memberships
            if row.semillero
        ],
        "projects": [
            {"name": row.title, "meta": f"Estado: {row.status}"} for row in projects
        ],
        "publications": [
            {
                "title": row.title,
                "venue": row.kind,
                "date": row.status,
            }
            for row in achievements
            if row.kind in {"article", "presentation"}
        ],
        "products": [
            {
                "type": row.kind,
                "name": row.title,
                "status": "Aprobado" if row.status == "approved" else "En revisión",
            }
            for row in achievements
        ],
        "achievements": [
            {"text": row.title, "done": row.status == "approved"} for row in achievements
        ],
    }


def update_profile(user_id: int, bio: str | None) -> dict:
    profile = db.session.get(UserProfile, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
    profile.bio = (bio or "").strip() or None
    db.session.commit()
    user = db.session.get(User, user_id)
    return profile_payload(user)


def gamification_payload(user_id: int) -> dict:
    progress = _progress(user_id)
    _apply_xp(progress)
    db.session.commit()
    mine = Achievement.query.filter_by(user_id=user_id).order_by(Achievement.id.desc()).all()
    badges = UserBadge.query.filter_by(user_id=user_id).all()
    ranking_rows = (
        db.session.query(UserProgress, User)
        .join(User, User.id == UserProgress.user_id)
        .filter(User.status == "active")
        .order_by(UserProgress.xp.desc(), User.full_name.asc())
        .limit(10)
        .all()
    )
    ranking = []
    for index, (prog, person) in enumerate(ranking_rows, start=1):
        ranking.append(
            {
                "position": index,
                "name": person.full_name or person.email,
                "role": {
                    "researcher": "Estudiante investigador",
                    "leader": "Docente líder",
                    "administrator": "Administrador",
                }.get(person.role, person.role),
                "xp": prog.xp,
                "isCurrentUser": person.id == user_id,
            }
        )
    return {
        "gamification": {
            "level": progress.level,
            "xp": progress.xp,
            "nextLevelXp": max(progress.level * 100, progress.xp + 1),
            "stars": progress.stars,
            "totalStars": 5,
        },
        "badges": [
            {"icon": row.badge.icon, "title": row.badge.title, "highlighted": True}
            for row in badges
            if row.badge
        ],
        "ranking": ranking,
        "achievements": [
            {
                "id": row.id,
                "icon": ICONS.get(row.kind, "military_tech"),
                "title": row.title,
                "description": row.description or "",
                "status": "Validado" if row.status == "approved" else (
                    "Rechazado" if row.status == "rejected" else "En revisión"
                ),
                "xp": row.xp_amount,
            }
            for row in mine
        ],
    }


def home_payload(user: User) -> dict:
    progress = _progress(user.id)
    projects = Project.query.order_by(Project.id.asc()).limit(4).all()
    notes = (
        Notification.query.filter_by(user_id=user.id)
        .order_by(Notification.created_at.desc())
        .limit(4)
        .all()
    )
    membership = (
        SemilleroMember.query.filter_by(user_id=user.id, status="active").first()
    )
    return {
        "projects": [
            {"id": row.slug, "title": row.title, "status": row.status} for row in projects
        ],
        "publications": [
            {"icon": "article", "title": row.title[:80], "meta": row.category}
            for row in user_posts(user.id)
        ],
        "semillero": {
            "name": membership.semillero.name if membership and membership.semillero else "Sin semillero",
            "members": f"{len(membership.semillero.members)} integrantes"
            if membership and membership.semillero
            else "Solicita vinculación",
            "activities": "Actividades en eventos",
        },
        "notifications": [
            {
                "icon": ICONS.get(row.type, "notifications"),
                "title": row.title,
                "text": row.message,
            }
            for row in notes
        ],
        "gamification": {
            "stars": progress.stars,
            "totalStars": 5,
        },
    }


def user_posts(user_id: int) -> list:
    from app.models import Post

    return (
        Post.query.filter_by(author_id=user_id)
        .order_by(Post.created_at.desc())
        .limit(5)
        .all()
    )


def list_notifications(user_id: int) -> list[dict]:
    rows = (
        Notification.query.filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(row.id),
            "type": row.type,
            "icon": ICONS.get(row.type, "notifications"),
            "title": row.title,
            "text": row.message,
            "createdAt": row.created_at.isoformat() if row.created_at else "",
            "read": row.read_at is not None,
            "href": row.href or "",
        }
        for row in rows
    ]


def mark_notification(user_id: int, notification_id: int) -> None:
    row = db.session.get(Notification, notification_id)
    if row is None or row.user_id != user_id:
        raise ServiceError("Notificación no encontrada.", 404)
    row.read_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.session.commit()


def list_achievements_admin() -> list[dict]:
    rows = Achievement.query.order_by(Achievement.id.desc()).limit(50).all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "kind": row.kind,
            "status": row.status,
            "xp": row.xp_amount,
            "user": row.user.full_name if row.user else "",
            "email": row.user.email if row.user else "",
        }
        for row in rows
    ]


def review_achievement(admin_id: int, achievement_id: int, status: str) -> dict:
    if status not in {"approved", "rejected"}:
        raise ServiceError("Estado de logro no válido.", 400)
    admin = db.session.get(User, admin_id)
    if admin is None or admin.role != "administrator":
        raise ServiceError("Se requieren permisos de administrador.", 403)
    row = db.session.get(Achievement, achievement_id)
    if row is None:
        raise ServiceError("Logro no encontrado.", 404)
    if row.status == "approved":
        raise ServiceError("Ese logro ya fue aprobado.", 409)
    row.status = status
    row.validated_by = admin_id
    if status == "approved":
        ensure_badges()
        progress = _progress(row.user_id)
        progress.xp += row.xp_amount
        _apply_xp(progress)
        code = BADGE_BY_KIND.get(row.kind)
        badge = Badge.query.filter_by(code=code).first() if code else None
        if badge and UserBadge.query.filter_by(user_id=row.user_id, badge_id=badge.id).first() is None:
            db.session.add(
                UserBadge(user_id=row.user_id, badge_id=badge.id, achievement_id=row.id)
            )
        _notify(
            row.user_id,
            "achievement",
            "Logro validado",
            f"{row.title} sumó {row.xp_amount} XP.",
            "/gamification",
        )
    else:
        _notify(
            row.user_id,
            "achievement",
            "Logro no aprobado",
            f"{row.title} fue rechazado por el administrador.",
            "/gamification",
        )
    db.session.commit()
    return {"id": row.id, "status": row.status}


def reports() -> dict:
    from app.models import Post

    ranking = (
        db.session.query(UserProgress, User)
        .join(User, User.id == UserProgress.user_id)
        .order_by(UserProgress.xp.desc())
        .limit(5)
        .all()
    )
    return {
        "users": User.query.count(),
        "posts": Post.query.count(),
        "semilleros": Semillero.query.count(),
        "projects": Project.query.count(),
        "events": Event.query.count(),
        "calls": Call.query.count(),
        "achievements": Achievement.query.count(),
        "pending_achievements": Achievement.query.filter_by(status="pending").count(),
        "ranking": [
            {
                "name": person.full_name or person.email,
                "xp": prog.xp,
                "level": prog.level,
                "stars": prog.stars,
            }
            for prog, person in ranking
        ],
    }


def pending_members(semillero_id: int) -> list[dict]:
    rows = SemilleroMember.query.filter_by(semillero_id=semillero_id, status="pending").all()
    return [
        {
            "user_id": row.user_id,
            "name": row.user.full_name if row.user else "",
            "email": row.user.email if row.user else "",
        }
        for row in rows
    ]
