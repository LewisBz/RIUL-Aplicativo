from datetime import date

from app.models import (
    ACHIEVEMENT_IN_REVIEW,
    ACHIEVEMENT_REJECTED,
    ACHIEVEMENT_VALIDATED,
    NOTIFICATION_ACHIEVEMENT,
    PRIORITY_HIGH,
    ROLE_ADMINISTRATOR,
    Achievement,
    User,
)
from app.repositories import engagement_repository
from app.services import notification_service
from app.utils.errors import ServiceError

LEVEL_XP = 200
MAX_STARS = 5
EVENT_PARTICIPATION_XP = 20


def _clean(value) -> str:
    return (value or "").strip()


def level_progress(total_xp: int) -> dict:
    level = total_xp // LEVEL_XP + 1
    return {
        "level": level,
        "xp": total_xp % LEVEL_XP,
        "next_level_xp": LEVEL_XP,
        "total_xp": total_xp,
        "stars": min(MAX_STARS, level),
        "total_stars": MAX_STARS,
    }


def summary(user_id: int) -> dict:
    achievements = engagement_repository.list_achievements(user_id=user_id)
    validated = [a for a in achievements if a.status == ACHIEVEMENT_VALIDATED]
    progress = level_progress(sum(a.xp for a in validated))
    badges = [
        {"icon": a.icon, "title": a.title, "highlighted": a.xp >= 100}
        for a in validated[:6]
    ]
    return {**progress, "badges": badges, "achievements": achievements}


def ranking(limit: int = 20) -> list[tuple[User, int]]:
    return engagement_repository.ranking(max(1, min(limit, 100)))


def award(
    user_id: int,
    title: str,
    description: str,
    xp: int,
    icon: str = "military_tech",
    status: str = ACHIEVEMENT_IN_REVIEW,
    achieved_on: date | None = None,
) -> Achievement:
    """Crea un logro. El commit lo realiza el servicio llamador."""
    return engagement_repository.add_achievement(
        Achievement(
            user_id=user_id,
            title=title,
            description=description,
            xp=xp,
            icon=icon,
            status=status,
            achieved_on=achieved_on or date.today(),
        )
    )


def register_achievement(user: User, data: dict) -> Achievement:
    title = _clean(data.get("title"))
    if not title:
        raise ServiceError("El título del logro es obligatorio.", 400)
    achievement = award(
        user.id,
        title=title,
        description=_clean(data.get("description")),
        xp=0,
        icon=_clean(data.get("icon")) or "military_tech",
        achieved_on=data.get("achieved_on"),
    )
    engagement_repository.commit()
    return achievement


def list_for_review(status: str | None = None) -> list[Achievement]:
    if status and status not in (
        ACHIEVEMENT_IN_REVIEW,
        ACHIEVEMENT_VALIDATED,
        ACHIEVEMENT_REJECTED,
    ):
        raise ServiceError("Estado de logro inválido.", 400)
    return engagement_repository.list_achievements(status=status)


def review(actor: User, achievement_id: int, status: str, xp: int | None) -> Achievement:
    if actor.role != ROLE_ADMINISTRATOR:
        raise ServiceError("Se requieren permisos de administrador.", 403)
    if status not in (ACHIEVEMENT_VALIDATED, ACHIEVEMENT_REJECTED):
        raise ServiceError("Estado de logro inválido.", 400)
    achievement = engagement_repository.get_achievement(achievement_id)
    if achievement is None:
        raise ServiceError("Logro no encontrado.", 404)
    achievement.status = status
    if status == ACHIEVEMENT_VALIDATED:
        if xp is not None:
            achievement.xp = xp
        elif achievement.xp == 0:
            achievement.xp = 50
    verdict = "validado" if status == ACHIEVEMENT_VALIDATED else "rechazado"
    notification_service.notify(
        achievement.user_id,
        NOTIFICATION_ACHIEVEMENT,
        f"Logro {verdict}",
        f"Tu logro «{achievement.title}» fue {verdict}.",
        href="/gamification",
        priority=PRIORITY_HIGH,
    )
    engagement_repository.commit()
    return achievement
