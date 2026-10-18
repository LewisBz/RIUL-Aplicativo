from flask import Blueprint

from app.controllers import semillero_controller

semilleros_bp = Blueprint("semilleros", __name__, url_prefix="/api/semilleros")

semilleros_bp.get("")(semillero_controller.list_semilleros)
semilleros_bp.get("/<string:identifier>")(semillero_controller.get_semillero)
