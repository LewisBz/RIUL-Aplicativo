"""Logros, XP y niveles.

Un solo flujo: un logro aprobado por la administración genera un asiento en
`xp_ledger`; de ahí se derivan `user_progress` (XP, nivel y estrellas),
`user_badges` y `semillero_progress`. El ranking en vivo se calcula con
``ORDER BY user_progress.xp`` y no se almacena.
"""
from datetime import date, datetime, timezone

from app.models import (
    ACHIEVEMENT_APPROVED,
    ACHIEVEMENT_PENDING,
    ACHIEVEMENT_REJECTED,
    ACHIEVEMENT_STATUSES,
    MAX_STARS,
    MEMBERSHIP_ACTIVE,
    NOTIFICATION_ACHIEVEMENT,
    PRIORITY_HIGH,
    PRODUCT_ARTICLE,
    PRODUCT_PATENT,
    PRODUCT_PRESENTATION,
    ROLE_ADMINISTRATOR,
    TYPE_ARTICLE,
    TYPE_EVENT,
    TYPE_PATENT,
    TYPE_POST,
    TYPE_PRESENTATION,
    TYPE_PROJECT,
    TYPE_SEMILLERO,
    Achievement,
    Evidence,
    Level,
    SemilleroProgress,
    User,
    UserBadge,
    UserProgress,
    XpLedger,
)
from app.reference_data import XP_PER_LEVEL
from app.repositories import (
    event_repository,
    gamification_repository,
    post_repository,
    project_repository,
    semillero_repository,
)
from app.services import notification_service, reference_service
from app.utils.errors import ServiceError
from app.utils.uploads import save_upload

LEVEL_XP = XP_PER_LEVEL
EVENT_PARTICIPATION_XP = 20  # valor de referencia del tipo `event`

_PRODUCT_TYPE_TO_ACHIEVEMENT = {
    PRODUCT_ARTICLE: TYPE_ARTICLE,
    PRODUCT_PRESENTATION: TYPE_PRESENTATION,
    PRODUCT_PATENT: TYPE_PATENT,
}


def _clean(value) -> str:
    return (value or "").strip()


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# --- Niveles ---
def _levels() -> list[Level]:
    levels = gamification_repository.list_levels()
    if not levels:  # base sin catálogo: lo siembra una sola vez
        reference_service.seed_reference_data()
        levels = gamification_repository.list_levels()
    return levels


def level_for_xp(total_xp: int) -> Level:
    levels = _levels()
    current = levels[0]
    for level in levels:
        if level.min_xp <= total_xp:
            current = level
    return current


def level_progress(total_xp: int) -> dict:
    levels = _levels()
    current = level_for_xp(total_xp)
    following = next((lv for lv in levels if lv.level_number == current.level_number + 1), None)
    span = following.min_xp - current.min_xp if following else LEVEL_XP
    return {
        "level": current.level_number,
        "xp": total_xp - current.min_xp,
        "next_level_xp": span,
        "total_xp": total_xp,
        "stars": current.stars,
        "total_stars": MAX_STARS,
    }


def _get_or_create_user_progress(user_id: int) -> UserProgress:
    progress = gamification_repository.get_user_progress(user_id)
    if progress is None:
        first = _levels()[0]
        progress = gamification_repository.add(
            UserProgress(user_id=user_id, xp=0, level_id=first.id, stars=first.stars)
        )
    return progress


def _get_or_create_semillero_progress(semillero_id: int) -> SemilleroProgress:
    progress = gamification_repository.get_semillero_progress(semillero_id)
    if progress is None:
        progress = gamification_repository.add(
            SemilleroProgress(semillero_id=semillero_id, xp=0, level_id=_levels()[0].id)
        )
    return progress


def ensure_semillero_progress(semillero_id: int) -> SemilleroProgress:
    """Crea la fila de progreso de un semillero nuevo (nivel 1, 0 XP)."""
    return _get_or_create_semillero_progress(semillero_id)


# --- Consulta ---
def summary(user_id: int) -> dict:
    achievements = gamification_repository.list_achievements(user_id=user_id)
    progress = gamification_repository.get_user_progress(user_id)
    data = level_progress(progress.xp if progress else 0)
    badges = [
        {
            "icon": user_badge.badge.icon,
            "title": user_badge.badge.name,
            "highlighted": user_badge.achievement.xp >= 100,
        }
        for user_badge in gamification_repository.list_user_badges(user_id)[:6]
    ]
    return {**data, "badges": badges, "achievements": achievements}


def ranking(limit: int = 20) -> list[tuple[User, int]]:
    return gamification_repository.ranking(max(1, min(limit, 100)))


def catalog() -> dict:
    return {"types": gamification_repository.list_types()}


