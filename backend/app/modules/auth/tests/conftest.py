import os
import uuid

import pytest
from sqlalchemy import create_engine, text

from app import create_app
from app.extensions import db as _db
from app.modules.auth.models import Faculty, Program

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://riul:riul@localhost:5433/riul_test",
)


def _ensure_test_database() -> None:
    admin_url = TEST_DB_URL.rsplit("/", 1)[0] + "/postgres"
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'riul_test'")
        ).scalar()
        if not exists:
            conn.execute(text("CREATE DATABASE riul_test"))
    engine.dispose()


@pytest.fixture(scope="session")
def app():
    _ensure_test_database()
    application = create_app("test")
    with application.app_context():
        yield application


@pytest.fixture(scope="session", autouse=True)
def schema(app):
    _db.drop_all()
    _db.create_all()
    ing = Faculty(name="Ingeniería")
    _db.session.add(ing)
    _db.session.flush()
    _db.session.add(Program(name="Ingeniería de Sistemas", faculty_id=ing.id))
    _db.session.add(Program(name="Ingeniería Industrial", faculty_id=ing.id))
    ciencias = Faculty(name="Ciencias Básicas")
    _db.session.add(ciencias)
    _db.session.commit()
    yield


@pytest.fixture(autouse=True)
def clean_users(schema):
    yield
    _db.session.execute(text("TRUNCATE users RESTART IDENTITY CASCADE"))
    _db.session.commit()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def ids(app):
    faculties = {f.name: f.id for f in Faculty.query.all()}
    programs = {p.name: p.id for p in Program.query.all()}
    return {
        "facultad_ingenieria": faculties["Ingeniería"],
        "programa_sistemas": programs["Ingeniería de Sistemas"],
        "programa_industrial": programs["Ingeniería Industrial"],
    }


def unique_email(domain: str = "unilibre.edu.co") -> str:
    return f"test-{uuid.uuid4().hex[:10]}@{domain}"


@pytest.fixture()
def make_user(client):
    def _make(email=None, password="secreto123", **overrides):
        payload = {
            "email": email or unique_email(),
            "password": password,
            "full_name": "Estudiante de Prueba",
            "faculty_id": None,
            "program_id": None,
        }
        payload.update(overrides)
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201, response.get_json()
        return payload, response.get_json()

    return _make
