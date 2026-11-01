from flask import Blueprint

from app.controllers import engagement_controller as c
from app.utils.errors import ServiceError

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")
notifications_bp.errorhandler(ServiceError)(c.handle_service_error)

notifications_bp.get("")(c.list_notifications)
notifications_bp.post("/read-all")(c.read_all_notifications)
notifications_bp.patch("/<int:notification_id>")(c.update_notification)

gamification_bp = Blueprint("gamification", __name__, url_prefix="/api/gamification")
gamification_bp.errorhandler(ServiceError)(c.handle_service_error)

gamification_bp.get("/me")(c.get_my_gamification)
gamification_bp.get("/ranking")(c.get_ranking)
gamification_bp.post("/achievements")(c.create_achievement)
