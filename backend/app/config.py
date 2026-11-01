import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


def _database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://riul:riul@localhost:3307/riul",
    )


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "dev-only-secret-key-not-for-production-use"
    )
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        "dev-only-jwt-secret-key-not-for-production-32b",
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    INSTITUTIONAL_EMAIL_DOMAIN = os.environ.get(
        "INSTITUTIONAL_EMAIL_DOMAIN", "unilibre.edu.co"
    )
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(_BACKEND_ROOT / "uploads"))
    JWT_TOKEN_LOCATION = ["headers", "query_string"]
    JWT_QUERY_STRING_NAME = "token"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    RATELIMIT_ENABLED = True
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    """Producción: exige secretos reales y orígenes CORS explícitos."""

    DEBUG = False

    @classmethod
    def validate(cls) -> None:
        if cls.SECRET_KEY.startswith("dev-only") or cls.JWT_SECRET_KEY.startswith("dev-only"):
            raise RuntimeError("SECRET_KEY y JWT_SECRET_KEY deben definirse en producción.")
        if cls.CORS_ORIGINS == "*":
            raise RuntimeError("CORS_ORIGINS debe listar orígenes explícitos en producción.")


class TestConfig(Config):
    TESTING = True
    RATELIMIT_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "mysql+pymysql://riul:riul@localhost:3307/riul_test",
    )


config_by_name = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig,
}

