from app.models import (
    NOTIFICATION_SEMILLERO,
    ROLE_ADMINISTRATOR,
    ROLE_LEADER,
    SEMILLERO_ROLE_MEMBER,
    ResearchLine,
    Semillero,
    SemilleroActivity,
    SemilleroMember,
    User,
)
from app.repositories import semillero_repository
from app.services import notification_service
from app.services.auth_service import resolve_faculty_program
from app.utils.errors import ServiceError
from app.utils.slug import unique_slug


def _clean(value) -> str:
    return (value or "").strip()


def can_manage(user: User, semillero: Semillero) -> bool:
    return user.role == ROLE_ADMINISTRATOR or semillero.leader_id == user.id


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
    semillero = Semillero(
        slug=unique_slug(name, semillero_repository.slug_exists),
        name=name,
        area=_clean(data.get("area")) or None,
        description=_clean(data.get("description")) or None,
        icon=_clean(data.get("icon")) or "science",
        faculty_id=faculty_id,
        program_id=program_id,
        leader_id=user.id,
        leader_name=user.full_name,
        about=_clean(data.get("about")) or None,
        mission=_clean(data.get("mission")) or None,
        vision=_clean(data.get("vision")) or None,
        interest_areas=data.get("interest_areas") or [],
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
    semillero_repository.commit()
    return semillero


def join(user: User, slug: str) -> Semillero:
    semillero = get_or_404(slug)
    if semillero.leader_id == user.id:
        raise ServiceError("Ya lideras este semillero.", 409)
    if semillero_repository.get_member(semillero.id, user.id) is not None:
        raise ServiceError("Ya eres miembro de este semillero.", 409)
    semillero_repository.add_member(
        SemilleroMember(semillero_id=semillero.id, user_id=user.id, role=SEMILLERO_ROLE_MEMBER)
    )
    if semillero.leader_id:
        notification_service.notify(
            semillero.leader_id,
            NOTIFICATION_SEMILLERO,
            "Nuevo miembro",
            f"{user.full_name or user.email} se unió a {semillero.name}.",
            href=f"/semillero-detalle?id={semillero.slug}",
        )
    semillero_repository.commit()
    return semillero


def leave(user: User, slug: str) -> None:
    semillero = get_or_404(slug)
    member = semillero_repository.get_member(semillero.id, user.id)
    if member is None:
        raise ServiceError("No eres miembro de este semillero.", 404)
    semillero_repository.delete_member(member)
    semillero_repository.commit()


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


def viewer_membership(semillero: Semillero, user_id: int) -> str | None:
    if semillero.leader_id == user_id:
        return "leader"
    member = semillero_repository.get_member(semillero.id, user_id)
    return member.role if member else None


def viewer_roles(user_id: int) -> dict[int, str]:
    roles = {
        m.semillero_id: m.role for m in semillero_repository.memberships_for_user(user_id)
    }
    for semillero in semillero_repository.list_semilleros():
        if semillero.leader_id == user_id:
            roles[semillero.id] = "leader"
    return roles
