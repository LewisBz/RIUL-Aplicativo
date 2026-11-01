from app.models import (
    MEMBERSHIP_ACTIVE,
    MEMBERSHIP_PENDING,
    MEMBERSHIP_REJECTED,
    NOTIFICATION_SEMILLERO,
    PRIORITY_HIGH,
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    SEMILLERO_ROLE_CO_LEADER,
    SEMILLERO_ROLE_LEADER,
    SEMILLERO_ROLE_MEMBER,
    ResearchLine,
    Semillero,
    SemilleroActivity,
    SemilleroFollow,
    SemilleroMember,
    User,
)
from app.repositories import semillero_repository
from app.services import gamification_service, notification_service
from app.services.auth_service import resolve_faculty_program
from app.utils.errors import ServiceError
from app.utils.slug import unique_slug


def _clean(value) -> str:
    return (value or "").strip()


def can_manage(user: User, semillero: Semillero) -> bool:
    """Administrador, líder del semillero o co-líder activo."""
    if user.role == ROLE_ADMINISTRATOR or semillero.leader_id == user.id:
        return True
    member = semillero_repository.get_member(semillero.id, user.id)
    return (
        member is not None
        and member.status == MEMBERSHIP_ACTIVE
        and member.role == SEMILLERO_ROLE_CO_LEADER
    )


def list_semilleros(q=None, faculty_id=None, area=None) -> list[Semillero]:
    return semillero_repository.list_semilleros(_clean(q) or None, faculty_id, area or None)


def list_areas() -> list[str]:
    return semillero_repository.list_areas()


def get_or_404(slug: str) -> Semillero:
    semillero = semillero_repository.get_by_slug(slug)
    if semillero is None:
        raise ServiceError("Semillero no encontrado.", 404)
    return semillero


def create(user: User, data: dict) -> Semillero:
    if user.role not in (ROLE_LEADER, ROLE_ADMINISTRATOR):
        raise ServiceError("Solo docentes líderes o administradores crean semilleros.", 403)
    name = _clean(data.get("name"))
    if not name:
        raise ServiceError("El nombre del semillero es obligatorio.", 400)
    faculty_id, program_id = resolve_faculty_program(data)
    if faculty_id is None:
        faculty_id = user.faculty_id
    if faculty_id is None:
        raise ServiceError("Debe seleccionar la facultad del semillero.", 400)
    semillero = Semillero(
        slug=unique_slug(name, semillero_repository.slug_exists),
        name=name,
        area=_clean(data.get("area")) or None,
        description=_clean(data.get("description")) or None,
        icon=_clean(data.get("icon")) or "science",
        faculty_id=faculty_id,
        program_id=program_id,
        leader_id=user.id,
        about=_clean(data.get("about")) or None,
        mission=_clean(data.get("mission")) or None,
        vision=_clean(data.get("vision")) or None,
        interest_areas=data.get("interest_areas") or [],
    )
    semillero.members.append(
        SemilleroMember(
            user_id=user.id,
            role=SEMILLERO_ROLE_LEADER,
            status=MEMBERSHIP_ACTIVE,
            approved_by=user.id,
        )
    )
    for line in data.get("lines") or []:
        semillero.lines.append(
            ResearchLine(
                name=line["name"],
                icon=line.get("icon") or "science",
                coordinator=line.get("coordinator"),
            )
        )
    semillero_repository.add(semillero)
    semillero_repository.flush()
    gamification_service.ensure_semillero_progress(semillero.id)
    semillero_repository.commit()
    return semillero


# --- Membresía (solicitud -> aprobación) ---
def join(user: User, slug: str) -> Semillero:
    semillero = get_or_404(slug)
    member = semillero_repository.get_member(semillero.id, user.id)
    if member is not None:
        if member.status == MEMBERSHIP_ACTIVE:
            raise ServiceError(
                "Ya lideras este semillero."
                if member.role == SEMILLERO_ROLE_LEADER
                else "Ya eres miembro de este semillero.",
                409,
            )
        if member.status == MEMBERSHIP_PENDING:
            raise ServiceError("Ya tienes una solicitud pendiente en este semillero.", 409)
        # Solicitud rechazada previamente: se permite volver a intentarlo.
        member.status, member.approved_by = MEMBERSHIP_PENDING, None
    else:
        semillero_repository.add_member(
            SemilleroMember(
                semillero_id=semillero.id,
                user_id=user.id,
                role=SEMILLERO_ROLE_MEMBER,
                status=MEMBERSHIP_PENDING,
            )
        )
    notification_service.notify(
        semillero.leader_id,
        NOTIFICATION_SEMILLERO,
        "Nueva solicitud de vinculación",
        f"{user.full_name or user.email} solicitó unirse a {semillero.name}.",
        href=f"/semillero-detalle?id={semillero.slug}",
        priority=PRIORITY_HIGH,
        entity=("semillero", semillero.id),
    )
    semillero_repository.commit()
    return semillero


