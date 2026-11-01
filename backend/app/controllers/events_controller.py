from flask import jsonify, request

from app.controllers.guards import active_user_required, items_response
from app.controllers.http import json_error, load_schema, query_args
from app.schemas import EventCreateSchema, EventListQuerySchema, serialize_event
from app.services import event_service
from app.utils.errors import ServiceError


def _event(user, event) -> dict:
    return serialize_event(event, event.id in event_service.registered_ids(user.id))


@active_user_required
def list_events(user):
    query = load_schema(
        EventListQuerySchema(),
        query_args(request, "kind", "status", "q"),
    )
    registered = event_service.registered_ids(user.id)
    events = event_service.list_events(**query)
    return items_response([serialize_event(e, e.id in registered) for e in events])


@active_user_required
def get_event(user, slug: str):
    return jsonify(event=_event(user, event_service.get_or_404(slug))), 200


@active_user_required
def create_event(user):
    data = load_schema(EventCreateSchema(), request.get_json(silent=True) or {})
    return jsonify(event=_event(user, event_service.create(user, data))), 201


@active_user_required
def register(user, slug: str):
    return jsonify(event=_event(user, event_service.register(user, slug))), 201


@active_user_required
def unregister(user, slug: str):
    return jsonify(event=_event(user, event_service.unregister(user, slug))), 200


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)

