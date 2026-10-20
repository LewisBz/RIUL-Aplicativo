from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers.http import json_error
from app.extensions import db
from app.models import User
from app.services import workflow_service
from app.utils.errors import ServiceError


def _user_id() -> int:
    return int(get_jwt_identity())


def _guard(fn):
    try:
        return fn()
    except ServiceError as error:
        return json_error(error.message, error.status)


@jwt_required()
def list_comments(post_id: int):
    return jsonify(items=workflow_service.list_comments(post_id)), 200


@jwt_required()
def create_comment(post_id: int):
    body = (request.get_json(silent=True) or {}).get("body")
    return _guard(lambda: (jsonify(comment=workflow_service.add_comment(_user_id(), post_id, body)), 201))


@jwt_required()
def join_semillero(identifier: str):
    from app.services import semillero_service

    semillero = semillero_service.get_semillero(identifier)
    if semillero is None:
        return json_error("Semillero no encontrado.", 404)
    payload = request.get_json(silent=True) or {}

    def run():
        return jsonify(
            workflow_service.join_semillero(
                _user_id(), semillero.id, payload.get("motivation")
            )
        ), 201

    return _guard(run)


@jwt_required()
def follow_semillero(identifier: str):
    from app.services import semillero_service

    semillero = semillero_service.get_semillero(identifier)
    if semillero is None:
        return json_error("Semillero no encontrado.", 404)
    return _guard(lambda: (jsonify(workflow_service.follow_semillero(_user_id(), semillero.id)), 200))


@jwt_required()
def review_member(identifier: str, user_id: int):
    from app.services import semillero_service

    semillero = semillero_service.get_semillero(identifier)
    if semillero is None:
        return json_error("Semillero no encontrado.", 404)
    status = (request.get_json(silent=True) or {}).get("status")
    return _guard(
        lambda: (
            jsonify(workflow_service.review_member(_user_id(), semillero.id, user_id, status)),
            200,
        )
    )


@jwt_required()
def semillero_pending(identifier: str):
    from app.services import semillero_service

    semillero = semillero_service.get_semillero(identifier)
    if semillero is None:
        return json_error("Semillero no encontrado.", 404)
    return jsonify(items=workflow_service.pending_members(semillero.id)), 200


def list_projects():
    return jsonify(items=workflow_service.list_projects()), 200


@jwt_required()
def get_project(slug: str):
    return _guard(lambda: (jsonify(project=workflow_service.get_project(slug)), 200))


@jwt_required()
def create_project():
    data = request.get_json(silent=True) or {}
    return _guard(lambda: (jsonify(project=workflow_service.create_project(_user_id(), data)), 201))


def list_activities():
    from flask_jwt_extended import verify_jwt_in_request

    verify_jwt_in_request(optional=True)
    raw = get_jwt_identity()
    user_id = int(raw) if raw else None
    return jsonify(items=workflow_service.list_activities(user_id)), 200


@jwt_required()
def get_activity(slug: str):
    return _guard(lambda: (jsonify(item=workflow_service.get_activity(slug, _user_id())), 200))


@jwt_required()
def join_activity(slug: str):
    return _guard(lambda: (jsonify(item=workflow_service.join_activity(_user_id(), slug)), 200))


@jwt_required()
def get_profile():
    user = db.session.get(User, _user_id())
    return jsonify(workflow_service.profile_payload(user)), 200


@jwt_required()
def patch_profile():
    bio = (request.get_json(silent=True) or {}).get("bio")
    return jsonify(workflow_service.update_profile(_user_id(), bio)), 200


@jwt_required()
def gamification():
    return jsonify(workflow_service.gamification_payload(_user_id())), 200


@jwt_required()
def create_achievement():
    data = request.get_json(silent=True) or {}
    kind = data.get("kind") or "article"

    def run():
        row = workflow_service.record_pending(
            _user_id(),
            kind,
            data.get("title") or "Logro de investigación",
            data.get("description"),
            evidence=data.get("evidence"),
        )
        return jsonify(id=row.id, status=row.status), 201

    return _guard(run)


@jwt_required()
def home():
    user = db.session.get(User, _user_id())
    return jsonify(workflow_service.home_payload(user)), 200


@jwt_required()
def list_notifications():
    return jsonify(items=workflow_service.list_notifications(_user_id())), 200


@jwt_required()
def read_notification(notification_id: int):
    def run():
        workflow_service.mark_notification(_user_id(), notification_id)
        return "", 204

    return _guard(run)
