"""Add semilleros and semillero_members tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-15

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "semilleros",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("area", sa.String(length=100), nullable=True),
        sa.Column("mission", sa.Text(), nullable=True),
        sa.Column("vision", sa.Text(), nullable=True),
        sa.Column("faculty_id", sa.Integer(), nullable=True),
        sa.Column("program_id", sa.Integer(), nullable=True),
        sa.Column("leader_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.ForeignKeyConstraint(["leader_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_semilleros_slug", "semilleros", ["slug"], unique=True)

    op.create_table(
        "semillero_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("semillero_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "role_in_semillero",
            sa.String(length=50),
            nullable=False,
            server_default="Estudiante Investigador",
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["semillero_id"], ["semilleros.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("semillero_id", "user_id"),
    )


def downgrade():
    op.drop_table("semillero_members")
    op.drop_index("ix_semilleros_slug", table_name="semilleros")
    op.drop_table("semilleros")
