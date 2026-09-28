from flask import Blueprint

from app.controllers import auth_controller
from app.utils.errors import ServiceError

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
auth_bp.errorhandler(ServiceError)(auth_controller.handle_service_error)

auth_bp.post("/register")(auth_controller.register)
auth_bp.post("/request-account")(auth_controller.request_account)
auth_bp.post("/login")(auth_controller.login)
auth_bp.get("/me")(auth_controller.me)
auth_bp.get("/catalog")(auth_controller.catalog)
