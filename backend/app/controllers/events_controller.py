from flask import jsonify, request

from app.controllers.guards import active_user_required, items_response
from app.controllers.http import json_error, load_schema, query_args
from app.schemas import (
    ApplicationReviewSchema,
    EventCreateSchema,
    EventListQuerySchema,
    RegistrationSchema,
    serialize_application,
    serialize_event,
)
from app.services import event_service
from app.utils.errors import ServiceError


def _event(user, activity) -> dict:
    keys = event_service.registered_keys(user.id)
    return serialize_event(activity, event_service.is_registered(activity, keys))


@active_user_required
def list_events(user):
    query = load_schema(
        EventListQuerySchema(),
        query_args(request, "kind", "status", "q"),
    )
    keys = event_service.registered_keys(user.id)
    activities = event_service.list_events(**query)
    return items_response(
        [serialize_event(a, event_service.is_registered(a, keys)) for a in activities]
    )


@active_user_required
def get_event(user, slug: str):
    return jsonify(event=_event(user, event_service.get_or_404(slug))), 200


@active_user_required
def create_event(user):
    data = load_schema(EventCreateSchema(), request.get_json(silent=True) or {})
    return jsonify(event=_event(user, event_service.create(user, data))), 201


@active_user_required
def register(user, slug: str):
    data = load_schema(RegistrationSchema(), request.get_json(silent=True) or {})
    return jsonify(event=_event(user, event_service.register(user, slug, data))), 201


@active_user_required
def unregister(user, slug: str):
    return jsonify(event=_event(user, event_service.unregister(user, slug))), 200


@active_user_required
def list_applications(user, slug: str):
    applications = event_service.list_applications(user, slug)
    return items_response([serialize_application(a) for a in applications])


@active_user_required
def review_application(user, slug: str, application_id: int):
    data = load_schema(ApplicationReviewSchema(), request.get_json(silent=True) or {})
    application = event_service.review_application(user, slug, application_id, data["status"])
    return jsonify(application=serialize_application(application)), 200


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)
