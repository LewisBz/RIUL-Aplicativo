from sqlalchemy import func, select

from app.extensions import db
from app.models import (
    ACHIEVEMENT_APPROVED,
    ROLE_ADMINISTRATOR,
    STATUS_ACTIVE,
    Achievement,
    AchievementType,
    Badge,
    Evidence,
    Level,
    SemilleroProgress,
    User,
    UserBadge,
    UserProgress,
    XpLedger,
)


def add(entity):
    db.session.add(entity)
    return entity


# --- Catálogos ---
def list_levels() -> list[Level]:
    return list(db.session.scalars(select(Level).order_by(Level.level_number)).all())


def get_badge_by_name(name: str) -> Badge | None:
    return db.session.scalar(select(Badge).where(Badge.name == name))


def get_type_by_code(code: str) -> AchievementType | None:
    return db.session.scalar(select(AchievementType).where(AchievementType.code == code))


def list_types() -> list[AchievementType]:
    return list(db.session.scalars(select(AchievementType).order_by(AchievementType.id)).all())


def get_level_by_number(number: int) -> Level | None:
    return db.session.scalar(select(Level).where(Level.level_number == number))


# --- Logros ---
def get_achievement(achievement_id: int) -> Achievement | None:
    return db.session.get(Achievement, achievement_id)


def list_achievements(user_id: int | None = None, status: str | None = None):
    stmt = select(Achievement).order_by(Achievement.achieved_on.desc(), Achievement.id.desc())
    if user_id:
        stmt = stmt.where(Achievement.user_id == user_id)
    if status:
        stmt = stmt.where(Achievement.status == status)
    return list(db.session.scalars(stmt).all())


def achievement_exists(user_id: int, type_id: int, origin_column: str, origin_id: int) -> bool:
    column = getattr(Achievement, origin_column)
    return (
        db.session.scalar(
            select(Achievement.id).where(
                Achievement.user_id == user_id,
                Achievement.type_id == type_id,
                column == origin_id,
            )
        )
        is not None
    )


def count_achievements(status: str | None = None) -> int:
    stmt = select(func.count()).select_from(Achievement)
    if status:
        stmt = stmt.where(Achievement.status == status)
    return int(db.session.scalar(stmt) or 0)


def total_approved_xp() -> int:
    return int(db.session.scalar(select(func.coalesce(func.sum(XpLedger.amount), 0))) or 0)


def add_evidence(evidence: Evidence) -> Evidence:
    db.session.add(evidence)
    return evidence


# --- Progreso de usuario ---
def get_evidence_by_storage_name(storage_name: str) -> Evidence | None:
    return db.session.scalar(select(Evidence).where(Evidence.storage_name == storage_name))


def get_user_progress(user_id: int) -> UserProgress | None:
    return db.session.scalar(select(UserProgress).where(UserProgress.user_id == user_id))


def user_ledger_total(user_id: int) -> int:
    return int(
        db.session.scalar(
            select(func.coalesce(func.sum(XpLedger.amount), 0)).where(XpLedger.user_id == user_id)
        )
        or 0
    )


def user_badge_exists(user_id: int, badge_id: int) -> bool:
    return (
        db.session.scalar(
            select(UserBadge.id).where(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
        )
        is not None
    )


def list_user_badges(user_id: int) -> list[UserBadge]:
    stmt = select(UserBadge).where(UserBadge.user_id == user_id).order_by(UserBadge.id)
    return list(db.session.scalars(stmt).all())


def ranking(limit: int) -> list[tuple[User, int]]:
    xp = func.coalesce(UserProgress.xp, 0).label("xp")
    stmt = (
        select(User, xp)
        .outerjoin(UserProgress, UserProgress.user_id == User.id)
        .where(User.status == STATUS_ACTIVE, User.role != ROLE_ADMINISTRATOR)
        .order_by(xp.desc(), User.full_name)
        .limit(limit)
    )
    return [(row[0], int(row[1])) for row in db.session.execute(stmt).all()]


# --- Progreso de semillero ---
def get_semillero_progress(semillero_id: int) -> SemilleroProgress | None:
    return db.session.scalar(
        select(SemilleroProgress).where(SemilleroProgress.semillero_id == semillero_id)
    )


def semillero_ledger_total(semillero_id: int) -> int:
    """XP del semillero: asientos de logros aprobados acreditados al semillero."""
    return int(
        db.session.scalar(
            select(func.coalesce(func.sum(XpLedger.amount), 0))
            .join(Achievement, Achievement.id == XpLedger.achievement_id)
            .where(
                Achievement.xp_semillero_id == semillero_id,
                Achievement.status == ACHIEVEMENT_APPROVED,
            )
        )
        or 0
    )


def commit() -> None:
    db.session.commit()


def flush() -> None:
    db.session.flush()
