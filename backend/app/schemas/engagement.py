from marshmallow import Schema, fields, validate

from app.schemas.projects import iso


class NotificationListQuerySchema(Schema):
    unread = fields.Bool(load_default=False)


class NotificationUpdateSchema(Schema):
    read = fields.Bool(required=True)


class AchievementCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=160, error="El título debe tener entre 3 y 160 caracteres."))
    description = fields.Str(load_default="")
    icon = fields.Str(load_default="military_tech")
    achieved_on = fields.Date(load_default=None, allow_none=True)


class AchievementReviewSchema(Schema):
    status = fields.Str(required=True)
    xp = fields.Int(load_default=None, allow_none=True, validate=validate.Range(min=0, max=1000, error="XP fuera de rango."))


class AchievementListQuerySchema(Schema):
    status = fields.Str(load_default=None, allow_none=True)


def serialize_notification(n) -> dict:
    return {
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "text": n.text,
        "priority": n.priority,
        "href": n.href,
        "read": n.is_read,
        "created_at": iso(n.created_at),
    }


def serialize_achievement(a, with_user: bool = False) -> dict:
    payload = {
        "id": a.id,
        "icon": a.icon,
        "title": a.title,
        "description": a.description,
        "status": a.status,
        "xp": a.xp,
        "achieved_on": iso(a.achieved_on),
    }
    if with_user:
        payload["user"] = {"id": a.user.id, "full_name": a.user.full_name}
    return payload


def serialize_gamification(summary: dict) -> dict:
    return {
        "level": summary["level"],
        "xp": summary["xp"],
        "next_level_xp": summary["next_level_xp"],
        "total_xp": summary["total_xp"],
        "stars": summary["stars"],
        "total_stars": summary["total_stars"],
        "badges": summary["badges"],
        "achievements": [serialize_achievement(a) for a in summary["achievements"]],
    }


def serialize_ranking(entries, viewer_id: int) -> list[dict]:
    return [
        {
            "position": index,
            "user_id": user.id,
            "full_name": user.full_name,
            "role": user.role,
            "xp": xp,
            "is_current_user": user.id == viewer_id,
        }
        for index, (user, xp) in enumerate(entries, start=1)
    ]


