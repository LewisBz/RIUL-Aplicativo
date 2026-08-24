"""Auth module initial tables: users, faculties, programs

Revision ID: 0001
Revises:
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "faculties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "programs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("faculty_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "faculty_id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role", sa.String(length=20), nullable=False, server_default="researcher"
        ),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="active"
        ),
        sa.Column("motivation", sa.String(length=500), nullable=True),
        sa.Column("faculty_id", sa.Integer(), nullable=True),
        sa.Column("program_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_users_email", "users", ["email"], unique=True
    )


def downgrade():
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("programs")
    op.drop_table("faculties")