# --- Registro de logros ---
def _resolve_origin(user: User, data: dict) -> tuple[str, int, str]:
    """Valida el origen único del logro y devuelve (columna, id, código de tipo)."""
    given = {
        key: data.get(key)
        for key in ("event", "post", "project", "product", "semillero")
        if data.get(key) not in (None, "")
    }
    if len(given) != 1:
        raise ServiceError(
            "Indica exactamente un origen del logro: evento, publicación, proyecto, "
            "producto o semillero.",
            400,
        )
    kind, ref = next(iter(given.items()))

    if kind == "event":
        event = event_repository.get_event_by_slug(str(ref))
        if event is None:
            raise ServiceError("Evento no encontrado.", 404)
        if event_repository.get_participation(event.id, user.id) is None:
            raise ServiceError("Solo puedes registrar logros de eventos en los que participaste.", 403)
        return "event_id", event.id, TYPE_EVENT

    if kind == "post":
        post = post_repository.get_post(_as_int(ref, "publicación"))
        if post is None:
            raise ServiceError("Publicación no encontrada.", 404)
        if post.author_id != user.id:
            raise ServiceError("Solo el autor puede registrar un logro de su publicación.", 403)
        return "post_id", post.id, TYPE_POST

    if kind == "project":
        project = project_repository.get_by_slug(str(ref))
        if project is None:
            raise ServiceError("Proyecto no encontrado.", 404)
        if project_repository.get_member(project.id, user.id) is None:
            raise ServiceError("Solo los integrantes pueden registrar logros del proyecto.", 403)
        return "project_id", project.id, TYPE_PROJECT

    if kind == "product":
        product = project_repository.get_product(_as_int(ref, "producto"))
        if product is None:
            raise ServiceError("Producto no encontrado.", 404)
        if product.user_id != user.id:
            raise ServiceError("Solo el responsable del producto puede registrar su logro.", 403)
        type_code = _PRODUCT_TYPE_TO_ACHIEVEMENT.get(product.type)
        if type_code is None:
            raise ServiceError("Este tipo de producto no genera logros.", 400)
        return "product_id", product.id, type_code

    semillero = semillero_repository.get_by_slug(str(ref))
    if semillero is None:
        raise ServiceError("Semillero no encontrado.", 404)
    member = semillero_repository.get_member(semillero.id, user.id)
    if member is None or member.status != MEMBERSHIP_ACTIVE:
        raise ServiceError("Solo los miembros activos pueden registrar logros del semillero.", 403)
    return "semillero_id", semillero.id, TYPE_SEMILLERO


