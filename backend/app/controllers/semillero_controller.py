from flask import jsonify, request

from app.controllers.http import json_error
from app.schemas import SemilleroDetailSchema, SemilleroListSchema
from app.services import semillero_service


def list_semilleros():
    faculty_id = request.args.get("faculty_id", type=int)
    program_id = request.args.get("program_id", type=int)
    area = request.args.get("area")
    query = request.args.get("query") or request.args.get("q")

    semilleros = semillero_service.list_semilleros(
        faculty_id=faculty_id,
        program_id=program_id,
        area=area,
        query=query,
    )
    return (
        jsonify(
            items=SemilleroListSchema(many=True).dump(semilleros),
            total=len(semilleros),
        ),
        200,
    )


def get_semillero(identifier: str):
    semillero = semillero_service.get_semillero(identifier)
    if not semillero:
        return json_error("Semillero no encontrado.", 404)
    return jsonify(semillero=SemilleroDetailSchema().dump(semillero)), 200
