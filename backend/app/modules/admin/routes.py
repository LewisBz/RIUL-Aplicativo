from functools import wraps

from flask import Blueprint, jsonify
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