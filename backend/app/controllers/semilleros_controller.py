from flask import jsonify, request

from app.controllers.guards import active_user_required, items_response
from app.controllers.http import json_error, load_schema, query_args
from app.schemas import (
    MemberReviewSchema,
    SemilleroActivitySchema,
    SemilleroCreateSchema,
    SemilleroListQuerySchema,
    serialize_semillero_detail,
    serialize_semillero_summary,
)
from app.services import project_service, semillero_service
from app.repositories import project_repository
from app.utils.errors import ServiceError


def _detail(user, semillero) -> dict:
    return serialize_semillero_detail(
        semillero,
        semillero_service.viewer_membership(semillero, user.id),
        project_service.list_projects(semillero_slug=semillero.slug),
        project_repository.list_semillero_products(semillero.id),
        can_manage=semillero_service.can_manage(user, semillero),
        following=semillero.id in semillero_service.followed_ids(user.id),
        follower_count=semillero_service.follower_count(semillero),
    )


@active_user_required
def list_semilleros(user):
    query = load_schema(
        SemilleroListQuerySchema(),
        query_args(request, "q", "faculty_id", "area"),
    )
    roles = semillero_service.viewer_roles(user.id)
    semilleros = semillero_service.list_semilleros(**query)
    return items_response(
        [serialize_semillero_summary(s, roles.get(s.id)) for s in semilleros],
        areas=semillero_service.list_areas(),
    )


@active_user_required
def get_semillero(user, slug: str):
    semillero = semillero_service.get_or_404(slug)
    return jsonify(semillero=_detail(user, semillero)), 200


@active_user_required
def create_semillero(user):
    data = load_schema(SemilleroCreateSchema(), request.get_json(silent=True) or {})
    semillero = semillero_service.create(user, data)
    return jsonify(semillero=_detail(user, semillero)), 201


@active_user_required
def join_semillero(user, slug: str):
    semillero = semillero_service.join(user, slug)
    return jsonify(semillero=_detail(user, semillero)), 201


@active_user_required
def leave_semillero(user, slug: str):
    semillero_service.leave(user, slug)
    return jsonify(semillero=_detail(user, semillero_service.get_or_404(slug))), 200


@active_user_required
def add_activity(user, slug: str):
    data = load_schema(SemilleroActivitySchema(), request.get_json(silent=True) or {})
    semillero_service.add_activity(user, slug, data)
    return jsonify(semillero=_detail(user, semillero_service.get_or_404(slug))), 201


@active_user_required
def review_member(user, slug: str, user_id: int):
    data = load_schema(MemberReviewSchema(), request.get_json(silent=True) or {})
    semillero_service.review_member(user, slug, user_id, data['status'], data['role'])
    return jsonify(semillero=_detail(user, semillero_service.get_or_404(slug))), 200


@active_user_required
def follow_semillero(user, slug: str):
    semillero = semillero_service.follow(user, slug)
    return jsonify(semillero=_detail(user, semillero)), 201


@active_user_required
def unfollow_semillero(user, slug: str):
    semillero = semillero_service.unfollow(user, slug)
    return jsonify(semillero=_detail(user, semillero)), 200


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)

