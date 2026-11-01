"""Research domain: semilleros, projects, publications, events, notifications, achievements.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-01

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def _id():
    return sa.Column("id", sa.Integer(), nullable=False)


def _fk(name, target, nullable=False):
    return sa.Column(name, sa.Integer(), sa.ForeignKey(target), nullable=nullable)


def _created_at():
    return sa.Column(
        "created_at",
        sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )


def upgrade():
    op.create_table(
        "semilleros",
        _id(),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("area", sa.String(120)),
        sa.Column("description", sa.Text()),
        sa.Column("icon", sa.String(40), nullable=False, server_default="science"),
        sa.Column("top_badge", sa.String(40)),
        _fk("faculty_id", "faculties.id", True),
        _fk("program_id", "programs.id", True),
        _fk("leader_id", "users.id", True),
        sa.Column("leader_name", sa.String(160)),
        sa.Column("leader_title", sa.String(160)),
        sa.Column("affiliation", sa.String(255)),
        sa.Column("about", sa.Text()),
        sa.Column("mission", sa.Text()),
        sa.Column("vision", sa.Text()),
        sa.Column("interest_areas", sa.JSON()),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_semilleros_slug", "semilleros", ["slug"], unique=True)

    op.create_table(
        "semillero_members",
        _id(),
        _fk("semillero_id", "semilleros.id"),
        _fk("user_id", "users.id"),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
        sa.Column(
            "joined_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("semillero_id", "user_id"),
    )
    op.create_table(
        "research_lines",
        _id(),
        _fk("semillero_id", "semilleros.id"),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("icon", sa.String(40), nullable=False, server_default="science"),
        sa.Column("coordinator", sa.String(160)),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "semillero_activities",
        _id(),
        _fk("semillero_id", "semilleros.id"),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("place", sa.String(200)),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "projects",
        _id(),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("type", sa.String(60)),
        sa.Column("status", sa.String(20), nullable=False, server_default="planned"),
        sa.Column("description", sa.Text()),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("line", sa.String(120)),
        sa.Column("role_required", sa.String(160)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        _fk("semillero_id", "semilleros.id", True),
        _fk("leader_id", "users.id"),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_slug", "projects", ["slug"], unique=True)
    op.create_table(
        "project_members",
        _id(),
        _fk("project_id", "projects.id"),
        _fk("user_id", "users.id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "user_id"),
    )
    op.create_table(
        "project_products",
        _id(),
        _fk("project_id", "projects.id"),
        sa.Column("type", sa.String(60), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_review"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_milestones",
        _id(),
        _fk("project_id", "projects.id"),
        sa.Column("text", sa.String(200), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "publications",
        _id(),
        _fk("author_id", "users.id"),
        _fk("semillero_id", "semilleros.id", True),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("venue", sa.String(160)),
        sa.Column("published_on", sa.Date()),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_review"),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "events",
        _id(),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("kind", sa.String(10), nullable=False, server_default="event"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("type", sa.String(60)),
        sa.Column("status", sa.String(10), nullable=False, server_default="open"),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(160)),
        sa.Column("capacity", sa.Integer()),
        sa.Column("organizer", sa.String(160)),
        sa.Column("requirements", sa.JSON()),
        _fk("created_by", "users.id", True),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_slug", "events", ["slug"], unique=True)
    op.create_table(
        "event_registrations",
        _id(),
        _fk("event_id", "events.id"),
        _fk("user_id", "users.id"),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "user_id"),
    )

    op.create_table(
        "notifications",
        _id(),
        _fk("user_id", "users.id"),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("priority", sa.String(10), nullable=False, server_default="normal"),
        sa.Column("href", sa.String(200)),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="0"),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_table(
        "achievements",
        _id(),
        _fk("user_id", "users.id"),
        sa.Column("icon", sa.String(40), nullable=False, server_default="military_tech"),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_review"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("achieved_on", sa.Date(), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_achievements_user_id", "achievements", ["user_id"])


def downgrade():
    op.drop_index("ix_achievements_user_id", table_name="achievements")
    op.drop_table("achievements")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_table("event_registrations")
    op.drop_index("ix_events_slug", table_name="events")
    op.drop_table("events")
    op.drop_table("publications")
    op.drop_table("project_milestones")
    op.drop_table("project_products")
    op.drop_table("project_members")
    op.drop_index("ix_projects_slug", table_name="projects")
    op.drop_table("projects")
    op.drop_table("semillero_activities")
    op.drop_table("research_lines")
    op.drop_table("semillero_members")
    op.drop_index("ix_semilleros_slug", table_name="semilleros")
    op.drop_table("semilleros")
