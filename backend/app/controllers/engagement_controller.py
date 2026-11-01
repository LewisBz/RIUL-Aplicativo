from flask import jsonify, request

from app.controllers.guards import active_user_required, items_response
from app.controllers.http import json_error, load_schema, query_args
from app.schemas import (
    AchievementCreateSchema,
    NotificationListQuerySchema,
    NotificationUpdateSchema,
    serialize_achievement,
    serialize_gamification,
    serialize_notification,
    serialize_ranking,
)
from app.services import gamification_service, notification_service
from app.utils.errors import ServiceError


# --- Notificaciones ---
@active_user_required
def list_notifications(user):
    query = load_schema(
        NotificationListQuerySchema(), query_args(request, "unread")
    )
    items, unread = notification_service.list_notifications(user.id, query["unread"])
    return items_response([serialize_notification(n) for n in items], unread_count=unread)


@active_user_required
def update_notification(user, notification_id: int):
    data = load_schema(NotificationUpdateSchema(), request.get_json(silent=True) or {})
    notification = notification_service.mark_read(user.id, notification_id, data["read"])
    return jsonify(notification=serialize_notification(notification)), 200


@active_user_required
def read_all_notifications(user):
    notification_service.mark_all_read(user.id)
    return jsonify(unread_count=0), 200


# --- Gamificación ---
@active_user_required
def get_my_gamification(user):
    return jsonify(gamification=serialize_gamification(gamification_service.summary(user.id))), 200


@active_user_required
def get_ranking(user):
    entries = gamification_service.ranking(request.args.get("limit", 20, type=int))
    return items_response(serialize_ranking(entries, user.id))


@active_user_required
def create_achievement(user):
    data = load_schema(AchievementCreateSchema(), request.get_json(silent=True) or {})
    achievement = gamification_service.register_achievement(user, data)
    return jsonify(achievement=serialize_achievement(achievement)), 201


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)

