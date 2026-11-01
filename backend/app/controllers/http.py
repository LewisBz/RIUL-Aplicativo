from flask import jsonify
from marshmallow import ValidationError

from app.utils.errors import ServiceError, first_marshmallow_message


def json_error(message: str, status: int):
    return jsonify(message=message), status


def load_schema(schema, data: dict):
    try:
        return schema.load(data or {})
    except ValidationError as error:
        raise ServiceError(first_marshmallow_message(error), 400) from error


def query_args(request, *names: str) -> dict:
    """Devuelve solo los parámetros de consulta presentes y no vacíos."""
    return {name: request.args[name] for name in names if request.args.get(name)}
