from flask import jsonify, request

from app.controllers.guards import active_user_required, items_response
from app.controllers.http import json_error, load_schema, query_args
from app.schemas import (
    MilestoneUpdateSchema,
    ProjectCreateSchema,
    ProjectListQuerySchema,
    ProjectProductSchema,
    ProjectUpdateSchema,
    serialize_product,
    serialize_project_detail,
    serialize_project_summary,
)
from app.services import project_service
from app.utils.errors import ServiceError


def _detail(user, project) -> dict:
    return serialize_project_detail(project, project_service.viewer_role(project, user))


@active_user_required
def list_projects(user):
    query = load_schema(
        ProjectListQuerySchema(),
        query_args(request, "q", "status", "semillero", "mine"),
    )
    projects = project_service.list_projects(
        q=query["q"],
        status=query["status"],
        semillero_slug=query["semillero"],
        member_id=user.id if query["mine"] else None,
    )
    return items_response(
        [
            serialize_project_summary(p, project_service.viewer_role(p, user))
            for p in projects
        ]
    )


@active_user_required
def get_project(user, slug: str):
    return jsonify(project=_detail(user, project_service.get_or_404(slug))), 200


@active_user_required
def create_project(user):
    data = load_schema(ProjectCreateSchema(), request.get_json(silent=True) or {})
    return jsonify(project=_detail(user, project_service.create(user, data))), 201


@active_user_required
def update_project(user, slug: str):
    data = load_schema(ProjectUpdateSchema(), request.get_json(silent=True) or {})
    return jsonify(project=_detail(user, project_service.update(user, slug, data))), 200


@active_user_required
def add_product(user, slug: str):
    data = load_schema(ProjectProductSchema(), request.get_json(silent=True) or {})
    product = project_service.add_product(user, slug, data)
    return jsonify(product=serialize_product(product)), 201


@active_user_required
def update_milestone(user, slug: str, milestone_id: int):
    data = load_schema(MilestoneUpdateSchema(), request.get_json(silent=True) or {})
    project_service.set_milestone(user, slug, milestone_id, data["done"])
    return jsonify(project=_detail(user, project_service.get_or_404(slug))), 200


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)