def leave(user: User, slug: str) -> None:
    semillero = get_or_404(slug)
    member = semillero_repository.get_member(semillero.id, user.id)
    if member is None:
        raise ServiceError("No eres miembro de este semillero.", 404)
    if member.role == SEMILLERO_ROLE_LEADER:
        raise ServiceError("El líder no puede abandonar su propio semillero.", 409)
    semillero_repository.delete_member(member)
    semillero_repository.commit()


def review_member(
    actor: User, slug: str, user_id: int, status: str, role: str | None = None
) -> SemilleroMember:
    semillero = get_or_404(slug)
    if not can_manage(actor, semillero):
        raise ServiceError("Solo el líder del semillero puede resolver solicitudes.", 403)
    if status not in (MEMBERSHIP_ACTIVE, MEMBERSHIP_REJECTED):
        raise ServiceError("Estado de vinculación inválido.", 400)
    if role and role not in (SEMILLERO_ROLE_MEMBER, SEMILLERO_ROLE_CO_LEADER):
        raise ServiceError("Rol de vinculación inválido.", 400)
    member = semillero_repository.get_member(semillero.id, user_id)
    if member is None:
        raise ServiceError("Solicitud no encontrada.", 404)
    if member.role == SEMILLERO_ROLE_LEADER:
        raise ServiceError("No se puede modificar al líder del semillero.", 409)
    member.status = status
    if status == MEMBERSHIP_ACTIVE:
        member.approved_by = actor.id
        if role:
            member.role = role
    else:
        member.approved_by = actor.id
    verdict = "aprobada" if status == MEMBERSHIP_ACTIVE else "rechazada"
    notification_service.notify(
        member.user_id,
        NOTIFICATION_SEMILLERO,
        f"Solicitud {verdict}",
        f"Tu solicitud para unirte a {semillero.name} fue {verdict}.",
        href=f"/semillero-detalle?id={semillero.slug}",
        priority=PRIORITY_HIGH,
        entity=("semillero", semillero.id),
    )
    semillero_repository.commit()
    return member


# --- Seguimiento ---
def follow(user: User, slug: str) -> Semillero:
    semillero = get_or_404(slug)
    if semillero_repository.get_follow(semillero.id, user.id) is not None:
        raise ServiceError("Ya sigues este semillero.", 409)
    semillero_repository.add_follow(SemilleroFollow(semillero_id=semillero.id, user_id=user.id))
    semillero_repository.commit()
    return semillero


def unfollow(user: User, slug: str) -> Semillero:
    semillero = get_or_404(slug)
    follow_row = semillero_repository.get_follow(semillero.id, user.id)
    if follow_row is None:
        raise ServiceError("No sigues este semillero.", 404)
    semillero_repository.delete_follow(follow_row)
    semillero_repository.commit()
    return semillero


def followed_ids(user_id: int) -> set[int]:
    return semillero_repository.followed_ids(user_id)


def follower_count(semillero: Semillero) -> int:
    return semillero_repository.count_followers(semillero.id)


# --- Actividades ---
def add_activity(user: User, slug: str, data: dict) -> SemilleroActivity:
    semillero = get_or_404(slug)
    if not can_manage(user, semillero):
        raise ServiceError("Solo el líder del semillero puede registrar actividades.", 403)
    title = _clean(data.get("title"))
    if not title:
        raise ServiceError("El título de la actividad es obligatorio.", 400)
    activity = SemilleroActivity(
        title=title, place=_clean(data.get("place")) or None, occurred_on=data["occurred_on"]
    )
    semillero.activities.append(activity)
    semillero_repository.commit()
    return activity


# --- Vista del usuario ---
def viewer_membership(semillero: Semillero, user_id: int) -> dict:
    """Rol vigente y estado de la vinculación del usuario con el semillero."""
    member = semillero_repository.get_member(semillero.id, user_id)
    if member is None:
        return {"role": None, "status": None}
    role = member.role if member.status == MEMBERSHIP_ACTIVE else None
    return {"role": role, "status": member.status}


def viewer_roles(user_id: int) -> dict[int, str]:
    return {
        m.semillero_id: m.role for m in semillero_repository.memberships_for_user(user_id)
    }


def viewer_statuses(user_id: int) -> dict[int, str]:
    return {
        m.semillero_id: m.status
        for m in semillero_repository.memberships_for_user(user_id, active_only=False)
    }
