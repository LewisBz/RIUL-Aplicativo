import os

os.environ.setdefault(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://riul:riul@localhost:5433/riul_test",
)
