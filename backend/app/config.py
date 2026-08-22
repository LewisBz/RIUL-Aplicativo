import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://riul:riul@localhost:5433/riul",
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


class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://riul:riul@localhost:5433/riul_test",
    )


config_by_name = {
    "dev": DevConfig,
    "test": TestConfig,
}
