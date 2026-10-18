from app.extensions import db
from app.models import Faculty, Program, Semillero, SemilleroMember, User


def test_list_semilleros_empty(client):
    response = client.get("/api/semilleros")
    assert response.status_code == 200
    body = response.get_json()
    assert "items" in body
    assert "total" in body


def test_list_and_get_semillero(client, ids):
    faculty = db.session.get(Faculty, ids["facultad_ingenieria"])
    program = db.session.get(Program, ids["programa_sistemas"])

    user = User(
        full_name="Docente Investigador",
        email="docente.semillero@unilibre.edu.co",
        role="leader",
        status="active",
        faculty_id=faculty.id,
        program_id=program.id,
    )
    user.set_password("secreto123")
    db.session.add(user)
    db.session.flush()

    semillero = Semillero(
        slug="semillero-test",
        name="Semillero de Inteligencia Computacional",
        description="Semillero enfocado en investigación de algoritmos avanzados.",
        area="Inteligencia Artificial",
        mission="Fomentar el pensamiento científico.",
        vision="Liderar la innovación regional.",
        faculty_id=faculty.id,
        program_id=program.id,
        leader_id=user.id,
    )
    db.session.add(semillero)
    db.session.flush()

    member = SemilleroMember(
        semillero_id=semillero.id,
        user_id=user.id,
        role_in_semillero="Líder Principal",
    )
    db.session.add(member)
    db.session.commit()

    # List endpoint
    response = client.get("/api/semilleros")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] >= 1
    found = next((s for s in data["items"] if s["slug"] == "semillero-test"), None)
    assert found is not None
    assert found["name"] == "Semillero de Inteligencia Computacional"
    assert found["area"] == "Inteligencia Artificial"
    assert found["leader"] == "Docente Investigador"
    assert found["member_count"] == 1

    # Filter endpoint
    filter_resp = client.get(f"/api/semilleros?faculty_id={faculty.id}&area=Inteligencia%20Artificial")
    assert filter_resp.status_code == 200
    assert any(s["slug"] == "semillero-test" for s in filter_resp.get_json()["items"])

    # Detail endpoint by slug
    detail_resp = client.get("/api/semilleros/semillero-test")
    assert detail_resp.status_code == 200
    detail = detail_resp.get_json()["semillero"]
    assert detail["mission"] == "Fomentar el pensamiento científico."
    assert len(detail["members"]) == 1
    assert detail["members"][0]["full_name"] == "Docente Investigador"

    # Detail endpoint 404
    not_found = client.get("/api/semilleros/no-existe-slug")
    assert not_found.status_code == 404
