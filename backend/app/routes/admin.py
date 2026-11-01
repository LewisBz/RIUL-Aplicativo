from flask import Blueprint

from app.controllers import admin_controller, support_controller
from app.utils.errors import ServiceError

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
admin_bp.errorhandler(ServiceError)(admin_controller.handle_service_error)


admin_bp.get("/overview")(admin_controller.get_overview)
admin_bp.get("/analytics")(admin_controller.get_analytics)
admin_bp.get("/users")(admin_controller.get_users)
admin_bp.patch("/users/<int:user_id>")(admin_controller.patch_user)
admin_bp.get("/achievements")(admin_controller.get_achievements)
admin_bp.patch("/achievements/<int:achievement_id>")(admin_controller.patch_achievement)
admin_bp.get("/support/tickets")(support_controller.admin_list_tickets)
admin_bp.patch("/support/tickets/<int:ticket_id>")(support_controller.admin_reply_ticket)
