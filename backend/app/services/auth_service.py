import re
import uuid

from flask import current_app
from flask_jwt_extended import create_access_token

from app.models import STATUS_ACTIVE, STATUS_PENDING, User
from app.repositories import catalog_repository, user_repository
from app.utils.errors import ServiceError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def _clean(value) -> str:
    return (value or "").strip()


def _validate_email(email: str) -> str:
    if not email or not EMAIL_RE.match(email):
        raise ServiceError("Correo electrónico inválido.", 400)
    return email.lower()


def _validate_password(password) -> None:
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise ServiceError(
            f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.",
            400,
        )


def _institutional_domain() -> str:
    return current_app.config["INSTITUTIONAL_EMAIL_DOMAIN"].lower()


def _ensure_unique_email(email: str) -> None:
    if user_repository.get_user_by_email(email) is not None:
        raise ServiceError("Este correo ya está registrado.", 409)


def _resolve_faculty_program(data: dict) -> tuple[int | None, int | None]:
    faculty_id = data.get("faculty_id")
    program_id = data.get("program_id")
    if not faculty_id and not program_id:
        return None, None
    try:
        faculty_id = int(faculty_id) if faculty_id else None
        program_id = int(program_id) if program_id else None
    except (TypeError, ValueError):
        raise ServiceError("Facultad o programa inválido.", 400)

    if faculty_id is not None and user_repository.get_faculty(faculty_id) is None:
        raise ServiceError("La facultad indicada no existe.", 400)
    if program_id is not None:
        program = user_repository.get_program(program_id)
        if program is None:
            raise ServiceError("El programa indicado no existe.", 400)
        if faculty_id is None:
            faculty_id = program.faculty_id
        elif program.faculty_id != faculty_id:
            raise ServiceError(
                "El programa no pertenece a la facultad seleccionada.", 400
            )
    return faculty_id, program_id


def create_access_token_for(user: User) -> str:
    return create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "status": user.status},
    )


def register_institutional(data: dict) -> User:
    domain = _institutional_domain()
    email = _validate_email(_clean(data.get("email")))
    if not email.endswith(f"@{domain}"):
        raise ServiceError(
            f"El registro institucional requiere un correo @{domain}.", 400
        )
    _validate_password(data.get("password"))
    _ensure_unique_email(email)

    full_name = _clean(data.get("full_name")) or None
    faculty_id, program_id = _resolve_faculty_program(data)

    user = User(
        full_name=full_name,
        email=email,
        role="researcher",
        status=STATUS_ACTIVE,
        faculty_id=faculty_id,
        program_id=program_id,
    )
    user.set_password(data["password"])
    user_repository.add_user(user)
    user_repository.commit()
    return user


def request_account(data: dict) -> User:
    domain = _institutional_domain()
    email = _validate_email(_clean(data.get("email")))
    if email.endswith(f"@{domain}"):
        raise ServiceError(
            f"Ese correo es institucional (@{domain}); usa el registro institucional.",
            400,
        )
    full_name = _clean(data.get("full_name"))
    motivation = _clean(data.get("motivation"))
    if not full_name or not motivation:
        raise ServiceError(
            "Nombre completo y motivo de solicitud son obligatorios.", 400
        )
    _ensure_unique_email(email)

    faculty_id, program_id = _resolve_faculty_program(data)
    if faculty_id is None or program_id is None:
        raise ServiceError("Debe seleccionar facultad y programa.", 400)

    user = User(
        full_name=full_name,
        email=email,
        status=STATUS_PENDING,
        motivation=motivation,
        faculty_id=faculty_id,
        program_id=program_id,
    )
    user.set_password(uuid.uuid4().hex)
    user_repository.add_user(user)
    user_repository.commit()
    return user


def authenticate(email, password) -> User:
    normalized = _validate_email(_clean(email)).lower()
    user = user_repository.get_user_by_email(normalized)
    if user is None:
        raise ServiceError("Credenciales incorrectas.", 401)
    if user.status == STATUS_PENDING:
        raise ServiceError(
            "Estado de validación: Solicitud pendiente de aprobación.", 403
        )
    if user.status != STATUS_ACTIVE:
        raise ServiceError("Su cuenta no está autorizada para acceder.", 403)
    if not user.check_password(password or ""):
        raise ServiceError("Credenciales incorrectas.", 401)
    return user


def get_identity(user_id: int) -> User:
    user = user_repository.get_user_by_id(user_id)
    if user is None or user.status != STATUS_ACTIVE:
        raise ServiceError("Cuenta no disponible.", 401)
    return user


def catalog() -> dict:
    faculties = catalog_repository.list_faculties()
    programs = catalog_repository.list_programs()
    return {
        "faculties": faculties,
        "programs": programs,
    }
