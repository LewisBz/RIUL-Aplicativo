from flask import Blueprint

from app.controllers import reports_controller as c
from app.utils.errors import ServiceError

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")
reports_bp.errorhandler(ServiceError)(c.handle_service_error)

reports_bp.get("")(c.list_published)
reports_bp.get("/<int:report_id>")(c.get_published)
