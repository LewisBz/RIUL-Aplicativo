from flask import Blueprint

from app.controllers import projects_controller as c
from app.utils.errors import ServiceError

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")
projects_bp.errorhandler(ServiceError)(c.handle_service_error)

projects_bp.get("")(c.list_projects)
projects_bp.post("")(c.create_project)
projects_bp.get("/<slug>")(c.get_project)
projects_bp.patch("/<slug>")(c.update_project)
projects_bp.post("/<slug>/products")(c.add_product)
projects_bp.patch("/<slug>/milestones/<int:milestone_id>")(c.update_milestone)
