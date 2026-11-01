from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import STATUS_ACTIVE, User
from app.repositories import user_repository
from app.utils.errors import ServiceError


def current_user() -> User:
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        raise ServiceError("Token inválido.", 401)
    user = user_repository.get_user_by_id(user_id)
    if user is None or user.status != STATUS_ACTIVE:
        raise ServiceError("Cuenta no disponible.", 401)
    return user


def active_user_required(view):
    """Exige JWT válido y cuenta activa; inyecta `user` como primer argumento."""

    @wraps(view)
    @jwt_required()
    def wrapped(*args, **kwargs):
        return view(current_user(), *args, **kwargs)

    return wrapped


def items_response(items: list, **extra):
    return jsonify(items=items, total=len(items), **extra), 200
