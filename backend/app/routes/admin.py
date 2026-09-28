from flask import Blueprint

from app.controllers import admin_controller
from app.utils.errors import ServiceError

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
admin_bp.errorhandler(ServiceError)(admin_controller.handle_service_error)


admin_bp.get("/overview")(admin_controller.get_overview)
admin_bp.get("/users")(admin_controller.get_users)
admin_bp.patch("/users/<int:user_id>")(admin_controller.patch_user)
