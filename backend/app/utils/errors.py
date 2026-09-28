from marshmallow import ValidationError


class ServiceError(Exception):
    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.message = message
        self.status = status


def first_marshmallow_message(exc: ValidationError) -> str:
    def walk(node):
        if isinstance(node, list):
            return str(node[0]) if node else "Datos inválidos."
        if isinstance(node, dict):
            for value in node.values():
                return walk(value)
        return str(node)

    return walk(exc.messages)
