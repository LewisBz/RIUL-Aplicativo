"""Complete data model (ER diagram): profiles, comments/shares, memberships with
approval, follows, products, calls, gamification ledger, reports.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-01

Cambios principales (con migración de datos):

* ``posts.author_id`` -> ``posts.user_id``; nuevas ``comments`` y ``post_shares``.
* ``user_profiles`` (bio, foto, ORCID).
* ``semilleros``: facultad y líder obligatorios; ``leader_name`` desaparece.
  ``semillero_members`` gana ``status``/``approved_by``/roles y el líder figura
  como miembro. ``research_lines`` -> ``semillero_research_lines``. Nuevas
  ``semillero_follows`` y ``semillero_progress``.
* ``projects.leader_id`` -> miembro con rol ``principal``; ``completed`` ->
  ``closed``; ``project_milestones.text`` -> ``title``.
* ``publications`` + ``project_products`` -> ``products``.
* ``events.kind='call'`` -> ``calls`` (+ ``call_applications``);
  ``event_registrations`` -> ``event_participations``.
* ``notifications.is_read`` -> ``read_at`` (+ ``entity_kind``/``entity_id``).
* ``achievements`` rediseñada (tipo + origen único + validación) con
  ``achievement_types``, ``badges``, ``levels``, ``evidences``, ``user_badges``,
  ``xp_ledger`` y ``user_progress``. Los logros antiguos que nacieron de una
  inscripción a un evento se conservan (mismo id); los demás no tienen origen
  y se archivan en ``achievements_legacy`` para que el equipo los revise.
* ``report_snapshots``.

MySQL no admite DDL transaccional: respalda la base antes de migrar.
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

# --- Datos de referencia (copia congelada de app/reference_data.py) ---------
XP_PER_LEVEL = 200
MAX_LEVEL = 20
BADGES = [
    ("Participante de eventos", "Participó en un evento institucional.", "event"),
    ("Voz de la comunidad", "Aportó contenido valioso al feed.", "forum"),
    ("Investigador de proyectos", "Contribuyó a un proyecto de investigación.", "science"),
    ("Publicador académico", "Publicó un artículo académico.", "article"),
    ("Ponente", "Presentó una ponencia o producto.", "slideshow"),
    ("Innovador", "Registró una patente.", "lightbulb"),
    ("Líder de semillero", "Impulsó un semillero de investigación.", "groups"),
]
ACHIEVEMENT_TYPES = [
    ("event", "Participación en evento", "event", 20, "Participante de eventos"),
    ("post", "Publicación destacada", "forum", 10, "Voz de la comunidad"),
    ("project", "Proyecto de investigación", "science", 100, "Investigador de proyectos"),
    ("article", "Artículo académico", "article", 150, "Publicador académico"),
    ("presentation", "Ponencia", "slideshow", 80, "Ponente"),
    ("patent", "Patente", "lightbulb", 300, "Innovador"),
    ("semillero", "Aporte a semillero", "groups", 50, "Líder de semillero"),
]

NOW = sa.text("CURRENT_TIMESTAMP")
ADMIN_OR_FIRST_USER = (
    "COALESCE((SELECT id FROM users WHERE role = 'administrator' ORDER BY id LIMIT 1),"
    " (SELECT MIN(id) FROM users))"
)
# Título que generaba la inscripción a un evento en el esquema anterior.
LEGACY_EVENT_MATCH = (
    "(SELECT MIN(e.id) FROM events e WHERE CONCAT('Participación en ', e.title) = o.title)"
)


# --- Utilidades ------------------------------------------------------------------
def _sql(statement: str, **params):
    op.get_bind().execute(sa.text(statement), params)


def _scalar(statement: str):
    return op.get_bind().execute(sa.text(statement)).scalar()


def _drop_fks(table: str, column: str) -> None:
    """Elimina las FK de una columna (su nombre lo genera MySQL, se descubre)."""
    for fk in sa.inspect(op.get_bind()).get_foreign_keys(table):
        if column in fk["constrained_columns"] and fk["name"]:
            op.drop_constraint(fk["name"], table, type_="foreignkey")


def _rename_index(table: str, old: str, new: str) -> None:
    """Renombra el índice que MySQL creó para una FK (si existe)."""
    names = {i["name"] for i in sa.inspect(op.get_bind()).get_indexes(table)}
    if old in names and new not in names:
        op.execute(f"ALTER TABLE `{table}` RENAME INDEX `{old}` TO `{new}`")


def _table_exists(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def _id():
    return sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True)


def _created_at():
    return sa.Column("created_at", sa.DateTime(), server_default=NOW, nullable=False)


def _fk(name, target, nullable=False, ondelete=None):
    return sa.Column(
        name, sa.Integer(), sa.ForeignKey(target, ondelete=ondelete), nullable=nullable
    )


# =============================== UPGRADE =====================================
def upgrade():
    _create_catalogs()
    _users_and_posts()
    _semilleros()
    _projects_and_products()
    _events_and_calls()
    _notifications()
    _achievements()
    _reports()


def _create_catalogs():
    op.create_table(
        "levels",
        _id(),
        sa.Column("level_number", sa.Integer(), nullable=False),
        sa.Column("min_xp", sa.Integer(), nullable=False),
        sa.Column("stars", sa.Integer(), nullable=False),
        sa.UniqueConstraint("level_number"),
        sa.CheckConstraint("stars BETWEEN 1 AND 5", name="ck_levels_stars"),
    )
    op.create_table(
        "badges",
        _id(),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.String(255)),
        sa.Column("icon", sa.String(40), nullable=False, server_default="military_tech"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "achievement_types",
        _id(),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("icon", sa.String(40), nullable=False, server_default="military_tech"),
        sa.Column("xp_value", sa.Integer(), nullable=False, server_default="0"),
        _fk("badge_id", "badges.id", nullable=True),
        sa.UniqueConstraint("code"),
        sa.CheckConstraint(
            "code IN ('event','post','project','article','presentation','patent','semillero')",
            name="ck_achievement_types_code",
        ),
    )
    for number in range(1, MAX_LEVEL + 1):
        _sql(
            "INSERT INTO levels (level_number, min_xp, stars) VALUES (:n, :xp, :s)",
            n=number, xp=(number - 1) * XP_PER_LEVEL, s=min(5, number),
        )
    for name, description, icon in BADGES:
        _sql(
            "INSERT INTO badges (name, description, icon) VALUES (:n, :d, :i)",
            n=name, d=description, i=icon,
        )
    for code, name, icon, xp, badge in ACHIEVEMENT_TYPES:
        _sql(
            "INSERT INTO achievement_types (code, name, icon, xp_value, badge_id) "
            "VALUES (:c, :n, :i, :x, (SELECT id FROM badges WHERE name = :b))",
            c=code, n=name, i=icon, x=xp, b=badge,
        )


def _users_and_posts():
    op.create_table(
        "user_profiles",
        _id(),
        _fk("user_id", "users.id", ondelete="CASCADE"),
        sa.Column("bio", sa.Text()),
        sa.Column("photo", sa.String(255)),
        sa.Column("orcid", sa.String(19)),
        sa.UniqueConstraint("user_id"),
    )
    op.alter_column(
        "posts", "author_id", new_column_name="user_id",
        existing_type=sa.Integer(), existing_nullable=False,
    )
    _rename_index("posts", "author_id", "user_id")
    op.create_table(
        "comments",
        _id(),
        _fk("post_id", "posts.id", ondelete="CASCADE"),
        _fk("user_id", "users.id"),
        sa.Column("body", sa.Text(), nullable=False),
        _created_at(),
    )
    op.create_index("ix_comments_post_id", "comments", ["post_id"])
    op.create_table(
        "post_shares",
        _id(),
        _fk("post_id", "posts.id", ondelete="CASCADE"),
        _fk("user_id", "users.id"),
        _created_at(),
        sa.UniqueConstraint("post_id", "user_id"),
    )


def _semilleros():
    # Líder y facultad pasan a ser obligatorios: se rellenan los huecos.
    _sql(f"UPDATE semilleros SET leader_id = {ADMIN_OR_FIRST_USER} WHERE leader_id IS NULL")
    if _scalar("SELECT COUNT(*) FROM semilleros WHERE leader_id IS NULL"):
        raise RuntimeError("Hay semilleros sin líder y no existen usuarios para asignarlo.")
    _sql(
        "UPDATE semilleros s JOIN users u ON u.id = s.leader_id "
        "SET s.faculty_id = u.faculty_id "
        "WHERE s.faculty_id IS NULL AND u.faculty_id IS NOT NULL"
    )
    _sql(
        "INSERT INTO faculties (name) SELECT 'Sin facultad' FROM DUAL "
        "WHERE EXISTS (SELECT 1 FROM semilleros WHERE faculty_id IS NULL) "
        "AND NOT EXISTS (SELECT 1 FROM faculties WHERE name = 'Sin facultad')"
    )
    _sql(
        "UPDATE semilleros SET faculty_id = (SELECT id FROM faculties WHERE name = 'Sin facultad') "
        "WHERE faculty_id IS NULL"
    )
    op.alter_column("semilleros", "faculty_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("semilleros", "leader_id", existing_type=sa.Integer(), nullable=False)
    _sql("UPDATE semilleros SET interest_areas = JSON_ARRAY() WHERE interest_areas IS NULL")
    op.alter_column("semilleros", "interest_areas", existing_type=sa.JSON(), nullable=False)
    op.drop_column("semilleros", "leader_name")

    # Membresías: estado de aprobación, roles acotados y líder como miembro.
    _sql(
        "UPDATE semillero_members m JOIN semilleros s ON s.id = m.semillero_id "
        "SET m.role = 'member' WHERE m.role = 'leader' AND m.user_id <> s.leader_id"
    )
    _sql("UPDATE semillero_members SET role = 'member' WHERE role NOT IN ('leader','co_leader','member')")
    op.add_column(
        "semillero_members",
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
    )
    op.add_column("semillero_members", sa.Column("approved_by", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_semillero_members_approved_by", "semillero_members", "users", ["approved_by"], ["id"]
    )
    op.alter_column(
        "semillero_members", "status", existing_type=sa.String(20),
        existing_nullable=False, server_default="pending",
    )
    _sql(
        "UPDATE semillero_members m JOIN semilleros s ON s.id = m.semillero_id "
        "SET m.approved_by = s.leader_id, m.status = 'active', "
        "m.role = IF(m.user_id = s.leader_id, 'leader', m.role)"
    )
    _sql(
        "INSERT INTO semillero_members (semillero_id, user_id, role, status, approved_by) "
        "SELECT s.id, s.leader_id, 'leader', 'active', s.leader_id FROM semilleros s "
        "WHERE NOT EXISTS (SELECT 1 FROM semillero_members m "
        "WHERE m.semillero_id = s.id AND m.user_id = s.leader_id)"
    )
    op.create_check_constraint(
        "ck_semillero_members_role", "semillero_members",
        "role IN ('leader','co_leader','member')",
    )
    op.create_check_constraint(
        "ck_semillero_members_status", "semillero_members",
        "status IN ('pending','active','rejected')",
    )

    op.rename_table("research_lines", "semillero_research_lines")
    op.create_table(
        "semillero_follows",
        _id(),
        _fk("semillero_id", "semilleros.id"),
        _fk("user_id", "users.id"),
        _created_at(),
        sa.UniqueConstraint("semillero_id", "user_id"),
    )
    op.create_table(
        "semillero_progress",
        _id(),
        _fk("semillero_id", "semilleros.id"),
        _fk("level_id", "levels.id"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("semillero_id"),
    )
    _sql(
        "INSERT INTO semillero_progress (semillero_id, level_id, xp) "
        "SELECT s.id, (SELECT id FROM levels WHERE level_number = 1), 0 FROM semilleros s"
    )


def _projects_and_products():
    _sql("UPDATE projects SET status = 'closed' WHERE status = 'completed'")
    _sql(
        "UPDATE projects SET status = 'planned' "
        "WHERE status NOT IN ('planned','in_progress','review','closed')"
    )
    _sql("UPDATE projects SET progress = LEAST(100, GREATEST(0, progress))")

    op.add_column(
        "project_members",
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
    )
    _sql(
        "UPDATE project_members m JOIN projects p ON p.id = m.project_id "
        "SET m.role = 'principal' WHERE m.user_id = p.leader_id"
    )
    _sql(
        "INSERT INTO project_members (project_id, user_id, role) "
        "SELECT p.id, p.leader_id, 'principal' FROM projects p "
        "WHERE NOT EXISTS (SELECT 1 FROM project_members m "
        "WHERE m.project_id = p.id AND m.user_id = p.leader_id)"
    )
    _drop_fks("projects", "leader_id")
    op.drop_column("projects", "leader_id")
    op.create_check_constraint(
        "ck_projects_status", "projects",
        "status IN ('planned','in_progress','review','closed')",
    )
    op.create_check_constraint("ck_projects_progress", "projects", "progress BETWEEN 0 AND 100")
    op.create_check_constraint(
        "ck_project_members_role", "project_members", "role IN ('principal','member')"
    )
    op.alter_column(
        "project_milestones", "text", new_column_name="title",
        existing_type=sa.String(200), existing_nullable=False,
    )

    op.create_table(
        "products",
        _id(),
        _fk("user_id", "users.id"),
        _fk("project_id", "projects.id", nullable=True),
        _fk("semillero_id", "semilleros.id", nullable=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("venue", sa.String(160)),
        sa.Column("published_on", sa.Date()),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_review"),
        _created_at(),
        sa.CheckConstraint(
            "type IN ('article','presentation','patent','report')", name="ck_products_type"
        ),
        sa.CheckConstraint("status IN ('in_review','approved')", name="ck_products_status"),
    )
    op.create_index("ix_products_user_id", "products", ["user_id"])
    op.create_index("ix_products_project_id", "products", ["project_id"])
    # publications -> artículos sueltos del investigador
    _sql(
        "INSERT INTO products (user_id, project_id, semillero_id, type, title, venue, "
        "published_on, status, created_at) "
        "SELECT author_id, NULL, semillero_id, 'article', title, venue, published_on, "
        "CASE WHEN status IN ('published','approved') THEN 'approved' ELSE 'in_review' END, "
        "created_at FROM publications"
    )
    # project_products -> productos del proyecto, a nombre del responsable
    _sql(
        "INSERT INTO products (user_id, project_id, semillero_id, type, title, status) "
        "SELECT m.user_id, pp.project_id, p.semillero_id, "
        "CASE WHEN LOWER(pp.type) IN ('article','articulo','artículo') THEN 'article' "
        "WHEN LOWER(pp.type) IN ('presentation','ponencia','presentacion','presentación') "
        "THEN 'presentation' "
        "WHEN LOWER(pp.type) IN ('patent','patente') THEN 'patent' ELSE 'report' END, "
        "pp.name, "
        "CASE WHEN pp.status IN ('published','approved') THEN 'approved' ELSE 'in_review' END "
        "FROM project_products pp "
        "JOIN projects p ON p.id = pp.project_id "
        "JOIN project_members m ON m.project_id = pp.project_id AND m.role = 'principal'"
    )
    op.drop_table("publications")
    op.drop_table("project_products")


def _events_and_calls():
    _sql("UPDATE events SET status = 'open' WHERE status NOT IN ('open','closed')")
    _sql("UPDATE events SET ends_at = starts_at WHERE ends_at < starts_at")
    _sql("UPDATE events SET requirements = JSON_ARRAY() WHERE requirements IS NULL")
    op.alter_column("events", "requirements", existing_type=sa.JSON(), nullable=False)
    op.add_column("events", sa.Column("semillero_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_events_semillero_id", "events", "semilleros", ["semillero_id"], ["id"]
    )

    op.create_table(
        "event_participations",
        _id(),
        _fk("event_id", "events.id"),
        _fk("user_id", "users.id"),
        sa.Column("role", sa.String(20), nullable=False, server_default="attendee"),
        sa.Column("status", sa.String(20), nullable=False, server_default="registered"),
        _created_at(),
        sa.UniqueConstraint("event_id", "user_id"),
        sa.CheckConstraint(
            "role IN ('attendee','speaker','organizer')", name="ck_event_participations_role"
        ),
        sa.CheckConstraint(
            "status IN ('available','registered','pending','closed')",
            name="ck_event_participations_status",
        ),
    )
    op.create_table(
        "calls",
        _id(),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("type", sa.String(60)),
        sa.Column("status", sa.String(10), nullable=False, server_default="open"),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(160)),
        sa.Column("organizer", sa.String(160)),
        sa.Column("requirements", sa.JSON(), nullable=False),
        _fk("published_by", "users.id"),
        _created_at(),
        sa.CheckConstraint("status IN ('open','closed')", name="ck_calls_status"),
        sa.CheckConstraint("ends_at >= starts_at", name="ck_calls_dates"),
    )
    op.create_index("ix_calls_slug", "calls", ["slug"], unique=True)
    op.create_table(
        "call_applications",
        _id(),
        _fk("call_id", "calls.id"),
        _fk("user_id", "users.id", nullable=True),
        _fk("semillero_id", "semilleros.id", nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        _created_at(),
        sa.UniqueConstraint("call_id", "user_id"),
        sa.UniqueConstraint("call_id", "semillero_id"),
        sa.CheckConstraint(
            "(user_id IS NOT NULL AND semillero_id IS NULL) OR "
            "(user_id IS NULL AND semillero_id IS NOT NULL)",
            name="ck_call_applications_applicant",
        ),
        sa.CheckConstraint(
            "status IN ('pending','accepted','rejected')", name="ck_call_applications_status"
        ),
    )

    _sql(
        "INSERT INTO event_participations (event_id, user_id, role, status, created_at) "
        "SELECT r.event_id, r.user_id, 'attendee', 'registered', r.created_at "
        "FROM event_registrations r JOIN events e ON e.id = r.event_id WHERE e.kind = 'event'"
    )
    _sql(
        "INSERT INTO calls (slug, title, description, type, status, starts_at, ends_at, "
        "location, organizer, requirements, published_by, created_at) "
        "SELECT e.slug, e.title, e.description, e.type, e.status, e.starts_at, e.ends_at, "
        f"e.location, e.organizer, COALESCE(e.requirements, JSON_ARRAY()), "
        f"COALESCE(e.created_by, {ADMIN_OR_FIRST_USER}), "
        "e.created_at FROM events e WHERE e.kind = 'call'"
    )
    _sql(
        "INSERT INTO call_applications (call_id, user_id, status, created_at) "
        "SELECT c.id, r.user_id, 'pending', r.created_at FROM event_registrations r "
        "JOIN events e ON e.id = r.event_id AND e.kind = 'call' "
        "JOIN calls c ON c.slug = e.slug"
    )
    _sql(
        "DELETE r FROM event_registrations r JOIN events e ON e.id = r.event_id "
        "WHERE e.kind = 'call'"
    )
    _sql("DELETE FROM events WHERE kind = 'call'")
    op.drop_table("event_registrations")
    op.drop_column("events", "kind")
    op.create_check_constraint("ck_events_status", "events", "status IN ('open','closed')")
    op.create_check_constraint("ck_events_dates", "events", "ends_at >= starts_at")


def _notifications():
    op.add_column("notifications", sa.Column("entity_kind", sa.String(30)))
    op.add_column("notifications", sa.Column("entity_id", sa.Integer()))
    op.add_column("notifications", sa.Column("read_at", sa.DateTime()))
    _sql("UPDATE notifications SET read_at = created_at WHERE is_read = 1")
    op.drop_column("notifications", "is_read")


def _achievements():
    # La tabla anterior cede su nombre; se suelta su FK para que MySQL no
    # reutilice el nombre de restricción al crear la nueva.
    op.rename_table("achievements", "achievements_old")
    _drop_fks("achievements_old", "user_id")
    op.drop_index("ix_achievements_user_id", table_name="achievements_old")

    op.create_table(
        "achievements",
        _id(),
        _fk("user_id", "users.id"),
        _fk("type_id", "achievement_types.id"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        _fk("validated_by", "users.id", nullable=True),
        sa.Column("validated_at", sa.DateTime()),
        _fk("event_id", "events.id", nullable=True),
        _fk("post_id", "posts.id", nullable=True),
        _fk("project_id", "projects.id", nullable=True),
        _fk("product_id", "products.id", nullable=True),
        _fk("semillero_id", "semilleros.id", nullable=True),
        _fk("xp_semillero_id", "semilleros.id", nullable=True),
        sa.Column("title", sa.String(160)),
        sa.Column("description", sa.Text()),
        sa.Column("achieved_on", sa.Date(), nullable=False),
        _created_at(),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_achievements_status"
        ),
        sa.CheckConstraint(
            "(event_id IS NOT NULL) + (post_id IS NOT NULL) + (project_id IS NOT NULL) + "
            "(product_id IS NOT NULL) + (semillero_id IS NOT NULL) = 1",
            name="ck_achievements_single_origin",
        ),
    )
    op.create_index("ix_achievements_user_id", "achievements", ["user_id"])
    op.create_table(
        "evidences",
        _id(),
        _fk("achievement_id", "achievements.id", ondelete="CASCADE"),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("storage_name", sa.String(120), nullable=False),
        sa.Column("mime_type", sa.String(100)),
        sa.Column("file_size", sa.Integer()),
        _created_at(),
        sa.UniqueConstraint("storage_name"),
    )
    op.create_index("ix_evidences_achievement_id", "evidences", ["achievement_id"])
    op.create_table(
        "user_badges",
        _id(),
        _fk("user_id", "users.id"),
        _fk("badge_id", "badges.id"),
        _fk("achievement_id", "achievements.id"),
        _created_at(),
        sa.UniqueConstraint("user_id", "badge_id"),
    )
    op.create_table(
        "xp_ledger",
        _id(),
        _fk("user_id", "users.id"),
        _fk("achievement_id", "achievements.id"),
        sa.Column("amount", sa.Integer(), nullable=False),
        _created_at(),
        sa.UniqueConstraint("achievement_id"),
    )
    op.create_index("ix_xp_ledger_user_id", "xp_ledger", ["user_id"])
    op.create_table(
        "user_progress",
        _id(),
        _fk("user_id", "users.id"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        _fk("level_id", "levels.id"),
        sa.Column("stars", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("user_id"),
        sa.CheckConstraint("stars BETWEEN 1 AND 5", name="ck_user_progress_stars"),
    )

    # Logros sin origen reconocible: se archivan, no se pierden.
    op.execute(
        f"CREATE TABLE achievements_legacy AS SELECT o.* FROM achievements_old o "
        f"WHERE {LEGACY_EVENT_MATCH} IS NULL"
    )
    if not _scalar("SELECT COUNT(*) FROM achievements_legacy"):
        op.drop_table("achievements_legacy")

    # Logros de participación en eventos: se conservan con su id.
    _sql(
        "INSERT INTO achievements (id, user_id, type_id, status, validated_at, event_id, "
        "title, description, achieved_on, created_at) "
        "SELECT o.id, o.user_id, (SELECT id FROM achievement_types WHERE code = 'event'), "
        "CASE o.status WHEN 'validated' THEN 'approved' WHEN 'rejected' THEN 'rejected' "
        "ELSE 'pending' END, "
        "IF(o.status IN ('validated','rejected'), o.created_at, NULL), "
        f"{LEGACY_EVENT_MATCH}, LEFT(o.title, 160), o.description, o.achieved_on, o.created_at "
        f"FROM achievements_old o WHERE {LEGACY_EVENT_MATCH} IS NOT NULL"
    )
    _sql(
        "INSERT INTO xp_ledger (user_id, achievement_id, amount, created_at) "
        "SELECT o.user_id, o.id, o.xp, o.created_at FROM achievements_old o "
        "JOIN achievements a ON a.id = o.id WHERE o.status = 'validated'"
    )
    _sql(
        "INSERT INTO user_progress (user_id, xp, level_id, stars) "
        "SELECT t.user_id, t.xp, l.id, l.stars "
        "FROM (SELECT user_id, SUM(amount) AS xp FROM xp_ledger GROUP BY user_id) t "
        "JOIN levels l ON l.level_number = "
        "(SELECT MAX(level_number) FROM levels WHERE min_xp <= t.xp)"
    )
    _sql(
        "INSERT INTO user_badges (user_id, badge_id, achievement_id) "
        "SELECT a.user_id, t.badge_id, MIN(a.id) FROM achievements a "
        "JOIN achievement_types t ON t.id = a.type_id "
        "WHERE a.status = 'approved' AND t.badge_id IS NOT NULL "
        "GROUP BY a.user_id, t.badge_id"
    )
    op.drop_table("achievements_old")


def _reports():
    op.create_table(
        "report_snapshots",
        _id(),
        _fk("generated_by", "users.id"),
        sa.Column("kind", sa.String(10), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("published_at", sa.DateTime()),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        _created_at(),
        sa.CheckConstraint("kind IN ('report','ranking')", name="ck_report_snapshots_kind"),
        sa.CheckConstraint("period_end >= period_start", name="ck_report_snapshots_period"),
    )


# =============================== DOWNGRADE ===================================
def downgrade():
    op.drop_table("report_snapshots")
    _downgrade_achievements()
    _downgrade_notifications()
    _downgrade_events()
    _downgrade_products_and_projects()
    _downgrade_semilleros()
    _downgrade_users_and_posts()
    op.drop_table("achievement_types")
    op.drop_table("badges")
    op.drop_table("levels")


def _downgrade_achievements():
    op.create_table(
        "achievements_prev",
        _id(),
        _fk("user_id", "users.id"),
        sa.Column("icon", sa.String(40), nullable=False, server_default="military_tech"),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_review"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("achieved_on", sa.Date(), nullable=False),
        _created_at(),
    )
    _sql(
        "INSERT INTO achievements_prev (id, user_id, icon, title, description, status, xp, "
        "achieved_on, created_at) "
        "SELECT a.id, a.user_id, t.icon, COALESCE(a.title, t.name), a.description, "
        "CASE a.status WHEN 'approved' THEN 'validated' WHEN 'rejected' THEN 'rejected' "
        "ELSE 'in_review' END, "
        "COALESCE((SELECT l.amount FROM xp_ledger l WHERE l.achievement_id = a.id), t.xp_value), "
        "a.achieved_on, a.created_at "
        "FROM achievements a JOIN achievement_types t ON t.id = a.type_id"
    )
    if _table_exists("achievements_legacy"):
        _sql(
            "INSERT INTO achievements_prev (user_id, icon, title, description, status, xp, "
            "achieved_on, created_at) "
            "SELECT user_id, icon, title, description, status, xp, achieved_on, created_at "
            "FROM achievements_legacy"
        )
        op.drop_table("achievements_legacy")
    for table in ("user_progress", "xp_ledger", "user_badges", "evidences", "achievements"):
        op.drop_table(table)
    op.rename_table("achievements_prev", "achievements")
    op.create_index("ix_achievements_user_id", "achievements", ["user_id"])


def _downgrade_notifications():
    op.add_column(
        "notifications",
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="0"),
    )
    _sql("UPDATE notifications SET is_read = 1 WHERE read_at IS NOT NULL")
    op.drop_column("notifications", "read_at")
    op.drop_column("notifications", "entity_id")
    op.drop_column("notifications", "entity_kind")


def _downgrade_events():
    op.drop_constraint("ck_events_dates", "events", type_="check")
    op.drop_constraint("ck_events_status", "events", type_="check")
    op.alter_column("events", "requirements", existing_type=sa.JSON(), nullable=True)
    op.add_column(
        "events", sa.Column("kind", sa.String(10), nullable=False, server_default="event")
    )
    op.create_table(
        "event_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        _fk("event_id", "events.id"),
        _fk("user_id", "users.id"),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "user_id"),
    )
    _sql(
        "INSERT INTO event_registrations (event_id, user_id, created_at) "
        "SELECT event_id, user_id, created_at FROM event_participations"
    )
    _sql(
        "INSERT INTO events (slug, kind, title, description, type, status, starts_at, ends_at, "
        "location, organizer, requirements, created_by, created_at) "
        "SELECT slug, 'call', title, description, type, status, starts_at, ends_at, "
        "location, organizer, requirements, published_by, created_at FROM calls"
    )
    _sql(
        "INSERT INTO event_registrations (event_id, user_id, created_at) "
        "SELECT e.id, a.user_id, a.created_at FROM call_applications a "
        "JOIN calls c ON c.id = a.call_id "
        "JOIN events e ON e.slug = c.slug AND e.kind = 'call' WHERE a.user_id IS NOT NULL"
    )
    op.drop_constraint("fk_events_semillero_id", "events", type_="foreignkey")
    op.drop_column("events", "semillero_id")
    op.drop_table("call_applications")
    op.drop_table("calls")
    op.drop_table("event_participations")


def _downgrade_products_and_projects():
    op.create_table(
        "publications",
        sa.Column("id", sa.Integer(), nullable=False),
        _fk("author_id", "users.id"),
        _fk("semillero_id", "semilleros.id", nullable=True),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("venue", sa.String(160)),
        sa.Column("published_on", sa.Date()),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_review"),
        _created_at(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_products",
        sa.Column("id", sa.Integer(), nullable=False),
        _fk("project_id", "projects.id"),
        sa.Column("type", sa.String(60), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_review"),
        sa.PrimaryKeyConstraint("id"),
    )
    _sql(
        "INSERT INTO publications (author_id, semillero_id, title, venue, published_on, "
        "status, created_at) "
        "SELECT user_id, semillero_id, title, venue, published_on, "
        "IF(status = 'approved', 'published', 'in_review'), created_at "
        "FROM products WHERE project_id IS NULL"
    )
    _sql(
        "INSERT INTO project_products (project_id, type, name, status) "
        "SELECT project_id, CASE type WHEN 'article' THEN 'Artículo' "
        "WHEN 'presentation' THEN 'Ponencia' WHEN 'patent' THEN 'Patente' ELSE 'Informe' END, "
        "LEFT(title, 200), status FROM products WHERE project_id IS NOT NULL"
    )
    op.drop_table("products")

    op.alter_column(
        "project_milestones", "title", new_column_name="text",
        existing_type=sa.String(200), existing_nullable=False,
    )
    op.drop_constraint("ck_project_members_role", "project_members", type_="check")
    op.drop_constraint("ck_projects_progress", "projects", type_="check")
    op.drop_constraint("ck_projects_status", "projects", type_="check")
    op.add_column("projects", sa.Column("leader_id", sa.Integer(), nullable=True))
    _sql(
        "UPDATE projects p SET p.leader_id = COALESCE("
        "(SELECT m.user_id FROM project_members m "
        "WHERE m.project_id = p.id AND m.role = 'principal' LIMIT 1), "
        f"(SELECT m.user_id FROM project_members m WHERE m.project_id = p.id LIMIT 1), "
        f"{ADMIN_OR_FIRST_USER})"
    )
    op.alter_column("projects", "leader_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key("fk_projects_leader_id", "projects", "users", ["leader_id"], ["id"])
    _sql("UPDATE projects SET status = 'completed' WHERE status = 'closed'")
    op.drop_column("project_members", "role")


def _downgrade_semilleros():
    op.drop_table("semillero_progress")
    op.drop_table("semillero_follows")
    op.rename_table("semillero_research_lines", "research_lines")
    op.drop_constraint("ck_semillero_members_status", "semillero_members", type_="check")
    op.drop_constraint("ck_semillero_members_role", "semillero_members", type_="check")
    _sql("DELETE FROM semillero_members WHERE status <> 'active' OR role = 'leader'")
    _sql("UPDATE semillero_members SET role = 'member' WHERE role = 'co_leader'")
    op.drop_constraint("fk_semillero_members_approved_by", "semillero_members", type_="foreignkey")
    op.drop_column("semillero_members", "approved_by")
    op.drop_column("semillero_members", "status")

    op.add_column("semilleros", sa.Column("leader_name", sa.String(160)))
    _sql(
        "UPDATE semilleros s JOIN users u ON u.id = s.leader_id SET s.leader_name = u.full_name"
    )
    op.alter_column("semilleros", "leader_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("semilleros", "faculty_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("semilleros", "interest_areas", existing_type=sa.JSON(), nullable=True)


def _downgrade_users_and_posts():
    op.drop_table("post_shares")
    op.drop_table("comments")
    op.alter_column(
        "posts", "user_id", new_column_name="author_id",
        existing_type=sa.Integer(), existing_nullable=False,
    )
    _rename_index("posts", "user_id", "author_id")
    op.drop_table("user_profiles")
