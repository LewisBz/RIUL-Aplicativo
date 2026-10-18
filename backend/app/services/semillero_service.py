from app.models.semillero import Semillero
from app.repositories import semillero_repository


def list_semilleros(
    faculty_id: int | None = None,
    program_id: int | None = None,
    area: str | None = None,
    query: str | None = None,
) -> list[Semillero]:
    return semillero_repository.list_semilleros(
        faculty_id=faculty_id,
        program_id=program_id,
        area=area,
        query=query,
    )


def get_semillero(identifier: str | int) -> Semillero | None:
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        found = semillero_repository.get_by_id(int(identifier))
        if found:
            return found
    return semillero_repository.get_by_slug(str(identifier))


def count_semilleros() -> int:
    return semillero_repository.count_semilleros()
