from flask import jsonify, request

from app.controllers.guards import active_user_required
from app.controllers.http import json_error, load_schema
from app.schemas import (
    ChangePasswordSchema,
    ProfileUpdateSchema,
    PublicationCreateSchema,
    UserSchema,
    serialize_dashboard,
    serialize_profile,
    serialize_publication,
)
from app.services import profile_service
from app.utils.errors import ServiceError
from app.utils.rate_limit import rate_limit


def _profile(user) -> dict:
    return serialize_profile(
        profile_service.get_profile(user), UserSchema().dump(user)
    )


@active_user_required
def get_profile(user):
    return jsonify(profile=_profile(user)), 200


@active_user_required
def update_profile(user):
    data = load_schema(ProfileUpdateSchema(), request.get_json(silent=True) or {})
    profile_service.update_profile(user, data)
    return jsonify(profile=_profile(user)), 200


@active_user_required
@rate_limit(5, 600)
def change_password(user):
    data = load_schema(ChangePasswordSchema(), request.get_json(silent=True) or {})
    profile_service.change_password(user, data["current_password"], data["new_password"])
    return "", 204


@active_user_required
def create_publication(user):
    data = load_schema(PublicationCreateSchema(), request.get_json(silent=True) or {})
    publication = profile_service.add_publication(user, data)
    return jsonify(publication=serialize_publication(publication)), 201


@active_user_required
def get_dashboard(user):
    return jsonify(dashboard=serialize_dashboard(profile_service.get_dashboard(user))), 200


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)
