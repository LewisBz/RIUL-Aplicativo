"""Add database-level CHECK constraints and ON DELETE rules.

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-18

Enforces the enum-like columns and the referential actions that were only
handled by the ORM cascade before, so integrity cannot be bypassed.
"""
from alembic import op
import sqlalchemy as sa


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


CHECKS = (
    ("users", "ck_users_role", "role IN ('researcher','leader','administrator')"),
    ("users", "ck_users_status", "status IN ('active','pending','rejected')"),
    (
        "posts",
        "ck_posts_category",
        "category IN ('article','project_advance','presentation','event','community')",
    ),
    (
        "post_attachments",
        "ck_post_attachments_kind",
        "kind IN ('image','file')",
    ),
)

FKS = (
    ("programs", "faculty_id", "faculties", "id", "CASCADE"),
    ("users", "faculty_id", "faculties", "id", "SET NULL"),
    ("users", "program_id", "programs", "id", "SET NULL"),
    ("posts", "author_id", "users", "id", "CASCADE"),
    ("post_attachments", "post_id", "posts", "id", "CASCADE"),
    ("post_reactions", "post_id", "posts", "id", "CASCADE"),
    ("post_reactions", "user_id", "users", "id", "CASCADE"),
    ("semilleros", "faculty_id", "faculties", "id", "SET NULL"),
    ("semilleros", "program_id", "programs", "id", "SET NULL"),
    ("semilleros", "leader_id", "users", "id", "SET NULL"),
    ("semillero_members", "semillero_id", "semilleros", "id", "CASCADE"),
    ("semillero_members", "user_id", "users", "id", "CASCADE"),
)


def _existing_fk_name(bind, table: str, column: str) -> str | None:
    return bind.execute(
        sa.text(
            "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table "
            "AND COLUMN_NAME = :column AND REFERENCED_TABLE_NAME IS NOT NULL "
            "LIMIT 1"
        ),
        {"table": table, "column": column},
    ).scalar()


def upgrade():
    bind = op.get_bind()

    for table, name, condition in CHECKS:
        op.create_check_constraint(name, table, condition)

    for table, column, ref_table, ref_column, ondelete in FKS:
        existing = _existing_fk_name(bind, table, column)
        if existing is None:
            continue
        op.drop_constraint(existing, table, type_="foreignkey")
        op.create_foreign_key(
            f"fk_{table}_{column}",
            table,
            ref_table,
            [column],
            [ref_column],
            ondelete=ondelete,
        )


def downgrade():
    bind = op.get_bind()

    for table, column, ref_table, ref_column, ondelete in FKS:
        existing = _existing_fk_name(bind, table, column)
        if existing is None:
            continue
        op.drop_constraint(existing, table, type_="foreignkey")
        op.create_foreign_key(existing, table, ref_table, [column], [ref_column])

    for table, name, condition in CHECKS:
        op.drop_constraint(name, table, type_="check")
