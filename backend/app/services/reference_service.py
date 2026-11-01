from app.extensions import db
from app.models import AchievementType, Badge, Level
from app.reference_data import ACHIEVEMENT_TYPES, BADGES, LEVELS


def seed_reference_data() -> int:
    """Crea o actualiza niveles, insignias y tipos de logro (idempotente).

    Devuelve cuántos registros nuevos se crearon. No hace commit.
    """
    created = 0
    for number, min_xp, stars in LEVELS:
        level = Level.query.filter_by(level_number=number).first()
        if level is None:
            db.session.add(Level(level_number=number, min_xp=min_xp, stars=stars))
            created += 1
        else:
            level.min_xp, level.stars = min_xp, stars

    badges = {}
    for name, description, icon in BADGES:
        badge = Badge.query.filter_by(name=name).first()
        if badge is None:
            badge = Badge(name=name, description=description, icon=icon)
            db.session.add(badge)
            created += 1
        else:
            badge.description, badge.icon = description, icon
        badges[name] = badge
    db.session.flush()

    for code, name, icon, xp_value, badge_name in ACHIEVEMENT_TYPES:
        achievement_type = AchievementType.query.filter_by(code=code).first()
        if achievement_type is None:
            achievement_type = AchievementType(code=code)
            db.session.add(achievement_type)
            created += 1
        achievement_type.name = name
        achievement_type.icon = icon
        achievement_type.xp_value = xp_value
        achievement_type.badge_id = badges[badge_name].id
    db.session.flush()
    return created