def _as_int(value, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ServiceError(f"Identificador de {label} inválido.", 400)


def register_achievement(user: User, data: dict) -> Achievement:
    column, origin_id, type_code = _resolve_origin(user, data)
    requested = _clean(data.get("type"))
    if requested and requested != type_code:
        raise ServiceError("El tipo de logro no corresponde al origen indicado.", 400)
    achievement_type = gamification_repository.get_type_by_code(type_code)
    if achievement_type is None:
        _levels()  # asegura el catálogo
        achievement_type = gamification_repository.get_type_by_code(type_code)
    if gamification_repository.achievement_exists(user.id, achievement_type.id, column, origin_id):
        raise ServiceError("Ya registraste un logro para este origen.", 409)
    achievement = gamification_repository.add(
        Achievement(
            user_id=user.id,
            type_id=achievement_type.id,
            status=ACHIEVEMENT_PENDING,
            title=_clean(data.get("title")) or None,
            description=_clean(data.get("description")) or None,
            achieved_on=data.get("achieved_on") or date.today(),
            **{column: origin_id},
        )
    )
    gamification_repository.commit()
    return achievement


def award_event_participation(user_id: int, event) -> Achievement | None:
    """Logro pendiente de participación al inscribirse en un evento.

    No hace commit: lo realiza el servicio llamador.
    """
    achievement_type = gamification_repository.get_type_by_code(TYPE_EVENT)
    if achievement_type is None:
        reference_service.seed_reference_data()
        achievement_type = gamification_repository.get_type_by_code(TYPE_EVENT)
    if gamification_repository.achievement_exists(
        user_id, achievement_type.id, "event_id", event.id
    ):
        return None
    return gamification_repository.add(
        Achievement(
            user_id=user_id,
            type_id=achievement_type.id,
            status=ACHIEVEMENT_PENDING,
            event_id=event.id,
            title=f"Participación en {event.title}"[:160],
            description="Pendiente de validación por la Dirección de Investigación.",
            achieved_on=date.today(),
        )
    )


def add_evidence(user: User, achievement_id: int, file) -> Evidence:
    achievement = gamification_repository.get_achievement(achievement_id)
    if achievement is None:
        raise ServiceError("Logro no encontrado.", 404)
    if achievement.user_id != user.id:
        raise ServiceError("Solo el dueño del logro puede adjuntar evidencias.", 403)
    if file is None or not getattr(file, "filename", ""):
        raise ServiceError("Adjunta un archivo como evidencia.", 400)
    stored = save_upload(file, "evidences")
    stored.pop("kind")
    evidence = Evidence(achievement_id=achievement.id, **stored)
    gamification_repository.add_evidence(evidence)
    gamification_repository.commit()
    return evidence


def get_evidence_for_download(user: User, storage_name: str) -> Evidence:
    """Las evidencias son privadas: solo su dueño o un administrador."""
    evidence = gamification_repository.get_evidence_by_storage_name(storage_name)
    if evidence is None:
        raise ServiceError("Evidencia no encontrada.", 404)
    if evidence.achievement.user_id != user.id and user.role != ROLE_ADMINISTRATOR:
        raise ServiceError("No tienes acceso a esta evidencia.", 403)
    return evidence


# --- Revisión (administración) ---
def list_for_review(status: str | None = None) -> list[Achievement]:
    if status and status not in ACHIEVEMENT_STATUSES:
        raise ServiceError("Estado de logro inválido.", 400)
    return gamification_repository.list_achievements(status=status)


def _credited_semillero_id(achievement: Achievement) -> int | None:
    """Semillero que recibe el XP: explícito, de origen o el del recurso origen."""
    if achievement.xp_semillero_id:
        return achievement.xp_semillero_id
    if achievement.semillero_id:
        return achievement.semillero_id
    for related in (achievement.project, achievement.event):
        if related is not None and related.semillero_id:
            return related.semillero_id
    product = achievement.product
    if product is not None:
        if product.semillero_id:
            return product.semillero_id
        if product.project is not None:
            return product.project.semillero_id
    return None


def apply_approval(achievement: Achievement, amount: int) -> XpLedger:
    """Registra el asiento de XP de un logro ya marcado como aprobado.

    Actualiza `user_progress`, la insignia del tipo y `semillero_progress`.
    No hace commit.
    """
    ledger = gamification_repository.add(
        XpLedger(user_id=achievement.user_id, achievement=achievement, amount=amount)
    )
    semillero_id = _credited_semillero_id(achievement)
    if semillero_id and not achievement.xp_semillero_id:
        achievement.xp_semillero_id = semillero_id
    gamification_repository.flush()

    progress = _get_or_create_user_progress(achievement.user_id)
    progress.xp = gamification_repository.user_ledger_total(achievement.user_id)
    level = level_for_xp(progress.xp)
    progress.level_id, progress.stars = level.id, level.stars

    badge_id = achievement.type.badge_id
    if badge_id and not gamification_repository.user_badge_exists(achievement.user_id, badge_id):
        gamification_repository.add(
            UserBadge(user_id=achievement.user_id, badge_id=badge_id, achievement_id=achievement.id)
        )

    if semillero_id:
        sem_progress = _get_or_create_semillero_progress(semillero_id)
        sem_progress.xp = gamification_repository.semillero_ledger_total(semillero_id)
        sem_progress.level_id = level_for_xp(sem_progress.xp).id
    gamification_repository.flush()
    return ledger


def review(actor: User, achievement_id: int, status: str, xp: int | None) -> Achievement:
    if actor.role != ROLE_ADMINISTRATOR:
        raise ServiceError("Se requieren permisos de administrador.", 403)
    if status not in (ACHIEVEMENT_APPROVED, ACHIEVEMENT_REJECTED):
        raise ServiceError("Estado de logro inválido.", 400)
    achievement = gamification_repository.get_achievement(achievement_id)
    if achievement is None:
        raise ServiceError("Logro no encontrado.", 404)
    if achievement.status != ACHIEVEMENT_PENDING:
        raise ServiceError("El logro ya fue revisado.", 409)

    achievement.status = status
    achievement.validated_by = actor.id
    achievement.validated_at = _now()
    if status == ACHIEVEMENT_APPROVED:
        apply_approval(achievement, xp if xp is not None else achievement.type.xp_value)
    verdict = "aprobado" if status == ACHIEVEMENT_APPROVED else "rechazado"
    notification_service.notify(
        achievement.user_id,
        NOTIFICATION_ACHIEVEMENT,
        f"Logro {verdict}",
        f"Tu logro «{achievement.display_title}» fue {verdict}.",
        href="/gamification",
        priority=PRIORITY_HIGH,
        entity=("achievement", achievement.id),
    )
    gamification_repository.commit()
    return achievement
