from flask import jsonify, request

from app.controllers.guards import active_user_required
from app.controllers.http import json_error, load_schema
from app.schemas import ReportListQuerySchema, serialize_report
from app.services import report_service
from app.utils.errors import ServiceError


@active_user_required
def list_published(user):
    query = load_schema(
        ReportListQuerySchema(),
        {"kind": request.args["kind"]} if request.args.get("kind") else {},
    )
    reports = report_service.list_published(query.get("kind"))
    return jsonify(
        items=[serialize_report(r, with_metrics=False) for r in reports], total=len(reports)
    ), 200


@active_user_required
def get_published(user, report_id: int):
    return jsonify(report=serialize_report(report_service.get_published_or_404(report_id))), 200


def handle_service_error(error: ServiceError):
    return json_error(error.message, error.status)
