import os
import shutil
import tempfile
import uuid

import pytest
from sqlalchemy import create_engine, text

_UPLOAD_ROOT = os.path.join(
    tempfile.gettempdir(), f"riul_test_uploads_{uuid.uuid4().hex[:8]}"
)
os.environ.setdefault("UPLOAD_FOLDER", _UPLOAD_ROOT)
os.environ.setdefault(
    "TEST_DATABASE_URL",
    "mysql+pymysql://riul:riul@localhost:3307/riul_test",
)
os.environ.setdefault(
    "MYSQL_ADMIN_URL",
    "mysql+pymysql://root:riulroot@localhost:3307/mysql",
)

from app import create_app  # noqa: E402
from app.extensions import db as _db  # noqa: E402
from app.models import Faculty, Program  # noqa: E402

TEST_DB_URL = os.environ["TEST_DATABASE_URL"]
MYSQL_ADMIN_URL = os.environ["MYSQL_ADMIN_URL"]


def _ensure_test_database() -> None:
    engine = create_engine(MYSQL_ADMIN_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS riul_test CHARACTER SET utf8mb4"))
        conn.execute(text("GRANT ALL PRIVILEGES ON riul_test.* TO 'riul'@'%'"))
        conn.execute(text("FLUSH PRIVILEGES"))
    engine.dispose()


def _truncate_all() -> None:
    _db.session.expunge_all()
    _db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(text(f"TRUNCATE TABLE `{table.name}`"))
    _db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    _db.session.commit()
    _db.session.expunge_all()


@pytest.fixture(scope="session")
def app():
    _ensure_test_database()
    application = create_app("test")
    application.config["UPLOAD_FOLDER"] = _UPLOAD_ROOT
    with application.app_context():
        yield application


@pytest.fixture(scope="session", autouse=True)
def uploads_root(app):
    yield _UPLOAD_ROOT
    shutil.rmtree(_UPLOAD_ROOT, ignore_errors=True)


@pytest.fixture(scope="session", autouse=True)
def schema(app):
    _db.drop_all()
    _db.create_all()
    yield


@pytest.fixture(autouse=True)
def clean_data(schema):
    _truncate_all()
    ing = Faculty(name="Ingeniería")
    _db.session.add(ing)
    _db.session.flush()
    _db.session.add(Program(name="Ingeniería de Sistemas", faculty_id=ing.id))
    _db.session.add(Program(name="Ingeniería Industrial", faculty_id=ing.id))
    _db.session.add(Faculty(name="Ciencias Básicas"))
    _db.session.commit()
    yield
    posts_dir = os.path.join(_UPLOAD_ROOT, "posts")
    if os.path.isdir(posts_dir):
        for name in os.listdir(posts_dir):
            os.unlink(os.path.join(posts_dir, name))


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
            "full_name": overrides.pop("full_name", "Estudiante de Prueba"),
            "faculty_id": None,
            "program_id": None,
        }
        payload.update(overrides)
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201, response.get_json()
        return payload, response.get_json()

    return _make


@pytest.fixture()
def make_headers():
    def _headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    return _headers
