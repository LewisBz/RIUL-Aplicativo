from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers.http import json_error, load_schema
from app.models import ROLE_ADMINISTRATOR, STATUS_ACTIVE
from app.repositories import user_repository
from app.schemas import (
    AchievementListQuerySchema,
    AchievementReviewSchema,
    AdminUsersQuerySchema,
    UserSchema,
    UserStatusSchema,
    serialize_achievement,
)
from app.services import admin_service, gamification_service
from app.utils.errors import ServiceError


def require_administrator(view):
    @wraps(view)
    @jwt_required()
    def wrapped(*args, **kwargs):
        try:
            user_id = int(get_jwt_identity())
        except (TypeError, ValueError):
            return json_error("Token inválido.", 401)
        user = user_repository.get_user_by_id(user_id)
        if user is None or user.status != STATUS_ACTIVE:
            return json_error("Cuenta no disponible.", 401)
        if user.role != ROLE_ADMINISTRATOR:
            return json_error("Se requieren permisos de administrador.", 403)
        return view(*args, **kwargs)

    return wrapped


@require_administrator
def get_overview():
    return jsonify(admin_service.overview()), 200


@require_administrator
def get_analytics():
    return jsonify(admin_service.analytics()), 200


@require_administrator
def get_users():
    query = load_schema(
        AdminUsersQuerySchema(),
        {k: request.args[k] for k in ("status", "role", "q") if request.args.get(k)},
    )
    try:
        users = admin_service.list_users(
            status=query.get("status"), role=query.get("role"), q=query.get("q")
        )
    except ValueError as error:
        return json_error(str(error), 400)
    return jsonify(items=UserSchema(many=True).dump(users), total=len(users)), 200


@require_administrator
def patch_user(user_id: int):
    data = load_schema(UserStatusSchema(), request.get_json(silent=True) or {})
    try:
        actor_id = int(get_jwt_identity())
        user = admin_service.update_user_status(actor_id, user_id, data.get("status"))
    except ValueError as error:
        return json_error(str(error), 400)
    except LookupError as error:
        return json_error(str(error), 404)
    except PermissionError as error:
        return json_error(str(error), 403)
    return jsonify(user=UserSchema().dump(user)), 200


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)


@require_administrator
def get_achievements():
    query = load_schema(
        AchievementListQuerySchema(),
        {"status": request.args["status"]} if request.args.get("status") else {},
    )
    achievements = gamification_service.list_for_review(query.get("status"))
    items = [serialize_achievement(a, with_user=True) for a in achievements]
    return jsonify(items=items, total=len(items)), 200


@require_administrator
def patch_achievement(achievement_id: int):
    data = load_schema(AchievementReviewSchema(), request.get_json(silent=True) or {})
    actor = user_repository.get_user_by_id(int(get_jwt_identity()))
    achievement = gamification_service.review(
        actor, achievement_id, data["status"], data.get("xp")
    )
    return jsonify(achievement=serialize_achievement(achievement, with_user=True)), 200
