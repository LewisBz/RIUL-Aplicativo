from app.models import (
    NOTIFICATION_PROJECT,
    PROJECT_PLANNED,
    PROJECT_STATUSES,
    ROLE_ADMINISTRATOR,
    Project,
    ProjectMember,
    ProjectMilestone,
    ProjectProduct,
    User,
)
from app.repositories import project_repository, semillero_repository
from app.services import notification_service
from app.utils.errors import ServiceError
from app.utils.slug import unique_slug


def _clean(value) -> str:
    return (value or "").strip()


def _validate_status(status: str) -> str:
    if status not in PROJECT_STATUSES:
        raise ServiceError("Estado de proyecto inválido.", 400)
    return status


def _is_member(project: Project, user: User) -> bool:
    return project.leader_id == user.id or any(m.user_id == user.id for m in project.members)


def _ensure_member(project: Project, user: User) -> None:
    if user.role != ROLE_ADMINISTRATOR and not _is_member(project, user):
        raise ServiceError("Solo los integrantes del proyecto pueden modificarlo.", 403)


def list_projects(q=None, status=None, semillero_slug=None, member_id=None):
    if status:
        _validate_status(status)
    semillero_id = None
    if semillero_slug:
        semillero = semillero_repository.get_by_slug(semillero_slug)
        if semillero is None:
            raise ServiceError("Semillero no encontrado.", 404)
        semillero_id = semillero.id
    return project_repository.list_projects(_clean(q) or None, status, semillero_id, member_id)


def get_or_404(slug: str) -> Project:
    project = project_repository.get_by_slug(slug)
    if project is None:
        raise ServiceError("Proyecto no encontrado.", 404)
    return project


def create(user: User, data: dict) -> Project:
    title = _clean(data.get("title"))
    if not title:
        raise ServiceError("El título del proyecto es obligatorio.", 400)
    status = _validate_status(data.get("status") or PROJECT_PLANNED)

    semillero_id = None
    if data.get("semillero"):
        semillero = semillero_repository.get_by_slug(data["semillero"])
        if semillero is None:
            raise ServiceError("Semillero no encontrado.", 404)
        is_part = semillero.leader_id == user.id or (
            semillero_repository.get_member(semillero.id, user.id) is not None
        )
        if not is_part and user.role != ROLE_ADMINISTRATOR:
            raise ServiceError("Debes pertenecer al semillero para crear su proyecto.", 403)
        semillero_id = semillero.id

    start, end = data.get("start_date"), data.get("end_date")
    if start and end and end < start:
        raise ServiceError("La fecha de cierre no puede ser anterior al inicio.", 400)

    project = Project(
        slug=unique_slug(title, project_repository.slug_exists, 100),
        title=title,
        type=_clean(data.get("type")) or None,
        status=status,
        description=_clean(data.get("description")) or None,
        line=_clean(data.get("line")) or None,
        role_required=_clean(data.get("role_required")) or None,
        start_date=start,
        end_date=end,
        semillero_id=semillero_id,
        leader_id=user.id,
    )
    project.members.append(ProjectMember(user_id=user.id))
    for position, text in enumerate(data.get("milestones") or []):
        project.milestones.append(ProjectMilestone(text=text, position=position))
    project_repository.add(project)
    project_repository.commit()
    return project


def update(user: User, slug: str, data: dict) -> Project:
    project = get_or_404(slug)
    if user.role != ROLE_ADMINISTRATOR and project.leader_id != user.id:
        raise ServiceError("Solo el líder del proyecto puede editarlo.", 403)
    previous_status = project.status
    if "status" in data:
        project.status = _validate_status(data["status"])
    if "progress" in data:
        project.progress = data["progress"]
    for field in ("description", "line"):
        if field in data:
            setattr(project, field, _clean(data[field]) or None)
    if "end_date" in data:
        project.end_date = data["end_date"]
    if project.status != previous_status:
        for member in project.members:
            if member.user_id != user.id:
                notification_service.notify(
                    member.user_id,
                    NOTIFICATION_PROJECT,
                    "Avance de proyecto",
                    f"«{project.title}» cambió de estado.",
                    href=f"/project-detail?id={project.slug}",
                )
    project_repository.commit()
    return project


def add_product(user: User, slug: str, data: dict) -> ProjectProduct:
    project = get_or_404(slug)
    _ensure_member(project, user)
    type_, name = _clean(data.get("type")), _clean(data.get("name"))
    if not type_ or not name:
        raise ServiceError("Tipo y nombre del producto son obligatorios.", 400)
    product = ProjectProduct(type=type_, name=name)
    project.products.append(product)
    project_repository.commit()
    return product


def set_milestone(user: User, slug: str, milestone_id: int, done: bool) -> ProjectMilestone:
    project = get_or_404(slug)
    _ensure_member(project, user)
    milestone = project_repository.get_milestone(project.id, milestone_id)
    if milestone is None:
        raise ServiceError("Hito no encontrado.", 404)
    milestone.done = done
    if project.milestones:
        project.progress = round(
            100 * sum(1 for m in project.milestones if m.done) / len(project.milestones)
        )
    project_repository.commit()
    return milestone


def viewer_role(project: Project, user: User) -> str | None:
    if project.leader_id == user.id:
        return "leader"
    return "member" if _is_member(project, user) else None
