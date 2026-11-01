"""Las migraciones de Alembic deben producir exactamente el esquema de los modelos."""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parent.parent
SCRATCH_DB = "riul_migrations_test"

COMPARE_SCRIPT = """
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from app import create_app
from app.extensions import db

app = create_app("dev")
with app.app_context(), db.engine.connect() as conn:
    ctx = MigrationContext.configure(conn, opts={"compare_type": True})
    diffs = compare_metadata(ctx, db.metadata)
print("DIFFS=%d" % len(diffs))
for diff in diffs:
    print(diff)
"""


@pytest.fixture(scope="module")
def scratch_url():
    admin = create_engine(os.environ["MYSQL_ADMIN_URL"], isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {SCRATCH_DB}"))
        conn.execute(text(f"CREATE DATABASE {SCRATCH_DB} CHARACTER SET utf8mb4"))
        conn.execute(text(f"GRANT ALL PRIVILEGES ON {SCRATCH_DB}.* TO 'riul'@'%'"))
        conn.execute(text("FLUSH PRIVILEGES"))
    base = os.environ["TEST_DATABASE_URL"].rsplit("/", 1)[0]
    yield f"{base}/{SCRATCH_DB}"
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {SCRATCH_DB}"))
    admin.dispose()


def _run(url: str, *args: str) -> str:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=BACKEND_DIR,
        env={**os.environ, "DATABASE_URL": url, "FLASK_APP": "run.py"},
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def _flask(url: str, *args: str) -> str:
    return _run(url, "-m", "flask", *args)


def test_upgrade_matches_models_and_is_reversible(scratch_url):
    _flask(scratch_url, "db", "upgrade")
    report = _run(scratch_url, "-c", COMPARE_SCRIPT)
    assert "DIFFS=0" in report, report

    # Los catálogos de gamificación los siembra la propia migración.
    engine = create_engine(scratch_url)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM levels")).scalar() == 20
        assert conn.execute(text("SELECT COUNT(*) FROM achievement_types")).scalar() == 7
    engine.dispose()

    _flask(scratch_url, "db", "downgrade", "0003")
    engine = create_engine(scratch_url)
    with engine.connect() as conn:
        tables = {row[0] for row in conn.execute(text("SHOW TABLES"))}
    engine.dispose()
    assert {"publications", "project_products", "event_registrations"} <= tables
    assert not ({"products", "calls", "xp_ledger", "comments"} & tables)

    _flask(scratch_url, "db", "upgrade")
    assert "DIFFS=0" in _run(scratch_url, "-c", COMPARE_SCRIPT)
