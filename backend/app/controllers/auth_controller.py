from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.controllers.http import json_error, load_schema
from app.schemas import (
    FacultyCatalogSchema,
    LoginSchema,
    RegisterSchema,
    RequestAccountSchema,
    UserSchema,
)
from app.services import auth_service
from app.utils.errors import ServiceError


def register():
    data = load_schema(RegisterSchema(), request.get_json(silent=True) or {})
    user = auth_service.register_institutional(data)
    token = auth_service.create_access_token_for(user)
    return (
        jsonify(access_token=token, user=UserSchema().dump(user)),
        201,
    )


def request_account():
    data = load_schema(RequestAccountSchema(), request.get_json(silent=True) or {})
    auth_service.request_account(data)
    return (
        jsonify(
            message="Solicitud enviada. Estado de validación: Solicitud pendiente de aprobación."
        ),
        202,
    )


def login():
    data = load_schema(LoginSchema(), request.get_json(silent=True) or {})
    user = auth_service.authenticate(data.get("email"), data.get("password"))
    token = auth_service.create_access_token_for(user)
    return jsonify(access_token=token, user=UserSchema().dump(user)), 200


@jwt_required()
def me():
    try:
        user = auth_service.get_identity(int(get_jwt_identity()))
    except ValueError:
        return json_error("Token inválido.", 401)
    return jsonify(user=UserSchema().dump(user)), 200


def catalog():
    payload = auth_service.catalog()
    faculties = []
    for faculty in payload["faculties"]:
        faculties.append(
            FacultyCatalogSchema().dump(
                {
                    "id": faculty.id,
                    "name": faculty.name,
                    "programs": [
                        p
                        for p in payload["programs"]
                        if p.faculty_id == faculty.id
                    ],
                }
            )
        )
    return jsonify(faculties=faculties), 200


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)
