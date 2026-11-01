from flask import jsonify, request

from app.controllers.admin_controller import require_administrator
from app.controllers.guards import active_user_required, items_response
from app.controllers.http import load_schema, query_args
from app.schemas.support import (
    TicketCreateSchema,
    TicketListQuerySchema,
    TicketReplySchema,
    serialize_ticket,
)
from app.services import support_service


@active_user_required
def create_ticket(user):
    data = load_schema(TicketCreateSchema(), request.get_json(silent=True) or {})
    ticket = support_service.create_ticket(user, data)
    return jsonify(ticket=serialize_ticket(ticket)), 201


@active_user_required
def list_my_tickets(user):
    tickets = support_service.list_my_tickets(user)
    return items_response([serialize_ticket(t) for t in tickets])


@require_administrator
def admin_list_tickets():
    query = load_schema(TicketListQuerySchema(), query_args(request, "status"))
    tickets = support_service.list_all_tickets(query.get("status"))
    return items_response([serialize_ticket(t, with_user=True) for t in tickets])


@require_administrator
def admin_reply_ticket(ticket_id: int):
    data = load_schema(TicketReplySchema(), request.get_json(silent=True) or {})
    ticket = support_service.reply_ticket(ticket_id, data)
    return jsonify(ticket=serialize_ticket(ticket, with_user=True)), 200
