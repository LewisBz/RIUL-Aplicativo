from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.modules.auth.models import ROLE_ADMINISTRATOR, User

from . import services

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def require_administrator(view):
    @wraps(view)
    @jwt_required()
    def wrapped(*args, **kwargs):
        try:
            user_id = int(get_jwt_identity())
        except (TypeError, ValueError):
            return jsonify(message="Token inválido."), 401
        user = db.session.get(User, user_id)
        if user is None or user.status != "active":
            return jsonify(message="Cuenta no disponible."), 401
        if user.role != ROLE_ADMINISTRATOR:
            return jsonify(message="Se requieren permisos de administrador."), 403
        return view(*args, **kwargs)

    return wrapped


@admin_bp.get("/overview")
@require_administrator
def get_overview():
    return jsonify(services.overview()), 200


@admin_bp.get("/users")
@require_administrator
def get_users():
    try:
        users = services.list_users(
            status=request.args.get("status"), role=request.args.get("role")
        )
    except ValueError as error:
        return jsonify(message=str(error)), 400
    return jsonify(items=users, total=len(users)), 200


@admin_bp.patch("/users/<int:user_id>")
@require_administrator
def patch_user(user_id: int):
    data = request.get_json(silent=True) or {}
    try:
        actor_id = int(get_jwt_identity())
        user = services.update_user_status(actor_id, user_id, data.get("status"))
    except ValueError as error:
        return jsonify(message=str(error)), 400
    except LookupError as error:
        return jsonify(message=str(error)), 404
    except PermissionError as error:
        return jsonify(message=str(error)), 403
    return jsonify(user=user), 200