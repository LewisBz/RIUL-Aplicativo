import re
from datetime import date

from app.models import PRODUCT_ARTICLE, PRODUCT_STATUSES, Product, User
from app.repositories import (
    engagement_repository,
    project_repository,
    semillero_repository,
)
from app.services import gamification_service
from app.services.auth_service import resolve_faculty_program
from app.utils.errors import ServiceError

MIN_PASSWORD_LENGTH = 8
DASHBOARD_ITEMS = 5
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
MAX_BIO_LENGTH = 2000


def _clean(value) -> str:
    return (value or "").strip()


def _projects_of(user: User):
    return project_repository.list_projects(member_id=user.id)


def get_profile(user: User) -> dict:
    projects = _projects_of(user)
    return {
        "user": user,
        "semilleros": [
            {"semillero": m.semillero, "role": m.role}
            for m in semillero_repository.memberships_for_user(user.id)
        ],
        "projects": [
            {"project": p, "role": "leader" if p.leader_id == user.id else "member"}
            for p in projects
        ],
        "publications": project_repository.list_user_publications(user.id),
        "products": [
            {"project": p, "product": product} for p in projects for product in p.products
        ],
        "gamification": gamification_service.summary(user.id),
    }


def _validate_orcid(raw: str) -> str | None:
    orcid = _clean(raw).upper()
    if not orcid:
        return None
    if not ORCID_RE.match(orcid):
        raise ServiceError("El ORCID debe tener el formato 0000-0000-0000-0000.", 400)
    return orcid


def _validate_photo(raw: str) -> str | None:
    photo = _clean(raw)
    if not photo:
        return None
    if not photo.lower().startswith(("http://", "https://", "/")):
        raise ServiceError("La foto debe ser una URL http(s) o una ruta del sitio.", 400)
    return photo


def update_profile(user: User, data: dict) -> User:
    if "full_name" in data:
        name = _clean(data["full_name"])
        if not name:
            raise ServiceError("El nombre no puede estar vacío.", 400)
        user.full_name = name
    if "faculty_id" in data or "program_id" in data:
        faculty_id, program_id = resolve_faculty_program(
            {
                "faculty_id": data.get("faculty_id", user.faculty_id),
                "program_id": data.get("program_id"),
            }
        )
        user.faculty_id, user.program_id = faculty_id, program_id
    if {"bio", "photo", "orcid"} & data.keys():
        profile = user.ensure_profile()
        if "bio" in data:
            bio = _clean(data["bio"])
            if len(bio) > MAX_BIO_LENGTH:
                raise ServiceError(f"La biografía no puede superar {MAX_BIO_LENGTH} caracteres.", 400)
            profile.bio = bio or None
        if "photo" in data:
            profile.photo = _validate_photo(data["photo"])
        if "orcid" in data:
            profile.orcid = _validate_orcid(data["orcid"])
    project_repository.commit()
    return user


def change_password(user: User, current: str, new: str) -> None:
    if not user.check_password(current or ""):
        raise ServiceError("La contraseña actual es incorrecta.", 400)
    if not new or len(new) < MIN_PASSWORD_LENGTH:
        raise ServiceError(
            f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.", 400
        )
    user.set_password(new)
    project_repository.commit()


def add_publication(user: User, data: dict) -> Product:
    """Registra un artículo propio (producto de tipo `article`)."""
    title = _clean(data.get("title"))
    if not title:
        raise ServiceError("El título de la publicación es obligatorio.", 400)
    status = data.get("status") or "in_review"
    if status not in PRODUCT_STATUSES:
        raise ServiceError("Estado de publicación inválido.", 400)
    semillero_id = None
    if data.get("semillero"):
        semillero = semillero_repository.get_by_slug(data["semillero"])
        if semillero is None:
            raise ServiceError("Semillero no encontrado.", 404)
        semillero_id = semillero.id
    product = project_repository.add_product(
        Product(
            user_id=user.id,
            semillero_id=semillero_id,
            type=PRODUCT_ARTICLE,
            title=title,
            venue=_clean(data.get("venue")) or None,
            published_on=data.get("published_on"),
            status=status,
        )
    )
    project_repository.commit()
    return product


def get_dashboard(user: User) -> dict:
    memberships = semillero_repository.memberships_for_user(user.id)
    semillero = memberships[0].semillero if memberships else None
    activities = (
        semillero_repository.count_activities_since(semillero.id, date.today().replace(day=1))
        if semillero
        else 0
    )
    notifications = engagement_repository.list_notifications(user.id, limit=DASHBOARD_ITEMS)
    return {
        "projects": _projects_of(user)[:DASHBOARD_ITEMS],
        "publications": project_repository.list_user_publications(user.id, DASHBOARD_ITEMS),
        "semillero": semillero,
        "semillero_activities_this_month": activities,
        "notifications": notifications,
        "unread_notifications": engagement_repository.count_unread(user.id),
        "gamification": gamification_service.summary(user.id),
    }
