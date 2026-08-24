import os
import shutil
import tempfile
import uuid

import pytest
from sqlalchemy import create_engine, text

_UPLOAD_ROOT = os.path.join(tempfile.gettempdir(), f"riul_test_uploads_{uuid.uuid4().hex[:8]}")
os.environ["UPLOAD_FOLDER"] = _UPLOAD_ROOT

from app import create_app  # noqa: E402  (after UPLOAD_FOLDER override)
from app.extensions import db as _db  # noqa: E402

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
def clean_posts_data(schema):
    yield
    _db.session.execute(text("TRUNCATE users RESTART IDENTITY CASCADE"))
    _db.session.commit()
    posts_dir = os.path.join(_UPLOAD_ROOT, "posts")
    if os.path.isdir(posts_dir):
        for name in os.listdir(posts_dir):
            os.unlink(os.path.join(posts_dir, name))


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_user(client):
    def _make(email=None, password="secreto123", **overrides):
        payload = {
            "email": email or f"post-{uuid.uuid4().hex[:10]}@unilibre.edu.co",
            "password": password,
            "full_name": "Investigador de Prueba",
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
