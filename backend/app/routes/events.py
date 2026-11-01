from flask import Blueprint

from app.controllers import events_controller as c
from app.utils.errors import ServiceError

events_bp = Blueprint("events", __name__, url_prefix="/api/events")
events_bp.errorhandler(ServiceError)(c.handle_service_error)

events_bp.get("")(c.list_events)
events_bp.post("")(c.create_event)
events_bp.get("/<slug>")(c.get_event)
events_bp.post("/<slug>/registrations")(c.register)
events_bp.delete("/<slug>/registrations/me")(c.unregister)
