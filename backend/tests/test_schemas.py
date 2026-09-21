from marshmallow import ValidationError

from app.schemas import LoginSchema, PostCreateSchema, RegisterSchema


def test_register_schema_rejects_short_password():
    try:
        RegisterSchema().load(
            {"email": "ana@unilibre.edu.co", "password": "corta"}
        )
        assert False, "expected ValidationError"
    except ValidationError as error:
        assert "8" in str(error.messages)


def test_login_schema_rejects_invalid_email():
    try:
        LoginSchema().load({"email": "no-es-correo", "password": "secreto123"})
        assert False, "expected ValidationError"
    except ValidationError as error:
        assert error.messages


def test_post_create_schema_rejects_unknown_category():
    try:
        PostCreateSchema().load({"category": "chisme", "content": "hola"})
        assert False, "expected ValidationError"
    except ValidationError as error:
        assert "Categoría inválida" in str(error.messages)
