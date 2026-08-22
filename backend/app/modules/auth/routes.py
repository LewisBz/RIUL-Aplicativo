from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.modules.auth.models import Faculty, Program

from . import services
from .services import ServiceError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.errorhandler(ServiceError)
def handle_service_error(error):
    return jsonify(message=error.message), error.status


@auth_bp.post("/register")
def register():
    user = services.register_institutional(request.get_json(silent=True) or {})
    token = services.create_access_token_for(user)
    return jsonify(access_token=token, user=user.to_dict()), 201


@auth_bp.post("/request-account")
def request_account():
    user = services.request_account(request.get_json(silent=True) or {})
    return (
        jsonify(
            message="Solicitud enviada. Estado de validación: Solicitud pendiente de aprobación."
        ),
        202,
    )


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = services.authenticate(data.get("email"), data.get("password"))
    token = services.create_access_token_for(user)
    return jsonify(access_token=token, user=user.to_dict()), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    try:
        user = services.get_identity(int(get_jwt_identity()))
    except ValueError:
        return jsonify(message="Token inválido."), 401
    return jsonify(user=user.to_dict()), 200


@auth_bp.get("/catalog")
def catalog():
    faculties = db.session.scalars(db.select(Faculty).order_by(Faculty.name)).all()
    programs = db.session.scalars(db.select(Program).order_by(Program.name)).all()
    return (
        jsonify(
            faculties=[
                {
                    "id": f.id,
                    "name": f.name,
                    "programs": [p.to_dict() for p in programs if p.faculty_id == f.id],
                }
                for f in faculties
            ]
        ),
        200,
    )
