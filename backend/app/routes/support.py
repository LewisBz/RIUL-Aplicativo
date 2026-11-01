from flask import Blueprint

from app.controllers import support_controller as c
from app.utils.errors import ServiceError
from app.controllers.admin_controller import handle_service_error

support_bp = Blueprint("support", __name__, url_prefix="/api/support")
support_bp.errorhandler(ServiceError)(handle_service_error)

support_bp.get("/tickets")(c.list_my_tickets)
support_bp.post("/tickets")(c.create_ticket)
