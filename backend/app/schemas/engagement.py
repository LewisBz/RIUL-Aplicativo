from marshmallow import Schema, fields, validate

from app.schemas.projects import iso


class NotificationListQuerySchema(Schema):
    unread = fields.Bool(load_default=False)


class NotificationUpdateSchema(Schema):
    read = fields.Bool(required=True)


class AchievementCreateSchema(Schema):
    """Un logro nace de exactamente un origen; el tipo se deduce de él."""

    type = fields.Str(load_default=None, allow_none=True)
    event = fields.Str(load_default=None, allow_none=True)
    post = fields.Raw(load_default=None, allow_none=True)
    project = fields.Str(load_default=None, allow_none=True)
    product = fields.Raw(load_default=None, allow_none=True)
    semillero = fields.Str(load_default=None, allow_none=True)
    title = fields.Str(load_default="", validate=validate.Length(max=160, error="El título no puede superar 160 caracteres."))
    description = fields.Str(load_default="")
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
        "entity": {"kind": n.entity_kind, "id": n.entity_id} if n.entity_kind else None,
        "read": n.is_read,
        "read_at": iso(n.read_at),
        "created_at": iso(n.created_at),
    }


def _origin(a) -> dict:
    if a.event_id:
        return {"kind": "event", "id": a.event_id, "label": a.event.title, "slug": a.event.slug}
    if a.post_id:
        return {"kind": "post", "id": a.post_id, "label": f"Publicación #{a.post_id}"}
    if a.project_id:
        return {"kind": "project", "id": a.project_id, "label": a.project.title, "slug": a.project.slug}
    if a.product_id:
        return {"kind": "product", "id": a.product_id, "label": a.product.title}
    return {"kind": "semillero", "id": a.semillero_id, "label": a.semillero.name, "slug": a.semillero.slug}


def serialize_achievement(a, with_user: bool = False) -> dict:
    payload = {
        "id": a.id,
        "type": a.type.code,
        "icon": a.icon,
        "title": a.display_title,
        "description": a.description,
        "status": a.status,
        "xp": a.xp,
        "achieved_on": iso(a.achieved_on),
        "origin": _origin(a),
        "evidence_count": len(a.evidences),
        "validated_at": iso(a.validated_at),
    }
    if with_user:
        payload["user"] = {"id": a.user.id, "full_name": a.user.full_name}
    return payload


def serialize_evidence(evidence) -> dict:
    return {
        "id": evidence.id,
        "achievement_id": evidence.achievement_id,
        "file_name": evidence.file_name,
        "mime_type": evidence.mime_type,
        "file_size": evidence.file_size,
        "url": f"/api/gamification/evidences/{evidence.storage_name}",
    }


def serialize_achievement_type(t) -> dict:
    return {
        "code": t.code,
        "name": t.name,
        "icon": t.icon,
        "xp_value": t.xp_value,
        "badge": {"name": t.badge.name, "icon": t.badge.icon} if t.badge else None,
    }


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
