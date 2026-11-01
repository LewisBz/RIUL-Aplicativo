from marshmallow import Schema, fields, validate

from app.schemas.engagement import serialize_gamification, serialize_notification
from app.schemas.projects import (
    serialize_product,
    serialize_project_summary,
    serialize_publication,
)
from app.schemas.semilleros import serialize_semillero_summary


class ProfileUpdateSchema(Schema):
    full_name = fields.Str(validate=validate.Length(min=2, max=160, error="El nombre debe tener entre 2 y 160 caracteres."))
    faculty_id = fields.Int(allow_none=True)
    program_id = fields.Int(allow_none=True)


class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8, error="La contraseña debe tener al menos 8 caracteres."),
    )


def serialize_profile(profile: dict, user_payload: dict) -> dict:
    user = profile["user"]
    return {
        "user": user_payload,
        "faculty": {"id": user.faculty.id, "name": user.faculty.name} if user.faculty else None,
        "program": {"id": user.program.id, "name": user.program.name} if user.program else None,
        "semilleros": [
            serialize_semillero_summary(item["semillero"], item["role"])
            for item in profile["semilleros"]
        ],
        "projects": [
            serialize_project_summary(item["project"], item["role"])
            for item in profile["projects"]
        ],
        "publications": [serialize_publication(p) for p in profile["publications"]],
        "products": [
            {**serialize_product(item["product"]), "project": item["project"].slug}
            for item in profile["products"]
        ],
        "gamification": serialize_gamification(profile["gamification"]),
    }


def serialize_dashboard(data: dict) -> dict:
    semillero = data["semillero"]
    return {
        "projects": [serialize_project_summary(p) for p in data["projects"]],
        "publications": [serialize_publication(p) for p in data["publications"]],
        "semillero": (
            {
                **serialize_semillero_summary(semillero),
                "activities_this_month": data["semillero_activities_this_month"],
            }
            if semillero
            else None
        ),
        "notifications": [serialize_notification(n) for n in data["notifications"]],
        "unread_notifications": data["unread_notifications"],
        "gamification": serialize_gamification(data["gamification"]),
    }

