from flask import Blueprint

from app.controllers import semilleros_controller as c
from app.utils.errors import ServiceError

semilleros_bp = Blueprint("semilleros", __name__, url_prefix="/api/semilleros")
semilleros_bp.errorhandler(ServiceError)(c.handle_service_error)

semilleros_bp.get("")(c.list_semilleros)
semilleros_bp.post("")(c.create_semillero)
semilleros_bp.get("/<slug>")(c.get_semillero)
semilleros_bp.post("/<slug>/members")(c.join_semillero)
semilleros_bp.delete("/<slug>/members/me")(c.leave_semillero)
semilleros_bp.post("/<slug>/activities")(c.add_activity)
