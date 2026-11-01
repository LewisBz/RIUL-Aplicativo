from datetime import date, datetime

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.user import User

ACHIEVEMENT_PENDING = "pending"
ACHIEVEMENT_APPROVED = "approved"
ACHIEVEMENT_REJECTED = "rejected"
ACHIEVEMENT_STATUSES = (ACHIEVEMENT_PENDING, ACHIEVEMENT_APPROVED, ACHIEVEMENT_REJECTED)

# Códigos de `achievement_types`; coinciden con el origen del logro.
TYPE_EVENT = "event"
TYPE_POST = "post"
TYPE_PROJECT = "project"
TYPE_ARTICLE = "article"
TYPE_PRESENTATION = "presentation"
TYPE_PATENT = "patent"
TYPE_SEMILLERO = "semillero"
ACHIEVEMENT_TYPE_CODES = (
    TYPE_EVENT,
    TYPE_POST,
    TYPE_PROJECT,
    TYPE_ARTICLE,
    TYPE_PRESENTATION,
    TYPE_PATENT,
    TYPE_SEMILLERO,
)

# Columnas de origen del logro: exactamente una debe estar informada.
ORIGIN_COLUMNS = ("event_id", "post_id", "project_id", "product_id", "semillero_id")

MAX_STARS = 5


class Level(db.Model):
    """Catálogo de niveles compartido por usuarios y semilleros."""

    __tablename__ = "levels"
    __table_args__ = (
        db.CheckConstraint("stars BETWEEN 1 AND 5", name="ck_levels_stars"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    level_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    min_xp: Mapped[int] = mapped_column(Integer, nullable=False)
    stars: Mapped[int] = mapped_column(Integer, nullable=False)


class Badge(db.Model):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    icon: Mapped[str] = mapped_column(
        String(40), nullable=False, default="military_tech", server_default="military_tech"
    )


class AchievementType(db.Model):
    __tablename__ = "achievement_types"
    __table_args__ = (
        db.CheckConstraint(
            "code IN ('event','post','project','article','presentation','patent','semillero')",
            name="ck_achievement_types_code",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    icon: Mapped[str] = mapped_column(
        String(40), nullable=False, default="military_tech", server_default="military_tech"
    )
    xp_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    badge_id: Mapped[int | None] = mapped_column(ForeignKey("badges.id"))

    badge: Mapped["Badge | None"] = relationship()


class Achievement(db.Model):
    """Logro de un usuario con un único origen (evento, publicación, proyecto,
    producto o semillero). Solo los aprobados suman XP."""

    __tablename__ = "achievements"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending','approved','rejected')", name="ck_achievements_status"
        ),
        db.CheckConstraint(
            "(event_id IS NOT NULL) + (post_id IS NOT NULL) + (project_id IS NOT NULL) + "
            "(product_id IS NOT NULL) + (semillero_id IS NOT NULL) = 1",
            name="ck_achievements_single_origin",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("achievement_types.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ACHIEVEMENT_PENDING, server_default=ACHIEVEMENT_PENDING
    )
    validated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    validated_at: Mapped[datetime | None] = mapped_column()
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"))
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))
    # Semillero adicional que recibe el XP del logro (además del de origen).
    xp_semillero_id: Mapped[int | None] = mapped_column(ForeignKey("semilleros.id"))
    title: Mapped[str | None] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    achieved_on: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    validator: Mapped["User | None"] = relationship(foreign_keys=[validated_by])
    type: Mapped["AchievementType"] = relationship()
    evidences: Mapped[list["Evidence"]] = relationship(
        back_populates="achievement", cascade="all, delete-orphan", passive_deletes=True
    )
    ledger_entry: Mapped["XpLedger | None"] = relationship(
        back_populates="achievement", uselist=False
    )
    event = relationship("Event", foreign_keys=[event_id])
    post = relationship("Post", foreign_keys=[post_id])
    project = relationship("Project", foreign_keys=[project_id])
    product = relationship("Product", foreign_keys=[product_id])
    semillero = relationship("Semillero", foreign_keys=[semillero_id])
    xp_semillero = relationship("Semillero", foreign_keys=[xp_semillero_id])

    @property
    def display_title(self) -> str:
        return self.title or self.type.name

    @property
    def icon(self) -> str:
        return self.type.icon

    @property
    def xp(self) -> int:
        """XP otorgado (libro mayor) si está aprobado; si no, el valor del tipo."""
        if self.ledger_entry is not None:
            return self.ledger_entry.amount
        return self.type.xp_value


class Evidence(db.Model):
    __tablename__ = "evidences"

    id: Mapped[int] = mapped_column(primary_key=True)
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    file_size: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    achievement: Mapped["Achievement"] = relationship(back_populates="evidences")


class UserBadge(db.Model):
    """Insignia obtenida por un usuario gracias a un logro aprobado."""

    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship()
    badge: Mapped["Badge"] = relationship()
    achievement: Mapped["Achievement"] = relationship()


class XpLedger(db.Model):
    """Libro mayor de XP: un asiento por logro aprobado."""

    __tablename__ = "xp_ledger"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id"), nullable=False, unique=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship()
    achievement: Mapped["Achievement"] = relationship(back_populates="ledger_entry")


class UserProgress(db.Model):
    """Resumen por usuario: XP = SUM(xp_ledger), nivel vigente y estrellas."""

    __tablename__ = "user_progress"
    __table_args__ = (
        db.CheckConstraint("stars BETWEEN 1 AND 5", name="ck_user_progress_stars"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    stars: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")

    user: Mapped["User"] = relationship()
    level: Mapped["Level"] = relationship()
