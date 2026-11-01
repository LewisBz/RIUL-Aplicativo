from flask import Blueprint

from app.controllers import profile_controller as c
from app.utils.errors import ServiceError

profile_bp = Blueprint("profile", __name__, url_prefix="/api")
profile_bp.errorhandler(ServiceError)(c.handle_service_error)

profile_bp.get("/dashboard")(c.get_dashboard)
profile_bp.get("/profile")(c.get_profile)
profile_bp.patch("/profile")(c.update_profile)
profile_bp.post("/profile/password")(c.change_password)
profile_bp.post("/publications")(c.create_publication)
